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

def save_user_data(db, uid: str, data: Dict[str, Any], token: str = None):
    """Saves user data (preferences, reminders) to the Realtime Database.
    
    Args:
        db: Firebase database instance
        uid: User ID
        data: Data to save
        token: Firebase auth token (idToken) - required for authenticated access
    """
    try:
        if token:
            # Use token for authenticated access
            db.child("users").child(uid).set(data, token=token)
        else:
            # Fallback without token (may fail if rules require auth)
            db.child("users").child(uid).set(data)
        return True
    except Exception as e:
        st.error(f"Database Error: Failed to save user data. {e}")
        return False

def load_user_data(db, uid: str, token: str = None) -> Dict[str, Any]:
    """Loads user data from the Realtime Database.
    
    Args:
        db: Firebase database instance
        uid: User ID
        token: Firebase auth token (idToken) - required for authenticated access
    """
    try:
        if token:
            # Use token for authenticated access
            data = db.child("users").child(uid).get(token=token).val()
        else:
            # Fallback without token (may fail if rules require auth)
            data = db.child("users").child(uid).get().val()
        return data if data else {}
    except Exception as e:
        st.error(f"Database Error: Failed to load user data. {e}")
        return {}
    
def refresh_token(auth, refresh_token: str):
    """Refreshes an expired Firebase auth token.
    
    Args:
        auth: Firebase auth instance
        refresh_token: The refresh token from a previous login
        
    Returns:
        Tuple of (refreshed_user_info, error_message)
    """
    try:
        user = auth.refresh(refresh_token)
        return user, None
    except Exception as e:
        try:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
        except (IndexError, KeyError, json.JSONDecodeError):
            error_message = str(e)
        return None, error_message

def verify_token(auth, id_token: str):
    """Verifies if a Firebase ID token is still valid.
    
    Args:
        auth: Firebase auth instance
        id_token: The ID token to verify
        
    Returns:
        Tuple of (user_info, error_message)
    """
    try:
        # Get account info using the token
        account_info = auth.get_account_info(id_token)
        if account_info and 'users' in account_info and len(account_info['users']) > 0:
            user_data = account_info['users'][0]
            # Reconstruct user info similar to login response
            user_info = {
                'localId': user_data.get('localId'),
                'email': user_data.get('email'),
                'idToken': id_token,
                'refreshToken': None  # We don't get refresh token from account info
            }
            return user_info, None
        return None, "Invalid token"
    except Exception as e:
        try:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
        except (IndexError, KeyError, json.JSONDecodeError):
            error_message = str(e)
        return None, error_message