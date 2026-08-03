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


class BacktestInputError(ValueError):
    """Prezzi o pesi inutilizzabili: il backtest non parte.

    Sottoclasse di `ValueError` per restare compatibile con chi cattura
    quell'eccezione usando la libreria da script. `kind` e `symbols` sono
    strutturati apposta perche' l'interfaccia (`app.py`) deve poter tradurre
    l'errore con `t()`, non limitarsi a mostrare `str(exc)`.
    """

    def __init__(self, kind: str, symbols: list[str], message: str) -> None:
        super().__init__(message)
        self.kind = kind
        self.symbols = symbols


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
    # per_fund*, contributions: columns keyed by symbol, not by label - see
    # `labels` below for the symbol -> display name mapping.
    per_fund: pd.DataFrame  # value of the full capital in each fund alone
    per_fund_gross: pd.DataFrame
    per_fund_nav: pd.DataFrame  # same, contributions stripped out (time-weighted)
    contributions: pd.DataFrame  # value of each sleeve inside the portfolio
    prices: pd.DataFrame  # fee-adjusted prices actually used
    start: pd.Timestamp
    end: pd.Timestamp
    fee_drag: float  # final gross value - final net value, base currency
    nav: pd.Series  # portfolio value with contributions stripped out (time-weighted)
    nav_gross: pd.Series  # same, fee-free
    invested: pd.Series  # cumulative capital paid in: initial value + instalments
    cashflows: list[tuple[pd.Timestamp, float]]  # for XIRR: negative = paid in
    pic: pd.Series | None  # the same total money invested in one go on day one
    labels: dict[str, str]  # symbol -> unique display label (see `etichette_uniche`)


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


def valida_prezzi(prices: pd.DataFrame, *, consenti_nan: bool = False) -> None:
    """Rifiuta un frame di prezzi inutilizzabile invece di lasciarlo passare.

    Nessun prezzo di mercato e' zero, negativo o infinito: un valore cosi'
    indica un errore di fonte o di file caricato a mano, non un dato da
    trattare come "nessuna variazione" (era il comportamento di
    `np.nan_to_num` che questa funzione sostituisce - vedi
    `docs/audit-codebase-2026-08-01.md`, P1). Un `NaN` invece e' spesso un
    buco di calendario legittimo (fondi comuni, listati incrociati), chiuso a
    monte con un `ffill`: e' ammesso solo con `consenti_nan=True`, che
    `run_backtest` usa prima di quel passaggio; `simulate`, che gira
    sull'output gia' pulito, valida in modo stretto.
    """
    if prices.index.has_duplicates:
        duplicate = sorted({str(d.date()) for d in prices.index[prices.index.duplicated()]})
        raise BacktestInputError(
            "date_duplicate", duplicate,
            f"Date duplicate nella serie storica: {', '.join(duplicate)}.",
        )

    if not prices.index.is_monotonic_increasing:
        raise BacktestInputError(
            "indice_non_ordinato", [],
            "L'indice delle date non è ordinato in senso crescente.",
        )

    valori = prices.to_numpy(dtype=float)
    mancante = np.isnan(valori)
    non_valido = (~mancante) & ~((valori > 0) & np.isfinite(valori))
    if not consenti_nan:
        non_valido = non_valido | mancante
    if non_valido.any():
        colonne = [
            str(prices.columns[j]) for j in range(prices.shape[1]) if non_valido[:, j].any()
        ]
        raise BacktestInputError(
            "quote_non_valide", colonne,
            f"Quote non valide (zero, negative, non finite o mancanti) per: "
            f"{', '.join(colonne)}.",
        )


def valida_holdings(holdings: list[Holding], colonne) -> None:
    """Nessun simbolo duplicato, ogni simbolo con una colonna di prezzi, pesi
    validi con somma positiva.

    E' la barriera che rende impossibile far girare il backtest su un
    sottoinsieme del portafoglio senza che sia una scelta esplicita: prima di
    questa funzione un fondo senza prezzi veniva semplicemente escluso dagli
    `Holding` costruiti a monte in `app.py`, e il motore rinormalizzava i pesi
    dei rimasti come se il portafoglio fosse sempre stato quello.
    """
    if not holdings:
        raise BacktestInputError(
            "simboli_senza_prezzi", [], "Nessun fondo da simulare."
        )

    simboli = [h.symbol for h in holdings]
    duplicati = sorted({s for s in simboli if simboli.count(s) > 1})
    if duplicati:
        raise BacktestInputError(
            "simboli_duplicati", duplicati,
            f"Simboli duplicati nel portafoglio: {', '.join(duplicati)}.",
        )

    disponibili = set(colonne)
    assenti = [s for s in simboli if s not in disponibili]
    if assenti:
        raise BacktestInputError(
            "simboli_senza_prezzi", assenti,
            f"Nessun prezzo disponibile per: {', '.join(assenti)}.",
        )

    non_validi = [h.symbol for h in holdings if not np.isfinite(h.weight) or h.weight < 0]
    if non_validi:
        raise BacktestInputError(
            "pesi_non_validi", non_validi,
            f"Peso non valido per: {', '.join(non_validi)}.",
        )
    if sum(h.weight for h in holdings) <= 0:
        raise BacktestInputError(
            "pesi_non_validi", simboli,
            "La somma dei pesi deve essere maggiore di zero.",
        )


