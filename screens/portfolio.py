# FinTrackAI - 2. Kısım: Portföy Yönetimi (Veri Katmanı ve Cüzdan Yönetimi)
# Fiyatlar USD; kar/zarar TL (1 USD = 44 TL).

import streamlit as st
from datetime import date
from utils.supabase_utils import portfolio_insert, portfolio_select_by_user, portfolio_delete
from utils.portfolio_engine import compute_portfolio_pnl
from utils.market_data_utils import get_current_price

# [Geri almak için: POPULAR_ASSETS listesini ve "Popüler hisse ve kriptolar" form bloğunu silin]
POPULAR_ASSETS = [
    ("Apple", "AAPL"), ("Microsoft", "MSFT"), ("Google", "GOOGL"), ("Amazon", "AMZN"), ("Nvidia", "NVDA"),
    ("Tesla", "TSLA"), ("Meta", "META"), ("Netflix", "NFLX"), ("Adobe", "ADBE"), ("PayPal", "PYPL"),
    ("Take-Two", "TTWO"), ("JPMorgan", "JPM"), ("Visa", "V"), ("Mastercard", "MA"), ("Walmart", "WMT"), ("Coca-Cola", "KO"),
    ("Bitcoin", "BTC"), ("Ethereum", "ETH"), ("Binance Coin", "BNB"), ("Solana", "SOL"), ("XRP", "XRP"),
    ("Cardano", "ADA"), ("Dogecoin", "DOGE"), ("Polkadot", "DOT"), ("Avalanche", "AVAX"), ("Chainlink", "LINK"),
    ("Polygon", "MATIC"), ("Litecoin", "LTC"), ("Uniswap", "UNI"), ("Shiba Inu", "SHIB"), ("Toncoin", "TON"),
]

try:
    from streamlit_autorefresh import st_autorefresh
    _AUTOREFRESH_AVAILABLE = True
except Exception:
    _AUTOREFRESH_AVAILABLE = False


def _fmt_money(val: float) -> str:
    if val >= 0:
        return f"+{val:,.2f}"
    return f"{val:,.2f}"


def _fmt_pct(val: float) -> str:
    if val >= 0:
        return f"+%{val:.2f}"
    return f"%{val:.2f}"


