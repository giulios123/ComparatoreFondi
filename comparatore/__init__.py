"""Comparatore Fondi - backtester per fondi ed ETF su dati Yahoo Finance."""

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

__all__ = [
    "BacktestResult",
    "FeeMode",
    "Holding",
    "Instrument",
    "Rebalance",
    "apply_annual_fee",
    "convert_currency",
    "coverage_warnings",
    "get_metadata",
    "get_prices",
    "run_backtest",
    "search",
]
