"""Portfolio tracking: load holdings from CSV, value them with live quotes."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from financialcoy.market import get_quote


HOLDINGS_COLUMNS = ["symbol", "shares", "cost_basis"]


def load_holdings(path: str | Path) -> pd.DataFrame:
    """CSV columns: symbol, shares, cost_basis (price paid per share)."""
    df = pd.read_csv(path)
    missing = [c for c in HOLDINGS_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"holdings CSV missing columns: {missing}")
    df["symbol"] = df["symbol"].str.upper().str.strip()
    df["shares"] = df["shares"].astype(float)
    df["cost_basis"] = df["cost_basis"].astype(float)
    return df[HOLDINGS_COLUMNS].copy()


def value_holdings(holdings: pd.DataFrame) -> pd.DataFrame:
    """Add price, market_value, cost, gain, return_pct columns."""
    rows = []
    for _, h in holdings.iterrows():
        quote = get_quote(h["symbol"])
        rows.append(quote.price)
    out = holdings.copy()
    out["price"] = rows
    out["market_value"] = out["shares"] * out["price"]
    out["cost"] = out["shares"] * out["cost_basis"]
    out["gain"] = out["market_value"] - out["cost"]
    out["return_pct"] = (out["gain"] / out["cost"]).where(out["cost"] != 0, 0.0) * 100
    return out


def summarize(valued: pd.DataFrame) -> dict[str, float]:
    total_value = float(valued["market_value"].sum())
    total_cost = float(valued["cost"].sum())
    total_gain = total_value - total_cost
    return {
        "market_value": total_value,
        "cost": total_cost,
        "gain": total_gain,
        "return_pct": (total_gain / total_cost * 100) if total_cost else 0.0,
    }
