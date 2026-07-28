"""Yahoo Finance access: instrument search, metadata (currency / TER) and prices.

All functions here are pure and free of Streamlit imports so they can be used
from scripts and tests; the app layer wraps them in its own cache.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import pandas as pd
import yfinance as yf

# Yahoo quote types that make sense in a fund backtester.
FUND_TYPES = ("ETF", "MUTUALFUND")


@dataclass
class Instrument:
    symbol: str
    name: str
    quote_type: str
    exchange: str = ""
    currency: str = ""
    ter: float | None = None  # annual fraction, e.g. 0.0022 == 0.22%
    ter_source: str = ""

    @property
    def label(self) -> str:
        return f"{self.name} ({self.symbol})" if self.name else self.symbol


# --------------------------------------------------------------------------
# Search
# --------------------------------------------------------------------------


def search(query: str, limit: int = 12, funds_only: bool = True) -> list[Instrument]:
    """Search Yahoo Finance by name, ticker or ISIN.

    ISIN lookups work directly (e.g. IE00B3XXRP09 -> VUSA.L), which is the
    usual way European funds are identified.
    """
    query = (query or "").strip()
    if not query:
        return []

    res = yf.Search(
        query,
        max_results=max(limit, 10),
        news_count=0,
        lists_count=0,
        enable_fuzzy_query=True,
        raise_errors=False,
    )
    out: list[Instrument] = []
    for row in res.quotes or []:
        qtype = (row.get("quoteType") or "").upper()
        if funds_only and qtype not in FUND_TYPES:
            continue
        symbol = row.get("symbol")
        if not symbol:
            continue
        name = row.get("longname") or row.get("shortname") or symbol
        out.append(
            Instrument(
                symbol=symbol,
                name=name,
                quote_type=qtype,
                exchange=row.get("exchDisp") or row.get("exchange") or "",
            )
        )
        if len(out) >= limit:
            break
    return out


# --------------------------------------------------------------------------
# Metadata: currency and expense ratio
# --------------------------------------------------------------------------


def _extract_ter(info: dict) -> tuple[float | None, str]:
    """Pull an expense ratio out of a Yahoo `info` dict.

    Yahoo exposes it inconsistently: `annualReportExpenseRatio` is a decimal
    fraction (0.0074), `netExpenseRatio` is a percentage (0.74). Coverage for
    European funds is poor, so the value is only ever a suggestion.
    """
    val = info.get("annualReportExpenseRatio")
    if isinstance(val, (int, float)) and val > 0:
        return float(val), "annualReportExpenseRatio"

    val = info.get("netExpenseRatio")
    if isinstance(val, (int, float)) and val > 0:
        return float(val) / 100.0, "netExpenseRatio"

    return None, ""


def get_metadata(symbol: str) -> Instrument:
    """Fetch name, currency and (best-effort) TER for one symbol."""
    ticker = yf.Ticker(symbol)
    try:
        info = ticker.info or {}
    except Exception:
        info = {}

    ter, source = _extract_ter(info)
    name = info.get("longName") or info.get("shortName") or symbol
    currency = (info.get("currency") or "").upper()

    if not currency:
        # `info` can come back empty for thin listings; price metadata is a
        # cheaper and more reliable fallback.
        try:
            meta = ticker.history_metadata or {}
            currency = (meta.get("currency") or "").upper()
        except Exception:
            currency = ""

    return Instrument(
        symbol=symbol,
        name=name,
        quote_type=(info.get("quoteType") or "").upper(),
        exchange=info.get("fullExchangeName") or "",
        currency=currency,
        ter=ter,
        ter_source=source,
    )


# --------------------------------------------------------------------------
# Prices
# --------------------------------------------------------------------------


def _naive_index(idx: pd.Index) -> pd.DatetimeIndex:
    idx = pd.DatetimeIndex(idx)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    return idx.normalize()


def get_prices(
    symbols: list[str], start: dt.date, end: dt.date
) -> tuple[pd.DataFrame, dict[str, str]]:
    """Download total-return price series (dividends reinvested).

    Returns the raw price frame (one column per symbol, native currency) and a
    map of symbol -> currency as reported by the price feed.
    """
    symbols = list(dict.fromkeys(symbols))
    if not symbols:
        return pd.DataFrame(), {}

    raw = yf.download(
        symbols,
        start=start,
        # yfinance treats `end` as exclusive.
        end=end + dt.timedelta(days=1),
        auto_adjust=True,  # total return: dividends reinvested
        progress=False,
        actions=False,
        group_by="column",
        threads=True,
    )
    if raw is None or raw.empty:
        return pd.DataFrame(), {}

    close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
    if not isinstance(raw.columns, pd.MultiIndex):
        close.columns = symbols[:1]

    close = close.reindex(columns=[s for s in symbols if s in close.columns])
    close.index = _naive_index(close.index)
    close = close.dropna(how="all").sort_index()

    # Casing matters here: Yahoo reports London listings as "GBp" (pence).
    currencies: dict[str, str] = {}
    for sym in close.columns:
        try:
            meta = yf.Ticker(sym).history_metadata or {}
            currencies[sym] = meta.get("currency") or ""
        except Exception:
            currencies[sym] = ""

    return close, currencies


# --------------------------------------------------------------------------
# FX conversion
# --------------------------------------------------------------------------


@dataclass
class FxResult:
    prices: pd.DataFrame
    converted: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)


def _fx_series(src: str, dst: str, start: dt.date, end: dt.date) -> pd.Series | None:
    """Daily rate to multiply a `src` amount by to obtain `dst`."""
    for symbol, invert in ((f"{src}{dst}=X", False), (f"{dst}{src}=X", True)):
        try:
            hist = yf.Ticker(symbol).history(
                start=start, end=end + dt.timedelta(days=1), auto_adjust=False
            )
        except Exception:
            continue
        if hist is None or hist.empty or "Close" not in hist:
            continue
        rate = hist["Close"].dropna()
        if rate.empty:
            continue
        rate.index = _naive_index(rate.index)
        return (1.0 / rate) if invert else rate
    return None


def convert_currency(
    prices: pd.DataFrame,
    currencies: dict[str, str],
    base: str,
    start: dt.date,
    end: dt.date,
) -> FxResult:
    """Convert every column to `base` using daily Yahoo FX rates.

    Columns whose currency cannot be resolved are dropped: silently mixing
    currencies would produce a portfolio curve that is simply wrong.
    """
    base = base.upper()
    out = prices.copy()
    converted: list[str] = []
    failed: list[str] = []

    for sym in list(out.columns):
        ccy = (currencies.get(sym) or "").strip()

        # Yahoo quotes London listings in pence; normalise to pounds first.
        if ccy == "GBp":
            out[sym] = out[sym] / 100.0
            ccy = "GBP"
        ccy = ccy.upper()

        if not ccy:
            failed.append(sym)
            out = out.drop(columns=[sym])
            continue
        if ccy == base:
            continue

        rate = _fx_series(ccy, base, start, end)
        if rate is None:
            failed.append(sym)
            out = out.drop(columns=[sym])
            continue

        aligned = rate.reindex(out.index).ffill().bfill()
        out[sym] = out[sym] * aligned
        converted.append(sym)

    return FxResult(prices=out, converted=converted, failed=failed)
