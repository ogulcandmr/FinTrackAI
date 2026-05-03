import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.supabase_utils import portfolio_select_by_user
from utils.market_data_utils import get_current_price, get_daily_change, USD_TO_TRY
import pandas as pd
import yfinance as yf

def render_dashboard():
    st.markdown("""
        <div class="animate-page" style="background: rgba(15, 23, 42, 0.4); border-radius: 30px; padding: 40px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 2.5rem; backdrop-filter: blur(20px);">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem; font-weight: 800; letter-spacing: -1px; color:#f8fafc;">🏠 Financial Cockpit</h1>
            <p style="color: #cbd5e1; font-size: 1.2rem; font-weight: 400;">Smart asset management and real-time data analysis in one place.</p>
        </div>
        """, unsafe_allow_html=True)
    
    user_id = st.session_state.user['id']
    portfolio = portfolio_select_by_user(user_id)
    
    total_value = 0.0
    daily_profit = 0.0
    asset_count = len(set([item['asset_id'] for item in portfolio]))
    
    allocations = []
    daily_changes = []

    if portfolio:
        for item in portfolio:
            sym = item['asset_id']
            qty = float(item['quantity'])
            curr_price = get_current_price(sym)
            if curr_price:
                val = curr_price * qty
                total_value += val
                allocations.append({"Asset": sym, "Value (USD)": val})
                
                pct_change, abs_change = get_daily_change(sym)
                if pct_change is not None:
                    daily_changes.append({"symbol": sym, "pct": pct_change, "abs": abs_change or 0.0})
                if abs_change:
                    daily_profit += (abs_change * qty)
    
    col1, col2, col3 = st.columns(3)
    metric_css = """
    <div style="background: rgba(30, 41, 59, 0.5); padding: 30px; border-radius: 25px; border: 1px solid rgba(255,255,255,0.05); backdrop-filter: blur(20px); animation: pageAppear 0.8s ease-out; height: 100%;">
        <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">{title}</p>
        <h2 style="font-size: 2.5rem; margin: 0; color: {val_color}; font-weight: 800;">{value}</h2>
        <div style="height: 10px;"></div>
        <p style="color: {sub_color}; font-size: 1rem; font-weight: 600; margin-bottom: 0;">{sub}</p>
    </div>
    """
    
    val_color = "white"
    profit_color = "#10b981" if daily_profit >= 0 else "#ef4444"
    profit_sign = "+" if daily_profit > 0 else ""
    
    val_sub = "⚖️ Current Portfolio Size" if total_value > 0 else "⚖️ Awaiting Data"
        
    with col1: st.markdown(metric_css.format(title="📊 Net Portfolio", value=f"${total_value:,.2f}", val_color="white", sub=val_sub, sub_color="#cbd5e1"), unsafe_allow_html=True)
    with col2: st.markdown(metric_css.format(title="🚀 Daily Gain", value=f"{profit_sign}${daily_profit:,.2f}", val_color=profit_color, sub="Last 24 Hours", sub_color="#cbd5e1"), unsafe_allow_html=True)
    with col3: st.markdown(metric_css.format(title="💎 Asset Diversity", value=str(asset_count), val_color="white", sub="Different Instruments", sub_color="#cbd5e1"), unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if portfolio and allocations:
        st.markdown("### 📈 Portfolio Analysis", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)
        
        df_alloc = pd.DataFrame(allocations)
        df_alloc = df_alloc.groupby("Asset").sum().reset_index()
        
        with chart_col1:
            st.markdown("<h4 style='color:#f8fafc; font-weight:700;'>Asset Allocation</h4>", unsafe_allow_html=True)
            fig_pie = px.pie(df_alloc, names="Asset", values="Value (USD)", hole=0.5,
                             color_discrete_sequence=["#3b82f6", "#a855f7", "#10b981", "#f59e0b", "#ef4444", "#06b6d4", "#ec4899", "#8b5cf6"])
            fig_pie.update_traces(textinfo="percent+label", textfont_size=13, textfont_color="#f8fafc",
                                  marker=dict(line=dict(color="rgba(15,23,42,0.8)", width=2)))
            fig_pie.update_layout(paper_bgcolor="rgba(15, 23, 42, 0.4)", plot_bgcolor="rgba(0,0,0,0)",
                                  font=dict(color="#f8fafc"), showlegend=True,
                                  legend=dict(font=dict(size=12)),
                                  margin=dict(l=0, r=0, t=10, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with chart_col2:
            st.markdown("<h4 style='color:#f8fafc; font-weight:700;'>Asset Price Analysis</h4>", unsafe_allow_html=True)
            
            options = df_alloc.sort_values(by="Value (USD)", ascending=False)["Asset"].tolist()
            
            col_sel1, col_sel2 = st.columns([1, 1])
            with col_sel1:
                top_asset = st.selectbox("Select Asset", options, label_visibility="collapsed")
            with col_sel2:
                chart_type = st.radio("Type", ["📈 Line", "🕯️ Candle"], horizontal=True, label_visibility="collapsed")
            try:
                syms_to_try = [top_asset]
                
                if "/" in top_asset:
                    syms_to_try.append(top_asset.replace("/", "-"))
                elif any(crypto in top_asset for crypto in ["BTC","ETH","BNB","SOL","USDT"]):
                    if "-USD" not in top_asset:
                        syms_to_try.append(top_asset + "-USD")
                elif "." not in top_asset and len(top_asset) <= 6:
                    syms_to_try.append(top_asset + ".IS")
                
                hist = None
                success_sym = top_asset
                for s in syms_to_try:
                    tkr = yf.Ticker(s)
                    tmp_hist = tkr.history(period="1mo")
                    if not tmp_hist.empty:
                        hist = tmp_hist
                        success_sym = s
                        break
                        
                if hist is not None and not hist.empty:
                    if chart_type == "📈 Line":
                        fig_chart = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], mode='lines', line=dict(color='#3b82f6', width=3), fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.15)')])
                    else:
                        fig_chart = go.Figure(data=[go.Candlestick(x=hist.index,
                                        open=hist['Open'],
                                        high=hist['High'],
                                        low=hist['Low'],
                                        close=hist['Close'],
                                        increasing_line_color='#10b981', increasing_fillcolor='rgba(16,185,129,0.3)',
                                        decreasing_line_color='#ef4444', decreasing_fillcolor='rgba(239,68,68,0.3)')])
                                        
                    fig_chart.update_layout(
                        title=f"{top_asset} - Last 1 Month",
                        xaxis_rangeslider_visible=False,
                        paper_bgcolor="rgba(15, 23, 42, 0.4)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#f8fafc"),
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    st.plotly_chart(fig_chart, use_container_width=True)
                else:
                    st.info(f"Price chart could not be drawn for {top_asset} ({success_sym}).")
            except Exception as e:
                st.warning(f"An error occurred while loading the chart: {e}")
        # --- Top Gainer / Loser Cards ---
        if daily_changes:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🏆 Daily Performance Leaders", unsafe_allow_html=True)
            
            sorted_changes = sorted(daily_changes, key=lambda x: x["pct"], reverse=True)
            seen = set()
            unique_changes = []
            for c in sorted_changes:
                if c["symbol"] not in seen:
                    seen.add(c["symbol"])
                    unique_changes.append(c)
            
            if len(unique_changes) >= 1:
                gainer = unique_changes[0]
                loser = unique_changes[-1]
                
                perf_card = """
                <div style="background: rgba(30, 41, 59, 0.5); padding: 24px 28px; border-radius: 20px;
                            border: 1px solid {border_color}; backdrop-filter: blur(20px);
                            animation: pageAppear 0.8s ease-out;">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div style="font-size: 2rem;">{icon}</div>
                        <div style="flex: 1;">
                            <p style="color: #cbd5e1; font-size: 0.8rem; margin: 0 0 4px 0; font-weight: 700;
                                      text-transform: uppercase; letter-spacing: 1px;">{label}</p>
                            <h3 style="margin: 0; color: #f8fafc; font-weight: 800; font-size: 1.4rem;">{symbol}</h3>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 0; color: {val_color}; font-size: 1.6rem; font-weight: 800;">{sign}{pct:.2f}%</p>
                            <p style="margin: 4px 0 0 0; color: {val_color}; font-size: 0.9rem; font-weight: 600;">{sign_abs}${abs_val:.2f}</p>
                        </div>
                    </div>
                </div>
                """
                
                g_col, l_col = st.columns(2)
                with g_col:
                    st.markdown(perf_card.format(
                        icon="🟢", label="Top Gainer", symbol=gainer["symbol"],
                        pct=gainer["pct"], abs_val=abs(gainer["abs"]),
                        sign="+" if gainer["pct"] >= 0 else "",
                        sign_abs="+" if gainer["abs"] >= 0 else "-",
                        val_color="#10b981",
                        border_color="rgba(16, 185, 129, 0.2)"
                    ), unsafe_allow_html=True)
                with l_col:
                    loser_color = "#ef4444" if loser["pct"] < 0 else "#f59e0b"
                    loser_border = "rgba(239, 68, 68, 0.2)" if loser["pct"] < 0 else "rgba(245, 158, 11, 0.2)"
                    st.markdown(perf_card.format(
                        icon="🔴" if loser["pct"] < 0 else "🟡",
                        label="Top Loser" if loser["pct"] < 0 else "Least Gainer",
                        symbol=loser["symbol"],
                        pct=loser["pct"], abs_val=abs(loser["abs"]),
                        sign="+" if loser["pct"] >= 0 else "",
                        sign_abs="+" if loser["abs"] >= 0 else "-",
                        val_color=loser_color,
                        border_color=loser_border
                    ), unsafe_allow_html=True)
    else:
        st.info("Your portfolio has no assets yet. Please add data to your portfolio from the left menu first.")
