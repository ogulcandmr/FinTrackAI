import re
from supabase import create_client, Client
import streamlit as st

# Supabase URL and Key are loaded from .streamlit/secrets.toml
url = st.secrets.get("SUPABASE_URL", "")
key = st.secrets.get("SUPABASE_KEY", "")

def get_supabase_client() -> Client:
    if not url or not key:
        return None
    try:
        # Create client fresh each time (to prevent Server disconnected errors)
        client = create_client(url, key)

        # If previously logged in, transfer auth token to new client (to pass RLS)
        if 'supabase_session' in st.session_state and st.session_state.supabase_session:
            try:
                client.auth.set_session(
                    st.session_state.supabase_session['access_token'],
                    st.session_state.supabase_session['refresh_token']
                )
            except Exception as e:
                print(f"Session set error: {e}")

        return client
    except Exception as e:
        print(f"Supabase Client Error: {e}")
        return None

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def sign_in(email, password):
    if not is_valid_email(email):
        return "Invalid email format."
    try:
        supabase = get_supabase_client()
        if not supabase: return "Could not establish connection."
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.session:
            st.session_state.supabase_session = {
                'access_token': response.session.access_token,
                'refresh_token': response.session.refresh_token
            }
        return response
    except Exception as e:
        err_msg = str(e)
        if "Invalid login credentials" in err_msg:
            return "Incorrect email or password."
        return err_msg

def sign_up(email, password):
    if not is_valid_email(email):
        return "Invalid email format."
    try:
        supabase = get_supabase_client()
        if not supabase: return "Could not establish connection."
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.session:
            st.session_state.supabase_session = {
                'access_token': response.session.access_token,
                'refresh_token': response.session.refresh_token
            }
        return response
    except Exception as e:
        err_msg = str(e)
        if "User already registered" in err_msg:
            return "This email address is already registered."
        return err_msg

def check_onboarding_status(user_id):
    try:
        supabase = get_supabase_client()
        if not supabase: return False

        # Read the user's profiles table
        response = supabase.table("profiles").select("onboarding_complete").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0].get("onboarding_complete", False)
        return False
    except Exception as e:
        print(f"Onboarding status check error: {e}")
        return False

def get_onboarding_data(user_id):
    try:
        supabase = get_supabase_client()
        if not supabase: return None
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Onboarding data fetch error: {e}")
        return None

def save_onboarding_data(user_id, profile_data):
    try:
        supabase = get_supabase_client()
        if not supabase: return False

        # Save user's survey to the "profiles" table in the database.
        payload = {
            "id": user_id,
            "onboarding_complete": True,
            "age": profile_data.get("age"),
            "experience": profile_data.get("experience"),
            "risk_tolerance": profile_data.get("risk_tolerance"),
            "objective": profile_data.get("objective")
        }

        # Safer upsert:
        res = supabase.table("profiles").upsert(payload).execute()
        return True
    except Exception as e:
        print(f"Onboarding save error: {e}")
        return False

# --- PORTFOLIO (Data Layer and Wallet Management) ---
# Local SQLite is used; Supabase portfolio schema is not required. Works at record time, live price comes from yfinance/ccxt.

from utils.portfolio_store import insert as _local_insert, select_by_user as _local_select, delete as _local_delete


def portfolio_insert(user_id, asset_id, purchase_date, price, quantity):
    """Adds a new position to the portfolio. Saves to local SQLite."""
    value = str(asset_id).strip().upper()
    date_str = str(purchase_date)[:10] if purchase_date else ""
    row, err = _local_insert(user_id, value, date_str, float(price), float(quantity))
    if err:
        return None, err
    return row, None


def portfolio_select_by_user(user_id):
    """Returns all portfolio records for the user (from local store)."""
    return _local_select(user_id)


def portfolio_delete(record_id, user_id):
    """Deletes the specified portfolio record."""
    ok, err = _local_delete(record_id, user_id)
    if err:
        return False, err
    return True, None
