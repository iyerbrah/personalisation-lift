"""Measure what recommendation adds over random, for whom, and why.

Every user here saw both recommended and random videos in the same feed and the same
weeks, so each user is their own control. For each user:

    lift = long-view rate on recommended videos - long-view rate on random videos

The lift is averaged over users, and users are resampled to get the intervals.

Writes:
    reports/lift.json          headline, other signals, checks, popularity split
    reports/segments.csv       lift by activity level and by time since joining
    reports/daily.csv          both rates for each day of the experiment
    reports/sensitivity.csv    the headline under different user cut-offs
    data/processed/users.parquet   one row per user, read by the app

Run:  python src/lift.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

MIN_EXPOSURES = 5        # a user needs this many videos of each kind to have a rate worth comparing
MIN_VIDEO_EXPOSURES = 30  # random showings a video needs before its general appeal is trusted
RESAMPLES = 2000
SEED = 42
METRICS = {"long_view": "Long views", "is_like": "Likes", "is_hate": "Dislikes", "watch_s": "Seconds watched"}
SEGMENTS = {
    "activity": ["Daily", "Frequent", "Occasional", "Rare or new"],
    "tenure": ["Over 2 years", "1 to 2 years", "6 to 12 months", "Under 6 months"],
}
LENGTH_BANDS = [0, 15, 60, 180, np.inf]


def bootstrap_means(values, rng):
    """Means of `values` (users x columns) over resamples of the users."""
    picks = rng.integers(0, len(values), size=(RESAMPLES, len(values)))
    return values[picks].mean(axis=1)


def interval(samples, alpha=0.05):
    return [float(np.quantile(samples, alpha / 2)), float(np.quantile(samples, 1 - alpha / 2))]


def per_user(df, metric):
    """One row per user: the metric's average on recommended and on random videos."""
    table = df.pivot_table(index="user_id", columns="is_rand", values=metric, aggfunc="mean")
    return table.rename(columns={0: "recommended", 1: "random"})


def lift_summary(users, rng, alpha=0.05):
    """Average of each arm and of the per-user difference, with intervals from resampling users."""
    values = users[["recommended", "random"]].to_numpy()
    means = bootstrap_means(values, rng)
    diffs = means[:, 0] - means[:, 1]
    lift = float(values[:, 0].mean() - values[:, 1].mean())
    standard_error = float(diffs.std())
    return {
        "users": int(len(users)),
        "recommended": float(values[:, 0].mean()),
        "random": float(values[:, 1].mean()),
        "lift": lift,
        "lift_interval": interval(diffs, alpha),
        "ratio": float(values[:, 0].mean() / values[:, 1].mean()),
        "ratio_interval": interval(means[:, 0] / means[:, 1], alpha),
        # Smallest lift this many users could detect 80% of the time at the 5% level.
        "detectable_lift": 2.8 * standard_error,
    }


def cramers_v(a, b):
    """Strength of association between two categories: 0 is none, 1 is complete."""
    table = pd.crosstab(a, b).to_numpy()
    expected = table.sum(1, keepdims=True) * table.sum(0, keepdims=True) / table.sum()
    chi2 = ((table - expected) ** 2 / expected).sum()
    return float(np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1))))


def top_share(counts, share=0.10):
    ordered = np.sort(counts)[::-1]
    return float(ordered[:max(1, int(round(share * len(ordered))))].sum() / ordered.sum())


def randomisation_checks(df):
    """Was the random arm really random? Videos should be spread evenly and not matched to users."""
    checks = {}
    length = pd.cut(df.duration_s, LENGTH_BANDS)
    for arm, name in ((1, "random"), (0, "recommended")):
        part = df[df.is_rand == arm]
        checks[name] = {
            "videos_shown": int(part.video_id.nunique()),
            "top_10pct_videos_share": top_share(part.video_id.value_counts().to_numpy()),
            "video_length_vs_user_activity": cramers_v(length[part.index], part.activity.fillna("Unknown")),
        }
    return checks


def popularity_split(df, kept, rng):
    """How much of the lift comes from picking videos most people like, and how much from fit.

    A video's long-view rate when shown at random is its appeal to an average user. Giving
    every recommended video that rate answers: what if these same videos had gone to anyone?
    """
    random = df[df.is_rand == 1]
    appeal = random.groupby("video_id").long_view.agg(["mean", "size"])
    appeal = appeal.loc[appeal["size"] >= MIN_VIDEO_EXPOSURES, "mean"]

    rec = df[(df.is_rand == 0) & df.user_id.isin(kept.index)].copy()
    rec["appeal"] = rec.video_id.map(appeal)
    covered = float(rec.appeal.notna().mean())
    rec = rec.dropna(subset="appeal")

    table = kept[["random"]].join(rec.groupby("user_id").agg(same_videos_to_anyone=("appeal", "mean"),
                                                            recommended=("long_view", "mean")), how="inner")
    values = table[["random", "same_videos_to_anyone", "recommended"]].to_numpy()
    means = bootstrap_means(values, rng)
    random_rate, anyone_rate, recommended_rate = values.mean(axis=0)
    share = (means[:, 1] - means[:, 0]) / (means[:, 2] - means[:, 0])
    return {
        "users": int(len(table)),
        "recommended_exposures_covered": covered,
        "random": float(random_rate),
        "same_videos_to_anyone": float(anyone_rate),
        "recommended": float(recommended_rate),
        "from_video_choice": float(anyone_rate - random_rate),
        "from_personal_fit": float(recommended_rate - anyone_rate),
        "video_choice_share": float((anyone_rate - random_rate) / (recommended_rate - random_rate)),
        "video_choice_share_interval": interval(share),
    }


