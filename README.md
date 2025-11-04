# 🌟 Artisans GenAI

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-blue">
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white">
  <a href="#-license"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-green.svg"></a>
</p>

🔗 **Live App:** [https://artisansai-studios.streamlit.app/](https://artisansai-studios.streamlit.app/)

<p align="center">
  <img src="logo.gif" alt="Artisans GenAI Logo" width="200"/>
</p>

Empowering artisans and creators with AI-assisted ideation, content generation, image creation, and calendar-based reminders — built with **Streamlit**, **Firebase**, **Vertex AI**, and **Google Generative AI (Gemini 2.5 Flash)**.


## 📑 Table of Contents
- [🌟 Artisans GenAI](#-artisans-genai)
  - [📑 Table of Contents](#-table-of-contents)
  - [🎨 Introduction](#-introduction)
  - [🚀 Features](#-features)
  - [🏗️ Architecture](#️-architecture)
  - [🗂️ Project Structure](#️-project-structure)
  - [🛠️ Installation](#️-installation)
  - [⚙️ Configuration](#️-configuration)
    - [1. Firebase Setup](#1-firebase-setup)
    - [2. Google Generative / Vertex AI](#2-google-generative--vertex-ai)
    - [3. Streamlit Secrets (required)](#3-streamlit-secrets-required)
  - [🔐 Environment Variables / Secrets](#-environment-variables--secrets)
  - [💻 Usage](#-usage)
  - [🧪 Development \& Testing](#-development--testing)
  - [🛠️ Troubleshooting](#️-troubleshooting)
  - [🗺️ Roadmap](#️-roadmap)
  - [🤝 Contributing](#-contributing)
  - [👨‍💻 Contributors](#-contributors)
  - [📜 License](#-license)

---

## 🎨 Introduction
Artisans GenAI blends multilingual UI, AI content generation, optional AI image generation, and an events calendar with reminders. Authenticated users can:
- Generate stories and social captions from prompts or uploaded images.
- Discover market trends and create growth plans.
- Track craft events and set reminders.

---

## 🚀 Features
- 🔐 Firebase-backed email/password auth (Pyrebase)
- 🤖 Google Generative AI (Gemini 2.5 Flash) for text/JSON output
- 🖼️ Vertex AI ImageGenerationModel (Imagen) for 1:1 images
- 🌐 Multilingual UI (English, Hindi; extendable)
- 📅 Events calendar with reminders and preferences
- 🎛️ Config-driven via Streamlit secrets
- 🎨 Themed Streamlit UI with logo/favicon/background support

---

## 🏗️ Architecture
1. frontend.py — Streamlit UI, routing, session state, widgets, calendar, reminders
2. backend.py — Translations, AI helpers (Gemini/Vertex), events data, auth/bootstrap
3. firebase_auth.py — Firebase initialization and helpers (sign up, login, save/load user data)
4. .streamlit/config.toml — Theme
5. .streamlit/secrets.toml — Secrets (NOT COMMITED)
6. requirements.txt — Python dependencies

---

## 🗂️ Project Structure
```

artisans_ai/
frontend.py
backend.py
firebase_auth.py
.streamlit/
config.toml
secrets.toml  (gitignored; contains your keys)
requirements.txt
README.md
logo.gif        (app logo, used in UI)
background.jpg  (optional; background image)

````

---

## 🛠️ Installation
```bash
git clone https://github.com/jatin-encrypted/Artisans-GenAI.git
cd Artisans-GenAI

python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows (Powershell)
venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt
````

---

## ⚙️ Configuration

### 1. Firebase Setup

1. Create a Firebase project.
2. Enable Authentication (Email/Password).
3. Create a Realtime Database (or ensure databaseURL exists in your web config).
4. From Project Settings → Your apps (Web) copy the Web app config (apiKey, authDomain, databaseURL, etc.).
5. Paste those values under [firebase_config] in .streamlit/secrets.toml (see Streamlit Secrets below).

### 2. Google Generative / Vertex AI

1. Create/choose a Google Cloud project.
2. Enable: Vertex AI API and Generative Language API.
3. Create a Service Account with Vertex permissions and generate a JSON key.
4. Put the raw JSON into GCP_SERVICE_ACCOUNT_JSON in .streamlit/secrets.toml.
5. Also set GEMINI_API_KEY for google-generativeai (used for text).
6. Vertex region used in code: us-central1.

### 3. Streamlit Secrets (required)

Create .streamlit/secrets.toml. The keys below match how the code reads them.

```toml
# Top-level API keys used by backend.py
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

# Provide raw JSON of your service account as a string (backend.py checks 'GCP_SERVICE_ACCOUNT_JSON')
GCP_SERVICE_ACCOUNT_JSON = """
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "xxx",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@your-project-id.iam.gserviceaccount.com",
  "client_id": "1234567890",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account%40your-project-id.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
"""

[firebase_config]
apiKey = "YOUR_FIREBASE_WEB_API_KEY"
authDomain = "yourapp.firebaseapp.com"
databaseURL = "https://yourapp-default-rtdb.firebaseio.com"
projectId = "yourapp"
storageBucket = "yourapp.appspot.com"
messagingSenderId = "1234567890"
appId = "1:1234567890:web:abc123"
measurementId = "G-XXXXXXX" # optional

[firebase_database]
databaseURL = "https://yourapp-default-rtdb.firebaseio.com/"
```

Notes:

* Do not commit secrets.toml.
* backend.py uses GEMINI_API_KEY and GCP_SERVICE_ACCOUNT_JSON.
* firebase_auth.py expects [firebase_config] for Pyrebase initialization.

---

## 🔐 Environment Variables / Secrets

Alternative to secrets.toml (if you prefer env vars):

```
# Firebase web config (map to your pyrebase config)
FIREBASE_API_KEY=...
FIREBASE_AUTH_DOMAIN=yourapp.firebaseapp.com
FIREBASE_DATABASE_URL=https://yourapp-default-rtdb.firebaseio.com
FIREBASE_PROJECT_ID=yourapp
FIREBASE_STORAGE_BUCKET=yourapp.appspot.com
FIREBASE_MESSAGING_SENDER_ID=1234567890
FIREBASE_APP_ID=1:1234567890:web:abc123

# Google Generative AI (Gemini) and Vertex
GEMINI_API_KEY=...
GCP_SERVICE_ACCOUNT_JSON='{"type":"service_account", ... }'
VERTEX_LOCATION=us-central1
```

If you use env vars, load them into st.secrets at runtime (or adapt firebase_auth.py to read envs directly).

---

## 💻 Usage

Run the Streamlit app:

```bash
streamlit run frontend.py
```

Then:

1. Open the local URL from the terminal.
2. Register or log in (email/password).
3. Pick a workflow from the sidebar and generate content or set reminders.

---

## 🧪 Development & Testing

Basic checks:

* Invalid login shows a friendly error.
* Valid login persists session.
* “Generate Marketing Kit” returns story/captions JSON rendered in UI.
* “Discover Market Trends” and “Growth Plan” return markdown.
* Calendar renders and reminders toggle/save to Realtime DB.

Optional rebuild:

```bash
pip install --force-reinstall -r requirements.txt
```

---

## 🛠️ Troubleshooting

* Auth fails: confirm [firebase_config] matches your Firebase Web config.
* Vertex/Gemini errors: ensure APIs are enabled and billing is active; verify GEMINI_API_KEY and service account permissions.
* Secrets not loading: ensure .streamlit/secrets.toml exists and keys match names above.
* Background/logo missing: app will warn if background.jpg is absent; logo.gif is optional but recommended.

---

## 🗺️ Roadmap

* Persistent content save/export
* More languages
* Rich event sources (remote)
* Fine-grained role access

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch: git checkout -b feat/your-feature
3. Commit: git commit -m "feat: add your feature"
4. Push: git push origin feat/your-feature
5. Open Pull Request

---

## 👨‍💻 Contributors

* [@jatin-encrypted](https://github.com/jatin-encrypted)
* [@Tvaibhav06](https://github.com/Tvaibhav06)
* [@Advikmangal](https://github.com/Advikmangal)
* [@Tanishka290305](https://github.com/Tanishka290305)
* [@nakshtra3108](https://github.com/nakshtra3108)

---

## 📜 License

MIT License

Copyright (c) 2025 Artisans GenAI contributors

```
```
