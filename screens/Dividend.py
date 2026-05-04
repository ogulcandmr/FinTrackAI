import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Import our new utils/finance_math module
from utils.finance_math import calculate_compound_interest, fetch_dividend_history, get_sectoral_yields, scrape_upcoming_dividends

def render_dividend_screen():
    st.markdown("""
        <div class="animate-page" style="background: linear-gradient(145deg, rgba(30, 58, 138, 0.6), rgba(15, 23, 42, 0.8)); border-radius: 30px; padding: 40px; border: 1px solid rgba(96, 165, 250, 0.3); margin-bottom: 2.5rem; backdrop-filter: blur(20px); box-shadow: 0 10px 40px rgba(0,0,0,0.5);">
            <h1 style="font-size: 3.8rem; margin-bottom: 0.5rem; font-weight: 900; letter-spacing: -1px; background: linear-gradient(90deg, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📅 Dividend Retirement Engine</h1>
            <p style="color: #f8fafc; font-size: 1.35rem; font-weight: 500; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">Analyze historical data, discover sectoral yield, and simulate your retirement.</p>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🚀 Simulator (Compound Interest)", "🗓️ Upcoming Calendar", "📊 Sectoral Analysis"])

    with tab1:
        st.markdown("<h3 style='margin-bottom:20px; color: #60a5fa; font-weight: 800; font-size: 1.8rem; text-shadow: 0 2px 5px rgba(0,0,0,0.5);'>4. Simulator Screen (5-10-20 Years)</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2.5], gap="large")
        with col1:
            st.markdown("<div style='background: rgba(30, 41, 59, 0.7); padding: 25px; border-radius: 20px; border: 1px solid rgba(96, 165, 250, 0.3); box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>", unsafe_allow_html=True)
            initial = st.number_input("Initial Capital (TRY)", min_value=0, value=100000, step=10000)
            monthly = st.number_input("Monthly Additional Investment (TRY)", min_value=0, value=5000, step=1000)
            rate = st.slider("Expected Annual Return (%)", min_value=1, max_value=150, value=40)
            years = st.selectbox("Investment Duration (Years)", [5, 10, 20], index=1)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            future_vals, invest_vals, final_val, total_inv = calculate_compound_interest(initial, monthly, rate, years)
            years_list = list(range(years + 1))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years_list, y=future_vals, name='Portfolio Size', line=dict(color='#60a5fa', width=5), fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.25)'))
            fig.add_trace(go.Scatter(x=years_list, y=invest_vals, name='Invested Principal', line=dict(color='#cbd5e1', width=3, dash='dash')))
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc', size=14), margin=dict(l=0, r=0, t=30, b=0), xaxis=dict(showgrid=False, title="Year"), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.15)', title="TRY"))
            st.plotly_chart(fig, use_container_width=True)
            
            sc1, sc2, sc3 = st.columns(3)
            # Custom styled metrics for better visibility
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; margin-top: 15px;'>
                <div style='background: rgba(15, 23, 42, 0.7); padding: 20px; border-radius: 15px; border-left: 5px solid #cbd5e1; width: 32%; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3);'>
                    <p style='color: #cbd5e1; font-weight: 700; margin-bottom: 5px; font-size: 1rem;'>Total Invested</p>
                    <h3 style='color: white; font-weight: 800; font-size: 1.5rem; margin: 0;'>₺ {total_inv:,.0f}</h3>
                </div>
                <div style='background: rgba(15, 23, 42, 0.7); padding: 20px; border-radius: 15px; border-left: 5px solid #a855f7; width: 32%; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3);'>
                    <p style='color: #c084fc; font-weight: 700; margin-bottom: 5px; font-size: 1rem;'>Compound Interest Profit</p>
                    <h3 style='color: white; font-weight: 800; font-size: 1.5rem; margin: 0;'>₺ {(final_val - total_inv):,.0f}</h3>
                </div>
                <div style='background: rgba(15, 23, 42, 0.7); padding: 20px; border-radius: 15px; border-left: 5px solid #3b82f6; width: 32%; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3);'>
                    <p style='color: #60a5fa; font-weight: 700; margin-bottom: 5px; font-size: 1rem;'>Final Portfolio Value</p>
                    <h3 style='color: white; font-weight: 800; font-size: 1.5rem; margin: 0;'>₺ {final_val:,.0f}</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("<h3 style='margin-bottom:20px; color: #a855f7; font-weight: 800; font-size: 1.8rem; text-shadow: 0 2px 5px rgba(0,0,0,0.5);'>2. Upcoming Dividend Calendar (Real Data)</h3>", unsafe_allow_html=True)
        
        df = scrape_upcoming_dividends()
        
        def color_status(val):
            if isinstance(val, str):
                if val == 'Confirmed': return 'color: #34d399; font-weight: 900; background-color: rgba(16, 185, 129, 0.15);'
                elif val == 'Expected': return 'color: #fbbf24; font-weight: 900; background-color: rgba(245, 158, 11, 0.15);'
                elif val == 'Paid': return 'color: #60a5fa; font-weight: 900; background-color: rgba(96, 165, 250, 0.15);'
                else: return 'color: #f87171; font-weight: 900; background-color: rgba(239, 68, 68, 0.15);'
            return ''
            
        st.dataframe(df.style.applymap(color_status, subset=['Status']).set_properties(**{'background-color': 'rgba(15, 23, 42, 0.8)', 'color': 'white', 'font-size': '1.1rem', 'border-color': 'rgba(255,255,255,0.1)'}), use_container_width=True, hide_index=True, height=300)

    with tab3:
        st.markdown("<h3 style='margin-bottom:20px; color: #f472b6; font-weight: 800; font-size: 1.8rem; text-shadow: 0 2px 5px rgba(0,0,0,0.5);'>5. Sectoral Dividend Yield Tables</h3>", unsafe_allow_html=True)
        tickers = ["TUPRS.IS", "FROTO.IS", "DOAS.IS", "SISE.IS", "ENJSA.IS", "TTRAK.IS"]
        df_divs = fetch_dividend_history(tickers)
        
        col_a, col_b = st.columns([1.5, 1])
        with col_a:
            st.markdown("<h4 style='color: #e2e8f0; font-weight: 700;'>Company Based Data</h4>", unsafe_allow_html=True)
            st.dataframe(df_divs.style.format({"Last Dividend (TRY)": "{:.2f} ₺", "Yield (%)": "%{:.2f}"}).set_properties(**{'background-color': 'rgba(15, 23, 42, 0.8)', 'color': 'white', 'font-size': '1.1rem'}), use_container_width=True, hide_index=True)
            
        with col_b:
            st.markdown("<h4 style='color: #e2e8f0; font-weight: 700;'>Sector Averages</h4>", unsafe_allow_html=True)
            sec_df = get_sectoral_yields(df_divs)
            st.dataframe(sec_df.style.format({"Yield (%)": "%{:.2f}"}).set_properties(**{'background-color': 'rgba(15, 23, 42, 0.8)', 'color': 'white', 'font-size': '1.1rem'}), use_container_width=True, hide_index=True)
            
            # Make the bar chart pop out more
            st.bar_chart(sec_df.set_index("Sector"), color="#c084fc", height=250)
