"""Backtest engine: fee adjustment, portfolio simulation, rebalancing.

On the treatment of the TER
---------------------------
The NAV / price series Yahoo publishes for a fund or ETF is **already net of
the TER** - the management fee is accrued daily inside the NAV. So the naive
"subtract the TER from the historical return" is double counting.

This module therefore works with three explicitly labelled series:

  net    the series as published: what an investor actually earned.
  gross  the TER added back on top, i.e. the hypothetical fee-free fund.
         The gap between gross and net *is* the cost of the TER.
  extra  an additional cost the historical NAV does not contain (custody fees,
         advisory fees, or a different share class's TER) applied as a drag.

`FeeMode` picks which one drives the backtest; the app charts them together so
the fee drag is visible.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd

DAYS_PER_YEAR = 365.25


class FeeMode(str, Enum):
    NET = "net"  # as published (TER already deducted)
    GROSS = "gross"  # TER added back: fee-free hypothetical


class Rebalance(str, Enum):
    NONE = "none"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class Frequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


# Keyed by the plain string value so both `Rebalance` and `Frequency` share it.
_FREQ = {
    "monthly": "M",
    "quarterly": "Q",
    "yearly": "Y",
}


@dataclass
class Holding:
    symbol: str
    label: str
    weight: float  # portfolio share, 0..1
    ter: float = 0.0  # annual fraction already inside the NAV
    extra_cost: float = 0.0  # annual fraction NOT in the NAV


@dataclass
class Pac:
    """A recurring contribution plan layered on top of the initial capital."""

    amount: float  # per-instalment amount, base currency
    frequency: Frequency = Frequency.MONTHLY
    step_up: float = 0.0  # annual increase applied to `amount`, e.g. 0.02 = +2%/year
    start: dt.date | None = None  # None = from the first trading day
    end: dt.date | None = None  # None = through the last trading day


@dataclass
class BacktestResult:
    portfolio: pd.Series  # portfolio value over time, base currency
    portfolio_gross: pd.Series  # same, with every TER added back
    per_fund: pd.DataFrame  # value of the full capital in each fund alone
    per_fund_gross: pd.DataFrame
    contributions: pd.DataFrame  # value of each sleeve inside the portfolio
    prices: pd.DataFrame  # fee-adjusted prices actually used
    start: pd.Timestamp
    end: pd.Timestamp
    fee_drag: float  # final gross value - final net value, base currency
    nav: pd.Series  # portfolio value with contributions stripped out (time-weighted)
    nav_gross: pd.Series  # same, fee-free
    invested: pd.Series  # cumulative capital paid in: initial value + instalments
    cashflows: list[tuple[pd.Timestamp, float]]  # for XIRR: negative = paid in


def apply_annual_fee(prices: pd.DataFrame | pd.Series, annual_rate: float):
    """Compound an annual fee into a price series.

    A positive rate is a cost (the series is pulled down); a negative rate adds
    the fee back (used to reconstruct the gross, fee-free series).
    """
    if not annual_rate:
        return prices.copy()
    elapsed = (prices.index - prices.index[0]).days.to_numpy() / DAYS_PER_YEAR
    factor = np.power(1.0 - annual_rate, elapsed)
    if isinstance(prices, pd.Series):
        return prices * factor
    return prices.mul(pd.Series(factor, index=prices.index), axis=0)


def adjust_for_fees(
    prices: pd.DataFrame, holdings: list[Holding], mode: FeeMode
) -> pd.DataFrame:
    """Build the price frame the simulation runs on, per fee mode."""
    out = prices.copy()
    for h in holdings:
        if h.symbol not in out.columns:
            continue
        rate = h.extra_cost
        if mode is FeeMode.GROSS:
            # Add the TER back, then still charge any extra cost.
            rate = rate - h.ter
        out[h.symbol] = apply_annual_fee(out[h.symbol], rate)
    return out


def _period_start_dates(index: pd.DatetimeIndex, freq: str) -> pd.DatetimeIndex:
    """First trading day of each calendar period, at a pandas frequency code."""
    periods = index.to_period(freq)
    is_first = pd.Series(periods, index=index).ne(pd.Series(periods, index=index).shift())
    return index[is_first.to_numpy()]


def rebalance_dates(index: pd.DatetimeIndex, mode: Rebalance) -> set[pd.Timestamp]:
    """First trading day of each period."""
    if mode is Rebalance.NONE:
        return set()
    dates = set(_period_start_dates(index, _FREQ[mode.value]))
    dates.discard(index[0])  # the initial purchase is not a rebalance
    return dates


def contribution_schedule(index: pd.DatetimeIndex, pac: Pac | None) -> np.ndarray:
    """Instalment amount due on each trading day, zero where nothing is paid.

    Instalments land on the first trading day of each period - the same
    calendar `rebalance_dates` uses - excluding the very first day of the
    backtest, which is the initial capital rather than a contribution.
    `step_up` compounds once per full year elapsed since the first instalment
    actually paid (which may be later than the backtest start if `pac.start`
    delays it).
    """
    contrib = np.zeros(len(index))
    if pac is None or not pac.amount:
        return contrib

    dates = list(_period_start_dates(index, _FREQ[pac.frequency.value]))
    if dates and dates[0] == index[0]:
        dates = dates[1:]
    if pac.start is not None:
        start = pd.Timestamp(pac.start)
        dates = [d for d in dates if d >= start]
    if pac.end is not None:
        end = pd.Timestamp(pac.end)
        dates = [d for d in dates if d <= end]
    if not dates:
        return contrib

    position = {date: i for i, date in enumerate(index)}
    first = dates[0]
    for date in dates:
        years = ((date.year - first.year) * 12 + (date.month - first.month)) // 12
        contrib[position[date]] = pac.amount * (1.0 + pac.step_up) ** years
    return contrib


def nav_curve(value: pd.Series, contributions: np.ndarray, base: float) -> pd.Series:
    """Time-weighted curve: `value` with the effect of cash flows stripped out.

    Every metric in `comparatore.metrics` assumes a single, unchanging pot of
    money - the classic total/CAGR/Sharpe/drawdown formulas all divide the
    final value by the first one. That breaks the moment `value` receives
    contributions: the series would show a gain on every top-up day that has
    nothing to do with the market. This reconstructs the return the
    underlying strategy actually earned, day by day:

        nav_t = nav_{t-1} * (V_t - c_t) / V_{t-1}

    i.e. the day's growth factor with that day's contribution excluded before
    dividing. With no contributions the growth factors are all 1 and `value`
    is returned unchanged - not an approximation of it, the same object -
    which is what keeps every existing metric byte-identical when the PAC is
    off.
    """
    if contributions is None or not np.asarray(contributions).any():
        return value
    v = value.to_numpy()
    ratios = np.ones(len(v))
    ratios[1:] = (v[1:] - contributions[1:]) / v[:-1]
    return pd.Series(base * np.cumprod(ratios), index=value.index)


def simulate(
    prices: pd.DataFrame,
    weights: dict[str, float],
    initial_value: float,
    rebalance: Rebalance = Rebalance.NONE,
    pac: Pac | None = None,
) -> tuple[pd.Series, pd.DataFrame]:
    """Run the portfolio forward.

    Returns the total value series and the per-sleeve value frame. Each
    instalment of `pac`, if given, is invested at the target weights - the
    same way the initial capital is - the day it lands.
    """
    cols = list(prices.columns)
    w = np.array([weights.get(c, 0.0) for c in cols], dtype=float)
    total_w = w.sum()
    if total_w <= 0:
        raise ValueError("La somma dei pesi deve essere maggiore di zero.")
    w = w / total_w

    step = prices.to_numpy()
    # Daily gross return factor per asset, forward-filled across missing NAVs.
    ratios = np.ones_like(step)
    ratios[1:] = step[1:] / step[:-1]
    ratios = np.nan_to_num(ratios, nan=1.0, posinf=1.0, neginf=1.0)

    rb = rebalance_dates(prices.index, rebalance)
    contrib = contribution_schedule(prices.index, pac)
    holdings = w * initial_value
    values = np.empty_like(step)
    values[0] = holdings

    for i in range(1, len(prices)):
        holdings = holdings * ratios[i]
        if contrib[i]:
            holdings = holdings + w * contrib[i]
        if prices.index[i] in rb:
            holdings = w * holdings.sum()
        values[i] = holdings

    per_sleeve = pd.DataFrame(values, index=prices.index, columns=cols)
    return per_sleeve.sum(axis=1), per_sleeve


def _standalone_curve(
    prices_col: pd.Series, initial_value: float, pac: Pac | None
) -> pd.Series:
    """One fund alone, receiving the same capital and the same PAC schedule."""
    value, _ = simulate(
        prices_col.to_frame(), {prices_col.name: 1.0}, initial_value, Rebalance.NONE, pac
    )
    return value


def run_backtest(
    prices: pd.DataFrame,
    holdings: list[Holding],
    initial_value: float,
    rebalance: Rebalance = Rebalance.NONE,
    mode: FeeMode = FeeMode.NET,
    pac: Pac | None = None,
) -> BacktestResult:
    """Full backtest: portfolio plus each fund standalone, net and gross."""
    prices = prices.dropna(how="all").sort_index()
    # Start where every fund has data, then carry NAVs forward across the
    # calendar gaps that mutual funds and cross-market listings inevitably have.
    first_valid = prices.apply(lambda c: c.first_valid_index()).max()
    if pd.isna(first_valid):
        raise ValueError("Nessun dato di prezzo disponibile per i fondi selezionati.")
    prices = prices.loc[first_valid:].ffill().dropna(how="any")
    if len(prices) < 2:
        raise ValueError(
            "Storico troppo corto: i fondi selezionati non hanno un periodo in comune."
        )

    weights = {h.symbol: h.weight for h in holdings}

    net_prices = adjust_for_fees(prices, holdings, FeeMode.NET)
    gross_prices = adjust_for_fees(prices, holdings, FeeMode.GROSS)
    used = net_prices if mode is FeeMode.NET else gross_prices

    portfolio, sleeves = simulate(used, weights, initial_value, rebalance, pac)
    portfolio_gross, _ = simulate(gross_prices, weights, initial_value, rebalance, pac)
    portfolio_net, _ = simulate(net_prices, weights, initial_value, rebalance, pac)

    contrib = contribution_schedule(prices.index, pac)
    nav = nav_curve(portfolio, contrib, initial_value)
    nav_gross = nav_curve(portfolio_gross, contrib, initial_value)
    invested = pd.Series(initial_value + np.cumsum(contrib), index=prices.index)
    cashflows = [(prices.index[0], -initial_value)] + [
        (prices.index[i], -float(contrib[i]))
        for i in range(1, len(prices))
        if contrib[i]
    ]

    # Each fund alone, for a like-for-like comparison: same starting capital,
    # same PAC. A plain `net_prices / net_prices.iloc[0] * initial_value`
    # would compare a portfolio fed by contributions to funds that never
    # receive any.
    per_fund = pd.DataFrame(
        {col: _standalone_curve(net_prices[col], initial_value, pac) for col in net_prices.columns}
    )
    per_fund_gross = pd.DataFrame(
        {col: _standalone_curve(gross_prices[col], initial_value, pac) for col in gross_prices.columns}
    )

    label_map = {h.symbol: h.label for h in holdings}
    per_fund = per_fund.rename(columns=label_map)
    per_fund_gross = per_fund_gross.rename(columns=label_map)
    sleeves = sleeves.rename(columns=label_map)

    return BacktestResult(
        portfolio=portfolio,
        portfolio_gross=portfolio_gross,
        per_fund=per_fund,
        per_fund_gross=per_fund_gross,
        contributions=sleeves,
        prices=used,
        start=prices.index[0],
        end=prices.index[-1],
        fee_drag=float(portfolio_gross.iloc[-1] - portfolio_net.iloc[-1]),
        nav=nav,
        nav_gross=nav_gross,
        invested=invested,
        cashflows=cashflows,
    )


def coverage_warnings(
    prices: pd.DataFrame, requested_start: dt.date
) -> list[tuple[str, dt.date]]:
    """Funds whose history starts after the requested window: (symbol, first date).

    Returns raw data, not a formatted message: the message is user-facing
    text and belongs in the UI layer, which localizes it (see
    `comparatore.i18n`).
    """
    out = []
    req = pd.Timestamp(requested_start)
    for col in prices.columns:
        first = prices[col].first_valid_index()
        if first is not None and first > req + pd.Timedelta(days=7):
            out.append((col, first.date()))
    return out
