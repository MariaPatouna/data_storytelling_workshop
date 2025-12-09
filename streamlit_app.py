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

SURVEY_WAVES = ["Baseline", "Midline", "Endline"]

# Survey umbrella categories and modules
SURVEY_STRUCTURE = {
    "Organisational context": [
        "Mission orientation",
        "Organisational culture",
        "Psychological safety",
    ],
    "Capability": [
        "Evaluative capability",
        "Adaptive capability & responsiveness",
        "Decision-making capability",
        "Relational capability",
    ],
    "Capacity": [
        "Resource availability",
        "Resource efficiency",
        "Funding & financial investment",
        "Digital infrastructure",
        "Working in the open",
    ],
}

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

# ---- Survey data (dummy, 0–100) ----------------------------------
survey_rows = []
for acc in ACCELERATORS:
    base_level = np.random.uniform(45, 65)
    for umbrella, modules in SURVEY_STRUCTURE.items():
        for module in modules:
            drift = np.random.uniform(-3, 8)  # improvement over waves
            for i, wave in enumerate(SURVEY_WAVES):
                score = base_level + i * drift + np.random.normal(0, 3)
                survey_rows.append(
                    {
                        "Accelerator": acc,
                        "Wave": wave,
                        "Umbrella": umbrella,
                        "Module": module,
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
                "Effect_size": eff,  # absolute (e.g. 0.06 = +6 ppts)
                "CI_low": ci_low,
                "CI_high": ci_high,
                "p_value": p_val,
            }
        )
quant_df = pd.DataFrame(quant_rows)

# ---- Qualitative theme counts (dummy coded segments) ---------------
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
selected_accelerator = st.sidebar.selectbox("Select accelerator", ACCELERATORS)

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
    "Dummy dashboard illustrating how the TLG evaluation can be structured "
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

# Dummy survey metric
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

    # Aggregate to thematic group level
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
        - **Document groups** (e.g. interviews, weeknotes, observations) are treated as stable
          characteristics of the data and used here as filters rather than analytical codes.  
        - **Infrastructure codes** such as *phase* and *level of analysis* (programme, accelerator,
          central, local, delivery partners) structure where and when evidence arises.  
        - **Thematic groups** provide deductive scaffolding aligned with the TLG Theory of Change:
          TLG practices, enablers, barriers, mechanisms, outcomes, sustainability & scaling,
          governance & partnership, and contextual factors.  
        - Within each thematic group, inductive subcodes would capture specific routines, behaviours,
          constraints, and outcomes as they emerge from the material.
        """
    )

# ------------------------ SURVEY TAB -------------------------------
with tab_survey:
    st.subheader("Survey of ways of working")

    acc_survey = survey_df[survey_df["Accelerator"] == selected_accelerator].copy()
    if selected_waves:
        acc_survey = acc_survey[acc_survey["Wave"].isin(selected_waves)]

    # Aggregated view by umbrella category
    umbrella_summary = (
        acc_survey.groupby(["Umbrella", "Wave"], as_index=False)["Score"].mean()
    )

    st.markdown("**Average scores by umbrella category (Organisational context / Capability / Capacity)**")
    fig_umbrella = px.bar(
        umbrella_summary,
        x="Umbrella",
        y="Score",
        color="Wave",
        barmode="group",
        title="Average survey scores by umbrella category and wave (dummy)",
    )
    fig_umbrella.update_yaxes(range=[0, 100], title="Score (0–100)")
    st.plotly_chart(fig_umbrella, use_container_width=True)

    st.markdown("**Module-level view**")

    selected_umbrella = st.selectbox(
        "Focus on umbrella category",
        ["All"] + list(SURVEY_STRUCTURE.keys()),
    )

    module_df = acc_survey.copy()
    if selected_umbrella != "All":
        module_df = module_df[module_df["Umbrella"] == selected_umbrella]

    fig_modules = px.line(
        module_df,
        x="Wave",
        y="Score",
        color="Module",
        markers=True,
        title="Survey modules by wave (dummy)",
    )
    fig_modules.update_traces(line=dict(width=3))
    fig_modules.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_modules, use_container_width=True)

    st.markdown("#### Conceptual alignment")
    st.markdown(
        """
        - **Organisational context** modules proxy mission orientation, culture and trust,
          and psychological safety – the backdrop against which TLG practices land.  
        - **Capability** modules capture evaluative, adaptive, decision-making, and relational
          capabilities – the ability to generate, interpret and act on feedback.  
        - **Capacity** modules reflect resourcing, digital infrastructure, funding, and
          working-in-the-open – the Grow “foundations” that shape what is feasible.  
        - In the real survey, these modules would be operationalised with items drawn from
          established scales (e.g. Moynihan & Landuyt; Moynihan & Pandey; Edmondson; etc.).
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
          with monetised benefits (e.g., reduced demand, improved outcomes) to estimate VfI.
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
