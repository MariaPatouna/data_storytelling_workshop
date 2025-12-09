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
# CONSTANTS / DUMMY DATA DEFINITIONS
# -------------------------------------------------------------------
np.random.seed(42)

# Actual accelerators
ACCELERATORS = [
    "Best Start in Life (BSIL) x Northumberland",
    "Best Start in Life (BSIL) x Manchester",
    "Neighbourhood health x Plymouth",
    "Neighbourhood health x Liverpool",
    "Neighbourhood health x Essex",
    "Economic inactivity x Wakefield",
    "Violence Against Women and Girls (VAWG) x London",
    "SEND transitions x Sandwell",
    "SEND transition x Nottingham",
    "AI at the frontline x Barnsley",
]

SURVEY_WAVES = ["Wave 1", "Wave 2", "Wave 3"]

# Likert-style item battery
SURVEY_QUESTIONS = [
    "Developing ways to measure if project outcomes are being achieved",
    "Gathering and analysing data to measure if project outcomes are being achieved",
    "Assessing the quality of data used in measuring project outcomes",
    "Using data to determine if long-term strategic goals are being achieved",
]

LIKERT_OPTIONS = [
    "1 = To no extent",
    "2 = To a small extent",
    "3 = To a moderate extent",
    "4 = To a great extent",
    "5 = To a very great extent",
]

# ONS-style diverging Likert palette (approximate)
LIKERT_COLOURS = [
    "#CC1F24",  # strong negative
    "#F46A25",  # small extent
    "#D9D9D9",  # neutral
    "#2CA3A3",  # great extent
    "#005F83",  # very great extent
]

OUTCOMES = ["Outcome 1", "Outcome 2", "Outcome 3", "Outcome 4"]

QUAL_DOC_GROUPS = [
    "Interviews",
    "Weeknotes",
    "Meeting notes",
    "Observations",
    "Programme documents",
]

QUAL_PHASES = [
    "Set-up & inception",
    "Early delivery",
    "Mid-programme adaptation",
    "Late programme / scaling",
]

QUAL_LEVELS = [
    "Programme",
    "Accelerator",
    "Central government",
    "Local government",
    "Delivery partners",
]

QUAL_THEMATIC_GROUPS = [
    "TLG Practices",
    "Enablers",
    "Barriers",
    "Mechanisms of change",
    "Outcomes",
    "Sustainability & scaling",
    "Governance & partnership",
    "Contextual factors",
]

# -------------------------------------------------------------------
# DUMMY SURVEY DATA (LIKERT DISTRIBUTIONS)
# -------------------------------------------------------------------
likert_rows = []
for acc in ACCELERATORS:
    for wave in SURVEY_WAVES:
        for q in SURVEY_QUESTIONS:
            # Bias slightly towards "moderate" and "great extent"
            probs = np.random.dirichlet([1.0, 1.5, 2.5, 2.5, 1.5])
            n = 80  # pretend 80 respondents
            counts = np.random.multinomial(n, probs)

            for i, likert in enumerate(LIKERT_OPTIONS, start=1):
                count = counts[i - 1]
                percent = count / n * 100
                likert_rows.append(
                    {
                        "Accelerator": acc,
                        "Wave": wave,
                        "Question": q,
                        "Likert": likert,
                        "Score": i,       # 1–5
                        "Count": count,
                        "Percent": percent,
                    }
                )

survey_df = pd.DataFrame(likert_rows)
survey_df["Weighted"] = survey_df["Score"] * survey_df["Percent"]

# -------------------------------------------------------------------
# DUMMY QUANT DATA (DiD-STYLE EFFECTS)
# -------------------------------------------------------------------
quant_rows = []
for acc in ACCELERATORS:
    for outcome in OUTCOMES:
        eff = np.random.normal(0.05, 0.04)  # mean +5 ppts
        se = np.random.uniform(0.01, 0.03)
        ci_low = eff - 1.96 * se
        ci_high = eff + 1.96 * se
        p_val = np.random.uniform(0.01, 0.25)
        quant_rows.append(
            {
                "Accelerator": acc,
                "Outcome": outcome,
                "Effect_size": eff,
                "CI_low": ci_low,
                "CI_high": ci_high,
                "p_value": p_val,
            }
        )
quant_df = pd.DataFrame(quant_rows)

# -------------------------------------------------------------------
# DUMMY QUAL DATA (CODED SEGMENTS BY GROUP)
# -------------------------------------------------------------------
qual_rows = []
for acc in ACCELERATORS:
    for doc in QUAL_DOC_GROUPS:
        for phase in QUAL_PHASES:
            for level in QUAL_LEVELS:
                base = np.random.randint(5, 20)
                for theme in QUAL_THEMATIC_GROUPS:
                    mentions = base + np.random.randint(-5, 10)
                    qual_rows.append(
                        {
                            "Accelerator": acc,
                            "Document_group": doc,
                            "Phase": phase,
                            "Level": level,
                            "Thematic_group": theme,
                            "Mentions": max(0, mentions),
                        }
                    )
qual_df = pd.DataFrame(qual_rows)

# -------------------------------------------------------------------
# DUMMY VfI DATA
# -------------------------------------------------------------------
vfi_rows = []
for acc in ACCELERATORS:
    cost = np.random.uniform(800, 1800)  # cost per participant
    benefit = cost * np.random.uniform(0.8, 2.0)
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
selected_accelerator = st.sidebar.selectbox("Select accelerator", ACCELERATORS)

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
    "Dummy dashboard illustrating how the TLG evaluation can be structured "
    "across qualitative, survey (Likert), quantitative, and value-for-investment strands."
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

