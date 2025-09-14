# backend.py

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

import firebase_auth # Helper module for Firebase (email/password auth, db helpers)
import base64

# --- TRANSLATIONS & CONFIG ---
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
        "planner_platform_placeholder": "Choose platforms",
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
        # Calendar Translations
        "events_header": "📅 Artisans Events & Notifications",
        "event_preferences_header": "Event Preferences",
        "event_preferences_info": "Choose crafts you are interested in — notifications will match these tags.",
        "select_crafts_label": "Select crafts",
        "notify_days_label": "Notify me about events up to (days ahead)",
        "upcoming_events_info": "You have {count} upcoming event(s) matching your selected crafts (next {days} days):",
        "no_upcoming_events": "No matching events in the next {days} days.",
        "event_when": "in {days}",
        "event_when_ago": "{days} ago",
        "event_venue_label": "Venue:",
        "set_reminder_button": "Set Reminder",
        "cancel_reminder_button": "Cancel Reminder",
        "reminder_set_success": "Reminder set. (This is a simulation and will not send a real notification).",
        "reminder_cancelled_success": "Reminder cancelled.",
        "calendar_header": "Calendar",
        "events_list_header": "Events List & Details",
        "event_dates_label": "Dates:",
        "event_tags_label": "Tags:",
        "starts_in_caption": "Starts in {days}",
        "started_ago_caption": "Event started {days} ago",
        "ended_ago_caption": "Event ended {days} ago",
        "active_reminder_warning": "Reminder: '{title}' starts in {days} on {date}. Venue: {venue} — {city}",
        "no_active_reminders": "No active reminders within your reminder window.",
        "event_concluded": "Event Concluded",
        "calendar_year_label": "Year",
        "calendar_month_label": "Month",
        # Field Labels
        "field_label_title": "Title",
        "field_label_materials": "Materials",
        "field_label_region": "Region",
        "field_label_tone": "Tone",
        # Event Status Messages
        "event_done": "Event Done",
        "event_ongoing": "Event Ongoing",
    },
    "Hindi": {
        "app_title": "Artisans AI Studio",
        "app_subheader": "कंटेंट निर्माण, छवि निर्माण और विकास योजना के लिए आपका ऑल-इन-वन टूल।",
        "controls_header": "नियंत्रण",
        "page_language_label": "पेज की भाषा",
        "page_language_help": "यूजर इंटरफेस के लिए मुख्य भाषा चुनें।",
        "caption_language_label": "सामग्री की भाषा",
        "caption_language_help": "कहानी और सभी सोशल मीडिया कैप्शन (इंस्टाग्राम, फेसबुक, ट्विटर) के लिए भाषा चुनें।",
        "workflow_label": "अपना रचनात्मक मार्ग चुनें:",
        "workflow_option_1": "मार्केटिंग किट बनाएं",
        "workflow_option_2": "बाजार के रुझान खोजें",
        "workflow_option_3": "विकास योजना बनाएं",
        "workflow_option_4": "कार्यक्रम और कैलेंडर",
        "generate_kit_subheader": "मार्केटिंग किट बनाएं",
        "image_source_label": "अपनी छवि का स्रोत चुनें:",
        "source_option_1": "एआई को आपके लिए एक छवि बनाने दें",
        "source_option_2": "अपनी खुद की छवि अपलोड करें",
        "prompt_subheader": "उस सामग्री का वर्णन करें जो आप चाहते हैं",
        "prompt_placeholder_title": "जैसे, हस्तनिर्मित टेराकोटा दीया",
        "prompt_placeholder_materials": "जैसे, टेराकोटा मिट्टी, प्राकृतिक रंग",
        "prompt_placeholder_region": "जैसे, बिष्णुपुर, पश्चिम बंगाल",
        "prompt_placeholder_tone": "जैसे, देहाती, उत्सवपूर्ण, आधुनिक, सांस्कृतिक",
        "prompt_placeholder_description": "जैसे, 'एक मधुबनी कलाकार के बारे में एक कहानी जिसका काम प्रकृति की भावना को दर्शाता है।'",
        "generate_button": "मार्केटिंग किट बनाएं",
        "prompt_warning": "सामग्री बनाने के लिए कृपया एक शीर्षक या क्षेत्र दर्ज करें।",
        "upload_image_subheader": "अपनी खुद की छवि अपलोड करें",
        "image_uploader_label": "छवि अपलोड करें",
        "image_uploader_help": ".png, .jpg, या .jpeg फ़ाइल अपलोड करें।",
        "upload_warning": "सामग्री बनाने के लिए कृपया एक छवि अपलोड करें और एक शीर्षक या क्षेत्र दर्ज करें।",
        "trends_subheader": "रुझान संबंधी जानकारी प्राप्त करें",
        "trends_language_label": "रुझान की भाषा",
        "trends_label": "अपनी कला का प्रकार दर्ज करें",
        "trends_placeholder": "जैसे, मधुबनी पेंटिंग, ब्लू पॉटरी, कांथा कढ़ाई",
        "trends_button": "रुझान बनाएं",
        "trends_warning": "कृपया रुझान प्राप्त करने के लिए अपनी कला का प्रकार और एक क्षेत्र दर्ज करें।",
        "planner_subheader": "सोशल मीडिया विकास योजनाकार",
        "plan_language_label": "योजना की भाषा",
        "planner_platform_label": "अपनी योजना के लिए प्लेटफ़ॉर्म चुनें",
        "planner_platform_placeholder": "प्लेटफ़ॉर्म चुनें",
        "planner_craft_label": "अपनी कला का वर्णन करें",
        "planner_craft_placeholder": "जैसे, जयपुर से हस्तनिर्मित ब्लू पॉटरी",
        "planner_audience_label": "अपने लक्षित दर्शकों का वर्णन करें",
        "planner_audience_placeholder": "जैसे, पर्यटक, इंटीरियर डिजाइनर, 25-40 आयु वर्ग के लोग",
        "planner_button": "योजना बनाएं",
        "planner_warning": "कृपया कम से कम एक प्लेटफ़ॉर्म चुनें, अपनी कला का वर्णन करें, और एक क्षेत्र दर्ज करें।",
        "spinner_text_content": "एआई आपकी कहानी और कैप्शन {caption_lang} में तैयार कर रहा है...",
        "spinner_text_image": "इमेजेन 2 के साथ एक अनूठी छवि बना रहा है... 🖼",
        "spinner_text_trends": "{trends_lang} में बाजार के रुझानों का विश्लेषण किया जा रहा है...",
        "spinner_text_planner": "{plan_lang} में आपकी कस्टम विकास योजना बन रही है...",
        "results_header": "आपकी जेनरेट की गई मार्केटिंग किट",
        "content_ready": "आपकी सामग्री तैयार है! 🎉",
        "ai_image_caption": "एआई-जेनरेटेड छवि",
        "user_image_caption": "अपलोड की गई छवि",
        "story_header": "📜 कहानी",
        "social_header": "📱 सोशल मीडिया पोस्ट",
        "caption_suggestion": "कैप्शन सुझाव:",
        "hashtags": "हैशटैग:",
        "tweet_suggestion": "ट्वीट सुझाव:",
        "trends_results_header": "📈 बाजार रुझान अंतर्दृष्टि",
        "trends_ready": "आपकी ट्रेंड रिपोर्ट तैयार है!",
        "planner_results_header": "🚀 आपकी सोशल मीडिया विकास योजना",
        "planner_ready": "आपकी विकास योजना तैयार है!",
        "info_box": "होमपेज पर एक रचनात्मक मार्ग चुनें, अपना इनपुट प्रदान करें, और जेनरेट बटन पर क्लिक करें। साइडबार से आप किसी भी समय पथ बदल सकते हैं।",
        "clear_button": "परिणाम साफ़ करें",
        "other_option": "अन्य (कृपया निर्दिष्ट करें)",
        "other_specify": "कृपया निर्दिष्ट करें:",
        "choose_path_header": "अपना रचनात्मक मार्ग चुनें:",
        "path_option_1": "मार्केटिंग किट बनाएं",
        "path_option_2": "बाजार के रुझान खोजें",
        "path_option_3": "विकास योजना बनाएं",
        "path_option_4": "कार्यक्रम और कैलेंडर",
        "start_prompt": "शुरू करने के लिए एक पथ चुनें",
        "landing_info": "आप कभी भी साइडबार से इस पथ को बदल सकते हैं।",
        "back_to_home": "वापस होम पर जाएं",
        "desc_heading": "विवरण (वैकल्पिक)",
        # Calendar Translations
        "events_header": "📅 कारीगर कार्यक्रम और सूचनाएं",
        "event_preferences_header": "कार्यक्रम प्राथमिकताएं",
        "event_preferences_info": "उन शिल्पों को चुनें जिनमें आपकी रुचि है - सूचनाएं इन टैग से मेल खाएंगी।",
        "select_crafts_label": "शिल्प चुनें",
        "notify_days_label": "मुझे आने वाले कार्यक्रमों के बारे में सूचित करें (दिन पहले)",
        "upcoming_events_info": "आपके चयनित शिल्पों से मेल खाने वाले {count} आगामी कार्यक्रम हैं (अगले {days} दिनों में):",
        "no_upcoming_events": "अगले {days} दिनों में कोई मेल खाने वाला कार्यक्रम नहीं है।",
        "event_when": "{days} दिन में",
        "event_when_ago": "{days} दिन पहले",
        "event_venue_label": "स्थान:",
        "set_reminder_button": "रिमाइंडर सेट करें",
        "cancel_reminder_button": "रिमाइंडर रद्द करें",
        "reminder_set_success": "रिमाइंडर सेट हो गया। (यह एक सिमुलेशन है और वास्तविक सूचना नहीं भेजेगा)।",
        "reminder_cancelled_success": "रिमाइंडर रद्द कर दिया गया।",
        "calendar_header": "कैलेंडर",
        "events_list_header": "कार्यक्रम सूची और विवरण",
        "event_dates_label": "तिथियां:",
        "event_tags_label": "टैग:",
        "starts_in_caption": "{days} दिन में शुरू होगा",
        "started_ago_caption": "कार्यक्रम {days} दिन पहले शुरू हुआ",
        "ended_ago_caption": "कार्यक्रम {days} दिन पहले समाप्त हुआ",
        "active_reminder_warning": "रिमाइंडर: '{title}' {days} दिन में {date} को शुरू होगा। स्थान: {venue} — {city}",
        "no_active_reminders": "आपकी अनुस्मारक विंडो के भीतर कोई सक्रिय अनुस्मारक नहीं है।",
        "event_concluded": "कार्यक्रम समाप्त",
        "calendar_year_label": "वर्ष",
        "calendar_month_label": "महीना",
        # Field Labels
        "field_label_title": "शीर्षक",
        "field_label_materials": "सामग्री",
        "field_label_region": "क्षेत्र / शहर",
        "field_label_tone": "शैली / टोन",
        # Event Status Messages
        "event_done": "कार्यक्रम समाप्त",
        "event_ongoing": "कार्यक्रम चालू",
    }
}

