"""Lift page: recommended against random, and the checks behind the comparison."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from charts import COLORS, MUTED, load_csv, load_report, load_users, rate_bars

report = load_report()
headline = report["headline"]
low, high = headline["lift_interval"]

st.title("Recommender engagement experiment")
st.write("What a recommender is worth: the share of videos watched at length, for videos it chose "
         "and for videos chosen at random, shown to the same users in the same feed.")

users, lift, ratio, per_thousand = st.columns(4)
users.metric("Users compared", f"{headline['users']:,}")
lift.metric("Lift", f"{headline['lift'] * 100:.1f} pts")
ratio.metric("Ratio", f"{headline['ratio']:.1f}x")
per_thousand.metric("Extra long views per 1,000", f"{headline['lift'] * 1000:.0f}")

st.subheader("Recommended against random")
st.plotly_chart(rate_bars(["Recommended", "Random"], [headline["recommended"], headline["random"]],
                          [COLORS["recommended"], COLORS["random"]], height=220), width="stretch")
st.caption(f"Lift is {headline['lift'] * 100:.1f} percentage points "
           f"(95% interval {low * 100:.1f} to {high * 100:.1f}). "
           "A long view is 18 seconds or more, or the whole video if it is shorter.")

st.subheader("Other signals")
labels = {"is_like": "Likes per 1,000 videos", "is_hate": "Dislikes per 1,000 videos",
          "watch_s": "Seconds watched per video"}
scale = {"is_like": 1000, "is_hate": 1000, "watch_s": 1}
st.dataframe(pd.DataFrame([{
    "Signal": labels[metric],
    "Recommended": f"{result['recommended'] * scale[metric]:.1f}",
    "Random": f"{result['random'] * scale[metric]:.1f}",
    "Ratio": f"{result['ratio']:.1f}x",
} for metric, result in report["other_signals"].items()]), width="stretch", hide_index=True)

st.subheader("User by user")
table = load_users()
fig = go.Figure(go.Histogram(x=table.lift, xbins=dict(start=-1, end=1, size=0.05),
                             marker_color=COLORS["recommended"], hovertemplate="%{x}: %{y} users<extra></extra>"))
fig.add_vline(x=0, line_dash="dash", line_color=MUTED, line_width=1)
fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), bargap=0.05,
                  xaxis=dict(title="A user's lift (recommended rate minus random rate)", tickformat=".0%"),
                  yaxis=dict(title="Users"))
st.plotly_chart(fig, width="stretch")
st.caption(f"{(table.lift > 0).mean():.0%} of users watched recommended videos at length more often than random ones.")

st.subheader("Day by day")
daily = load_csv("daily.csv")
dates = pd.to_datetime(daily.date.astype(str))
fig = go.Figure()
for arm in ("recommended", "random"):
    fig.add_trace(go.Scatter(x=dates, y=daily[arm], mode="lines+markers", name=arm.capitalize(),
                             line=dict(color=COLORS[arm], width=2), hovertemplate="%{y:.1%}"))
fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified",
                  yaxis=dict(title="Share watched at length", tickformat=".0%", rangemode="tozero"),
                  legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
st.plotly_chart(fig, width="stretch")
st.caption("The gap holds on every one of the 17 days, so no single day drives the result.")

st.subheader("Checks")
checks = report["randomisation"]
sensitivity = load_csv("sensitivity.csv")
st.markdown(
    f"- **Random videos were spread evenly.** The most-shown 10% of videos took "
    f"{checks['random']['top_10pct_videos_share']:.0%} of random showings, against "
    f"{checks['recommended']['top_10pct_videos_share']:.0%} of recommended ones. An even spread would be 10%.\n"
    f"- **The user cut-off does not drive the result.** Users needed {report['min_exposures']} videos of each "
    f"kind to be compared. From 1 to 20, the ratio stays between "
    f"{sensitivity.ratio.min():.1f}x and {sensitivity.ratio.max():.1f}x.\n"
    f"- **The sample is large enough.** It could detect a lift as small as "
    f"{headline['detectable_lift'] * 100:.1f} points.")
st.dataframe(pd.DataFrame({
    "Minimum videos of each kind": sensitivity.min_exposures,
    "Users": [f"{n:,}" for n in sensitivity.users],
    "Recommended": [f"{rate:.1%}" for rate in sensitivity.recommended],
    "Random": [f"{rate:.1%}" for rate in sensitivity["random"]],
    "Ratio": [f"{value:.1f}x" for value in sensitivity.ratio],
}), width="stretch", hide_index=True)

st.info(f"**Conclusion.** Users watched recommended videos at length {headline['ratio']:.1f} times as often "
        "as random ones, liked them more and disliked them less.", icon=":material/lightbulb:")
st.caption("Limitation: this measures what users did with each video, not whether they came back. "
           "Only videos from the experiment's pool of about 7,300 are compared.")
