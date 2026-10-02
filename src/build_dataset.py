"""Turn the KuaiRand-Pure logs into one row per video shown, for the weeks the experiment ran.

Between 22 April and 8 May 2022 the app replaced some recommended videos with ones drawn
at random from a fixed pool. Each row here is one video shown to one user in that period,
marked as recommended or random, with what the user did.

Run:  python src/build_dataset.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "KuaiRand-Pure" / "data"
OUT = ROOT / "data" / "processed"

MAIN_FEED = 1   # 99% of random videos were shown in this feed, so the comparison stays inside it

# The app's activity labels, grouped so that every segment has enough users to measure.
ACTIVITY = {
    "full_active": "Daily", "high_active": "Frequent", "middle_active": "Occasional",
    "low_active": "Rare or new", "single_low_active": "Rare or new",
    "2_14_day_new": "Rare or new", "day_new": "Rare or new",
}
TENURE = {
    "15-30": "Under 6 months", "31-60": "Under 6 months", "61-90": "Under 6 months",
    "91-180": "Under 6 months", "181-365": "6 to 12 months", "366-730": "1 to 2 years",
    "730+": "Over 2 years",
}


def main():
    random = pd.read_csv(RAW / "log_random_4_22_to_5_08_pure.csv")
    standard = pd.read_csv(RAW / "log_standard_4_22_to_5_08_pure.csv")
    users = pd.read_csv(RAW / "user_features_pure.csv")
    print(f"rows read:        {len(random):,} random, {len(standard):,} recommended")

    df = pd.concat([random, standard], ignore_index=True)
    print(f"feeds, random:    {random.tab.value_counts(normalize=True).round(3).head(3).to_dict()}")
    df = df[df.tab == MAIN_FEED]
    # long_view is defined from the video's length, so rows with no recorded length can't be trusted.
    df = df[df.duration_ms > 0]

    users["activity"] = users.user_active_degree.map(ACTIVITY)
    users["tenure"] = users.register_days_range.map(TENURE)
    df = df.merge(users[["user_id", "activity", "tenure"]], on="user_id", how="left")

    df["duration_s"] = df.duration_ms / 1000
    # Videos loop, so watch time is capped at one full play.
    df["watch_s"] = df[["play_time_ms", "duration_ms"]].min(axis=1) / 1000
    df = df[["user_id", "video_id", "date", "is_rand", "long_view", "is_like", "is_hate",
             "watch_s", "duration_s", "activity", "tenure"]]

    OUT.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT / "exposures.parquet", index=False)

    print(f"rows kept:        {(df.is_rand == 1).sum():,} random, {(df.is_rand == 0).sum():,} recommended")
    print(f"users:            {df.user_id.nunique():,}")
    print(f"videos:           {df.video_id.nunique():,}")
    print(f"dates:            {df.date.min()} to {df.date.max()}")
    print(df.groupby("is_rand")[["long_view", "is_like", "is_hate", "watch_s"]].mean().round(4).to_string())


if __name__ == "__main__":
    main()
