"""Analisi temporali pure per le viste avanzate.

Il modulo non conosce Streamlit: riceve curve gia' risolte e restituisce
DataFrame e metadati pronti per una qualsiasi interfaccia. Le finestre usano
le date reali della serie, senza comprimere buchi di calendario in rendimenti
che sembrerebbero osservati.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import metrics

ROLLING_HORIZONS = (1, 3, 5, 10, 15, 20)
ROLLING_METRICS = ("cagr", "volatility", "sharpe", "sortino", "calmar", "ulcer_index")
_EDGE_TOLERANCE_DAYS = 15


def _rolling_series(
    values: dict[pd.Timestamp, float], kind: str, years: int,
    coverage: tuple[pd.Timestamp, pd.Timestamp] | None, reason: str = "",
) -> pd.Series:
    """Costruisce il risultato con copertura e motivo leggibili dall'interfaccia."""
    out = pd.Series(values, dtype=float, name=f"{kind}_{years}y").sort_index()
    out.attrs["coverage"] = coverage
    out.attrs["reason"] = reason
    return out


@dataclass(frozen=True)
class HeatmapResult:
    """Matrice mensile e rendimento composto annuo della stessa curva."""

    monthly: pd.DataFrame
    annual: pd.Series
    partial_months: frozenset[pd.Timestamp]
    partial_years: frozenset[int]
    start: pd.Timestamp | None
    end: pd.Timestamp | None


def _clean(curve: pd.Series) -> pd.Series:
    if curve is None:
        return pd.Series(dtype=float)
    values = pd.Series(curve, copy=True).astype(float)
    values.index = pd.DatetimeIndex(values.index).tz_localize(None).normalize()
    return values.replace([np.inf, -np.inf], np.nan).dropna().sort_index()


def _frequency_factor(index: pd.DatetimeIndex) -> int:
    """Stima il fattore annuo senza chiamare giornaliero un CSV mensile."""
    if len(index) < 2:
        return 252
    days = np.diff(index.as_unit("ns").asi8) / (24 * 60 * 60 * 1e9)
    median = float(np.median(days))
    if median <= 3:
        return 252
    if median <= 10:
        return 52
    if median <= 45:
        return 12
    return 1


def _has_acceptable_gaps(index: pd.DatetimeIndex, factor: int) -> bool:
    if len(index) < 2:
        return False
    gaps = np.diff(index.as_unit("ns").asi8) / (24 * 60 * 60 * 1e9)
    limit = 15 if factor >= 52 else 45 if factor == 12 else 400
    return bool(np.max(gaps) <= limit)


def _metric(curve: pd.Series, kind: str, risk_free: float, factor: int) -> float:
    values = _clean(curve)
    if len(values) < 2:
        return float("nan")
    returns = values.pct_change().dropna()
    if len(returns) < 2:
        return float("nan")
    annual_cagr = metrics.cagr(values)
    if kind == "cagr":
        return annual_cagr
    if kind == "volatility":
        return float(returns.std(ddof=1) * np.sqrt(factor))
    period_rf = (1.0 + risk_free) ** (1.0 / factor) - 1.0
    excess = returns.to_numpy() - period_rf
    if kind == "sharpe":
        deviation = float(np.std(excess, ddof=1))
        return float(np.mean(excess) / deviation * np.sqrt(factor)) if deviation else float("nan")
    if kind == "sortino":
        downside = np.minimum(excess, 0.0)
        deviation = float(np.sqrt(np.mean(np.square(downside))))
        return float(np.mean(excess) / deviation * np.sqrt(factor)) if deviation else float("nan")
    if kind == "calmar":
        drawdown = metrics.max_drawdown(values)
        if drawdown and np.isfinite(drawdown):
            return float(annual_cagr / abs(drawdown))
        return float("nan")
    if kind == "ulcer_index":
        return metrics.ulcer_index(values)
    raise ValueError(f"Metrica rolling sconosciuta: {kind}")


def rolling_metric(
    curve: pd.Series,
    years: int,
    kind: str = "cagr",
    risk_free: float = 0.0,
    mode: str = "continuous",
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
) -> pd.Series:
    """Calcola una metrica su ogni finestra completa dell'orizzonte scelto."""
    if years not in ROLLING_HORIZONS:
        raise ValueError("Orizzonte rolling non supportato")
    if kind not in ROLLING_METRICS:
        raise ValueError("Metrica rolling non supportata")
    if mode not in {"continuous", "annual"}:
        raise ValueError("Modalita' rolling non supportata")
    values = _clean(curve)
    if values.empty:
        return _rolling_series({}, kind, years, None, "empty_series")
    factor = _frequency_factor(values.index)
    display_start = pd.Timestamp(start).normalize() if start is not None else values.index[0]
    display_end = pd.Timestamp(end).normalize() if end is not None else values.index[-1]
    annual_end_dates: dict[int, pd.Timestamp] | None = None
    if mode == "annual":
        # Un solo punto per anno: l'ultima osservazione di dicembre. Un
        # dicembre troncato non e' un anno concluso e resta indisponibile.
        december = values[values.index.month == 12]
        annual_end_dates = {
            year: group.index[-1]
            for year, group in december.groupby(december.index.year)
            if group.index[-1].day >= 28
        }
    result: dict[pd.Timestamp, float] = {}
    for position, date in enumerate(values.index):
        if date < display_start or date > display_end:
            continue
        if mode == "annual" and date != (annual_end_dates or {}).get(date.year):
            continue
        target = date - pd.DateOffset(years=years)
        insertion = int(values.index.searchsorted(target, side="left"))
        candidates = [position for position in (insertion - 1, insertion)
                      if 0 <= position < len(values.index)]
        gap_limit = 15 if factor >= 52 else 45 if factor == 12 else 400
        # Non si puo' scegliere il primo valore dopo un buco lungo: sembrerebbe
        # una finestra completa pur avendo perso settimane o mesi di mercato.
        if insertion < len(values.index) and insertion > 0:
            if (values.index[insertion] - values.index[insertion - 1]).days > gap_limit:
                candidates = [candidate for candidate in candidates if candidate != insertion]
        if not candidates:
            continue
        start_position = min(
            candidates, key=lambda candidate: abs(values.index[candidate] - target)
        )
        if start_position < 0 or start_position >= position:
            continue
        window = values.iloc[start_position:position + 1]
        if len(window) < 3 or not _has_acceptable_gaps(window.index, factor):
            continue
        # Un giorno di borsa festivo puo' anticipare il bordo, ma un buco lungo
        # non deve diventare una finestra apparentemente continua.
        if abs((target - window.index[0]).days) > _EDGE_TOLERANCE_DAYS:
            continue
        value = _metric(window, kind, risk_free, factor)
        if np.isfinite(value):
            result[date] = value
    coverage = (values.index[0], values.index[-1])
    reason = "" if result else "insufficient_history_or_gaps"
    return _rolling_series(result, kind, years, coverage, reason)


