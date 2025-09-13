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
import base64
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

# Ensure all translation keys exist and avoid raw key names showing in UI.
# Also replace the cached translator with a safer fallback mechanism.

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

# ---- FIX TRANSLATION FALLBACKS (replace the two t() definitions with this single one) ----
# Ensure every required key exists in Hindi (and any future languages) by copying from English.
for _k in ALL_REQUIRED_KEYS:
    if _k not in translations["Hindi"] or not translations["Hindi"][_k]:
        translations["Hindi"][_k] = translations["English"].get(_k, _k)

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

# --- 2. CACHED HELPERS ---
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
    today = date(2025, 9, 10)  # Fixed date to match provided screenshot logic
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
            "start_date": today + timedelta(days=1),  # Sep 11
            "end_date": today + timedelta(days=1),
            "venue": "Pragati Maidan - Hall 6", "address": "Pragati Maidan Complex",
            "city": "New Delhi",
            "description": "A forum for artisans to discuss market linkages and policy.",
        },
        {
            "id": "ev-001", "title": "Handmade Bazaar",
            "craft_tags": ["Terracotta clay", "Ceramics", "Pottery"],
            "start_date": today + timedelta(days=6),  # Sep 16
            "end_date": today + timedelta(days=8),    # Sep 18
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
            "start_date": today + timedelta(days=17),  # Sep 27
            "end_date": today + timedelta(days=18),    # Sep 28
            "venue": "Vishwanath Conference Hall",
            "address": "Manduadih Rd, Near Kashi Vishwanath Temple",
            "city": "Varanasi, Uttar Pradesh",
            "description": "Silk weavers showcase and buyer connect event.",
        },
        {
            "id": "ev-003", "title": "Kutch Embroidery Symposium",
            "craft_tags": ["Embroidery", "Bandhani", "Fabric"],
            "start_date": today + timedelta(days=32),  # Oct 12
            "end_date": today + timedelta(days=33),    # Oct 13
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

# Added helpers for improved calendar wording
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
    p, li, div, label, .stMarkdown { font-size: 1.15rem; }
    [data-testid="stSidebar"] { background-color: var(--sidebar-background); border-right: 1px solid var(--border-color); }
    [data-testid="stHeader"] { background-color: rgba(253, 245, 230, 0.8); backdrop-filter: blur(10px); box-shadow: none; border-bottom: 1px solid var(--border-color); }
    .stSelectbox, .stTextInput, .stTextArea, .stFileUploader, .stMultiSelect { border-radius: var(--border-radius); }
    .stSelectbox > div > div, .stTextInput > div > div, .stTextArea > div > div, .stFileUploader > div > div { background-color: var(--widget-background); border: 1px solid var(--border-color); border-radius: var(--border-radius); box-shadow: var(--shadow); color: var(--primary-text-color); }
    .stSelectbox div[role="listbox"] { background-color: var(--widget-background); border-radius: var(--border-radius); border: 1px solid var(--border-color); }
    .stButton > button { background-color: var(--accent-color); color: white; border: none; padding: 12px 28px; font-size: 16px; font-weight: bold; border-radius: var(--border-radius); box-shadow: var(--shadow); transition: background-color 0.2s ease-in-out, transform 0.1s ease-in-out; }
    .stButton > button:hover { background-color: var(--accent-hover-color); transform: scale(1.02); }
    .stButton > button:active { transform: scale(0.98); }
    .stButton > button:disabled { background-color: var(--accent-color); color: white; opacity: 1; cursor: not-allowed; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: var(--border-radius) var(--border-radius) 0 0; border-bottom: 2px solid var(--border-color); padding: 10px 16px; }
    .stTabs [aria-selected="true"] { background-color: var(--widget-background); border-bottom: 2px solid var(--accent-color); box-shadow: var(--shadow); }
    .stCodeBlock, .st-emotion-cache-1f2d20p { background-color: #F5F0E8; color: var(--primary-text-color); border-left: 5px solid var(--accent-color); border-radius: var(--border-radius); padding: 1rem; font-size: 1.15rem !important; }
    .stAlert { border-radius: var(--border-radius); box-shadow: var(--shadow); }
    .stAlert.success { background-color: #E8F5E9; border-left: 8px solid #4CAF50; }
    .stAlert.warning { background-color: #FFFDE7; border-left: 8px solid #FFC107; }
    .stAlert.info { background-color: #E1F5FE; border-left: 8px solid #03A9F4; }
    
    /* --- UPDATED CALENDAR CSS (New provided variant) --- */
    .demo-container {
        display: flex;
        gap: 10px;
    }

    .calendar-cell {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        min-height: 120px;
        width: 170px;
        padding: 6px;
        display: flex;
        flex-direction: column;
        gap: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        overflow: hidden;
    }

    .day-number {
        font-weight: 500;
        font-size: 0.875rem; /* 14px equivalent */
        color: #111827;
        margin: 0;
    }

    .events-container {
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 3px;
        overflow: hidden;
    }

    .event-bar {
        background-color: #5D4037;
        color: white;
        padding: 3px 6px;
        font-size: 12px;
        font-weight: 500;
        border-radius: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .event-bar a {
        color:#fff;
        text-decoration:none;
        display:block;
        width:100%;
    }
    .event-bar a:hover { text-decoration:underline; }
    /* Optional highlight style when jumping */
    .focused-event-row {
        border-left:4px solid var(--accent-color);
        background:#FFF8ED;
        padding-left:6px;
    }

    .event-bar-start { border-top-right-radius:0; border-bottom-right-radius:0; }
    .event-bar-middle { border-radius:0; }
    .event-bar-end { border-top-left-radius:0; border-bottom-left-radius:0; }

    /* Remove legacy container style that pushed content over the date */
    .calendar-event-container { margin-top:0; background:transparent; padding:0; box-shadow:none; }
</style>
"""
st.markdown(pottery_theme_css, unsafe_allow_html=True)
# ...existing code above...

# REPLACE the existing second calendar style block (the one that makes .day-number absolute)
# with this updated block so events render below the date number cleanly.
st.markdown("""
<style>
    /* Calendar layout fix: keep date at top, events below (no overlay) */
    .calendar-cell {
        min-height:120px;
        padding:8px 8px 6px;
        border-radius:10px;
        background:#fff;
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
    .event-bar-start { border-top-right-radius:0; border-bottom-right-radius:0; }
    .event-bar-middle { border-radius:0; }
    .event-bar-end { border-top-left-radius:0; border-bottom-left-radius:0; }

    /* Remove legacy container style that pushed content over the date */
    .calendar-event-container { margin-top:0; background:transparent; padding:0; box-shadow:none; }
</style>
""", unsafe_allow_html=True)

# ...existing code below...

# ...some existing code above (place this CSS after your main theme CSS blocks, before WORKFLOW 4)...
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
# ...existing code...

# ...replace the existing reminder button CSS block (black/grey one) with this brown/grey version...
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
# ...existing code...

# ...append AFTER existing reminder button CSS block (this overrides previous hover behaviors)...

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

# ...append AFTER the existing reminder button CSS blocks (final override)...
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
# ...existing code...

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
    st.session_state.selected_workflow_key = mapped  # stays None if none selected
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

        st.markdown("---")
        if st.button(t('clear_button', page_language), on_click=clear_results, use_container_width=True):
            st.rerun()

        st.markdown("---")
        st.header(t('event_preferences_header', page_language))
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
            "Brass": "पीतल",
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
        else:
            st.markdown("#### " + t('upload_image_subheader', page_language))
            uploaded_file = st.file_uploader(
                t('image_uploader_label', page_language),
                type=["png","jpg","jpeg"],
                help=t('image_uploader_help', page_language)
            )
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
    elif workflow_key == "discover_trends":
        st.subheader(t('trends_subheader', page_language))
        content_language_list = ["English","Hindi","Hinglish","Bengali","Tamil","Gujarati","Marathi"]
        trends_language = st.selectbox(t('trends_language_label', page_language), content_language_list, key='trends_lang')
        trends_region = st.text_input(
            t('field_label_region', page_language),
            placeholder=t('prompt_placeholder_region', page_language),
            key='trends_region'
        )
        craft_type = st.text_input(t('trends_label', page_language), placeholder=t('trends_placeholder', page_language))
        if st.button(t('trends_button', page_language), use_container_width=True):
            if craft_type and trends_region:
                clear_results()
                with st.spinner(t('spinner_text_trends', page_language).format(trends_lang=trends_language)):
                    st.session_state.market_trends = get_market_trends(trends_region, trends_language, craft_type)
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
        today_ref = date(2025, 9, 13)  # single consistent 'today'
        retention_days = 14  # keep ended events up to 2 weeks old
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
            if not (ev['end_date'] < retention_cutoff)  # drop very old past events
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
                    if ev['start_date'] > today_ref:  # only future events toggle reminders
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

        today_fixed = today_ref  # Align with new calendar baseline (or replace with date.today())
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
    elif workflow_key != "events_calendar":
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
