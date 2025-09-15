🌟 Artisans GenAI
<p align="center"> <img src="logo.gif" alt="Artisans GenAI Logo" width="200"/> </p>
🎨 Introduction

Artisans GenAI is a Streamlit-based web application that integrates Google Generative AI with Firebase authentication to empower artisans and creators.

It enables authenticated users to:
✨ Interact with AI models
✨ Explore generative design ideas
✨ Manage and schedule creative sessions

<p align="center"> <img src="background.jpg" alt="Artisans GenAI Background" width="600"/> </p>
📑 Table of Contents

Introduction

Preview

Features

Installation

Usage

Dependencies

Configuration

Examples

Troubleshooting

Contributors

License

👀 Preview

Here’s a sneak peek of the app in action:

<p align="center"> <img src="logo.gif" alt="Login Page" width="220"/> <br/> <em>🔐 Login page with Firebase authentication</em> </p> <p align="center"> <img src="background.jpg" alt="Dashboard UI" width="600"/> <br/> <em>🎨 Dashboard with custom background and artisan-friendly UI</em> </p>

👉 Once you run frontend.py, you can add real screenshots of the app’s interface to replace these placeholders. Recommended sections to capture:

Login page (Firebase Auth in Streamlit)

Main dashboard with AI interaction

Calendar view (from streamlit-calendar)

🚀 Features

🔐 User Authentication with Firebase

🤖 Generative AI Models powered by Google

🖼️ Custom UI with artisan branding

🗓️ Calendar Scheduling for collaboration

🎛️ Streamlit-powered Interface

🛠️ Installation
git clone https://github.com/jatin-encrypted/Artisans-GenAI.git
cd Artisans-GenAI
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

💻 Usage
streamlit run frontend.py


App runs on: http://localhost:8501

📦 Dependencies

From requirements.txt:

streamlit – UI framework

google-generativeai, vertexai – AI integration

firebase-admin, pyrebase4 – Firebase auth & DB

streamlit-authenticator – Login system

streamlit-calendar – Schedule manager

Pillow, PyYAML – Utilities

⚙️ Configuration

Firebase Project Setup

Google Cloud APIs Setup

Add secrets (Firebase key, Google credentials)

🧩 Examples

Generate design concepts with AI

Organize artisan workshops with calendar integration

Customize UI branding with background.jpg & logo.gif

🛠️ Troubleshooting

Login issues → Check Firebase config

API errors → Ensure Google Cloud APIs are enabled

Streamlit errors → Run pip install -r requirements.txt

👨‍💻 Contributors

@jatin-encrypted
@Tvaibhav06

📜 License

MIT License – see LICENSE