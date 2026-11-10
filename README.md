# Recommender Engagement Experiment: what is a recommender worth?

Measures what a video recommender is worth, using an experiment in which a real app replaced some recommended videos with random ones. Each user saw both kinds in the same feed and the same weeks, so each user is their own control.

[![CI](https://github.com/iyerbrah/personalisation-lift/actions/workflows/ci.yml/badge.svg)](https://github.com/iyerbrah/personalisation-lift/actions/workflows/ci.yml)
[![Live app](https://img.shields.io/badge/live-Streamlit%20app-3987e5)](https://personalisation-lift-dkvysrjbxfpijjzcnot9ju.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/license-MIT-199e70)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-3776ab)](requirements.txt)

**[Try the live app →](https://personalisation-lift-dkvysrjbxfpijjzcnot9ju.streamlit.app/)** · Built by [Ram Iyer](https://github.com/iyerbrah) · *Hosted on Streamlit Community Cloud: if it has gone to sleep, click to wake it and give it a minute.*

![The Lift page: recommended videos are watched at length 4.6 times as often as random ones](docs/lift.png)

## Highlights

- **Recommended videos were watched at length 4.6 times as often as random ones.** 36.3% against 7.9%, which is 285 extra long views for every 1,000 videos shown.
- **Most of the gain is matching, not popularity.** About a quarter comes from showing videos that most people like. The other three quarters comes from showing each user the videos that suit them.
- **Every type of user gains by a similar factor.** The ratio is between 4.1x and 4.7x for daily, frequent, occasional and new users.
- **Checked before it's believed.** The random arm really was random, the gap holds on every one of the 17 days, the answer doesn't move with the user cut-off, and the segment intervals are corrected for testing eight groups.
- **Tested like software.** 18 offline tests in CI check the statistics on tables with known answers, that the reports agree with each other, that the README's numbers match the reports, and that all three pages render.
- **Known limit:** videos were randomised, not users, so this measures watching and not retention (see [Limitations](#limitations)).

**Stack:** Python · pandas · NumPy · Plotly · Streamlit · pytest · GitHub Actions

| The headline lift | Who benefits | Popularity or fit |
| --- | --- | --- |
| ![The Lift page: 15,128 users compared, 28.5 points of lift](docs/app.jpg) | ![Lift by type of user, with corrected intervals](docs/who_benefits.jpg) | ![Random videos, the recommended videos shown to anyone, and shown to their user](docs/popularity_fit.jpg) |

## Why I built it

A streaming service cannot tell from its normal logs whether its recommender is good. People watch what they are shown, so a recommended video always looks popular. The only fair test is to show some videos the recommender did not choose, and compare.

Kuaishou, a short-video app, did this for 17 days in 2022 and published the logs as [KuaiRand](https://kuairand.com/). I used them to answer three questions:

1. How much more do people watch recommended videos than random ones?
2. Is that true for every type of user?
3. Is the recommender matching videos to people, or only showing popular videos?

## How it works

```mermaid
flowchart LR
  K[KuaiRand-Pure logs<br/>17 days, 2022] --> B[build_dataset.py<br/>one row per video shown,<br/>recommended or random]
  B --> L[lift.py<br/>per-user lift, bootstrap intervals,<br/>segments, checks, popularity split]
  L --> R[reports/*.json, *.csv]
  R --> A[Streamlit app]
```

## What it does

| Step | What happens |
|---|---|
| 1. Data | The logs become one row per video shown, marked as recommended or random: 27,024 users, 1,361,320 videos shown |
| 2. Lift | Each user's long-view rate on recommended videos is compared with their own rate on random ones |
| 3. Segments | The comparison is repeated for eight types of user |
| 4. Popularity or fit | The lift is split into two parts: choosing well-liked videos, and matching them to the user |
| 5. App | A Streamlit app shows the lift, the segments and the split |

Two terms are used throughout:

- **Long view:** the user watched 18 seconds or more, or the whole video if it is shorter.
- **Lift:** a user's long-view rate on recommended videos minus their rate on random videos.

## How the lift is measured

Every user saw both kinds of video in the same feed and the same weeks, so each user is their own control.

1. For each user, work out the long-view rate on recommended videos and on random videos.
2. Subtract one from the other. That is the user's lift.
3. Average over users. Resample the users 2,000 times to get a 95% interval.

A user needs at least 5 videos of each kind to be compared. That leaves 15,128 of the 27,024 users.

## Results

| | Recommended | Random | Ratio |
|---|---|---|---|
| Watched at length | 36.3% | 7.9% | 4.6x |
| Likes per 1,000 videos | 20.2 | 4.7 | 4.3x |
| Dislikes per 1,000 videos | 0.7 | 1.5 | 0.4x |
| Seconds watched per video | 24.6 | 6.2 | 4.0x |

The lift in long views is 28.5 percentage points (95% interval 28.2 to 28.8). 91% of users had a positive lift.

### By type of user

| Group | Users | Recommended | Random | Ratio |
|---|---|---|---|---|
| Daily | 10,153 | 34.2% | 7.3% | 4.7x |
| Frequent | 3,061 | 39.9% | 8.8% | 4.5x |
| Occasional | 1,355 | 42.8% | 9.3% | 4.6x |
| Rare or new | 548 | 40.9% | 9.9% | 4.1x |

I expected rare and new users to gain much less, because the recommender has little history for them. Their ratio is the lowest, but its interval (3.7 to 4.6) overlaps the others, so this data does not confirm it.

### Popularity or fit

A recommender can do well by picking videos most people like, or by picking the right video for each person. To separate the two, I used each video's long-view rate when it was shown at random. That rate is the video's appeal to an average user.

| Audience | Watched at length |
|---|---|
| Random videos | 7.9% |
| The recommended videos, shown to anyone | 14.8% |
| The recommended videos, shown to their user | 36.4% |

The first step (7.9% to 14.8%) is the gain from choosing well-liked videos: 24% of the lift. The second step (14.8% to 36.4%) is the gain from matching: 76% of the lift. A feed of popular videos alone would capture only a quarter of the gain.

![The Popularity or fit page: random videos, the recommended videos shown to anyone, and shown to their user](docs/popularity_or_fit.png)

## Checks

- **Random videos were spread evenly.** The most-shown 10% of videos took 12% of random showings, against 61% of recommended ones. An even spread would be 10%.
- **The gap holds every day.** On each of the 17 days the recommended rate was between 32% and 38%, and the random rate between 7% and 9%.
- **The user cut-off does not matter.** With a minimum of 1, 3, 5, 10 or 20 videos of each kind, the ratio stays between 4.6x and 4.7x.
- **The sample is large enough.** It could detect a lift as small as 0.4 points.
- **Segments are corrected for multiple tests.** Eight groups are compared, so each interval is widened to keep 95% cover across all of them.

## Key decisions

- **Each user is their own control.** Comparing a user's recommended videos with their own random ones removes differences between heavy and light users, which a pooled average would mix in.
- **Intervals from resampling users, not videos.** Views by the same person aren't independent, so the bootstrap resamples whole users, 2,000 times.
- **A fair split of the gain.** A video's long-view rate when shown at random is its appeal to an average user; giving every recommended video that rate separates choosing popular videos from matching them to people.
- **Corrected for many comparisons.** Eight user groups are compared, so each interval is widened to keep 95% cover across all of them.
- **Checks before claims.** The random arm's spread, every day's gap, and five different user cut-offs are all reported, so the headline can be judged, not just read.

## Limitations

- **This is not a two-group A/B test.** Videos were randomised, not users. It measures what people did with each video, not whether a worse feed makes them leave.
- **Only the pool's videos are compared.** The random videos came from about 7,300 titles, and the recommended side is limited to the same titles. That is a small part of what the app shows.
- **The matching share is a remainder.** It includes anything else that differs between the two kinds of video, such as where in a session each was shown.
- **Rare and new users are under-represented.** Those with five videos of each kind are the more active members of that group.
- **The setting differs from long-form streaming.** These are short videos on a Chinese app in 2022. The method carries over; the numbers may not.

## Repository tour

| Path | What's there |
| --- | --- |
| [`src/build_dataset.py`](src/build_dataset.py) | Raw KuaiRand logs to one row per video shown, marked recommended or random |
| [`src/lift.py`](src/lift.py) | The lift, the bootstrap intervals, the segments, the checks and the popularity split |
| [`app.py`](app.py), [`views/`](views/), [`charts.py`](charts.py) | The Streamlit app: lift, who benefits, popularity or fit |
| [`reports/`](reports/) | The results the app reads |
| [`data/processed/`](data/processed/) | The cleaned dataset and one row per user |
| [`tests/`](tests/) | 18 offline tests: the statistics, report consistency, README numbers, all three pages |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Lint and tests on every pull request |

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/streamlit run app.py
.venv/bin/pytest -q          # 18 tests, all offline
```

The results are in the repo, so the app and the tests run as they are. To rebuild them, download `KuaiRand-Pure.tar.gz` from [Zenodo](https://zenodo.org/records/10439422), unpack it into `data/raw/`, and run:

```bash
python src/build_dataset.py
python src/lift.py
```

## License

The code is under the [MIT license](LICENSE). Data: Gao et al., *KuaiRand: An Unbiased Sequential Recommendation Dataset with Randomly Exposed Videos*, CIKM 2022. The dataset is shared under CC BY-SA 4.0, and the processed files here are shared under the same licence.
