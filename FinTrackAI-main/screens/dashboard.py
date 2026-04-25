import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.supabase_utils import portfolio_select_by_user
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
    
    # 1. Hata Ayıklama & Veri Bağlantısı
    # Session state üzerinden dinamik kullanıcı ID alımı
    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("Kullanıcı oturumu bulunamadı.")
        return

    user_id = st.session_state.user['id']
    portfolio = portfolio_select_by_user(user_id)
    
    # Aynı varlığı içeren kayıtları birleştir (Quantity toplamı)
    portfolio_totals = {}
    if portfolio:
        for item in portfolio:
            sym = item['asset_id'].strip().upper()
            qty = float(item['quantity'])
            portfolio_totals[sym] = portfolio_totals.get(sym, 0.0) + qty

    total_value = 0.0
    daily_profit = 0.0
    asset_count = len(portfolio_totals)
    
    allocations = []
    asset_performance = []
    
    for sym, qty in portfolio_totals.items():
        curr_price = get_current_price(sym)
        if curr_price is not None:
            val = curr_price * qty
            total_value += val
            allocations.append({"Varlık": sym, "Değer (USD)": val})
            
            pct_change, abs_change = get_daily_change(sym)
            if pct_change is not None and abs_change is not None:
                daily_profit += (abs_change * qty)
                asset_performance.append({
                    "Varlık": sym, 
                    "Değişim": pct_change, 
                    "Fiyat": curr_price
                })
    
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
    with col2: st.markdown(metric_css.format(title="🚀 Günlük Kazanç", value=f"{profit_sign}${daily_profit:,.2f}", val_color=profit_color, sub="Son 24 Saat Değişimi", sub_color="#cbd5e1"), unsafe_allow_html=True)
    with col3: st.markdown(metric_css.format(title="💎 Varlık Çeşitliliği", value=str(asset_count), val_color="white", sub="Farklı Enstrüman", sub_color="#cbd5e1"), unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if allocations:
        st.markdown("### 📈 Portföy & Fiyat Analizi", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns([1, 1.2])
        
        df_alloc = pd.DataFrame(allocations)
        df_alloc = df_alloc.groupby("Varlık").sum().reset_index()
        
        # 2. Yeni Özellik: Varlık Dağılımı (Donut Chart)
        with chart_col1:
            st.markdown("<h4 style='color:#f8fafc; font-weight:700;'>Varlık Dağılımı (Ağırlık)</h4>", unsafe_allow_html=True)
            # hole=0.6 ile Donut grafik (Halka) görünümü elde edilir
            fig_pie = px.pie(df_alloc, names="Varlık", values="Değer (USD)", hole=0.6,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', 
                                  hoverinfo='label+percent', marker=dict(line=dict(color='#0f172a', width=2)))
            
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                font=dict(color="#cbd5e1", size=13), 
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            
            # Glassmorphism Box for Donut
            st.markdown('<div style="background: rgba(30, 41, 59, 0.3); padding: 20px; border-radius: 25px; border: 1px solid rgba(255,255,255,0.05); backdrop-filter: blur(10px);">', unsafe_allow_html=True)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # 3. Yeni Özellik: İnteraktif Hisse Fiyat Grafiği 
        with chart_col2:
            st.markdown("<h4 style='color:#f8fafc; font-weight:700;'>Fiyat Geçmişi (30 Gün)</h4>", unsafe_allow_html=True)
            options = df_alloc.sort_values(by="Değer (USD)", ascending=False)["Varlık"].tolist()
            
            col_sel1, col_sel2 = st.columns([1.5, 1])
            with col_sel1:
                top_asset = st.selectbox("İncelenecek Varlık:", options, label_visibility="collapsed")
            with col_sel2:
                chart_type = st.radio("Grafik Tipi:", ["📈 Çizgi", "🕯️ Mum"], horizontal=True, label_visibility="collapsed")
                
            try:
                # Market Data Utilities'de son 30 günlük history için public bir metod olmadığından 
                # (sadece güncel fiyat / get_daily_change var), projede kullanılan yfinance ile çekim yapıyoruz.
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
                    st.markdown('<div style="background: rgba(30, 41, 59, 0.3); padding: 20px; border-radius: 25px; border: 1px solid rgba(255,255,255,0.05); backdrop-filter: blur(10px); margin-top: 10px;">', unsafe_allow_html=True)
                    if chart_type == "📈 Çizgi":
                        fig_chart = go.Figure(data=[go.Scatter(
                            x=hist.index, y=hist['Close'], mode='lines', 
                            line=dict(color='#3b82f6', width=3), 
                            fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.15)'
                        )])
                    else:
                        fig_chart = go.Figure(data=[go.Candlestick(x=hist.index,
                                        open=hist['Open'],
                                        high=hist['High'],
                                        low=hist['Low'],
                                        close=hist['Close'])])
                                        
                    fig_chart.update_layout(
                        xaxis_rangeslider_visible=False,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#cbd5e1"),
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig_chart, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info(f"{top_asset} ({success_sym}) için geçmiş fiyat verisi bulunamadı.")
            except Exception as e:
                st.warning(f"Grafik yüklenirken bir hata oluştu: {e}")
                
        # 4. Yeni Özellik: Performans Özet Kartları
        if asset_performance and len(asset_performance) > 0:
            st.markdown("<br><br>### 🏆 Performans Özetleri (Günlük)", unsafe_allow_html=True)
            
            best_asset = max(asset_performance, key=lambda x: x["Değişim"])
            worst_asset = min(asset_performance, key=lambda x: x["Değişim"])
            
            perf_col1, perf_col2 = st.columns(2)
            
            perf_css = """
            <div style="background: rgba(30, 41, 59, 0.5); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); backdrop-filter: blur(15px); text-align: center;">
                <p style="color: #cbd5e1; font-size: 1rem; margin-bottom: 8px; font-weight: 600;">{title}</p>
                <h3 style="font-size: 2.2rem; margin: 0; color: {color}; font-weight: 800;">{asset}</h3>
                <span style="font-size: 1.3rem; font-weight: 700; color: {color};">{pct}%</span>
            </div>
            """
            
            # En Çok Kazanan ve Kaybeden bile aynı ve %0 ise renkleri dengele
            best_color = "#10b981" if best_asset["Değişim"] >= 0 else "#ef4444"
            worst_color = "#ef4444" if worst_asset["Değişim"] <= 0 else "#10b981"
            
            with perf_col1:
                st.markdown(perf_css.format(
                    title="🚀 En Çok Kazanan", 
                    asset=best_asset["Varlık"], 
                    pct=f"+{best_asset['Değişim']:.2f}" if best_asset['Değişim'] > 0 else f"{best_asset['Değişim']:.2f}",
                    color=best_color
                ), unsafe_allow_html=True)
                
            with perf_col2:
                st.markdown(perf_css.format(
                    title="📉 En Çok Kaybeden", 
                    asset=worst_asset["Varlık"], 
                    pct=f"{worst_asset['Değişim']:.2f}",
                    color=worst_color
                ), unsafe_allow_html=True)

    elif asset_count == 0:
        st.info("Portföyünüzde henüz bir varlık bulunmuyor. Öncelikle sol menüden portföyünüze veri ekleyin.")
