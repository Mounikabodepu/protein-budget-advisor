
import streamlit as st
import pandas as pd

from common import require_login, load_history

st.set_page_config(
    page_title="History | Protein & Balance",
    page_icon="📈",
    layout="wide"
)

require_login()

# Cream and warm-orange theme
st.markdown("""
<style>
    .stApp {
        background: #FBF5EC;
    }
    h1, h2, h3 {
        color: #633D29;
    }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #F0DDCC;
        padding: 18px;
        border-radius: 16px;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #F0DDCC;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Your Nutrition History")
st.caption(
    "Your saved daily summaries — actual intake, goal progress "
    "and activity over time."
)

# Load saved records from Supabase
try:
    history = load_history()
except Exception as e:
    st.error("Unable to load your saved history.")
    st.caption(f"Technical details: {e}")
    st.stop()

if not history:
    st.info(
        "No saved daily summaries yet. Open the Summary page, "
        "enter your daily values and select Save Daily Summary. "
        "Your saved records will appear here."
    )
    st.stop()

df = pd.DataFrame(history)

# Support the current Summary column names and older column names.
aliases = {
    "log_date": ["log_date", "date"],
    "calories_consumed": ["calories_consumed", "calories"],
    "protein_consumed": ["protein_consumed", "protein"],
    "calorie_target": ["calorie_target"],
    "protein_target": ["protein_target"],
    "steps_done": ["steps_done", "steps"],
    "step_goal": ["step_goal"],
    "calories_burnt": ["calories_burnt", "calories_burned"],
    "food_log": ["food_log", "food_consumed", "food_notes"],
}

for standard_name, possible_names in aliases.items():
    if standard_name not in df.columns:
        for old_name in possible_names:
            if old_name in df.columns:
                df[standard_name] = df[old_name]
                break

# Convert saved values to numeric values for calculations.
numeric_columns = [
    "calories_consumed",
    "calorie_target",
    "protein_consumed",
    "protein_target",
    "steps_done",
    "step_goal",
    "calories_burnt",
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

if "log_date" in df.columns:
    df["log_date"] = pd.to_datetime(
        df["log_date"], errors="coerce"
    ).dt.date
    df = df.dropna(subset=["log_date"])
    df = df.sort_values("log_date", ascending=False)

if df.empty:
    st.warning(
        "Records were returned, but no valid daily dates were found. "
        "Please check the log_date column in Supabase."
    )
    st.stop()

# Calculate progress and goal achievement from actual values.
def add_progress(actual_col, target_col, prefix):
    if actual_col in df.columns and target_col in df.columns:
        valid = (
            df[actual_col].notna()
            & df[target_col].notna()
            & (df[target_col] > 0)
        )

        df[f"{prefix}_progress_pct"] = float("nan")
        df.loc[valid, f"{prefix}_progress_pct"] = (
            df.loc[valid, actual_col]
            / df.loc[valid, target_col]
            * 100
        )

        if prefix == "calorie":
            # Calorie goal means staying at or below the target.
            df[f"{prefix}_goal_status"] = "Not recorded"
            df.loc[valid, f"{prefix}_goal_status"] = (
                df.loc[valid, actual_col]
                .le(df.loc[valid, target_col])
                .map({True: "Reached", False: "Over target"})
            )
        else:
            df[f"{prefix}_goal_status"] = "Not recorded"
            df.loc[valid, f"{prefix}_goal_status"] = (
                df.loc[valid, actual_col]
                .ge(df.loc[valid, target_col])
                .map({True: "Reached", False: "In progress"})
            )

add_progress(
    "calories_consumed", "calorie_target", "calorie"
)
add_progress(
    "protein_consumed", "protein_target", "protein"
)
add_progress("steps_done", "step_goal", "steps")

# Select a day to inspect.
st.subheader("Daily summary")

date_values = df["log_date"].tolist()
selected_date = st.selectbox(
    "Choose a saved day",
    options=date_values,
    format_func=lambda d: d.strftime("%d %b %Y")
)

day = df[df["log_date"] == selected_date].iloc[0]

# Main metrics
col1, col2, col3 = st.columns(3)

with col1:
    actual = day.get("calories_consumed")
    target = day.get("calorie_target")
    st.metric(
        "Calories consumed",
        f"{actual:,.0f} kcal" if pd.notna(actual) else "Not recorded",
        f"Target: {target:,.0f} kcal"
        if pd.notna(target) else None
    )

with col2:
    actual = day.get("protein_consumed")
    target = day.get("protein_target")
    st.metric(
        "Protein consumed",
        f"{actual:.1f} g" if pd.notna(actual) else "Not recorded",
        f"Target: {target:.1f} g"
        if pd.notna(target) else None
    )

with col3:
    actual = day.get("steps_done")
    target = day.get("step_goal")
    st.metric(
        "Steps completed",
        f"{actual:,.0f}" if pd.notna(actual) else "Not recorded",
        f"Goal: {target:,.0f}"
        if pd.notna(target) else None
    )

# Progress bars
st.subheader("🎯 Goal progress")

progress_items = [
    ("Calories", "calories_consumed", "calorie_target",
     "calorie_progress_pct", "calorie_goal_status"),
    ("Protein", "protein_consumed", "protein_target",
     "protein_progress_pct", "protein_goal_status"),
    ("Steps", "steps_done", "step_goal",
     "steps_progress_pct", "steps_goal_status"),
]

for label, actual_col, target_col, pct_col, status_col in progress_items:
    if actual_col not in df.columns or target_col not in df.columns:
        continue

    actual = day.get(actual_col)
    target = day.get(target_col)

    if pd.isna(actual) or pd.isna(target) or target <= 0:
        continue

    pct = min(max(float(actual / target), 0), 1)
    display_pct = day.get(pct_col)
    status = day.get(status_col, "Not recorded")

    st.markdown(f"**{label}** — {display_pct:.1f}% of target")
    st.progress(pct)
    st.caption(f"Status: {status}")

# Food consumed
st.subheader("🍽️ What you consumed")

food_log = day.get("food_log")

if pd.notna(food_log) and str(food_log).strip():
    st.markdown(
        f"""
        <div style="
            background:#FFFFFF;
            border:1px solid #F0DDCC;
            border-radius:14px;
            padding:18px;
            color:#633D29;
            white-space:pre-wrap;
        ">{food_log}</div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info(
        "No food log was saved for this day. "
        "The Summary page must save the food log for it to appear here."
    )

