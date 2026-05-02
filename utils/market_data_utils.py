# FinTrackAI - İnternetten canlı fiyat: tüm alternatif yollar denenir
# 1) Yahoo Chart API (doğrudan HTTP) 2) yfinance 3) ccxt 4) Yahoo -USD/.IS 5) Finnhub (opsiyonel)

from typing import Optional, Tuple
import logging
import json
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

# Tarayıcı benzeri User-Agent (Yahoo bazen bot isteklerini engeller)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# TRY->USD için sabit kur (1 USD = 44 TL)
USD_TO_TRY = 44.0

# Son güvenli fiyat cache (process bazlı)
_LAST_GOOD_PRICE_USD = {}  # symbol -> float
_LAST_PRICE_WARNING = {}   # symbol -> str

# Yaygın kripto kısaltmaları (BTC yazınca 30$ gibi yanlış enstrüman gelmesini önlemek için)
COMMON_CRYPTO = {
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC", "AVAX",
    "LTC", "LINK", "ATOM", "BCH", "TRX", "ETC", "XLM", "NEAR", "FIL", "APT",
    "ARB", "OP", "SUI", "TON", "PEPE", "SHIB", "UNI", "AAVE", "INJ", "ICP",
}


def _looks_like_crypto_symbol(sym: str) -> bool:
    s = str(sym or "").strip().upper()
    if not s:
        return False
    if "/" in s:
        return True
    # BTC, ETH gibi bilinen kısaltmalar
    if s in COMMON_CRYPTO:
        return True
    return False


def get_last_price_warning(symbol: str) -> Optional[str]:
    """Son fiyat çekiminde anormallik filtresi devreye girdiyse mesaj döner."""
    if not symbol:
        return None
    return _LAST_PRICE_WARNING.get(str(symbol).strip().upper())


def clear_price_cache():
    """Son güvenli fiyat cache'ini sıfırlar (yanlış fiyat yakalandıysa toparlamak için)."""
    _LAST_GOOD_PRICE_USD.clear()
    _LAST_PRICE_WARNING.clear()


def _apply_sanity_filter(symbol: str, new_price_usd: Optional[float]) -> Optional[float]:
    """
    Hatalı kaynak/para birimi vb. durumlarda oluşan gerçek dışı sıçramaları engeller.
    - Kripto: daha volatil → daha geniş tolerans
    - Hisse: daha dar tolerans
    """
    sym = str(symbol or "").strip().upper()
    if new_price_usd is None:
        return None
    try:
        p = float(new_price_usd)
    except Exception:
        return None
    if p <= 0 or p != p:  # NaN kontrolü
        return None

    prev = _LAST_GOOD_PRICE_USD.get(sym)
    # İlk ölçüm: direkt kabul
    if prev is None or prev <= 0:
        _LAST_GOOD_PRICE_USD[sym] = p
        _LAST_PRICE_WARNING.pop(sym, None)
        return p

    # Mutlak akıl sınırları (USD)
    if p < 0.000001 or p > 1_000_000_000:
        _LAST_PRICE_WARNING[sym] = "Price looked abnormal; last safe quote was kept."
        return prev

    rel = abs(p - prev) / prev if prev else 0.0
    is_crypto = _looks_like_crypto_symbol(sym)
    # 2 dakikalık yenilemede gerçek dışı sıçrama eşiği
    max_rel = 1.00 if is_crypto else 0.50   # kripto %100, hisse %50

    # 5x üzeri veya 5x altı gibi “çarpan hatası” yakalama (örn. TRY/USD karışması)
    if p > prev * 5 or p < prev / 5:
        _LAST_PRICE_WARNING[sym] = "Unrealistic jump detected; last safe quote was kept."
        return prev

    if rel > max_rel:
        _LAST_PRICE_WARNING[sym] = "Extreme price move detected; last safe quote was kept."
        return prev

    _LAST_GOOD_PRICE_USD[sym] = p
    _LAST_PRICE_WARNING.pop(sym, None)
    return p


def _convert_price_to_usd(price: float, currency: Optional[str]) -> float:
    """
    Veri kaynağı TRY döndürüyorsa USD'ye çevirir.
    Bu projede kur sabiti: 1 USD = 44 TL.
    """
    cur = (currency or "").upper().strip()
    if cur == "TRY":
        return float(price) / USD_TO_TRY
    return float(price)


