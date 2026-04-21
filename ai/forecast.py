"""
forecast.py – Stock price forecasting with Prophet.

Downloads historical closing-price data via yfinance, prepares it for
Prophet, trains a model, and returns a 15-day-ahead prediction as a
pandas DataFrame.

Configuration defaults are loaded from ``config.py``.

Example
-------
>>> from forecast import run_forecast
>>> result = run_forecast("AAPL")
>>> result["predictions"].head()
          ds       yhat  yhat_lower  yhat_upper
0 2026-04-22  198.1234     195.432     200.814
"""

import logging
from typing import Any, Dict, Optional

import pandas as pd
import yfinance as yf
from prophet import Prophet

from config import settings

logger = logging.getLogger(__name__)

# Type alias for the structured return value
ForecastResultDict = Dict[str, Any]

# ---------------------------------------------------------------------------
# Step helpers (each encapsulates one pipeline stage)
# ---------------------------------------------------------------------------


def _download_history(ticker: str, period: str) -> Optional[pd.DataFrame]:
    """
    Download historical closing prices for *ticker*.

    Parameters
    ----------
    ticker : str
        Stock symbol (e.g. "AAPL", "MSFT").
    period : str
        Look-back window accepted by yfinance (e.g. "1y", "6mo").

    Returns
    -------
    pd.DataFrame | None
        DataFrame with columns ``['ds', 'y']`` ready for Prophet,
        or ``None`` if the download fails or returns no data.
    """
    logger.info("Downloading %s history for '%s'…", period, ticker)

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
    except Exception as exc:  # noqa: BLE001
        logger.error("yfinance download failed for '%s': %s", ticker, exc)
        return None

    if hist.empty:
        logger.error("No historical data returned for '%s'.", ticker)
        return None

    # Keep only the 'Close' column and drop any NaN rows
    df = hist[["Close"]].dropna().reset_index()
    df.columns = ["ds", "y"]

    # Prophet requires timezone-naive datetime
    df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)

    logger.info("Downloaded %d rows of history for '%s'.", len(df), ticker)
    return df


def _build_and_train_model(df: pd.DataFrame) -> Prophet:
    """
    Instantiate and fit a Prophet model on prepared data.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ``ds`` (datetime) and ``y`` (float) columns.

    Returns
    -------
    Prophet
        A fitted Prophet model instance.
    """
    model = Prophet(
        daily_seasonality=False,
        yearly_seasonality=True,
        weekly_seasonality=True,
        changepoint_prior_scale=0.05,   # conservative trend flexibility
    )

    # Suppress Prophet's internal stdout logging
    model.fit(df)
    return model


def _generate_predictions(
    model: Prophet,
    days: int,
) -> pd.DataFrame:
    """
    Create a future dataframe and run prediction.

    Parameters
    ----------
    model : Prophet
        A fitted Prophet model.
    days : int
        Number of future days to predict.

    Returns
    -------
    pd.DataFrame
        Forecast dataframe with columns
        ``['ds', 'yhat', 'yhat_lower', 'yhat_upper']``
        containing **only** the future rows (not in-sample).
    """
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    # Return only the future (out-of-sample) rows
    predictions = forecast.tail(days)[
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ].reset_index(drop=True)

    # Round for readability
    for col in ["yhat", "yhat_lower", "yhat_upper"]:
        predictions[col] = predictions[col].round(2)

    return predictions


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_forecast(
    ticker: str,
    period: str | None = None,
    days: int | None = None,
) -> Optional[ForecastResultDict]:
    """
    End-to-end stock price forecast for *ticker*.

    Pipeline
    --------
    1. Download historical close prices via yfinance.
    2. Format as ``(ds, y)`` DataFrame for Prophet.
    3. Train a Prophet model.
    4. Forecast the next *days* trading days.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g. ``"AAPL"``).
    period : str, optional
        How far back to fetch history.
        Falls back to ``settings.forecast_history_period``.
    days : int, optional
        How many days ahead to predict.
        Falls back to ``settings.forecast_days``.

    Returns
    -------
    dict | None
        A structured dictionary on success::

            {
                "ticker":           str,
                "history_rows":     int,
                "forecast_days":    int,
                "predictions":      pd.DataFrame,   # ds, yhat, yhat_lower, yhat_upper
                "historical_df":    pd.DataFrame,    # ds, y
            }

        Returns ``None`` if any stage fails.

    Example
    -------
    >>> result = run_forecast("AAPL")
    >>> print(result["predictions"])
    """
    if period is None:
        period = settings.forecast_history_period
    if days is None:
        days = settings.forecast_days

    # ── Validate inputs ───────────────────────────────────────────────
    if not ticker or not isinstance(ticker, str):
        logger.error("Invalid ticker: %r", ticker)
        return None

    ticker = ticker.upper().strip()

    if days < 1:
        logger.error("forecast days must be >= 1, got %d", days)
        return None

    # ── Step 1 & 2: Download + format ─────────────────────────────────
    df = _download_history(ticker, period)
    if df is None:
        return None

    # ── Step 3: Train ─────────────────────────────────────────────────
    try:
        logger.info("Fitting Prophet model for '%s'…", ticker)
        model = _build_and_train_model(df)
    except Exception as exc:  # noqa: BLE001
        logger.error("Model training failed for '%s': %s", ticker, exc)
        return None

    # ── Step 4: Predict ───────────────────────────────────────────────
    try:
        predictions = _generate_predictions(model, days)
    except Exception as exc:  # noqa: BLE001
        logger.error("Prediction generation failed for '%s': %s", ticker, exc)
        return None

    logger.info(
        "Forecast complete for '%s' – %d future rows generated.",
        ticker, days,
    )

    return {
        "ticker": ticker,
        "history_rows": len(df),
        "forecast_days": days,
        "predictions": predictions,
        "historical_df": df,
    }
