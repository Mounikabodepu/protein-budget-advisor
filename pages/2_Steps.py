import streamlit as st

st.set_page_config(page_title="Steps Tracker", page_icon="🚶")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

* { font-family: 'Poppins', sans-serif; }

.stApp {
    background-image: linear-gradient(rgba(8, 15, 12, 0.82), rgba(8, 15, 12, 0.82)),
                       url("https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1600&q=80");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

h1 {
    color: #ffffff !important;
    font-weight: 700 !important;
    text-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
h2, h3, p, label, .stMarkdown { color: #ffffff !important; }

section[data-testid="stSidebar"] {
    background-color: rgba(12, 22, 18, 0.95);
    border-right: 1px solid rgba(153, 242, 200, 0.3);
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #99f2c8 !important;
    border-bottom: 2px solid #99f2c8;
    padding-bottom: 8px;
    margin-bottom: 16px;
}
section[data-testid="stSidebar"] label {
    font-weight: 600;
    font-size: 14px;
}

div[data-testid="stNumberInput"] input {
    border-radius: 8px !important;
    border: 1px solid rgba(153, 242, 200, 0.4) !important;
}

div[data-testid="stMetric"] {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 10px;
    border: 1px solid rgba(153, 242, 200, 0.3);
}
div[data-testid="stMetricValue"] { color: #99f2c8 !important; }
div[data-testid="stMetricLabel"] { color: #ffffff !important; }

.recipe-card {
    background-color: rgba(255, 255, 255, 0.97);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 14px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.35);
    border-left: 5px solid #99f2c8;
}
.recipe-card h4 { color: #1f4037 !important; margin-bottom: 6px; }
.recipe-card p { color: #333333 !important; margin: 2px 0; }
</style>
""", unsafe_allow_html=True)

st.title("Steps & Calories Burnt")
st.write("Track today's steps against your goal, and see calories burnt.")

with st.sidebar:
    st.header("🚶 Your Details")
    weight_kg = st.number_input("⚖️ Your weight (kg)", min_value=1, value=60)
    step_goal = st.number_input("🎯 Daily step goal", min_value=0, value=8000)

steps_done = st.number_input("Steps completed today", min_value=0, value=0)

if st.button("Calculate"):
    calories_burnt = steps_done * weight_kg * 0.0005
    st.session_state['calories_burnt'] = calories_burnt
    st.session_state['steps_done'] = steps_done
    st.session_state['step_goal'] = step_goal
    remaining_steps = max(step_goal - steps_done, 0)
    progress = min(steps_done / step_goal, 1.0) if step_goal > 0 else 0

    st.markdown(f"""
    <div class="recipe-card">
        <h4>Today's Progress</h4>
        <p>Steps completed: {steps_done} / {step_goal}</p>
        <p>Remaining steps: {remaining_steps}</p>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress)

    col1, col2 = st.columns(2)
    col1.metric("Calories Burnt", f"{calories_burnt:.1f} kcal")
    col2.metric("Steps Remaining", f"{remaining_steps}")

    if steps_done >= step_goal:
        st.success("🎉 You've hit your step goal for today!")
    else:
        st.info(f"Keep going — {remaining_steps} steps left to reach your goal.")

    st.caption("Calorie estimate uses a standard formula (steps × weight × 0.0005) - actual burn varies by pace, terrain, and individual metabolism.")