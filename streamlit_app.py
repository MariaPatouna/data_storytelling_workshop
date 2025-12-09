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

# Approximate coordinates for each accelerator place
ACCELERATOR_GEO = {
    "Best Start in Life (BSIL) x Northumberland": {
        "Place": "Northumberland",
        "lat": 55.1667,
        "lon": -2.0000,
    },
    "Best Start in Life (BSIL) x Manchester": {
        "Place": "Manchester",
        "lat": 53.4808,
        "lon": -2.2426,
    },
    "Neighbourhood health x Plymouth": {
        "Place": "Plymouth",
        "lat": 50.3755,
        "lon": -4.1427,
    },
    "Neighbourhood health x Liverpool": {
        "Place": "Liverpool",
        "lat": 53.4084,
        "lon": -2.9916,
    },
    "Neighbourhood health x Essex": {
        "Place": "Essex (Chelmsford)",
        "lat": 51.7360,
        "lon": 0.4790,
    },
    "Economic inactivity x Wakefield": {
        "Place": "Wakefield",
        "lat": 53.6829,
        "lon": -1.4969,
    },
    "Violence Against Women and Girls (VAWG) x London": {
        "Place": "London",
        "lat": 51.5074,
        "lon": -0.1278,
    },
    "SEND transitions x Sandwell": {
        "Place": "Sandwell",
        "lat": 52.5050,
        "lon": -2.0110,
    },
    "SEND transition x Nottingham": {
        "Place": "Nottingham",
        "lat": 52.9548,
        "lon": -1.1581,
    },
    "AI at the frontline x Barnsley": {
        "Place": "Barnsley",
        "lat": 53.5526,
        "lon": -1.4797,
    },
}

# Build a small DF for the map
geo_rows = []
for acc, info in ACCELERATOR_GEO.items():
    geo_rows.append(
        {
            "Accelerator": acc,
            "Place": info["Place"],
            "lat": info["lat"],
            "lon": info["lon"],
        }
    )
geo_df = pd.DataFrame(geo_rows)

SURVEY_WAVES = ["Wave 1", "Wave 2", "Wave 3"]

# ONS-style diverging Likert palette (approximate)
ONS_5 = [
    "#CC1F24",  # strong negative
    "#F46A25",  # small extent / disagree
    "#D9D9D9",  # neutral
    "#2CA3A3",  # great extent / agree
    "#005F83",  # very great extent / strongly agree
]
ONS_DK = "#B3B3B3"  # Don't know / NA

