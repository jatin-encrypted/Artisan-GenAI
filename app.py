# --- IMPORTS ---
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import json
import re
from datetime import datetime, date, timedelta
import calendar
from typing import List, Dict, Any
import google.auth
from google.oauth2 import service_account
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

import firebase_auth  # Helper module for Firebase (email/password auth, db helpers)

# --- 1. TRANSLATIONS DICTIONARY (UNCHANGED) ---
translations = {
    "English": {
        "app_title": "Artisans AI Studio",
        "app_subheader": "Your all-in-one tool for content creation, image generation, and growth planning.",
        "controls_header": "Controls",
        "page_language_label": "Page Language",
        "page_language_help": "Select the main language for the user interface.",
        "caption_language_label": "Content Language",
        "caption_language_help": "Select the language for the story and all social media captions (Instagram, Facebook, Twitter).",
        "workflow_label": "Choose your creative path:",
        "workflow_option_1": "Generate Marketing Kit",
        "workflow_option_2": "Discover Market Trends",
        "workflow_option_3": "Create a Growth Plan",
        "workflow_option_4": "Events & Calendar",
        "generate_kit_subheader": "Generate a Marketing Kit",
        "image_source_label": "Choose your image source:",
        "source_option_1": "Let AI create an image for you",
        "source_option_2": "Upload your own image",
        "prompt_subheader": "Describe the content you want",
        "prompt_placeholder_title": "e.g., Handmade Terracotta Diya",
        "prompt_placeholder_materials": "e.g., Terracotta clay, natural dyes",
        "prompt_placeholder_region": "e.g., Bishnupur, West Bengal",
        "prompt_placeholder_tone": "e.g., rustic, festive, modern, cultural",
        "prompt_placeholder_description": "e.g., 'A story about a Madhubani artist whose work reflects the spirit of nature.'",
        "generate_button": "Generate Marketing Kit",
        "prompt_warning": "Please enter a Title or Region to generate content.",
        "upload_image_subheader": "Upload your own image",
        "image_uploader_label": "Upload Image",
        "image_uploader_help": "Upload a .png, .jpg, or .jpeg file.",
        "upload_warning": "Please upload an image to generate content.",
        "trends_subheader": "Get Trend Insights",
        "trends_language_label": "Trends Language",
        "trends_label": "Enter your type of craft",
        "trends_placeholder": "e.g., Madhubani Painting, Blue Pottery, Kantha Embroidery",
        "trends_button": "Generate Trends",
        "trends_warning": "Please enter your craft type and a region to get trends.",
        "planner_subheader": "Social Media Growth Planner",
        "plan_language_label": "Plan Language",
        "planner_platform_label": "Choose platforms for your plan",
        "planner_craft_label": "Describe your craft/art",
        "planner_craft_placeholder": "e.g., Handmade blue pottery from Jaipur",
        "planner_audience_label": "Describe your target audience",
        "planner_audience_placeholder": "e.g., Tourists, interior designers, people aged 25-40",
        "planner_button": "Generate Plan",
        "planner_warning": "Please choose at least one platform, describe your craft, and enter a region.",
        "spinner_text_content": "AI is crafting your story and captions in {caption_lang}...",
        "spinner_text_image": "Generating a unique image... 🖼",
        "spinner_text_trends": "Analyzing market trends in {trends_lang}...",
        "spinner_text_planner": "Building your custom growth plan in {plan_lang}...",
        "results_header": "Your Generated Marketing Kit",
        "content_ready": "Your content is ready! 🎉",
        "ai_image_caption": "AI-Generated Image",
        "user_image_caption": "Uploaded Image",
        "story_header": "📜 The Story",
        "social_header": "📱 Social Media Posts",
        "caption_suggestion": "Caption Suggestion:",
        "hashtags": "Hashtags:",
        "tweet_suggestion": "Tweet Suggestion:",
        "trends_results_header": "📈 Market Trend Insights",
        "trends_ready": "Your trend report is ready!",
        "planner_results_header": "🚀 Your Social Media Growth Plan",
        "planner_ready": "Your growth plan is ready!",
        "info_box": "Choose a creative path in the homepage, provide your input, and click the generate button. Use the sidebar to switch paths anytime.",
        "clear_button": "Clear Results",
        "other_option": "Other (please specify)",
        "other_specify": "Please specify:",
        "choose_path_header": "Choose your creative path:",
        "path_option_1": "Generate Marketing Kit",
        "path_option_2": "Discover Market Trends",
        "path_option_3": "Create a Growth Plan",
        "path_option_4": "Events & Calendar",
        "start_prompt": "Select a path to get started",
        "landing_info": "You can change this path anytime from the sidebar.",
        "back_to_home": "Back to Home",
        "desc_heading": "Description (Optional)",
        "events_header": "📅 Artisans Events & Notifications",
        "event_preferences_header": "Event Preferences",
        "event_preferences_info": "Choose crafts you are interested in — notifications will match these tags.",
        "select_crafts_label": "Select crafts",
        "notify_days_label": "Notify me about events up to (days ahead)",
        "upcoming_events_info": "You have {count} upcoming event(s) matching your selected crafts (next {days} days):",
        "no_upcoming_events": "No matching events in the next {days} days.",
        "event_when": "in {days} day(s)",
        "event_when_ago": "{days} day(s) ago",
        "event_venue_label": "Venue:",
        "set_reminder_button": "Set reminder for {event_id}",
        "cancel_reminder_button": "Cancel reminder for {event_id}",
        "reminder_set_success": "Reminder set. (This is a simulation and will not send a real notification).",
        "reminder_cancelled_success": "Reminder cancelled.",
        "calendar_header": "Calendar",
        "events_list_header": "Events List & Details",
        "event_dates_label": "Dates:",
        "event_tags_label": "Tags:",
        "starts_in_caption": "Starts in {days} day(s)",
        "started_ago_caption": "Event started {days} day(s) ago",
        "active_reminder_warning": "Reminder: '{title}' starts in {days} day(s) on {date}. Venue: {venue} — {city}",
        "no_active_reminders": "No active reminders within your reminder window.",
        "event_concluded": "Event Concluded",
        "calendar_year_label": "Year",
        "calendar_month_label": "Month",
    },
    "Hindi": {
        "app_title": "कलाकार एआई स्टूडियो",
        "app_subheader": "कंटेंट निर्माण, छवि निर्माण और विकास योजना के लिए आपका ऑल-इन-वन टूल।",
        # (Abbreviated for brevity)
        "workflow_option_1": "मार्केटिंग किट बनाएं",
        "workflow_option_2": "बाजार के रुझान खोजें",
        "workflow_option_3": "विकास योजना बनाएं",
        "workflow_option_4": "कार्यक्रम और कैलेंडर",
        "other_option": "अन्य (कृपया निर्दिष्ट करें)",
        "other_specify": "कृपया निर्दिष्ट करें:",
        "clear_button": "परिणाम साफ़ करें",
        "generate_button": "मार्केटिंग किट बनाएं",
        "events_header": "📅 कारीगर कार्यक्रम और सूचनाएं",
        "event_preferences_header": "कार्यक्रम प्राथमिकताएं",
        "event_preferences_info": "उन शिल्पों को चुनें जिनमें आपकी रुचि है - सूचनाएं इन टैग से मेल खाएंगी।",
        "select_crafts_label": "शिल्प चुनें",
        "notify_days_label": "मुझे आने वाले कार्यक्रमों के बारे में सूचित करें (दिन पहले)",
        "upcoming_events_info": "आपके चयनित शिल्पों से मेल खाने वाले {count} आगामी कार्यक्रम हैं (अगले {days} दिनों में):",
        "no_upcoming_events": "अगले {days} दिनों में कोई मेल खाने वाला कार्यक्रम नहीं है।",
        "event_when": "{days} दिन में",
        "event_when_ago": "{days} दिन पहले",
        "set_reminder_button": "{event_id} के लिए रिमाइंडर सेट करें",
        "cancel_reminder_button": "{event_id} के लिए रिमाइंडर रद्द करें",
        "reminder_set_success": "रिमाइंडर सेट हो गया।",
        "reminder_cancelled_success": "रिमाइंडर रद्द किया गया।",
        "calendar_header": "कैलेंडर",
        "events_list_header": "कार्यक्रम सूची और विवरण",
        "event_dates_label": "तिथियां:",
        "event_tags_label": "टैग:",
        "starts_in_caption": "{days} दिन में शुरू होगा",
        "started_ago_caption": "कार्यक्रम {days} दिन पहले शुरू हुआ",
        "active_reminder_warning": "रिमाइंडर: '{title}' {days} दिन में {date} को शुरू होगा। स्थान: {venue} — {city}",
    }
}

