"""
news.py – Financial news fetcher.

Uses the NewsAPI (https://newsapi.org) to retrieve the latest headlines
related to a given stock ticker or company name.

Configuration is loaded from ``config.py`` — no secrets are hardcoded.
"""

import logging
from typing import List

import requests

<<<<<<< HEAD
from config import settings
=======
from ai.config import settings
>>>>>>> main

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_news(query: str, max_articles: int | None = None) -> List[str]:
    """
    Fetch financial news article titles for a given query (e.g. "AAPL").

    Parameters
    ----------
    query : str
        Search term – typically a stock ticker or company name.
    max_articles : int, optional
        Maximum number of titles to return.
        Falls back to ``settings.news_max_articles`` (default 10).

    Returns
    -------
    list[str]
        A list of article headline strings.  Returns an empty list on error.
    """
    if not settings.has_news_api_key:
        logger.error("NEWS_API_KEY is not set. Add it to your .env file.")
        return []

    if max_articles is None:
        max_articles = settings.news_max_articles

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles,
        "apiKey": settings.news_api_key,
    }

    try:
        response = requests.get(
            settings.news_api_url, params=params, timeout=15,
        )
        response.raise_for_status()

        data = response.json()
        articles = data.get("articles", [])

        # Extract only the titles, filtering out None values
        titles: List[str] = [
            article["title"]
            for article in articles
            if article.get("title")
        ]

        logger.info("Fetched %d headlines for '%s'.", len(titles), query)
        return titles

    except requests.exceptions.Timeout:
        logger.error("Request to NewsAPI timed out for query '%s'.", query)
    except requests.exceptions.HTTPError as exc:
        logger.error("HTTP error from NewsAPI: %s", exc)
    except requests.exceptions.RequestException as exc:
        logger.error("Network error while fetching news: %s", exc)
    except (KeyError, ValueError) as exc:
        logger.error("Failed to parse NewsAPI response: %s", exc)

    return []
