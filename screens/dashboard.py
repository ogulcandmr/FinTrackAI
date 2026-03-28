import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.portfolio_store import select_by_user
from utils.market_data_utils import get_current_price, get_daily_change
import pandas as pd
import yfinance as yf

def render_dashboard():
    st.markdown("""
        <div class="animate-page" style="background: rgba(15, 23, 42, 0.4); border-radius: 30px; padding: 40px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 2.5rem; backdrop-filter: blur(20px);">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem; font-weight: 800; letter-spacing: -1px; color:#f8fafc;">🏠 Finansal Kokpit</h1>
            <p style="color: #cbd5e1; font-size: 1.2rem; font-weight: 400;">Akıllı varlık yönetimi ve anlık veri analizi bir arada.</p>
        </div>
        """, unsafe_allow_html=True)
    
    user_id = st.session_state.user['id']
    portfolio = select_by_user(user_id)
    
    total_value = 0.0
    daily_profit = 0.0
    asset_count = len(set([item['asset_id'] for item in portfolio]))
    
    allocations = []
    
    if portfolio:
        for item in portfolio:
            sym = item['asset_id']
            qty = float(item['quantity'])
            curr_price = get_current_price(sym)
            if curr_price:
                val = curr_price * qty
                total_value += val
                allocations.append({"Varlık": sym, "Değer (USD)": val})
                
                pct_change, abs_change = get_daily_change(sym)
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
    
    val_sub = "⚖️ Güncel Portföy Büyüklüğü" if total_value > 0 else "⚖️ Veri Bekleniyor"
        
    with col1: st.markdown(metric_css.format(title="📊 Net Portföy", value=f"${total_value:,.2f}", val_color="white", sub=val_sub, sub_color="#cbd5e1"), unsafe_allow_html=True)
    with col2: st.markdown(metric_css.format(title="🚀 Günlük Kazanç", value=f"{profit_sign}${daily_profit:,.2f}", val_color=profit_color, sub="Son 24 Saat", sub_color="#cbd5e1"), unsafe_allow_html=True)
    with col3: st.markdown(metric_css.format(title="💎 Varlık Çeşitliliği", value=str(asset_count), val_color="white", sub="Farklı Enstrüman", sub_color="#cbd5e1"), unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if portfolio and allocations:
        st.markdown("### 📈 Portföy Analizi", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)
        
        df_alloc = pd.DataFrame(allocations)
        df_alloc = df_alloc.groupby("Varlık").sum().reset_index()
        
        with chart_col1:
            st.markdown("<h4 style='color:#f8fafc; font-weight:700;'>Varlık Dağılımı</h4>", unsafe_allow_html=True)
            fig_pie = px.pie(df_alloc, names="Varlık", values="Değer (USD)", hole=0.5,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_layout(paper_bgcolor="rgba(15, 23, 42, 0.4)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"), showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with chart_col2:
            st.markdown("<h4 style='color:#f8fafc; font-weight:700;'>Varlık Fiyat Analizi</h4>", unsafe_allow_html=True)
            
            options = df_alloc.sort_values(by="Değer (USD)", ascending=False)["Varlık"].tolist()
            
            col_sel1, col_sel2 = st.columns([1, 1])
            with col_sel1:
                top_asset = st.selectbox("Varlık Seçin", options, label_visibility="collapsed")
            with col_sel2:
                chart_type = st.radio("Tip", ["📈 Çizgi", "🕯️ Mum"], horizontal=True, label_visibility="collapsed")
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
                    if chart_type == "📈 Çizgi":
                        fig_chart = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], mode='lines', line=dict(color='#3b82f6', width=3), fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.15)')])
                    else:
                        fig_chart = go.Figure(data=[go.Candlestick(x=hist.index,
                                        open=hist['Open'],
                                        high=hist['High'],
                                        low=hist['Low'],
                                        close=hist['Close'])])
                                        
                    fig_chart.update_layout(
                        title=f"{top_asset} - Son 1 Ay",
                        xaxis_rangeslider_visible=False,
                        paper_bgcolor="rgba(15, 23, 42, 0.4)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#f8fafc"),
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    st.plotly_chart(fig_chart, use_container_width=True)
                else:
                    st.info(f"{top_asset} ({success_sym}) için fiyat grafiği çizilemedi.")
            except Exception as e:
                st.warning(f"Grafik yüklenirken bir hata oluştu: {e}")
    else:
        st.info("Portföyünüzde henüz bir varlık bulunmuyor. Öncelikle sol menüden portföyünüze veri ekleyin.")
