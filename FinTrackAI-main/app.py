import streamlit as st
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="FinTrack AI | Premium Wealth Management",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.supabase_utils import sign_in, sign_up, check_onboarding_status
from screens.onboarding import risk_onboarding
from screens.portfolio import render_portfolio_screen
from screens.Dividend import render_dividend_screen
from screens.AiLab import render_ai_screen
from screens.dashboard import render_dashboard

# --- STATE MANAGEMENT ---
if 'user' not in st.session_state:
    st.session_state.user = None
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = "login"
if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False
if 'supabase_session' not in st.session_state:
    st.session_state.supabase_session = None

# --- LUXURY UI/UX DESIGN (CUSTOM CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Reset */
    html, body, .stApp {
        font-family: 'Outfit', sans-serif;
        color: #f1f5f9;
        transition: background 0.5s ease;
    }
    
    /* Ensure icon fonts are not broken */
    .material-symbols-rounded, [data-testid="stIconMaterial"], .st-emotion-cache-1vt4ygl {
        font-family: 'Material Symbols Rounded' !important;
    }

    /* Streamlit UI Clean */
    .stAppDeployButton { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    
    /* Ensure Header (which contains the sidebar toggle button) stays on top */
    [data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 999999 !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Sidebar genişliği ve kaydırma çubuğunu kapat */
    [data-testid="stSidebar"] {
        min-width: 250px !important;
        overflow: visible !important;
    }

    /* FORCE SIDEBAR TOGGLE VISIBILITY WHEN CLOSED */
    [data-testid="collapsedControl"] {
        display: flex !important;
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 8px !important;
        margin: 15px !important;
        backdrop-filter: blur(10px) !important;
        z-index: 999999 !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="collapsedControl"]:hover {
        background-color: #3b82f6 !important;
        transform: scale(1.05) !important;
    }

    [data-testid="collapsedControl"] svg {
        fill: white !important;
        color: white !important;
        width: 24px !important;
        height: 24px !important;
    }

    /* Sidebar menü hizası */
    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding-left: 0.5rem !important;
        align-items: center !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        flex-wrap: nowrap !important;
    }
    /* Premium Background Image */
    .stApp {
        background: url("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=2832&auto=format&fit=crop") no-repeat center center fixed !important;
        background-size: cover !important;
    }
    
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at 30% 30%, rgba(2, 6, 23, 0.6) 0%, rgba(2, 6, 23, 0.9) 100%);
        z-index: 0;
    }
    
    [data-testid="stAppViewBlockContainer"] {
        z-index: 1;
        position: relative;
    }

    /* Sidebar daima üstte ve görünür */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        z-index: 99999 !important;
        position: relative !important;
        min-width: 16rem !important;
        transform: none !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Sidebar toggle butonu (collapsedControl) — her zaman görünür */
    button[kind="header"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 9999999 !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        background-color: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 8px !important;
        color: white !important;
    }
    [data-testid="collapsedControl"]:hover,
    [data-testid="stSidebarCollapsedControl"]:hover {
        background-color: #3b82f6 !important;
    }
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* Slider Interaction Fix */
    .stSlider [data-testid="baseAxis"], .stSlider [role="slider"] {
        pointer-events: auto !important;
        cursor: grab !important;
        z-index: 10 !important;
    }
    
    /* SENIOR ANIMATIONS (Force Render with Unique IDs) */
    @keyframes slideFwd {
        0% { opacity: 0; transform: translateX(50px) scale(0.98); filter: blur(10px); }
        100% { opacity: 1; transform: translateX(0) scale(1); filter: blur(0); }
    }

    @keyframes pageAppear {
        0% { opacity: 0; transform: translateY(30px); filter: blur(10px); }
        100% { opacity: 1; transform: translateY(0); filter: blur(0); }
    }

    .animate-forward {
        animation: slideFwd 0.8s cubic-bezier(0.19, 1, 0.22, 1) forwards !important;
    }
    
    .animate-page {
        animation: pageAppear 1s cubic-bezier(0.19, 1, 0.22, 1) forwards !important;
    }
    
    [data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.5) !important;
        backdrop-filter: blur(30px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 30px !important;
        padding: 45px !important;
        box-shadow: 0 40px 100px -20px rgba(0,0,0,0.8) !important;
        pointer-events: auto !important;
    }

    /* Input & Button Styles */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 18px !important;
        padding: 18px 25px !important;
        color: white !important;
        font-size: 1rem !important;
    }
    .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.3) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        border-radius: 18px !important;
        padding: 0.9rem !important;
        font-weight: 700 !important;
        border: none !important;
        color: white !important;
        transition: 0.5s cubic-bezier(0.19, 1, 0.22, 1) !important;
        letter-spacing: 0.5px !important;
    }
    .stButton > button:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 20px 40px rgba(37, 99, 235, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
def render_sidebar():
    st.sidebar.markdown("""
        <div style="text-align: center; margin-bottom: 2.5rem;">
            <h1 style="font-size: 2.5rem; font-weight: 800; color: #3b82f6; text-shadow: 0 0 30px rgba(59,130,246,0.4); margin-bottom: 0;">FinTrack.</h1>
            <p style="color: #64748b; font-weight: 600; font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase;">Intelligence Layer</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.user:
        st.sidebar.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.05); padding: 1.5rem; border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.1); margin-bottom: 2.5rem;">
                <p style="color: #94a3b8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Bağlı Hesap</p>
                <p style="color: white; font-weight: 700; margin: 0; font-size: 1.1rem; word-break: break-all;">{st.session_state.user['email']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Fixed Emoji usage for professional look
        menu = [
            "🏛️ Dashboard",
            "💼 Portföyüm",
            "📅 Temettü Emekliliği Motoru",
            "🧠 AI Analiz Merkezi",
            "🛡️ Güvenlik & Profil"
        ]

        choice = st.sidebar.radio("Navigasyon", menu, index=0, label_visibility="collapsed")
        
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        if st.sidebar.button("🔓 Güvenli Çıkış", key="logout_btn", use_container_width=True):
            st.session_state.user = None
            st.session_state.onboarding_complete = False
            st.rerun()
        return choice
    return None

def auth_screen():
    st.markdown("<div style='height: 12vh;'></div>", unsafe_allow_html=True)
    col_img, col_form = st.columns([1.3, 1], gap="large")
    
    with col_img:
        # Dynamic Marketing with Page Appear animation
        st.markdown(f'<div class="animate-page" key="hero_text">', unsafe_allow_html=True)
        st.markdown("""
            <div style="padding-top: 50px; padding-left: 20px;">
                <h1 style="font-size: 5rem; font-weight: 800; line-height: 1; margin-bottom: 1.5rem; color: white;">
                    Finansal <br>
                    <span style="background: linear-gradient(90deg, #3b82f6, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Geleceğinizi</span> <br>
                    Yönetin.
                </h1>
                <p style="color: #94a3b8; font-size: 1.4rem; margin-bottom: 3rem; max-width: 85%; font-weight: 400; line-height: 1.6;">
                    Yapay zeka katmanlı varlık yönetimi ile verilerinizi stratejik birer avantaja dönüştürün. Standartların ötesinde bir deneyim sizi bekliyor.
                </p>
                <div style="display: flex; gap: 25px;">
                    <div style="background: rgba(59, 130, 246, 0.1); padding: 15px 30px; border-radius: 40px; color: #3b82f6; font-weight: 700; border: 1px solid rgba(59, 130, 246, 0.2); font-size: 0.9rem;">💎 +10K Yatırımcı</div>
                    <div style="background: rgba(255, 255, 255, 0.05); padding: 15px 30px; border-radius: 40px; color: #e2e8f0; font-weight: 700; border: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.9rem;">🔒 Banka Düzeyi Koruma</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_form:
        mode = st.session_state.auth_mode
        # Forced re-render for animation using st.empty + unique key BASED ON MODE
        auth_container = st.empty()
        with auth_container.container():
            # KEY IN DIV FORCES ANIMATION RE-RUN
            st.markdown(f'<div class="animate-forward" key="auth_block_{mode}">', unsafe_allow_html=True)
            if mode == "login":
                st.markdown("<h2 style='text-align: center; margin-bottom: 5px; font-weight: 800; font-size: 2.2rem;'>Giriş Yap</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #64748b; font-size: 1rem; margin-bottom: 40px;'>FinTrack evrenine hoş geldiniz</p>", unsafe_allow_html=True)
                with st.form("login_form_v3"):
                    email = st.text_input("Kurumsal E-posta", placeholder="investor@fintrack.ai")
                    password = st.text_input("Gizli Şifre", type="password", placeholder="••••••••")
                    if st.form_submit_button("Sisteme Eriş", use_container_width=True):
                        if email and password:
                            res = sign_in(email, password)
                            if isinstance(res, str): st.error(f"❌ {res}")
                            else:
                                st.session_state.user = {"email": email, "id": res.user.id}
                                # Check if onboarding is already completed in Supabase
                                st.session_state.onboarding_complete = check_onboarding_status(res.user.id)
                                st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("🛠️ Test Modu İle Giriş (Supabase Olmadan)"):
                    st.session_state.user = {"email": "test@fintrack.ai", "id": "test-user-id"}
                    st.session_state.onboarding_complete = True
                    st.rerun()
                
                if st.button("Henüz hesabınız yok mu? Hemen Katılın ✨", key="to_reg", use_container_width=True):
                    st.session_state.auth_mode = "register"
                    st.rerun()
            else:
                st.markdown("<h2 style='text-align: center; margin-bottom: 5px; font-weight: 800; font-size: 2.2rem;'>Yeni Hesap</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #64748b; font-size: 1rem; margin-bottom: 40px;'>Sınırlarınızı bugün genişletin</p>", unsafe_allow_html=True)
                with st.form("register_form_v3"):
                    email = st.text_input("E-posta Adresi", placeholder="investor@fintrack.ai")
                    password = st.text_input("Güçlü Şifre", type="password", placeholder="••••••••")
                    confirm = st.text_input("Şifre Tekrar", type="password", placeholder="••••••••")
                    if st.form_submit_button("Üyeliği Başlat", use_container_width=True):
                        if password != confirm: st.error("❌ Şifreler uyuşmuyor.")
                        elif len(password) < 6: st.error("❌ Şifre güvenliği yetersiz.")
                        else:
                            res = sign_up(email, password)
                            if isinstance(res, str): st.error(f"❌ {res}")
                            else:
                                if res.session:
                                    st.session_state.user = {"email": email, "id": res.user.id}
                                    # Newly signed up users haven't completed onboarding
                                    st.session_state.onboarding_complete = False
                                    st.rerun()
                                else: st.info("ℹ️ Kayıt Başarılı! E-postanızı onaylayın.")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Zaten üye misiniz? Giriş Yapın 🏮", key="to_log", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

def main():
    if st.session_state.user:
        if not st.session_state.onboarding_complete:
            st.markdown('<div class="animate-page" key="onboard_cont">', unsafe_allow_html=True)
            risk_onboarding()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            choice = render_sidebar()
            if choice == "🏛️ Dashboard":
                render_dashboard()
            elif choice == "💼 Portföyüm":
                render_portfolio_screen()
            elif choice == "📅 Temettü Emekliliği Motoru":
                render_dividend_screen()
            elif choice == "🧠 AI Analiz Merkezi":
                render_ai_screen()
            elif choice == "🛡️ Güvenlik & Profil":

                st.markdown("<h1 class='animate-page'>🛡️ Güvenlik & Profil</h1>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("📝 Yatırımcı Karakterinizi Güncelleyin", expanded=True):
                    risk_onboarding()
            else:
                st.header(choice)
                st.write("Modül hazırlık aşamasında.")
    else:
        auth_screen()

if __name__ == "__main__":
    main()
