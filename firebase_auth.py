import streamlit as st
import pyrebase
import json
from typing import Dict, Any

# Use st.cache_resource to initialize Firebase only once
@st.cache_resource
def init_firebase():
    """Initializes and returns the Pyrebase app object."""
    config = dict(st.secrets["firebase_config"])
    firebase = pyrebase.initialize_app(config)
    return firebase

def sign_up(auth, email, password):
    """Signs up a new user and returns user info or an error message."""
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user, None
    except Exception as e:
        try:
            # Firebase returns errors in a specific JSON format
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
        except (IndexError, KeyError, json.JSONDecodeError):
            error_message = str(e)
        return None, error_message

def login(auth, email, password):
    """Logs in an existing user and returns user info or an error message."""
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user, None
    except Exception as e:
        try:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
        except (IndexError, KeyError, json.JSONDecodeError):
            error_message = str(e)
        return None, error_message

def save_user_data(db, uid: str, data: Dict[str, Any]):
    """Saves user data (preferences, reminders) to the Realtime Database."""
    try:
        db.child("users").child(uid).set(data)
        return True
    except Exception as e:
        st.error(f"Database Error: Failed to save user data. {e}")
        return False

def load_user_data(db, uid: str) -> Dict[str, Any]:
    """Loads user data from the Realtime Database."""
    try:
        data = db.child("users").child(uid).get().val()
        return data if data else {}
    except Exception as e:
        st.error(f"Database Error: Failed to load user data. {e}")
        return {}