import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st

def calculate_compound_interest(initial, monthly, rate, years):
    """
    Compound interest projection model.
    Parameters:
    - initial: Starting capital (TRY)
    - monthly: Amount to add each month (TRY)
    - rate: Expected annual return (%)
    - years: Investment horizon (years)
    """
    months = years * 12
    monthly_rate = (rate / 100) / 12

    future_values = []
    invested_amounts = []
    current_value = initial
    total_invested = initial

    for i in range(years + 1):
        if i == 0:
            future_values.append(current_value)
            invested_amounts.append(total_invested)
        else:
            for _ in range(12):
                current_value = current_value * (1 + monthly_rate) + monthly
                total_invested += monthly
            future_values.append(current_value)
            invested_amounts.append(total_invested)

    return future_values, invested_amounts, current_value, total_invested

@st.cache_data(ttl=3600)
def fetch_dividend_history(tickers):
    """
    Engine that pulls and processes historical dividend data.
    Uses Yahoo Finance (yfinance) for live market data.
    """
    data = []
    for t in tickers:
        try:
            ticker = yf.Ticker(t)
            divs = ticker.dividends

            if not divs.empty:
                last_div = float(divs.iloc[-1])
            else:
                last_div = 0.0

            try:
                current_price = float(ticker.fast_info['lastPrice'])
            except Exception:
                current_price = 0.0

            yield_pct = (last_div / current_price) * 100 if current_price > 0 else 0.0

            data.append({
                "Symbol": t.replace('.IS', ''),
                "Last dividend (TRY)": round(last_div, 2),
                "Yield (%)": round(yield_pct, 2),
                "Sector": "Automotive" if "FROTO" in t or "DOAS" in t else ("Energy/Industrial" if "TUPRS" in t or "ENJSA" in t else "Industrial/Other")
            })
        except Exception:
            pass

    return pd.DataFrame(data)

def get_sectoral_yields(df):
    """
    Builds sector-level dividend yield summary from company rows.
    """
    if df.empty: return df
    return df.groupby("Sector")["Yield (%)"].mean().reset_index().round(2)
