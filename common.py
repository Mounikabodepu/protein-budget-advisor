"""Shared helpers for every page: styling, Supabase login, per-user data, Gemini call."""
import json
import time
from datetime import datetime, timedelta, timezone

import streamlit as st
from google import genai
from supabase import create_client

GEMINI_MODEL = "gemini-3.6-flash"
IST = timezone(timedelta(hours=5, minutes=30))  # India Standard Time


def today_str():
    """Today's date in India time. (Streamlit Cloud servers run on UTC, which would
    give the wrong 'today' between midnight and 5:30am IST.)"""
    return datetime.now(IST).date().isoformat()


# ---------------------------------------------------------------- styling

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, .stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, h1, h2, h3, h4 {
    font-family: 'Poppins', sans-serif;
}
.stApp {
    background-image: linear-gradient(rgba(10, 20, 15, 0.78), rgba(10, 20, 15, 0.78)), url("BG_URL");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
h1, h2, h3, p, label, .stMarkdown, .stCheckbox label, .stMultiSelect label, .stRadio label {
    color: #ffffff !important;
}
div[data-testid="stAlert"] p { color: #1b1b1b !important; }

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
section[data-testid="stSidebar"] label { font-weight: 600; font-size: 14px; }

div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input { border-radius: 8px !important; }

div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #ff6b35, #ff8c5a);
    color: white;
    border-radius: 10px;
    padding: 10px 26px;
    font-weight: 700;
    border: none;
    box-shadow: 0 4px 14px rgba(255, 107, 53, 0.4);
    transition: transform 0.15s ease;
}
div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover { transform: translateY(-2px); }

div[data-testid="stForm"] {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(153, 242, 200, 0.3);
    border-radius: 12px;
}

.recipe-card {
    background-color: rgba(255, 255, 255, 0.96);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 14px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
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

/* light card for charts, so axis labels stay readable on the dark background */
[class*="st-key-chartcard"] {
    background-color: rgba(255, 255, 255, 0.96);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 14px;
}
</style>
"""


def apply_style(background_url):
    st.markdown(_CSS.replace("BG_URL", background_url), unsafe_allow_html=True)


# ---------------------------------------------------------------- Supabase client + login

def get_client():
    """One Supabase client PER browser session (stored in session_state), so one
    person's login can never leak into another person's session."""
    if "sb" not in st.session_state:
        st.session_state["sb"] = create_client(
            st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
        )
    return st.session_state["sb"]


def show_auth_form():
    st.markdown("""
    <style>
    .stApp,
    [data-testid="stAppViewContainer"] {
        background: #FAF5ED !important;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 1rem;
    }

    .hero {
        padding: 2.5rem 0.5rem 1rem;
    }

    .brand {
        color: #C85D2B;
        font-size: 15px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: #39291F;
        font-size: 3.1rem;
        line-height: 1.12;
        letter-spacing: -1.5px;
        margin: 0 0 18px;
        font-weight: 800;
    }

    .hero h1 span {
        color: #D96835;
    }

    .hero p {
        color: #806D60;
        font-size: 1.05rem;
        line-height: 1.8;
        max-width: 420px;
    }

    .food-art {
        margin: 25px auto 15px;
        max-width: 440px;
        background: #F4E5D2;
        border-radius: 45% 45% 35% 35%;
        padding: 15px;
    }

    .feature {
        background: #FFFFFF;
        border: 1px solid #EFE3D5;
        color: #594639;
        border-radius: 13px;
        padding: 13px 15px;
        margin: 10px 0;
        font-size: 0.93rem;
    }

    .feature b {
        color: #C85D2B;
    }

    
.auth-card {
    background: #FFFFFF;
    border: 1px solid #F0E2D3;
    border-radius: 26px;
    padding: 2rem 1.7rem;
    box-shadow: 0 20px 55px rgba(87, 56, 32, 0.12);
    margin-top: 2rem;
}

.auth-card h2 {
    color: #39291F;
    font-size: 1.9rem;
    letter-spacing: -0.5px;
}

.auth-card [data-testid="stCaptionContainer"] {
    color: #806D60;
    line-height: 1.6;
}


    div[data-testid="stTabs"] {
        background: transparent;
    }

    div[data-testid="stTabs"] button[role="tab"] {
        color: #806D60;
        font-weight: 700;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #C85D2B;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background: #E77743;
    }

    div[data-testid="stTextInput"] label {
        color: #514238;
        font-weight: 600;
    }

    div[data-testid="stTextInput"] input {
        background: #FFFCF8;
        color: #39291F;
        border: 1px solid #E9DCCF;
        border-radius: 11px;
        min-height: 44px;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #E77743;
        box-shadow: 0 0 0 1px #E77743;
    }

    div[data-testid="stFormSubmitButton"] button {
        background: #D96835;
        color: white;
        border: none;
        border-radius: 11px;
        min-height: 47px;
        font-weight: 700;
        width: 100%;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background: #B94F24;
        color: white;
    }

    .auth-footer {
        text-align: center;
        color: #927E70;
        font-size: 0.82rem;
        padding: 25px 0 5px;
    }

    @media (max-width: 700px) {
        .hero h1 {
            font-size: 2.35rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.08, 0.92], gap="large")

    
    with left:
        st.markdown("""
    <div class="hero">
        <div class="brand">🥗 PROTEIN &amp; BALANCE</div>
        <h1>Eat better.<br>Feel <span>stronger.</span></h1>
        <p>
            Your everyday companion for smarter nutrition,
            balanced meals and a healthier relationship with food.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.image(
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"
        "?auto=format&fit=crop&w=1000&q=85",
        use_container_width=True
    )

    st.markdown("""
    <div class="feature">🥙 &nbsp; <b>Eat smarter</b> — build balanced meals</div>
    <div class="feature">🎯 &nbsp; <b>Stay on track</b> — monitor protein and calories</div>
    <div class="feature">💰 &nbsp; <b>Respect your budget</b> — plan affordable nutrition</div>
    """, unsafe_allow_html=True)


    with right:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown("## Welcome")
        st.caption("Sign in or create your account to get started.")

        login_tab, signup_tab = st.tabs(["Sign in", "Create account"])
        client = get_client()

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email address", key="login_email")
                password = st.text_input(
                    "Password", type="password", key="login_password"
                )
                submitted = st.form_submit_button("Sign in")

            if submitted:
                if not email.strip() or not password:
                    st.error("Please enter your email and password.")
                else:
                    try:
                        res = client.auth.sign_in_with_password({
                            "email": email.strip(),
                            "password": password
                        })
                        st.session_state["user"] = res.user
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not log in: {e}")

        with signup_tab:
            with st.form("signup_form"):
                name = st.text_input("Your name", key="signup_name")
                email = st.text_input("Email address", key="signup_email")
                password = st.text_input(
                    "Create password (min. 8 characters)",
                    type="password",
                    key="signup_password"
                )
                submitted = st.form_submit_button("Create my account")

            if submitted:
                if not name.strip():
                    st.error("Please enter your name.")
                elif "@" not in email or len(password) < 8:
                    st.error(
                        "Enter a valid email and a password of at least 8 characters."
                    )
                else:
                    try:
                        res = client.auth.sign_up({
                            "email": email.strip(),
                            "password": password,
                            "options": {
                                "data": {"display_name": name.strip()}
                            }
                        })

                        if res.session:
                            st.session_state["user"] = res.user
                            save_profile(display_name=name.strip())
                            st.rerun()
                        else:
                            st.success(
                                "Account created! Check your email if confirmation is required."
                            )
                    except Exception as e:
                        st.error(f"Could not create account: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-footer">
        MADE WITH CARE &nbsp; · &nbsp; YOUR GOALS, YOUR PROGRESS, YOUR JOURNEY 🌱
    </div>
    """, unsafe_allow_html=True)

def require_login():
    """Call at the top of every page. Shows the login screen and stops the page
    until someone is logged in. Returns the user once they are."""
    user = st.session_state.get("user")
    if user is None:
        show_auth_form()
        st.stop()
    with st.sidebar:
        st.markdown(f"**Signed in as**  \n{user.email}")
        if st.button("Log out", key="logout_btn"):
            try:
                get_client().auth.sign_out()
            except Exception:
                pass
            for k in ["user", "sb", "profile", "today_row", "protein_already_manual"]:
                st.session_state.pop(k, None)
            st.rerun()
    return user


# ---------------------------------------------------------------- saved data

def _db_error(action, e):
    st.warning(f"Couldn't {action} (your results are still shown): {e}")


def pref(profile, key, default):
    """Read a saved number as a whole int (Streamlit inputs need matching types)."""
    try:
        return int(round(float(profile.get(key))))
    except (TypeError, ValueError):
        return default


def load_profile():
    if "profile" not in st.session_state:
        user = st.session_state.get("user")
        data = {}
        try:
            res = get_client().table("profiles").select("*").eq("user_id", user.id).execute()
            data = res.data[0] if res.data else {}
        except Exception as e:
            _db_error("load your saved preferences", e)
        st.session_state["profile"] = data
    return st.session_state["profile"]


def save_profile(**fields):
    user = st.session_state.get("user")
    if not user:
        return False
    payload = {"user_id": user.id, "updated_at": datetime.now(timezone.utc).isoformat(), **fields}
    try:
        get_client().table("profiles").upsert(payload, on_conflict="user_id").execute()
        st.session_state["profile"] = {**st.session_state.get("profile", {}), **fields}
        return True
    except Exception as e:
        _db_error("save your preferences", e)
        return False


def load_today():
    cached = st.session_state.get("today_row")
    if cached and cached["date"] == today_str():
        return cached["row"]
    user = st.session_state.get("user")
    row = {}
    try:
        res = (get_client().table("daily_logs").select("*")
               .eq("user_id", user.id).eq("log_date", today_str()).execute())
        row = res.data[0] if res.data else {}
        st.session_state["today_row"] = {"date": today_str(), "row": row}
    except Exception as e:
        _db_error("load today's log", e)
    return row


def save_today(**fields):
    """Add/overwrite fields on today's row. Each page saves only its own fields."""
    user = st.session_state.get("user")
    if not user:
        return False
    payload = {"user_id": user.id, "log_date": today_str(), **fields}
    try:
        get_client().table("daily_logs").upsert(payload, on_conflict="user_id,log_date").execute()
        st.session_state["today_row"] = {"date": today_str(), "row": {**load_today(), **fields}}
        return True
    except Exception as e:
        _db_error("save today's log", e)
        return False


def load_history(days=30):
    user = st.session_state.get("user")
    if not user:
        return []
    try:
        res = (get_client().table("daily_logs").select("*").eq("user_id", user.id)
               .order("log_date", desc=True).limit(days).execute())
        return res.data or []
    except Exception as e:
        _db_error("load your history", e)
        return []


# ---------------------------------------------------------------- Gemini

def call_gemini(system_prompt, user_prompt, retries=3):
    """Ask Gemini for JSON. Retries a few times, because free-tier servers sometimes
    answer 'high demand' (503) for a moment."""
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    last_error = None
    for _ in range(retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL, contents=system_prompt + "\n\n" + user_prompt
            )
            cleaned = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except Exception as e:
            last_error = e
            time.sleep(2)
    raise last_error
