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

from config import settings
from news import fetch_news
from sentiment import analyze_sentiment
from forecast import run_forecast
from db import insert_sentiment, insert_sentiment_batch, fetch_sentiments
from main import run_pipeline, PipelineResult

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
