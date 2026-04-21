"""
sentiment.py – Sentiment analysis using TextBlob.

Receives a list of text strings (e.g. news headlines) and returns a
structured dictionary with per-item scores and an aggregate summary.

Example
-------
>>> from sentiment import analyze_sentiment
>>> result = analyze_sentiment(["Apple stock is rising", "Market crash fears"])
>>> result["average_polarity"]
0.1
>>> result["overall_label"]
'positive'
"""

import logging
from typing import Any, Dict, List, Optional

from textblob import TextBlob

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type aliases (for readability)
# ---------------------------------------------------------------------------
SentimentItemDict = Dict[str, Any]
SentimentResultDict = Dict[str, Any]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _polarity_to_label(polarity: float) -> str:
    """
    Map a polarity score to a human-readable label.

    Thresholds
    ----------
    polarity > +0.1  →  "positive"
    polarity < -0.1  →  "negative"
    otherwise        →  "neutral"
    """
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    return "neutral"


def _sanitize_text(text: Any) -> Optional[str]:
    """
    Validate and clean a single text entry.

    Returns the stripped string if valid, or ``None`` for entries that
    should be skipped (empty strings, non-string types, whitespace-only).
    """
    if not isinstance(text, str):
        logger.warning("Skipping non-string entry: %r (type=%s)", text, type(text).__name__)
        return None

    cleaned = text.strip()
    if not cleaned:
        logger.warning("Skipping empty/whitespace-only string.")
        return None

    return cleaned


def _analyze_single(text: str) -> Optional[SentimentItemDict]:
    """
    Run TextBlob sentiment analysis on a single string.

    Returns a dict with ``text``, ``polarity``, ``subjectivity``,
    and ``label`` – or ``None`` if analysis fails.
    """
    try:
        blob = TextBlob(text)
        polarity: float = round(blob.sentiment.polarity, 4)
        subjectivity: float = round(blob.sentiment.subjectivity, 4)
        label: str = _polarity_to_label(polarity)

        return {
            "text": text,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "label": label,
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Sentiment analysis failed for '%.80s': %s", text, exc)
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_sentiment(texts: List[str]) -> SentimentResultDict:
    """
    Analyse the sentiment of each text in *texts*.

    Parameters
    ----------
    texts : list[str]
        List of strings to analyse (e.g. news headlines).
        Non-string entries, empty strings, and whitespace-only strings
        are silently filtered out.

    Returns
    -------
    dict
        A structured dictionary with the following keys:

        - **items** (``list[dict]``) – Per-headline results.
          Each dict contains:
            - ``text``          (str)   – Original headline.
            - ``polarity``      (float) – Score from -1.0 to +1.0.
            - ``subjectivity``  (float) – Score from  0.0 to  1.0.
            - ``label``         (str)   – "positive" | "negative" | "neutral".

        - **average_polarity** (``float``) – Mean polarity across all items.
        - **overall_label** (``str``)      – Aggregate label.
        - **total_analyzed** (``int``)     – Number of items successfully analyzed.
        - **total_skipped** (``int``)      – Number of inputs that were invalid or failed.

    Example
    -------
    >>> analyze_sentiment(["Apple stock is rising", "Market crash fears"])
    {
        "items": [
            {"text": "Apple stock is rising",  "polarity": 0.2, "subjectivity": 0.4, "label": "positive"},
            {"text": "Market crash fears",     "polarity": -0.1, "subjectivity": 0.8, "label": "neutral"},
        ],
        "average_polarity": 0.05,
        "overall_label": "neutral",
        "total_analyzed": 2,
        "total_skipped": 0,
    }
    """

    # ── Edge case: no input at all ────────────────────────────────────
    if not texts:
        logger.warning("Empty or None text list passed to analyze_sentiment.")
        return {
            "items": [],
            "average_polarity": 0.0,
            "overall_label": "neutral",
            "total_analyzed": 0,
            "total_skipped": 0,
        }

    items: List[SentimentItemDict] = []
    skipped: int = 0

    for raw in texts:
        # Validate / clean
        cleaned = _sanitize_text(raw)
        if cleaned is None:
            skipped += 1
            continue

        # Analyse
        result = _analyze_single(cleaned)
        if result is None:
            skipped += 1
            continue

        items.append(result)

    # ── Aggregate ─────────────────────────────────────────────────────
    if items:
        avg_polarity: float = round(
            sum(item["polarity"] for item in items) / len(items), 4
        )
    else:
        avg_polarity = 0.0

    overall_label: str = _polarity_to_label(avg_polarity)

    logger.info(
        "Sentiment analysis complete – %d analysed, %d skipped, "
        "avg polarity %.4f (%s).",
        len(items), skipped, avg_polarity, overall_label,
    )

    return {
        "items": items,
        "average_polarity": avg_polarity,
        "overall_label": overall_label,
        "total_analyzed": len(items),
        "total_skipped": skipped,
    }
