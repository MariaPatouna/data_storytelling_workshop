import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -------------------------------------------------------
# PAGE CONFIG & SIMPLE STYLING
# -------------------------------------------------------
st.set_page_config(
    page_title="Kirklees labour market – APS trends",
    layout="wide",
    page_icon="📈",
)

st.markdown(
    """
    <style>
    * { font-family: "Verdana", sans-serif; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# DATA
# -------------------------------------------------------

# Raw APS table coded directly
data = [
    # Period label, employment %, employment CI, unemployment %, unemployment CI,
    # inactivity %, inactivity CI
    ("Jul 2015-Jun 2016", 70.0, 3.1, 5.1, 1.7, 26.2, 3.0),
    ("Jul 2016-Jun 2017", 70.7, 3.0, 6.4, 1.9, 24.4, 2.9),
    ("Jul 2017-Jun 2018", 70.5, 3.0, 4.5, 1.6, 26.2, 2.9),
    ("Jul 2018-Jun 2019", 71.9, 2.8, 4.1, 1.5, 25.0, 2.7),
    ("Jul 2019-Jun 2020", 73.6, 3.0, 1.8, 1.0, 25.0, 3.0),
    ("Jul 2020-Jun 2021", 69.9, 3.4, 5.9, 2.0, 25.7, 3.3),
    ("Jul 2021-Jun 2022", 73.7, 3.4, 2.3, 1.3, 24.6, 3.3),
    ("Jul 2022-Jun 2023", 72.7, 3.9, 4.8, 2.2, 23.6, 3.8),
    ("Jul 2023-Jun 2024", 74.1, 4.0, 3.3, 1.9, 23.3, 3.9),
    ("Jul 2024-Jun 2025", 76.4, 3.2, 5.1, 1.8, 19.5, 3.0),
]

df = pd.DataFrame(
    data,
    columns=[
        "RawPeriod",
        "employment_rate",
        "employment_ci",
        "unemployment_rate",
        "unemployment_ci",
        "inactive_rate",
        "inactive_ci",
    ],
)

# Shorter period labels for the x-axis
short_labels = [
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
]
df["Period"] = pd.Categorical(short_labels, categories=short_labels, ordered=True)

# Pre-KBOP vs KBOP split: first 6 rows are pre, remaining are KBOP
df["is_kbop"] = False
df.loc[df.index >= 6, "is_kbop"] = True

# Compute upper / lower CI bounds
for prefix in ["employment", "unemployment", "inactive"]:
    df[f"{prefix}_upper"] = df[f"{prefix}_rate"] + df[f"{prefix}_ci"]
    df[f"{prefix}_lower"] = df[f"{prefix}_rate"] - df[f"{prefix}_ci"]

# -------------------------------------------------------
# COLOURS (ONS STYLE)
# -------------------------------------------------------
PRE_COLOUR = "#959495"                     # Vintage grey
CURR_COLOUR = "#206095"                    # Ocean blue
PRE_FILL = "rgba(149,148,149,0.25)"
CURR_FILL = "rgba(32,96,149,0.25)"
AVG_LINE_COLOUR = "#595959"

# -------------------------------------------------------
# HELPER: CREATE FIGURE FOR ONE INDICATOR
# -------------------------------------------------------
def create_indicator_figure(
    df,
    value_col,
    ci_col,
    title,
    y_range,
):
    upper_col = f"{value_col.rsplit('_', 1)[0]}_upper"
    lower_col = f"{value_col.rsplit('_', 1)[0]}_lower"

    # Split into pre-KBOP and KBOP periods
    pre = df[~df["is_kbop"]].copy()
    cur = df[df["is_kbop"]].copy()

    fig = go.Figure()

    # --- Pre-KBOP CI ribbon (grey) ---
    fig.add_trace(
        go.Scatter(
            x=pre["Period"],
            y=pre[upper_col],
            mode="lines",
            line=dict(width=0, color="rgba(0,0,0,0)"),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=pre["Period"],
            y=pre[lower_col],
            mode="lines",
            line=dict(width=0, color="rgba(0,0,0,0)"),
            fill="tonexty",
            fillcolor=PRE_FILL,
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # --- KBOP CI ribbon (blue) ---
    fig.add_trace(
        go.Scatter(
            x=cur["Period"],
            y=cur[upper_col],
            mode="lines",
            line=dict(width=0, color="rgba(0,0,0,0)"),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=cur["Period"],
            y=cur[lower_col],
            mode="lines",
            line=dict(width=0, color="rgba(0,0,0,0)"),
            fill="tonexty",
            fillcolor=CURR_FILL,
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # --- Pre-KBOP line (no markers) ---
    fig.add_trace(
        go.Scatter(
            x=pre["Period"],
            y=pre[value_col],
            mode="lines",
            line=dict(color=PRE_COLOUR, width=2.5),
            name="Pre-KBOP periods (2015–16 to 2020–21)",
            showlegend=True,
        )
    )

    # --- KBOP line (no markers; this is what we changed) ---
    fig.add_trace(
        go.Scatter(
            x=cur["Period"],
            y=cur[value_col],
            mode="lines",
            line=dict(color=CURR_COLOUR, width=3),
            marker=dict(size=0),
            name="KBOP periods (2021–22 to 2024–25)",
            showlegend=True,
        )
    )

    # --- Dashed average line across all years ---
    avg_val = df[value_col].mean()
    fig.add_hline(
        y=avg_val,
        line_dash="dash",
        line_color=AVG_LINE_COLOUR,
        line_width=1.5,
    )
    # Label for the average line, anchored on the left
    fig.add_annotation(
        x=df["Period"].iloc[0],
        y=avg_val + 0.3,
        xanchor="left",
        showarrow=False,
        text=f"Average: {avg_val:.1f}%",
        font=dict(size=11, color=AVG_LINE_COLOUR),
    )

    # Layout
    fig.update_layout(
        title=dict(
            text=title,
            x=0,
            xanchor="left",
            yanchor="top",
            font=dict(size=18),
        ),
        margin=dict(l=60, r=30, t=40, b=60),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        xaxis=dict(
            title="Time period",
            tickangle=45,
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            title="Percent of working-age population",
            range=y_range,
            zeroline=False,
            showgrid=True,
            gridcolor="#E5E5E5",
        ),
    )

    return fig


# -------------------------------------------------------
# STREAMLIT LAYOUT
# -------------------------------------------------------
st.title("Employment, unemployment and economic inactivity over time")
st.subheader("Kirklees, age 16–64 – 12-month APS periods")

# Employment chart
fig_emp = create_indicator_figure(
    df,
    value_col="employment_rate",
    ci_col="employment_ci",
    title="Employment rate (16–64)",
    y_range=[60, 80],
)
st.plotly_chart(fig_emp, use_container_width=True)

# Unemployment chart
fig_unemp = create_indicator_figure(
    df,
    value_col="unemployment_rate",
    ci_col="unemployment_ci",
    title="Unemployment rate (16–64)",
    y_range=[0, 8],
)
st.plotly_chart(fig_unemp, use_container_width=True)

# Economic inactivity chart
fig_inact = create_indicator_figure(
    df,
    value_col="inactive_rate",
    ci_col="inactive_ci",
    title="Economic inactivity rate (16–64)",
    y_range=[18, 30],
)
st.plotly_chart(fig_inact, use_container_width=True)

# Simple source note
st.markdown(
    """
    **Source:** Annual Population Survey (APS), ONS via Nomis.  
    Notes: 12-month APS periods; 95% confidence intervals shown as shaded ranges.
    """,
)
