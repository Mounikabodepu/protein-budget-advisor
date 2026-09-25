import streamlit as st
from google import genai
import json

st.set_page_config(page_title="Calorie Tracker", page_icon="🍽️")

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
st.title("Calorie & Protein Tracker")
st.write("Tell me what you ate today, and your daily targets.")

with st.sidebar:
    st.header("Your Targets")
    calorie_target = st.number_input("Daily calorie target (kcal)", min_value=0, value=2000)
    protein_target_today = st.number_input("Daily protein target (grams)", min_value=0, value=120)

food_log = st.text_area(
    "What did you eat today? (describe freely, e.g. '2 eggs, a bowl of dal, one roti')",
    ""
)

SYSTEM_PROMPT = """You are a careful, honest nutrition estimator.

STRICT RULES:
1. All nutrition values are ESTIMATES based on typical Indian food
   composition - clearly label them as estimated.
2. Break down each distinct food item the user mentioned separately.
3. Do not invent food items the user did not mention.
4. Sum the totals accurately from the individual items.

Respond ONLY with valid JSON, no other text, no markdown formatting, in
exactly this structure:
{
  "items": [
    {
      "name": "...",
      "estimated_calories": <number>,
      "estimated_protein_grams": <number>,
      "estimated_carbs_grams": <number>,
      "estimated_fat_grams": <number>,
      "estimated_fiber_grams": <number>
    }
  ],
  "total_calories": <number>,
  "total_protein_grams": <number>,
  "total_carbs_grams": <number>,
  "total_fat_grams": <number>,
  "total_fiber_grams": <number>
}
"""

def get_calorie_analysis(food_log):
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    full_prompt = SYSTEM_PROMPT + f"\n\nHere is what I ate today:\n{food_log}"
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=full_prompt
    )
    cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned_text)


if st.button("Analyze My Day"):
    if not food_log.strip():
        st.warning("Please describe what you ate first.")
    else:
        with st.spinner("Analyzing..."):
            result = get_calorie_analysis(food_log)
            st.session_state['calories_consumed'] = result['total_calories']
            st.session_state['protein_consumed'] = result['total_protein_grams']
            st.session_state['calorie_target'] = calorie_target

    

            st.subheader("Breakdown (estimated)")
        for item in result["items"]:
            st.markdown(f"""
            <div class="recipe-card">
                <h4>{item['name']}</h4>
                <p>Calories: ~{item['estimated_calories']} kcal</p>
                <p>Protein: ~{item['estimated_protein_grams']}g | Carbs: ~{item['estimated_carbs_grams']}g | Fat: ~{item['estimated_fat_grams']}g | Fiber: ~{item['estimated_fiber_grams']}g</p>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("Today's Totals (estimated)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Calories", f"{result['total_calories']} kcal", f"target {calorie_target}")
        col2.metric("Protein", f"{result['total_protein_grams']}g", f"target {protein_target_today}")
        col3.metric("Carbs", f"{result['total_carbs_grams']}g")

        col4, col5 = st.columns(2)
        col4.metric("Fat", f"{result['total_fat_grams']}g")
        col5.metric("Fiber", f"{result['total_fiber_grams']}g")

        remaining_calories = max(calorie_target - result['total_calories'], 0)
        remaining_protein = max(protein_target_today - result['total_protein_grams'], 0)
        st.info(f"Remaining today: ~{remaining_calories} kcal, ~{remaining_protein}g protein")

        st.caption("Remember: all values are ESTIMATES - not a substitute for professional dietary advice.")