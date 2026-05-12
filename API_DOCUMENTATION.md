# FinTrack AI - Macro Level API Documentation

This document describes the external REST APIs (Macro-Level Architecture) integrated into the FinTrack AI platform over the network. These endpoints power the database, real-time market data, and AI-driven news sentiment analysis.

## 1. Authentication & Database API (Supabase)

FinTrack AI uses the Supabase REST API for secure authentication and data persistence. All requests are routed through the `supabase-py` SDK.

### Endpoint: Authentication
* **URL:** `POST https://<project-ref>.supabase.co/auth/v1/token?grant_type=password`
* **Purpose:** Authenticates a user and returns a session JWT.
* **Headers:** 
  * `apikey`: `<SUPABASE_KEY>`
* **Payload:** `{"email": "user@example.com", "password": "secure_password"}`
* **Returns:** JSON object containing `access_token` and `user` object.

### Endpoint: Database (Profiles)
* **URL:** `GET https://<project-ref>.supabase.co/rest/v1/profiles?id=eq.<user_id>`
* **Purpose:** Fetches the onboarding status and risk tolerance of a specific user.
* **Headers:**
  * `apikey`: `<SUPABASE_KEY>`
  * `Authorization`: `Bearer <access_token>`
* **Returns:** JSON array representing the user's profile data.

---

## 2. Market Data Integration (Yahoo Finance)

Real-time stock and cryptocurrency pricing data is primarily fetched via Yahoo Finance's Chart API.

### Endpoint: Chart Data
* **URL:** `GET https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d`
* **Purpose:** Retrieves historical closing prices and metadata for daily change calculations.
* **Headers:**
  * `User-Agent`: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`
* **Query Parameters:**
  * `symbol`: Asset ticker (e.g., `AAPL`, `BTC-USD`)
  * `interval`: `1d` (daily)
  * `range`: `5d` (5 days)
* **Returns:** JSON object containing `chart.result`, which includes `meta.regularMarketPrice` and `indicators.quote`.

---

## 3. Sentiment Analysis Data (NewsAPI)

Provides live headlines used by the TextBlob natural language processing module to determine market sentiment.

### Endpoint: Everything (News)
* **URL:** `GET https://newsapi.org/v2/everything`
* **Purpose:** Fetches recent news articles containing a specific financial keyword or stock ticker.
* **Headers:**
  * `X-Api-Key`: `<NEWS_API_KEY>`
* **Query Parameters:**
  * `q`: Keyword to search (e.g., `AAPL`)
  * `language`: `en`
  * `sortBy`: `publishedAt`
  * `pageSize`: `10`
* **Returns:** JSON object containing a `articles` array with `title` and `description` fields.

---

## 4. Alternative Quote Provider (Finnhub)

Used as a fallback mechanism for market pricing if Yahoo Finance is rate-limited.

### Endpoint: Quote
* **URL:** `GET https://finnhub.io/api/v1/quote`
* **Purpose:** Retrieves the current, high, low, and open prices for an asset.
* **Query Parameters:**
  * `symbol`: Asset ticker (e.g., `MSFT`)
  * `token`: `<FINNHUB_API_KEY>`
* **Returns:** JSON object containing `c` (current price) and `pc` (previous close).
