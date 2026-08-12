"""Analisi comparative indipendenti dall'interfaccia.

Il benchmark e' una vista di confronto, non una holding: qui entrano soltanto
curve gia' risolte e validate. Le funzioni usano un calendario comune e dati
mensili completi, cosi' una cella della matrice e' sempre riferita allo stesso
periodo delle altre.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

MONTHS_PER_YEAR = 12
MIN_OBSERVATIONS = 12
ROLLING_YEARS = (1, 3, 5, 10)


@dataclass(frozen=True)
class ComparativeMetrics:
    """Metriche relative al benchmark sul periodo comune."""

    portfolio_cagr: float
    benchmark_cagr: float
    active_return: float
    tracking_error: float
    information_ratio: float
    observations: int
    start: pd.Timestamp | None
    end: pd.Timestamp | None
    reason: str = ""
    portfolio_total_return: float = float("nan")
    benchmark_total_return: float = float("nan")
    portfolio_volatility: float = float("nan")
    benchmark_volatility: float = float("nan")
    portfolio_max_drawdown: float = float("nan")
    benchmark_max_drawdown: float = float("nan")

    def as_dict(self) -> dict[str, object]:
        return {
            "portfolio_cagr": self.portfolio_cagr,
            "benchmark_cagr": self.benchmark_cagr,
            "active_return": self.active_return,
            "tracking_error": self.tracking_error,
            "information_ratio": self.information_ratio,
            "observations": self.observations,
            "start": self.start,
            "end": self.end,
            "reason": self.reason,
            "portfolio_total_return": self.portfolio_total_return,
            "benchmark_total_return": self.benchmark_total_return,
            "portfolio_volatility": self.portfolio_volatility,
            "benchmark_volatility": self.benchmark_volatility,
            "portfolio_max_drawdown": self.portfolio_max_drawdown,
            "benchmark_max_drawdown": self.benchmark_max_drawdown,
        }


def _clean(series: pd.Series) -> pd.Series:
    if series is None:
        return pd.Series(dtype=float)
    out = pd.Series(series, copy=True).astype(float)
    out.index = pd.DatetimeIndex(out.index).tz_localize(None).normalize()
    return out.replace([np.inf, -np.inf], np.nan).dropna().sort_index()


def common_period(*curves: pd.Series) -> pd.DataFrame:
    """Allinea curve sul periodo osservato da tutte, senza backfill."""
    cleaned = [_clean(c) for c in curves]
    if not cleaned:
        return pd.DataFrame()
    frame = pd.concat(cleaned, axis=1, join="inner")
    frame.columns = [getattr(c, "name", None) or f"series_{i}" for i, c in enumerate(curves)]
    return frame.dropna(how="any").sort_index()


def align_common_period(
    portfolio: pd.Series, benchmark: pd.Series
) -> tuple[pd.Series, pd.Series]:
    """Compatibilita' esplicita per chi preferisce ricevere due serie."""
    frame = common_period(portfolio, benchmark)
    if frame.empty:
        return frame.get("series_0", pd.Series(dtype=float)), frame.get(
            "series_1", pd.Series(dtype=float)
        )
    return frame.iloc[:, 0].rename(portfolio.name), frame.iloc[:, 1].rename(benchmark.name)


