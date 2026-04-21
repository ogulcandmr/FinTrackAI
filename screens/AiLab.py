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
LABEL_EMOJI = {"positive": "🟢 Pozitif", "negative": "🔴 Negatif", "neutral": "⚪ Nötr"}

RISK_COMPATIBILITY = {
    "Çok Düşük":  {"positive": "✅ Uyumlu", "neutral": "⚠️ Dikkatli Ol", "negative": "🚫 Uyumsuz"},
    "Düşük":      {"positive": "✅ Uyumlu", "neutral": "⚠️ Dikkatli Ol", "negative": "🚫 Uyumsuz"},
    "Orta":       {"positive": "✅ Uyumlu", "neutral": "✅ Uyumlu",       "negative": "⚠️ Dikkatli Ol"},
    "Yüksek":     {"positive": "✅ Uyumlu", "neutral": "✅ Uyumlu",       "negative": "✅ Uyumlu"},
    "Çok Yüksek": {"positive": "✅ Uyumlu", "neutral": "✅ Uyumlu",       "negative": "✅ Uyumlu"},
}


def _risk_badge(user_risk: str, sentiment: str) -> str:
    """Kullanıcının risk profiline göre uyarı oluşturur."""
    table = RISK_COMPATIBILITY.get(user_risk, {})
    return table.get(sentiment, "⚠️ Bilinmiyor")


