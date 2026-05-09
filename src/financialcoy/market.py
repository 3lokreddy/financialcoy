"""Market data fetching via yfinance."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Quote:
    symbol: str
    price: float
    currency: str | None = None


def _yf():
    import yfinance as yf
    return yf


def get_quote(symbol: str) -> Quote:
    yf = _yf()
    ticker = yf.Ticker(symbol)
    fast = getattr(ticker, "fast_info", None) or {}
    price = fast.get("last_price") if isinstance(fast, dict) else getattr(fast, "last_price", None)
    currency = fast.get("currency") if isinstance(fast, dict) else getattr(fast, "currency", None)

    if price is None:
        hist = ticker.history(period="1d")
        if hist.empty:
            raise LookupError(f"no price data for {symbol!r}")
        price = float(hist["Close"].iloc[-1])

    return Quote(symbol=symbol.upper(), price=float(price), currency=currency)


def get_quotes(symbols: list[str]) -> list[Quote]:
    return [get_quote(s) for s in symbols]


def get_history(symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """Return OHLCV history for one symbol. period: 1d, 5d, 1mo, 3mo, 1y, 5y, max."""
    yf = _yf()
    df = yf.Ticker(symbol).history(period=period, interval=interval)
    if df.empty:
        raise LookupError(f"no history for {symbol!r}")
    df = df.rename(columns=str.lower)
    df.index.name = "date"
    return df
