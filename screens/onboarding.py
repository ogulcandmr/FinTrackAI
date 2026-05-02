import streamlit as st
from utils.supabase_utils import save_onboarding_data, get_onboarding_data

# Map legacy Turkish values stored in DB to current English options
_LEGACY_EXP = {
    "Hiç yok": "None",
    "1-3 Yıl": "1–3 years",
    "3-5 Yıl": "3–5 years",
    "5 Yıl +": "5+ years",
}
_LEGACY_RISK = {
    "Çok Düşük": "Very low",
    "Düşük": "Low",
    "Orta": "Medium",
    "Yüksek": "High",
    "Çok Yüksek": "Very high",
}
_LEGACY_OBJ = {
    "Temettü Emekliliği": "Dividend retirement",
    "Sermaye Kazancı": "Capital appreciation",
    "Kısa Vadeli Kar": "Short-term gains",
    "Enflasyondan Korunma": "Inflation hedge",
}


def _norm_exp(val):
    if not val:
        return "None"
    return _LEGACY_EXP.get(val, val)


def _norm_risk(val):
    if not val:
        return "Medium"
    return _LEGACY_RISK.get(val, val)


def _norm_objectives(obj_list):
    if not obj_list:
        return []
    out = []
    for o in obj_list:
        out.append(_LEGACY_OBJ.get(o, o))
    return out


def risk_onboarding():
    st.subheader("🎯 Define your investor profile")
    st.markdown("Please complete the questionnaire below so FinTrack AI can tailor recommendations for you.")
    
    existing_data = {}
    if st.session_state.user:
        fetched = get_onboarding_data(st.session_state.user['id'])
        if fetched:
            existing_data = fetched

    exp_options = ["None", "1–3 years", "3–5 years", "5+ years"]
    risk_options = ["Very low", "Low", "Medium", "High", "Very high"]
    obj_options = [
        "Dividend retirement",
        "Capital appreciation",
        "Short-term gains",
        "Inflation hedge",
    ]

    def_age = existing_data.get("age") if existing_data.get("age") is not None else 25
    def_exp = _norm_exp(existing_data.get("experience"))
    def_risk = _norm_risk(existing_data.get("risk_tolerance"))
    raw_obj = existing_data.get("objective") if existing_data.get("objective") else []
    def_obj = _norm_objectives(raw_obj if isinstance(raw_obj, list) else [])

    exp_index = exp_options.index(def_exp) if def_exp in exp_options else 0
    if def_risk not in risk_options:
        def_risk = "Medium"
    valid_def_obj = [obj for obj in def_obj if obj in obj_options]

    with st.form("risk_form"):
        age = st.number_input("Your age", min_value=18, max_value=100, value=def_age)
        experience = st.selectbox("Investment experience", exp_options, index=exp_index)
        risk_tolerance = st.select_slider(
            "📈 Risk tolerance",
            options=risk_options,
            value=def_risk
        )
        objective = st.multiselect(
            "Investment goals",
            obj_options,
            default=valid_def_obj
        )
        
        submit = st.form_submit_button("Save profile")
        
        if submit:
            user_id = st.session_state.user['id'] if st.session_state.user else None
            if user_id:
                profile_data = {
                    "age": age,
                    "experience": experience,
                    "risk_tolerance": risk_tolerance,
                    "objective": objective
                }
                save_onboarding_data(user_id, profile_data)
                
            st.session_state.onboarding_complete = True
            st.success("Your profile has been saved successfully!")
            st.rerun()
