"""Who benefits page: the lift for each type of user."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from charts import COLORS, load_csv

TRAITS = {"activity": "How often they use the app", "tenure": "How long since they joined"}

segments = load_csv("segments.csv")

st.title("Who benefits")
st.write("The same comparison, split by type of user.")

trait = st.segmented_control("Split users by", list(TRAITS), format_func=TRAITS.get, default="activity",
                             required=True)
part = segments[segments.trait == trait]

fig = go.Figure(go.Bar(
    x=part.group, y=part.lift, marker_color=COLORS["recommended"],
    error_y=dict(type="data", symmetric=False, array=part.lift_high - part.lift,
                 arrayminus=part.lift - part.lift_low, color="#d7d5cf", thickness=1.5),
    hovertemplate="%{x}: %{y:.1%}<extra></extra>",
))
fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10),
                  yaxis=dict(title="Lift in share watched at length", tickformat=".0%", rangemode="tozero"))
st.plotly_chart(fig, width="stretch")
st.caption("Bars show each group's interval. Eight groups are tested, so the intervals are widened "
           "to keep 95% cover across all of them.")

st.dataframe(pd.DataFrame({
    "Group": part.group,
    "Users": [f"{n:,}" for n in part.users],
    "Recommended": [f"{rate:.1%}" for rate in part.recommended],
    "Random": [f"{rate:.1%}" for rate in part["random"]],
    "Lift": [f"{value * 100:.1f} pts" for value in part.lift],
    "Ratio": [f"{row.ratio:.1f}x ({row.ratio_low:.1f} to {row.ratio_high:.1f})" for row in part.itertuples()],
}), width="stretch", hide_index=True)

st.subheader("Observations")
activity = segments[segments.trait == "activity"].set_index("group")
st.markdown(
    f"- Every group watches recommended videos at length about four to five times as often as random ones.\n"
    f"- Daily users have the smallest lift in points ({activity.lift['Daily'] * 100:.1f}), because they watch "
    f"less of everything: {activity['random']['Daily']:.1%} of random videos against "
    f"{activity['random']['Occasional']:.1%} for occasional users.\n"
    f"- Rare and new users have the lowest ratio ({activity.ratio['Rare or new']:.1f}x), but only "
    f"{activity.users['Rare or new']:,} of them had enough videos to compare, and their interval "
    f"overlaps the other groups'.")
st.info("**Conclusion.** The recommender helps every type of user by a similar factor. "
        "There is a hint that it does less for rare and new users, where it has the least history "
        "to work from, but this sample is too small to confirm it.",
        icon=":material/lightbulb:")
st.caption("Limitation: rare and new users who saw five videos of each kind are the more active "
           "members of that group, so they may not represent it.")
