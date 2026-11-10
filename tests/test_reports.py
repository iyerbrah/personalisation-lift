"""The committed results agree with each other and with the per-user table the app reads."""
import json

import pandas as pd
import pytest

REPORT = json.load(open("reports/lift.json"))
USERS = pd.read_parquet("data/processed/users.parquet")


def test_every_compared_user_meets_the_cutoff():
    assert len(USERS) == REPORT["headline"]["users"]
    assert (USERS.n_recommended >= REPORT["min_exposures"]).all()
    assert (USERS.n_random >= REPORT["min_exposures"]).all()


def test_headline_is_the_average_over_users():
    assert USERS.recommended.mean() == pytest.approx(REPORT["headline"]["recommended"])
    assert USERS["random"].mean() == pytest.approx(REPORT["headline"]["random"])
    assert (USERS.recommended - USERS["random"]).mean() == pytest.approx(REPORT["headline"]["lift"])


def test_interval_contains_the_estimate():
    low, high = REPORT["headline"]["lift_interval"]
    assert low < REPORT["headline"]["lift"] < high


def test_popularity_split_adds_up():
    split = REPORT["popularity_split"]
    total = split["recommended"] - split["random"]
    assert split["from_video_choice"] + split["from_personal_fit"] == pytest.approx(total)
    assert split["video_choice_share"] == pytest.approx(split["from_video_choice"] / total)


def test_every_day_shows_the_same_gap():
    daily = pd.read_csv("reports/daily.csv")
    assert len(daily) == 17
    assert (daily.recommended > 3 * daily["random"]).all()