def render_portfolio_screen():
    user = st.session_state.get("user")
    if not user:
        st.warning("Portföy için giriş yapmalısınız.")
        return

    user_id = user["id"]

    if _AUTOREFRESH_AVAILABLE:
        st_autorefresh(interval=2 * 60 * 1000, key="portfolio_autorefresh")

    # Ana başlık
    st.markdown("""
        <div class="animate-page" style="background: rgba(15, 23, 42, 0.4); border-radius: 30px; padding: 40px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 2rem; backdrop-filter: blur(20px);">
            <h1 style="font-size: 3rem; margin-bottom: 0; font-weight: 800;">💼 Veri Katmanı ve Cüzdan Yönetimi</h1>
        </div>
        """, unsafe_allow_html=True)

    _fragment = getattr(st, "fragment", lambda f: f)

    @_fragment
    def _portfolio_content():
        rows = portfolio_select_by_user(user_id)
        enriched_rows, summary = compute_portfolio_pnl(rows)

        # --- Özet kartları (TL) ---
        card_css = """
        <div style="background: rgba(30, 41, 59, 0.5); padding: 28px; border-radius: 25px; border: 1px solid rgba(255,255,255,0.05); backdrop-filter: blur(20px);">
            <p style="color: #64748b; font-size: 0.85rem; margin-bottom: 10px; font-weight: 700; text-transform: uppercase;">{title}</p>
            <h2 style="font-size: 2.2rem; margin: 0; color: {val_color}; font-weight: 800;">{value}</h2>
            <p style="color: {sub_color}; font-size: 0.95rem; font-weight: 600; margin: 8px 0 0 0;">{sub}</p>
        </div>
        """
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(card_css.format(
                title="📊 Toplam Varlık (TL)",
                value=f"{summary['total_value_tl']:,.2f} TL",
                val_color="white",
                sub=f"{summary['total_value_usd']:,.2f} USD · Maliyet: {summary['total_cost_tl']:,.2f} TL",
                sub_color="#94a3b8"
            ), unsafe_allow_html=True)
        with col2:
            daily_tl = summary["daily_change_tl"]
            daily_pct = summary["daily_change_pct"]
            daily_color = "#10b981" if daily_tl >= 0 else "#ef4444"
            st.markdown(card_css.format(
                title="📈 Günlük Değişim (TL)",
                value=f"{_fmt_money(daily_tl)} TL",
                val_color=daily_color,
                sub=_fmt_pct(daily_pct),
                sub_color=daily_color
            ), unsafe_allow_html=True)
        with col3:
            pnl_tl = summary["total_pnl_tl"]
            pnl_pct = summary["total_pnl_pct"]
            pnl_color = "#10b981" if pnl_tl >= 0 else "#ef4444"
            st.markdown(card_css.format(
                title="💰 Toplam Kar/Zarar (TL)",
                value=f"{_fmt_money(pnl_tl)} TL",
                val_color=pnl_color,
                sub=_fmt_pct(pnl_pct),
                sub_color=pnl_color
            ), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Yeni hisse: popüler hızlı ekle + elle giriş ---
        with st.expander("➕ Yeni Hisse Ekle", expanded=not enriched_rows):
            # Bilindik hisse/kripto — hızlı ekle (satır hizalı)
            st.markdown("**Bilindik şirketlerin hisse ve kriptoları**")
            st.markdown("""
                <style>
                [data-testid="stForm"] [data-testid="column"] > div { align-items: flex-end !important; }
                [data-testid="stForm"] [data-testid="stNumberInput"] { margin-top: 0 !important; }
                </style>
                """, unsafe_allow_html=True)
            popular_options = [f"{label} ({sym})" for label, sym in POPULAR_ASSETS]
            with st.form("quick_add_popular"):
                qcol1, qcol2, qcol3 = st.columns([2, 1.1, 1])
                with qcol1:
                    quick_choice = st.selectbox("Varlık", options=popular_options, key="quick_choice", label_visibility="collapsed")
                with qcol2:
                    quick_qty = st.number_input("Adet", min_value=0.0, value=0.0, step=0.01, format="%.4f", key="quick_qty", label_visibility="collapsed")
                with qcol3:
                    quick_submit = st.form_submit_button("Hızlı Ekle")
                if quick_submit and quick_choice and quick_qty > 0:
                    # Sembolü seçenek metninden çıkar: "Apple (AAPL)" -> AAPL
                    sym = quick_choice.split("(")[-1].rstrip(")")
                    with st.spinner("Fiyat getiriliyor..."):
                        price = get_current_price(sym)
                    if price and price > 0:
                        data, err = portfolio_insert(user_id, sym, str(date.today()), price, quick_qty)
                        if err:
                            st.error(f"Eklenemedi: {err}")
                        else:
                            st.success(f"**{sym}** {quick_qty:,.4f} adet eklendi (güncel fiyat: {price:,.2f} USD).")
                            st.rerun()
                    else:
                        st.error(f"{sym} için fiyat alınamadı. Lütfen 'Kar/Zararı güncelle' sonra tekrar deneyin.")
                elif quick_submit and quick_qty <= 0:
                    st.warning("Adet 0'dan büyük olmalı.")

            st.markdown("---")
            r1, r2 = st.columns([2, 1])
            with r1:
                suggest_symbol = st.text_input("Hisse veya kripto sembolü", key="suggest_sym", placeholder="Örn: AAPL, TTWO, BTC, ETH, XRP, THYAO")
            with r2:
                st.markdown("<br>", unsafe_allow_html=True)
                get_price_btn = st.button("🔃 Fiyat getir (USD)")
            if get_price_btn and suggest_symbol:
                with st.spinner("Fiyat getiriliyor..."):
                    p = get_current_price(suggest_symbol.strip())
                if p is not None and p > 0:
                    st.session_state["portfolio_suggested_price"] = p
                    st.session_state["portfolio_suggested_symbol"] = suggest_symbol.strip().upper()
                    st.success(f"**{suggest_symbol.strip().upper()}** güncel fiyat: **{p:,.2f} USD** — Aşağıdaki formda alış fiyatı alanı güncellendi.")
                    st.rerun()
                else:
                    st.error("Bu sembol için fiyat alınamadı. Sembolü kontrol edip tekrar deneyin (örn: AAPL, TTWO, BTC, ETH).")
                    if "portfolio_suggested_price" in st.session_state:
                        del st.session_state["portfolio_suggested_price"]

            with st.form("portfolio_add_form"):
                c1, c2 = st.columns(2)
                with c1:
                    asset_id = st.text_input(
                        "Varlık sembolü (Hisse: AAPL, TTWO | Kripto: BTC, ETH veya BTC/USDT)",
                        value=st.session_state.get("portfolio_suggested_symbol", ""),
                        placeholder="AAPL veya BTC",
                        key="form_asset"
                    )
                    purchase_date = st.date_input("Alış tarihi", value=date.today(), key="form_date")
                with c2:
                    default_price = st.session_state.get("portfolio_suggested_price") or 0.0
                    price = st.number_input("Alış fiyatı (USD, birim)", min_value=0.0, value=float(default_price), step=0.01, format="%.4f", key="form_price")
                    quantity = st.number_input("Adet", min_value=0.0, value=0.0, step=0.0001, format="%.4f", key="form_qty")
                if st.form_submit_button("Portföye Ekle"):
                    if not (asset_id and price > 0 and quantity > 0):
                        st.error("Varlık sembolü, fiyat (USD) ve adet zorunludur (pozitif).")
                    else:
                        data, err = portfolio_insert(user_id, asset_id.strip().upper(), str(purchase_date), price, quantity)
                        if err:
                            st.error(f"Eklenemedi: {err}")
                        else:
                            if "portfolio_suggested_price" in st.session_state:
                                del st.session_state["portfolio_suggested_price"]
                            if "portfolio_suggested_symbol" in st.session_state:
                                del st.session_state["portfolio_suggested_symbol"]
                            st.success("Pozisyon eklendi. Fiyatlar USD; kar/zarar TL (1 USD = 44 TL) hesaplanır.")
                            st.rerun()

        # --- Hisseler: USD fiyat + TL kar/zarar ---
        st.markdown("### 📋 Hisseler")
        if st.button("🔄 Kar/Zararı güncelle", key="manual_refresh_list", use_container_width=True):
            pass
        st.markdown("<br>", unsafe_allow_html=True)
        if not enriched_rows:
            st.info("Henüz hisse yok. Yukarıdan 'Yeni Hisse Ekle' ile ekleyebilirsiniz.")
            return

        for i, row in enumerate(enriched_rows):
            rid = row.get("id")
            pnl_tl = row.get("pnl_tl", 0)
            pnl_color = "#10b981" if pnl_tl >= 0 else "#ef4444"
            current_usd = float(row.get("current_price", 0))
            purchase_usd = float(row.get("price", 0))
            warn = row.get("price_warning")
            with st.container():
                st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.4); border-radius: 16px; padding: 20px; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.06);">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                            <div>
                                <strong style="font-size: 1.1rem;">{row.get('asset_id', '-')}</strong>
                                <span style="color: #64748b; margin-left: 10px;">Alış: {row.get('purchase_date', '-')} · {float(row.get('quantity', 0)):,.4f} adet @ {purchase_usd:,.2f} USD</span>
                            </div>
                            <div style="text-align: right;">
                                <span style="color: #94a3b8;">Güncel: <strong>{current_usd:,.2f} USD</strong></span>
                                <span style="margin-left: 14px; color: {pnl_color}; font-weight: 700;">{_fmt_money(pnl_tl)} TL ({_fmt_pct(row.get('pnl_pct', 0))})</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                if warn:
                    st.warning(f"⚠️ {warn}", icon="⚠️")
                col_a, col_b = st.columns([5, 1])
                with col_b:
                    if st.button("🗑️ Sil", key=f"del_{rid}_{i}"):
                        ok, err = portfolio_delete(rid, user_id)
                        if ok:
                            st.success("Kayıt silindi.")
                            st.rerun()
                        else:
                            st.error(err or "Silinemedi.")
                st.markdown("---")

    _portfolio_content()
