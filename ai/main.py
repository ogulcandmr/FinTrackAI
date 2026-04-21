"""
main.py – Orchestrator for the FinTrack AI analysis pipeline.

Usage
-----
    python main.py              # analyse AAPL (default)
    python main.py MSFT         # analyse any ticker

Pipeline
--------
1. Get stock symbol
2. Fetch financial news headlines
3. Analyse headline sentiment (TextBlob)
4. Run 15-day price forecast (Prophet + yfinance)
5. Save sentiment results to Supabase
6. Print a consolidated summary
"""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Ensure UTF-8 output (Windows consoles may default to a local codepage)
# ---------------------------------------------------------------------------
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from ai.config import settings
from ai.news import fetch_news
from ai.sentiment import analyze_sentiment
from ai.forecast import run_forecast
from ai.db import insert_sentiment_batch, fetch_sentiments

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants (display only — no secrets, no config)
# ---------------------------------------------------------------------------
SEPARATOR = "=" * 60

LABEL_EMOJI = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}


# ---------------------------------------------------------------------------
# Pipeline result container
# ---------------------------------------------------------------------------
@dataclass
class PipelineResult:
    """Holds the output of a full pipeline run."""

    ticker: str
    headlines: List[str] = field(default_factory=list)
    sentiment_report: Dict[str, Any] = field(default_factory=dict)
    forecast_result: Optional[Dict[str, Any]] = None
    rows_saved: int = 0
    elapsed_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _header(icon: str, title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{SEPARATOR}")
    print(f"  {icon}  {title}")
    print(SEPARATOR)


def _timed(label: str):
    """Context-manager that prints elapsed time for a block."""
    class _Timer:
        def __enter__(self):
            self.t0 = time.perf_counter()
            return self
        def __exit__(self, *_):
            elapsed = time.perf_counter() - self.t0
            print(f"  ⏱  {label} completed in {elapsed:.2f}s")
    return _Timer()


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------

def step_fetch_news(ticker: str) -> List[str]:
    """
    Step 1 — Fetch latest financial news headlines for *ticker*.

    Uses the NewsAPI integration in ``news.py``.
    Returns a list of headline strings (may be empty).
    """
    _header("📰", f"Step 1 · Fetching news for {ticker}")

    with _timed("News fetch"):
        headlines = fetch_news(ticker)

    if not headlines:
        print("  ⚠️  No headlines found. Pipeline continues with empty list.")
        return []

    for i, title in enumerate(headlines, 1):
        print(f"  {i:>2}. {title}")

    print(f"\n  → {len(headlines)} headline(s) fetched.")
    return headlines


def step_analyze_sentiment(headlines: List[str]) -> Dict[str, Any]:
    """
    Step 2 — Score each headline with TextBlob sentiment analysis.

    Returns the full sentiment report dictionary including per-item
    scores and aggregate statistics.
    """
    _header("🧠", f"Step 2 · Analysing sentiment ({len(headlines)} headlines)")

    with _timed("Sentiment analysis"):
        report = analyze_sentiment(headlines)

    # Per-item breakdown
    for item in report["items"]:
        emoji = LABEL_EMOJI.get(item["label"], "⚪")
        print(f"  {emoji} [{item['polarity']:+.4f}]  {item['text'][:75]}")

    # Aggregate
    print(f"\n  → Average polarity  : {report['average_polarity']:+.4f}")
    print(f"  → Overall label     : {report['overall_label']}")
    print(f"  → Analysed / Skipped: {report['total_analyzed']} / {report['total_skipped']}")

    return report


def step_forecast(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Step 3 — Predict the next N days of closing prices.

    Uses Prophet trained on historical yfinance data.
    Returns the forecast result dict, or ``None`` on failure.
    """
    days = settings.forecast_days
    _header("📈", f"Step 3 · Forecasting {ticker} (next {days} days)")

    with _timed("Forecast"):
        result = run_forecast(ticker)

    if result is None:
        print("  ⚠️  Forecast could not be generated.")
        return None

    print(f"  Trained on {result['history_rows']} rows of historical data.\n")
    print(result["predictions"].to_string(index=False))

    return result


def step_save_to_supabase(ticker: str, report: Dict[str, Any]) -> int:
    """
    Step 4 — Persist sentiment results to Supabase.

    Transforms the sentiment items into ``(stock, sentiment, score)``
    rows and batch-inserts them into the ``sentiment_results`` table.
    Returns the number of rows inserted.
    """
    _header("💾", "Step 4 · Saving results to Supabase")

    items = report.get("items", [])
    if not items:
        print("  ⚠️  No sentiment data to store. Skipping.")
        return 0

    rows = [
        {
            "stock": ticker,
            "sentiment": item["label"],
            "score": item["polarity"],
        }
        for item in items
    ]

    with _timed("Database insert"):
        inserted = insert_sentiment_batch(rows)

    if inserted:
        print(f"  ✅ {inserted} row(s) saved successfully.")
    else:
        print("  ❌ Insert failed – check logs for details.")

    return inserted


def step_print_summary(result: PipelineResult) -> None:
    """
    Step 5 — Print a consolidated summary of the entire pipeline run.
    """
    _header("📊", f"Summary for {result.ticker}")

    report = result.sentiment_report

    # ── News ──────────────────────────────────────────────────────────
    print(f"  Headlines fetched    : {len(result.headlines)}")

    # ── Sentiment ─────────────────────────────────────────────────────
    overall = report.get("overall_label", "n/a")
    avg_pol = report.get("average_polarity", 0.0)
    emoji = LABEL_EMOJI.get(overall, "⚪")
    print(f"  Sentiment            : {emoji} {overall} (avg {avg_pol:+.4f})")
    print(f"  Analysed / Skipped   : {report.get('total_analyzed', 0)}"
          f" / {report.get('total_skipped', 0)}")

    # ── Forecast ──────────────────────────────────────────────────────
    if result.forecast_result:
        preds = result.forecast_result["predictions"]
        first, last = preds.iloc[0], preds.iloc[-1]
        print(f"  Forecast range       : {first['ds'].date()} → {last['ds'].date()}")
        print(f"  Last predicted close : ${last['yhat']:.2f}  "
              f"(${last['yhat_lower']:.2f} – ${last['yhat_upper']:.2f})")
    else:
        print("  Forecast             : unavailable")

    # ── Database ──────────────────────────────────────────────────────
    print(f"  Rows saved to DB     : {result.rows_saved}")

    # ── Recent stored records ─────────────────────────────────────────
    stored = fetch_sentiments(stock=result.ticker, limit=5)
    if stored:
        print(f"\n  🔍 Last {len(stored)} stored record(s):")
        for row in stored:
            ts = row["created_at"][:19]
            print(f"     [{ts}] {row['stock']} → {row['sentiment']}"
                  f" ({row['score']:+.4f})")

    # ── Timing ────────────────────────────────────────────────────────
    print(f"\n  ⏱  Total elapsed     : {result.elapsed_seconds:.2f}s")


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------

def run_pipeline(ticker: str | None = None) -> PipelineResult:
    """
    Execute the full FinTrack analysis pipeline.

    Parameters
    ----------
    ticker : str, optional
        Stock ticker symbol (e.g. ``"AAPL"``, ``"MSFT"``, ``"GOOGL"``).
        Falls back to ``settings.default_ticker``.

    Returns
    -------
    PipelineResult
        A dataclass containing every artefact produced by the pipeline.
    """
    if ticker is None:
        ticker = settings.default_ticker
    ticker = ticker.upper().strip()

    # Validate config at startup
    settings.validate()

    t0 = time.perf_counter()

    print(f"\n{'*' * 60}")
    print(f"  🚀  FinTrack AI Pipeline — {ticker}")
    print(f"{'*' * 60}")

    # Step 1 – Fetch news
    headlines = step_fetch_news(ticker)

    # Step 2 – Analyse sentiment
    report = step_analyze_sentiment(headlines)

    # Step 3 – Run forecast
    forecast_result = step_forecast(ticker)

    # Step 4 – Save to Supabase
    rows_saved = step_save_to_supabase(ticker, report)

    # Collect results
    elapsed = time.perf_counter() - t0
    result = PipelineResult(
        ticker=ticker,
        headlines=headlines,
        sentiment_report=report,
        forecast_result=forecast_result,
        rows_saved=rows_saved,
        elapsed_seconds=round(elapsed, 2),
    )

    # Step 5 – Print summary
    step_print_summary(result)

    # Done
    print(f"\n{SEPARATOR}")
    print(f"  🏁  Pipeline complete for {ticker}.")
    print(f"{SEPARATOR}\n")

    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else None
    run_pipeline(symbol)