# Survey metric: average Likert score (1–5) across questions & waves
acc_survey = survey_df[survey_df["Accelerator"] == selected_accelerator]
mean_score = acc_survey["Weighted"].sum() / acc_survey["Percent"].sum()

# Quant metric: share of outcomes with p < 0.05
acc_quant = quant_df[quant_df["Accelerator"] == selected_accelerator]
sig_share = (acc_quant["p_value"] < 0.05).mean() * 100

# VfI metric
acc_vfi = vfi_df[vfi_df["Accelerator"] == selected_accelerator].iloc[0]

with col1:
    st.metric("Mean survey score (1–5)", f"{mean_score:,.2f}")
with col2:
    st.metric("% outcomes with p < 0.05", f"{sig_share:,.0f}%")
with col3:
    st.metric("Benefit–cost ratio", f"{acc_vfi['Benefit_cost_ratio']:,.2f}x")

# -------------------------------------------------------------------
# TABS FOR STRANDS
# -------------------------------------------------------------------
tab_qual, tab_survey, tab_quant, tab_vfi = st.tabs(
    ["📋 Qualitative evaluation", "📊 Survey (Likert)", "📈 Quantitative impact", "💷 Value for Investment"]
)

# ------------------------ QUALITATIVE TAB ---------------------------
with tab_qual:
    st.subheader("Qualitative evaluation – codebook view")

    acc_qual = qual_df[qual_df["Accelerator"] == selected_accelerator].copy()

    # Filters mimicking infrastructure codes
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        selected_doc = st.selectbox(
            "Document group",
            ["All"] + QUAL_DOC_GROUPS,
        )
    with col_q2:
        selected_phase = st.selectbox(
            "Programme / accelerator phase",
            ["All"] + QUAL_PHASES,
        )

    if selected_doc != "All":
        acc_qual = acc_qual[acc_qual["Document_group"] == selected_doc]
    if selected_phase != "All":
        acc_qual = acc_qual[acc_qual["Phase"] == selected_phase]

    thematic_summary = (
        acc_qual.groupby("Thematic_group", as_index=False)["Mentions"]
        .sum()
        .sort_values("Mentions", ascending=False)
    )

    fig_qual = px.bar(
        thematic_summary,
        x="Thematic_group",
        y="Mentions",
        title="Coded segments by thematic group (dummy)",
        text_auto=True,
        color="Thematic_group",
        color_discrete_sequence=[chart_color],
    )
    fig_qual.update_layout(
        xaxis_title="Thematic group",
        yaxis_title="Number of coded segments",
    )
    st.plotly_chart(fig_qual, use_container_width=True)

    st.markdown("#### How this reflects the qualitative approach")
    st.markdown(
        """
        - **Document groups** (interviews, weeknotes, observations, programme documents) are
          treated as stable document attributes and used here as filters.  
        - **Infrastructure codes** (phase, level of analysis) structure where and when evidence arises.  
        - **Thematic groups** mirror the deductive scaffolding: TLG practices, enablers, barriers,
          mechanisms of change, outcomes, sustainability & scaling, governance & partnership, and context.  
        - Within each thematic group, inductive subcodes would capture specific routines, behaviours,
          constraints and outcomes as they emerge from the material.
        """
    )

# ------------------------ SURVEY TAB (LIKERT) -----------------------
with tab_survey:
    st.subheader("Survey of ways of working – Likert distribution")

    # Wave selector INSIDE the tab (not in sidebar)
    selected_wave = st.radio(
        "Select survey wave",
        SURVEY_WAVES,
        horizontal=True,
    )

    wave_df = survey_df[
        (survey_df["Accelerator"] == selected_accelerator)
        & (survey_df["Wave"] == selected_wave)
    ].copy()

    # Ensure Likert categories plotted in the right order
    wave_df["Likert"] = pd.Categorical(
        wave_df["Likert"],
        categories=LIKERT_OPTIONS,
        ordered=True,
    )

    st.markdown(
        """
        **Question battery**

        *Thinking about your most recent project, to what extent, if at all, were you involved in the following activities?*  
        Response scale (1–5):

        1 = To no extent  
        2 = To a small extent  
        3 = To a moderate extent  
        4 = To a great extent  
        5 = To a very great extent  
        """
    )

    fig_likert = px.bar(
        wave_df,
        x="Question",
        y="Percent",
        color="Likert",
        barmode="stack",
        title=f"Distribution of responses by question – {selected_wave} (dummy)",
        color_discrete_sequence=LIKERT_COLOURS,
        category_orders={"Likert": LIKERT_OPTIONS},
    )
    fig_likert.update_layout(
        yaxis_title="Percent of respondents",
        xaxis_title="Question",
        legend_title="Response",
    )
    st.plotly_chart(fig_likert, use_container_width=True)

    st.markdown(
        """
        This stacked Likert chart mirrors the intended reporting structure:  
        - A common **question stem** with several activities in a grid.  
        - A 5-point **extent** scale using a diverging palette from “to no extent” to “to a very great extent”.  
        - Wave selection handled within the tab rather than in the global filters.
        """
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
        - In the real evaluation, this strand would combine incremental costs from MI/admin data
          with monetised benefits (for example reduced demand, improved outcomes) to estimate VfI.
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