ALL_REQUIRED_KEYS = [
    "app_title","app_subheader","controls_header","page_language_label","page_language_help",
    "caption_language_label","caption_language_help","workflow_label","workflow_option_1",
    "workflow_option_2","workflow_option_3","workflow_option_4","generate_kit_subheader",
    "image_source_label","source_option_1","source_option_2","prompt_subheader",
    "prompt_placeholder_title","prompt_placeholder_materials","prompt_placeholder_region",
    "prompt_placeholder_tone","prompt_placeholder_description","generate_button",
    "prompt_warning","upload_image_subheader","image_uploader_label","image_uploader_help",
    "upload_warning","trends_subheader","trends_language_label","trends_label",
    "trends_placeholder","trends_button","trends_warning","planner_subheader",
    "plan_language_label","planner_platform_label","planner_platform_placeholder",
    "planner_craft_label","planner_craft_placeholder","planner_audience_label","planner_audience_placeholder",
    "planner_button","planner_warning","spinner_text_content","spinner_text_image",
    "spinner_text_trends","spinner_text_planner","results_header","content_ready",
    "ai_image_caption","user_image_caption","story_header","social_header",
    "caption_suggestion","hashtags","tweet_suggestion","trends_results_header",
    "trends_ready","planner_results_header","planner_ready","info_box","clear_button",
    "other_option","other_specify","choose_path_header","path_option_1","path_option_2",
    "path_option_3","path_option_4","start_prompt","landing_info","back_to_home",
    "desc_heading","events_header","event_preferences_header","event_preferences_info",
    "select_crafts_label","notify_days_label","upcoming_events_info","no_upcoming_events",
    "event_when","event_when_ago","event_venue_label","set_reminder_button",
    "cancel_reminder_button","reminder_set_success","reminder_cancelled_success",
    "calendar_header","events_list_header","event_dates_label","event_tags_label",
    "starts_in_caption","started_ago_caption","ended_ago_caption","active_reminder_warning",
    "no_active_reminders","event_concluded","calendar_year_label","calendar_month_label",
    "field_label_title","field_label_materials","field_label_region","field_label_tone",
    "event_done","event_ongoing"
]

