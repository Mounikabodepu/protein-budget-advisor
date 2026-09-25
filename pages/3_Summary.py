import streamlit as st

st.set_page_config(page_title="Daily Summary", page_icon="📊")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp {
    background-image: linear-gradient(rgba(8, 15, 12, 0.82), rgba(8, 15, 12, 0.82)),
                       url("https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1600&q=80");
    background-size: cover; background-position: center; background-attachment: fixed;
}
h1 { color: #ffffff !important; font-weight: 700 !important; text-shadow: 0 2px 8px rgba(0,0,0,0.4); }
h2, h3, p, label, .stMarkdown { color: #ffffff !important; }
div[data-testid="stMetric"] {
    background-color: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 10px;
    border: 1px solid rgba(153, 242, 200, 0.3);
}
div[data-testid="stMetricValue"] { color: #99f2c8 !important; }
div[data-testid="stMetricLabel"] { color: #ffffff !important; }
.recipe-card {
    background-color: rgba(255, 255, 255, 0.97); border-radius: 14px; padding: 18px 22px;
    margin-bottom: 14px; box-shadow: 0 6px 16px rgba(0,0,0,0.35); border-left: 5px solid #99f2c8;
}
.recipe-card h4 { color: #1f4037 !important; margin-bottom: 6px; }
.recipe-card p { color: #333333 !important; margin: 2px 0; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Today's Summary")
st.write("Pulling together your protein, calorie, and step data from the other pages.")

protein_target = st.session_state.get('protein_target')
calories_consumed = st.session_state.get('calories_consumed')
protein_consumed = st.session_state.get('protein_consumed')
calorie_target = st.session_state.get('calorie_target')
calories_burnt = st.session_state.get('calories_burnt')
steps_done = st.session_state.get('steps_done')
step_goal = st.session_state.get('step_goal')

missing = []
if protein_target is None: missing.append("Protein & Budget page")
if calories_consumed is None: missing.append("Calorie Tracker page")
if calories_burnt is None: missing.append("Steps page")

if missing:
    st.warning(f"Visit and use these pages first to see your full summary: {', '.join(missing)}")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Protein Consumed", f"{protein_consumed}g", f"target {protein_target}g")
    col2.metric("Calories Consumed", f"{calories_consumed} kcal", f"target {calorie_target}")
    col3.metric("Steps / Calories Burnt", f"{steps_done}", f"{calories_burnt:.0f} kcal burnt")

    net_calories = calories_consumed - calories_burnt

    st.markdown(f"""
    <div class="recipe-card">
        <h4>Net Calorie Balance (Today)</h4>
        <p>Consumed: {calories_consumed} kcal | Burnt (from steps only): {calories_burnt:.0f} kcal</p>
        <p><b>Net: {net_calories:.0f} kcal</b> ({'surplus' if net_calories > 0 else 'deficit'})</p>
    </div>
    """, unsafe_allow_html=True)

    protein_met = protein_consumed >= protein_target
    st.markdown(f"""
    <div class="recipe-card">
        <h4>Protein Adequacy</h4>
        <p>{'✅ You met your protein target today - supports muscle maintenance/growth (with resistance training).' if protein_met else '⚠️ You are below your protein target - may limit muscle maintenance/growth over time.'}</p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "IMPORTANT: This is ONE day of data. Real fat loss or muscle gain happens over "
        "weeks, and depends heavily on resistance training, sleep, consistency, and your "
        "individual metabolism - not just one day's numbers. As a very rough, long-term "
        "illustration only: a sustained daily deficit/surplus of this size, over time, "
        "roughly corresponds to a change of about "
        f"{abs(net_calories) / 7700:.2f} kg of body fat per day if sustained "
        "(7700 kcal ≈ 1kg fat, a standard approximation) - this is NOT a same-day result "
        "and does not account for your resting metabolic rate (BMR), only steps-based burn."
    )

    st.caption("This summary is for general fitness awareness only and is not medical or professional dietary advice.")