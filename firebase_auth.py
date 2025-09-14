import streamlit as st
# REPLACED: import pyrebase
try:
    import pyrebase  # Works if pyrebase4 installed (it registers as pyrebase)
except ImportError as _e1:
    try:
        import pyrebase4 as pyrebase  # Fallback name (rarely needed)
    except ImportError as _e2:
        raise ImportError(
            "Neither 'pyrebase' nor 'pyrebase4' is installed. "
            "Install with: pip install pyrebase4"
        ) from _e2
import json
from typing import Dict, Any

def firebase_lib_version() -> str:
    """Returns the detected pyrebase library version (for debugging)."""
    try:
        import importlib.metadata as im
        for dist_name in ("pyrebase4", "pyrebase"):
            try:
                return f"{dist_name} {im.version(dist_name)}"
            except im.PackageNotFoundError:
                continue
    except Exception:
        pass
    return "unknown"

@st.cache_resource
def init_firebase():
    """Initializes and returns the Pyrebase app object."""
    config = dict(st.secrets["firebase_config"])
    try:
        firebase = pyrebase.initialize_app(config)
    except Exception as e:
        st.error(
            "Failed to initialize Firebase. "
            "If you see gcloud/pkg_resources errors, install a maintained fork: "
            "pip install --upgrade setuptools && pip install --upgrade pyrebase4"
        )
        raise
    st.sidebar.caption(f"Firebase client: {firebase_lib_version()}")
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