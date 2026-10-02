# Personalisation Lift

Measures what a video recommender is worth, using an experiment in which a real app replaced some recommended videos with random ones.

**Try it:** _add the Streamlit link after deploying_

## The finding

Users watched recommended videos at length **4.6 times** as often as random ones: 36.3% against 7.9%. That is 285 extra long views for every 1,000 videos shown.

About a quarter of that gain comes from showing videos that most people like. The other three quarters comes from showing each user the videos that suit them.

## Why I built it

A streaming service cannot tell from its normal logs whether its recommender is good. People watch what they are shown, so a recommended video always looks popular. The only fair test is to show some videos that the recommender did not choose, and compare.

Kuaishou, a short-video app, did this for 17 days in 2022 and published the logs as [KuaiRand](https://kuairand.com/). I used them to answer three questions:

1. How much more do people watch recommended videos than random ones?
2. Is that true for every type of user?
3. Is the recommender matching videos to people, or only showing popular videos?

## The data

| | |
|---|---|
| Period | 22 April to 8 May 2022 |
| Users | 27,024 |
| Random videos shown | 1,141,393 |
| Recommended videos shown | 219,927 |
| Videos in the pool | about 7,300 |

Each row is one video shown to one user, with how long they watched. The outcome is a **long view**: 18 seconds or more, or the whole video if it is shorter.

Only the app's main feed is used, because 99% of the random videos were shown there.

## How the lift is measured

Every user saw both kinds of video, so each user is their own control.

1. For each user, work out the long-view rate on recommended videos and on random videos.
2. Subtract one from the other. That is the user's lift.
3. Average over users. Resample the users 2,000 times to get a 95% interval.

A user needs at least 5 videos of each kind to be compared. That leaves 15,128 users.

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

The ratio is about the same for every group. I expected rare and new users to gain much less, because the recommender has little history for them. Their ratio is the lowest, but its interval (3.7 to 4.6) overlaps the others, so this data does not confirm it.

### Popularity or fit

Each video was shown at random to many users, so its long-view rate there is its appeal to an average user. Giving every recommended video that rate shows what the same videos would have earned if shown to anyone.

| Audience | Watched at length |
|---|---|
| Random videos | 7.9% |
| The recommended videos, shown to anyone | 14.8% |
| The recommended videos, shown to their user | 36.4% |

So 24% of the lift (95% interval 24% to 25%) comes from choosing well-liked videos, and 76% from matching them to the user. A feed of popular videos alone would capture only a quarter of the gain.

## Checks

- **Random videos were spread evenly.** The most-shown 10% of videos took 12% of random showings, against 61% of recommended ones. An even spread would be 10%.
- **The gap holds every day.** On each of the 17 days the recommended rate was between 32% and 38% and the random rate between 7% and 9%.
- **The user cut-off does not matter.** With a minimum of 1, 3, 5, 10 or 20 videos of each kind, the ratio stays between 4.6x and 4.7x.
- **The sample is large enough.** It could detect a lift as small as 0.4 points.
- **Segments are corrected for multiple tests.** Eight groups are compared, so each interval is widened to keep 95% cover across all of them.

## Limitations

- **This is not a two-group A/B test.** Videos were randomised, not users. It measures what people did with each video, not whether a worse feed makes them leave.
- **Only the pool's videos are compared.** The random videos came from about 7,300 titles, and the recommended side is limited to the same titles. That is a small part of what the app shows.
- **The matching share is a remainder.** It includes anything else that differs between the two kinds of video, such as where in a session each was shown.
- **Rare and new users are under-represented.** Those with five videos of each kind are the more active members of that group.
- **The setting is different from long-form streaming.** These are short videos on a Chinese app in 2022. The method carries over; the numbers may not.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

The results are in the repo, so the app runs as is. To rebuild them, download `KuaiRand-Pure.tar.gz` from [Zenodo](https://zenodo.org/records/10439422), unpack it into `data/raw/`, and run:

```bash
python src/build_dataset.py
python src/lift.py
```

## Files

```
app.py                 Entry point: sidebar and page navigation
views/                 The three pages: lift, who benefits, popularity or fit
charts.py              Data loading and the chart both result pages use
src/build_dataset.py   Raw logs to one row per video shown
src/lift.py            The lift, the segments, the checks and the popularity split
reports/               Results the app reads
data/processed/        The cleaned dataset and one row per user
```

Data: Gao et al., *KuaiRand: An Unbiased Sequential Recommendation Dataset with Randomly Exposed Videos*, CIKM 2022. The dataset is shared under CC BY-SA 4.0, and the processed files here are shared under the same licence.
