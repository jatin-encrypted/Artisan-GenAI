# frontend.py

# --- IMPORTS ---
import streamlit as st
from datetime import date, timedelta
import calendar

# Import from backend file
from backend import (
    t, get_image_as_base64, load_dummy_events, filter_events_by_crafts,
    days_until, format_days, clean_day_artifacts, get_ai_content,
    generate_image_with_imagen, get_ai_content_from_image,
    get_market_trends, get_growth_plan, parse_firebase_error,
    auth_handler, db_handler, translations, firebase_auth
)

# --- UI HELPER FUNCTIONS ---
def clear_results():
    st.session_state.ai_results = None
    st.session_state.generated_image = None
    st.session_state.uploaded_image = None
    st.session_state.market_trends = None
    st.session_state.growth_plan = None
    st.session_state.story_is_ready = False
    st.session_state.current_prompt_fields = {}


# --- PAGE CONFIG & THEME ---
initial_lang = st.query_params.get("lang", "English")
st.set_page_config(
    page_title=t("app_title", initial_lang),
    page_icon="🏺",
    layout="wide",
)

final_theme_css = f"""
<style>
    :root {{
        --font: 'serif';
        --sidebar-background: #EADDC5;
        --primary-text-color: #5D4037;
        --accent-color: #d46c04;
        --accent-hover-color: #d77c02;
        --widget-background: #FFFFFF;
        --border-color: #D7CCC8;
        --border-radius: 12px;
        --shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }}

    /* This is the new, important part: make the inner container transparent */
    [data-testid="stAppViewContainer"] > .main > .block-container,
    [data-testid="stAppViewContainer"] {{
        background: transparent;
    }}

    /* You may also want to ensure other elements like the header remain semi-opaque */
    [data-testid="stHeader"] {{
        background-color: rgba(253, 245, 230, 0.8);
    }}

    h1, h2, h3, h4, h5, h6, .stMarkdown, label, p, .stAlert, [data-baseweb="tab"] {{
        color: var(--primary-text-color) !important;
        font-family: var(--font);
    }}
    p, li, div, label, .stMarkdown {{ font-size: 1.15rem; }}
    [data-testid="stSidebar"] {{
        background-color: var(--sidebar-background);
        border-right: 1px solid var(--border-color);
    }}
    /* The rest of your styles remain the same... */
    .stSelectbox, .stTextInput, .stTextArea, .stFileUploader, .stMultiSelect {{ border-radius: var(--border-radius); }}
    .stSelectbox > div > div, .stTextInput > div > div, .stTextArea > div > div, .stFileUploader > div > div {{ background-color: var(--widget-background); border: 1px solid var(--border-color); border-radius: var(--border-radius); box-shadow: var(--shadow); color: var(--primary-text-color); }}
    .stSelectbox div[role="listbox"] {{ background-color: var(--widget-background); border-radius: var(--border-radius); border: 1px solid var(--border-color); }}
    .stButton > button {{ background-color: var(--accent-color); color: white; border: none; padding: 12px 28px; font-size: 16px; font-weight: bold; border-radius: var(--border-radius); box-shadow: var(--shadow); transition: background-color 0.2s ease-in-out, transform 0.1s ease-in-out; }}
    .stButton > button:hover {{ background-color: var(--accent-hover-color); transform: scale(1.02); }}
    .stButton > button:active {{ transform: scale(0.98); }}
    .stButton > button:disabled {{ background-color: var(--accent-color); color: white; opacity: 1; cursor: not-allowed; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{ background-color: transparent; border-radius: var(--border-radius) var(--border-radius) 0 0; border-bottom: 2px solid var(--border-color); padding: 10px 16px; }}
    .stTabs [aria-selected="true"] {{ background-color: var(--widget-background); border-bottom: 2px solid var(--accent-color); box-shadow: var(--shadow); }}
    .stCodeBlock, .st-emotion-cache-1f2d20p {{ background-color: #F5F0E8; color: var(--primary-text-color); border-left: 5px solid var(--accent-color); border-radius: var(--border-radius); padding: 1rem; font-size: 1.15rem !important ; background-image="}}
    .stAlert {{ border-radius: var(--border-radius); box-shadow: var(--shadow); }};
    .stAlert.success {{ background-color: #E8F5E9; border-left: 8px solid #4CAF50; }}
    .stAlert.warning {{ background-color: #FFFDE7; border-left: 8px solid #FFC107; }}
    .stAlert.info {{ background-color: #E1F5FE; border-left: 8px solid #03A9F4; }}
</style>
"""
st.markdown(final_theme_css, unsafe_allow_html=True)

logo_path = "logo.gif"
logo_base64 = get_image_as_base64(logo_path)
if logo_base64:
    st.markdown(
        f'<link rel="icon" href="data:image/gif;base64,{logo_base64}" type="image/gif">',
        unsafe_allow_html=True,
    )
login_register_input_css = """
<style>
/* Login/Register form input backgrounds to white */
.stTextInput input, .stPasswordInput input, .stForm input, .stForm textarea {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #CCC !important;
    border-radius: 6px !important;
}
.stTextInput input:focus, .stPasswordInput input:focus, .stForm input:focus, .stForm textarea:focus {
    border: 1px solid #d46c04 !important;
    outline: none !important;
    box-shadow: 0 0 0 1px #d46c0433 !important;
}
.stPasswordInput button {
    filter: invert(0); /* keep visibility icon normal */
}
input::placeholder, textarea::placeholder {
    color: #666666 !important;
    opacity: 1 !important;
}
</style>
"""
st.markdown(login_register_input_css, unsafe_allow_html=True)

