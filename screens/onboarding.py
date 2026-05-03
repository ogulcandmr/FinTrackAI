import streamlit as st
from utils.supabase_utils import save_onboarding_data, get_onboarding_data

_LEGACY_EXP = {
    "Hiç yok": "None",
    "1-3 Yıl": "1-3 Years",
    "3-5 Yıl": "3-5 Years",
    "5 Yıl +": "5+ Years",
}
_LEGACY_RISK = {
    "Çok Düşük": "Very Low",
    "Düşük": "Low",
    "Orta": "Medium",
    "Yüksek": "High",
    "Çok Yüksek": "Very High",
}
_LEGACY_OBJ = {
    "Temettü Emekliliği": "Dividend Retirement",
    "Sermaye Kazancı": "Capital Gains",
    "Kısa Vadeli Kar": "Short-Term Profit",
    "Enflasyondan Korunma": "Inflation Hedge",
}


def risk_onboarding():
    st.subheader("🎯 Define Your Investor Profile")
    st.markdown("Please complete the following survey so FinTrack AI can provide personalized recommendations for you.")

    existing_data = {}
    if st.session_state.user:
        fetched = get_onboarding_data(st.session_state.user["id"])
        if fetched:
            existing_data = fetched

    def_age = existing_data.get("age") if existing_data.get("age") is not None else 25
    raw_exp = existing_data.get("experience") if existing_data.get("experience") else "None"
    raw_risk = existing_data.get("risk_tolerance") if existing_data.get("risk_tolerance") else "Medium"
    def_obj = existing_data.get("objective") if existing_data.get("objective") else []

    exp_options = ["None", "1-3 Years", "3-5 Years", "5+ Years"]
    risk_options = ["Very Low", "Low", "Medium", "High", "Very High"]
    obj_options = ["Dividend Retirement", "Capital Gains", "Short-Term Profit", "Inflation Hedge"]

    def_exp = _LEGACY_EXP.get(raw_exp, raw_exp)
    if def_exp not in exp_options:
        def_exp = "None"
    def_risk = _LEGACY_RISK.get(raw_risk, raw_risk)
    if def_risk not in risk_options:
        def_risk = "Medium"

    exp_index = exp_options.index(def_exp) if def_exp in exp_options else 0

    with st.form("risk_form"):
        age = st.number_input("Your Age", min_value=18, max_value=100, value=def_age)
        experience = st.selectbox("Investment Experience", exp_options, index=exp_index)
        risk_tolerance = st.select_slider(
            "📈 Risk Tolerance",
            options=risk_options,
            value=def_risk,
        )
        mapped_obj = [_LEGACY_OBJ.get(o, o) for o in (def_obj or [])]
        valid_def_obj = [obj for obj in mapped_obj if obj in obj_options]
        objective = st.multiselect(
            "Investment Goals",
            obj_options,
            default=valid_def_obj,
        )

        submit = st.form_submit_button("Save Profile")

        if submit:
            user_id = st.session_state.user["id"] if st.session_state.user else None
            if user_id:
                profile_data = {
                    "age": age,
                    "experience": experience,
                    "risk_tolerance": risk_tolerance,
                    "objective": objective,
                }
                saved = save_onboarding_data(user_id, profile_data)
                if saved:
                    st.session_state.onboarding_complete = True
                    st.success("✅ Your profile has been saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Profile could not be saved. Please try again.")
