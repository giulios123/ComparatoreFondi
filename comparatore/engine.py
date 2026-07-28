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


_FREQ = {
    Rebalance.MONTHLY: "M",
    Rebalance.QUARTERLY: "Q",
    Rebalance.YEARLY: "Y",
}


@dataclass
class Holding:
    symbol: str
    label: str
    weight: float  # portfolio share, 0..1
    ter: float = 0.0  # annual fraction already inside the NAV
    extra_cost: float = 0.0  # annual fraction NOT in the NAV


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


def rebalance_dates(index: pd.DatetimeIndex, mode: Rebalance) -> set[pd.Timestamp]:
    """First trading day of each period."""
    if mode is Rebalance.NONE:
        return set()
    periods = index.to_period(_FREQ[mode])
    is_first = pd.Series(periods, index=index).ne(pd.Series(periods, index=index).shift())
    dates = set(index[is_first.to_numpy()])
    dates.discard(index[0])  # the initial purchase is not a rebalance
    return dates


def simulate(
    prices: pd.DataFrame,
    weights: dict[str, float],
    initial_value: float,
    rebalance: Rebalance = Rebalance.NONE,
) -> tuple[pd.Series, pd.DataFrame]:
    """Run the portfolio forward.

    Returns the total value series and the per-sleeve value frame.
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
    holdings = w * initial_value
    values = np.empty_like(step)
    values[0] = holdings

    for i in range(1, len(prices)):
        holdings = holdings * ratios[i]
        if prices.index[i] in rb:
            holdings = w * holdings.sum()
        values[i] = holdings

    per_sleeve = pd.DataFrame(values, index=prices.index, columns=cols)
    return per_sleeve.sum(axis=1), per_sleeve


def run_backtest(
    prices: pd.DataFrame,
    holdings: list[Holding],
    initial_value: float,
    rebalance: Rebalance = Rebalance.NONE,
    mode: FeeMode = FeeMode.NET,
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

    portfolio, sleeves = simulate(used, weights, initial_value, rebalance)
    portfolio_gross, _ = simulate(gross_prices, weights, initial_value, rebalance)
    portfolio_net, _ = simulate(net_prices, weights, initial_value, rebalance)

    # Each fund holding 100% of the capital, for a like-for-like comparison.
    per_fund = net_prices / net_prices.iloc[0] * initial_value
    per_fund_gross = gross_prices / gross_prices.iloc[0] * initial_value

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
    )


def coverage_warnings(
    prices: pd.DataFrame, requested_start: dt.date
) -> list[str]:
    """Flag funds whose history starts after the requested window."""
    msgs = []
    req = pd.Timestamp(requested_start)
    for col in prices.columns:
        first = prices[col].first_valid_index()
        if first is not None and first > req + pd.Timedelta(days=7):
            msgs.append(f"{col}: dati disponibili solo dal {first.date()}")
    return msgs
