from pathlib import Path

import pandas as pd
import pytest

from financialcoy import portfolio


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "holdings.csv"


def test_load_holdings_normalizes_symbols():
    df = portfolio.load_holdings(EXAMPLE)
    assert list(df.columns) == ["symbol", "shares", "cost_basis"]
    assert df["symbol"].str.isupper().all()


def test_load_holdings_rejects_missing_columns(tmp_path: Path):
    bad = tmp_path / "bad.csv"
    bad.write_text("symbol,shares\nAAPL,1\n")
    with pytest.raises(ValueError):
        portfolio.load_holdings(bad)


def test_summarize_totals():
    valued = pd.DataFrame(
        {
            "symbol": ["A", "B"],
            "shares": [10, 5],
            "cost_basis": [10.0, 20.0],
            "price": [12.0, 25.0],
            "market_value": [120.0, 125.0],
            "cost": [100.0, 100.0],
            "gain": [20.0, 25.0],
            "return_pct": [20.0, 25.0],
        }
    )
    summary = portfolio.summarize(valued)
    assert summary["market_value"] == pytest.approx(245.0)
    assert summary["cost"] == pytest.approx(200.0)
    assert summary["gain"] == pytest.approx(45.0)
    assert summary["return_pct"] == pytest.approx(22.5)
