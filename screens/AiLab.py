"""
AiLab.py – Yapay Zeka ve Algoritmik Analiz Ekranı (4. Kişi Görevleri)
Streamlit arayüzü: Sentiment Analiz, Prophet Fiyat Tahmini, Risk Uyumluluk.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

try:
    from ai.sentiment import analyze_sentiment
    from ai.forecast import run_forecast
    from ai.news import fetch_news
    _AI_AVAILABLE = True
except ImportError:
    _AI_AVAILABLE = False

LABEL_COLOR = {"positive": "#10b981", "negative": "#ef4444", "neutral": "#f59e0b"}
LABEL_EMOJI = {"positive": "🟢 Positive", "negative": "🔴 Negative", "neutral": "⚪ Neutral"}

RISK_COMPATIBILITY = {
    "Very Low":   {"positive": "✅ Compatible", "neutral": "⚠️ Be Careful", "negative": "🚫 Incompatible"},
    "Low":        {"positive": "✅ Compatible", "neutral": "⚠️ Be Careful", "negative": "🚫 Incompatible"},
    "Medium":     {"positive": "✅ Compatible", "neutral": "✅ Compatible", "negative": "⚠️ Be Careful"},
    "High":       {"positive": "✅ Compatible", "neutral": "✅ Compatible", "negative": "✅ Compatible"},
    "Very High":  {"positive": "✅ Compatible", "neutral": "✅ Compatible", "negative": "✅ Compatible"},
}


def _risk_badge(user_risk: str, sentiment: str) -> str:
    """Kullanıcının risk profiline göre uyarı oluşturur."""
    table = RISK_COMPATIBILITY.get(user_risk, {})
    return table.get(sentiment, "⚠️ Unknown")


def render_ai_screen():
    st.markdown("""
        <div class="animate-page" style="background: rgba(15, 23, 42, 0.4); border-radius: 30px; padding: 40px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 2.5rem; backdrop-filter: blur(20px);">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem; font-weight: 800; letter-spacing: -1px;">🧠 AI Analysis Center</h1>
            <p style="color: #94a3b8; font-size: 1.2rem; font-weight: 400;">Prophet price prediction, news sentiment analysis, and risk profile compatibility check.</p>
        </div>
        """, unsafe_allow_html=True)

    if not _AI_AVAILABLE:
        st.error("❌ AI modules failed to load. Ensure `prophet`, `textblob`, and `requests` are installed.")
        st.code("pip install prophet textblob requests", language="bash")
        return

    # Kullanıcının risk profili
    user = st.session_state.get("user", {})
    user_risk = st.session_state.get("user_risk_tolerance", "Medium")  # Onboarding'den gelirse

    tab1, tab2 = st.tabs(["📈 Price Forecast (Prophet)", "📰 News Sentiment Analysis"])

    # ─── TAB 1: PROPHET FORECAST ─────────────────────────────────────────────
    with tab1:
        st.markdown("<h3 style='color:white; margin-bottom:20px;'>15-Day Price Forecast</h3>", unsafe_allow_html=True)

        col_input, col_run = st.columns([3, 1])
        with col_input:
            ticker_input = st.text_input(
                "Stock / Crypto Symbol",
                value="AAPL",
                placeholder="e.g.: AAPL, MSFT, BTC-USD",
                label_visibility="collapsed"
            )
        with col_run:
            run_btn = st.button("🚀 Forecast", use_container_width=True)

        if run_btn and ticker_input:
            with st.spinner(f"📊 Training Prophet model for {ticker_input.upper()}... (this may take 20-30 seconds)"):
                result = run_forecast(ticker_input.strip().upper())

            if result is None:
                st.error(f"❌ Forecast could not be generated for **{ticker_input.upper()}**. Check the symbol (Use BTC-USD format for crypto).")
            else:
                preds = result["predictions"]
                hist = result["historical_df"]

                # Tarihsel + Tahmin Grafiği
                fig = go.Figure()
                # Son 60 gün tarihsel
                hist_tail = hist.tail(60)
                fig.add_trace(go.Scatter(
                    x=hist_tail["ds"], y=hist_tail["y"],
                    name="Historical Close",
                    line=dict(color="#3b82f6", width=2)
                ))
                # Prophet tahmini
                fig.add_trace(go.Scatter(
                    x=preds["ds"], y=preds["yhat"],
                    name="Forecast (yhat)",
                    line=dict(color="#a855f7", width=3, dash="dot")
                ))
                # Güven aralığı
                fig.add_trace(go.Scatter(
                    x=pd.concat([preds["ds"], preds["ds"][::-1]]),
                    y=pd.concat([preds["yhat_upper"], preds["yhat_lower"][::-1]]),
                    fill="toself",
                    fillcolor="rgba(168, 85, 247, 0.15)",
                    line=dict(color="rgba(0,0,0,0)"),
                    name="Confidence Interval"
                ))
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white"), margin=dict(l=0, r=0, t=30, b=0),
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
                    legend=dict(bgcolor="rgba(0,0,0,0)")
                )
                st.plotly_chart(fig, use_container_width=True)

                # Tahmin tablosu
                st.markdown("#### 📋 Forecast Table")
                preds_display = preds.copy()
                preds_display["ds"] = preds_display["ds"].dt.strftime("%Y-%m-%d")
                preds_display.columns = ["Date", "Forecast", "Lower Bound", "Upper Bound"]
                st.dataframe(preds_display.style.format({"Forecast": "${:.2f}", "Lower Bound": "${:.2f}", "Upper Bound": "${:.2f}"}), use_container_width=True, hide_index=True)

                # ── Risk Uyumluluk Kontrolü ────────────────────────────────
                trend = "positive" if preds["yhat"].iloc[-1] > preds["yhat"].iloc[0] else "negative"
                badge = _risk_badge(user_risk, trend)
                trend_label = "📈 Upward Trend" if trend == "positive" else "📉 Downward Trend"
                color = "#10b981" if trend == "positive" else "#ef4444"

                st.markdown(f"""
                    <div style="background: rgba(30,41,59,0.5); border-radius:20px; padding:25px; border:1px solid rgba(255,255,255,0.08); margin-top:20px;">
                        <h4 style="color:white; margin-bottom:10px;">🛡️ Risk Profile Compatibility Check</h4>
                        <p style="color:#94a3b8; margin-bottom:5px;">Your Risk Tolerance: <strong style="color:white">{user_risk}</strong></p>
                        <p style="color:#94a3b8; margin-bottom:5px;">Forecast Trend: <strong style="color:{color}">{trend_label}</strong></p>
                        <p style="font-size:1.3rem; font-weight:800; color:white; margin:15px 0 0 0;">{badge}</p>
                    </div>
                """, unsafe_allow_html=True)

    # ─── TAB 2: SENTIMENT ANALİZ ─────────────────────────────────────────────
    with tab2:
        st.markdown("<h3 style='color:white; margin-bottom:20px;'>News Sentiment Analysis</h3>", unsafe_allow_html=True)

        news_key_set = bool(st.secrets.get("NEWS_API_KEY", ""))

        col_news1, col_news2 = st.columns([3, 1])
        with col_news1:
            news_ticker = st.text_input(
                "Stock Symbol (Fetch News)",
                value="AAPL",
                label_visibility="collapsed",
                placeholder="e.g.: AAPL, TESLA, Bitcoin"
            )
        with col_news2:
            news_btn = st.button("🔍 Analyze", use_container_width=True)

        if news_btn and news_ticker:
            if not news_key_set:
                st.warning("⚠️ NewsAPI key is not defined. Live news fetching is disabled.")
                st.info("Analyzing 5 sample headlines for testing...")
                sample_headlines = [
                    f"{news_ticker} stock hits all-time high amid strong earnings",
                    f"Analysts bullish on {news_ticker} growth prospects",
                    f"{news_ticker} faces regulatory scrutiny in Europe",
                    f"Investors cautious as {news_ticker} misses revenue targets",
                    f"{news_ticker} announces new product line to boost market share",
                ]
                headlines = sample_headlines
            else:
                with st.spinner(f"📰 Fetching news for {news_ticker.upper()}..."):
                    headlines = fetch_news(news_ticker.strip())

            if not headlines:
                st.error("News not found. Change the symbol or keyword and try again.")
            else:
                with st.spinner("🧠 Performing sentiment analysis..."):
                    report = analyze_sentiment(headlines)

                overall = report.get("overall_label", "neutral")
                avg_pol = report.get("average_polarity", 0.0)
                overall_color = LABEL_COLOR.get(overall, "white")
                overall_emoji = LABEL_EMOJI.get(overall, "⚪")

                # Özet kart
                st.markdown(f"""
                    <div style="background: rgba(30,41,59,0.5); border-radius:20px; padding:30px; border:1px solid rgba(255,255,255,0.08); margin-bottom:25px;">
                        <h2 style="color:{overall_color}; margin:0; font-size:2.5rem;">{overall_emoji}</h2>
                        <p style="color:#94a3b8; margin:10px 0 0 0;">Average Sentiment Score: <strong style="color:white">{avg_pol:+.3f}</strong> &nbsp;|&nbsp; 
                        Analyzed: <strong style="color:white">{report.get("total_analyzed", 0)}</strong> headlines</p>
                    </div>
                """, unsafe_allow_html=True)

                # Per-headline tablo
                items = report.get("items", [])
                rows_display = []
                for item in items:
                    lbl = item["label"]
                    rows_display.append({
                        "Headline": item["text"][:100],
                        "Sentiment": LABEL_EMOJI.get(lbl, lbl),
                        "Score": round(item["polarity"], 3),
                    })
                if rows_display:
                    df_items = pd.DataFrame(rows_display)
                    st.dataframe(df_items, use_container_width=True, hide_index=True)

                # Risk uyumluluk
                badge = _risk_badge(user_risk, overall)
                st.markdown(f"""
                    <div style="background: rgba(30,41,59,0.4); border-radius:16px; padding:20px; border:1px solid rgba(255,255,255,0.06); margin-top:20px;">
                        <h4 style="color:white; margin-bottom:8px;">🛡️ Risk Profile Compatibility</h4>
                        <p style="color:#94a3b8; margin:0;">Your Profile (<strong style="color:white">{user_risk}</strong>) + This News Sentiment = <strong style="color:white; font-size:1.2rem;">{badge}</strong></p>
                    </div>
                """, unsafe_allow_html=True)
