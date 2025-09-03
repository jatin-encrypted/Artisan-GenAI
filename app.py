# app.py
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import json
import os
import re

# Imports for robust authentication
import google.auth
from google.oauth2 import service_account

# Import Vertex AI libraries for Imagen
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

# --- 1. TRANSLATIONS DICTIONARY ---
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
        "workflow_option_1": "Generate Content & Image",
        "workflow_option_2": "Upload an Image & Generate Content",
        "workflow_option_3": "Discover Market Trends",
        "workflow_option_4": "Create a Growth Plan",
        "prompt_subheader": "Describe the content you want",
        "prompt_placeholder_title": "e.g., Handmade Terracotta Diya",
        "prompt_placeholder_materials": "e.g., Terracotta clay, natural dyes",
        "prompt_placeholder_region": "e.g., Bishnupur, West Bengal",
        "prompt_placeholder_size": "e.g., 3-inch diameter, set of 6",
        "prompt_placeholder_tone": "e.g., rustic, festive, modern, cultural",
        "prompt_placeholder_description": "e.g., 'A story about a Madhubani artist whose work reflects the spirit of nature.'",
        "generate_content_button": "Generate Content",
        "generate_image_button": "Generate Image",
        "prompt_warning": "Please enter a Title or Region to generate content.",
        "upload_image_subheader": "Upload your own image",
        "image_uploader_label": "Upload Image",
        "image_uploader_help": "Upload a .png, .jpg, or .jpeg file.",
        "upload_warning": "Please upload an image and enter a Title or Region to generate content.",
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
        # New keys for size selector and landing page
        "select_size": "Select Output Size",
        "enter_size": "Enter size (integer)",
        "unit_label": "Unit",
        "unit_option_inches": "inches",
        "unit_option_cm": "cm",
        "choose_path_header": "Choose your creative path:",
        "path_option_1": "Generate Content & Image",
        "path_option_2": "Upload an Image & Generate Content",
        "path_option_3": "Discover Market Trends",
        "path_option_4": "Create a Growth Plan",
        "start_prompt": "Select a path to get started",
        "landing_info": "You can change this path anytime from the sidebar.",
        "back_to_home": "Back to Home"
    },
    "Hindi": {
        "app_title": "कलाकार एआई स्टूडियो",
        "app_subheader": "कंटेंट निर्माण, छवि निर्माण और विकास योजना के लिए आपका ऑल-इन-वन टूल।",
        "controls_header": "नियंत्रण",
        "page_language_label": "पेज की भाषा",
        "page_language_help": "यूजर इंटरफेस के लिए मुख्य भाषा चुनें।",
        "caption_language_label": "सामग्री की भाषा",
        "caption_language_help": "कहानी और सभी सोशल मीडिया कैप्शन (इंस्टाग्राम, फेसबुक, ट्विटर) के लिए भाषा चुनें।",
        "workflow_label": "अपना रचनात्मक मार्ग चुनें:",
        "workflow_option_1": "सामग्री और छवि बनाएं",
        "workflow_option_2": "एक छवि अपलोड करें और सामग्री बनाएं",
        "workflow_option_3": "बाजार के रुझान खोजें",
        "workflow_option_4": "विकास योजना बनाएं",
        "prompt_subheader": "उस सामग्री का वर्णन करें जो आप चाहते हैं",
        "prompt_placeholder_title": "जैसे, हस्तनिर्मित टेराकोटा दीया",
        "prompt_placeholder_materials": "जैसे, टेराकोटा मिट्टी, प्राकृतिक रंग",
        "prompt_placeholder_region": "जैसे, बिष्णुपुर, पश्चिम बंगाल",
        "prompt_placeholder_size": "जैसे, 3-इंच व्यास, 6 का सेट",
        "prompt_placeholder_tone": "जैसे, देहाती, उत्सवपूर्ण, आधुनिक, सांस्कृतिक",
        "prompt_placeholder_description": "जैसे, 'एक मधुबनी कलाकार के बारे में एक कहानी जिसका काम प्रकृति की भावना को दर्शाता है।'",
        "generate_content_button": "सामग्री बनाएं",
        "generate_image_button": "छवि बनाएं",
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
        # New keys for size selector and landing page
        "select_size": "आउटपुट आकार चुनें",
        "enter_size": "आकार दर्ज करें (पूर्णांक)",
        "unit_label": "इकाई",
        "unit_option_inches": "इंच",
        "unit_option_cm": "सेमी",
        "choose_path_header": "अपना रचनात्मक मार्ग चुनें:",
        "path_option_1": "सामग्री और छवि बनाएं",
        "path_option_2": "एक छवि अपलोड करें और सामग्री बनाएं",
        "path_option_3": "बाजार के रुझान खोजें",
        "path_option_4": "विकास योजना बनाएं",
        "start_prompt": "शुरू करने के लिए एक पथ चुनें",
        "landing_info": "आप कभी भी साइडबार से इस पथ को बदल सकते हैं।",
        "back_to_home": "वापस होम पर जाएं"
    }
}

