"""
ai – FinTrack AI analysis package.

Modules
-------
- ``config``     : Centralised settings (env vars, defaults).
- ``news``       : Financial news headline fetcher (NewsAPI).
- ``sentiment``  : TextBlob-based sentiment analysis.
- ``forecast``   : Prophet-based stock price forecasting.
- ``db``         : Supabase persistence layer.
- ``main``       : Pipeline orchestrator.
"""

from ai.config import settings
from ai.news import fetch_news
from ai.sentiment import analyze_sentiment
from ai.forecast import run_forecast
from ai.db import insert_sentiment, insert_sentiment_batch, fetch_sentiments
from ai.main import run_pipeline, PipelineResult

__all__ = [
    "settings",
    "fetch_news",
    "analyze_sentiment",
    "run_forecast",
    "insert_sentiment",
    "insert_sentiment_batch",
    "fetch_sentiments",
    "run_pipeline",
    "PipelineResult",
]
