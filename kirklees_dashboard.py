import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Kirklees APS – Employment, unemployment and inactivity",
    layout="wide",
    page_icon="📈",
)

# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------
periods = [
    "2015-16",
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
]

employment_pct = [70.0, 70.7, 70.5, 71.9, 73.6, 69.9, 73.7, 72.7, 74.1, 76.4]
employment_ci  = [3.1,  3.0,  3.0,  2.8,  3.0,  3.4,  3.4,  3.9,  4.0,  3.2]

unemp_pct = [5.1, 6.4, 4.5, 4.1, 1.8, 5.9, 2.3, 4.8, 3.3, 5.1]
unemp_ci  = [1.7, 1.9, 1.6, 1.5, 1.0, 2.0, 1.3, 2.2, 1.9, 1.8]

inact_pct = [26.2, 24.4, 26.2, 25.0, 25.0, 25.7, 24.6, 23.6, 23.3, 19.5]
inact_ci  = [3.0,  2.9,  2.9,  2.7,  3.0,  3.3,  3.3,  3.8,  3.9,  3.0]

df = pd.DataFrame(
    {
        "Period": periods,
        "Employment_pct": employment_pct,
        "Employment_ci": employment_ci,
        "Unemp_pct": unemp_pct,
        "Unemp_ci": unemp_ci,
        "Inact_pct": inact_pct,
        "Inact_ci": inact_ci,
    }
)

# split at 2021–22
split_period = "2021-22"
split_idx = df.index[df["Period"] == split_period][0]

# ONS colours
PRE_COLOUR = "#959495"
CURR_COLOUR = "#206095"
PRE_SHADE = "rgba(149,148,149,0.25)"
CURR_SHADE = "rgba(32,96,149,0.25)"

# ---------------------------------------------------------
# FIGURE FACTORY
# ---------------------------------------------------------
def make_metric_figure(df, value_col, ci_col, title, y_min, y_max):

    fig = go.Figure()

    # CI bounds
    ci_low = df[value_col] - df[ci_col]
    ci_high = df[value_col] + df[ci_col]

    pre = df.iloc[: split_idx + 1]
    curr = df.iloc[split_idx:]

    pre_low = ci_low.iloc[: split_idx + 1]
    pre_high = ci_high.iloc[: split_idx + 1]
    curr_low = ci_low.iloc[split_idx:]
    curr_high = ci_high.iloc[split_idx:]

    # pre CI
    fig.add_trace(
        go.Scatter(
            x=list(pre["Period"]) + list(pre["Period"][::-1]),
            y=list(pre_low) + list(pre_high[::-1]),
            fill="toself",
            fillcolor=PRE_SHADE,
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # post CI
    fig.add_trace(
        go.Scatter(
            x=list(curr["Period"]) + list(curr["Period"][::-1]),
            y=list(curr_low) + list(curr_high[::-1]),
            fill="toself",
            fillcolor=CURR_SHADE,
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # pre-KBOP line — NO MARKERS
    fig.add_trace(
        go.Scatter(
            x=pre["Period"],
            y=pre[value_col],
            mode="lines",
            line=dict(color=PRE_COLOUR, width=3),
            name="Pre-KBOP period (2015–16 to 2020–21)",
        )
    )

    # KBOP line — NO MARKERS
    fig.add_trace(
        go.Scatter(
            x=curr["Period"],
            y=curr[value_col],
            mode="lines",
            line=dict(color=CURR_COLOUR, width=3),
            name="KBOP period (2021–22 to 2024–25)",
        )
    )

    # Average line
    avg_val = df[value_col].mean()
    fig.add_hline(
        y=avg_val,
        line_dash="dash",
        line_color="#595959",
        annotation_text=f"Average: {avg_val:.1f}%",
        annotation_position="top left",
        annotation_font=dict(size=11, color="#595959"),
    )

    fig.update_layout(
        title=title,
        title_x=0.0,
        margin=dict(l=60, r=40, t=60, b=80),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(
            title="Time period",
            tickmode="array",
            tickvals=df["Period"],
            ticktext=df["Period"],
            tickangle=45,
            showgrid=False,
        ),
        yaxis=dict(
            title="Percent of working-age population",
            range=[y_min, y_max],
            showgrid=True,
            gridcolor="#E5E5E5",
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.02,
        ),
    )

    return fig

# ---------------------------------------------------------
# PAGE CONTENT
# ---------------------------------------------------------
st.markdown(
    "<h1 style='color:#206095;'>Employment, unemployment and economic inactivity over time</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 style='color:#595959;'>Kirklees, age 16–64 – 12-month APS periods</h3>",
    unsafe_allow_html=True,
)

st.plotly_chart(
    make_metric_figure(df, "Employment_pct", "Employment_ci", "Employment rate (16–64)", 60, 80),
    use_container_width=True,
)

st.plotly_chart(
    make_metric_figure(df, "Unemp_pct", "Unemp_ci", "Unemployment rate (16–64)", 0, 8),
    use_container_width=True,
)

st.plotly_chart(
    make_metric_figure(df, "Inact_pct", "Inact_ci", "Economic inactivity rate (16–64)", 15, 30),
    use_container_width=True,
)

st.markdown(
    """
**Source:** ONS Annual Population Survey (APS), Kirklees residents aged 16–64.  
Confidence intervals shown at the 95% level.  
Visual style informed by the ONS design guidance.
"""
)
