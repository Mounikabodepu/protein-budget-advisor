def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

daily_budget = 200  # in rupees - change this to your real budget
protein_target = 120  # in grams - change this to your real target

kitchen_items = read_file("my_kitchen.txt")

print("Budget:", daily_budget)
print("Protein target:", protein_target, "grams")
print("Kitchen items loaded:", kitchen_items)
from google import genai
import json

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
5. When multiple current kitchen items can reasonably be combined into one
   dish (e.g. milk + peanuts), include at least one such combined dish, not
   only single-item dishes.
6. If the user has NO current kitchen items at all, treat the entire protein
   target as the gap - dish_options can be empty, and suggested_item_to_buy
   should recommend the most budget-efficient way to hit the FULL target,
   possibly combining more than one cheap item if needed.

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
    client = genai.Client()

    full_prompt = (
        SYSTEM_PROMPT
        + f"\n\nMy budget for today is Rs.{daily_budget}."
        + f"\nMy remaining protein target for today is {protein_target} grams (already accounting for what I've eaten so far)."
        + f"\nHere is what I currently have in my kitchen:\n{kitchen_items}"
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=full_prompt

    )

    raw_text = response.text
    cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()

    return json.loads(cleaned_text)


print("\nCalling Gemini...\n")
result = get_ai_response(kitchen_items, daily_budget, protein_target)
print("=" * 60)
print("PROTEIN OPTIONS FROM YOUR KITCHEN (sorted by cost, estimated)")
print("=" * 60)

# Sort dish options by estimated cost, lowest first
sorted_dishes = sorted(result["dish_options"], key=lambda d: d["estimated_cost_rupees"])

for dish in sorted_dishes:
    print(f"\n{dish['name']}")
    print(f"  Protein: ~{dish['estimated_protein_grams']}g (estimated)")
    print(f"  Cost: ~Rs.{dish['estimated_cost_rupees']} (estimated)")

print("\n" + "=" * 60)
if result["target_met_with_current_items"]:
    print("Your current kitchen items can meet today's protein target.")
else:
    print("Your current items DON'T fully meet today's protein target.")
    suggestion = result["suggested_item_to_buy"]
    print(f"\nSuggested addition: {suggestion['name']}")
    print(f"  Estimated cost: Rs.{suggestion['estimated_cost_rupees']}")
    print(f"  Why: {suggestion['reason']}")

print("\n(Remember: all prices and protein values are ESTIMATES - verify before shopping.)")