def rolling_distribution(
    curve: pd.Series,
    years: int,
    kind: str = "cagr",
    risk_free: float = 0.0,
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
) -> pd.Series:
    """Alias semantico per la distribuzione: la serie rolling e' la fonte."""
    return rolling_metric(curve, years, kind, risk_free, "continuous", start, end)


def _monthly_return_series(values: pd.Series) -> tuple[pd.Series, pd.Series]:
    monthly_values = values.resample("ME").last()
    monthly_returns = monthly_values.pct_change(fill_method=None)
    first_month = monthly_values.index[0]
    # Il primo mese ha una base reale nella prima quota, anche se la serie
    # non parte il primo giorno del mese: non si inventa il mese precedente.
    monthly_returns.loc[first_month] = monthly_values.iloc[0] / values.iloc[0] - 1.0
    for previous, current in zip(monthly_values.index[:-1], monthly_values.index[1:]):
        if current.to_period("M").ordinal - previous.to_period("M").ordinal != 1:
            monthly_returns.loc[current] = np.nan
    return monthly_values, monthly_returns


def calendar_heatmap(
    curve: pd.Series,
    last_years: int = 10,
    show_all: bool = False,
) -> HeatmapResult:
    """Matrice anno/mese con rendimento annuo composto e copertura esplicita."""
    values = _clean(curve)
    if values.empty:
        return HeatmapResult(
            pd.DataFrame(columns=list(range(1, 13)) + ["annual_return"]),
            pd.Series(dtype=float, name="annual_return"),
            frozenset(), frozenset(), None, None,
        )
    monthly_values, monthly_returns = _monthly_return_series(values)
    first_year, last_year = values.index[0].year, values.index[-1].year
    years = list(range(first_year, last_year + 1))
    if not show_all:
        years = years[-max(1, last_years):]
    rows: dict[int, dict[int | str, float]] = {}
    annual: dict[int, float] = {}
    partial_months: set[pd.Timestamp] = set()
    partial_years: set[int] = set()
    first_date, last_date = values.index[0], values.index[-1]
    for month in monthly_values.index:
        if month == monthly_values.index[0] and first_date.day > 1:
            partial_months.add(month)
        if month == monthly_values.index[-1] and last_date < month:
            partial_months.add(month)
    for year in years:
        row = {month: float("nan") for month in range(1, 13)}
        year_returns = monthly_returns[monthly_returns.index.year == year]
        for month, value in year_returns.items():
            row[month.month] = value
        expected = list(range(1, 13))
        if year == first_year:
            expected = list(range(monthly_returns.index[0].month, 13))
            if first_date.month != 1 or first_date.day > 1:
                partial_years.add(year)
        if year == last_year and last_date < pd.Timestamp(year=year, month=12, day=31):
            first_month_number = monthly_returns.index[0].month if year == first_year else 1
            expected = expected[:max(1, last_date.month - first_month_number + 1)]
            partial_years.add(year)
        selected = [row[month] for month in expected]
        if selected and all(np.isfinite(selected)):
            annual[year] = float(np.prod(1.0 + np.asarray(selected)) - 1.0)
        else:
            annual[year] = float("nan")
        row["annual_return"] = annual[year]
        rows[year] = row
    matrix = pd.DataFrame.from_dict(rows, orient="index")
    matrix.index.name = "year"
    matrix = matrix.reindex(columns=list(range(1, 13)) + ["annual_return"])
    annual_series = pd.Series(annual, dtype=float, name="annual_return")
    return HeatmapResult(
        matrix.sort_index(ascending=False), annual_series.sort_index(ascending=False),
        frozenset(partial_months), frozenset(partial_years), values.index[0], values.index[-1],
    )


def rolling_summary(values: pd.Series) -> dict[str, float | int]:
    """Riepilogo comune usato dal grafico e dal pannello distribuzione."""
    clean = pd.Series(values).replace([np.inf, -np.inf], np.nan).dropna()
    if clean.empty:
        return {
            "observations": 0, "worst": float("nan"), "median": float("nan"),
            "best": float("nan"), "p05": float("nan"), "p95": float("nan"),
        }
    return {
        "observations": int(len(clean)),
        "worst": float(clean.min()),
        "median": float(clean.median()),
        "best": float(clean.max()),
        "p05": float(clean.quantile(0.05)),
        "p95": float(clean.quantile(0.95)),
    }
