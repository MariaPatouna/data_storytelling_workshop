import io

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Kirklees labour-market context",
    layout="wide",
    page_icon="📈",
)

# -------------------------------------------------------------------
# BASIC STYLING (ONS-ish)
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
    * {
        font-family: "Arial", sans-serif;
    }
    /* tighten layout a bit */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ONS colour approximations
ONS_BLUE = "#12436D"   # employment
ONS_RED = "#D4351C"    # unemployment
ONS_GREY = "#6F777B"   # inactivity
ONS_LIGHT_GREY = "#E5E5E5"

# -------------------------------------------------------------------
# DATA: ANNUAL POPULATION SURVEY – KIRKLEES
# -------------------------------------------------------------------
APS_CSV = """Date,emp_num,emp_den,emp_pct,emp_conf,unemp_num,unemp_den,unemp_pct,unemp_conf,inact_num,inact_den,inact_pct,inact_conf
Jul 2015-Jun 2016,188600,269500,70.0,3.1,10200,198800,5.1,1.7,70700,269500,26.2,3.0
Jul 2016-Jun 2017,193000,272800,70.7,3.0,13200,206100,6.4,1.9,66700,272800,24.4,2.9
Jul 2017-Jun 2018,192900,273700,70.5,3.0,9000,202000,4.5,1.6,71800,273700,26.2,2.9
Jul 2018-Jun 2019,195000,271200,71.9,2.8,8400,203400,4.1,1.5,67800,271200,25.0,2.7
Jul 2019-Jun 2020,200000,271500,73.6,3.0,3600,203500,1.8,1.0,68000,271500,25.0,3.0
Jul 2020-Jun 2021,190400,272200,69.9,3.4,12000,202400,5.9,2.0,69800,272200,25.7,3.3
Jul 2021-Jun 2022,200800,272600,73.7,3.4,4700,205500,2.3,1.3,67100,272600,24.6,3.3
Jul 2022-Jun 2023,200200,275200,72.7,3.9,10200,210300,4.8,2.2,64800,275200,23.6,3.8
Jul 2023-Jun 2024,203500,274500,74.1,4.0,6900,210500,3.3,1.9,64000,274500,23.3,3.9
Jul 2024-Jun 2025,209400,273900,76.4,3.2,11200,220600,5.1,1.8,53300,273900,19.5,3.0
"""

df = pd.read_csv(io.StringIO(APS_CSV))

# Create a cleaner label for the x axis
df["Period"] = df["Date"]

# Confidence interval bounds
df["emp_low"] = df["emp_pct"] - df["emp_conf"]
df["emp_high"] = df["emp_pct"] + df["emp_conf"]
df["inact_low"] = df["inact_pct"] - df["inact_conf"]
df["inact_high"] = df["inact_pct"] + df["inact_conf"]

# Long format for multi-series chart
rates_long = df.melt(
    id_vars=["Period"],
    value_vars=["emp_pct", "unemp_pct", "inact_pct"],
    var_name="Indicator",
    value_name="Percent",
)

indicator_labels = {
    "emp_pct": "Employment rate (16–64)",
    "unemp_pct": "Unemployment rate (16–64)",
    "inact_pct": "Economic inactivity rate (16–64)",
}
rates_long["Indicator"] = rates_long["Indicator"].map(indicator_labels)

indicator_colors = {
    "Employment rate (16–64)": ONS_BLUE,
    "Unemployment rate (16–64)": ONS_RED,
    "Economic inactivity rate (16–64)": ONS_GREY,
}

# -------------------------------------------------------------------
# TITLE + NARRATIVE
# -------------------------------------------------------------------
st.title("Kirklees labour-market context – Annual Population Survey")

st.markdown(
    """
    This dashboard summarises **employment, unemployment and economic inactivity**  
    for people aged 16–64 in **Kirklees**, using the *Annual Population Survey (APS)*.

    The aim is explanatory: to show that **economic (in)activity has been broadly
    comparable over time**, with only gradual shifts rather than sharp breaks.
    """
)

st.markdown("---")

# -------------------------------------------------------------------
# HIGH-LEVEL CHART: THREE RATES OVER TIME
# -------------------------------------------------------------------
st.subheader("Employment, unemployment and economic inactivity over time")

