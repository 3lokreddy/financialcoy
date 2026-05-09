"""Expense and budget analysis from transaction CSVs."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


TRANSACTION_COLUMNS = ["date", "description", "amount", "category"]


def load_transactions(path: str | Path) -> pd.DataFrame:
    """CSV columns: date, description, amount, category.

    Negative amounts = expenses, positive = income (consistent with most bank exports).
    """
    df = pd.read_csv(path, parse_dates=["date"])
    missing = [c for c in TRANSACTION_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"transactions CSV missing columns: {missing}")
    df["amount"] = df["amount"].astype(float)
    df["category"] = df["category"].fillna("uncategorized").str.lower().str.strip()
    return df[TRANSACTION_COLUMNS].copy()


def summarize_by_category(df: pd.DataFrame, expenses_only: bool = True) -> pd.DataFrame:
    data = df[df["amount"] < 0] if expenses_only else df
    grouped = (
        data.assign(spend=lambda x: -x["amount"] if expenses_only else x["amount"])
        .groupby("category", as_index=False)["spend"]
        .sum()
        .sort_values("spend", ascending=False)
        .reset_index(drop=True)
    )
    return grouped


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    monthly = df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
    income = (
        monthly[monthly["amount"] > 0].groupby("month")["amount"].sum().rename("income")
    )
    expense = (
        monthly[monthly["amount"] < 0].groupby("month")["amount"].sum().abs().rename("expense")
    )
    out = pd.concat([income, expense], axis=1).fillna(0.0)
    out["net"] = out["income"] - out["expense"]
    return out.reset_index()


def budget_report(df: pd.DataFrame, budgets: dict[str, float]) -> pd.DataFrame:
    """Compare actual spend per category against a budget dict {category: monthly_budget}."""
    spent = summarize_by_category(df, expenses_only=True).set_index("category")["spend"]
    rows = []
    for cat, limit in budgets.items():
        cat_l = cat.lower().strip()
        actual = float(spent.get(cat_l, 0.0))
        rows.append(
            {
                "category": cat_l,
                "budget": float(limit),
                "actual": actual,
                "remaining": float(limit) - actual,
                "over": actual > float(limit),
            }
        )
    return pd.DataFrame(rows)
