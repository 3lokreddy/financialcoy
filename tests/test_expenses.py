from pathlib import Path

import pytest

from financialcoy import expenses


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "transactions.csv"


def test_load_transactions_columns():
    df = expenses.load_transactions(EXAMPLE)
    assert list(df.columns) == ["date", "description", "amount", "category"]
    assert len(df) > 0


def test_summarize_by_category_only_expenses():
    df = expenses.load_transactions(EXAMPLE)
    summary = expenses.summarize_by_category(df)
    assert "income" not in set(summary["category"])
    assert (summary["spend"] >= 0).all()


def test_monthly_summary_has_net():
    df = expenses.load_transactions(EXAMPLE)
    monthly = expenses.monthly_summary(df)
    assert {"month", "income", "expense", "net"}.issubset(monthly.columns)
    for _, row in monthly.iterrows():
        assert row["net"] == pytest.approx(row["income"] - row["expense"])


def test_budget_report_flags_overspend():
    df = expenses.load_transactions(EXAMPLE)
    report = expenses.budget_report(df, {"groceries": 50})
    row = report.iloc[0]
    assert row["category"] == "groceries"
    assert row["over"]
