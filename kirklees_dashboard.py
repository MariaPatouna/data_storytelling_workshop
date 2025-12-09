import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -------------------------------------------------------
# PAGE SETUP
# -------------------------------------------------------
st.set_page_config(
    page_title="Kirklees labour market – APS",
    layout="wide",
    page_icon="📉",
)

st.markdown(
    "<h1 style='color:#1B4F72;'>Employment, unemployment and economic inactivity over time</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 style='color:#4D4D4D;'>Kirklees, age 16–64 – 12-month APS periods</h3>",
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# DATA
# -------------------------------------------------------
data = [
    {"Period": "Jul 2015-Jun 2016", "emp_pct": 70.0, "emp_conf": 3.1,
     "unemp_pct": 5.1, "unemp_conf": 1.7, "inactive_pct": 26.2, "inactive_conf": 3.0},
    {"Period": "Jul 2016-Jun 2017", "emp_pct": 70.7, "emp_conf": 3.0,
     "unemp_pct": 6.4, "unemp_conf": 1.9, "inactive_pct": 24.4, "inactive_conf": 2.9},
    {"Period": "Jul 2017-Jun 2018", "emp_pct": 70.5, "emp_conf": 3.0,
     "unemp_pct": 4.5, "unemp_conf": 1.6, "inactive_pct": 26.2, "inactive_conf": 2.9},
    {"Period": "Jul 2018-Jun 2019", "emp_pct": 71.9, "emp_conf": 2.8,
     "unemp_pct": 4.1, "unemp_conf": 1.5, "inactive_pct": 25.0, "inactive_conf": 2.7},
    {"Period": "Jul 2019-Jun 2020", "emp_pct": 73.6, "emp_conf": 3.0,
     "unemp_pct": 1.8, "unemp_conf": 1.0, "inactive_pct": 25.0, "inactive_conf": 3.0},
    {"Period": "Jul 2020-Jun 2021", "emp_pct": 69.9, "emp_conf": 3.4,
     "unemp_pct": 5.9, "unemp_conf": 2.0, "inactive_pct": 25.7, "inactive_conf": 3.3},
    {"Period": "Jul 2021-Jun 2022", "emp_pct": 73.7, "emp_conf": 3.4,
     "unemp_pct": 2.3, "unemp_conf": 1.3, "inactive_pct": 24.6, "inactive_conf": 3.3},
    {"Period": "Jul 2022-Jun 2023", "emp_pct": 72.7, "emp_conf": 3.9,
     "unemp_pct": 4.8, "unemp_conf": 2.2, "inactive_pct": 23.6, "inactive_conf": 3.8},
    {"Period": "Jul 2023-Jun 2024", "emp_pct": 74.1, "emp_conf": 4.0,
     "unemp_pct": 3.3, "unemp_conf": 1.9, "inactive_pct": 23.3, "inactive_conf": 3.9},
    {"Period": "Jul 2024-Jun 2025", "emp_pct": 76.4, "emp_conf": 3.2,
     "unemp_pct": 5.1, "unemp_conf": 1.8, "inactive_pct": 19.5, "inactive_conf": 3.0},
]

df = pd.DataFrame(data)

# Short, reader-friendly period labels: e.g. "2015–16"
df["Period_short"] = df["Period"].str.slice(4, 8) + "–" + df["Period"].str.slice(-2)

# CI bounds
df["emp_low"] = df["emp_pct"] - df["emp_conf"]
df["emp_high"] = df["emp_pct"] + df["emp_conf"]

df["unemp_low"] = df["unemp_pct"] - df["unemp_conf"]
df["unemp_high"] = df["unemp_pct"] + df["unemp_conf"]

df["inactive_low"] = df["inactive_pct"] - df["inactive_conf"]
df["inactive_high"] = df["inactive_pct"] + df["inactive_conf"]

# Ensure categorical order along x-axis
df["Period_short"] = pd.Categorical(df["Period_short"], categories=list(df["Period_short"]), ordered=True)

# -------------------------------------------------------
# HELPER: CI LINE CHART
# -------------------------------------------------------
def make_ci_chart(
    x,
    y,
    low,
    high,
    title,
    colour_line,
    colour_band,
    y_range=None,
):
    fig = go.Figure()

    # CI band (lower then upper, filled)
    fig.add_trace(
        go.Scatter(
            x=x,
            y=low,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=high,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor=colour_band,
            name="95% CI",
            hoverinfo="skip",
        )
    )

    # Central estimate line
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines+markers",
            line=dict(color=colour_line, width=3),
            marker=dict(size=6),
            name="Estimate",
        )
    )

    fig.update_layout(
        title=title,
        template="simple_white",
        height=350,
        margin=dict(l=40, r=20, t=60, b=60),
        xaxis=dict(
            title="12-month APS period",
            tickangle=45,
            showgrid=False,
        ),
        yaxis=dict(
            title="Percent of working-age population",
            range=y_range,
            gridcolor="#D8DDE0",
            zeroline=False,
        ),
        showlegend=False,
    )

    return fig


# -------------------------------------------------------
# THREE GRAPHS SIDE BY SIDE
# -------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    fig_emp = make_ci_chart(
        x=df["Period_short"],
        y=df["emp_pct"],
        low=df["emp_low"],
        high=df["emp_high"],
        title="Employment rate (16–64)",
        colour_line="#12436D",           # ONS dark blue
        colour_band="rgba(18,67,109,0.15)",
        y_range=[60, 80],
    )
    st.plotly_chart(fig_emp, use_container_width=True)

with col2:
    fig_unemp = make_ci_chart(
        x=df["Period_short"],
        y=df["unemp_pct"],
        low=df["unemp_low"],
        high=df["unemp_high"],
        title="Unemployment rate (16–64)",
        colour_line="#D4351C",           # ONS red
        colour_band="rgba(212,53,28,0.15)",
        y_range=[0, 8],
    )
    st.plotly_chart(fig_unemp, use_container_width=True)

with col3:
    fig_inact = make_ci_chart(
        x=df["Period_short"],
        y=df["inactive_pct"],
        low=df["inactive_low"],
        high=df["inactive_high"],
        title="Economic inactivity rate (16–64)",
        colour_line="#6B6E72",           # ONS grey
        colour_band="rgba(107,110,114,0.15)",
        y_range=[15, 30],
    )
    st.plotly_chart(fig_inact, use_container_width=True)

# -------------------------------------------------------
# SOURCE NOTE (minimal text)
# -------------------------------------------------------
st.markdown(
    """
    **Source:** Annual Population Survey (APS), ONS.  
    12-month periods ending June; estimates for Kirklees local authority, age 16–64.  
    Shaded bands show ±95% confidence intervals around the percentage estimates.
    """
)
