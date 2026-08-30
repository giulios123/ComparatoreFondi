"""Ricerca storica di allocazioni senza dipendenze dall'interfaccia."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .engine import Pac, Rebalance, contribution_schedule, rebalance_dates

OBJECTIVES = (
    "cagr", "volatility", "sharpe", "sortino", "calmar", "drawdown", "ulcer_index",
)
EXTREME_OBJECTIVES = ("cagr", "volatility", "sharpe", "drawdown")
DEFAULT_SAMPLE_COUNT = 5_000
MIN_SAMPLE_COUNT = 1_000
MAX_SAMPLE_COUNT = 20_000


@dataclass(frozen=True)
class FrontierResult:
    """Candidati, metriche, Pareto ed estremi trovati dalla ricerca."""

    weights: pd.DataFrame
    metrics: pd.DataFrame
    pareto_ids: tuple[str, ...]
    extrema: dict[str, str]
    input_fingerprint: str
    evaluations: int


def _fingerprint(
    prices: pd.DataFrame,
    symbols: list[str],
    initial_value: float,
    rebalance: Rebalance,
    pac: Pac | None,
    risk_free: float,
    lower: np.ndarray,
    upper: np.ndarray,
    current: np.ndarray | None,
) -> str:
    """Identifica anche i parametri che possono rendere vecchio un risultato."""
    payload = {
        "symbols": symbols,
        "start": str(prices.index[0]) if len(prices) else "",
        "end": str(prices.index[-1]) if len(prices) else "",
        "index": hashlib.sha256(
            prices.index.as_unit("ns").asi8.tobytes()
        ).hexdigest() if len(prices) else "",
        "prices": hashlib.sha256(prices.to_numpy(dtype=float).tobytes()).hexdigest(),
        "initial": initial_value,
        "rebalance": rebalance.value,
        "risk_free": risk_free,
        "pac": vars(pac) if pac else None,
        "lower": lower.tolist(),
        "upper": upper.tolist(),
        "current": current.tolist() if current is not None else None,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def input_fingerprint(
    prices: pd.DataFrame,
    symbols: list[str],
    initial_value: float,
    rebalance: Rebalance,
    pac: Pac | None,
    risk_free: float,
    lower: dict[str, float] | None = None,
    upper: dict[str, float] | None = None,
    current_weights: dict[str, float] | None = None,
) -> str:
    """Fingerprint pubblico per impedire di riusare un risultato obsoleto."""
    lo = np.asarray([float((lower or {}).get(symbol, 0.0)) for symbol in symbols])
    hi = np.asarray([float((upper or {}).get(symbol, 1.0)) for symbol in symbols])
    current = (
        np.asarray([float((current_weights or {}).get(symbol, 0.0)) for symbol in symbols])
        if current_weights is not None else None
    )
    return _fingerprint(
        prices, symbols, initial_value, rebalance, pac, risk_free, lo, hi, current,
    )


def _project_simplex(values: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
    """Proietta su sum(w)=1 con limiti per fondo usando una bisezione."""
    if lower.sum() > 1.0 + 1e-10 or upper.sum() < 1.0 - 1e-10:
        raise ValueError("I limiti dei pesi non consentono una somma del 100%.")
    values = np.asarray(values, dtype=float)
    left, right = -1.0, 1.0
    for _ in range(80):
        middle = (left + right) / 2.0
        candidate = np.clip(values + middle, lower, upper)
        if candidate.sum() < 1.0:
            left = middle
        else:
            right = middle
    return np.clip(values + (left + right) / 2.0, lower, upper)


def _sample_weights(
    count: int, lower: np.ndarray, upper: np.ndarray, seed: int, anchors: list[np.ndarray]
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = [_project_simplex(anchor, lower, upper) for anchor in anchors]
    while len(out) < count:
        out.append(_project_simplex(rng.dirichlet(np.ones(len(lower))), lower, upper))
    return np.asarray(out[:count], dtype=float)


def _unique_weights(weights: np.ndarray) -> np.ndarray:
    """Rimuove duplicati soltanto quando i vincoli lasciano un solo mix."""
    seen: set[tuple[float, ...]] = set()
    unique = []
    for row in np.asarray(weights, dtype=float):
        key = tuple(np.round(row, 12))
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    # Con una regione davvero univoca tutte le proiezioni coincidono; negli
    # altri casi conserviamo il numero di campioni richiesto dall'utente.
    return np.asarray(unique, dtype=float) if len(unique) == 1 else weights


def _batch_metrics(
    prices: pd.DataFrame,
    weights: np.ndarray,
    initial_value: float,
    rebalance: Rebalance,
    pac: Pac | None,
    risk_free: float,
    batch_size: int = 128,
    progress: Callable[[float], None] | None = None,
) -> pd.DataFrame:
    """Valuta molte allocazioni contemporaneamente, senza creare Streamlit."""
    if prices.empty or len(prices) < 2:
        raise ValueError("Storico insufficiente per la frontiera.")
    matrix = prices.to_numpy(dtype=float)
    if not np.isfinite(matrix).all() or (matrix <= 0).any():
        raise ValueError("Prezzi non validi per la frontiera.")
    ratios = np.ones_like(matrix)
    ratios[1:] = matrix[1:] / matrix[:-1]
    contributions = contribution_schedule(prices.index, pac)
    rebalance_days = rebalance_dates(prices.index, rebalance)
    if len(prices.index) < 2:
        factor = 252
    else:
        median_days = float(
            np.median(np.diff(prices.index.as_unit("ns").asi8) / 86_400_000_000_000)
        )
        factor = 252 if median_days <= 3 else 52 if median_days <= 10 else 12
    years = (prices.index[-1] - prices.index[0]).days / 365.25
    rows: list[np.ndarray] = []
    for first in range(0, len(weights), batch_size):
        current_weights = weights[first:first + batch_size]
        holdings = current_weights * initial_value
        values = np.empty((len(current_weights), len(prices)), dtype=float)
        values[:, 0] = holdings.sum(axis=1)
        for position in range(1, len(prices)):
            holdings *= ratios[position]
            if contributions[position]:
                holdings += current_weights * contributions[position]
            if prices.index[position] in rebalance_days:
                holdings = current_weights * holdings.sum(axis=1)[:, None]
            values[:, position] = holdings.sum(axis=1)
        nav = values.copy()
        if np.any(contributions):
            nav_ratios = np.ones_like(values)
            nav_ratios[:, 1:] = (values[:, 1:] - contributions[1:]) / values[:, :-1]
            nav = initial_value * np.cumprod(nav_ratios, axis=1)
        returns = nav[:, 1:] / nav[:, :-1] - 1.0
        daily_rf = (1.0 + risk_free) ** (1.0 / factor) - 1.0
        excess = returns - daily_rf
        deviation = np.std(excess, axis=1, ddof=1)
        downside = np.sqrt(np.mean(np.square(np.minimum(excess, 0.0)), axis=1))
        peaks = np.maximum.accumulate(nav, axis=1)
        drawdowns = nav / peaks - 1.0
        max_dd = np.min(drawdowns, axis=1)
        cagr = np.full(len(current_weights), np.nan)
        if years > 0:
            cagr = np.power(nav[:, -1] / nav[:, 0], 1.0 / years) - 1.0
        volatility = np.std(returns, axis=1, ddof=1) * np.sqrt(factor)
        sharpe = np.divide(
            np.mean(excess, axis=1) * np.sqrt(factor), deviation,
            out=np.full(len(current_weights), np.nan), where=deviation > 0,
        )
        sortino = np.divide(
            np.mean(excess, axis=1) * np.sqrt(factor), downside,
            out=np.full(len(current_weights), np.nan), where=downside > 0,
        )
        calmar = np.divide(
            cagr, np.abs(max_dd), out=np.full(len(current_weights), np.nan), where=max_dd != 0,
        )
        ulcer = np.sqrt(np.mean(np.square(drawdowns), axis=1))
        rows.append(np.column_stack((cagr, volatility, sharpe, sortino, calmar, -max_dd, ulcer)))
        if progress:
            progress(min(1.0, (first + len(current_weights)) / len(weights)))
    return pd.DataFrame(
        np.vstack(rows), columns=OBJECTIVES,
    )


def evaluate_weights(
    prices: pd.DataFrame,
    symbols: list[str],
    initial_value: float,
    rebalance: Rebalance,
    pac: Pac | None,
    risk_free: float,
    weights: dict[str, float],
) -> pd.Series:
    """Valuta un solo mix con la stessa pipeline batch della ricerca.

    L'interfaccia serve al punto del portafoglio attuale: riusare esattamente
    il valutatore dei candidati evita che il grafico confronti metriche calcolate
    su periodi, costi o trattamenti dei versamenti differenti.
    """
    if list(prices.columns) != list(symbols):
        raise ValueError("Simboli e colonne dei prezzi non coincidono.")
    vector = np.asarray([float(weights.get(symbol, 0.0)) for symbol in symbols])
    total = float(vector.sum())
    if total <= 0:
        raise ValueError("La somma dei pesi deve essere maggiore di zero.")
    vector /= total
    return _batch_metrics(
        prices, vector.reshape(1, -1), initial_value, rebalance, pac, risk_free,
    ).iloc[0]


def _better(value: float, reference: float, maximize: bool) -> bool:
    if not np.isfinite(value):
        return False
    return value > reference + 1e-12 if maximize else value < reference - 1e-12


def _refine(
    prices: pd.DataFrame,
    weights: list[np.ndarray],
    metric_rows: list[np.ndarray],
    lower: np.ndarray,
    upper: np.ndarray,
    initial_value: float,
    rebalance: Rebalance,
    pac: Pac | None,
    risk_free: float,
    budget: int = 10_000,
    progress: Callable[[float], None] | None = None,
) -> int:
    """Migliora i candidati estremi con trasferimenti locali ammissibili."""
    seen = {tuple(np.round(candidate, 12)) for candidate in weights}
    evaluations = 0
    for objective in EXTREME_OBJECTIVES:
        column = OBJECTIVES.index(objective)
        for maximize in (True, False):
            available = [
                i for i, row in enumerate(metric_rows) if np.isfinite(row[column])
            ]
            if not available:
                continue
            best_index = max(available, key=lambda i: metric_rows[i][column]) if maximize else min(
                available, key=lambda i: metric_rows[i][column]
            )
            current = weights[best_index].copy()
            current_value = metric_rows[best_index][column]
            for step in (0.05, 0.01, 0.002, 0.0005, 0.0001):
                improved = True
                while improved and evaluations < budget:
                    improved = False
                    candidates: list[np.ndarray] = []
                    for source in range(len(current)):
                        for target in range(len(current)):
                            if source == target or evaluations >= budget:
                                continue
                            candidate = current.copy()
                            candidate[source] += step
                            candidate[target] -= step
                            fuori_limite = (candidate < lower - 1e-10).any() or (
                                candidate > upper + 1e-10
                            ).any()
                            if fuori_limite:
                                continue
                            key = tuple(np.round(candidate, 12))
                            if key in seen:
                                continue
                            seen.add(key)
                            candidates.append(candidate)
                    if candidates:
                        candidates = candidates[: max(0, budget - evaluations)]
                    if candidates:
                        new_rows = _batch_metrics(
                            prices, np.asarray(candidates), initial_value, rebalance, pac,
                            risk_free,
                        ).to_numpy(dtype=float)
                        weights.extend(candidates)
                        metric_rows.extend(new_rows)
                        evaluations += len(candidates)
                        if progress:
                            progress(min(1.0, evaluations / budget))
                        viable = [
                            i for i, row in enumerate(new_rows) if np.isfinite(row[column])
                        ]
                        if viable:
                            best_new = max(
                                viable, key=lambda i: new_rows[i][column]
                            ) if maximize else min(
                                viable, key=lambda i: new_rows[i][column]
                            )
                            if _better(new_rows[best_new][column], current_value, maximize):
                                current = candidates[best_new]
                                current_value = new_rows[best_new][column]
                                improved = True
                    if not improved:
                        break
    return evaluations


def _pareto(metrics: pd.DataFrame, x: str = "volatility", y: str = "cagr") -> tuple[str, ...]:
    valid = metrics[[x, y]].dropna()
    if valid.empty:
        return ()
    # Ordinando l'asse da minimizzare basta conservare il massimo cumulato
    # dell'asse da massimizzare; il doppio ciclo pandas diventerebbe
    # quadratico proprio con i 5.000 campioni predefiniti.
    order = np.argsort(valid[x].to_numpy(dtype=float), kind="stable")
    x_values = valid[x].to_numpy(dtype=float)[order]
    y_values = valid[y].to_numpy(dtype=float)[order]
    keep_positions: list[int] = []
    best_y = -np.inf
    position = 0
    while position < len(order):
        next_position = position + 1
        while next_position < len(order) and np.isclose(
            x_values[next_position], x_values[position], rtol=0.0, atol=1e-12
        ):
            next_position += 1
        group = y_values[position:next_position]
        group_max = float(np.max(group))
        if group_max > best_y + 1e-12:
            keep_positions.extend(
                int(index)
                for index, value in zip(order[position:next_position], group)
                if value >= group_max - 1e-12
            )
            best_y = group_max
        position = next_position
    return tuple(str(valid.index[position]) for position in keep_positions)


def search_frontier(
    prices: pd.DataFrame,
    symbols: list[str],
    initial_value: float,
    rebalance: Rebalance,
    pac: Pac | None,
    risk_free: float,
    lower: dict[str, float] | None = None,
    upper: dict[str, float] | None = None,
    sample_count: int = DEFAULT_SAMPLE_COUNT,
    seed: int = 42,
    current_weights: dict[str, float] | None = None,
    progress: Callable[[float], None] | None = None,
) -> FrontierResult:
    """Cerca allocazioni ammissibili e affina gli otto estremi richiesti."""
    if not symbols or list(prices.columns) != list(symbols):
        raise ValueError("Simboli e colonne dei prezzi non coincidono.")
    if not MIN_SAMPLE_COUNT <= sample_count <= MAX_SAMPLE_COUNT:
        raise ValueError("Il numero di campioni deve essere fra 1.000 e 20.000.")
    lo = np.asarray([float((lower or {}).get(symbol, 0.0)) for symbol in symbols])
    hi = np.asarray([float((upper or {}).get(symbol, 1.0)) for symbol in symbols])
    if (lo < 0).any() or (hi > 1).any() or (lo > hi).any():
        raise ValueError("I limiti dei pesi non sono validi.")
    current = None
    if current_weights is not None:
        current = np.asarray([float(current_weights.get(symbol, 0.0)) for symbol in symbols])
    anchors = []
    if current is not None and (current >= lo - 1e-10).all() and (current <= hi + 1e-10).all():
        anchors.append(current)
    anchors.append(np.asarray([1.0 / len(symbols)] * len(symbols)))
    for position in range(len(symbols)):
        corner = np.zeros(len(symbols))
        corner[position] = 1.0
        anchors.append(corner)
    weights = _sample_weights(sample_count, lo, hi, seed, anchors)
    weights = _unique_weights(weights)
    if progress:
        progress(0.0)
    metric_frame = _batch_metrics(
        prices, weights, initial_value, rebalance, pac, risk_free,
        progress=(lambda value: progress(0.7 * value)) if progress else None,
    )
    weight_rows = [row.copy() for row in weights]
    metric_rows = [row.copy() for row in metric_frame.to_numpy(dtype=float)]
    refined = _refine(
        prices, weight_rows, metric_rows, lo, hi, initial_value, rebalance, pac, risk_free,
        progress=(lambda value: progress(0.7 + 0.3 * value)) if progress else None,
    )
    if refined:
        weights = np.asarray(weight_rows, dtype=float)
        metric_frame = pd.DataFrame(np.asarray(metric_rows), columns=OBJECTIVES)
    metric_frame.index = [f"mix-{i + 1:05d}" for i in range(len(metric_frame))]
    weight_frame = pd.DataFrame(weights, index=metric_frame.index, columns=symbols)
    evaluations = len(metric_frame)
    extrema: dict[str, str] = {}
    for objective in EXTREME_OBJECTIVES:
        valid = metric_frame[objective].dropna()
        if valid.empty:
            continue
        extrema[f"{objective}_max"] = str(valid.idxmax())
        extrema[f"{objective}_min"] = str(valid.idxmin())
    pareto_ids = _pareto(metric_frame)
    if progress:
        progress(1.0)
    return FrontierResult(
        weight_frame, metric_frame, pareto_ids, extrema,
        _fingerprint(
            prices, symbols, initial_value, rebalance, pac, risk_free, lo, hi,
            current,
        ), evaluations,
    )