st.markdown("""
<style>
    /* Calendar layout fix: keep date at top, events below (no overlay) */
    .calendar-cell {
        min-height:120px;
        padding:8px 8px 6px;
        border-radius:10px;
        background:#E3BB95;
        box-shadow:0 2px 4px rgba(0,0,0,.06);
        position:relative;
        border:1px solid #E5E7EB;
        display:flex;
        flex-direction:column;
    }
    .calendar-cell.is-today { outline:2px solid #d46c04; }
    .calendar-cell.is-past { opacity:.78; }

    /* Date number now inline (not absolute) so events naturally flow below */
    .calendar-cell .day-number {
        position:static;
        background:transparent;
        color:#5D4037;
        width:auto;
        height:auto;
        border-radius:0;
        display:flex;
        align-items:center;
        justify-content:flex-start;
        font-size:13px;
        font-weight:700;
        padding:0;
        margin:0 0 4px 0;
    }

    /* Events container fills remaining vertical space */
    .calendar-cell .events-container {
        flex:1;
        display:flex;
        flex-direction:column;
        gap:3px;
        overflow:hidden;
    }

    /* Multi‑day bar styles */
    .event-bar {
        background:#8B4513;
        color:#fff;
        padding:3px 6px;
        font-size:11px;
        font-weight:500;
        border-radius:5px;
        white-space:nowrap;
        overflow:hidden;
        text-overflow:ellipsis;
        line-height:1.1;
    }

    /* ADD THIS NEW RULE for the links inside the event bars */
    .event-bar a {
        color: #FFFFFF !important;
        text-decoration: none !important;
    }

    .event-bar-start { border-top-right-radius:0; border-bottom-right-radius:0; }
    .event-bar-middle { border-radius:0; }
    .event-bar-end { border-top-left-radius:0; border-bottom-left-radius:0; }

    /* Remove legacy container style that pushed content over the date */
    .calendar-event-container { margin-top:0; background:transparent; padding:0; box-shadow:none; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Reminder button color states (works for English & Hindi labels) */
form.reminder-form input[type=submit][value="Set Reminder"],
form.reminder-form input[type=submit][value="रिमाइंडर सेट करें"] {
    background:#2563EB !important;
    border:none !important;
    color:#fff !important;
}
form.reminder-form input[type=submit][value="Cancel Reminder"],
form.reminder-form input[type=submit][value="रिमाइंडर रद्द करें"] {
    background:#B91C1C !important;
    border:none !important;
    color:#fff !important;
}
form.reminder-form input[type=submit] {
    width:100%;
    padding:10px 14px;
    font-weight:600;
    border-radius:8px;
    cursor:pointer;
    box-shadow:0 2px 4px rgba(0,0,0,0.15);
}
form.reminder-form input[type=submit]:hover {
    filter:brightness(1.08);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Reminder buttons: Set = brown, Cancel = grey */

/* SET REMINDER (English & Hindi) */
form[id^="rem_"] input[type=submit][value="Set Reminder"],
form[id^="sum_rem_"] input[type=submit][value="Set Reminder"],
form[id^="rem_"] input[type=submit][value="रिमाइंडर सेट करें"],
form[id^="sum_rem_"] input[type=submit][value="रिमाइंडर सेट करें"] {
    background:#5D4037 !important;  /* brown */
    border:none !important;
    color:#FFFFFF !important;
}

/* CANCEL REMINDER (English & Hindi) */
form[id^="rem_"] input[type=submit][value="Cancel Reminder"],
form[id^="sum_rem_"] input[type=submit][value="Cancel Reminder"],
form[id^="rem_"] input[type=submit][value="रिमाइंडर रद्द करें"],
form[id^="sum_rem_"] input[type=submit][value="रिमाइंडर रद्द करें"] {
    background:#6B7280 !important;  /* grey */
    border:none !important;
    color:#FFFFFF !important;
}

/* Base styling */
form[id^="rem_"] input[type=submit],
form[id^="sum_rem_"] input[type=submit] {
    width:100%;
    padding:10px 14px;
    font-weight:600;
    border-radius:8px;
    cursor:pointer;
    box-shadow:0 2px 4px rgba(0,0,0,0.15);
    font-size:14px;
    transition:filter .15s ease, transform .15s ease;
}

form[id^="rem_"] input[type=submit]:hover,
form[id^="sum_rem_"] input[type=submit]:hover {
    filter:brightness(1.08);
}

form[id^="rem_"] input[type=submit]:active,
form[id^="sum_rem_"] input[type=submit]:active {
    transform:scale(.97);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* --- Override hover behaviors as requested --- */

/* 1. Disable hover effects for 'Event Done' (disabled) buttons */
.stButton > button:disabled,
.stButton > button:disabled:hover,
.stButton > button[disabled]:hover {
    transform: none !important;
    filter: none !important;
    pointer-events: none !important;
}

/* 2. Reminder buttons:
      - Default already: Set = brown (#5D4037), Cancel = grey (#6B7280)
      - On hover: Set Reminder turns grey (while keeping brown default when not hovered)
      - Cancel Reminder keeps the same grey (no color shift)
*/

/* Remove old brightness hover for reminder forms */
form[id^="rem_"] input[type=submit]:hover,
form[id^="sum_rem_"] input[type=submit]:hover {
    filter: none !important;
    transform: none !important;
}

/* Set Reminder (English & Hindi) hover -> grey */
form[id^="rem_"] input[type=submit][value="Set Reminder"]:hover,
form[id^="sum_rem_"] input[type=submit][value="Set Reminder"]:hover,
form[id^="rem_"] input[type=submit][value="रिमाइंडर सेट करें"]:hover,
form[id^="sum_rem_"] input[type=submit][value="रिमाइंडर सेट करें"]:hover {
    background: #6B7280 !important;
    color: #FFFFFF !important;
}

/* Cancel Reminder hover stays same grey (explicitly fix) */
form[id^="rem_"] input[type=submit][value="Cancel Reminder"]:hover,
form[id^="sum_rem_"] input[type=submit][value="Cancel Reminder"]:hover,
form[id^="rem_"] input[type=submit][value="रिमाइंडर रद्द करें"]:hover,
form[id^="sum_rem_"] input[type=submit][value="रिमाइंडर रद्द करें"]:hover {
    background: #6B7280 !important;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Remove padding specifically for Set Reminder buttons (English & Hindi) */
form[id^="rem_"] input[type=submit][value="Set Reminder"],
form[id^="sum_rem_"] input[type=submit][value="Set Reminder"],
form[id^="rem_"] input[type=submit][value="रिमाइंडर सेट करें"],
form[id^="sum_rem_"] input[type=submit][value="रिमाइंडर सेट करें"] {
    padding: 0 !important;
    line-height: 1.25rem !important;
    min-height: 30px !important;
}

/* Keep Cancel Reminder padding as-is (explicit to avoid inheritance) */
form[id^="rem_"] input[type=submit][value="Cancel Reminder"],
form[id^="sum_rem_"] input[type=submit][value="Cancel Reminder"],
form[id^="rem_"] input[type=submit][value="रिमाइंडर रद्द करें"],
form[id^="sum_rem_"] input[type=submit][value="रिमाइंडर रद्द करें"] {
    padding: 10px 14px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Ensure 'Choose platforms for your plan' multiselect uses white background like other inputs */
div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
    background:#FFFFFF !important;
    color:#000000 !important;
    border:1px solid #CCC !important;
    border-radius:6px !important;
}
div[data-testid="stMultiSelect"] div[data-baseweb="popover"] {
    background:#FFFFFF !important;
    color:#000000 !important;
    border:1px solid #DDD !important;
    box-shadow:0 4px 10px rgba(0,0,0,0.08) !important;
}
div[data-testid="stMultiSelect"] div[data-baseweb="option"] {
    background:#FFFFFF !important;
    color:#000000 !important;
}
div[data-testid="stMultiSelect"] div[data-baseweb="option"]:hover {
    background:#F3F4F6 !important;
}
div[data-testid="stMultiSelect"] input {
    color:#000000 !important;
}
</style>
""", unsafe_allow_html=True)


# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = None
if 'user' not in st.session_state:
    st.session_state['user'] = {'uid': 'guest', 'email': 'guest@example.com', 'preferred_crafts': []}
if 'events' not in st.session_state: st.session_state['events'] = load_dummy_events()
if 'reminders' not in st.session_state: st.session_state['reminders'] = {} # dict: uid -> [event_ids]
if 'ai_results' not in st.session_state: st.session_state.ai_results = None
if 'generated_image' not in st.session_state: st.session_state.generated_image = None
if 'uploaded_image' not in st.session_state: st.session_state.uploaded_image = None
if 'market_trends' not in st.session_state: st.session_state.market_trends = None
if 'growth_plan' not in st.session_state: st.session_state.growth_plan = None
if 'story_is_ready' not in st.session_state: st.session_state.story_is_ready = False
if 'current_prompt_fields' not in st.session_state: st.session_state.current_prompt_fields = {}
if 'selected_workflow_key' not in st.session_state:
    # Migration: map any legacy localized label to a stable key
    legacy_label = st.session_state.get('selected_workflow')
    key_map = {
        "workflow_option_1": "generate_kit",
        "workflow_option_2": "discover_trends",
        "workflow_option_3": "growth_plan",
        "workflow_option_4": "events_calendar"
    }
    mapped = None
    if legacy_label:
        # Try both English & Hindi (extend if more UI languages added)
        for trans_lang in ["English","Hindi"]:
            for opt_key, stable in key_map.items():
                if translations[trans_lang].get(opt_key) == legacy_label:
                    mapped = stable
                    break
            if mapped: break
    st.session_state.selected_workflow_key = mapped # stays None if none selected
if 'calendar_year' not in st.session_state: st.session_state.calendar_year = date(2025,9,12).year
if 'calendar_month' not in st.session_state: st.session_state.calendar_month = date(2025,9,12).month
if 'reminder_days' not in st.session_state: st.session_state.reminder_days = 14

# --- LOGIN / REGISTER PAGE ---
def show_login_page():
    # --- VISUAL CONTAINER STYLE ---
    # This block defines how the login box will look
    st.markdown("""
    <style>
    .login-container {
        padding: 2rem 2.5rem;
        background-color: rgba(255, 255, 255, 0.85); /* Semi-transparent white */
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px); /* Optional: frosted glass effect */
        max-width: 450px;
        margin: auto; /* Center the container on the page */
        margin-top: 3rem; /* Add some space from the top */
    }
    </style>
    """, unsafe_allow_html=True)

    # --- LOGO AND TITLE ---
    logo_path = "logo.gif"
    app_title_text = t('app_title', 'English') 
    try:
        logo_base64 = get_image_as_base64(logo_path)
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/gif;base64,{logo_base64}" width="120" style="margin-bottom: 0.5rem; margin-top: -3rem;">
                <h1 style="font-family: 'serif'; font-weight: 600; font-size: 3rem; color: #5D4037; margin: -5;margin-top: -3rem;">{app_title_text}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.title(f"🏺 {app_title_text}")
        st.warning(f"Logo file '{logo_path}' not found.")

    # --- LOGIN/REGISTER FORM ---
    
    st.markdown("<p style='text-align: center;'>Please log in or register to continue.</p>", unsafe_allow_html=True)
    
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Login", use_container_width=True)
            if submit:
                with st.spinner("Logging in..."):
                    user, err = firebase_auth.login(auth_handler, email, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_info = user
                        data = firebase_auth.load_user_data(db_handler, user['localId'])
                        st.session_state['user'] = {'uid': user['localId'], 'email': user['email'], 'preferred_crafts': data.get('preferred_crafts', [])}
                        st.session_state['reminders'] = { user['localId']: data.get('reminders', []) }
                        st.rerun()
                    else:
                        st.error(parse_firebase_error(err))

    with register_tab:
        with st.form("register_form"):
            new_email = st.text_input("Email", key="reg_email", placeholder="your@email.com")
            new_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="At least 6 characters")
            confirm = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Repeat your password")
            reg_submit = st.form_submit_button("Register", use_container_width=True)
            if reg_submit:
                with st.spinner("Creating account..."):
                    if new_pass == confirm:
                        user, err = firebase_auth.sign_up(auth_handler, new_email, new_pass)
                        if user:
                            st.success("Registration successful! Please log in.")
                        else:
                            st.error(parse_firebase_error(err))
                    else:
                        st.error("Passwords do not match.")
            
# --- MAIN APP UI ---
def show_main_app():
    page_language = st.query_params.get("lang", "English")

    logo_path = "logo.gif"
    logo_base64 = get_image_as_base64(logo_path)
    app_title_text = t('app_title', page_language) # Get title text