# Fill any missing Hindi keys with English fallback (prevents raw key display)
for k in ALL_REQUIRED_KEYS:
    if k not in translations["Hindi"]:
        translations["Hindi"][k] = translations["English"].get(k, k)

# Ensure every required key exists in Hindi (and any future languages) by copying from English.
for _k in ALL_REQUIRED_KEYS:
    if _k not in translations["Hindi"] or not translations["Hindi"][_k]:
        translations["Hindi"][_k] = translations["English"].get(_k, _k)

# --- CACHED HELPERS & DATA FUNCTIONS ---

@st.cache_data
def t(key: str, lang: str = "English") -> str:
    """
    Unified translation lookup with robust fallback:
    1. If key exists in target language and non-empty -> return it
    2. Else if exists in English -> return English
    3. Else return the raw key (should not happen if ALL_REQUIRED_KEYS maintained)
    """
    lang_map = translations.get(lang, translations["English"])
    val = lang_map.get(key)
    if val:
        return val
    return translations["English"].get(key, key)

@st.cache_data
def get_image_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

@st.cache_resource
def get_gemini_model():
    return genai.GenerativeModel('gemini-1.5-pro-latest')

@st.cache_resource
def get_imagen_model():
    return ImageGenerationModel.from_pretrained("imagegeneration@006")

