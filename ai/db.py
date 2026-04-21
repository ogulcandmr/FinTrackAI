"""
db.py – Supabase database integration.

Provides reusable functions to insert and retrieve sentiment analysis
results from the ``sentiment_results`` table.

Configuration is loaded from ``config.py`` — no secrets are hardcoded.

Table schema
------------
    id          BIGINT   (auto-generated)
    stock       TEXT     – ticker symbol (e.g. "AAPL")
    sentiment   TEXT     – label: "positive" | "negative" | "neutral"
    score       FLOAT8   – polarity score (-1.0 … +1.0)
    created_at  TIMESTAMPTZ (defaults to now())

Setup SQL
---------
    CREATE TABLE sentiment_results (
        id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        stock      TEXT      NOT NULL,
        sentiment  TEXT      NOT NULL,
        score      FLOAT8    NOT NULL,
        created_at TIMESTAMPTZ DEFAULT now()
    );
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from supabase import create_client, Client

from config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Connection (singleton-style lazy init)
# ---------------------------------------------------------------------------
_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Create (or return cached) Supabase client.

    The client is created once and reused for the lifetime of the process.

    Returns
    -------
    Client | None
        An authenticated client, or ``None`` if credentials are missing
        or the connection fails.
    """
    global _client

    # Return cached client if already initialised
    if _client is not None:
        return _client

    if not settings.has_supabase_credentials:
        logger.error(
            "SUPABASE_URL or SUPABASE_KEY is not set. "
            "Add them to your .env file."
        )
        return None

    try:
        _client = create_client(settings.supabase_url, settings.supabase_key)
        logger.info("Supabase client created successfully.")
        return _client
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to create Supabase client: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Insert
# ---------------------------------------------------------------------------


def insert_sentiment(data: Dict[str, Any]) -> bool:
    """
    Insert a single sentiment result into the ``sentiment_results`` table.

    Parameters
    ----------
    data : dict
        Must contain the keys:

        - ``stock``     (str)   – ticker symbol, e.g. ``"AAPL"``
        - ``sentiment`` (str)   – label: ``"positive"`` / ``"negative"`` / ``"neutral"``
        - ``score``     (float) – polarity score (-1.0 … +1.0)
        - ``created_at``(str, optional) – ISO-8601 timestamp; auto-set if omitted.

    Returns
    -------
    bool
        ``True`` on success, ``False`` on failure.

    Example
    -------
    >>> insert_sentiment({
    ...     "stock": "AAPL",
    ...     "sentiment": "positive",
    ...     "score": 0.35,
    ... })
    True
    """
    client = get_supabase_client()
    if client is None:
        return False

    # ── Validate required fields ──────────────────────────────────────
    required = ("stock", "sentiment", "score")
    missing = [k for k in required if k not in data]
    if missing:
        logger.error("Missing required fields for insert: %s", missing)
        return False

    # Build the row, adding a timestamp if the caller didn't provide one
    row: Dict[str, Any] = {
        "stock": str(data["stock"]).upper().strip(),
        "sentiment": str(data["sentiment"]).lower().strip(),
        "score": float(data["score"]),
        "created_at": data.get(
            "created_at", datetime.now(timezone.utc).isoformat()
        ),
    }

    try:
        client.table(settings.db_table_name).insert(row).execute()
        logger.info(
            "Inserted sentiment row: %s → %s (%.4f)",
            row["stock"], row["sentiment"], row["score"],
        )
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Insert failed: %s", exc)
        return False


def insert_sentiment_batch(items: List[Dict[str, Any]]) -> int:
    """
    Insert multiple sentiment rows in a single round-trip.

    Parameters
    ----------
    items : list[dict]
        Each dict follows the same schema as :func:`insert_sentiment`.

    Returns
    -------
    int
        Number of rows successfully inserted (0 on total failure).
    """
    client = get_supabase_client()
    if client is None:
        return 0

    now = datetime.now(timezone.utc).isoformat()

    rows: List[Dict[str, Any]] = []
    for item in items:
        required = ("stock", "sentiment", "score")
        if not all(k in item for k in required):
            logger.warning("Skipping row with missing fields: %s", item)
            continue

        rows.append({
            "stock": str(item["stock"]).upper().strip(),
            "sentiment": str(item["sentiment"]).lower().strip(),
            "score": float(item["score"]),
            "created_at": item.get("created_at", now),
        })

    if not rows:
        logger.warning("No valid rows to insert.")
        return 0

    try:
        client.table(settings.db_table_name).insert(rows).execute()
        logger.info("Batch-inserted %d sentiment rows.", len(rows))
        return len(rows)
    except Exception as exc:  # noqa: BLE001
        logger.error("Batch insert failed: %s", exc)
        return 0


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------


def fetch_sentiments(
    stock: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Retrieve sentiment results from the database.

    Parameters
    ----------
    stock : str, optional
        If provided, filter results to this ticker symbol.
    limit : int, optional
        Maximum number of rows to return (default 50).

    Returns
    -------
    list[dict]
        Each dict contains ``id``, ``stock``, ``sentiment``, ``score``,
        and ``created_at``.  Returns an empty list on error.

    Example
    -------
    >>> rows = fetch_sentiments(stock="AAPL", limit=10)
    >>> for r in rows:
    ...     print(r["stock"], r["sentiment"], r["score"])
    AAPL positive 0.35
    """
    client = get_supabase_client()
    if client is None:
        return []

    try:
        query = (
            client
            .table(settings.db_table_name)
            .select("id, stock, sentiment, score, created_at")
            .order("created_at", desc=True)
            .limit(limit)
        )

        # Optional ticker filter
        if stock:
            query = query.eq("stock", stock.upper().strip())

        response = query.execute()
        rows: List[Dict[str, Any]] = response.data or []

        logger.info(
            "Fetched %d sentiment rows%s.",
            len(rows),
            f" for '{stock.upper()}'" if stock else "",
        )
        return rows

    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch sentiments: %s", exc)
        return []