def main():
    rng = np.random.default_rng(SEED)
    df = pd.read_parquet(ROOT / "data" / "processed" / "exposures.parquet")

    counts = df.pivot_table(index="user_id", columns="is_rand", values="video_id", aggfunc="size", fill_value=0)
    counts = counts.rename(columns={0: "n_recommended", 1: "n_random"})
    traits = df.drop_duplicates("user_id").set_index("user_id")[["activity", "tenure"]]
    users = per_user(df, "long_view").join(counts).join(traits)
    kept = users[(users.n_recommended >= MIN_EXPOSURES) & (users.n_random >= MIN_EXPOSURES)].copy()
    kept["lift"] = kept.recommended - kept["random"]
    in_kept = df.user_id.isin(kept.index)

    headline = lift_summary(kept, rng)
    other = {metric: lift_summary(per_user(df[in_kept], metric), rng) for metric in METRICS if metric != "long_view"}

    # Does the answer depend on the cut-off? Repeat it with looser and stricter ones.
    sensitivity = []
    for cutoff in (1, 3, 5, 10, 20):
        part = users[(users.n_recommended >= cutoff) & (users.n_random >= cutoff)]
        sensitivity.append({"min_exposures": cutoff, **lift_summary(part, rng)})
    sensitivity = pd.DataFrame(sensitivity).drop(columns=["lift_interval", "ratio_interval"])

    # Segments: eight groups are tested, so each interval is widened to keep 95% cover overall.
    n_groups = sum(len(groups) for groups in SEGMENTS.values())
    segments = []
    for trait, groups in SEGMENTS.items():
        for group in groups:
            part = kept[kept[trait] == group]
            summary = lift_summary(part, rng, alpha=0.05 / n_groups)
            low, high = summary.pop("lift_interval")
            ratio_low, ratio_high = summary.pop("ratio_interval")
            segments.append({"trait": trait, "group": group, **summary, "lift_low": low, "lift_high": high,
                             "ratio_low": ratio_low, "ratio_high": ratio_high})
    segments = pd.DataFrame(segments)

    daily = df[in_kept].pivot_table(index="date", columns="is_rand", values="long_view",
                                    aggfunc=["mean", "size"])
    daily.columns = ["recommended", "random", "n_recommended", "n_random"]

    report = {
        "min_exposures": MIN_EXPOSURES,
        "exposures": {"recommended": int((df.is_rand == 0).sum()), "random": int((df.is_rand == 1).sum())},
        "exposures_analysed": {"recommended": int(((df.is_rand == 0) & in_kept).sum()),
                               "random": int(((df.is_rand == 1) & in_kept).sum())},
        "users_total": int(len(users)),
        "pooled": {"recommended": float(df[df.is_rand == 0].long_view.mean()),
                   "random": float(df[df.is_rand == 1].long_view.mean())},
        "headline": headline,
        "other_signals": other,
        "randomisation": randomisation_checks(df),
        "popularity_split": popularity_split(df, kept, rng),
    }

    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "lift.json").write_text(json.dumps(report, indent=2))
    segments.to_csv(REPORTS / "segments.csv", index=False)
    daily.reset_index().to_csv(REPORTS / "daily.csv", index=False)
    sensitivity.to_csv(REPORTS / "sensitivity.csv", index=False)
    kept.reset_index().to_parquet(ROOT / "data" / "processed" / "users.parquet", index=False)

    low, high = headline["lift_interval"]
    print(f"users compared: {headline['users']:,} of {len(users):,}")
    print(f"long-view rate: recommended {headline['recommended']:.1%}, random {headline['random']:.1%}")
    print(f"lift: {headline['lift']:.1%} ({low:.1%} to {high:.1%}), {headline['ratio']:.1f}x")
    print(f"smallest detectable lift: {headline['detectable_lift']:.2%}")
    print("\nother signals")
    print(pd.DataFrame(other).T[["recommended", "random", "lift", "ratio"]].round(4).to_string())
    print("\nsegments")
    print(segments.drop(columns=["ratio_low", "ratio_high"]).round(4).to_string(index=False))
    print("\ncut-off sensitivity")
    print(sensitivity.round(4).to_string(index=False))
    print("\nrandomisation checks")
    print(json.dumps(report["randomisation"], indent=2))
    print("\npopularity split")
    print(json.dumps(report["popularity_split"], indent=2))
    print("\ndaily")
    print(daily.round(3).to_string())


if __name__ == "__main__":
    main()
