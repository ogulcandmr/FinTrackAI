# FinTrackAI - Local portfolio store (SQLite)
# Runs without a Supabase schema; for asset/stock records and live status tracking.

import os
import sqlite3
import uuid
from typing import List, Dict, Any, Optional, Tuple


def _db_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "portfolio.db")


def _get_conn():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_conn()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                asset_id TEXT NOT NULL,
                purchase_date TEXT NOT NULL,
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON portfolio(user_id)")
        conn.commit()
    finally:
        conn.close()


def insert(user_id: str, asset_id: str, purchase_date: str, price: float, quantity: float) -> Tuple[Optional[Dict], Optional[str]]:
    """Adds a position to the portfolio. purchase_date: 'YYYY-MM-DD' or date as string."""
    _init_db()
    try:
        conn = _get_conn()
        rid = str(uuid.uuid4())
        date_str = str(purchase_date)[:10] if purchase_date else ""
        conn.execute(
            "INSERT INTO portfolio (id, user_id, asset_id, purchase_date, price, quantity) VALUES (?, ?, ?, ?, ?, ?)",
            (rid, user_id, asset_id.strip().upper(), date_str, float(price), float(quantity)),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM portfolio WHERE id = ?", (rid,)).fetchone()
        conn.close()
        if row:
            return dict(row), None
        return {"id": rid, "user_id": user_id, "asset_id": asset_id, "purchase_date": date_str, "price": price, "quantity": quantity}, None
    except Exception as e:
        return None, str(e)


def select_by_user(user_id: str) -> List[Dict[str, Any]]:
    """Returns all portfolio records for the user."""
    _init_db()
    try:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT * FROM portfolio WHERE user_id = ? ORDER BY purchase_date DESC, created_at DESC",
            (user_id,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Portfolio list error (local): {e}")
        return []


def delete(record_id: str, user_id: str) -> Tuple[bool, Optional[str]]:
    """Deletes the given record (only for the matching user)."""
    _init_db()
    try:
        conn = _get_conn()
        cur = conn.execute("DELETE FROM portfolio WHERE id = ? AND user_id = ?", (record_id, user_id))
        conn.commit()
        conn.close()
        return cur.rowcount > 0, None
    except Exception as e:
        return False, str(e)
