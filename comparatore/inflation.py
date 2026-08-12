"""HICP Eurostat e rendimento reale, senza dipendenze dall'interfaccia."""

from __future__ import annotations

import datetime as dt
import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd
import requests

from . import cache

DATASET = "prc_hicp_minr"
EUROSTAT_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
SUPPORTED_AREAS = {"IT", "EA"}
DEFAULT_TTL_HOURS = 24


@dataclass
class HICPResult:
    series: pd.Series
    area: str
    unit: str = ""
    updated: str = ""
    dataset: str = DATASET
    error: str = ""
    stale: bool = False

    @property
    def ok(self) -> bool:
        return not self.series.empty and not self.error

    @property
    def first_date(self) -> dt.date | None:
        return self.series.index[0].date() if not self.series.empty else None

    @property
    def last_date(self) -> dt.date | None:
        return self.series.index[-1].date() if not self.series.empty else None


def _category_codes(dimension: dict) -> list[str]:
    category = dimension.get("category", {})
    index = category.get("index", {})
    if isinstance(index, list):
        return index
    return [code for code, _ in sorted(index.items(), key=lambda item: item[1])]


def _flat_index(position: list[int], sizes: list[int]) -> int:
    value = 0
    for i, current in enumerate(position):
        stride = math.prod(sizes[i + 1:]) if i + 1 < len(sizes) else 1
        value += current * stride
    return value


def parse_jsonstat(payload: dict, area: str = "") -> HICPResult:
    """Estrae TOTAL dall'ultima unita' indice disponibile nel JSON-stat 2."""
    if not isinstance(payload, dict) or payload.get("class") != "dataset":
        raise ValueError("payload Eurostat non e' un dataset JSON-stat")
    ids = payload.get("id")
    sizes = payload.get("size")
    dimensions = payload.get("dimension")
    if not isinstance(ids, list) or not isinstance(sizes, list) or not isinstance(dimensions, dict):
        raise ValueError("dimensioni JSON-stat mancanti")
    try:
        unit_codes = _category_codes(dimensions["unit"])
        candidates = [code for code in unit_codes if code.startswith("I") and code[1:].isdigit()]
        unit = max(candidates, key=lambda code: int(code[1:]))
        unit_pos = _category_codes(dimensions["unit"]).index(unit)
        coicop_key = "coicop18" if "coicop18" in ids else "coicop"
        coicop_codes = _category_codes(dimensions[coicop_key])
        total = "TOTAL" if "TOTAL" in coicop_codes else "CP00"
        coicop_pos = coicop_codes.index(total)
        geo_codes = _category_codes(dimensions["geo"])
        geo_pos = geo_codes.index(area) if area in geo_codes else 0
        if area and area not in geo_codes:
            raise ValueError(f"area HICP assente nel payload: {area}")
        time_codes = _category_codes(dimensions["time"])
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError("dimensioni HICP non riconosciute") from exc
    positions = []
    for time_pos, code in enumerate(time_codes):
        current = []
        for dimension_id in ids:
            if dimension_id == "unit":
                current.append(unit_pos)
            elif dimension_id == coicop_key:
                current.append(coicop_pos)
            elif dimension_id == "geo":
                current.append(geo_pos)
            elif dimension_id == "time":
                current.append(time_pos)
            else:
                current.append(0)
        flat = str(_flat_index(current, [int(s) for s in sizes]))
        values = payload.get("value", {})
        if isinstance(values, list):
            raw = values[int(flat)] if int(flat) < len(values) else None
        elif isinstance(values, dict):
            raw = values.get(flat, values.get(int(flat)))
        else:
            raw = None
        if raw is not None and np.isfinite(float(raw)):
            positions.append((pd.Period(code, freq="M").to_timestamp("M"), float(raw)))
    if not positions:
        raise ValueError("nessun indice HICP TOTAL nel payload")
    series = pd.Series(dict(positions), dtype=float).sort_index()
    return HICPResult(series=series, area=area, unit=unit, updated=str(payload.get("updated", "")))


def _cache_key(area: str) -> str:
    return f"eurostat/hicp/{area}/v2"


def _cached_result(area: str) -> HICPResult | None:
    entry = cache.read(_cache_key(area))
    meta = cache.read_meta(_cache_key(area)) or {}
    if entry is None:
        return None
    return HICPResult(
        series=entry.series, area=area, unit=str(meta.get("unit", "")),
        updated=str(meta.get("updated", "")), stale=False,
    )