@st.cache_data
def load_dummy_events() -> List[Dict[str, Any]]:
    """Return a list of richer dummy events (past, upcoming, next year).
        NOTE: Uses a fixed 'today' = 2025-09-10 for relative offsets.
        If your logic elsewhere assumes a different BASE today (e.g. 2025-09-13),
        either align that constant or adjust this 'today' value.
    """
    today = date(2025, 9, 10) # Fixed date to match provided screenshot logic
    events = [
        # --- Past Events (2025) ---
        {
            "id": "ev-past-01", "title": "Summer Pottery Fair",
            "craft_tags": ["Terracotta clay", "Ceramics", "Pottery"],
            "start_date": date(2025, 7, 15), "end_date": date(2025, 7, 17),
            "venue": "Bhopal Grounds", "city": "Bhopal, Madhya Pradesh",
            "description": "A showcase of central India's finest pottery.",
        },
        {
            "id": "ev-past-02", "title": "Monsoon Weaves",
            "craft_tags": ["Fabric", "Silk", "Weaving"],
            "start_date": date(2025, 8, 22), "end_date": date(2025, 8, 24),
            "venue": "Kolkata Expo Centre", "city": "Kolkata, West Bengal",
            "description": "Featuring Baluchari and Jamdani sarees.",
        },
        {
            "id": "ev-past-apr", "title": "Channapatna Toys Festival",
            "craft_tags": ["Wood", "Toys"],
            "start_date": date(2025, 4, 10), "end_date": date(2025, 4, 14),
            "venue": "Crafts Village", "city": "Channapatna, Karnataka",
            "description": "A vibrant festival for traditional toy makers.",
        },
        {
            "id": "ev-past-jun", "title": "Leather Craft Expo",
            "craft_tags": ["Leather"],
            "start_date": date(2025, 6, 5), "end_date": date(2025, 6, 7),
            "venue": "Kanpur Trade Hall", "city": "Kanpur, Uttar Pradesh",
            "description": "Connecting leather artisans with international buyers.",
        },

        # --- Upcoming Events (2025) relative to 'today' (Sept 10, 2025) ---
        {
            "id": "ev-005", "title": "All-India Craft Dialogue",
            "craft_tags": ["All", "Policy", "Market"],
            "start_date": today + timedelta(days=1), # Sep 11
            "end_date": today + timedelta(days=1),
            "venue": "Pragati Maidan - Hall 6", "address": "Pragati Maidan Complex",
            "city": "New Delhi",
            "description": "A forum for artisans to discuss market linkages and policy.",
        },
        {
            "id": "ev-001", "title": "Handmade Bazaar",
            "craft_tags": ["Terracotta clay", "Ceramics", "Pottery"],
            "start_date": today + timedelta(days=6), # Sep 16
            "end_date": today + timedelta(days=8),   # Sep 18
            "venue": "Amber Grounds", "address": "Amber Rd, Near Amer Fort",
            "city": "Jaipur, Rajasthan",
            "description": "A curated fair for pottery and terracotta artisans from Rajasthan.",
        },
        {
            "id": "ev-sep-17", "title": "Artisan Weavers Meet",
            "craft_tags": ["Weaving", "Fabric"],
            "start_date": date(2025, 9, 17), "end_date": date(2025, 9, 17),
            "venue": "Community Hall", "city": "Jaipur, Rajasthan",
            "description": "A meeting for local weavers.",
        },
        {
            "id": "ev-sep-24", "title": "Bazaar Planning Session",
            "craft_tags": ["Market", "Policy"],
            "start_date": date(2025, 9, 24), "end_date": date(2025, 9, 24),
            "venue": "Online", "city": "Virtual",
            "description": "Planning for the next big bazaar.",
        },
        {
            "id": "ev-002", "title": "Banarasi Silks Expo",
            "craft_tags": ["Fabric", "Silk", "Weaving"],
            "start_date": today + timedelta(days=17), # Sep 27
            "end_date": today + timedelta(days=18),   # Sep 28
            "venue": "Vishwanath Conference Hall",
            "address": "Manduadih Rd, Near Kashi Vishwanath Temple",
            "city": "Varanasi, Uttar Pradesh",
            "description": "Silk weavers showcase and buyer connect event.",
        },
        {
            "id": "ev-003", "title": "Kutch Embroidery Symposium",
            "craft_tags": ["Embroidery", "Bandhani", "Fabric"],
            "start_date": today + timedelta(days=32), # Oct 12
            "end_date": today + timedelta(days=33),   # Oct 13
            "venue": "Bhuj Crafts Centre",
            "address": "Plot 12, Crafts Complex, Bhuj",
            "city": "Bhuj, Kutch, Gujarat",
            "description": "Workshops and exhibitions focusing on Kutch embroidery.",
        },
        {
            "id": "ev-diwali", "title": "Diwali Crafts Mela",
            "craft_tags": ["All", "Festive", "Pottery", "Fabric"],
            "start_date": date(2025, 10, 25), "end_date": date(2025, 10, 30),
            "venue": "Dilli Haat INA", "city": "New Delhi",
            "description": "The biggest festive market for artisans.",
        },
        {
            "id": "ev-winter", "title": "Winter Pashmina Showcase",
            "craft_tags": ["Fabric", "Wool"],
            "start_date": date(2025, 12, 18), "end_date": date(2025, 12, 22),
            "venue": "Srinagar Arts Emporium", "city": "Srinagar, Jammu & Kashmir",
            "description": "Exclusive showcase of fine Pashmina shawls.",
        },

        # --- Next Year (2026) ---
        {
            "id": "ev-2026-01", "title": "New Year Woodcraft Show",
            "craft_tags": ["Wood", "Carving"],
            "start_date": date(2026, 1, 10), "end_date": date(2026, 1, 12),
            "venue": "Mysore Palace Grounds", "city": "Mysuru, Karnataka",
            "description": "Exhibition of fine sandalwood and rosewood carving.",
        },
        {
            "id": "ev-2026-02", "title": "Republic Day Parade Crafts",
            "craft_tags": ["All", "National"],
            "start_date": date(2026, 1, 26), "end_date": date(2026, 1, 26),
            "venue": "Kartavya Path", "city": "New Delhi",
            "description": "Selected artisans showcase their state's craft in the parade.",
        },
        {
            "id": "ev-2026-03", "title": "Spring Metalwork Conclave",
            "craft_tags": ["Metals", "Brass"],
            "start_date": date(2026, 3, 5), "end_date": date(2026, 3, 7),
            "venue": "Moradabad Trade Center", "city": "Moradabad, Uttar Pradesh",
            "description": "A B2B event for brass and metal artisans.",
        },
        {
            "id": "ev-2026-04", "title": "Pattachitra Art Camp",
            "craft_tags": ["Painting", "Art"],
            "start_date": date(2026, 5, 20), "end_date": date(2026, 5, 25),
            "venue": "Raghurajpur Heritage Village", "city": "Puri, Odisha",
            "description": "A live-in art camp for Pattachitra painters.",
        },
        {
            "id": "ev-2026-05", "title": "Southern Silk Summit",
            "craft_tags": ["Silk", "Fabric"],
            "start_date": date(2026, 8, 15), "end_date": date(2026, 8, 17),
            "venue": "Chennai Trade Centre", "city": "Chennai, Tamil Nadu",
            "description": "Showcasing Kanjeevaram and other southern silks.",
        },
    ]
    return events

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
    # Unified baseline date with calendar (was 2025-09-12 elsewhere)
    today = date(2025, 9, 13)
    return (d - today).days