# --- 2. CACHED HELPERS ---
@st.cache_data
def t(key, lang="English"):
    return translations.get(lang, translations["English"]).get(key, key)

@st.cache_resource
def get_gemini_model():
    return genai.GenerativeModel('gemini-1.5-pro-latest')

@st.cache_resource
def get_imagen_model():
    return ImageGenerationModel.from_pretrained("imagegeneration@006")

@st.cache_data
def load_dummy_events() -> List[Dict[str, Any]]:
    today = date(2025, 9, 12)
    return [
        {"id": "ev-001", "title": "Handmade Bazaar - Jaipur", "craft_tags": ["Terracotta clay","Ceramics","Pottery"], "start_date": today + timedelta(days=6), "end_date": today + timedelta(days=8), "venue": "Amber Grounds", "city": "Jaipur, Rajasthan", "description": "A curated fair for pottery and terracotta artisans from Rajasthan."},
        {"id": "ev-002", "title": "Banarasi Silks Expo", "craft_tags": ["Fabric","Silk","Weaving"], "start_date": today + timedelta(days=15), "end_date": today + timedelta(days=16), "venue": "Vishwanath Conference Hall", "city": "Varanasi, Uttar Pradesh", "description": "Silk weavers showcase and buyer connect event."},
        {"id": "ev-diwali", "title": "Diwali Crafts Mela", "craft_tags": ["All","Festive","Pottery","Fabric"], "start_date": date(2025,10,25), "end_date": date(2025,10,30), "venue": "Dilli Haat INA", "city": "New Delhi", "description": "The biggest festive market for artisans."},
    ]