def monthly_values(curves: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    """Ultimo valore disponibile di ogni mese."""
    if isinstance(curves, pd.Series):
        return _clean(curves).resample("ME").last().dropna()
    frame = curves.copy()
    frame.index = pd.DatetimeIndex(frame.index).tz_localize(None).normalize()
    return frame.sort_index().resample("ME").last()


def monthly_returns(curves: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    """Rendimenti mensili calcolati sugli ultimi valori del mese."""
    values = monthly_values(curves)
    return (
        values.pct_change(fill_method=None)
        .replace([np.inf, -np.inf], np.nan)
        .dropna(how="all")
    )


def _period_years(index: pd.DatetimeIndex) -> float:
    if len(index) < 2:
        return 0.0
    return (index[-1] - index[0]).days / 365.25


def _cagr(curve: pd.Series) -> float:
    curve = _clean(curve)
    years = _period_years(curve.index)
    if years <= 0 or len(curve) < 2 or curve.iloc[0] <= 0 or curve.iloc[-1] <= 0:
        return float("nan")
    return float((curve.iloc[-1] / curve.iloc[0]) ** (1 / years) - 1)


def _total_return(curve: pd.Series) -> float:
    curve = _clean(curve)
    if len(curve) < 2 or curve.iloc[0] == 0:
        return float("nan")
    return float(curve.iloc[-1] / curve.iloc[0] - 1)


def _monthly_volatility(curve: pd.Series) -> float:
    returns = monthly_returns(curve).dropna()
    if len(returns) < 2:
        return float("nan")
    return float(returns.std(ddof=1) * np.sqrt(MONTHS_PER_YEAR))


def _max_drawdown(curve: pd.Series) -> float:
    curve = _clean(curve)
    if len(curve) < 2:
        return float("nan")
    return float((curve / curve.cummax() - 1).min())


def correlation_matrix(
    curves: pd.Series | pd.DataFrame, min_observations: int = MIN_OBSERVATIONS
) -> pd.DataFrame:
    """Correlazioni mensili complete-case, oppure NaN se il campione e' corto."""
    frame = curves.to_frame() if isinstance(curves, pd.Series) else curves.copy()
    frame = monthly_returns(frame).dropna(how="any")
    if len(frame) < min_observations:
        return pd.DataFrame(np.nan, index=frame.columns, columns=frame.columns)
    return frame.corr()


def active_metrics(
    portfolio: pd.Series,
    benchmark: pd.Series,
    min_observations: int = MIN_OBSERVATIONS,
) -> ComparativeMetrics:
    """CAGR, rendimento attivo, tracking error e IR sul periodo comune."""
    common = common_period(portfolio, benchmark)
    if common.empty:
        return ComparativeMetrics(*(float("nan"),) * 5, 0, None, None, "common_period_empty")
    returns = monthly_returns(common).dropna(how="any")
    start, end = common.index[0], common.index[-1]
    if len(returns) < min_observations:
        reason = "insufficient_observations"
        return ComparativeMetrics(
            _cagr(common.iloc[:, 0]), _cagr(common.iloc[:, 1]),
            *(float("nan"),) * 3, len(returns), start, end, reason,
            _total_return(common.iloc[:, 0]), _total_return(common.iloc[:, 1]),
            _monthly_volatility(common.iloc[:, 0]),
            _monthly_volatility(common.iloc[:, 1]),
            _max_drawdown(common.iloc[:, 0]), _max_drawdown(common.iloc[:, 1]),
        )
    active = returns.iloc[:, 0] - returns.iloc[:, 1]
    active_return = float(active.mean() * MONTHS_PER_YEAR)
    tracking_error = float(active.std(ddof=1) * np.sqrt(MONTHS_PER_YEAR))
    if tracking_error <= 1e-12:
        return ComparativeMetrics(
            _cagr(common.iloc[:, 0]), _cagr(common.iloc[:, 1]), active_return,
            float("nan"), float("nan"), len(returns), start, end,
            "tracking_error_zero",
            _total_return(common.iloc[:, 0]), _total_return(common.iloc[:, 1]),
            _monthly_volatility(common.iloc[:, 0]), _monthly_volatility(common.iloc[:, 1]),
            _max_drawdown(common.iloc[:, 0]), _max_drawdown(common.iloc[:, 1]),
        )
    information_ratio = float(active_return / tracking_error)
    reason = ""
    return ComparativeMetrics(
        _cagr(common.iloc[:, 0]), _cagr(common.iloc[:, 1]), active_return,
        tracking_error, information_ratio, len(returns), start, end, reason,
        _total_return(common.iloc[:, 0]), _total_return(common.iloc[:, 1]),
        _monthly_volatility(common.iloc[:, 0]), _monthly_volatility(common.iloc[:, 1]),
        _max_drawdown(common.iloc[:, 0]), _max_drawdown(common.iloc[:, 1]),
    )


def rolling_returns(
    curve: pd.Series,
    windows: tuple[int, ...] = ROLLING_YEARS,
) -> dict[int, pd.Series]:
    """Rendimento annualizzato delle finestre mensili 1/3/5/10 anni."""
    values = monthly_values(_clean(curve))
    if values.empty:
        return {
            years: pd.Series(dtype=float, name=f"rolling_{years}y")
            for years in windows
        }
    full_index = pd.date_range(
        values.index[0].to_period("M").to_timestamp("M"),
        values.index[-1].to_period("M").to_timestamp("M"),
        freq="ME",
    )
    values = values.reindex(full_index)
    out: dict[int, pd.Series] = {}
    for years in windows:
        months = years * MONTHS_PER_YEAR
        if len(values) < months:
            out[years] = pd.Series(dtype=float, name=f"rolling_{years}y")
            continue
        result = pd.Series(np.nan, index=values.index, name=f"rolling_{years}y")
        for end_pos in range(months - 1, len(values)):
            window = values.iloc[end_pos - months + 1:end_pos + 1]
            if window.isna().any() or window.iloc[0] <= 0 or window.iloc[-1] <= 0:
                continue
            result.iloc[end_pos] = (window.iloc[-1] / window.iloc[0]) ** (1 / years) - 1
        out[years] = result.dropna()
    return out


def rolling_summary(values: pd.Series) -> dict[str, float | int]:
    """Riepilogo robusto di una serie rolling."""
    values = pd.Series(values).replace([np.inf, -np.inf], np.nan).dropna()
    if values.empty:
        return {
            "observations": 0, "worst": float("nan"), "median": float("nan"),
            "best": float("nan"), "positive_pct": float("nan"),
        }
    return {
        "observations": int(len(values)),
        "worst": float(values.min()),
        "median": float(values.median()),
        "best": float(values.max()),
        "positive_pct": float((values > 0).mean()),
    }


def compare(
    portfolio: pd.Series,
    benchmark: pd.Series | None = None,
    min_observations: int = MIN_OBSERVATIONS,
) -> dict[str, object]:
    """Calcola tutte le analisi comparative in una struttura serializzabile."""
    if benchmark is None:
        frame = common_period(portfolio)
        metrics = None
    else:
        frame = common_period(portfolio, benchmark)
        metrics = active_metrics(portfolio, benchmark, min_observations)
    monthly = monthly_returns(frame)
    return {
        "common": frame,
        "monthly_returns": monthly,
        "correlation": correlation_matrix(frame, min_observations),
        "metrics": metrics,
        "rolling": rolling_returns(frame.iloc[:, 0]) if not frame.empty else {},
        "rolling_benchmark": (
            rolling_returns(frame.iloc[:, 1]) if benchmark is not None and not frame.empty else {}
        ),
    }
