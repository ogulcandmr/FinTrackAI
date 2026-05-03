# FinTrackAI - Portfolio live data and P&L engine
# All prices are USD; TRY figures use 1 USD = 44 TRY.

from typing import List, Dict, Any, Optional
from utils.market_data_utils import get_prices_batch, get_daily_change, get_last_price_warning, clear_price_cache

# TRY conversion: 1 USD = 44 TRY
USD_TO_TRY = 44.0


def compute_portfolio_pnl(rows: List[Dict[str, Any]]) -> tuple:
    """
    Fetches spot USD prices for portfolio rows; computes P&L in both USD and TRY (1 USD = 44 TRY).

    rows: portfolio records (asset_id, price=USD, quantity)

    Returns:
        enriched_rows: current_price (USD), cost_basis, current_value, pnl (USD), pnl_pct, pnl_tl, current_value_tl, cost_basis_tl
        summary: total_cost_usd/tl, total_value_usd/tl, total_pnl_usd/tl, total_pnl_pct, daily_change_usd/tl, daily_change_pct
    """
    if not rows:
        return [], {
            "total_cost_usd": 0.0,
            "total_value_usd": 0.0,
            "total_pnl_usd": 0.0,
            "total_pnl_tl": 0.0,
            "total_pnl_pct": 0.0,
            "total_cost_tl": 0.0,
            "total_value_tl": 0.0,
            "daily_change_usd": 0.0,
            "daily_change_tl": 0.0,
            "daily_change_pct": 0.0,
        }

    clear_price_cache()
    symbols = list({str(r.get("asset_id", "")).strip().upper() for r in rows if r.get("asset_id")})
    prices = get_prices_batch(symbols)
    warnings = {s: get_last_price_warning(s) for s in symbols}

    enriched = []
    total_cost_usd = 0.0
    total_value_usd = 0.0
    symbol_values_usd: Dict[str, float] = {}

    for r in rows:
        asset_id = str(r.get("asset_id", "")).strip().upper()
        purchase_price_usd = float(r.get("price") or 0)
        qty = float(r.get("quantity") or 0)
        cost_basis_usd = purchase_price_usd * qty
        current_price_usd = prices.get(asset_id)
        if current_price_usd is None:
            current_price_usd = purchase_price_usd
        current_value_usd = current_price_usd * qty
        pnl_usd = current_value_usd - cost_basis_usd
        pnl_pct = (pnl_usd / cost_basis_usd * 100.0) if cost_basis_usd else 0.0
        pnl_tl = pnl_usd * USD_TO_TRY
        cost_basis_tl = cost_basis_usd * USD_TO_TRY
        current_value_tl = current_value_usd * USD_TO_TRY

        total_cost_usd += cost_basis_usd
        total_value_usd += current_value_usd
        symbol_values_usd[asset_id] = symbol_values_usd.get(asset_id, 0.0) + current_value_usd

        enriched.append({
            **r,
            "current_price": current_price_usd,
            "price_warning": warnings.get(asset_id),
            "cost_basis": cost_basis_usd,
            "current_value": current_value_usd,
            "pnl": pnl_usd,
            "pnl_pct": pnl_pct,
            "pnl_tl": pnl_tl,
            "cost_basis_tl": cost_basis_tl,
            "current_value_tl": current_value_tl,
        })

    total_pnl_usd = total_value_usd - total_cost_usd
    total_pnl_tl = total_pnl_usd * USD_TO_TRY
    total_pnl_pct = (total_pnl_usd / total_cost_usd * 100.0) if total_cost_usd else 0.0
    total_cost_tl = total_cost_usd * USD_TO_TRY
    total_value_tl = total_value_usd * USD_TO_TRY

    daily_change_usd = 0.0
    for sym, val_usd in symbol_values_usd.items():
        pct, _ = get_daily_change(sym)
        if pct is not None:
            daily_change_usd += val_usd * (pct / 100.0)
    daily_change_tl = daily_change_usd * USD_TO_TRY
    daily_change_pct = (daily_change_usd / total_value_usd * 100.0) if total_value_usd else 0.0

    summary = {
        "total_cost_usd": total_cost_usd,
        "total_value_usd": total_value_usd,
        "total_pnl_usd": total_pnl_usd,
        "total_pnl_tl": total_pnl_tl,
        "total_pnl_pct": total_pnl_pct,
        "total_cost_tl": total_cost_tl,
        "total_value_tl": total_value_tl,
        "daily_change_usd": daily_change_usd,
        "daily_change_tl": daily_change_tl,
        "daily_change_pct": daily_change_pct,
    }
    return enriched, summary
