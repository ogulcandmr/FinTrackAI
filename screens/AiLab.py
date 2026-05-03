"""
AiLab.py – AI and Algorithmic Analysis Screen
Streamlit interface: Sentiment Analysis, Prophet Price Prediction, Risk Compatibility.
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
    "Very Low":  {"positive": "✅ Compatible", "neutral": "⚠️ Be Cautious", "negative": "🚫 Incompatible"},
    "Low":       {"positive": "✅ Compatible", "neutral": "⚠️ Be Cautious", "negative": "🚫 Incompatible"},
    "Medium":    {"positive": "✅ Compatible", "neutral": "✅ Compatible",   "negative": "⚠️ Be Cautious"},
    "High":      {"positive": "✅ Compatible", "neutral": "✅ Compatible",   "negative": "✅ Compatible"},
    "Very High": {"positive": "✅ Compatible", "neutral": "✅ Compatible",   "negative": "✅ Compatible"},
}

_LEGACY_RISK_TR = {
    "Çok Düşük": "Very Low",
    "Düşük": "Low",
    "Orta": "Medium",
    "Yüksek": "High",
    "Çok Yüksek": "Very High",
}


def _normalize_risk_tolerance(raw: str) -> str:
    if not raw:
        return "Medium"
    if raw in RISK_COMPATIBILITY:
        return raw
    return _LEGACY_RISK_TR.get(raw, "Medium")


def _risk_badge(user_risk: str, sentiment: str) -> str:
    """Generates a warning based on the user's risk profile."""
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
        st.error("❌ AI modules could not be loaded. Make sure `prophet`, `textblob`, and `requests` libraries are installed.")
        st.code("pip install prophet textblob requests", language="bash")
        return

    # User's risk profile (Supabase profiles + legacy Turkish labels)
    user = st.session_state.get("user", {})
    user_risk = st.session_state.get("user_risk_tolerance")
    if user_risk is None and user.get("id"):
        from utils.supabase_utils import get_onboarding_data
        prof = get_onboarding_data(user["id"]) or {}
        user_risk = _normalize_risk_tolerance(prof.get("risk_tolerance") or "Medium")
    else:
        user_risk = _normalize_risk_tolerance(user_risk or "Medium")

    tab1, tab2 = st.tabs(["📈 Price Prediction (Prophet)", "📰 News Sentiment Analysis"])

    # ─── TAB 1: PROPHET FORECAST ─────────────────────────────────────────────
    with tab1:
        st.markdown("<h3 style='color:white; margin-bottom:20px;'>15-Day Price Prediction</h3>", unsafe_allow_html=True)

        col_input, col_run = st.columns([3, 1])
        with col_input:
            ticker_input = st.text_input(
                "Stock / Crypto Symbol",
                value="AAPL",
                placeholder="e.g. AAPL, MSFT, BTC-USD",
                label_visibility="collapsed"
            )
        with col_run:
            run_btn = st.button("🚀 Predict", use_container_width=True)

        if run_btn and ticker_input:
            with st.spinner(f"📊 Training Prophet model for {ticker_input.upper()}... (this may take 20-30 sec)"):
                result = run_forecast(ticker_input.strip().upper())

            if result is None:
                st.error(f"❌ Could not generate prediction for **{ticker_input.upper()}**. Check the symbol (use BTC-USD format for crypto).")
            else:
                preds = result["predictions"]
                hist = result["historical_df"]

                # Historical + Forecast Chart
                fig = go.Figure()
                hist_tail = hist.tail(60)
                fig.add_trace(go.Scatter(
                    x=hist_tail["ds"], y=hist_tail["y"],
                    name="Historical Close",
                    line=dict(color="#3b82f6", width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=preds["ds"], y=preds["yhat"],
                    name="Prediction (yhat)",
                    line=dict(color="#a855f7", width=3, dash="dot")
                ))
                # Confidence interval
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

                # Prediction table
                st.markdown("#### 📋 Prediction Table")
                preds_display = preds.copy()
                preds_display["ds"] = preds_display["ds"].dt.strftime("%Y-%m-%d")
                preds_display.columns = ["Date", "Prediction", "Lower Bound", "Upper Bound"]
                st.dataframe(preds_display.style.format({"Prediction": "${:.2f}", "Lower Bound": "${:.2f}", "Upper Bound": "${:.2f}"}), use_container_width=True, hide_index=True)

                # ── Risk Compatibility Check ────────────────────────────────
                trend = "positive" if preds["yhat"].iloc[-1] > preds["yhat"].iloc[0] else "negative"
                badge = _risk_badge(user_risk, trend)
                trend_label = "📈 Upward Trend" if trend == "positive" else "📉 Downward Trend"
                color = "#10b981" if trend == "positive" else "#ef4444"

                st.markdown(f"""
                    <div style="background: rgba(30,41,59,0.5); border-radius:20px; padding:25px; border:1px solid rgba(255,255,255,0.08); margin-top:20px;">
                        <h4 style="color:white; margin-bottom:10px;">🛡️ Risk Profile Compatibility Check</h4>
                        <p style="color:#94a3b8; margin-bottom:5px;">Your Risk Tolerance: <strong style="color:white">{user_risk}</strong></p>
                        <p style="color:#94a3b8; margin-bottom:5px;">Prediction Trend: <strong style="color:{color}">{trend_label}</strong></p>
                        <p style="font-size:1.3rem; font-weight:800; color:white; margin:15px 0 0 0;">{badge}</p>
                    </div>
                """, unsafe_allow_html=True)

    # ─── TAB 2: SENTIMENT ANALYSIS ───────────────────────────────────────────
    with tab2:
        st.markdown("<h3 style='color:white; margin-bottom:20px;'>News Sentiment Analysis</h3>", unsafe_allow_html=True)

        news_key_set = bool(st.secrets.get("NEWS_API_KEY", ""))

        col_news1, col_news2 = st.columns([3, 1])
        with col_news1:
            news_ticker = st.text_input(
                "Stock Symbol (Fetch News)",
                value="AAPL",
                label_visibility="collapsed",
                placeholder="e.g. AAPL, TESLA, Bitcoin"
            )
        with col_news2:
            news_btn = st.button("🔍 Analyze", use_container_width=True)

        if news_btn and news_ticker:
            if not news_key_set:
                st.warning("⚠️ NewsAPI key (`NEWS_API_KEY`) is not defined in `.streamlit/secrets.toml`. Live news fetching is disabled.")
                st.info("Analyzing with 5 sample headlines for testing...")
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
                st.error("No news found. Try changing the symbol or keyword.")
            else:
                with st.spinner("🧠 Running sentiment analysis..."):
                    report = analyze_sentiment(headlines)

                overall = report.get("overall_label", "neutral")
                avg_pol = report.get("average_polarity", 0.0)
                overall_color = LABEL_COLOR.get(overall, "white")
                overall_emoji = LABEL_EMOJI.get(overall, "⚪")

                # Summary card
                st.markdown(f"""
                    <div style="background: rgba(30,41,59,0.5); border-radius:20px; padding:30px; border:1px solid rgba(255,255,255,0.08); margin-bottom:25px;">
                        <h2 style="color:{overall_color}; margin:0; font-size:2.5rem;">{overall_emoji}</h2>
                        <p style="color:#94a3b8; margin:10px 0 0 0;">Average Sentiment Score: <strong style="color:white">{avg_pol:+.3f}</strong> &nbsp;|&nbsp; 
                        Analyzed: <strong style="color:white">{report.get("total_analyzed", 0)}</strong> headlines</p>
                    </div>
                """, unsafe_allow_html=True)

                # Per-headline table
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

                # Risk compatibility
                badge = _risk_badge(user_risk, overall)
                st.markdown(f"""
                    <div style="background: rgba(30,41,59,0.4); border-radius:16px; padding:20px; border:1px solid rgba(255,255,255,0.06); margin-top:20px;">
                        <h4 style="color:white; margin-bottom:8px;">🛡️ Risk Profile Compatibility</h4>
                        <p style="color:#94a3b8; margin:0;">Your Profile (<strong style="color:white">{user_risk}</strong>) + This News Sentiment = <strong style="color:white; font-size:1.2rem;">{badge}</strong></p>
                    </div>
                """, unsafe_allow_html=True)