fig_rates = px.line(
    rates_long,
    x="Period",
    y="Percent",
    color="Indicator",
    markers=True,
    color_discrete_map=indicator_colors,
)

fig_rates.update_layout(
    title="Kirklees, age 16–64 – APS 12-month periods",
    xaxis_title="12-month APS period",
    yaxis_title="Percent of working-age population",
    template="simple_white",
    font=dict(family="Arial", size=13),
    legend_title="Indicator",
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    margin=dict(l=60, r=20, t=80, b=90),
)

fig_rates.update_yaxes(
    range=[0, 80],
    ticks="outside",
    dtick=10,
    showgrid=True,
    gridcolor=ONS_LIGHT_GREY,
    zeroline=False,
)
fig_rates.update_xaxes(
    tickangle=-35,
    tickfont=dict(size=11),
    showgrid=False,
)

st.plotly_chart(fig_rates, use_container_width=True)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(
        """
        **Key points**

        - Employment has moved between **around 70% and mid-70s**.  
        - Unemployment remains **low in absolute terms**, mostly between **2–6%**.  
        - Economic inactivity sits in the **mid-20% range for most of the period**.
        """
    )
with col_b:
    st.markdown(
        """
        These patterns suggest **no dramatic break** in local labour-market conditions over  
        the last decade. Changes are **gradual and within a relatively narrow band**, which  
        is important context when interpreting outcomes for local programmes such as TLG.
        """
    )

st.markdown("---")

# -------------------------------------------------------------------
# FOCUSED CHART: ECONOMIC INACTIVITY WITH CONFIDENCE BANDS
# -------------------------------------------------------------------
st.subheader("Economic inactivity: stable within a band, with a recent fall")

fig_inact = go.Figure()

# Confidence band
fig_inact.add_trace(
    go.Scatter(
        x=pd.concat([df["Period"], df["Period"][::-1]]),
        y=pd.concat([df["inact_high"], df["inact_low"][::-1]]),
        fill="toself",
        fillcolor="rgba(111,119,123,0.2)",  # light grey band
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        showlegend=False,
    )
)

# Central line
fig_inact.add_trace(
    go.Scatter(
        x=df["Period"],
        y=df["inact_pct"],
        mode="lines+markers",
        name="Economic inactivity rate (16–64)",
        line=dict(color=ONS_GREY, width=3),
        marker=dict(size=7),
    )
)

fig_inact.update_layout(
    title="Economic inactivity rate with 95% confidence intervals – Kirklees, 16–64",
    xaxis_title="12-month APS period",
    yaxis_title="Percent of working-age population",
    template="simple_white",
    font=dict(family="Arial", size=13),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    margin=dict(l=60, r=20, t=80, b=90),
)

fig_inact.update_yaxes(
    range=[15, 30],
    ticks="outside",
    dtick=5,
    showgrid=True,
    gridcolor=ONS_LIGHT_GREY,
    zeroline=False,
)
fig_inact.update_xaxes(
    tickangle=-35,
    tickfont=dict(size=11),
    showgrid=False,
)

st.plotly_chart(fig_inact, use_container_width=True)

st.markdown(
    """
    The shaded band shows the **95% confidence interval** around the estimated inactivity rate.

    - For most of the period, inactivity sits between **about 24% and 26%**,  
      with overlapping confidence intervals from year to year.  
    - The most recent period shows a **modest fall towards roughly 20%**, but still  
      within a plausible range given sampling variation.

    Overall, the evidence points to **broadly comparable levels of economic inactivity over time**,  
    rather than a structural break coinciding with any single local intervention.
    """
)

st.markdown("---")

# -------------------------------------------------------------------
# FOOTNOTE / SOURCE
# -------------------------------------------------------------------
st.markdown(
    """
    <p style="font-size:12px; color:#6F777B;">
    Source: Annual Population Survey (APS), ONS – Crown Copyright Reserved.  
    Notes: APS estimates are weighted to 2018-based population projections.
    Rates are robust; levels and changes in levels should be interpreted with caution,
    particularly from 2019–20 onwards.
    </p>
    """,
    unsafe_allow_html=True,
)


