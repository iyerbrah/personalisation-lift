"""Data loading and the chart pieces the pages share."""
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent

# Fixed colour per arm, the same in every chart.
COLORS = {"recommended": "#3987e5", "random": "#898781", "anyone": "#199e70"}
MUTED = "#898781"


@st.cache_data
def load_report():
    return json.loads((ROOT / "reports" / "lift.json").read_text())


@st.cache_data
def load_csv(name):
    return pd.read_csv(ROOT / "reports" / name)


@st.cache_data
def load_users():
    return pd.read_parquet(ROOT / "data" / "processed" / "users.parquet")


def rate_bars(labels, rates, colors, height=300):
    """Horizontal bars of long-view rates, each labelled with its value."""
    fig = go.Figure(go.Bar(
        x=rates, y=labels, orientation="h", marker_color=colors,
        text=[f"{rate:.1%}" for rate in rates], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:.1%}<extra></extra>",
    ))
    fig.update_layout(
        height=height, margin=dict(l=10, r=40, t=10, b=10),
        xaxis=dict(title="Share of videos watched at length", tickformat=".0%", range=[0, max(rates) * 1.2]),
        yaxis=dict(autorange="reversed"),
    )
    return fig
