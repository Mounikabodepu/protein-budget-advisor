
import streamlit as st
from datetime import date

from common import require_login, load_today, save_today

st.set_page_config(
    page_title="Daily Summary | Protein & Balance",
    page_icon="🥗",
    layout="wide"
)

require_login()

# ---------- Warm cream & orange theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

.stApp {
    background: #FBF5EC;
    color: #3D3027;
}
header[data-testid="stHeader"] {
    background: rgba(251,245,236,0.95);
}
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}
h1, h2, h3, p, label, .stMarkdown {
    color: #3D3027;
    font-family: 'DM Sans', sans-serif;
}
h1, h2 {
    font-family: 'Playfair Display', serif;
}
.hero {
    background:
      linear-gradient(90deg, rgba(48,34,24,0.88), rgba(48,34,24,0.32)),
      url("https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1600&q=85");
    background-size: cover;
    background-position: center;
    border-radius: 24px;
    padding: 38px 36px;
    min-height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin-bottom: 22px;
    box-shadow: 0 12px 32px rgba(91,59,35,0.12);
}
.hero .eyebrow {
    color: #FFD1A6;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 10px;
}
.hero h1 {
    color: #FFFFFF !important;
    font-size: 38px;
    line-height: 1.15;
    margin: 0 0 10px 0;
}
.hero p {
    color: #FFF6EC !important;
    font-size: 15px;
    margin: 0;
    max-width: 560px;
    line-height: 1.7;
}
.section-title {
    font-family: 'Playfair Display', serif;
    color: #3D3027;
    font-size: 25px;
    font-weight: 700;
    margin: 18px 0 4px 0;
}
.section-subtitle {
    color: #8B7665;
    font-size: 14px;
    margin-bottom: 14px;
}
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #F0E1D1;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 5px 18px rgba(91,59,35,0.05);
}
div[data-testid="stMetricLabel"] {
    color: #806C5B !important;
    font-size: 13px;
}
div[data-testid="stMetricValue"] {
    color: #C9672B !important;
    font-weight: 700;
}
div[data-testid="stMetricDelta"] {
    color: #6E8461 !important;
}
div[data-testid="stProgress"] > div {
    background: #F0E1D1;
    border-radius: 20px;
}
div[data-testid="stProgress"] div[role="progressbar"] {
    background: #E58B45;
    border-radius: 20px;
}
div[data-testid="stNumberInput"] input {
    background: #FFFFFF;
    color: #3D3027;
    border: 1px solid #E9D6C3;
    border-radius: 10px;
}
div[data-testid="stNumberInput"] label {
    color: #594638 !important;
}
.stButton > button[kind="primary"],
.stButton > button {
    background: #D97736;
    color: #FFFFFF;
    border: 1px solid #D97736;
    border-radius: 12px;
    min-height: 44px;
    font-weight: 700;
}
.stButton > button:hover {
    background: #B95F27;
    border-color: #B95F27;
    color: #FFFFFF;
}
div[data-testid="stAlert"] {
    border-radius: 14px;
}
div[data-testid="stExpander"] {
    background: #FFFDF9;
    border: 1px solid #F0E1D1;
    border-radius: 14px;
}
hr {
    border-color: #EBDCCB;
}
@media (max-width: 700px) {
    .hero { padding: 26px 22px; min-height: 190px; }
    .hero h1 { font-size: 29px; }
}
</style>
""", unsafe_allow_html=True)

# ---------- Load today's data ----------
today = date.today()
saved = load_today() or {}

protein_target = st.session_state.get(
    "protein_target", saved.get("protein_target", 120)
)
protein_consumed = st.session_state.get(
    "protein_consumed", saved.get("protein_consumed", 0)
)
calories_consumed = st.session_state.get(
    "calories_consumed", saved.get("calories_consumed", 0)
)
calorie_target = st.session_state.get(
    "calorie_target", saved.get("calorie_target", 2000)
)
calories_burnt = st.session_state.get(
    "calories_burnt", saved.get("calories_burnt", 0)
)
steps_done = st.session_state.get(
    "steps_done", saved.get("steps_done", 0)
)
step_goal = st.session_state.get(
    "step_goal", saved.get("step_goal", 10000)
)

# ---------- Hero banner ----------
st.markdown(f"""
<div class="hero">
    <div class="eyebrow">PROTEIN &amp; BALANCE · DAILY CHECK-IN</div>
    <h1>Your day, in balance.</h1>
    <p>A little progress every day adds up.
       Review your nutrition, celebrate your wins, and plan your next step.</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    f"<div style='color:#8B7665;font-size:14px;margin-bottom:8px;'>"
    f"<b style='color:#594638'>{today.strftime('%A, %d %B %Y')}</b>"
    f" &nbsp;·&nbsp; Today's wellness overview</div>",
    unsafe_allow_html=True
)

# ---------- Editable daily values ----------
with st.expander("✏️ Review or edit today's numbers", expanded=False):
    st.caption(
        "Update these values if the other tracker pages have not supplied them yet."
    )

    left, right = st.columns(2)

    with left:
        calories_consumed = st.number_input(
            "Calories consumed (kcal)",
            min_value=0,
            value=max(0, int(calories_consumed or 0)),
            step=50,
            key="summary_calories_input"
        )
        protein_consumed = st.number_input(
            "Protein consumed (g)",
            min_value=0.0,
            value=max(0.0, float(protein_consumed or 0)),
            step=5.0,
            key="summary_protein_input"
        )
        calorie_target = st.number_input(
            "Daily calorie target (kcal)",
            min_value=0,
            value=max(0, int(calorie_target or 2000)),
            step=50,
            key="summary_calorie_target_input"
        )

    with right:
        protein_target = st.number_input(
            "Daily protein target (g)",
            min_value=0.0,
            value=max(0.0, float(protein_target or 120)),
            step=5.0,
            key="summary_protein_target_input"
        )
        steps_done = st.number_input(
            "Steps completed",
            min_value=0,
            value=max(0, int(steps_done or 0)),
            step=500,
            key="summary_steps_input"
        )
        step_goal = st.number_input(
            "Daily step goal",
            min_value=0,
            value=max(0, int(step_goal or 10000)),
            step=500,
            key="summary_step_goal_input"
        )

    calories_burnt = st.number_input(
        "Calories burnt from activity (kcal)",
        min_value=0.0,
        value=max(0.0, float(calories_burnt or 0)),
        step=10.0,
        key="summary_burnt_input"
    )

