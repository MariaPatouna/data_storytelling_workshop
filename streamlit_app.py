import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(
    page_title="TLG Evaluation Dashboard",
    layout="wide",
    page_icon="📊",
)

# -------------------------------------------------------------------
# BASIC STYLING
# -------------------------------------------------------------------

# Global font
st.markdown(
    """
    <style>
    * {
        font-family: 'Verdana', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar width
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            min-width: 220px;
            max-width: 320px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# DUMMY DATA GENERATION FOR TLG
# -------------------------------------------------------------------
np.random.seed(42)

ACCELERATORS = [
    "Barnsley – AI & Children’s Services",
    "Northumberland – Best Start in Life",
    "Kirklees – Housing & Complex Needs",
    "Pioneer X – Community Health",
]

SURVEY_DIMENSIONS = ["Learning routines", "User-centred design", "Collaboration", "Use of data"]
SURVEY_WAVES = ["Baseline", "Midline", "Endline"]

OUTCOMES = ["Engagement", "Service take-up", "Sustained participation", "Wellbeing index"]

QUAL_THEMES = [
    "Joined-up working",
    "Trust with partners",
    "Staff capability",
    "Data use in practice",
    "Barriers & constraints",
]

# ---- Survey data (dummy, 0–100) ----------------------------------
survey_rows = []
for acc in ACCELERATORS:
    base = np.random.uniform(45, 65)
    for dim in SURVEY_DIMENSIONS:
        drift = np.random.uniform(-3, 8)  # some improve more than others
        for i, wave in enumerate(SURVEY_WAVES):
            score = base + i * drift + np.random.normal(0, 3)
            survey_rows.append(
                {
                    "Accelerator": acc,
                    "Wave": wave,
                    "Dimension": dim,
                    "Score": np.clip(score, 0, 100),
                }
            )
survey_df = pd.DataFrame(survey_rows)

# ---- Quantitative impact data (dummy DiD-style effect sizes) ------
quant_rows = []
for acc in ACCELERATORS:
    for outcome in OUTCOMES:
        eff = np.random.normal(0.05, 0.04)  # mean 5 percentage points
        se = np.random.uniform(0.01, 0.03)
        ci_low = eff - 1.96 * se
        ci_high = eff + 1.96 * se
        p_val = np.random.uniform(0.01, 0.25)
        quant_rows.append(
            {
                "Accelerator": acc,
                "Outcome": outcome,
                "Effect_size": eff,  # in absolute terms (e.g., +0.06 = +6 ppts)
                "CI_low": ci_low,
                "CI_high": ci_high,
                "p_value": p_val,
            }
        )
quant_df = pd.DataFrame(quant_rows)

# ---- Qualitative theme counts (dummy “coded segments” per theme) ---
qual_rows = []
for acc in ACCELERATORS:
    base = np.random.randint(15, 40)
    for theme in QUAL_THEMES:
        # add variation by theme
        mentions = base + np.random.randint(-10, 10)
        qual_rows.append(
            {
                "Accelerator": acc,
                "Theme": theme,
                "Mentions": max(0, mentions),
            }
        )
qual_df = pd.DataFrame(qual_rows)

# ---- VfI / cost-effectiveness style dummy data ---------------------
vfi_rows = []
for acc in ACCELERATORS:
    cost = np.random.uniform(800, 1800)  # cost per participant
    benefit = cost * np.random.uniform(0.8, 2.0)  # monetised benefit
    bcr = benefit / cost
    vfi_rows.append(
        {
            "Accelerator": acc,
            "Cost_per_participant": cost,
            "Benefit_per_participant": benefit,
            "Benefit_cost_ratio": bcr,
        }
    )
vfi_df = pd.DataFrame(vfi_rows)

# -------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------

# Logo (optional)
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "logo.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, caption="Test, Learn & Grow", use_container_width=True)

st.sidebar.markdown("<h3 style='color:#4B0082;'>Filters</h3>", unsafe_allow_html=True)

# Accelerator selector
selected_accelerator = st.sidebar.selectbox("Select Accelerator", ACCELERATORS)

# Wave filter (for survey plots)
selected_waves = st.sidebar.multiselect(
    "Survey waves",
    SURVEY_WAVES,
    default=SURVEY_WAVES,
)

# Theme / colour options
chart_color = st.sidebar.color_picker("Pick accent colour", "#2E86C1")

# Theme toggle
theme = st.sidebar.radio("Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #111111;
                color: #F5F5F5;
            }
            [data-testid="stSidebar"] {
                background-color: #222222;
            }
            h1, h2, h3, h4, h5, h6, p, label {
                color: #F5F5F5;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Sidebar info
st.sidebar.info(
    "This dummy dashboard illustrates how the TLG evaluation can be structured "
    "across qualitative, survey, quantitative, and value-for-investment strands."
)

# -------------------------------------------------------------------
# HEADER
# -------------------------------------------------------------------
st.markdown(
    "<h1 style='text-align:center; color:#1B4F72;'>Evaluation of Test, Learn & Grow</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<h3 style='text-align:center;'>Accelerator: <em>{selected_accelerator}</em></h3>",
    unsafe_allow_html=True,
)

st.markdown("---")

# -------------------------------------------------------------------
# TOP SUMMARY METRICS (DUMMY)
# -------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

# Dummy survey engagement metric
acc_survey = survey_df[survey_df["Accelerator"] == selected_accelerator]
avg_score = acc_survey["Score"].mean()

# Dummy quant “share of outcomes significantly > 0”
acc_quant = quant_df[quant_df["Accelerator"] == selected_accelerator]
sig_share = (acc_quant["p_value"] < 0.05).mean() * 100

# Dummy VfI BCR
acc_vfi = vfi_df[vfi_df["Accelerator"] == selected_accelerator].iloc[0]

with col1:
    st.metric(
        "Avg survey score (0–100)",
        f"{avg_score:,.1f}",
    )
with col2:
    st.metric(
        "% outcomes with p < 0.05",
        f"{sig_share:,.0f}%",
    )
with col3:
    st.metric(
        "Benefit–cost ratio",
        f"{acc_vfi['Benefit_cost_ratio']:,.2f}x",
    )

# -------------------------------------------------------------------
# TABS FOR STRANDS
# -------------------------------------------------------------------
tab_qual, tab_survey, tab_quant, tab_vfi = st.tabs(
    ["📋 Qualitative evaluation", "📊 Survey", "📈 Quantitative impact", "💷 Value for Investment"]
)

# ------------------------ QUALITATIVE TAB ---------------------------
with tab_qual:
    st.subheader("Emergent themes from qualitative work")

    acc_qual = qual_df[qual_df["Accelerator"] == selected_accelerator]

    fig_qual = px.bar(
        acc_qual,
        x="Theme",
        y="Mentions",
        title="Number of coded segments per theme (dummy)",
        color="Theme",
        text_auto=True,
        color_discrete_sequence=[chart_color],
    )
    fig_qual.update_layout(xaxis_title="", yaxis_title="Coded segments")
    st.plotly_chart(fig_qual, use_container_width=True)

    st.markdown("#### Illustrative qualitative insights (dummy text)")
    st.markdown(
        """
        - Frontline teams report **greater clarity of roles** and stronger relationships with central teams.  
        - Data use is still described as **fragmented**, with several accelerators relying on legacy systems.  
        - Participants highlight **trusting relationships** with practitioners as a key driver of engagement.
        """
    )

# ------------------------ SURVEY TAB -------------------------------
with tab_survey:
    st.subheader("Survey of ways of working")

    acc_survey = survey_df[survey_df["Accelerator"] == selected_accelerator]
    if selected_waves:
        acc_survey = acc_survey[acc_survey["Wave"].isin(selected_waves)]

    # Line chart: scores over waves by dimension
    fig_survey = px.line(
        acc_survey,
        x="Wave",
        y="Score",
        color="Dimension",
        markers=True,
        title="Survey scores by dimension and wave (dummy)",
    )
    fig_survey.update_traces(line=dict(width=3))
    fig_survey.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_survey, use_container_width=True)

    # Optional: table
    st.markdown("#### Underlying survey data (dummy)")
    st.dataframe(
        acc_survey.pivot_table(
            index="Dimension",
            columns="Wave",
            values="Score",
        ).round(1)
    )

# ------------------------ QUANT TAB -------------------------------
with tab_quant:
    st.subheader("Quantitative impact (dummy DiD-style estimates)")

    acc_quant = quant_df[quant_df["Accelerator"] == selected_accelerator].copy()
    acc_quant["Effect (ppts)"] = acc_quant["Effect_size"] * 100

    fig_quant = px.bar(
        acc_quant,
        x="Outcome",
        y="Effect (ppts)",
        title="Estimated impact by outcome (dummy)",
        text="Effect (ppts)",
        color="Outcome",
        color_discrete_sequence=[chart_color],
    )
    fig_quant.update_layout(yaxis_title="Effect size (percentage points)")
    st.plotly_chart(fig_quant, use_container_width=True)

    st.markdown("#### Effect estimates with confidence intervals (dummy)")
    st.dataframe(
        acc_quant[["Outcome", "Effect_size", "CI_low", "CI_high", "p_value"]].assign(
            Effect_size=lambda d: (d["Effect_size"] * 100).round(2),
            CI_low=lambda d: (d["CI_low"] * 100).round(2),
            CI_high=lambda d: (d["CI_high"] * 100).round(2),
            p_value=lambda d: d["p_value"].round(3),
        ).rename(
            columns={
                "Effect_size": "Effect (ppts)",
                "CI_low": "CI low (ppts)",
                "CI_high": "CI high (ppts)",
            }
        )
    )

# ------------------------ VFI TAB -------------------------------
with tab_vfi:
    st.subheader("Value for Investment (dummy)")

    cost = acc_vfi["Cost_per_participant"]
    benefit = acc_vfi["Benefit_per_participant"]
    bcr = acc_vfi["Benefit_cost_ratio"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Cost per participant", f"£{cost:,.0f}")
    with c2:
        st.metric("Benefit per participant", f"£{benefit:,.0f}")
    with c3:
        st.metric("Benefit–cost ratio", f"{bcr:,.2f}x")

    vfi_plot_df = pd.DataFrame(
        {
            "Type": ["Cost per participant", "Benefit per participant"],
            "Amount": [cost, benefit],
        }
    )
    fig_vfi = px.bar(
        vfi_plot_df,
        x="Type",
        y="Amount",
        text_auto=True,
        title="Cost vs benefit per participant (dummy)",
        color="Type",
        color_discrete_sequence=[chart_color],
    )
    fig_vfi.update_yaxes(title="£ per participant")
    st.plotly_chart(fig_vfi, use_container_width=True)

    st.markdown(
        """
        **Interpretation (dummy narrative):**  
        - Values shown here are *illustrative only*.  
        - In the real evaluation, this strand would combine incremental costs from MI/admin data with monetised benefits (e.g., reduced demand, improved outcomes) to estimate VfI.
        """
    )

# -------------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 13px;
            color: #CCCCCC;
            background-color: #0B1F33;
            padding: 6px 0;
            z-index: 9999;
        }
        .stApp {
            padding-bottom: 40px;
        }
    </style>
    <div class="footer">© 2025 Test, Learn & Grow – Evaluation dashboard (dummy data)</div>
    """,
    unsafe_allow_html=True,
)
