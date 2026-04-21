"""
config.py – Centralised configuration for the FinTrack AI pipeline.

All environment variables and tuneable defaults live here.
Every other module imports from ``config`` rather than calling
``os.getenv`` or ``load_dotenv`` on its own.

Environment variables are loaded **once** from the ``.env`` file
in the project root (one directory above ``ai/``).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Load .env exactly once (project root is one level above this package)
# ---------------------------------------------------------------------------
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Settings:
    """
    Immutable application settings populated from environment variables.

    All secrets come from the environment / ``.env`` file — nothing is
    hardcoded.  Sensible defaults are provided only for non-secret,
    tuneable parameters.
    """

    # ── External API keys (secrets — no defaults) ─────────────────────
    supabase_url: str = field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    supabase_key: str = field(default_factory=lambda: os.getenv("SUPABASE_KEY", ""))
    news_api_key: str = field(default_factory=lambda: os.getenv("NEWS_API_KEY", ""))

    # ── News fetcher ──────────────────────────────────────────────────
    news_api_url: str = "https://newsapi.org/v2/everything"
    news_max_articles: int = 10

    # ── Forecast ──────────────────────────────────────────────────────
    forecast_history_period: str = "1y"
    forecast_days: int = 15

    # ── Database ──────────────────────────────────────────────────────
    db_table_name: str = "sentiment_results"

    # ── Pipeline ──────────────────────────────────────────────────────
    default_ticker: str = "AAPL"

    # ── Helpers ───────────────────────────────────────────────────────

    @property
    def has_supabase_credentials(self) -> bool:
        """Return ``True`` if both Supabase URL and key are set."""
        return bool(self.supabase_url and self.supabase_key)

    @property
    def has_news_api_key(self) -> bool:
        """Return ``True`` if the NewsAPI key is set."""
        return bool(self.news_api_key)

    def validate(self) -> None:
        """
        Log warnings for any missing credentials.

        This does **not** raise — missing keys are handled gracefully by
        each module at call time.
        """
        if not self.has_news_api_key:
            logger.warning(
                "NEWS_API_KEY is not set. News fetching will be disabled. "
                "Get a free key at https://newsapi.org"
            )
        if not self.has_supabase_credentials:
            logger.warning(
                "SUPABASE_URL and/or SUPABASE_KEY are not set. "
                "Database operations will be disabled."
            )


# ---------------------------------------------------------------------------
# Module-level singleton — import this from other modules
# ---------------------------------------------------------------------------
settings = Settings()