def format_days(count: int, lang: str) -> str:
    if lang == "Hindi":
        return f"{count} दिन"
    unit = "day" if abs(count) == 1 else "days"
    return f"{count} {unit}"

def clean_day_artifacts(text: str) -> str:
    import re as _re
    text = _re.sub(r"\bday\(s\)\b", "", text)
    text = _re.sub(r"\s{2,}", " ", text).strip()
    text = _re.sub(r"(\b\d+\s+days?)\s+day\(s\)", r"\1", text)
    text = _re.sub(r"(\b\d+\s+day)\s+day\(s\)", r"\1", text)
    return text

# --- AI & AUTHENTICATION CONFIG ---
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

# --- AI HELPER FUNCTIONS ---
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

# --- AUTH HELPER FUNCTIONS ---
def parse_firebase_error(error_message):
    """Converts Firebase error messages into user-friendly strings.
    Enhanced: case-insensitive matching + added USER_DISABLED, TOO_MANY_ATTEMPTS_TRY_LATER, and network/timeout hints.
    """
    if not error_message:
        return "An unexpected error occurred. Please try again later."
    msg = error_message.upper()

    if "INVALID_LOGIN_CREDENTIALS" in msg:
        return "Invalid email or password. Please try again."
    if "EMAIL_NOT_FOUND" in msg:
        return "No account found with this email address."
    if "INVALID_PASSWORD" in msg:
        return "Incorrect password. Please try again."
    if "EMAIL_EXISTS" in msg:
        return "An account with this email address already exists."
    if "WEAK_PASSWORD" in msg:
        return "Password is too weak. It should be at least 6 characters long."
    if "USER_DISABLED" in msg:
        return "This account has been disabled. Please contact support."
    if "TOO_MANY_ATTEMPTS_TRY_LATER" in msg:
        return "Too many failed attempts. Please try again later."
    if "NETWORK" in msg or "TIMEOUT" in msg:
        return "Network issue. Please check your connection and try again."

    return "An unexpected error occurred. Please try again later."