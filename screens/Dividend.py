import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Yeni yazdığımız utils/finance_math modülünü içe aktarıyoruz (Görev 1 referansı)
from utils.finance_math import calculate_compound_interest, fetch_dividend_history, get_sectoral_yields

def render_dividend_screen():
    st.markdown("""
        <div class="animate-page" style="background: rgba(15, 23, 42, 0.4); border-radius: 30px; padding: 40px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 2.5rem; backdrop-filter: blur(20px);">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem; font-weight: 800; letter-spacing: -1px;">📅 Temettü Emekliliği Motoru</h1>
            <p style="color: #94a3b8; font-size: 1.2rem; font-weight: 400;">Geçmiş verileri analiz edin, sektörel verimliliği keşfedin ve emekliliğinizi simüle edin.</p>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🚀 Simülatör (Bileşik Getiri)", "🗓️ Yaklaşan Takvim", "📊 Sektörel Analiz"])

    with tab1:
        st.markdown("<h3 style='margin-bottom:20px; color: white;'>4. Simülatör Ekranı (5-10-20 Yıllık)</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2.5], gap="large")
        with col1:
            st.markdown("<div style='background: rgba(255,255,255,0.03); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            initial = st.number_input("Başlangıç Sermayesi (TL)", min_value=0, value=100000, step=10000)
            monthly = st.number_input("Aylık Ek Yatırım (TL)", min_value=0, value=5000, step=1000)
            rate = st.slider("Beklenen Yıllık Getiri (%)", min_value=1, max_value=150, value=40)
            years = st.selectbox("Yatırım Süresi (Yıl)", [5, 10, 20], index=1)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            future_vals, invest_vals, final_val, total_inv = calculate_compound_interest(initial, monthly, rate, years)
            years_list = list(range(years + 1))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years_list, y=future_vals, name='Portföy Büyüklüğü', line=dict(color='#3b82f6', width=4), fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.2)'))
            fig.add_trace(go.Scatter(x=years_list, y=invest_vals, name='Yatırılan Anapara', line=dict(color='#94a3b8', width=3, dash='dash')))
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=0, r=0, t=30, b=0), xaxis=dict(showgrid=False, title="Yıl"), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="TL"))
            st.plotly_chart(fig, use_container_width=True)
            
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Toplam Yatırılan", f"₺ {total_inv:,.0f}")
            sc2.metric("Bileşik Getiri Kârı", f"₺ {(final_val - total_inv):,.0f}")
            sc3.metric("Ulaşılan Final Portföy", f"₺ {final_val:,.0f}")

    with tab2:
        st.markdown("<h3 style='margin-bottom:20px; color: white;'>2. Yaklaşan Temettü Takvimi</h3>", unsafe_allow_html=True)
        today = datetime.now()
        data = {
            "Şirket": ["TUPRS", "FROTO", "DOAS", "SISE", "THYAO"], 
            "Beklenen Tarih": [(today + timedelta(days=i*14)).strftime("%Y-%m-%d") for i in range(1, 6)], 
            "Durum": ["Kesinleşti", "Bekleniyor", "Kesinleşti", "Bekleniyor", "Pas Geçti"]
        }
        df = pd.DataFrame(data)
        
        def color_status(val):
            color = '#10b981' if val == 'Kesinleşti' else ('#f59e0b' if val == 'Bekleniyor' else '#ef4444')
            return f'color: {color}; font-weight: bold'
            
        st.dataframe(df.style.applymap(color_status, subset=['Durum']), use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("<h3 style='margin-bottom:20px; color: white;'>5. Sektörel Temettü Verimliliği Tabloları</h3>", unsafe_allow_html=True)
        tickers = ["TUPRS.IS", "FROTO.IS", "DOAS.IS", "SISE.IS", "ENJSA.IS", "TTRAK.IS"]
        df_divs = fetch_dividend_history(tickers)
        
        col_a, col_b = st.columns([1.5, 1])
        with col_a:
            st.markdown("#### Şirket Bazlı Veriler")
            st.dataframe(df_divs.style.format({"Son Temettü (TL)": "{:.2f} ₺", "Verim (%)": "%{:.2f}"}), use_container_width=True, hide_index=True)
            
        with col_b:
            st.markdown("#### Sektör Ortalamaları")
            sec_df = get_sectoral_yields(df_divs)
            st.dataframe(sec_df.style.format({"Verim (%)": "%{:.2f}"}), use_container_width=True, hide_index=True)
            st.bar_chart(sec_df.set_index("Sektör"), color="#a855f7")