def _fetch_yahoo_chart_api(symbol: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Yahoo'nun doğrudan chart API'si (query1.finance.yahoo.com).
    yfinance'tan bağımsız; tarayıcının kullandığı aynı kaynak.
    """
    symbol = str(symbol).strip().upper()
    if not symbol:
        return None, None
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read().decode()
        if not raw.strip().startswith("{"):
            logger.debug("Yahoo Chart API %s: JSON değil", symbol)
            return None, None
        data = json.loads(raw)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as e:
        logger.debug("Yahoo Chart API %s: %s", symbol, e)
        return None, None
    try:
        result = data.get("chart", {}).get("result")
        if not result:
            return None, None
        meta = result[0].get("meta", {}) or {}
        currency = meta.get("currency")
        price = meta.get("regularMarketPrice")
        if price is not None:
            return float(price), currency
        # Son kapanış
        quotes = result[0].get("indicators", {}).get("quote", [{}])
        if quotes and quotes[0].get("close"):
            closes = [c for c in quotes[0]["close"] if c is not None]
            if closes:
                return float(closes[-1]), currency
    except (IndexError, KeyError, TypeError) as e:
        logger.debug("Yahoo Chart parse %s: %s", symbol, e)
    return None, None


def _fetch_yf(symbol: str) -> Tuple[Optional[float], Optional[str]]:
    """yfinance: önce history (daha güvenilir), sonra info."""
    try:
        import yfinance as yf
        t = yf.Ticker(symbol)
        for period in ("1d", "5d"):
            hist = t.history(period=period)
            if hist is not None and not hist.empty and "Close" in hist.columns:
                # currency çoğu zaman info'da
                info = getattr(t, "info", None) or {}
                currency = info.get("currency") if isinstance(info, dict) else None
                return float(hist["Close"].iloc[-1]), currency
        info = getattr(t, "info", None) or {}
        if isinstance(info, dict):
            currency = info.get("currency")
            for key in ("currentPrice", "regularMarketPrice", "previousClose", "open"):
                v = info.get(key)
                if v is not None and isinstance(v, (int, float)):
                    return float(v), currency
    except Exception as e:
        logger.debug("yfinance %s: %s", symbol, e)
    return None, None


def _fetch_ccxt(symbol: str) -> Optional[float]:
    """ccxt Binance (USDT ≈ USD)."""
    try:
        import ccxt
        s = str(symbol).strip().upper().replace("-", "")
        if "/" not in s:
            s = s + "/USDT"
        exchange = ccxt.binance({"enableRateLimit": True, "timeout": 15000})
        ticker = exchange.fetch_ticker(s)
        if ticker and ticker.get("last") is not None:
            return float(ticker["last"])
    except Exception as e:
        logger.debug("ccxt %s: %s", symbol, e)
    return None


def _fetch_finnhub(symbol: str) -> Optional[float]:
    """Finnhub Quote API (ücretsiz tier). FINNHUB_API_KEY .streamlit/secrets.toml veya env'de."""
    try:
        import os
        key = os.environ.get("FINNHUB_API_KEY", "")
        if not key:
            try:
                import streamlit as st
                key = (st.secrets.get("FINNHUB_API_KEY") or "") if hasattr(st, "secrets") else ""
            except Exception:
                key = ""
        if not key:
            return None
        import urllib.request
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={key}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        c = data.get("c")  # current price
        if c is not None:
            return float(c)
    except Exception as e:
        logger.debug("finnhub %s: %s", symbol, e)
    return None


def _get_current_price_raw(symbol: str) -> Optional[float]:
    """
    Yazılan sembol için internetten fiyat (USD) çeker.
    Sıra: 1) Yahoo Chart API 2) yfinance 3) Yahoo -USD/.IS 4) ccxt 5) Finnhub (key varsa).
    """
    if not symbol or not str(symbol).strip():
        return None
    raw = str(symbol).strip()
    sym_upper = raw.upper()

    # Kriptoda (BTC, ETH, BTC/USDT) öncelik: ccxt veya BTC-USD (Yahoo),
    # çünkü 'BTC' gibi semboller Yahoo'da yanlış enstrümana denk gelebiliyor.
    if _looks_like_crypto_symbol(sym_upper):
        p = _fetch_ccxt(sym_upper)
        if p is not None and p > 0:
            return p

    # Hisse: önce düz sembol (AAPL, TTWO, ASELS), sonra TR .IS. Kripto: -USD ve düz.
    if _looks_like_crypto_symbol(sym_upper):
        variants = [sym_upper + "-USD", sym_upper]
    else:
        variants = [sym_upper]
        if len(sym_upper) <= 6 and "." not in sym_upper:
            variants.append(sym_upper + ".IS")

    # 1) Yahoo Chart API (doğrudan HTTP) — hisseler doğru kaynaktan
    for sym in variants:
        p, cur = _fetch_yahoo_chart_api(sym)
        if p is not None and p > 0:
            return _convert_price_to_usd(p, cur)

    # 2) yfinance
    for sym in variants:
        p, cur = _fetch_yf(sym)
        if p is not None and p > 0:
            return _convert_price_to_usd(p, cur)

    # 3) Binance (kripto)
    p = _fetch_ccxt(sym_upper)
    if p is not None and p > 0:
        return p

    # 4) Finnhub (API key varsa)
    p = _fetch_finnhub(sym_upper)
    if p is not None and p > 0:
        return p

    return None


def get_current_price(symbol: str) -> Optional[float]:
    """Doğrudan doğru kaynaktan fiyat çeker (sanity filter kapalı, her seferinde güncel)."""
    sym = str(symbol or "").strip().upper()
    raw = _get_current_price_raw(sym)
    if raw is not None and raw > 0:
        return raw
    return None


def _symbol_for_ccxt(symbol: str) -> str:
    s = str(symbol).strip().upper().replace("-", "")
    return s if "/" in s else s + "/USDT"


def get_daily_change(symbol: str) -> Tuple[Optional[float], Optional[float]]:
    """Günlük değişim: (yüzde, mutlak fark USD). Önce Yahoo Chart, sonra yfinance, sonra ccxt."""
    if not symbol or not str(symbol).strip():
        return None, None
    symbol = str(symbol).strip().upper()

    # Yahoo Chart API ile son iki gün
    # Kripto ise önce -USD (BTC-USD) veya ccxt kullanımı daha doğru
    if _looks_like_crypto_symbol(symbol):
        try:
            import ccxt
            exchange = ccxt.binance({"enableRateLimit": True, "timeout": 15000})
            ticker = exchange.fetch_ticker(_symbol_for_ccxt(symbol))
            if ticker and ticker.get("last") is not None and ticker.get("open") not in (None, 0):
                last = float(ticker["last"])
                open_ = float(ticker["open"])
                abs_ch = last - open_
                pct = (abs_ch / open_) * 100.0
                return pct, abs_ch
        except Exception:
            pass

    if "." not in symbol and "/" not in symbol:
        if _looks_like_crypto_symbol(symbol):
            yahoo_tries = [symbol + "-USD", symbol]
        else:
            yahoo_tries = [symbol, symbol + ".IS"]
    else:
        yahoo_tries = [symbol]

    for sym_try in yahoo_tries:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym_try}?interval=1d&range=5d"
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
            result = data.get("chart", {}).get("result")
            if not result:
                continue
            meta = result[0].get("meta", {}) or {}
            currency = meta.get("currency")
            quotes = result[0].get("indicators", {}).get("quote", [{}])
            if not quotes or not quotes[0].get("close"):
                continue
            closes = [c for c in quotes[0]["close"] if c is not None]
            if len(closes) >= 2:
                close_today = _convert_price_to_usd(float(closes[-1]), currency)
                close_prev = _convert_price_to_usd(float(closes[-2]), currency)
                if close_prev and close_prev > 0:
                    abs_ch = close_today - close_prev
                    pct = (abs_ch / close_prev) * 100.0
                    return pct, abs_ch
        except Exception:
            continue

    # yfinance
    try:
        import yfinance as yf
        for sym_try in [symbol, symbol + "-USD", symbol + ".IS"]:
            if "/" in sym_try:
                continue
            try:
                t = yf.Ticker(sym_try)
                hist = t.history(period="5d")
                if hist is not None and len(hist) >= 2 and "Close" in hist.columns:
                    info = getattr(t, "info", None) or {}
                    currency = info.get("currency") if isinstance(info, dict) else None
                    close_today = _convert_price_to_usd(float(hist["Close"].iloc[-1]), currency)
                    close_prev = _convert_price_to_usd(float(hist["Close"].iloc[-2]), currency)
                    if close_prev and close_prev > 0:
                        abs_ch = close_today - close_prev
                        pct = (abs_ch / close_prev) * 100.0
                        return pct, abs_ch
            except Exception:
                continue
    except Exception:
        pass

    # ccxt
    try:
        import ccxt
        exchange = ccxt.binance({"enableRateLimit": True, "timeout": 15000})
        ticker = exchange.fetch_ticker(_symbol_for_ccxt(symbol))
        if ticker and ticker.get("last") is not None and ticker.get("open") not in (None, 0):
            last = float(ticker["last"])
            open_ = float(ticker["open"])
            abs_ch = last - open_
            pct = (abs_ch / open_) * 100.0
            return pct, abs_ch
    except Exception as e:
        logger.debug("ccxt daily %s: %s", symbol, e)

    return None, None


def get_prices_batch(symbols: list) -> dict:
    """Birden fazla sembol için internetten fiyat çeker. Key: sembol (upper), Value: fiyat veya None."""
    result = {}
    for s in symbols:
        if not s:
            continue
        key = str(s).strip().upper()
        if key not in result:
            result[key] = get_current_price(key)
    return result
