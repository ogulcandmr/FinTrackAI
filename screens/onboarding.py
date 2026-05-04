import streamlit as st
from utils.supabase_utils import save_onboarding_data, get_onboarding_data

def risk_onboarding():
    st.subheader("🎯 Determine Your Investor Profile")
    st.markdown("Please fill out the survey below so FinTrack AI can offer you personalized recommendations.")
    
    existing_data = {}
    if st.session_state.user:
        fetched = get_onboarding_data(st.session_state.user['id'])
        if fetched:
            existing_data = fetched

    exp_map = {
        "Hiç yok": "None", "1-3 Yıl": "1-3 Years", "3-5 Yıl": "3-5 Years", "5 Yıl +": "5+ Years"
    }
    risk_map = {
        "Çok Düşük": "Very Low", "Düşük": "Low", "Orta": "Medium", "Yüksek": "High", "Çok Yüksek": "Very High"
    }
    obj_map = {
        "Temettü Emekliliği": "Dividend Retirement", "Sermaye Kazancı": "Capital Gain", 
        "Kısa Vadeli Kar": "Short-Term Profit", "Enflasyondan Korunma": "Inflation Protection"
    }

    def_age = existing_data.get("age") if existing_data.get("age") is not None else 25
    
    db_exp = existing_data.get("experience")
    def_exp = exp_map.get(db_exp, db_exp) if db_exp else "None"
    
    db_risk = existing_data.get("risk_tolerance")
    def_risk = risk_map.get(db_risk, db_risk) if db_risk else "Medium"
    
    db_obj = existing_data.get("objective") or []
    def_obj = [obj_map.get(o, o) for o in db_obj]
    
    exp_options = ["None", "1-3 Years", "3-5 Years", "5+ Years"]
    risk_options = ["Very Low", "Low", "Medium", "High", "Very High"]
    obj_options = ["Dividend Retirement", "Capital Gain", "Short-Term Profit", "Inflation Protection"]
    
    exp_index = exp_options.index(def_exp) if def_exp in exp_options else 0

    with st.form("risk_form"):
        age = st.number_input("Your Age", min_value=18, max_value=100, value=def_age)
        experience = st.selectbox("Your Investment Experience", exp_options, index=exp_index)
        risk_tolerance = st.select_slider(
            "📈 Your Risk Tolerance",
            options=risk_options,
            value=def_risk
        )
        # Ensure default objectives are valid options
        valid_def_obj = [obj for obj in def_obj if obj in obj_options]
        objective = st.multiselect(
            "Your Investment Objectives",
            obj_options,
            default=valid_def_obj
        )
        
        submit = st.form_submit_button("Save Profile")
        
        if submit:
            user_id = st.session_state.user['id'] if st.session_state.user else None
            if user_id:
                profile_data = {
                    "age": age,
                    "experience": experience,
                    "risk_tolerance": risk_tolerance,
                    "objective": objective
                }
                # Veritabanına kaydet ve SADECE başarılıysa tamamlandı say
                saved = save_onboarding_data(user_id, profile_data)
                if saved:
                    st.session_state.onboarding_complete = True
                    st.success("✅ Your profile has been successfully saved!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save profile. Please try again.")
