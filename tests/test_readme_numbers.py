"""Every number the README quotes comes from the committed reports, so the two can't drift apart."""
import json

import pandas as pd

README = open("README.md", encoding="utf-8").read()
REPORT = json.load(open("reports/lift.json"))
USERS = pd.read_parquet("data/processed/users.parquet")
H = REPORT["headline"]


def test_headline():
    assert f"{H['recommended']:.1%} against {H['random']:.1%}" in README
    assert f"{H['ratio']:.1f} times as often" in README
    low, high = H["lift_interval"]
    assert f"{H['lift'] * 100:.1f} percentage points (95% interval {low * 100:.1f} to {high * 100:.1f})" in README
    assert f"{(USERS.lift > 0).mean():.0%} of users had a positive lift" in README


def test_dataset_size():
    shown = REPORT["exposures"]["recommended"] + REPORT["exposures"]["random"]
    assert f"{REPORT['users_total']:,} users, {shown:,} videos shown" in README
    assert f"That leaves {H['users']:,} of the {REPORT['users_total']:,} users" in README


def test_segments_table():
    segments = pd.read_csv("reports/segments.csv")
    for row in segments[segments.trait == "activity"].itertuples():
        assert f"| {row.group} | {row.users:,} | {row.recommended:.1%} | {row.random:.1%} | {row.ratio:.1f}x |" in README


def test_popularity_split():
    split = REPORT["popularity_split"]
    assert f"| The recommended videos, shown to anyone | {split['same_videos_to_anyone']:.1%} |" in README
    assert f"{split['video_choice_share']:.0%} of the lift" in README
    assert f"{1 - split['video_choice_share']:.0%} of the lift" in README
