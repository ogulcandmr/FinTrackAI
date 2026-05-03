import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

from utils.finance_math import calculate_compound_interest, fetch_dividend_history, get_sectoral_yields

def render_dividend_screen():
    st.markdown("""
        <div class="animate-page" style="background: rgba(15, 23, 42, 0.4); border-radius: 30px; padding: 40px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 2.5rem; backdrop-filter: blur(20px);">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem; font-weight: 800; letter-spacing: -1px;">📅 Dividend Retirement Engine</h1>
            <p style="color: #94a3b8; font-size: 1.2rem; font-weight: 400;">Analyze historical data, explore sectoral efficiency, and simulate your retirement.</p>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🚀 Simulator (Compound Returns)", "🗓️ Upcoming Calendar", "📊 Sectoral Analysis"])

    with tab1:
        st.markdown("<h3 style='margin-bottom:20px; color: white;'>Simulator (5-10-20 Year)</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2.5], gap="large")
        with col1:
            st.markdown("<div style='background: rgba(255,255,255,0.03); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            initial = st.number_input("Initial Capital ($)", min_value=0, value=10000, step=1000)
            monthly = st.number_input("Monthly Additional Investment ($)", min_value=0, value=500, step=100)
            rate = st.slider("Expected Annual Return (%)", min_value=1, max_value=150, value=12)
            years = st.selectbox("Investment Period (Years)", [5, 10, 20], index=1)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            future_vals, invest_vals, final_val, total_inv = calculate_compound_interest(initial, monthly, rate, years)
            years_list = list(range(years + 1))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years_list, y=future_vals, name='Portfolio Size', line=dict(color='#3b82f6', width=4), fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.2)'))
            fig.add_trace(go.Scatter(x=years_list, y=invest_vals, name='Invested Principal', line=dict(color='#94a3b8', width=3, dash='dash')))
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=0, r=0, t=30, b=0), xaxis=dict(showgrid=False, title="Year"), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="USD"))
            st.plotly_chart(fig, use_container_width=True)
            
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Total Invested", f"$ {total_inv:,.0f}")
            sc2.metric("Compound Return Profit", f"$ {(final_val - total_inv):,.0f}")
            sc3.metric("Final Portfolio Value", f"$ {final_val:,.0f}")

    with tab2:
        st.markdown("<h3 style='margin-bottom:20px; color: white;'>Upcoming Dividend Calendar</h3>", unsafe_allow_html=True)
        today = datetime.now()
        data = {
            "Company": ["TUPRS", "FROTO", "DOAS", "SISE", "THYAO"], 
            "Expected Date": [(today + timedelta(days=i*14)).strftime("%Y-%m-%d") for i in range(1, 6)], 
            "Status": ["Confirmed", "Pending", "Confirmed", "Pending", "Skipped"]
        }
        df = pd.DataFrame(data)
        
        def color_status(val):
            color = '#10b981' if val == 'Confirmed' else ('#f59e0b' if val == 'Pending' else '#ef4444')
            return f'color: {color}; font-weight: bold'
            
        st.dataframe(df.style.applymap(color_status, subset=['Status']), use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("<h3 style='margin-bottom:20px; color: white;'>Sectoral Dividend Efficiency Tables</h3>", unsafe_allow_html=True)
        tickers = ["TUPRS.IS", "FROTO.IS", "DOAS.IS", "SISE.IS", "ENJSA.IS", "TTRAK.IS"]
        df_divs = fetch_dividend_history(tickers)
        
        col_a, col_b = st.columns([1.5, 1])
        with col_a:
            st.markdown("#### Company Data")
            st.dataframe(df_divs.style.format({"Last dividend (TRY)": "₺{:.2f}", "Yield (%)": "{:.2f}%"}), use_container_width=True, hide_index=True)
            
        with col_b:
            st.markdown("#### Sector Averages")
            sec_df = get_sectoral_yields(df_divs)
            st.dataframe(sec_df.style.format({"Yield (%)": "{:.2f}%"}), use_container_width=True, hide_index=True)
            st.bar_chart(sec_df.set_index("Sector"), color="#a855f7")
