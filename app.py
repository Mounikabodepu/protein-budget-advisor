import streamlit as st

st.set_page_config(page_title="Protein Budget Advisor", page_icon="🍳", layout="centered")

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
h2, h3, p, label, .stMarkdown, .stCheckbox label, .stMultiSelect label {
    color: #ffffff !important;
}

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

div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius: 8px !important;
    border: 1px solid rgba(153, 242, 200, 0.4) !important;
}

div.stButton > button {
    background: linear-gradient(135deg, #ff6b35, #ff8c5a);
    color: white;
    border-radius: 10px;
    padding: 12px 28px;
    font-weight: 700;
    border: none;
    font-size: 16px;
    box-shadow: 0 4px 14px rgba(255, 107, 53, 0.4);
    transition: transform 0.15s ease;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(255, 107, 53, 0.55);
}

.recipe-card {
    background-color: rgba(255, 255, 255, 0.97);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 14px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.35);
    border-left: 5px solid #99f2c8;
}
.recipe-card h4 { color: #1f4037 !important; margin-bottom: 6px; font-weight: 700; }
.recipe-card p { color: #333333 !important; margin: 2px 0; }

div[data-testid="stMetric"] {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 10px;
    border: 1px solid rgba(153, 242, 200, 0.3);
}
div[data-testid="stMetricValue"] { color: #99f2c8 !important; }
div[data-testid="stMetricLabel"] { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

import streamlit as st
from google import genai
import json

st.title("Budget Protein Recipe Advisor")
st.write("Tell me your budget, protein goal, and what's in your kitchen.")

with st.sidebar:
    st.header("🎯 Your Details")

    daily_budget = st.number_input("💰 Daily budget (Rs.)", min_value=0, value=200)

    st.divider()

    protein_target = st.number_input("🎯 Protein target (grams)", min_value=0, value=120)
    current_intake = st.number_input("✅ Protein already had today (grams)", min_value=0, value=0)
    remaining_target = max(protein_target - current_intake, 0)
    st.session_state['protein_target'] = protein_target
    st.session_state['protein_already_manual'] = current_intake
    st.caption(f"Remaining protein needed today: **{remaining_target}g**")

    st.divider()

    st.subheader("🥘 What's in your kitchen?")
    no_items = st.checkbox("I don't have any protein items right now")

    if no_items:
        common_items = []
        manual_items = ""
        st.info("We'll suggest the cheapest way to hit your full protein target.")
    else:
        common_items = st.multiselect(
            "Select common items you have:",
            ["eggs", "paneer", "dal", "milk", "peanuts", "soya chunks", "chicken", "rice", "curd", "chickpeas"]
        )
        manual_items = st.text_area("Anything else?", "")

kitchen_items = ", ".join(common_items) + "\n" + manual_items

SYSTEM_PROMPT = """You are a careful, practical budget nutrition assistant.

STRICT RULES:
1. All prices and protein values you give are ESTIMATES based on typical
   Indian grocery prices - you must clearly label them as estimated.
2. "dish_options" must ONLY include dishes makeable with the CURRENT
   kitchen items listed - never include an item from "suggested_item_to_buy"
   in any dish_options recipe. These two are separate: dish_options reflects
   what's possible right now, suggested_item_to_buy is a separate
   recommendation for closing any remaining gap.
3. If suggesting an item to buy, pick the single most budget-efficient
   option to close the gap - not a long list.
4. Do not invent ingredients or dishes that are nutritionally implausible.

Respond ONLY with valid JSON, no other text, no markdown formatting, in
exactly this structure:
{
  "dish_options": [
    {"name": "...", "estimated_protein_grams": <number>, "estimated_cost_rupees": <number>}
  ],
  "target_met_with_current_items": <true or false>,
  "suggested_item_to_buy": {
    "name": "...",
    "estimated_cost_rupees": <number>,
    "reason": "..."
  }
}
If the target is already met, set suggested_item_to_buy to null.
"""

def get_ai_response(kitchen_items, daily_budget, protein_target):
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    full_prompt = (
        SYSTEM_PROMPT
        + f"\n\nMy budget for today is Rs.{daily_budget}."
        + f"\nMy protein target for today is {protein_target} grams."
        + f"\nHere is what I currently have in my kitchen:\n{kitchen_items}"
    )
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=full_prompt
    )
    cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned_text)


if st.button("Get Recommendation"):
    with st.spinner("Asking Gemini..."):
        result = get_ai_response(kitchen_items, daily_budget, remaining_target)

        st.subheader("Protein options from your kitchen (estimated)")
    sorted_dishes = sorted(result["dish_options"], key=lambda d: d["estimated_cost_rupees"])
    for dish in sorted_dishes:
        st.markdown(f"""
        <div class="recipe-card">
            <h4>{dish['name']}</h4>
            <p>Protein: ~{dish['estimated_protein_grams']}g</p>
            <p>Cost: ~Rs.{dish['estimated_cost_rupees']}</p>
        </div>
        """, unsafe_allow_html=True)

    if result["target_met_with_current_items"]:
        st.success("Your current kitchen items meet today's protein target.")
    else:
        st.warning("Your current items don't fully meet today's protein target.")
        suggestion = result["suggested_item_to_buy"]
        st.write(f"**Suggested addition:** {suggestion['name']}")
        st.write(f"Estimated cost: Rs.{suggestion['estimated_cost_rupees']}")
        st.write(f"Why: {suggestion['reason']}")

    st.caption("Remember: all prices and protein values are ESTIMATES - verify before shopping.")