# This block creates a single, stable title element with the logo
    if logo_base64:
        st.markdown(
            f"""
            <style>
                .title-container {{
                    display: flex;
                    align-items: center;
                    
                    gap: 2px !important; /* Adjust the space between logo and text */
                }}
                .title-text {{
                    font-family: 'serif';      /* Matches your app's theme font */
                    font-weight: 600;
                    font-size: 4.5rem !important;      /* Matches Streamlit's default h1 size */
                    color: #5D4037;       /* Matches your app's theme color */
                    margin: 0;
                    margin-left: 1px !important;/* <-- AND ADDING THIS INSTEAD */
                    padding-top: 5px;       /* Fine-tunes vertical alignment */
                }}
            </style>

            <div class="title-container">
                <img src="data:image/gif;base64,{logo_base64}" width="120">
                <h1 class="title-text">{app_title_text}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Fallback in case the logo doesn't load
        st.title(app_title_text)

    st.markdown(t('app_subheader', page_language))

    with st.sidebar:
        st.header(f"⚙ {t('controls_header', page_language)}")

        if st.session_state.user_info:
            st.write(f"Welcome, {st.session_state.user_info.get('email','Artisan')}!")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user_info = None
                keep = ['logged_in','user_info']
                for k in list(st.session_state.keys()):
                    if k not in keep:
                        del st.session_state[k]
                st.rerun()

        page_language_list = list(translations.keys())
        content_language_list = ["English","Hindi","Hinglish","Bengali","Tamil","Gujarati","Marathi","Telugu","Kannada","Malayalam","Odia","Punjabi","Urdu"]

        def on_lang_change():
            st.query_params["lang"] = st.session_state.page_lang_selector
        sel_idx = page_language_list.index(page_language) if page_language in page_language_list else 0
        st.selectbox(
            t('page_language_label', page_language),
            page_language_list,
            index=sel_idx,
            help=t('page_language_help', page_language),
            key='page_lang_selector',
            on_change=on_lang_change
        )

        # --- Stable workflow keys & translation mapping ---
        WORKFLOW_KEY_TO_TRANS_KEY = {
            "generate_kit": "workflow_option_1",
            "discover_trends": "workflow_option_2",
            "growth_plan": "workflow_option_3",
            "events_calendar": "workflow_option_4"
        }
        ORDERED_WORKFLOWS = ["generate_kit","discover_trends","growth_plan","events_calendar"]

        # Build localized labels list
        localized_labels = [t(WORKFLOW_KEY_TO_TRANS_KEY[k], page_language) for k in ORDERED_WORKFLOWS]

        # Determine current index (fallback 0)
        try:
            current_idx = ORDERED_WORKFLOWS.index(st.session_state.selected_workflow_key) \
                if st.session_state.selected_workflow_key else 0
        except ValueError:
            current_idx = 0

        def on_workflow_change():
            chosen_label = st.session_state.sidebar_workflow_label
            for k in ORDERED_WORKFLOWS:
                if chosen_label == t(WORKFLOW_KEY_TO_TRANS_KEY[k], page_language):
                    st.session_state.selected_workflow_key = k
                    break

        st.radio(
            t('workflow_label', page_language),
            localized_labels,
            index=current_idx,
            key='sidebar_workflow_label',
            on_change=on_workflow_change
        )

    # MOVED CONTENT LANGUAGE DROPDOWN HERE
        st.selectbox(
            t('caption_language_label', page_language),
            content_language_list,
            help=t('caption_language_help', page_language),
            key='caption_language' # Using a stable key
        )

        st.markdown("---")
        if st.button(t('clear_button', page_language), on_click=clear_results, use_container_width=True):
            st.rerun()

        st.markdown("---")
        st.header(t('event_preferences_header', page_language))
        # ... (rest of sidebar code) ...
        st.markdown(t('event_preferences_info', page_language))

        # --- Craft Tag Localization (Event Preferences) ---
        all_tags_canonical = sorted({tag for ev in st.session_state['events'] for tag in ev['craft_tags']})

        craft_tag_map_hi = {
            "Terracotta clay": "टेराकोटा मिट्टी",
            "Ceramics": "सिरेमिक",
            "Pottery": "मिट्टी कला",
            "Brass": "पीतल",
            "Wood": "लकड़ी",
            "Stone": "पत्थर",
            "Leather": "चमड़ा",
            "Glass": "कांच",
            "Paper": "कागज",
            "Bamboo": "बांस",
            "Fabric": "वस्त्र",
            "Silk": "रेशम",
            "Weaving": "बुनाई",
            "Embroidery": "कढ़ाई",
            "Bandhani": "बांधनी",
            "Wool": "ऊन",
            "Painting": "पेंटिंग",
            "Art": "कला",
            "Metals": "धातु",
            "Carving": "नक्काशी",
            "Toys": "खिलौने",
            "All": "सभी",
            "Policy": "नीति",
            "Market": "बाज़ार",
            "National": "राष्ट्रीय",
            "Festive": "उत्सव"
        }

        if page_language == "Hindi":
            display_tags = [craft_tag_map_hi.get(tag, tag) for tag in all_tags_canonical]
            current_pref_display = [craft_tag_map_hi.get(tag, tag)
                                    for tag in st.session_state['user'].get('preferred_crafts', [])]
            selection_display = st.multiselect(
                t('select_crafts_label', page_language),
                display_tags,
                default=current_pref_display
            )
            # Map back to canonical English for logic/storage
            inverse_map = {v: k for k, v in craft_tag_map_hi.items()}
            selected_crafts = [inverse_map.get(d, d) for d in selection_display]
        else:
            selected_crafts = st.multiselect(
                t('select_crafts_label', page_language),
                all_tags_canonical,
                default=st.session_state['user'].get('preferred_crafts', [])
            )

        uid = st.session_state['user']['uid'] # Define uid for saving preferences
        if selected_crafts != st.session_state['user'].get('preferred_crafts', []):
            st.session_state['user']['preferred_crafts'] = selected_crafts
            data_to_save = {
                'preferred_crafts': selected_crafts,
                'reminders': st.session_state['reminders'].get(uid, [])
            }
            firebase_auth.save_user_data(db_handler, uid, data_to_save)
            st.toast("Preferences saved!")

        st.session_state.reminder_days = st.number_input(
            t('notify_days_label', page_language),
            min_value=1, max_value=90, value=st.session_state.reminder_days
        )

    if st.session_state.selected_workflow_key is None:
        st.markdown("### " + t('choose_path_header', page_language))
        st.info(t('landing_info', page_language))
        c1, c2 = st.columns(2)
        with c1:
            if st.button(t('path_option_1', page_language), use_container_width=True):
                st.session_state.selected_workflow_key = "generate_kit"; st.rerun()
            if st.button(t('path_option_3', page_language), use_container_width=True):
                st.session_state.selected_workflow_key = "growth_plan"; st.rerun()
        with c2:
            if st.button(t('path_option_2', page_language), use_container_width=True):
                st.session_state.selected_workflow_key = "discover_trends"; st.rerun()
            if st.button(t('path_option_4', page_language), use_container_width=True):
                st.session_state.selected_workflow_key = "events_calendar"; st.rerun()
        st.markdown("---")
        st.info(t('info_box', page_language))
        return

    workflow_key = st.session_state.selected_workflow_key

    # Region options (localized)
    base_regions = [
        "Jaipur, Rajasthan","Kutch, Gujarat","Madhubani, Bihar","Bishnupur, West Bengal",
        "Varanasi, Uttar Pradesh","New Delhi / Delhi","Mumbai, Maharashtra","Kolkata, West Bengal",
        "Chennai, Tamil Nadu","Bengaluru, Karnataka","Hyderabad, Telangana","Pune, Maharashtra",
        "Ahmedabad, Gujarat","Surat, Gujarat","Lucknow, Uttar Pradesh","Srinagar, Jammu & Kashmir",
    ]
    region_map_hi = {
        "Jaipur, Rajasthan": "जयपुर, राजस्थान",
        "Kutch, Gujarat": "कच्छ, गुजरात",
        "Madhubani, Bihar": "मधुबनी, बिहार",
        "Bishnupur, West Bengal": "बिष्णुपुर, पश्चिम बंगाल",
        "Varanasi, Uttar Pradesh": "वाराणसी, उत्तर प्रदेश",
        "New Delhi / Delhi": "नई दिल्ली / दिल्ली",
        "Mumbai, Maharashtra": "मुंबई, महाराष्ट्र",
        "Kolkata, West Bengal": "कोलकाता, पश्चिम बंगाल",
        "Chennai, Tamil Nadu": "चेन्नई, तमिलनाडु",
        "Bengaluru, Karnataka": "बेंगलुरु, कर्नाटक",
        "Hyderabad, Telangana": "हैदराबाद, तेलंगाना",
        "Pune, Maharashtra": "पुणे, महाराष्ट्र",
        "Ahmedabad, Gujarat": "अहमदाबाद, गुजरात",
        "Surat, Gujarat": "सूरत, गुजरात",
        "Lucknow, Uttar Pradesh": "लखनऊ, उत्तर प्रदेश",
        "Srinagar, Jammu & Kashmir": "श्रीनगर, जम्मू और कश्मीर",
    }
    if page_language == "Hindi":
        region_options_display = [region_map_hi[r] for r in base_regions] + [t('other_option', page_language)]
        # reverse map for lookup if needed later
        region_reverse_map = {region_map_hi[k]: k for k in region_map_hi}
    else:
        region_options_display = base_regions + [t('other_option', page_language)]
        region_reverse_map = {}

    EXTENDED_REGION_OPTIONS = [
        "Jaipur, Rajasthan","Kutch, Gujarat","Madhubani, Bihar","Bishnupur, West Bengal",
        "Varanasi, Uttar Pradesh","New Delhi / Delhi","Mumbai, Maharashtra","Kolkata, West Bengal",
        "Chennai, Tamil Nadu","Bengaluru, Karnataka","Hyderabad, Telangana","Pune, Maharashtra",
        "Ahmedabad, Gujarat","Surat, Gujarat","Lucknow, Uttar Pradesh","Srinagar, Jammu & Kashmir",
        t('other_option', page_language)
    ]

    # WORKFLOW 1
    if workflow_key == "generate_kit":
        caption_language = st.session_state.caption_language
        st.subheader(t('generate_kit_subheader', page_language))
        source_choice = st.radio(
            t('image_source_label', page_language),
            [t('source_option_1', page_language), t('source_option_2', page_language)],
            key='image_source_radio'
        )
        st.markdown("---")
        prompt_fields = {}
        if source_choice == t('source_option_1', page_language):
            st.markdown("#### " + t('prompt_subheader', page_language))

            # --- Title (translated label) ---
            prompt_fields['title'] = st.text_input(
                t('field_label_title', page_language),
                placeholder=t('prompt_placeholder_title', page_language),
                key='ai_title'
            )

            # --- Materials (translated label & option localization for Hindi) ---
            base_material_options = [
                "Terracotta clay","Brass","Wood","Ceramics","Stone",
                "Leather","Glass","Paper","Bamboo"
            ]
            if page_language == "Hindi":
                material_map_hi = {
                    "Terracotta clay": "टेराकोटा मिट्टी",
                    "Brass": "पीतल",
                    "Wood": "लकड़ी",
                    "Ceramics": "सिरेमिक",
                    "Stone": "पत्थर",
                    "Leather": "चमड़ा",
                    "Glass": "कांच",
                    "Paper": "कागज",
                    "Bamboo": "बांस"
                }
                material_options = [material_map_hi.get(m, m) for m in base_material_options]
            else:
                material_options = base_material_options
            material_options.append(t('other_option', page_language))

            selected_material = st.selectbox(
                t('field_label_materials', page_language),
                material_options,
                key='ai_materials'
            )
            if selected_material == t('other_option', page_language):
                prompt_fields['materials'] = st.text_input(
                    t('other_specify', page_language),
                    placeholder=t('prompt_placeholder_materials', page_language),
                    key='ai_materials_other'
                )
            else:
                prompt_fields['materials'] = selected_material

            # --- Region (translated label + localized names) ---
            selected_region_display = st.selectbox(
                t('field_label_region', page_language),
                region_options_display,
                key='ai_region'
            )
            if selected_region_display == t('other_option', page_language):
                prompt_fields['region'] = st.text_input(
                    t('other_specify', page_language),
                    placeholder=t('prompt_placeholder_region', page_language),
                    key='ai_region_other'
                )
            else:
                # store canonical English if Hindi selected (for consistent AI prompt), else the same
                if page_language == "Hindi":
                    prompt_fields['region'] = region_reverse_map.get(selected_region_display, selected_region_display)
                else:
                    prompt_fields['region'] = selected_region_display

            # --- Tone (translated label & option localization for Hindi) ---
            base_tone_options = ["rustic","festive","modern","cultural","elegant","minimalist"]
            if page_language == "Hindi":
                tone_map_hi = {
                    "rustic": "देहाती",
                    "festive": "उत्सवपूर्ण",
                    "modern": "आधुनिक",
                    "cultural": "सांस्कृतिक",
                    "elegant": "सौम्य",
                    "minimalist": "सरल"
                }
                tone_options = [tone_map_hi.get(tn, tn) for tn in base_tone_options]
            else:
                tone_options = base_tone_options
            tone_options.append(t('other_option', page_language))

            selected_tone = st.selectbox(
                t('field_label_tone', page_language),
                tone_options,
                key='ai_tone'
            )
            if selected_tone == t('other_option', page_language):
                prompt_fields['tone'] = st.text_input(
                    t('other_specify', page_language),
                    placeholder=t('prompt_placeholder_tone', page_language),
                    key='ai_tone_other'
                )
            else:
                prompt_fields['tone'] = selected_tone
        else: # Upload path
            st.markdown("#### " + t('upload_image_subheader', page_language))
            
            # --- CONDITIONAL UI: Show Image or Uploader ---
            # First, check if an image is already stored in the session state
            if 'uploaded_image' in st.session_state and st.session_state.uploaded_image is not None:
                # If an image exists, display it and a button to remove it.
                st.image(st.session_state.uploaded_image, caption=t('user_image_caption', page_language), use_container_width=True)
                if st.button("Remove Image", key="remove_image"):
                    st.session_state.uploaded_image = None
                    st.rerun()
            else:
                # If no image exists, show the file uploader.
                uploaded_file = st.file_uploader(
                    t('image_uploader_label', page_language),
                    type=['png', 'jpg', 'jpeg'],
                    help=t('image_uploader_help', page_language),
                    key='kit_file_uploader'
                )
                # When a file is uploaded, save it to the state and immediately rerun the script.
                # This will cause the above 'if' block to run, replacing the uploader with the image.
                if uploaded_file is not None:
                    st.session_state.uploaded_image = uploaded_file
                    st.rerun()

        # --- COMMON ELEMENTS for workflow 1 ---
        st.text_area(t('desc_heading', page_language), key='common_description_area', placeholder=t('prompt_placeholder_description', page_language))

        if st.button(t('generate_button', page_language), use_container_width=True, type="primary", key="generate_with_ai_or_upload"):
            if source_choice == t('source_option_1', page_language):
                if st.session_state.get('ai_title'): # VALIDATION: Check for Title
                    with st.spinner(t('spinner_text_content', page_language).format(caption_lang=caption_language)):
                        final_fields = {
                            'title': st.session_state.get('ai_title',''),
                            'materials': st.session_state.get('ai_materials_other', st.session_state.get('ai_materials','')),
                            'region': st.session_state.get('ai_region_other', st.session_state.get('ai_region','')),
                            'tone': st.session_state.get('ai_tone_other', st.session_state.get('ai_tone','')),
                            'description': st.session_state.get('common_description_area','')
                        }
                        st.session_state.ai_results = get_ai_content(final_fields, caption_language)
                    if st.session_state.ai_results:
                        parts = []
                        for k in ['title','materials','region','tone','description']:
                            v = final_fields.get(k)
                            if v: parts.append(f"{k.capitalize()}: {v}")
                        img_prompt = ", ".join(parts) or "Handcrafted Indian artisan item"
                        with st.spinner(t('spinner_text_image', page_language)):
                            st.session_state.generated_image = generate_image_with_imagen(img_prompt)
                        st.success(t('content_ready', page_language))
                else:
                    st.warning(t('prompt_warning', page_language))
            else:  # User Upload Path
                # Check for the file in session_state before generating content
                if 'uploaded_image' not in st.session_state or st.session_state.uploaded_image is None:
                    st.warning(t('upload_warning', page_language))
                else:
                    caption_language = st.session_state.caption_language
                    description = st.session_state.get('common_description_area', '')
                    with st.spinner(t('spinner_text_content', page_language).format(caption_lang=caption_language)):
                        st.session_state.ai_results = get_ai_content_from_image(
                            st.session_state.uploaded_image,
                            caption_language,
                            description
                        )

                    if st.session_state.ai_results:
                        st.success(t('content_ready', page_language))

    # WORKFLOW 2
    elif workflow_key == "discover_trends":
        st.subheader(t('trends_subheader', page_language))
        trends_language = st.session_state.caption_language

        trends_region = st.text_input(
            t('field_label_region', page_language),
            placeholder=t('prompt_placeholder_region', page_language),
            key='trends_region'
        )
        craft_type = st.text_input(
            t('trends_label', page_language),
            placeholder=t('trends_placeholder', page_language)
        )
        if st.button(t('trends_button', page_language), use_container_width=True):
            if craft_type and trends_region:
                clear_results()
                with st.spinner(
                    t('spinner_text_trends', page_language).format(trends_lang=trends_language)
                ):
                    st.session_state.market_trends = get_market_trends(
                        trends_region,
                        trends_language,
                        craft_type
                    )
            else:
                st.warning(t('trends_warning', page_language))

    # WORKFLOW 3
    elif workflow_key == "growth_plan":
        st.subheader(t('planner_subheader', page_language))
        content_language_list = ["English","Hindi","Hinglish","Bengali","Tamil","Gujarati","Marathi"]
        plan_language = st.selectbox(t('plan_language_label', page_language), content_language_list, key='plan_lang')
        planner_region = st.text_input(
            t('field_label_region', page_language),
            placeholder=t('prompt_placeholder_region', page_language),
            key='planner_region'
        )
        platforms = st.multiselect(
            t('planner_platform_label', page_language),
            ["Instagram","Facebook","X"],
            placeholder=t('planner_platform_placeholder', page_language)
        )
        craft_type = st.text_input(t('planner_craft_label', page_language), placeholder=t('planner_craft_placeholder', page_language))
        target_audience = st.text_input(t('planner_audience_label', page_language), placeholder=t('planner_audience_placeholder', page_language))
        if st.button(t('planner_button', page_language), use_container_width=True):
            if platforms and craft_type and planner_region:
                clear_results()
                with st.spinner(t('spinner_text_planner', page_language).format(plan_lang=plan_language)):
                    st.session_state.growth_plan = get_growth_plan(planner_region, plan_language, platforms, craft_type, target_audience)
            else:
                st.warning(t('planner_warning', page_language))

    # WORKFLOW 4
    elif workflow_key == "events_calendar":
        st.subheader(t('events_header', page_language))

        # --- Reminder & Event Window Logic Updates ---
        today_ref = date(2025, 9, 13) # single consistent 'today'
        retention_days = 14 # keep ended events up to 2 weeks old
        reminder_window_days = st.session_state.reminder_days

        uid = st.session_state['user']['uid']
        reminders_for_user = set(st.session_state['reminders'].get(uid, []))

        # Filter by crafts first
        base_events = filter_events_by_crafts(
            st.session_state['events'],
            st.session_state['user'].get('preferred_crafts', [])
        )

        # Keep past events only if they ended within retention window
        retention_cutoff = today_ref - timedelta(days=retention_days)
        visible_events = [
            ev for ev in base_events
            if not (ev['end_date'] < retention_cutoff) # drop very old past events
        ]

        # Upcoming events (within user reminder window) for summary section (future or ongoing)
        upcoming_horizon = today_ref + timedelta(days=reminder_window_days)
        upcoming_candidates = [
            ev for ev in visible_events
            if ev['start_date'] <= upcoming_horizon and ev['end_date'] >= today_ref
        ]

        # Recently ended events (ended within retention window, i.e., last 14 days)
        recently_ended = [
            ev for ev in visible_events
            if ev['end_date'] < today_ref and ev['end_date'] >= retention_cutoff
        ]

        def persist_reminders():
            st.session_state['reminders'][uid] = list(reminders_for_user)
            firebase_auth.save_user_data(
                db_handler,
                uid,
                {
                    'preferred_crafts': st.session_state['user'].get('preferred_crafts', []),
                    'reminders': st.session_state['reminders'][uid]
                }
            )

        # --- Summary / Quick Reminder Toggle Section ---
        st.markdown(f"**Upcoming & Ongoing (next {reminder_window_days} days)**")
        if not upcoming_candidates:
            st.info(t('no_upcoming_events', page_language).format(days=reminder_window_days))
        else:
            for ev in sorted(upcoming_candidates, key=lambda e: (e['start_date'], e['title'])):
                d_left = days_until(ev['start_date'])
                if d_left > 0:
                    status = f"⏳ {t('event_when', page_language).format(days=format_days(d_left, page_language))}"
                elif d_left == 0:
                    status = "✨ Starting Today!"
                else:
                    status = f"🟢 {t('event_ongoing', page_language)}"
                cols = st.columns([4, 2])
                with cols[0]:
                    st.markdown(f"**{ev['title']}** · {ev['city']} — {status}")
                with cols[1]:
                    if ev['start_date'] > today_ref: # only future events toggle reminders
                        # Use a form so we can apply CSS based on the label (value attribute)
                        with st.form(f"sum_rem_{ev['id']}", clear_on_submit=False):
                            is_set = ev['id'] in reminders_for_user
                            btn_label = t('cancel_reminder_button', page_language) if is_set else t('set_reminder_button', page_language)
                            submitted = st.form_submit_button(btn_label, use_container_width=True, help="Toggle reminder")
                            if submitted:
                                if is_set:
                                    reminders_for_user.remove(ev['id'])
                                    persist_reminders()
                                    st.success(t('reminder_cancelled_success', page_language))
                                else:
                                    reminders_for_user.add(ev['id'])
                                    persist_reminders()
                                    st.success(t('reminder_set_success', page_language))
                                st.rerun()
                    else:
                        st.button(t('event_ongoing', page_language), key=f"sum_on_{ev['id']}", disabled=True, use_container_width=True)

        # Recently Ended Section
        if recently_ended:
            st.markdown("**Recently Ended (last 14 days)**")
            for ev in sorted(recently_ended, key=lambda e: e['end_date'], reverse=True):
                days_ago = (today_ref - ev['end_date']).days
                st.caption(f"{ev['title']} · {ev['city']} — {t('ended_ago_caption', page_language).format(days=format_days(days_ago, page_language))}")

        st.markdown("---")
        st.subheader(t('calendar_header', page_language))

        def update_calendar_view(direction: str):
            base = date(st.session_state.calendar_year, st.session_state.calendar_month, 1)
            new_base = base - timedelta(days=1) if direction == "prev" else base + timedelta(days=32)
            st.session_state.calendar_year = new_base.year
            st.session_state.calendar_month = new_base.month

        nav_l, nav_c, nav_r = st.columns([1,5,1])
        with nav_l:
            if st.button("←", key="cal_prev"):
                update_calendar_view("prev")
                st.rerun()
        with nav_c:
            st.markdown(
                f"<h3 style='text-align:center;'>{calendar.month_name[st.session_state.calendar_month]} {st.session_state.calendar_year}</h3>",
                unsafe_allow_html=True
            )
        with nav_r:
            if st.button("→", key="cal_next"):
                update_calendar_view("next")
                st.rerun()

        cal = calendar.Calendar()
        month_matrix = cal.monthdayscalendar(st.session_state.calendar_year, st.session_state.calendar_month)
        days_header = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        hdr_cols = st.columns(7)
        for i, dw in enumerate(days_header):
            with hdr_cols[i]:
                st.markdown(f"<p style='text-align:center;font-weight:600;'>{dw}</p>", unsafe_allow_html=True)

        today_fixed = today_ref # Align with new calendar baseline (or replace with date.today())
        for week in month_matrix:
            wk_cols = st.columns(7)
            for i, day_val in enumerate(week):
                with wk_cols[i]:
                    if day_val == 0:
                        st.markdown("<div class='calendar-cell empty'></div>", unsafe_allow_html=True)
                        continue
                    current_day = date(st.session_state.calendar_year, st.session_state.calendar_month, day_val)
                    is_today = current_day == today_fixed
                    is_past = current_day < today_fixed

                    classes = ["calendar-cell"]
                    if is_today: classes.append("is-today")
                    if is_past: classes.append("is-past")

                    day_events = [
                        ev for ev in visible_events
                        if ev['start_date'] <= current_day <= ev['end_date']
                    ]
                    day_events = filter_events_by_crafts(
                        day_events,
                        st.session_state['user'].get('preferred_crafts', [])
                    )
                    day_events_sorted = sorted(day_events, key=lambda ev: (ev['start_date'], ev['title']))

                    bars_html = []
                    for ev in day_events_sorted:
                        bar_cls = ["event-bar"]
                        start_flag = current_day == ev['start_date']
                        end_flag = current_day == ev['end_date']
                        if not (start_flag and end_flag):
                            if start_flag:
                                bar_cls.append("event-bar-start")
                            elif end_flag:
                                bar_cls.append("event-bar-end")
                            else:
                                bar_cls.append("event-bar-middle")
                        if start_flag:
                            # Clickable link jumps down to the detailed event section
                            title_html = f"<a href='#event-{ev['id']}'>{ev['title']}</a>"
                        else:
                            title_html = "&nbsp;"
                        bars_html.append(f"<div class='{' '.join(bar_cls)}'>{title_html}</div>")

                    html = f"""
                    <div class="{' '.join(classes)}">
                        <div class="day-number">{day_val}</div>
                        <div class="events-container">{''.join(bars_html)}</div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader(t('events_list_header', page_language))

        # Reuse visible_events (already retention-filtered)
        def event_sort_key(ev):
            if ev['start_date'] <= today_ref <= ev['end_date']:
                return (0, ev['start_date'])
            elif ev['start_date'] > today_ref:
                return (1, ev['start_date'])
            else:
                return (2, -((today_ref - ev['start_date']).days))

        if not visible_events:
            st.info("No events match filters or are within retention window.")
        else:
            for ev in sorted(visible_events, key=event_sort_key):
                list_c1, list_c2 = st.columns([3,1])
                with list_c1:
                    # Anchor target so calendar click scrolls here
                    st.markdown(f"<div id='event-{ev['id']}'></div>", unsafe_allow_html=True)
                    st.markdown(f"#### {ev['title']}")
                    st.markdown(f"**{t('event_dates_label', page_language)}** {ev['start_date'].strftime('%b %d, %Y')} - {ev['end_date'].strftime('%b %d, %Y')}")
                    st.markdown(f"**{t('event_venue_label', page_language)}** {ev.get('venue')}, {ev.get('city')}")
                    display_tags = ev.get('craft_tags', [])
                    if page_language == "Hindi":
                        display_tags = [craft_tag_map_hi.get(tag, tag) for tag in display_tags]
                    st.markdown(f"**{t('event_tags_label', page_language)}** {', '.join(display_tags)}")
                    st.write(ev.get('description',''))

                    ds = days_until(ev['start_date'])
                    de = days_until(ev['end_date'])
                    if ds > 0:
                        st.info(clean_day_artifacts(
                            t('starts_in_caption', page_language).format(days=format_days(ds, page_language))
                        ))
                    elif de < 0:
                        st.warning(clean_day_artifacts(
                            t('ended_ago_caption', page_language).format(days=format_days(abs(de), page_language))
                        ))
                    else:
                        st.success(t('event_ongoing', page_language))

                with list_c2:
                    is_set = ev['id'] in reminders_for_user
                    if ev['end_date'] < today_ref:
                        st.button(t('event_done', page_language), key=f"done_{ev['id']}", disabled=True, use_container_width=True)
                    elif ev['start_date'] <= today_ref <= ev['end_date']:
                        st.button(t('event_ongoing', page_language), key=f"ongoing_{ev['id']}", disabled=True, use_container_width=True)
                    else:
                        with st.form(f"rem_{ev['id']}", clear_on_submit=False):
                            st.markdown("<div style='margin-top:2px'></div>", unsafe_allow_html=True)
                            btn_label = t('cancel_reminder_button', page_language) if is_set else t('set_reminder_button', page_language)
                            submitted = st.form_submit_button(btn_label, use_container_width=True, help="Toggle reminder", kwargs={})
                            # (Streamlit adds no class, we style via value selector in CSS)
                            if submitted:
                                if is_set:
                                    reminders_for_user.remove(ev['id'])
                                    persist_reminders()
                                    st.success(t('reminder_cancelled_success', page_language))
                                else:
                                    reminders_for_user.add(ev['id'])
                                    persist_reminders()
                                    st.success(t('reminder_set_success', page_language))
                                st.rerun()
                st.markdown("---")

    # --- RESULTS DISPLAY ---
    if st.session_state.get('ai_results'):
        st.header(t('results_header', page_language))

        # Check if a NEW image was generated by the AI
        if st.session_state.get('generated_image'):
            # If yes, use a two-column layout to show the new image and the story
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(st.session_state.generated_image, caption=t('ai_image_caption', page_language))
            with col2:
                st.subheader(t('story_header', page_language))
                st.write(st.session_state.ai_results.get('story', ''))
        else:
            # If you used your own uploaded image, just show the story in a single column
            st.subheader(t('story_header', page_language))
            st.write(st.session_state.ai_results.get('story', ''))

        # The social media posts will appear below in either case
        st.subheader(t('social_header', page_language))
        insta, twit, face = st.tabs(["Instagram","Twitter / X","Facebook"])
        with insta:
            ig = st.session_state.ai_results.get("instagram_post",{})
            st.markdown(f"**{t('caption_suggestion', page_language)}**")
            st.markdown(ig.get("caption",""))
            st.markdown(f"**{t('hashtags', page_language)}**")
            st.code(ig.get("hashtags",""))
        with twit:
            tw = st.session_state.ai_results.get("twitter_post",{})
            st.markdown(f"**{t('tweet_suggestion', page_language)}**")
            st.markdown(tw.get("text",""))
        with face:
            fb = st.session_state.ai_results.get("facebook_post",{})
            st.markdown(f"**{t('caption_suggestion', page_language)}**")
            st.markdown(fb.get("caption",""))
            st.markdown(f"**{t('hashtags', page_language)}**")
            st.code(fb.get("hashtags",""))
    elif st.session_state.get('market_trends'):
        st.header(t('trends_results_header', page_language))
        st.markdown(st.session_state.market_trends)
    elif st.session_state.get('growth_plan'):
        st.header(t('planner_results_header', page_language))
        st.markdown(st.session_state.growth_plan)
    elif workflow_key != "events_calendar":
        st.info(t('info_box', page_language))

# --- APPLY BACKGROUND IMAGE GLOBALLY ---
try:
    img = get_image_as_base64("background.jpg") # Make sure the image is in the same folder
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Background image 'background.jpg' not found.")
# --- END GLOBAL STYLES ---

# --- ROUTER ---
if not st.session_state.logged_in:
    show_login_page()
else:
    show_main_app()

# --- REMINDER TOASTS ---
if st.session_state.logged_in:
    page_language = st.query_params.get("lang","English")
    uid = st.session_state['user']['uid']
    user_reminders = set(st.session_state['reminders'].get(uid, []))
    for ev in st.session_state['events']:
        if ev['id'] in user_reminders:
            d_left = days_until(ev['start_date'])
            if 0 <= d_left <= st.session_state.reminder_days:
                st.toast(
                    t('active_reminder_warning', page_language).format(
                        title=ev['title'],
                        days=d_left,
                        date=ev['start_date'].strftime('%b %d'),
                        venue=ev.get('venue'),
                        city=ev.get('city')
                    ),
                    icon="🗓"
                )