def filter_events_by_crafts(events: List[Dict[str, Any]], crafts: List[str]) -> List[Dict[str, Any]]:
    if not crafts: return events
    out = []
    for ev in events:
        tags = [x.lower() for x in ev.get('craft_tags', [])]
        for c in crafts:
            if c.lower() in tags or 'all' in tags:
                out.append(ev); break
    return out

def upcoming_events(events: List[Dict[str, Any]], days_ahead: int = 14) -> List[Dict[str, Any]]:
    today = date(2025, 9, 12)
    horizon = today + timedelta(days=days_ahead)
    return [e for e in events if e['start_date'] <= horizon and e['end_date'] >= today]

def days_until(d: date) -> int:
    today = date(2025, 9, 12)
    return (d - today).days

def clear_results():
    st.session_state.ai_results = None
    st.session_state.generated_image = None
    st.session_state.uploaded_image = None
    st.session_state.market_trends = None
    st.session_state.growth_plan = None
    st.session_state.story_is_ready = False
    st.session_state.current_prompt_fields = {}

# --- 3. PAGE CONFIG & THEME ---
initial_lang = st.query_params.get("lang", "English")
st.set_page_config(page_title=t("app_title", initial_lang), page_icon="🏺", layout="wide")

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
pottery_theme_css = """
<style>
    :root {
        --font: 'serif';
        --background-color: #FDF5E6;
        --sidebar-background: #EADDC5;
        --primary-text-color: #5D4037;
        --accent-color: #d46c04;
        --accent-hover-color: #d77c02;
        --widget-background: #FFFFFF;
        --border-color: #D7CCC8;
        --border-radius: 12px;
        --shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        --background-image-url: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+IDxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiNGREY1RTYiLz4gPGcgb3BhY2l0eT0iMC4xIiBmaWxsPSJub25lIiBzdHJva2U9IiM1RDQwMzciIHN0cm9rZS13aWR0aD0iMSI+IDxwYXRoIGQ9Ik0gMjAgMjAgQyAyNSAyNSwgMzAgNDAsIDI1IDUwIFMyMCA3NSwgMzAgODAgIi8+IDxwYXRoIGQ9Ik0gODAgMjAgQyA3NSA0MCwgNzAgNDAsIDc1IDUwIFM4MCA3NSwgNzAgODAgIi8+IDxwYXRoIGQ9Ik0gNTAgMTUgQyA1NSAzMCwgNDUgMzAsIDUwIDQ1IFM1NSA3NSwgNTAgODUgIi8+IDxwYXRoIGQ9Ik0gNSAxMCBMIDUgOTAgIi8+IDxwYXRoIGQ9Ik0gOTUgMTAgTCA5NSA5MCAiLz4gPC9nPjwvc3ZnPg==");
    }
    .stApp { background-color: var(--background-color); background-image: var(--background-image-url); background-attachment: fixed; color: var(--primary-text-color); }
    h1, h2, h3, h4, h5, h6, .stMarkdown, label, p, .stAlert, [data-baseweb="tab"] { color: var(--primary-text-color) !important; font-family: var(--font); }
    p, li, div, label, .stMarkdown { font-size: 1.1rem; }
    [data-testid="stSidebar"] { background-color: var(--sidebar-background); border-right: 1px solid var(--border-color); }
    [data-testid="stHeader"] { background-color: rgba(253, 245, 230, 0.8); backdrop-filter: blur(10px); box-shadow: none; border-bottom: 1px solid var(--border-color); }
    .stSelectbox, .stTextInput, .stTextArea, .stFileUploader, .stMultiSelect { border-radius: var(--border-radius); }
    .stSelectbox > div > div, .stTextInput > div > div, .stTextArea > div > div, .stFileUploader > div > div { background-color: var(--widget-background); border: 1px solid var(--border-color); border-radius: var(--border-radius); box-shadow: var(--shadow); color: var(--primary-text-color); }
    .stSelectbox div[role="listbox"] { background-color: var(--widget-background); border-radius: var(--border-radius); border: 1px solid var(--border-color); }
    .stButton > button { background-color: var(--accent-color); color: white; border: none; padding: 12px 28px; font-size: 16px; font-weight: bold; border-radius: var(--border-radius); box-shadow: var(--shadow); transition: background-color 0.2s ease-in-out, transform 0.1s ease-in-out; }
    .stButton > button:hover { background-color: var(--accent-hover-color); transform: scale(1.02); }
    .stButton > button:active { transform: scale(0.98); }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: var(--border-radius) var(--border-radius) 0 0; border-bottom: 2px solid var(--border-color); padding: 10px 16px; }
    .stTabs [aria-selected="true"] { background-color: var(--widget-background); border-bottom: 2px solid var(--accent-color); box-shadow: var(--shadow); }
    .stCodeBlock, .st-emotion-cache-1f2d20p { background-color: #F5F0E8; color: var(--primary-text-color); border-left: 5px solid var(--accent-color); border-radius: var(--border-radius); padding: 1rem; font-size: 1rem !important; }
    .stAlert { border-radius: var(--border-radius); box-shadow: var(--shadow); }
    .stAlert.success { background-color: #E8F5E9; border-left: 8px solid #4CAF50; }
    .stAlert.warning { background-color: #FFFDE7; border-left: 8px solid #FFC107; }
    .stAlert.info { background-color: #E1F5FE; border-left: 8px solid #03A9F4; }
    
    /* Calendar-specific CSS */
    /* Basic styling for smooth scrolling */
    html { scroll-behavior: smooth; }

    /* Header for Days of the Week */
    .day-header { font-weight: 600; text-align: center; margin-bottom: 10px; color: #888; }

    /* Individual Day Cell */
    .calendar-day { min-height: 140px; border: 1px solid #ddd; border-radius: 8px; padding: 8px; display: flex; flex-direction: column; background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }

    /* Highlight for Today's Date */
    .calendar-day.today { border: 2px solid #007bff; background-color: #e7f3ff; }

    /* The number in the top-right of the cell */
    .day-number { text-align: right; font-size: 14px; font-weight: 600; margin-bottom: 5px; }

    /* Separator line between date and events */
    .day-separator { border: none; height: 1px; background-color: #eee; margin: 0 0 5px 0; }

    /* Container for events below the date */
    .events-container { 
        flex-grow: 1; 
        overflow: hidden; /* Hide overflowing events */
        position: relative;
    }

    /* Add a subtle fade-out effect if there are more events than can be shown */
    .events-container.has-more::after {
        content: '...';
        position: absolute;
        bottom: 0;
        right: 5px;
        font-size: 14px;
        font-weight: bold;
        color: #8B4513;
    }

    /* Base styling for each event tag */
    .calendar-event { 
        font-size: 11px; 
        background-color: #8B4513; 
        color: white; 
        padding: 3px 6px; 
        border-radius: 5px;  
        margin-bottom: 3px; 
        overflow: hidden; 
        text-overflow: ellipsis; 
        white-space: nowrap; 
        cursor: pointer; 
    }

    /* Styling for continuous event blocks */
    .calendar-event.event-start { border-top-right-radius: 0; border-bottom-right-radius: 0; }
    .calendar-event.event-middle { border-radius: 0; }
    .calendar-event.event-end { border-top-left-radius: 0; border-bottom-left-radius: 0; }
    .calendar-event:not(.event-start):not(.event-middle):not(.event-end) { border-radius: 5px; }

    /* Remove underline from links */
    a { text-decoration: none; }

    /* Center align the month header text */
    .month-header { text-align: center; }
</style>
"""
st.markdown(pottery_theme_css, unsafe_allow_html=True)