# ---------- Dashboard metrics ----------
st.markdown(
    '<div class="section-title">Your daily snapshot</div>'
    '<div class="section-subtitle">The numbers behind today\'s progress</div>',
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)
c1.metric(
    "🔥 Calories consumed",
    f"{calories_consumed:,.0f} kcal",
    f"Target: {calorie_target:,.0f}"
)
c2.metric(
    "🥗 Protein",
    f"{protein_consumed:,.1f} g",
    f"Target: {protein_target:,.1f} g"
)
c3.metric(
    "👟 Steps",
    f"{steps_done:,.0f}",
    f"Goal: {step_goal:,.0f}"
)

# ---------- Progress bars ----------
st.markdown(
    '<div class="section-title">How far have you come?</div>',
    unsafe_allow_html=True
)

p1, p2 = st.columns(2)

with p1:
    calorie_progress = (
        min(calories_consumed / calorie_target, 1.0)
        if calorie_target > 0 else 0
    )
    st.markdown("**Calorie target**")
    st.progress(calorie_progress)
    st.caption(
        f"{calorie_progress * 100:.0f}% of target · "
        f"{max(0, calorie_target - calories_consumed):,.0f} kcal remaining"
    )

with p2:
    protein_progress = (
        min(protein_consumed / protein_target, 1.0)
        if protein_target > 0 else 0
    )
    st.markdown("**Protein target**")
    st.progress(protein_progress)
    st.caption(
        f"{protein_progress * 100:.0f}% of target · "
        f"{max(0, protein_target - protein_consumed):,.1f} g remaining"
    )

step_progress = min(steps_done / step_goal, 1.0) if step_goal > 0 else 0
st.markdown("**Daily movement goal**")
st.progress(step_progress)
st.caption(
    f"{step_progress * 100:.0f}% complete · "
    f"{max(0, step_goal - steps_done):,.0f} steps to go"
)

# ---------- End-of-day conclusion ----------
st.markdown(
    '<div class="section-title">Your day at a glance</div>'
    '<div class="section-subtitle">A simple wrap-up of your nutrition and movement</div>',
    unsafe_allow_html=True
)

net_calories = calories_consumed - calories_burnt

summary_left, summary_right = st.columns([1.15, 0.85])

with summary_left:
    st.metric("Estimated net calories", f"{net_calories:,.0f} kcal")
    if protein_target > 0 and protein_consumed >= protein_target:
        st.success("Protein goal reached — well done!")
    elif protein_target > 0:
        st.info(
            f"You're {protein_target - protein_consumed:.1f} g away "
            "from your protein goal."
        )
    else:
        st.caption("Set a protein target to track your progress.")

    if step_goal > 0 and steps_done >= step_goal:
        st.success("Movement goal reached — great consistency!")
    elif step_goal > 0:
        st.caption(f"{max(0, step_goal - steps_done):,.0f} steps remaining.")

with summary_right:
    st.markdown("""
    <div style="
        background:#FFFDF9;
        border:1px solid #F0E1D1;
        border-radius:18px;
        padding:22px;
        min-height:170px;
    ">
        <div style="font-size:12px;color:#C9672B;font-weight:700;
                    letter-spacing:1.5px;">A GENTLE REMINDER</div>
        <div style="font-family:'Playfair Display',serif;font-size:23px;
                    color:#3D3027;margin:10px 0;">
            Progress over perfection.
        </div>
        <div style="font-size:14px;color:#806C5B;line-height:1.7;">
            One day doesn't define your health. Consistency, balanced meals,
            movement, rest and recovery matter over time.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------- Save to Supabase ----------
st.markdown(
    '<div class="section-title">Save today\'s progress</div>',
    unsafe_allow_html=True
)
st.caption(
    "Save your daily numbers so you can retrieve them later in History."
)

if st.button(
    "💾 Save Daily Summary",
    type="primary",
    use_container_width=True
):
    payload = {
        "calories_consumed": int(calories_consumed),
        "protein_consumed": float(protein_consumed),
        "calorie_target": int(calorie_target),
        "protein_target": float(protein_target),
        "steps_done": int(steps_done),
        "step_goal": int(step_goal),
        "calories_burnt": float(calories_burnt),
    }

    if save_today(**payload):
        st.session_state["calories_consumed"] = calories_consumed
        st.session_state["protein_consumed"] = protein_consumed
        st.session_state["calorie_target"] = calorie_target
        st.session_state["protein_target"] = protein_target
        st.session_state["steps_done"] = steps_done
        st.session_state["step_goal"] = step_goal
        st.session_state["calories_burnt"] = calories_burnt
        st.success("Your daily summary was saved!")
    else:
        st.error(
            "Couldn't save the summary. Check the database error in your "
            "terminal and confirm the daily_logs columns."
        )

st.caption(
    "Nutrition and activity values are estimates. This dashboard is for "
    "general wellness tracking, not medical advice."
)
