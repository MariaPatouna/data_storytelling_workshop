import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -------------------------------------------------------------
# PAGE SETUP
# -------------------------------------------------------------
st.set_page_config(
    page_title="Kirklees APS – Employment, unemployment, inactivity",
    layout="wide",
    page_icon="📉",
)

st.markdown(
    "<h1 style='text-align:left; color:#1B4F72;'>"
    "Employment, unemployment and economic inactivity over time"
    "</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 style='text-align:left; color:#555555;'>"
    "Kirklees, age 16–64 – 12-month APS periods"
    "</h3>",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# DATA
# -------------------------------------------------------------
data = {
    "Date": [
        "Jul 2015-Jun 2016",
        "Jul 2016-Jun 2017",
        "Jul 2017-Jun 2018",
        "Jul 2018-Jun 2019",
        "Jul 2019-Jun 2020",
        "Jul 2020-Jun 2021",
        "Jul 2021-Jun 2022",
        "Jul 2022-Jun 2023",
        "Jul 2023-Jun 2024",
        "Jul 2024-Jun 2025",
    ],
    "Period_short": [
        "2015–16",
        "2016–17",
        "2017–18",
        "2018–19",
        "2019–20",
        "2020–21",
        "2021–22",
        "2022–23",
        "2023–24",
        "2024–25",
    ],
    "emp_percent": [70.0, 70.7, 70.5, 71.9, 73.6, 69.9, 73.7, 72.7, 74.1, 76.4],
    "emp_conf":    [3.1,  3.0,  3.0,  2.8,  3.0,  3.4,  3.4,  3.9,  4.0,  3.2],
    "unemp_percent": [5.1, 6.4, 4.5, 4.1, 1.8, 5.9, 2.3, 4.8, 3.3, 5.1],
    "unemp_conf":    [1.7, 1.9, 1.6, 1.5, 1.0, 2.0, 1.3, 2.2, 1.9, 1.8],
    "inact_percent": [26.2, 24.4, 26.2, 25.0, 25.0, 25.7, 24.6, 23.6, 23.3, 19.5],
    "inact_conf":    [3.0,  2.9,  2.9,  2.7,  3.0,  3.3,  3.3,  3.8,  3.9,  3.0],
}

df = pd.DataFrame(data)

# CI bounds
for prefix in ["emp", "unemp", "inact"]:
    df[f"{prefix}_lower"] = df[f"{prefix}_percent"] - df[f"{prefix}_conf"]
    df[f"{prefix}_upper"] = df[f"{prefix}_percent"] + df[f"{prefix}_conf"]

# -------------------------------------------------------------
# COLOURS & SPLIT POINT
# -------------------------------------------------------------
PREV_COLOUR = "#959495"     # vintage grey
CURR_COLOUR = "#206095"     # ocean blue
PREV_CI = "rgba(149,148,149,0.25)"
CURR_CI = "rgba(32,96,149,0.25)"

split_idx = df.index[df["Date"] == "Jul 2020-Jun 2021"][0]

# -------------------------------------------------------------
# HELPER TO BUILD A FIGURE
# -------------------------------------------------------------
def make_metric_figure(
    df: pd.DataFrame,
    value_col: str,
    lower_col: str,
    upper_col: str,
    title: str,
    y_range=None,
):
    mean_val = df[value_col].mean()

    prev = df.iloc[: split_idx + 1]
    curr = df.iloc[split_idx:]

    fig = go.Figure()

    # ---- CI band for previous periods (grey) ----
    if len(prev) > 1:
        x_prev = list(prev["Period_short"]) + list(prev["Period_short"][::-1])
        y_prev = list(prev[upper_col]) + list(prev[lower_col][::-1])
        fig.add_trace(
            go.Scatter(
                x=x_prev,
                y=y_prev,
                mode="lines",
                line=dict(width=0),
                fill="toself",
                fillcolor=PREV_CI,
                name="95% confidence interval (previous)",
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # ---- CI band for current periods (blue) ----
    if len(curr) > 1:
        x_curr = list(curr["Period_short"]) + list(curr["Period_short"][::-1])
        y_curr = list(curr[upper_col]) + list(curr[lower_col][::-1])
        fig.add_trace(
            go.Scatter(
                x=x_curr,
                y=y_curr,
                mode="lines",
                line=dict(width=0),
                fill="toself",
                fillcolor=CURR_CI,
                name="95% confidence interval (current)",
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # ---- previous periods line (grey) ----
    fig.add_trace(
        go.Scatter(
            x=prev["Period_short"],
            y=prev[value_col],
            mode="lines+markers",
            line=dict(color=PREV_COLOUR, width=3),
            marker=dict(size=6),
            name="Previous periods",
            hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>",
            showlegend=False,  # keep legend simple
        )
    )

    # ---- current periods line (blue) ----
    fig.add_trace(
        go.Scatter(
            x=curr["Period_short"],
            y=curr[value_col],
            mode="lines+markers",
            line=dict(color=CURR_COLOUR, width=3),
            marker=dict(size=6),
            name="Current periods",
            hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>",
        )
    )

    # ---- average dashed line ----
    fig.add_hline(
        y=mean_val,
        line_dash="dash",
        line_color="#595959",
        annotation_text=f"Average: {mean_val:.1f}%",
        annotation_position="top left",
        annotation_font=dict(size=11, color="#595959"),
    )

    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=18)),
        xaxis=dict(
            title="Time period",
            tickangle=-40,
            showgrid=False,
        ),
        yaxis=dict(
            title="Percent of working-age population",
            rangemode="tozero",
        ),
        margin=dict(l=80, r=40, t=60, b=80),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        hovermode="x unified",
    )

    if y_range is not None:
        fig.update_yaxes(range=y_range)

    return fig

# -------------------------------------------------------------
# CHARTS (VERTICAL STACK)
# -------------------------------------------------------------
fig_emp = make_metric_figure(
    df,
    "emp_percent",
    "emp_lower",
    "emp_upper",
    "Employment rate (16–64)",
    y_range=[60, 80],
)

fig_unemp = make_metric_figure(
    df,
    "unemp_percent",
    "unemp_lower",
    "unemp_upper",
    "Unemployment rate (16–64)",
    y_range=[0, 8],
)

fig_inact = make_metric_figure(
    df,
    "inact_percent",
    "inact_lower",
    "inact_upper",
    "Economic inactivity rate (16–64)",
    y_range=[15, 30],
)

st.plotly_chart(fig_emp, use_container_width=True)
st.plotly_chart(fig_unemp, use_container_width=True)
st.plotly_chart(fig_inact, use_container_width=True)

# -------------------------------------------------------------
# FOOTNOTE / SOURCE
# -------------------------------------------------------------
st.markdown(
    """
**Source:** Annual Population Survey, Office for National Statistics (APS 12-month periods).  
95% confidence intervals shown as shaded bands.  
[ONS visualisation guidance](https://ons-design.notion.site/314386f7916e497baae8118a782911f5?v=d7efdd82e8884f548a6c79eda2d0b2e4&source=copy_link)
"""
)
