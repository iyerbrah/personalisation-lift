"""Popularity or fit page: how much of the lift is choosing good videos, and how much is matching."""
import streamlit as st

from charts import COLORS, load_report, rate_bars

split = load_report()["popularity_split"]
low, high = split["video_choice_share_interval"]

st.title("Popularity or fit")
st.write("A recommender can do well in two ways: by picking videos that most people like, "
         "or by picking the right video for each person. This page separates the two.")

st.subheader("Three audiences for the same feed")
st.plotly_chart(rate_bars(
    ["Random videos", "The recommended videos, shown to anyone", "The recommended videos, shown to their user"],
    [split["random"], split["same_videos_to_anyone"], split["recommended"]],
    [COLORS["random"], COLORS["anyone"], COLORS["recommended"]], height=260), width="stretch")
st.caption("The middle bar uses each video's long-view rate when it was shown at random. "
           "That rate is the video's appeal to an average user.")

choice, fit = st.columns(2)
choice.metric(f"From choosing well-liked videos ({split['video_choice_share']:.0%} of the lift)",
              f"{split['from_video_choice'] * 100:.1f} pts")
fit.metric(f"From matching video to user ({1 - split['video_choice_share']:.0%} of the lift)",
           f"{split['from_personal_fit'] * 100:.1f} pts")

st.subheader("How it is worked out")
st.markdown(
    "1. Each video was shown at random to many users. Its long-view rate there is its general appeal.\n"
    "2. Every recommended video is given that rate. The average is what the recommended videos "
    "would have earned if shown to anyone.\n"
    "3. The step from random to that figure is the gain from choosing well-liked videos.\n"
    "4. The step from that figure to the real rate is the gain from matching.")

st.info(f"**Conclusion.** About {split['video_choice_share']:.0%} of the lift "
        f"(95% interval {low:.0%} to {high:.0%}) comes from showing videos that most people like. "
        "The rest comes from showing each user the videos that suit them. "
        "A feed of popular videos alone would capture only a quarter of the gain.",
        icon=":material/lightbulb:")
st.caption("Limitation: the matching share is what is left over, so it also includes anything else that differs "
           "between the two kinds of video, such as where in a session each was shown.")