def render_ai_screen():
    st.markdown("""
        <div class="animate-page" style="background: rgba(15, 23, 42, 0.4); border-radius: 30px; padding: 40px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 2.5rem; backdrop-filter: blur(20px);">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem; font-weight: 800; letter-spacing: -1px;">🧠 AI Analiz Merkezi</h1>
            <p style="color: #94a3b8; font-size: 1.2rem; font-weight: 400;">Prophet fiyat tahmini, haber duygu analizi ve risk profil uyumluluk kontrolü.</p>
        </div>
        """, unsafe_allow_html=True)

    if not _AI_AVAILABLE:
        st.error("❌ AI modülleri yüklenemedi. `prophet`, `textblob` ve `requests` kütüphanelerinin yüklü olduğundan emin olun.")
        st.code("pip install prophet textblob requests", language="bash")
        return

    # Kullanıcının risk profili
    user = st.session_state.get("user", {})
    user_risk = st.session_state.get("user_risk_tolerance", "Orta")  # Onboarding'den gelirse

    tab1, tab2 = st.tabs(["📈 Fiyat Tahmini (Prophet)", "📰 Haber Duygu Analizi"])

    # ─── TAB 1: PROPHET FORECAST ─────────────────────────────────────────────
    with tab1:
        st.markdown("<h3 style='color:white; margin-bottom:20px;'>15 Günlük Fiyat Tahmini</h3>", unsafe_allow_html=True)

        col_input, col_run = st.columns([3, 1])
        with col_input:
            ticker_input = st.text_input(
                "Hisse / Kripto Sembolü",
                value="AAPL",
                placeholder="Örn: AAPL, MSFT, BTC-USD",
                label_visibility="collapsed"
            )
        with col_run:
            run_btn = st.button("🚀 Tahmin Et", use_container_width=True)

        if run_btn and ticker_input:
            with st.spinner(f"📊 {ticker_input.upper()} için Prophet modeli eğitiliyor... (bu 20-30 sn sürebilir)"):
                result = run_forecast(ticker_input.strip().upper())

            if result is None:
                st.error(f"❌ **{ticker_input.upper()}** için tahmin üretilemedi. Sembolü kontrol edin (Kripto için BTC-USD formatı kullanın).")
            else:
                preds = result["predictions"]
                hist = result["historical_df"]

                # Tarihsel + Tahmin Grafiği
                fig = go.Figure()
                # Son 60 gün tarihsel
                hist_tail = hist.tail(60)
                fig.add_trace(go.Scatter(
                    x=hist_tail["ds"], y=hist_tail["y"],
                    name="Tarihsel Kapanış",
                    line=dict(color="#3b82f6", width=2)
                ))
                # Prophet tahmini
                fig.add_trace(go.Scatter(
                    x=preds["ds"], y=preds["yhat"],
                    name="Tahmin (yhat)",
                    line=dict(color="#a855f7", width=3, dash="dot")
                ))
                # Güven aralığı
                fig.add_trace(go.Scatter(
                    x=pd.concat([preds["ds"], preds["ds"][::-1]]),
                    y=pd.concat([preds["yhat_upper"], preds["yhat_lower"][::-1]]),
                    fill="toself",
                    fillcolor="rgba(168, 85, 247, 0.15)",
                    line=dict(color="rgba(0,0,0,0)"),
                    name="Güven Aralığı"
                ))
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white"), margin=dict(l=0, r=0, t=30, b=0),
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
                    legend=dict(bgcolor="rgba(0,0,0,0)")
                )
                st.plotly_chart(fig, use_container_width=True)

                # Tahmin tablosu
                st.markdown("#### 📋 Tahmin Tablosu")
                preds_display = preds.copy()
                preds_display["ds"] = preds_display["ds"].dt.strftime("%Y-%m-%d")
                preds_display.columns = ["Tarih", "Tahmin", "Alt Sınır", "Üst Sınır"]
                st.dataframe(preds_display.style.format({"Tahmin": "${:.2f}", "Alt Sınır": "${:.2f}", "Üst Sınır": "${:.2f}"}), use_container_width=True, hide_index=True)

                # ── Risk Uyumluluk Kontrolü ────────────────────────────────
                trend = "positive" if preds["yhat"].iloc[-1] > preds["yhat"].iloc[0] else "negative"
                badge = _risk_badge(user_risk, trend)
                trend_label = "📈 Yükselen Trend" if trend == "positive" else "📉 Düşen Trend"
                color = "#10b981" if trend == "positive" else "#ef4444"

                st.markdown(f"""
                    <div style="background: rgba(30,41,59,0.5); border-radius:20px; padding:25px; border:1px solid rgba(255,255,255,0.08); margin-top:20px;">
                        <h4 style="color:white; margin-bottom:10px;">🛡️ Risk Profil Uyumluluk Kontrolü</h4>
                        <p style="color:#94a3b8; margin-bottom:5px;">Risk Toleransınız: <strong style="color:white">{user_risk}</strong></p>
                        <p style="color:#94a3b8; margin-bottom:5px;">Tahmin Trendi: <strong style="color:{color}">{trend_label}</strong></p>
                        <p style="font-size:1.3rem; font-weight:800; color:white; margin:15px 0 0 0;">{badge}</p>
                    </div>
                """, unsafe_allow_html=True)

    # ─── TAB 2: SENTIMENT ANALİZ ─────────────────────────────────────────────
    with tab2:
        st.markdown("<h3 style='color:white; margin-bottom:20px;'>Haber Duygu Analizi (Sentiment)</h3>", unsafe_allow_html=True)

        news_key_set = bool(st.secrets.get("NEWS_API_KEY", ""))

        col_news1, col_news2 = st.columns([3, 1])
        with col_news1:
            news_ticker = st.text_input(
                "Hisse Sembolü (Haber Çek)",
                value="AAPL",
                label_visibility="collapsed",
                placeholder="Örn: AAPL, TESLA, Bitcoin"
            )
        with col_news2:
            news_btn = st.button("🔍 Analiz Et", use_container_width=True)

        if news_btn and news_ticker:
            if not news_key_set:
                st.warning("⚠️ NewsAPI anahtarı (`NEWS_API_KEY`) `.streamlit/secrets.toml` dosyasında tanımlı değil. Anlık haber çekme devre dışı.")
                st.info("Test için 5 örnek başlık üzerinden analiz yapılıyor...")
                sample_headlines = [
                    f"{news_ticker} stock hits all-time high amid strong earnings",
                    f"Analysts bullish on {news_ticker} growth prospects",
                    f"{news_ticker} faces regulatory scrutiny in Europe",
                    f"Investors cautious as {news_ticker} misses revenue targets",
                    f"{news_ticker} announces new product line to boost market share",
                ]
                headlines = sample_headlines
            else:
                with st.spinner(f"📰 {news_ticker.upper()} için haberler çekiliyor..."):
                    headlines = fetch_news(news_ticker.strip())

            if not headlines:
                st.error("Haber bulunamadı. Sembolü veya anahtar kelimeyi değiştirip tekrar deneyin.")
            else:
                with st.spinner("🧠 Duygu analizi yapılıyor..."):
                    report = analyze_sentiment(headlines)

                overall = report.get("overall_label", "neutral")
                avg_pol = report.get("average_polarity", 0.0)
                overall_color = LABEL_COLOR.get(overall, "white")
                overall_emoji = LABEL_EMOJI.get(overall, "⚪")

                # Özet kart
                st.markdown(f"""
                    <div style="background: rgba(30,41,59,0.5); border-radius:20px; padding:30px; border:1px solid rgba(255,255,255,0.08); margin-bottom:25px;">
                        <h2 style="color:{overall_color}; margin:0; font-size:2.5rem;">{overall_emoji}</h2>
                        <p style="color:#94a3b8; margin:10px 0 0 0;">Ortalama Duygu Skoru: <strong style="color:white">{avg_pol:+.3f}</strong> &nbsp;|&nbsp; 
                        Analiz Edilen: <strong style="color:white">{report.get("total_analyzed", 0)}</strong> başlık</p>
                    </div>
                """, unsafe_allow_html=True)

                # Per-headline tablo
                items = report.get("items", [])
                rows_display = []
                for item in items:
                    lbl = item["label"]
                    rows_display.append({
                        "Başlık": item["text"][:100],
                        "Duygu": LABEL_EMOJI.get(lbl, lbl),
                        "Skor": round(item["polarity"], 3),
                    })
                if rows_display:
                    df_items = pd.DataFrame(rows_display)
                    st.dataframe(df_items, use_container_width=True, hide_index=True)

                # Risk uyumluluk
                badge = _risk_badge(user_risk, overall)
                st.markdown(f"""
                    <div style="background: rgba(30,41,59,0.4); border-radius:16px; padding:20px; border:1px solid rgba(255,255,255,0.06); margin-top:20px;">
                        <h4 style="color:white; margin-bottom:8px;">🛡️ Risk Profil Uyumluluk</h4>
                        <p style="color:#94a3b8; margin:0;">Profiliniz (<strong style="color:white">{user_risk}</strong>) + Bu Haber Duygusu = <strong style="color:white; font-size:1.2rem;">{badge}</strong></p>
                    </div>
                """, unsafe_allow_html=True)