# --- 2. CACHED HELPER FUNCTIONS ---
@st.cache_data
def t(key, lang="English"):
    """Gets the translated text for a given key and language, defaulting to English."""
    return translations.get(lang, translations["English"]).get(key, key)

@st.cache_resource
def get_gemini_model():
    return genai.GenerativeModel('gemini-1.5-pro-latest')

@st.cache_resource
def get_imagen_model():
    return ImageGenerationModel.from_pretrained("imagegeneration@006")

# --- 3. PAGE CONFIGURATION & THEME (Pottery Theme) ---
initial_lang = st.query_params.get("lang", "English")
st.set_page_config(
    page_title=t("app_title", initial_lang),
    page_icon="🏺",
    layout="wide",
)

# Inlined Base64 SVG for a subtle, artisanal background pattern
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
    .stApp {
        background-color: var(--background-color);
        background-image: var(--background-image-url);
        background-attachment: fixed;
        color: var(--primary-text-color);
    }
    h1, h2, h3, h4, h5, h6, .stMarkdown, label, p, .stAlert, [data-baseweb="tab"] {
        color: var(--primary-text-color) !important;
        font-family: var(--font);
    }
    p, li, div, label, .stMarkdown {
        font-size: 1.1rem;
    }
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-background);
        border-right: 1px solid var(--border-color);
    }
    [data-testid="stHeader"] {
        background-color: rgba(253, 245, 230, 0.8);
        backdrop-filter: blur(10px);
        box-shadow: none;
        border-bottom: 1px solid var(--border-color);
    }
    .stSelectbox, .stTextInput, .stTextArea, .stFileUploader, .stMultiSelect {
        border-radius: var(--border-radius);
    }
    .stSelectbox > div > div, .stTextInput > div > div, .stTextArea > div > div, .stFileUploader > div > div {
        background-color: var(--widget-background);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        color: var(--primary-text-color);
    }
    .stSelectbox div[role="listbox"] {
        background-color: var(--widget-background);
        border-radius: var(--border-radius);
        border: 1px solid var(--border-color);
    }
    .stButton > button {
        background-color: var(--accent-color);
        color: white;
        border: none;
        padding: 12px 28px;
        font-size: 16px;
        font-weight: bold;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        transition: background-color 0.2s ease-in-out, transform 0.1s ease-in-out;
    }
    .stButton > button:hover {
        background-color: var(--accent-hover-color);
        transform: scale(1.02);
    }
    .stButton > button:active {
        transform: scale(0.98);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: var(--border-radius) var(--border-radius) 0 0;
        border-bottom: 2px solid var(--border-color);
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--widget-background);
        border-bottom: 2px solid var(--accent-color);
        box-shadow: var(--shadow);
    }
    .stCodeBlock, .st-emotion-cache-1f2d20p {
        background-color: #F5F0E8;
        color: var(--primary-text-color);
        border-left: 5px solid var(--accent-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        font-size: 1rem !important;
    }
    .stAlert {
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
    }
    .stAlert.success { background-color: #E8F5E9; border-left: 8px solid #4CAF50; }
    .stAlert.warning { background-color: #FFFDE7; border-left: 8px solid #FFC107; }
    .stAlert.info { background-color: #E1F5FE; border-left: 8px solid #03A9F4; }
</style>
"""
st.markdown(pottery_theme_css, unsafe_allow_html=True)

# --- 4. AI & AUTHENTICATION CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    
    _project_id = None
    _credentials = None

    if 'GCP_SERVICE_ACCOUNT_JSON' in st.secrets:
        gcp_service_account_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT_JSON"])
        _credentials = service_account.Credentials.from_service_account_info(gcp_service_account_info)
        _project_id = _credentials.project_id
    else:
        _credentials, _project_id = google.auth.default()
    
    if not _project_id:
        st.error("GCP Project ID not found. Please ensure GCP_SERVICE_ACCOUNT_JSON is configured or default credentials are available.")
        st.stop()
    
    vertexai.init(project=_project_id, credentials=_credentials, location="us-central1")

except Exception as e:
    st.error(f"Authentication or Configuration Error: {e}. Please ensure GEMINI_API_KEY and GCP_SERVICE_ACCOUNT_JSON are correctly set in Streamlit secrets.")
    st.stop()

# --- 5. AI HELPER FUNCTIONS (Now with corrected JSON parsing) ---
def generate_image_with_imagen(prompt):
    try:
        model = get_imagen_model()
        response = model.generate_images(prompt=prompt, number_of_images=1, aspect_ratio="1:1")
        if response.images:
            image_bytes = response.images[0]._image_bytes
            return Image.open(io.BytesIO(image_bytes))
        else:
            st.error("Imagen did not return any images.")
            return None
    except Exception as e:
        st.error(f"An error occurred with Imagen: {e}. Please ensure the Imagen API is enabled for your GCP project and billing is set up.")
        return None

def get_ai_content(prompt_fields, caption_language):
    model = get_gemini_model()
    
    # Construct a detailed prompt from the structured inputs
    text_prompt = f"""
    Generate a story and social media content for a product with the following details. Ensure the content feels authentic to the artisan's voice and is culturally relevant.
    
    Title: {prompt_fields.get('title', '')}
    Materials: {prompt_fields.get('materials', '')}
    Region: {prompt_fields.get('region', '')}
    Size: {prompt_fields.get('size', '')}
    Size value (integer): {prompt_fields.get('size_value', '')}
    Unit: {prompt_fields.get('size_unit', '')}
    Tone: {prompt_fields.get('tone', '')}
    Description: {prompt_fields.get('description', '')}

    Instructions:
    - You are an expert creative assistant for Indian artisans from {prompt_fields.get('region', 'India')}.
    - The 'story' MUST be in {caption_language}.
    - The 'caption' and 'text' for all social media posts MUST be in {caption_language}.
    - The entire output must be a single, valid JSON object with this schema:
    {{
      "story": "...",
      "instagram_post": {{ "caption": "...", "hashtags": "..." }},
      "twitter_post": {{ "text": "..." }},
      "facebook_post": {{ "caption": "...", "hashtags": "..." }}
    }}
    """
    
    try:
        response = model.generate_content(text_prompt, request_options={"timeout": 600})
        
        # New, more robust JSON extraction
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            raise ValueError("Could not find a valid JSON object in the AI response.")
            
    except (json.JSONDecodeError, ValueError) as e:
        st.error(f"Error processing AI response: {e}")
        st.code(response.text if 'response' in locals() else "No response from model.", language="text")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def get_market_trends(region, language, craft_type):
    model = get_gemini_model()
    prompt_instructions = f"""
    You are a market analyst for Indian artisans from {region}. Provide actionable trend insights for '{craft_type}' in {language}.
    Format the output as clean markdown. Include:
    1. Trending Themes & Concepts: Explain relevance.
    2. Popular Color Palettes: Suggest combinations.
    3. Innovative Product Ideas: Be specific and modern.
    4. Marketing Angles & Keywords: Suggest a short angle and keywords.
    """
    try:
        response = model.generate_content(prompt_instructions, request_options={"timeout": 600})
        return response.text
    except Exception as e:
        st.error(f"Error generating trends: {e}")
        return None

def get_growth_plan(region, language, platforms, craft_type, target_audience):
    model = get_gemini_model()
    prompt_instructions = f"""
    You are a social media growth strategist from {region}, specializing in helping local artisans.
    Your task is to create a detailed, actionable social media growth plan in {language}.

    Artisan's Details:
    - Craft Type: {craft_type}
    - Target Audience: {target_audience}
    - Selected Platforms: {', '.join(platforms)}

    Instructions:
    Generate the plan in a clean, easy-to-read markdown format. The plan must be tailored to the specific craft and audience.
    The output MUST include the following sections for EACH of the selected platforms:

    ### {platforms[0]} Growth Plan

    - Optimal Posting Times (IST): Suggest 2-3 specific time slots and days.
    - Posting Frequency: Recommend a realistic number of posts per week.
    - Content Mix Strategy: Provide a percentage-based breakdown of content types.
    - A specific, creative post idea: Give one concrete example of a post they could make.

    --- 
    (Repeat the above structure for any other selected platforms).

    End with a short, encouraging general tip.
    """
    try:
        response = model.generate_content(prompt_instructions, request_options={"timeout": 600})
        return response.text
    except Exception as e:
        st.error(f"Error generating growth plan: {e}")
        return None

# --- 6. SESSION STATE INITIALIZATION ---
if 'ai_results' not in st.session_state: st.session_state.ai_results = None
if 'generated_image' not in st.session_state: st.session_state.generated_image = None
if 'uploaded_image' not in st.session_state: st.session_state.uploaded_image = None
if 'market_trends' not in st.session_state: st.session_state.market_trends = None
if 'growth_plan' not in st.session_state: st.session_state.growth_plan = None
if 'story_is_ready' not in st.session_state: st.session_state.story_is_ready = False
if 'current_prompt_fields' not in st.session_state: st.session_state.current_prompt_fields = {}
if 'selected_workflow' not in st.session_state: st.session_state.selected_workflow = None

def clear_results():
    st.session_state.ai_results = None
    st.session_state.generated_image = None
    st.session_state.uploaded_image = None
    st.session_state.market_trends = None
    st.session_state.growth_plan = None
    st.session_state.story_is_ready = False
    st.session_state.current_prompt_fields = {}
    st.session_state.user_region = ""
    st.session_state.user_craft_type = ""

# --- 7. MAIN APP UI ---
page_language = st.query_params.get("lang", "English")

st.title(f"🏺 {t('app_title', page_language)}")
st.markdown(t('app_subheader', page_language))

# --- 8. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header(f"⚙ {t('controls_header', page_language)}")
    
    page_language_list = list(translations.keys())
    content_language_list = ["English", "Hindi", "Hinglish", "Bengali", "Tamil", "Gujarati", "Marathi", "Telugu", "Kannada", "Malayalam", "Odia", "Punjabi", "Urdu"]
    
    def on_lang_change():
        st.query_params["lang"] = st.session_state.page_lang_selector
    
    selected_index = page_language_list.index(page_language) if page_language in page_language_list else 0
    st.selectbox(
        t('page_language_label', page_language),
        page_language_list,
        index=selected_index,
        help=t('page_language_help', page_language),
        key='page_lang_selector',
        on_change=on_lang_change
    )
    
    # Sidebar workflow radio (keeps the sidebar available to change workflow later)
    workflow_options = [
        t('workflow_option_1', page_language), 
        t('workflow_option_2', page_language),
        t('workflow_option_3', page_language),
        t('workflow_option_4', page_language)
    ]
    def on_sidebar_workflow_change():
        st.session_state.selected_workflow = st.session_state.sidebar_workflow

    # default index if already selected
    sidebar_index = 0
    if st.session_state.selected_workflow in workflow_options:
        try:
            sidebar_index = workflow_options.index(st.session_state.selected_workflow)
        except Exception:
            sidebar_index = 0

    st.radio(t('workflow_label', page_language), workflow_options, index=sidebar_index, key='sidebar_workflow', on_change=on_sidebar_workflow_change)
    st.markdown("---")
    
    if st.button(t('clear_button', page_language), on_click=clear_results, use_container_width=True):
        # st.rerun() is an available function in many Streamlit versions; keep as-is.
        try:
            st.rerun()
        except Exception:
            pass

# --- Landing page for first-time choice ---
if not st.session_state.selected_workflow:
    st.markdown("### " + t('choose_path_header', page_language))
    st.info(t('landing_info', page_language))
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('path_option_1', page_language), key="landing_p1", use_container_width=True):
            st.session_state.selected_workflow = t('workflow_option_1', page_language)
            # try to rerun if available, otherwise continue (Streamlit will usually rerun automatically)
            try:
                st.rerun()
            except Exception:
                pass
        st.write("")
        if st.button(t('path_option_3', page_language), key="landing_p3", use_container_width=True):
            st.session_state.selected_workflow = t('workflow_option_3', page_language)
            try:
                st.rerun()
            except Exception:
                pass
    with col2:
        if st.button(t('path_option_2', page_language), key="landing_p2", use_container_width=True):
            st.session_state.selected_workflow = t('workflow_option_2', page_language)
            try:
                st.rerun()
            except Exception:
                pass
        st.write("")
        if st.button(t('path_option_4', page_language), key="landing_p4", use_container_width=True):
            st.session_state.selected_workflow = t('workflow_option_4', page_language)
            try:
                st.rerun()
            except Exception:
                pass

    st.markdown("---")
    st.info(t('info_box', page_language))
    st.stop()

# Use selected workflow (either from landing or sidebar)
workflow = st.session_state.selected_workflow

# --- MAIN CONTENT & ACTION BUTTONS ---
#st.markdown("---", help="Separator")

# Create a merged, extended region list (old list + craft hubs)
EXTENDED_REGION_OPTIONS = [
    # original examples
    "Jaipur, Rajasthan",
    "Kutch, Gujarat",
    "Madhubani, Bihar",
    "Bishnupur, West Bengal",
    "Varanasi, Uttar Pradesh",
    # major metro + craft hubs
    "New Delhi / Delhi",
    "Mumbai, Maharashtra",
    "Kolkata, West Bengal",
    "Chennai, Tamil Nadu",
    "Bengaluru, Karnataka",
    "Hyderabad, Telangana",
    "Pune, Maharashtra",
    "Ahmedabad, Gujarat",
    "Surat, Gujarat",
    "Lucknow, Uttar Pradesh",
    "Kanpur, Uttar Pradesh",
    "Nagpur, Maharashtra",
    "Indore, Madhya Pradesh",
    "Bhopal, Madhya Pradesh",
    "Visakhapatnam, Andhra Pradesh",
    "Patna, Bihar",
    "Vadodara, Gujarat",
    "Ghaziabad, Uttar Pradesh",
    "Ludhiana, Punjab",
    "Agra, Uttar Pradesh",
    "Nashik, Maharashtra",
    "Faridabad, Haryana",
    "Meerut, Uttar Pradesh",
    "Rajkot, Gujarat",
    "Kalyan-Dombivali, Maharashtra",
    "Vasai-Virar, Maharashtra",
    "Srinagar, Jammu & Kashmir",
    "Dhanbad, Jharkhand",
    "Jodhpur, Rajasthan",
    "Amritsar, Punjab",
    "Raipur, Chhattisgarh",
    "Howrah, West Bengal",
    "Coimbatore, Tamil Nadu",
    "Jabalpur, Madhya Pradesh",
    "Gwalior, Madhya Pradesh",
    "Vijayawada, Andhra Pradesh",
    "Madurai, Tamil Nadu",
    "Tiruchirappalli, Tamil Nadu",
    "Kota, Rajasthan",
    "Bareilly, Uttar Pradesh",
    "Moradabad, Uttar Pradesh",
    "Mysuru (Mysore), Karnataka",
    "Jalandhar, Punjab",
    "Aligarh, Uttar Pradesh",
    "Gurugram (Gurgaon), Haryana",
    "Bilaspur, Chhattisgarh",
    # Craft-specific hubs (from curated list)
    "Banaras / Varanasi (Banarasi silk, brass)",
    "Moradabad (Brassware)",
    "Firozabad (Glass & bangles)",
    "Aligarh (Zari & metalwork)",
    "Agra (Pietra Dura inlay)",
    "Mirzapur / Bhadohi (Carpets)",
    "Saharanpur (Wood-carving)",
    "Mathura (Bronze sculptures)",
    "Khurja (Glazed pottery)",
    "Mainpuri (Woodwork)",
    "Vrindavan (Decorative crafts)",
    "Hathras (Carving & crafts)",
    "Rampur (Textiles & crafts)",
    "Shahjahanpur (Handicrafts)",
    "Makrana (Marble/stone craft)",
    "Bhuj / Kutch (Bandhani, embroidery, lacquer)",
    "Nirona (Rogan painting, lacquer)",
    "Surat (Diamond & textile crafts)",
    "Rajkot (Textiles & metalwork)",
    "Palitana (Stone carving, temple crafts)",
    "Mysore (Silk, sandalwood carving)",
    "Channapatna (Lacquered toys)",
    "Kinnal (Wood carving)",
    "Bishnupur (Terracotta, Baluchari)",
    "Murshidabad / Khagra (Silk, metalwork)",
    "Raghurajpur (Pattachitra painting)",
    "Pipili (Applique work)",
    "Kondapalli (Wooden toys)",
    "Srinagar (Pashmina, papier-mâché)",
    "Aranmula (Aranmula metal mirrors)",
    "Asharikandi (Terracotta - Assam)",
    "Kota Doria / Kota (Textiles)",
    "Bikaner (Cane, leather, metalwork)",
    "Sualkuchi (Silk weaving, Assam)",
    "Salarpuria / small craft towns",  # placeholder if you want to add more
    # Fallback
    t('other_option', page_language)
]

# --- WORKFLOW 1: GENERATE CONTENT & IMAGE ---
if workflow == t('workflow_option_1', page_language):
    caption_language = st.sidebar.selectbox(
        t('caption_language_label', page_language),
        content_language_list,
        help=t('caption_language_help', page_language)
    )
    
    st.subheader(t('prompt_subheader', page_language))
    prompt_fields = {}
    prompt_fields['title'] = st.text_input("Title", placeholder=t('prompt_placeholder_title', page_language))
    
    # ✅ Expanded Materials Dropdown
    material_options = [
        "Terracotta clay",
        "Brass",
        "Wood",
        "Ceramics",
        "Stone",
        "Leather",
        "Metals (e.g., copper, silver, iron)",
        "Fabric (cotton, silk, jute, khadi)",
        "Glass",
        "Paper",
        "Bamboo",
        t('other_option', page_language)
    ]
    selected_material = st.selectbox("Materials", material_options)
    if selected_material == t('other_option', page_language):
        prompt_fields['materials'] = st.text_input(t('other_specify', page_language), placeholder=t('prompt_placeholder_materials', page_language))
    else:
        prompt_fields['materials'] = selected_material

    # Region Dropdown with large combined list
    selected_region = st.selectbox("Region", EXTENDED_REGION_OPTIONS)
    if selected_region == t('other_option', page_language):
        prompt_fields['region'] = st.text_input(t('other_specify', page_language), placeholder=t('prompt_placeholder_region', page_language))
    else:
        prompt_fields['region'] = selected_region

    # --- NEW: Size selector block (integer + units) ---
    st.markdown("**" + t('select_size', page_language) + "**")
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        size_value = st.number_input(t('enter_size', page_language), min_value=1, max_value=200, value=3, step=1, key='size_value_workflow1')
    with col_s2:
        size_unit = st.radio(t('unit_label', page_language), [t('unit_option_inches', page_language), t('unit_option_cm', page_language)], index=0, key='size_unit_workflow1')
    # Save both integer and combined size string
    prompt_fields['size_value'] = int(size_value)
    prompt_fields['size_unit'] = size_unit
    prompt_fields['size'] = f"{prompt_fields['size_value']} {prompt_fields['size_unit']}"

    prompt_fields['tone'] = st.selectbox("Tone", ["rustic", "festive", "modern", "cultural", "elegant", "minimalist", t('other_option', page_language)])
    if prompt_fields['tone'] == t('other_option', page_language):
        prompt_fields['tone'] = st.text_input(t('other_specify', page_language), placeholder=t('prompt_placeholder_tone', page_language), key='tone_other_1')

    prompt_fields['description'] = st.text_area("Description (Optional)", placeholder=t('prompt_placeholder_description', page_language))
    
    # Store fields in session state for cross-button use
    st.session_state.current_prompt_fields = prompt_fields

    if st.button(t('generate_content_button', page_language), key="gen_content", use_container_width=True, type="primary"):
        if prompt_fields.get('title') or prompt_fields.get('region'):
            st.session_state.ai_results = None
            st.session_state.generated_image = None
            st.session_state.uploaded_image = None
            spinner_text = t('spinner_text_content', page_language).format(caption_lang=caption_language)
            with st.spinner(spinner_text):
                st.session_state.ai_results = get_ai_content(prompt_fields, caption_language)
            if st.session_state.ai_results:
                st.session_state.story_is_ready = True
                st.success(t('content_ready', page_language) + " Now you can create an image to match.")
        else:
            st.warning(t('prompt_warning', page_language))

    if st.session_state.story_is_ready:
        st.markdown("---")
        if st.button(t('generate_image_button', page_language), key="gen_image", use_container_width=True):
            image_prompt_parts = []
            if prompt_fields.get('description'):
                image_prompt_parts.append(prompt_fields['description'])
            if prompt_fields.get('title'):
                image_prompt_parts.append(f"Product: {prompt_fields['title']}")
            if prompt_fields.get('materials'):
                image_prompt_parts.append(f"Materials: {prompt_fields['materials']}")
            if prompt_fields.get('region'):
                image_prompt_parts.append(f"Region: {prompt_fields['region']}")
            if prompt_fields.get('tone'):
                image_prompt_parts.append(f"Tone: {prompt_fields['tone']}")
            if prompt_fields.get('size'):
                image_prompt_parts.append(f"Size: {prompt_fields['size']}")
            
            image_prompt = ", ".join(image_prompt_parts)
            
            if not image_prompt:
                image_prompt = "A piece of Indian artisan craft" # Default fallback
            
            with st.spinner(t('spinner_text_image', page_language)):
                st.session_state.generated_image = generate_image_with_imagen(image_prompt)
            if st.session_state.generated_image:
                st.success("Image generated! See your full marketing kit below.")

# --- WORKFLOW 2: UPLOAD IMAGE & GENERATE CONTENT ---
elif workflow == t('workflow_option_2', page_language):
    caption_language = st.sidebar.selectbox(
        t('caption_language_label', page_language),
        content_language_list,
        help=t('caption_language_help', page_language)
    )

    st.subheader(t('upload_image_subheader', page_language))
    uploaded_file = st.file_uploader(t('image_uploader_label', page_language), type=["png", "jpg", "jpeg"], help=t('image_uploader_help', page_language))

    if uploaded_file is not None:
        try:
            st.session_state.uploaded_image = Image.open(uploaded_file)
        except Exception as e:
            st.error("Error opening uploaded image: " + str(e))
            st.session_state.uploaded_image = None
    else:
        st.session_state.uploaded_image = None 

    st.subheader(t('prompt_subheader', page_language))
    prompt_fields = {}
    prompt_fields['title'] = st.text_input("Title", placeholder=t('prompt_placeholder_title', page_language))
    
    # ✅ Expanded Materials Dropdown for upload workflow
    material_options_upload = [
        "Terracotta clay",
        "Brass",
        "Wood",
        "Ceramics",
        "Stone",
        "Leather",
        "Metals (e.g., copper, silver, iron)",
        "Fabric (cotton, silk, jute, khadi)",
        "Glass",
        "Paper",
        "Bamboo",
        t('other_option', page_language)
    ]
    selected_material_upload = st.selectbox("Materials", material_options_upload, key='materials_upload')
    if selected_material_upload == t('other_option', page_language):
        prompt_fields['materials'] = st.text_input(t('other_specify', page_language), placeholder=t('prompt_placeholder_materials', page_language), key='materials_upload_text')
    else:
        prompt_fields['materials'] = selected_material_upload

    # Region Dropdown with combined list for upload workflow
    selected_region_upload = st.selectbox("Region", EXTENDED_REGION_OPTIONS, key='region_upload')
    if selected_region_upload == t('other_option', page_language):
        prompt_fields['region'] = st.text_input(t('other_specify', page_language), placeholder=t('prompt_placeholder_region', page_language), key='region_upload_text')
    else:
        prompt_fields['region'] = selected_region_upload

    # --- NEW: Size selector for uploaded-image workflow ---
    st.markdown("**" + t('select_size', page_language) + "**")
    col_s1_u, col_s2_u = st.columns([1, 1])
    with col_s1_u:
        size_value_u = st.number_input(t('enter_size', page_language), min_value=1, max_value=200, value=3, step=1, key='size_value_workflow2')
    with col_s2_u:
        size_unit_u = st.radio(t('unit_label', page_language), [t('unit_option_inches', page_language), t('unit_option_cm', page_language)], index=0, key='size_unit_workflow2')
    prompt_fields['size_value'] = int(size_value_u)
    prompt_fields['size_unit'] = size_unit_u
    prompt_fields['size'] = f"{prompt_fields['size_value']} {prompt_fields['size_unit']}"

    prompt_fields['tone'] = st.selectbox("Tone", ["rustic", "festive", "modern", "cultural", "elegant", "minimalist", t('other_option', page_language)], key='tone_upload')
    if prompt_fields['tone'] == t('other_option', page_language):
        prompt_fields['tone'] = st.text_input(t('other_specify', page_language), placeholder=t('prompt_placeholder_tone', page_language), key='tone_upload_text')

    prompt_fields['description'] = st.text_area("Description (Optional)", placeholder=t('prompt_placeholder_description', page_language), key='description_upload')

    if st.button(t('generate_content_button', page_language), key="gen_content_upload", use_container_width=True, type="primary"):
        if st.session_state.uploaded_image and (prompt_fields.get('title') or prompt_fields.get('region')):
            st.session_state.ai_results = None
            st.session_state.generated_image = None
            spinner_text = t('spinner_text_content', page_language).format(caption_lang=caption_language)
            with st.spinner(spinner_text):
                st.session_state.ai_results = get_ai_content(prompt_fields, caption_language)
            if st.session_state.ai_results:
                st.session_state.story_is_ready = True
                st.success(t('content_ready', page_language))
        else:
            st.warning(t('upload_warning', page_language))

# --- WORKFLOW 3: MARKET TRENDS ---
elif workflow == t('workflow_option_3', page_language):
    st.subheader(t('trends_subheader', page_language))
    trends_language = st.selectbox(t('trends_language_label', page_language), content_language_list, key='trends_lang')
    trends_region = st.text_input("Region", placeholder=t('prompt_placeholder_region', page_language), key='trends_region')
    craft_type = st.text_input(t('trends_label', page_language), placeholder=t('trends_placeholder', page_language))
    if st.button(t('trends_button', page_language), key="trends", use_container_width=True):
        if craft_type and trends_region:
            clear_results()
            st.session_state.story_is_ready = False
            spinner_text = t('spinner_text_trends', page_language).format(trends_lang=trends_language)
            with st.spinner(spinner_text):
                st.session_state.market_trends = get_market_trends(trends_region, trends_language, craft_type)
        else:
            st.warning(t('trends_warning', page_language))

# --- WORKFLOW 4: GROWTH PLANNER ---
elif workflow == t('workflow_option_4', page_language):
    st.subheader(t('planner_subheader', page_language))
    plan_language = st.selectbox(t('plan_language_label', page_language), content_language_list, key='plan_lang')
    planner_region = st.text_input("Region", placeholder=t('prompt_placeholder_region', page_language), key='planner_region')
    platforms = st.multiselect(t('planner_platform_label', page_language), ["Instagram", "Facebook", "X"])
    craft_type = st.text_input(t('planner_craft_label', page_language), placeholder=t('planner_craft_placeholder', page_language))
    target_audience = st.text_input(t('planner_audience_label', page_language), placeholder=t('planner_audience_placeholder', page_language))
    if st.button(t('planner_button', page_language), key="planner", use_container_width=True):
        if platforms and craft_type and planner_region:
            clear_results()
            st.session_state.story_is_ready = False
            spinner_text = t('spinner_text_planner', page_language).format(plan_lang=plan_language)
            with st.spinner(spinner_text):
                st.session_state.growth_plan = get_growth_plan(planner_region, plan_language, platforms, craft_type, target_audience)
        else:
            st.warning(t('planner_warning', page_language))

# --- 9. MAIN CONTENT DISPLAY ---
if st.session_state.get('ai_results'):
    st.markdown("---")
    st.header(t('results_header', page_language))
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.session_state.generated_image:
            st.image(st.session_state.generated_image, caption=t('ai_image_caption', page_language), use_container_width=True)
        elif st.session_state.uploaded_image:
            st.image(st.session_state.uploaded_image, caption=t('user_image_caption', page_language), use_container_width=True)
        else:
            st.info("Generate or upload an image to see it here.")
            
    with col2:
        st.subheader(t('story_header', page_language))
        st.write(st.session_state.ai_results["story"])

    st.markdown("---")
    st.subheader(t('social_header', page_language))
    insta, twit, face = st.tabs(["Instagram", "Twitter / X", "Facebook"])
    with insta:
        st.markdown(f"{t('caption_suggestion', page_language)}")
        st.markdown(st.session_state.ai_results["instagram_post"]["caption"])
        st.markdown(f"{t('hashtags', page_language)}")
        st.code(st.session_state.ai_results["instagram_post"]["hashtags"])
    with twit:
        st.markdown(f"{t('tweet_suggestion', page_language)}")
        st.markdown(st.session_state.ai_results["twitter_post"]["text"])
    with face:
        st.markdown(f"{t('caption_suggestion', page_language)}")
        st.markdown(st.session_state.ai_results["facebook_post"]["caption"])
        st.markdown(f"{t('hashtags', page_language)}")
        st.code(st.session_state.ai_results["facebook_post"]["hashtags"])

elif st.session_state.get('market_trends'):
    st.header(t('trends_results_header', page_language))
    st.markdown(st.session_state.market_trends)

elif st.session_state.get('growth_plan'):
    st.header(t('planner_results_header', page_language))
    st.markdown(st.session_state.growth_plan)

else:
    st.info(t('info_box', page_language))