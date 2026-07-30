"""Performance metrics for equity curves."""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def _years(index: pd.DatetimeIndex) -> float:
    if len(index) < 2:
        return 0.0
    return (index[-1] - index[0]).days / 365.25


def total_return(curve: pd.Series) -> float:
    if len(curve) < 2 or curve.iloc[0] == 0:
        return float("nan")
    return curve.iloc[-1] / curve.iloc[0] - 1.0


def cagr(curve: pd.Series) -> float:
    yrs = _years(curve.index)
    if yrs <= 0 or curve.iloc[0] <= 0 or curve.iloc[-1] <= 0:
        return float("nan")
    return (curve.iloc[-1] / curve.iloc[0]) ** (1 / yrs) - 1.0


def volatility(curve: pd.Series) -> float:
    """Annualised standard deviation of daily returns."""
    rets = curve.pct_change().dropna()
    if len(rets) < 2:
        return float("nan")
    return rets.std(ddof=1) * np.sqrt(TRADING_DAYS)


def drawdown_series(curve: pd.Series) -> pd.Series:
    peak = curve.cummax()
    return curve / peak - 1.0


def max_drawdown(curve: pd.Series) -> float:
    if len(curve) < 2:
        return float("nan")
    return drawdown_series(curve).min()


def sharpe(curve: pd.Series, risk_free: float = 0.0) -> float:
    """Sharpe ratio using a constant annual risk-free rate."""
    rets = curve.pct_change().dropna()
    if len(rets) < 2:
        return float("nan")
    daily_rf = (1 + risk_free) ** (1 / TRADING_DAYS) - 1
    excess = rets - daily_rf
    sd = excess.std(ddof=1)
    if sd == 0:
        return float("nan")
    return excess.mean() / sd * np.sqrt(TRADING_DAYS)


def sortino(curve: pd.Series, risk_free: float = 0.0) -> float:
    """Like Sharpe but penalising only downside deviation."""
    rets = curve.pct_change().dropna()
    if len(rets) < 2:
        return float("nan")
    daily_rf = (1 + risk_free) ** (1 / TRADING_DAYS) - 1
    excess = rets - daily_rf
    downside = excess[excess < 0]
    if len(downside) < 2:
        return float("nan")
    dd = downside.std(ddof=1)
    if dd == 0:
        return float("nan")
    return excess.mean() / dd * np.sqrt(TRADING_DAYS)


def calmar(curve: pd.Series) -> float:
    mdd = max_drawdown(curve)
    if not mdd or np.isnan(mdd) or mdd == 0:
        return float("nan")
    return cagr(curve) / abs(mdd)


def best_worst_year(curve: pd.Series) -> tuple[float, float]:
    yearly = curve.resample("YE").last().pct_change().dropna()
    if yearly.empty:
        return float("nan"), float("nan")
    return yearly.max(), yearly.min()


def calendar_year_returns(curve: pd.Series) -> pd.Series:
    """Calendar-year returns, with the first (possibly partial) year included."""
    yearly = curve.resample("YE").last()
    first = pd.Series([curve.iloc[0]], index=[curve.index[0]])
    joined = pd.concat([first, yearly])
    out = joined.pct_change().dropna()
    out.index = out.index.year
    return out[~out.index.duplicated(keep="last")]


def summarize(curve: pd.Series, risk_free: float = 0.0) -> dict:
    """Full metric set for one equity curve.

    Keys are stable English identifiers: they become DataFrame column names
    and lookup keys into the UI's translated labels/help text, so renaming
    them would ripple into every caller and any exported file that embeds
    them (see `comparatore.portfolio_io`, which does not - these values are
    computed fresh each run, never persisted).
    """
    best, worst = best_worst_year(curve)
    return {
        "final_value": curve.iloc[-1],
        "total_return": total_return(curve),
        "cagr": cagr(curve),
        "volatility": volatility(curve),
        "sharpe": sharpe(curve, risk_free),
        "sortino": sortino(curve, risk_free),
        "max_drawdown": max_drawdown(curve),
        "calmar": calmar(curve),
        "best_year": best,
        "worst_year": worst,
    }
