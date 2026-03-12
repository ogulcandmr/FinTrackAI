import re
from supabase import create_client, Client
import streamlit as st

# Supabase URL ve Key bilgileri .streamlit/secrets.toml dosyasından çekilir
url = st.secrets.get("SUPABASE_URL", "")
key = st.secrets.get("SUPABASE_KEY", "")

def get_supabase_client() -> Client:
    if not url or not key:
        return None
    try:
        # Client'ı her seferinde baştan yaratıyoruz (Server disconnected hatasını önlemek için)
        client = create_client(url, key)
        
        # Eğer daha önce giriş yapıldıysa, auth token'ı yeni client'a aktarıyoruz (RLS'yi geçmek için)
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
        return "Geçersiz e-posta formatı."
    try:
        supabase = get_supabase_client()
        if not supabase: return "Bağlantı kurulamadı."
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
            return "Hatalı e-posta veya şifre."
        return err_msg

def sign_up(email, password):
    if not is_valid_email(email):
        return "Geçersiz e-posta formatı."
    try:
        supabase = get_supabase_client()
        if not supabase: return "Bağlantı kurulamadı."
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
            return "Bu e-posta adresi zaten kayıtlı."
        return err_msg

def check_onboarding_status(user_id):
    try:
        supabase = get_supabase_client()
        if not supabase: return False
        
        # Kullanıcının profiles tablosunu okuyoruz
        response = supabase.table("profiles").select("onboarding_complete").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0].get("onboarding_complete", False)
        return False
    except Exception as e:
        print(f"Onboarding durum kontrol hatası: {e}")
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
        print(f"Onboarding verisi cekme hatasi: {e}")
        return None

def save_onboarding_data(user_id, profile_data):
    try:
        supabase = get_supabase_client()
        if not supabase: return False
        
        # Veritabanı "profiles" tablosuna kullanıcının anketini kaydeder.
        payload = {
            "id": user_id,
            "onboarding_complete": True,
            "age": profile_data.get("age"),
            "experience": profile_data.get("experience"),
            "risk_tolerance": profile_data.get("risk_tolerance"),
            "objective": profile_data.get("objective")
        }
        
        # Daha güvenli upsert:
        res = supabase.table("profiles").upsert(payload).execute()
        return True
    except Exception as e:
        print(f"Onboarding kaydetme hatası: {e}")
        return False