st.markdown("""
<style>
    .calendar-cell{min-height:110px;padding:8px;border-radius:10px;background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.06);position:relative}
    .day-number{position:absolute;top:6px;right:6px;background:#d46c04;color:#fff;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700}
    .calendar-event-container{margin-top:32px;padding:6px;border-radius:6px;background:rgba(212,108,4,0.08)}
    .calendar-event-container.concluded{text-decoration:line-through;opacity:.55}
</style>
""", unsafe_allow_html=True)

# --- 4. AI & AUTHENTICATION CONFIG ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)

    _project_id = None
    _credentials = None
    if 'GCP_SERVICE_ACCOUNT_JSON' in st.secrets:
        info = json.loads(st.secrets['GCP_SERVICE_ACCOUNT_JSON'])
        _credentials = service_account.Credentials.from_service_account_info(info)
        _project_id = _credentials.project_id
    else:
        _credentials, _project_id = google.auth.default()

    if not _project_id:
        st.error("GCP Project ID missing.")
        st.stop()

    vertexai.init(project=_project_id, credentials=_credentials, location="us-central1")

    # Firebase init (from helper)
    firebase_app = firebase_auth.init_firebase()
    auth_handler = firebase_app.auth()
    db_handler = firebase_app.database()

except Exception as e:
    st.error(f"Authentication or Configuration Error: {e}")
    st.stop()

# --- 5. AI HELPER FUNCTIONS ---
def generate_image_with_imagen(prompt: str):
    try:
        model = get_imagen_model()
        resp = model.generate_images(prompt=prompt, number_of_images=1, aspect_ratio="1:1")
        if resp.images:
            return Image.open(io.BytesIO(resp.images[0]._image_bytes))
        st.error("No image returned.")
    except Exception as e:
        st.error(f"Imagen error: {e}")
    return None