def etichette_uniche(holdings: list[Holding]) -> dict[str, str]:
    """Simbolo -> etichetta da mostrare, disambiguata quando due fondi
    condividono lo stesso nome visuale.

    Il simbolo resta la chiave interna delle colonne per tutto il calcolo
    (vedi `run_backtest`): questa e' l'unica traduzione verso un nome
    leggibile, fatta una volta sola invece di lasciare che ogni punto
    dell'interfaccia la reinventi rinominando colonne.
    """
    conteggio: dict[str, int] = {}
    for h in holdings:
        conteggio[h.label] = conteggio.get(h.label, 0) + 1
    return {
        h.symbol: h.label if conteggio[h.label] == 1 else f"{h.label} ({h.symbol})"
        for h in holdings
    }


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
    prices = prices.sort_index()
    valida_prezzi(prices)
    cols = list(prices.columns)
    w = np.array([weights.get(c, 0.0) for c in cols], dtype=float)
    total_w = w.sum()
    if total_w <= 0:
        raise ValueError("La somma dei pesi deve essere maggiore di zero.")
    w = w / total_w

    step = prices.to_numpy()
    # Il rapporto giorno/giorno e' definito ovunque perche' `valida_prezzi` ha
    # gia' rifiutato zero, negativi e non finiti: non serve piu' sostituire
    # nulla con `np.nan_to_num`, che trasformava un dato corrotto in un
    # rendimento nullo invece di segnalarlo (vedi audit-codebase-2026-08-01.md, P1).
    ratios = np.ones_like(step)
    ratios[1:] = step[1:] / step[:-1]

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
    valida_holdings(holdings, prices.columns)
    # Solo le colonne del portafoglio, nell'ordine degli holding: scarta
    # qualunque colonna estranea rimasta nel frame passato dal chiamante e
    # rende l'ordine deterministico invece di dipendere da come e' stato
    # assemblato `prices`.
    prices = prices[[h.symbol for h in holdings]]
    valida_prezzi(prices, consenti_nan=True)

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
        {col: _standalone_curve(gross_prices[col], initial_value, pac)
         for col in gross_prices.columns}
    )

    # Le colonne restano indicizzate per simbolo fino in fondo: rinominarle
    # qui con l'etichetta visuale (comportamento di prima) rompe il calcolo
    # quando due strumenti condividono lo stesso nome - due colonne
    # duplicate, e la selezione di una di esse in `nav_curve()` diventa un
    # DataFrame invece di una Series (vedi audit-codebase-2026-08-01.md, P1).
    # `labels` e' l'unica traduzione verso un nome leggibile, gia' disambiguata.
    labels = etichette_uniche(holdings)

    # Time-weighted curves for the standalone funds too. Without them a
    # comparison table would put per-fund metrics inflated by the
    # contributions next to portfolio metrics already stripped of them - the
    # rows would not be comparable. With no PAC this is the same object as
    # `per_fund`, exactly as `nav` is the same object as `portfolio`.
    per_fund_nav = per_fund if not contrib.any() else pd.DataFrame(
        {col: nav_curve(per_fund[col], contrib, initial_value) for col in per_fund}
    )

    # PIC: the same money (initial capital plus every instalment) invested in
    # one go on day one - the natural yardstick for a PAC, i.e. what spreading
    # the entry over time cost or saved. None without a PAC, where it would
    # just be `portfolio` again.
    pic = None
    if contrib.any():
        pic, _ = simulate(used, weights, float(invested.iloc[-1]), rebalance, None)

    return BacktestResult(
        portfolio=portfolio,
        portfolio_gross=portfolio_gross,
        per_fund=per_fund,
        per_fund_gross=per_fund_gross,
        per_fund_nav=per_fund_nav,
        contributions=sleeves,
        prices=used,
        start=prices.index[0],
        end=prices.index[-1],
        fee_drag=float(portfolio_gross.iloc[-1] - portfolio_net.iloc[-1]),
        nav=nav,
        nav_gross=nav_gross,
        invested=invested,
        cashflows=cashflows,
        pic=pic,
        labels=labels,
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