# Two batteries: metadata, questions, scales, colours
BATTERIES = {
    "Involvement in measuring outcomes": {
        "stem": (
            "Thinking about your **most recent project**, to what extent, if at all, "
            "were you involved in the following activities?"
        ),
        "questions": [
            "Developing ways to measure\nif project outcomes are being achieved",
            "Gathering and analysing data\nto measure if project outcomes\nare being achieved",
            "Assessing the quality of data\nused in measuring project outcomes",
            "Using data to determine if\nlong-term strategic goals\nare being achieved",
        ],
        "likert_options": [
            "1 = To no extent",
            "2 = To a small extent",
            "3 = To a moderate extent",
            "4 = To a great extent",
            "5 = To a very great extent",
        ],
        "scale_text": [
            "1 = To no extent",
            "2 = To a small extent",
            "3 = To a moderate extent",
            "4 = To a great extent",
            "5 = To a very great extent",
        ],
        "palette": ONS_5,
        "has_dk": False,
    },
    "Team learning and feedback culture": {
        "stem": (
            "Thinking about **your team**, to what extent do you agree or disagree "
            "with the following statements?"
        ),
        "questions": [
            "We are encouraged\nto learn from our mistakes.",
            "We use feedback from those we serve\nto improve performance.",
            "We integrate information\nand act intelligently on that information.",
            "I believe we will use the insights\nfrom this survey to improve our work.",
        ],
        "likert_options": [
            "1 = Strongly disagree",
            "2 = Disagree",
            "3 = Feel neutral",
            "4 = Agree",
            "5 = Strongly agree",
            "6 = Don’t know / not applicable",
        ],
        "scale_text": [
            "1 = Strongly disagree",
            "2 = Disagree",
            "3 = Feel neutral",
            "4 = Agree",
            "5 = Strongly agree",
            "6 = Don’t know / not applicable",
        ],
        "palette": ONS_5 + [ONS_DK],
        "has_dk": True,
    },
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

# -------------------------------------------------------------------
# DUMMY SURVEY DATA (LIKERT DISTRIBUTIONS FOR BOTH BATTERIES)
# -------------------------------------------------------------------
likert_rows = []
for acc in ACCELERATORS:
    for wave in SURVEY_WAVES:
        for battery_name, meta in BATTERIES.items():
            questions = meta["questions"]
            likert_opts = meta["likert_options"]
            has_dk = meta["has_dk"]

            for q in questions:
                # Bias slightly towards middle / positive categories
                probs = np.random.dirichlet([1.0] * len(likert_opts))
                n = 80
                counts = np.random.multinomial(n, probs)

                for i, likert in enumerate(likert_opts, start=1):
                    count = counts[i - 1]
                    percent = count / n * 100

                    # Don't-know category gets no score
                    if has_dk and "Don’t know" in likert:
                        score = np.nan
                    else:
                        score = i

                    likert_rows.append(
                        {
                            "Accelerator": acc,
                            "Wave": wave,
                            "Battery": battery_name,
                            "Question": q,
                            "Likert": likert,
                            "Score": score,  # may be NaN for DK
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
# MAP OF ENGLAND – TLG SITES
# -------------------------------------------------------------------
st.markdown("### Where is this accelerator located?")

map_df = geo_df.copy()
map_df["Selected"] = map_df["Accelerator"] == selected_accelerator
map_df["Marker_size"] = map_df["Selected"].map({True: 18, False: 10})

fig_map = px.scatter_mapbox(
    map_df,
    lat="lat",
    lon="lon",
    hover_name="Place",
    hover_data={"Accelerator": True, "Selected": False, "lat": False, "lon": False},
    color="Selected",
    size="Marker_size",
    size_max=20,
    zoom=5,
    center={"lat": 53.5, "lon": -2.0},
    mapbox_style="open-street-map",
    color_discrete_map={
        True: "#005F83",   # highlighted site
        False: "#7FB3D5",  # other TLG sites
    },
)

fig_map.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    height=400,
    legend_title="Selected accelerator",
)

st.plotly_chart(fig_map, use_container_width=True)

# -------------------------------------------------------------------
# TOP SUMMARY METRICS (DUMMY)
# -------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

# Survey metric: average Likert score (1–5) across batteries, questions & waves (excluding DK)
acc_survey = survey_df[survey_df["Accelerator"] == selected_accelerator]
mask = acc_survey["Score"].notna()
mean_score = acc_survey.loc[mask, "Weighted"].sum() / acc_survey.loc[mask, "Percent"].sum()

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

    # Wave selector INSIDE the tab
    selected_wave = st.radio(
        "Select survey wave",
        SURVEY_WAVES,
        horizontal=True,
    )

    # Battery selector (the two question sets)
    selected_battery = st.selectbox(
        "Select question set",
        list(BATTERIES.keys()),
    )
    meta = BATTERIES[selected_battery]
    questions = meta["questions"]
    likert_opts = meta["likert_options"]
    palette = meta["palette"]

    wave_df = survey_df[
        (survey_df["Accelerator"] == selected_accelerator)
        & (survey_df["Wave"] == selected_wave)
        & (survey_df["Battery"] == selected_battery)
    ].copy()

    # Ordering for axes
    wave_df["Likert"] = pd.Categorical(
        wave_df["Likert"],
        categories=likert_opts,
        ordered=True,
    )
    wave_df["Question"] = pd.Categorical(
        wave_df["Question"],
        categories=questions,
        ordered=True,
    )

    # Question stem + scale text
    st.markdown(f"**Question stem**  \n{meta['stem']}")
    st.markdown("**Response scale**")
    for line in meta["scale_text"]:
        st.markdown(f"- {line}")

    # Horizontal stacked bar chart, ONS-style
    fig_likert = px.bar(
        wave_df,
        x="Percent",
        y="Question",
        color="Likert",
        orientation="h",
        barmode="stack",
        title=f"Distribution of responses by question – {selected_battery}, {selected_wave} (dummy)",
        color_discrete_sequence=palette,
        category_orders={
            "Likert": likert_opts,
            "Question": list(reversed(questions)),
        },
    )

    fig_likert.update_layout(
        xaxis_title="Percent of respondents",
        yaxis_title="",
        xaxis=dict(
            range=[0, 100],
            ticks="outside",
            tick0=0,
            dtick=20,
            showgrid=True,
            gridcolor="#E5E5E5",
            zeroline=False,
        ),
        yaxis=dict(showgrid=False),
        legend_title="Response",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        bargap=0.25,
        margin=dict(l=260, r=40, t=80, b=60),
    )

    # Data labels inside bars
    fig_likert.update_traces(
        texttemplate="%{x:.0f}%",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#FFFFFF", size=11),
        hovertemplate="<b>%{y}</b><br>%{legendgroup}<br>%{x:.1f}%<extra></extra>",
    )

    st.plotly_chart(fig_likert, use_container_width=True)

    st.markdown(
        """
        This layout mirrors the ONS horizontal bar style:

        - One stacked bar per activity/statement, labelled on the left with manual line breaks.  
        - Diverging **ONS palette** from negative to positive responses, with a separate neutral/DK tone where applicable.  
        - 0–100% scale with light gridlines to support quick comparison across items and waves.
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
