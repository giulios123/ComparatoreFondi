"""Comparatore Fondi - backtester per fondi ed ETF su piu' fonti dati."""

from . import allocazione, cache, covip, fx, horizons
from .covip import Comparto
from .data import Instrument, convert_currency, get_metadata, get_prices, search
from .engine import (
    BacktestResult,
    FeeMode,
    Holding,
    Rebalance,
    apply_annual_fee,
    coverage_warnings,
    run_backtest,
)
from .proxies import ProxyDef, extend_with_proxy, suggest_proxy
from .sources import CsvParseError, PriceSeries, Registry, is_isin, parse_csv

__all__ = [
    "BacktestResult",
    "Comparto",
    "CsvParseError",
    "FeeMode",
    "Holding",
    "Instrument",
    "PriceSeries",
    "ProxyDef",
    "Rebalance",
    "Registry",
    "allocazione",
    "apply_annual_fee",
    "cache",
    "convert_currency",
    "coverage_warnings",
    "covip",
    "extend_with_proxy",
    "fx",
    "horizons",
    "get_metadata",
    "get_prices",
    "is_isin",
    "parse_csv",
    "run_backtest",
    "search",
    "suggest_proxy",
]
