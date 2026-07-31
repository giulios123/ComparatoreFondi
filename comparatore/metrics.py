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


def xirr(
    cashflows: list[tuple[pd.Timestamp, float]],
    final_value: float,
    final_date: pd.Timestamp,
) -> float:
    """Money-weighted annual return of a stream of contributions.

    `cashflows` are negative (money paid in) at their respective dates;
    `final_value` is what the investor holds on `final_date`, treated as one
    positive cashflow. This is the number a PAC needs and `cagr` cannot give:
    `cagr` assumes one pot of money planted on day one, which is false the
    moment there is more than one contribution.

    Solved by bisection on the discount rate, not Newton's method: Newton can
    diverge on a cashflow list with very uneven spacing (typical of a PAC with
    a long history), while bisection on a bounded rate range always finds the
    root whenever one exists in that range.
    """
    if not cashflows or final_value <= 0:
        return float("nan")
    dates = [d for d, _ in cashflows] + [pd.Timestamp(final_date)]
    amounts = [a for _, a in cashflows] + [final_value]
    t0 = dates[0]
    years = [(d - t0).days / 365.25 for d in dates]

    def npv(rate: float) -> float:
        return sum(a / (1.0 + rate) ** y for a, y in zip(amounts, years))

    lo, hi = -0.9999, 10.0
    npv_lo, npv_hi = npv(lo), npv(hi)
    if npv_lo == 0:
        return lo
    if npv_hi == 0:
        return hi
    if (npv_lo > 0) == (npv_hi > 0):
        return float("nan")

    for _ in range(100):
        mid = (lo + hi) / 2
        npv_mid = npv(mid)
        if abs(npv_mid) < 1e-9:
            return mid
        if (npv_mid > 0) == (npv_lo > 0):
            lo, npv_lo = mid, npv_mid
        else:
            hi = mid
    return (lo + hi) / 2


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
