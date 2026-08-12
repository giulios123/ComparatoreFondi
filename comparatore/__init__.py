"""Comparatore Fondi - backtester per fondi ed ETF su piu' fonti dati."""

# Fonte unica della versione: il progetto non ha un [build-system] e non viene
# mai installato come distribuzione, quindi `importlib.metadata.version()` non
# la troverebbe ne' da sorgente ne' nel bundle. `app.py` la importa da qui, e
# `desktop/comparatore.spec` la estrae con `ast` (senza importare il pacchetto,
# che tirerebbe dentro pandas e streamlit in fase di build). Va tenuta
# allineata a `version` in pyproject.toml - lo verifica tests/test_versione.py.
__version__ = "0.2.0"

from . import allocazione, cache, comparative, covip, fx, horizons, inflation
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
    "comparative",
    "convert_currency",
    "coverage_warnings",
    "covip",
    "extend_with_proxy",
    "fx",
    "horizons",
    "inflation",
    "get_metadata",
    "get_prices",
    "is_isin",
    "parse_csv",
    "run_backtest",
    "search",
    "suggest_proxy",
]