def fetch_hicp(
    area: str,
    start: dt.date,
    end: dt.date,
    *,
    force: bool = False,
    http_get: Callable = requests.get,
    ttl_hours: int = DEFAULT_TTL_HOURS,
) -> HICPResult:
    """Scarica HICP o usa la cache; un errore degrada ai dati vecchi coperti."""
    area = str(area or "").upper()
    if area not in SUPPORTED_AREAS:
        return HICPResult(pd.Series(dtype=float), area, error="area HICP non supportata")
    key = _cache_key(area)
    cached = _cached_result(area)
    fresh = False
    entry = cache.read(key)
    if entry is not None:
        fetched_at = entry.fetched_at.replace(tzinfo=None)
        fresh = (dt.datetime.now() - fetched_at) < dt.timedelta(hours=ttl_hours)
    if (
        cached is not None and fresh and not force
        and entry.req_start <= start and end <= entry.req_end
    ):
        return cached
    request_start = min(start, entry.req_start) if entry else start
    request_end = max(end, entry.req_end) if entry else end
    params = {
        "format": "JSON", "lang": "EN", "freq": "M",
        "coicop18": "TOTAL", "geo": area,
        "sinceTimePeriod": request_start.strftime("%Y-%m"),
        "untilTimePeriod": request_end.strftime("%Y-%m"),
    }
    try:
        response = http_get(f"{EUROSTAT_URL}{DATASET}", params=params, timeout=30)
        response.raise_for_status()
        parsed = parse_jsonstat(response.json(), area)
        old_unit = cached.unit if cached else ""
        if cached is not None and old_unit == parsed.unit:
            series = pd.concat([cached.series, parsed.series])
            series = series[~series.index.duplicated(keep="last")].sort_index()
            req_start, req_end = request_start, request_end
        else:
            series = parsed.series
            # La serie nuova sostituisce quella precedente (cambio base), ma
            # l'intervallo richiesto resta cumulativo: il prossimo refresh
            # dovra' continuare a coprire tutto lo storico gia' usato.
            req_start, req_end = request_start, request_end
        cache.write(key, series, req_start, req_end)
        cache.write_meta(key, {"area": area, "unit": parsed.unit, "updated": parsed.updated})
        parsed.series = series
        return parsed
    except Exception as exc:
        if cached is not None and entry is not None:
            cached.error = str(exc)
            cached.stale = True
            return cached
        return HICPResult(pd.Series(dtype=float), area, error=str(exc))


def factors_for_dates(index: pd.Series | pd.DatetimeIndex, hicp: pd.Series) -> pd.Series:
    """Fattore prezzi mensile per ogni data, senza estendere la copertura."""
    dates = index.index if isinstance(index, pd.Series) else pd.DatetimeIndex(index)
    dates = pd.DatetimeIndex(dates).tz_localize(None).normalize()
    monthly = pd.Series(hicp, copy=True).sort_index().dropna()
    monthly.index = pd.DatetimeIndex(monthly.index).to_period("M").to_timestamp("M")
    monthly = monthly[~monthly.index.duplicated(keep="last")]
    factors = monthly.reindex(dates.to_period("M").to_timestamp("M"))
    factors.index = dates
    return factors


def deflate_curve(curve: pd.Series, hicp: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Restituisce curva reale e fattore relativo alla prima data coperta."""
    curve = pd.Series(curve, copy=True).sort_index().dropna()
    factors = factors_for_dates(curve, hicp)
    mask = factors.notna() & np.isfinite(factors) & (factors > 0)
    if not mask.any():
        return pd.Series(dtype=float), pd.Series(dtype=float)
    factors = factors.loc[mask]
    factors = factors / float(factors.iloc[0])
    real = curve.loc[factors.index] / factors
    return real, factors


def deflate_pac(
    nav: pd.Series,
    invested: pd.Series,
    cashflows: list[tuple[pd.Timestamp, float]],
    hicp: pd.Series,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Deflaziona NAV, saldo e capitale versato rata per rata."""
    real_nav, factors = deflate_curve(nav, hicp)
    if real_nav.empty:
        return real_nav, pd.Series(dtype=float), pd.Series(dtype=float)
    if not cashflows:
        invested = pd.Series(invested).reindex(real_nav.index).ffill()
        return real_nav, invested / factors, factors
    flows = pd.Series(0.0, index=real_nav.index)
    for date, amount in cashflows:
        timestamp = pd.Timestamp(date)
        if timestamp > factors.index[-1]:
            continue
        # Un flusso precedente al primo indice ufficiale entra nella prima
        # data reale disponibile: non si inventa un HICP retroattivo, ma si
        # conserva il capitale iniziale nel cumulato espresso a quella base.
        eligible = factors.index[factors.index >= timestamp]
        if timestamp < factors.index[0]:
            eligible = factors.index[:1]
        if len(eligible) == 0:
            continue
        target = eligible[0]
        flows.loc[target] += abs(float(amount)) / float(factors.loc[target])
    return real_nav, flows.cumsum(), factors


# Nomi brevi mantenuti per i caller esterni e per le fixture.
parse_hicp_jsonstat = parse_jsonstat
deflate = deflate_curve
