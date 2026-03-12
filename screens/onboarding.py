import streamlit as st
from utils.supabase_utils import save_onboarding_data, get_onboarding_data

def risk_onboarding():
    st.subheader("🎯 Yatırımcı Profilinizi Belirleyin")
    st.markdown("FinTrack AI'nın size özel öneriler sunabilmesi için lütfen aşağıdaki anketi doldurun.")
    
    existing_data = {}
    if st.session_state.user:
        fetched = get_onboarding_data(st.session_state.user['id'])
        if fetched:
            existing_data = fetched

    def_age = existing_data.get("age") if existing_data.get("age") is not None else 25
    def_exp = existing_data.get("experience") if existing_data.get("experience") else "Hiç yok"
    def_risk = existing_data.get("risk_tolerance") if existing_data.get("risk_tolerance") else "Orta"
    def_obj = existing_data.get("objective") if existing_data.get("objective") else []
    
    exp_options = ["Hiç yok", "1-3 Yıl", "3-5 Yıl", "5 Yıl +"]
    risk_options = ["Çok Düşük", "Düşük", "Orta", "Yüksek", "Çok Yüksek"]
    obj_options = ["Temettü Emekliliği", "Sermaye Kazancı", "Kısa Vadeli Kar", "Enflasyondan Korunma"]
    
    exp_index = exp_options.index(def_exp) if def_exp in exp_options else 0

    with st.form("risk_form"):
        age = st.number_input("Yaşınız", min_value=18, max_value=100, value=def_age)
        experience = st.selectbox("Yatırım Deneyiminiz", exp_options, index=exp_index)
        risk_tolerance = st.select_slider(
            "📈 Risk Algınız",
            options=risk_options,
            value=def_risk
        )
        # Ensure default objectives are valid options
        valid_def_obj = [obj for obj in def_obj if obj in obj_options]
        objective = st.multiselect(
            "Yatırım Hedefleriniz",
            obj_options,
            default=valid_def_obj
        )
        
        submit = st.form_submit_button("Profili Kaydet")
        
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
                    st.success("✅ Profiliniz başarıyla kaydedildi!")
                    st.rerun()
                else:
                    st.error("❌ Profil kaydedilemedi. Lütfen tekrar deneyin.")
