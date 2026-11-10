"""The statistics in src/lift.py, on small tables where the right answer is known."""
import numpy as np
import pandas as pd
import pytest

from lift import cramers_v, interval, lift_summary, per_user, top_share


def test_per_user_rates():
    df = pd.DataFrame({"user_id": [1, 1, 1, 2, 2], "is_rand": [0, 0, 1, 0, 1], "long_view": [1, 0, 0, 1, 1]})
    users = per_user(df, "long_view")
    assert users.loc[1, "recommended"] == 0.5 and users.loc[1, "random"] == 0.0
    assert users.loc[2, "recommended"] == 1.0 and users.loc[2, "random"] == 1.0


def test_lift_summary_on_a_known_table():
    users = pd.DataFrame({"recommended": [0.5, 0.3, 0.4, 0.4], "random": [0.1, 0.1, 0.1, 0.1]})
    s = lift_summary(users, np.random.default_rng(0))
    assert s["users"] == 4
    assert s["lift"] == pytest.approx(0.3)
    assert s["ratio"] == pytest.approx(4.0)
    low, high = s["lift_interval"]
    assert low <= s["lift"] <= high


def test_no_difference_means_no_lift():
    users = pd.DataFrame({"recommended": [0.2] * 50, "random": [0.2] * 50})
    s = lift_summary(users, np.random.default_rng(0))
    assert s["lift"] == 0 and s["ratio"] == 1
    assert s["lift_interval"] == [0.0, 0.0]


def test_interval_covers_the_middle():
    low, high = interval(np.arange(1001))
    assert low == pytest.approx(25) and high == pytest.approx(975)


def test_top_share():
    assert top_share(np.ones(10)) == pytest.approx(0.1)          # perfectly even
    assert top_share(np.array([91] + [1] * 9)) == pytest.approx(0.91)


def test_cramers_v():
    a = pd.Series(list("xxyyxxyy"))
    assert cramers_v(a, a) == pytest.approx(1.0)                  # one decides the other
    assert cramers_v(a, pd.Series(list("ppppqqqq"))) == pytest.approx(0.0)