def get_ai_content(prompt_fields, caption_language):
    model = get_gemini_model()
    text_prompt = f"""
Generate a story and social media content for:
Title: {prompt_fields.get('title','')}
Materials: {prompt_fields.get('materials','')}
Region: {prompt_fields.get('region','')}
Tone: {prompt_fields.get('tone','')}
Description: {prompt_fields.get('description','')}

All output must be valid JSON and in {caption_language}.
Schema:
{{
"story":"...",
"instagram_post":{{"caption":"...","hashtags":"..."}},
"twitter_post":{{"text":"..."}},
"facebook_post":{{"caption":"...","hashtags":"..."}}
}}
"""
    try:
        r = model.generate_content(text_prompt, request_options={"timeout":600})
        m = re.search(r'\{.*\}', r.text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        st.error("No JSON found.")
    except Exception as e:
        st.error(f"Content generation error: {e}")
    return None

def get_ai_content_from_image(uploaded_image, caption_language, description):
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    prompt = f"""
Analyze the craft image and produce JSON marketing kit in {caption_language}.
Description: {description}
Schema:
{{
"story":"...",
"instagram_post":{{"caption":"...","hashtags":"..."}},
"twitter_post":{{"text":"..."}},
"facebook_post":{{"caption":"...","hashtags":"..."}}
}}
"""
    try:
        img = Image.open(io.BytesIO(uploaded_image.getvalue()))
        r = model.generate_content([prompt, img], request_options={"timeout":600})
        m = re.search(r'\{.*\}', r.text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        st.error("No JSON found in response.")
    except Exception as e:
        st.error(f"Image content error: {e}")
    return None

def get_market_trends(region, language, craft_type):
    model = get_gemini_model()
    prompt = f"""
Provide a detailed actionable market trend report (Markdown) in {language} for {craft_type} from {region}.
Sections:
- 📈 Trending Themes & Concepts
- 🎨 Popular Materials & Color Palettes
- 💲 Current Market Price Analysis (table with columns: Online Retail Price Range (INR), Offline/Wholesale Price Range (INR))
- 💡 Actionable Pricing & Marketing Strategies
Do not mention current date.
"""
    try:
        return model.generate_content(prompt, request_options={"timeout":600}).text
    except Exception as e:
        st.error(f"Trend gen error: {e}")
        return None

def get_growth_plan(region, language, platforms, craft_type, target_audience):
    model = get_gemini_model()
    prompt = f"""
Create a social media growth plan in {language} for {craft_type} from {region} targeting {target_audience}.
For each platform ({', '.join(platforms)}):
- Optimal Posting Times (IST)
- Posting Frequency
- Content Mix Strategy (% breakdown)
- One creative sample post idea
End with encouragement.
Markdown output only.
"""
    try:
        return model.generate_content(prompt, request_options={"timeout":600}).text
    except Exception as e:
        st.error(f"Growth plan error: {e}")
        return None

# --- 6. SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = None
if 'user' not in st.session_state:
    st.session_state['user'] = {'uid': 'guest', 'email': 'guest@example.com', 'preferred_crafts': []}
if 'events' not in st.session_state: st.session_state['events'] = load_dummy_events()
if 'reminders' not in st.session_state: st.session_state['reminders'] = {}  # dict: uid -> [event_ids]
if 'ai_results' not in st.session_state: st.session_state.ai_results = None
if 'generated_image' not in st.session_state: st.session_state.generated_image = None
if 'uploaded_image' not in st.session_state: st.session_state.uploaded_image = None
if 'market_trends' not in st.session_state: st.session_state.market_trends = None
if 'growth_plan' not in st.session_state: st.session_state.growth_plan = None
if 'story_is_ready' not in st.session_state: st.session_state.story_is_ready = False
if 'current_prompt_fields' not in st.session_state: st.session_state.current_prompt_fields = {}
if 'selected_workflow' not in st.session_state: st.session_state.selected_workflow = None
if 'calendar_year' not in st.session_state: st.session_state.calendar_year = date(2025,9,12).year
if 'calendar_month' not in st.session_state: st.session_state.calendar_month = date(2025,9,12).month
if 'reminder_days' not in st.session_state: st.session_state.reminder_days = 14

# --- 7. LOGIN / REGISTER PAGE ---
def show_login_page():
    st.title(f"🏺 {t('app_title','English')}")
    st.markdown("Please log in or register to continue.")
    login_tab, register_tab = st.tabs(["Login","Register"])
    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                user, err = firebase_auth.login(auth_handler, email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_info = user
                    data = firebase_auth.load_user_data(db_handler, user['localId'])
                    st.session_state['user'] = {
                        'uid': user['localId'],
                        'email': user['email'],
                        'preferred_crafts': data.get('preferred_crafts', [])
                    }
                    st.session_state['reminders'] = { user['localId']: data.get('reminders', []) }
                    st.rerun()
                else:
                    st.error(f"Login failed: {err}")
    with register_tab:
        with st.form("register_form"):
            new_email = st.text_input("Email", key="reg_email")
            new_pass = st.text_input("Password", type="password", key="reg_pass")
            confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
            reg_submit = st.form_submit_button("Register")
            if reg_submit:
                if new_pass == confirm:
                    user, err = firebase_auth.sign_up(auth_handler, new_email, new_pass)
                    if user:
                        st.success("Registration successful! Please log in.")
                    else:
                        st.error(f"Registration failed: {err}")
                else:
                    st.error("Passwords do not match.")

# --- 8. MAIN APP UI ---
def show_main_app():
    page_language = st.query_params.get("lang","English")
    st.title(f"🏺 {t('app_title', page_language)}")
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

        workflow_options = [
            t('workflow_option_1', page_language),
            t('workflow_option_2', page_language),
            t('workflow_option_3', page_language),
            t('workflow_option_4', page_language)
        ]
        def on_sidebar_workflow_change():
            st.session_state.selected_workflow = st.session_state.sidebar_workflow
        sidebar_index = 0
        if st.session_state.selected_workflow in workflow_options:
            try:
                sidebar_index = workflow_options.index(st.session_state.selected_workflow)
            except Exception:
                sidebar_index = 0
        st.radio(
            t('workflow_label', page_language),
            workflow_options,
            index=sidebar_index,
            key='sidebar_workflow',
            on_change=on_sidebar_workflow_change
        )
        st.markdown("---")
        if st.button(t('clear_button', page_language), on_click=clear_results, use_container_width=True):
            st.rerun()

        st.markdown("---")
        st.header(t('event_preferences_header', page_language))
        st.markdown(t('event_preferences_info', page_language))

        all_tags = sorted({tag for ev in st.session_state['events'] for tag in ev['craft_tags']})
        uid = st.session_state['user']['uid']

        selected_crafts = st.multiselect(
            t('select_crafts_label', page_language),
            all_tags,
            default=st.session_state['user'].get('preferred_crafts', [])
        )
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

    if not st.session_state.selected_workflow:
        st.markdown("### " + t('choose_path_header', page_language))
        st.info(t('landing_info', page_language))
        c1, c2 = st.columns(2)
        with c1:
            if st.button(t('path_option_1', page_language), use_container_width=True):
                st.session_state.selected_workflow = t('workflow_option_1', page_language); st.rerun()
            if st.button(t('path_option_3', page_language), use_container_width=True):
                st.session_state.selected_workflow = t('workflow_option_3', page_language); st.rerun()
        with c2:
            if st.button(t('path_option_2', page_language), use_container_width=True):
                st.session_state.selected_workflow = t('workflow_option_2', page_language); st.rerun()
            if st.button(t('path_option_4', page_language), use_container_width=True):
                st.session_state.selected_workflow = t('workflow_option_4', page_language); st.rerun()
        st.markdown("---")
        st.info(t('info_box', page_language))
        return

    workflow = st.session_state.selected_workflow

    EXTENDED_REGION_OPTIONS = [
        "Jaipur, Rajasthan","Kutch, Gujarat","Madhubani, Bihar","Bishnupur, West Bengal",
        "Varanasi, Uttar Pradesh","New Delhi / Delhi","Mumbai, Maharashtra","Kolkata, West Bengal",
        "Chennai, Tamil Nadu","Bengaluru, Karnataka","Hyderabad, Telangana","Pune, Maharashtra",
        "Ahmedabad, Gujarat","Surat, Gujarat","Lucknow, Uttar Pradesh","Srinagar, Jammu & Kashmir",
        t('other_option', page_language)
    ]

    # WORKFLOW 1
    if workflow == t('workflow_option_1', page_language):
        caption_language = st.sidebar.selectbox(
            t('caption_language_label', page_language),
            ["English","Hindi","Hinglish","Bengali","Tamil","Gujarati","Marathi"],
            help=t('caption_language_help', page_language)
        )
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
            prompt_fields['title'] = st.text_input("Title", placeholder=t('prompt_placeholder_title', page_language), key='ai_title')
            material_options = ["Terracotta clay","Brass","Wood","Ceramics","Stone","Leather","Glass","Paper","Bamboo", t('other_option', page_language)]
            selected_material = st.selectbox("Materials", material_options, key='ai_materials')
            if selected_material == t('other_option', page_language):
                prompt_fields['materials'] = st.text_input(t('other_specify', page_language), placeholder=t('prompt_placeholder_materials', page_language), key='ai_materials_other')
            else:
                prompt_fields['materials'] = selected_material
            selected_region = st.selectbox("Region", EXTENDED_REGION_OPTIONS, key='ai_region')
            if selected_region == t('other_option', page_language):
                prompt_fields['region'] = st.text_input(t('other_specify', page_language), placeholder=t('prompt_placeholder_region', page_language), key='ai_region_other')
            else:
                prompt_fields['region'] = selected_region
            prompt_fields['tone'] = st.selectbox("Tone", ["rustic","festive","modern","cultural","elegant","minimalist", t('other_option', page_language)], key='ai_tone')
            if prompt_fields['tone'] == t('other_option', page_language):
                prompt_fields['tone'] = st.text_input(t('other_specify', page_language), placeholder=t('prompt_placeholder_tone', page_language), key='ai_tone_other')
        else:
            st.markdown("#### " + t('upload_image_subheader', page_language))
            uploaded_file = st.file_uploader(t('image_uploader_label', page_language), type=["png","jpg","jpeg"], help=t('image_uploader_help', page_language))
            if uploaded_file:
                st.session_state.uploaded_image = uploaded_file
                st.image(uploaded_file, caption=t('user_image_caption', page_language), use_container_width=True)
            else:
                st.session_state.uploaded_image = None
                st.info("Upload an image to get started.")
        st.text_area(t('desc_heading', page_language), key='common_description_area', placeholder=t('prompt_placeholder_description', page_language))

        if st.button(t('generate_button', page_language), use_container_width=True, type="primary"):
            clear_results()
            if source_choice == t('source_option_1', page_language):
                if st.session_state.get('ai_title') or st.session_state.get('ai_region'):
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
            else:
                if st.session_state.get('uploaded_image'):
                    with st.spinner(t('spinner_text_content', page_language).format(caption_lang=caption_language)):
                        st.session_state.ai_results = get_ai_content_from_image(
                            st.session_state.uploaded_image,
                            caption_language,
                            st.session_state.get('common_description_area','')
                        )
                    if st.session_state.ai_results:
                        st.success(t('content_ready', page_language))
                else:
                    st.warning(t('upload_warning', page_language))

    # WORKFLOW 2
    elif workflow == t('workflow_option_2', page_language):
        st.subheader(t('trends_subheader', page_language))
        content_language_list = ["English","Hindi","Hinglish","Bengali","Tamil","Gujarati","Marathi"]
        trends_language = st.selectbox(t('trends_language_label', page_language), content_language_list, key='trends_lang')
        trends_region = st.text_input("Region", placeholder=t('prompt_placeholder_region', page_language), key='trends_region')
        craft_type = st.text_input(t('trends_label', page_language), placeholder=t('trends_placeholder', page_language))
        if st.button(t('trends_button', page_language), use_container_width=True):
            if craft_type and trends_region:
                clear_results()
                with st.spinner(t('spinner_text_trends', page_language).format(trends_lang=trends_language)):
                    st.session_state.market_trends = get_market_trends(trends_region, trends_language, craft_type)
            else:
                st.warning(t('trends_warning', page_language))

    # WORKFLOW 3
    elif workflow == t('workflow_option_3', page_language):
        st.subheader(t('planner_subheader', page_language))
        content_language_list = ["English","Hindi","Hinglish","Bengali","Tamil","Gujarati","Marathi"]
        plan_language = st.selectbox(t('plan_language_label', page_language), content_language_list, key='plan_lang')
        planner_region = st.text_input("Region", placeholder=t('prompt_placeholder_region', page_language), key='planner_region')
        platforms = st.multiselect(t('planner_platform_label', page_language), ["Instagram","Facebook","X"])
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
    elif workflow == t('workflow_option_4', page_language):
        st.subheader(t('events_header', page_language))

        filtered_upcoming = upcoming_events(
            filter_events_by_crafts(st.session_state['events'], st.session_state['user'].get('preferred_crafts', [])),
            days_ahead=st.session_state.reminder_days
        )
        reminders_for_user = st.session_state['reminders'].get(uid, [])
        active_reminders = [ev for ev in filtered_upcoming if ev['id'] in reminders_for_user]

        if active_reminders:
            st.markdown(f"**{t('upcoming_events_info', page_language).format(count=len(active_reminders), days=st.session_state.reminder_days)}**")
            for ev in active_reminders:
                d_left = days_until(ev['start_date'])
                if d_left > 0:
                    st.info(f"**{ev['title']}** - {t('event_when', page_language).format(days=d_left)}")
                elif d_left == 0:
                    st.info(f"**{ev['title']}** - ✨ Starting Today!")
                else:
                    st.success(f"**{ev['title']}** - {t('event_when_ago', page_language).format(days=abs(d_left))}")
        else:
            st.info(t('no_upcoming_events', page_language).format(days=st.session_state.reminder_days))

        st.markdown("---")
        st.subheader(t('calendar_header', page_language))

        def update_calendar(direction):
            base = date(st.session_state.calendar_year, st.session_state.calendar_month, 1)
            new_date = base - timedelta(days=1) if direction == "prev" else base + timedelta(days=32)
            st.session_state.calendar_year = new_date.year
            st.session_state.calendar_month = new_date.month

        c1,c2,c3 = st.columns([1,5,1])
        with c1:
            if st.button("←"): update_calendar("prev"); st.rerun()
        with c2:
            st.markdown(f"<h3 style='text-align:center;'>{calendar.month_name[st.session_state.calendar_month]} {st.session_state.calendar_year}</h3>", unsafe_allow_html=True)
        with c3:
            if st.button("→"): update_calendar("next"); st.rerun()

        cal = calendar.Calendar()
        month_days = cal.monthdayscalendar(st.session_state.calendar_year, st.session_state.calendar_month)
        days_of_week = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        cols = st.columns(7)
        for i,dw in enumerate(days_of_week):
            with cols[i]:
                st.markdown(f"<p style='text-align:center;'><b>{dw}</b></p>", unsafe_allow_html=True)

        for week in month_days:
            cols = st.columns(7)
            for i,day in enumerate(week):
                with cols[i]:
                    if day == 0: continue
                    current_date = date(st.session_state.calendar_year, st.session_state.calendar_month, day)
                    st.markdown(f"<div class='calendar-cell'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='day-number'>{day}</div>", unsafe_allow_html=True)
                    day_events = [ev for ev in st.session_state['events'] if ev['start_date'] <= current_date <= ev['end_date']]
                    day_events = filter_events_by_crafts(day_events, st.session_state['user'].get('preferred_crafts', []))
                    for ev in day_events:
                        concluded = days_until(ev['end_date']) < 0
                        cls = "calendar-event-container concluded" if concluded else "calendar-event-container"
                        st.markdown(f"<div class='{cls}'>**{ev['title']}**<br><small>{ev['city']}</small></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader(t('events_list_header', page_language))

        filtered_events = filter_events_by_crafts(st.session_state['events'], st.session_state['user'].get('preferred_crafts', []))
        if not filtered_events:
            st.info("No events found for your selected crafts.")
        for ev in sorted(filtered_events, key=lambda e: e['start_date']):
            col1, col2 = st.columns([3,1])
            with col1:
                st.markdown(f"#### {ev['title']}")
                st.markdown(f"**{t('event_dates_label', page_language)}** {ev['start_date'].strftime('%b %d, %Y')} - {ev['end_date'].strftime('%b %d, %Y')}")
                st.markdown(f"**{t('event_venue_label', page_language)}** {ev.get('venue')}, {ev.get('city')}")
                st.markdown(f"**{t('event_tags_label', page_language)}** {', '.join(ev.get('craft_tags', []))}")
                st.write(ev.get('description',''))
                d_left = days_until(ev['start_date'])
                if d_left > 0:
                    st.info(t('starts_in_caption', page_language).format(days=d_left))
                elif d_left < 0:
                    st.warning(t('started_ago_caption', page_language).format(days=abs(d_left)))
            with col2:
                reminders_for_user = st.session_state['reminders'].setdefault(uid, [])
                is_set = ev['id'] in reminders_for_user

                def persist():
                    firebase_auth.save_user_data(
                        db_handler,
                        uid,
                        {
                            'preferred_crafts': st.session_state['user']['preferred_crafts'],
                            'reminders': st.session_state['reminders'][uid]
                        }
                    )

                if is_set:
                    if st.button(t('cancel_reminder_button', page_language).format(event_id=ev['id']), key=f"cancel_{ev['id']}", use_container_width=True):
                        reminders_for_user.remove(ev['id'])
                        persist()
                        st.success(t('reminder_cancelled_success', page_language))
                        st.rerun()
                else:
                    if st.button(t('set_reminder_button', page_language).format(event_id=ev['id']), key=f"set_{ev['id']}", use_container_width=True):
                        reminders_for_user.append(ev['id'])
                        persist()
                        st.success(t('reminder_set_success', page_language))
                        st.rerun()
            st.markdown("---")

    # RESULTS
    if st.session_state.get('ai_results'):
        st.markdown("---")
        st.header(t('results_header', page_language))
        c1, c2 = st.columns([1,2])
        with c1:
            if st.session_state.generated_image:
                st.image(st.session_state.generated_image, caption=t('ai_image_caption', page_language), use_container_width=True)
            elif st.session_state.uploaded_image:
                st.image(st.session_state.uploaded_image, caption=t('user_image_caption', page_language), use_container_width=True)
        with c2:
            st.subheader(t('story_header', page_language))
            st.write(st.session_state.ai_results.get("story",""))
        st.subheader(t('social_header', page_language))
        insta, twit, face = st.tabs(["Instagram","Twitter / X","Facebook"])
        with insta:
            ig = st.session_state.ai_results.get("instagram_post",{})
            st.markdown(t('caption_suggestion', page_language))
            st.markdown(ig.get("caption",""))
            st.markdown(t('hashtags', page_language))
            st.code(ig.get("hashtags",""))
        with twit:
            tw = st.session_state.ai_results.get("twitter_post",{})
            st.markdown(t('tweet_suggestion', page_language))
            st.markdown(tw.get("text",""))
        with face:
            fb = st.session_state.ai_results.get("facebook_post",{})
            st.markdown(t('caption_suggestion', page_language))
            st.markdown(fb.get("caption",""))
            st.markdown(t('hashtags', page_language))
            st.code(fb.get("hashtags",""))
    elif st.session_state.get('market_trends'):
        st.header(t('trends_results_header', page_language))
        st.markdown(st.session_state.market_trends)
    elif st.session_state.get('growth_plan'):
        st.header(t('planner_results_header', page_language))
        st.markdown(st.session_state.growth_plan)
    elif workflow != t('workflow_option_4', page_language):
        st.info(t('info_box', page_language))

# --- 9. ROUTER ---
if not st.session_state.logged_in:
    show_login_page()
else:
    show_main_app()

# --- 10. REMINDER TOASTS ---
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