# Trends over time
st.subheader("📊 Progress over time")

trend_df = df.sort_values("log_date", ascending=True).copy()
trend_df["log_date"] = pd.to_datetime(trend_df["log_date"])

chart_metric = st.radio(
    "Choose a trend",
    ["Calories", "Protein", "Steps"],
    horizontal=True
)

trend_options = {
    "Calories": ("calories_consumed", "calorie_target"),
    "Protein": ("protein_consumed", "protein_target"),
    "Steps": ("steps_done", "step_goal"),
}

actual_col, target_col = trend_options[chart_metric]
chart_columns = {}

if actual_col in trend_df.columns:
    chart_columns["Actual"] = trend_df.set_index("log_date")[actual_col]

if target_col in trend_df.columns:
    chart_columns["Target"] = trend_df.set_index("log_date")[target_col]

if chart_columns:
    chart_df = pd.DataFrame(chart_columns).dropna(how="all")
    if not chart_df.empty:
        st.line_chart(chart_df)
    else:
        st.info("No recorded values are available for this chart.")
else:
    st.info("The selected metric is not available in your saved records.")

# Complete daily history table
st.subheader("🗓️ All saved daily summaries")

table_columns = [
    "log_date",
    "calories_consumed",
    "calorie_target",
    "calorie_goal_status",
    "protein_consumed",
    "protein_target",
    "protein_goal_status",
    "steps_done",
    "step_goal",
    "steps_goal_status",
    "calories_burnt",
]

available_columns = [
    c for c in table_columns if c in df.columns
]

display_df = df[available_columns].copy()

rename_columns = {
    "log_date": "Date",
    "calories_consumed": "Calories consumed",
    "calorie_target": "Calorie target",
    "calorie_goal_status": "Calorie goal",
    "protein_consumed": "Protein consumed (g)",
    "protein_target": "Protein target (g)",
    "protein_goal_status": "Protein goal",
    "steps_done": "Steps completed",
    "step_goal": "Step goal",
    "steps_goal_status": "Steps goal",
    "calories_burnt": "Calories burnt",
}

display_df = display_df.rename(columns=rename_columns)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "This page displays saved records. Goal status is calculated "
    "from the actual values and targets recorded for each day."
)
