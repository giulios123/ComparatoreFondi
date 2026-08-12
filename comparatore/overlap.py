"""Sovrapposizione delle partecipazioni, senza dipendenze dall'interfaccia.

Le fonti gratuite restituiscono spesso soltanto una parte delle posizioni di
un fondo. Questo modulo mantiene la parte osservata nella sua scala originale:
un overlap e' quindi sempre un limite inferiore, mai una rinormalizzazione
delle prime posizioni al 100%.
"""

from __future__ import annotations

import datetime as dt
import math
import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

QUOTA_TOLLERANZA = 1e-6
GIORNI_DATATI = 180


def _text(value: object) -> str:
    return str(value or "").strip()


def _date(value: object) -> dt.date | None:
    if value in (None, ""):
        return None
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(_text(value)[:10])
    except (TypeError, ValueError):
        return None


def _normalizza(value: object) -> str:
    """Normalizza testo libero senza cancellare il suffisso di borsa."""
    value = unicodedata.normalize("NFKC", _text(value)).casefold()
    return re.sub(r"\s+", " ", value).strip()


def _symbol(value: object) -> str:
    return _normalizza(value)


def _name(value: object) -> str:
    value = _normalizza(value)
    return re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE)


@dataclass(frozen=True)
class HoldingPosition:
    """Una partecipazione osservata dentro un fondo."""

    quota: float
    stable_id: str = ""
    stable_id_type: str = ""
    symbol: str = ""
    name: str = ""

    @classmethod
    def from_value(cls, value: object) -> HoldingPosition:
        if isinstance(value, cls):
            return value
        if not isinstance(value, Mapping):
            return cls(quota=float("nan"))
        raw_quota = value.get("quota", value.get("weight", value.get("holding_percent")))
        try:
            quota = float(raw_quota)
        except (TypeError, ValueError):
            quota = float("nan")
        return cls(
            quota=quota,
            stable_id=_text(value.get("stable_id", value.get("identifier", value.get("id")))),
            stable_id_type=_text(
                value.get("stable_id_type", value.get("identifier_type", value.get("id_type")))
            ),
            symbol=_text(value.get("symbol", value.get("ticker"))),
            name=_text(value.get("name", value.get("holding_name", value.get("title")))),
        )


@dataclass(frozen=True)
class FundHoldings:
    """Holdings normalizzate e peso del fondo nel portafoglio."""

    fund_id: str
    holdings: tuple[HoldingPosition, ...] = ()
    weight: float = 1.0
    name: str = ""
    source: str = ""
    as_of: dt.date | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "holdings",
            tuple(HoldingPosition.from_value(h) for h in (self.holdings or ())),
        )
        object.__setattr__(self, "as_of", _date(self.as_of))

    @classmethod
    def from_value(cls, value: object, fund_id: str | None = None) -> FundHoldings:
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            identifier = _text(value.get("fund_id", value.get("id", fund_id))) or "fund"
            raw_weight = value.get("weight", value.get("peso", 1.0))
            try:
                weight = float(raw_weight)
            except (TypeError, ValueError):
                weight = 0.0
            if weight > 1.0:
                weight /= 100.0
            return cls(
                fund_id=identifier,
                holdings=tuple(value.get("holdings") or ()),
                weight=weight,
                name=_text(value.get("name", value.get("fondo", ""))),
                source=_text(value.get("holdings_source", value.get("source", ""))),
                as_of=_date(value.get("holdings_as_of", value.get("as_of"))),
            )
        return cls(fund_id=_text(fund_id) or "fund")


@dataclass(frozen=True)
class FundCoverage:
    fund_id: str
    known_weight: float
    coverage: float
    valid: bool
    source: str = ""
    as_of: dt.date | None = None
    stale: bool = False
    reason: str = ""
    ambiguous_count: int = 0
    invalid_count: int = 0

    @property
    def unknown_weight(self) -> float:
        return max(0.0, 1.0 - self.coverage)


@dataclass(frozen=True)
class PairOverlap:
    fund_a: str
    fund_b: str
    overlap: float | None
    coverage_a: float
    coverage_b: float
    lower_bound: bool = True
    ambiguous_count: int = 0
    reason: str = ""

    @property
    def is_available(self) -> bool:
        return self.overlap is not None

    @property
    def display_value(self) -> float | None:
        return self.overlap


@dataclass(frozen=True)
class PortfolioExposure:
    exposures: dict[str, float] = field(default_factory=dict)
    known_weight: float = 0.0
    unknown_weight: float = 1.0


@dataclass(frozen=True)
class OverlapReport:
    funds: tuple[FundHoldings, ...]
    coverage: dict[str, FundCoverage]
    pairwise: tuple[PairOverlap, ...]
    exposure: PortfolioExposure

    @property
    def matrix(self) -> dict[tuple[str, str], float | None]:
        out: dict[tuple[str, str], float | None] = {}
        for pair in self.pairwise:
            out[(pair.fund_a, pair.fund_b)] = pair.overlap
            out[(pair.fund_b, pair.fund_a)] = pair.overlap
        return out

    def pair(self, fund_a: str, fund_b: str) -> PairOverlap | None:
        wanted = {fund_a, fund_b}
        return next(
            (p for p in self.pairwise if {p.fund_a, p.fund_b} == wanted), None
        )

    def anonymous_summary(self) -> dict[str, Any]:
        """Forma minima priva di nomi, pronta per il rapporto della spec 008."""
        ids = {fund.fund_id: f"asset_{index}" for index, fund in enumerate(self.funds, 1)}
        return {
            "coverage": [
                {
                    "asset": ids[fund_id],
                    "coverage": round(value.coverage, 8),
                    "known": round(value.known_weight, 8),
                    "stale": value.stale,
                    "source": value.source or "missing",
                    "ambiguous": value.ambiguous_count,
                }
                for fund_id, value in sorted(self.coverage.items())
            ],
            "overlap": [
                {
                    "asset_a": ids[pair.fund_a],
                    "asset_b": ids[pair.fund_b],
                    "overlap": None if pair.overlap is None else round(pair.overlap, 8),
                    "coverage_a": round(pair.coverage_a, 8),
                    "coverage_b": round(pair.coverage_b, 8),
                    "lower_bound": pair.lower_bound,
                    "ambiguous": pair.ambiguous_count,
                }
                for pair in self.pairwise
            ],
            "exposure": {
                "positions": {
                    key: round(value, 8)
                    for key, value in sorted(self.exposure.exposures.items())
                },
                "known": round(self.exposure.known_weight, 8),
                "unknown": round(self.exposure.unknown_weight, 8),
            },
        }


def _stable_key(position: HoldingPosition) -> tuple[str, str, str] | None:
    if position.stable_id:
        return (
            "stable",
            _normalizza(position.stable_id_type) or "unknown",
            _normalizza(position.stable_id),
        )
    if position.symbol:
        return ("symbol", "", _symbol(position.symbol))
    return None


def _valid_quota(value: float) -> bool:
    return math.isfinite(value) and 0.0 < value <= 1.0


def _prepare_fund(
    fund: FundHoldings,
) -> tuple[FundCoverage, list[tuple[HoldingPosition, str, bool]]]:
    valid_rows: list[tuple[HoldingPosition, str, bool]] = []
    invalid_count = 0
    for index, position in enumerate(fund.holdings):
        if not _valid_quota(position.quota):
            invalid_count += 1
            continue
        key = _stable_key(position)
        # Un'identita' anonima resta separata dal resto: non e' un match, ma
        # la sua quota continua a essere parte dei dati osservati.
        if key is None:
            key = ("anonymous", fund.fund_id, str(index))
        valid_rows.append((position, "|".join(key), key[0] == "anonymous"))

    totals: dict[str, float] = {}
    for position, key, _ in valid_rows:
        totals[key] = totals.get(key, 0.0) + position.quota
    total = sum(totals.values())
    if total > 1.0 + QUOTA_TOLLERANZA:
        coverage = FundCoverage(
            fund_id=fund.fund_id, known_weight=0.0, coverage=0.0, valid=False,
            source=fund.source, as_of=fund.as_of,
            stale=_is_stale(fund.as_of), reason="coverage_over_100", invalid_count=invalid_count,
        )
        return coverage, []

    # Duplicati uguali vengono sommati. La chiave anonima e' volutamente
    # unica per riga, mentre stable/symbol/name vengono consolidati piu' avanti.
    consolidated = [
        (HoldingPosition(quota=quota), key, key.startswith("anonymous|"))
        for key, quota in totals.items()
    ]
    known = min(max(total, 0.0), 1.0)
    coverage = FundCoverage(
        fund_id=fund.fund_id, known_weight=known, coverage=known, valid=bool(consolidated),
        source=fund.source, as_of=fund.as_of, stale=_is_stale(fund.as_of),
        reason="" if consolidated else ("invalid_holdings" if invalid_count else "no_holdings"),
        invalid_count=invalid_count,
    )
    return coverage, consolidated


def _is_stale(value: dt.date | None, today: dt.date | None = None) -> bool:
    return bool(value and (today or dt.date.today()) - value > dt.timedelta(days=GIORNI_DATATI))


def _name_ambiguities(funds: Iterable[FundHoldings]) -> set[str]:
    strong: dict[str, set[tuple[str, str, str]]] = {}
    for fund in funds:
        for position in fund.holdings:
            if not _valid_quota(position.quota) or not position.name:
                continue
            key = _stable_key(position)
            if key is not None:
                strong.setdefault(_name(position.name), set()).add(key)
    return {name for name, keys in strong.items() if len(keys) > 1}


def _match_key(position: HoldingPosition, ambiguous_names: set[str]) -> tuple[str, str, str] | None:
    key = _stable_key(position)
    if key is not None:
        return key
    name = _name(position.name)
    if name and name not in ambiguous_names:
        return ("name", "", name)
    return None


def _normalizza_fondi(funds: object) -> list[FundHoldings]:
    if isinstance(funds, Mapping):
        return [FundHoldings.from_value(value, str(key)) for key, value in funds.items()]
    if isinstance(funds, Iterable) and not isinstance(funds, (str, bytes)):
        out: list[FundHoldings] = []
        for index, value in enumerate(funds, 1):
            out.append(FundHoldings.from_value(value, f"fund_{index}"))
        return out
    return []


def analyze_overlap(funds: object) -> OverlapReport:
    """Calcola copertura, overlap pairwise ed esposizione aggregata."""
    normalized = _normalizza_fondi(funds)
    ambiguous_names = _name_ambiguities(normalized)
    prepared: dict[str, tuple[FundCoverage, dict[tuple[str, str, str], float], int]] = {}

    for fund in normalized:
        coverage, rows = _prepare_fund(fund)
        by_key: dict[tuple[str, str, str], float] = {}
        ambiguous = 0
        # Si ricostruisce dalle holdings originali per conservare nome e
        # distinguere un fallback ambiguo da una riga senza identita'.
        for position in fund.holdings:
            if not _valid_quota(position.quota):
                continue
            if position.name and _name(position.name) in ambiguous_names:
                ambiguous += 1
            key = _match_key(position, ambiguous_names)
            if key is None:
                continue
            by_key[key] = by_key.get(key, 0.0) + position.quota
        if not coverage.valid:
            by_key = {}
        coverage = FundCoverage(
            **{**coverage.__dict__, "ambiguous_count": ambiguous}
        )
        prepared[fund.fund_id] = (coverage, by_key, ambiguous)

    pairwise: list[PairOverlap] = []
    for index, first in enumerate(normalized):
        for second in normalized[index + 1:]:
            cov_a, holdings_a, amb_a = prepared[first.fund_id]
            cov_b, holdings_b, amb_b = prepared[second.fund_id]
            if not cov_a.valid or not cov_b.valid:
                pairwise.append(PairOverlap(
                    first.fund_id, second.fund_id, None, cov_a.coverage, cov_b.coverage,
                    ambiguous_count=amb_a + amb_b, reason="insufficient_holdings",
                ))
                continue
            common = set(holdings_a) & set(holdings_b)
            overlap = sum(min(holdings_a[key], holdings_b[key]) for key in common)
            pairwise.append(PairOverlap(
                first.fund_id, second.fund_id, min(max(overlap, 0.0), 1.0),
                cov_a.coverage, cov_b.coverage, ambiguous_count=amb_a + amb_b,
                reason="ambiguous_identifiers" if amb_a or amb_b else "",
            ))

    weights: dict[str, float] = {}
    for fund in normalized:
        weight = fund.weight if math.isfinite(fund.weight) and fund.weight > 0 else 0.0
        weights[fund.fund_id] = weight
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {key: value / total_weight for key, value in weights.items()}

    exposure: dict[str, float] = {}
    known_weight = 0.0
    for fund in normalized:
        coverage, by_key, _ = prepared[fund.fund_id]
        fund_weight = weights.get(fund.fund_id, 0.0)
        known_weight += fund_weight * coverage.coverage
        for key, value in by_key.items():
            exposure["|".join(key)] = exposure.get("|".join(key), 0.0) + fund_weight * value
    known_weight = min(max(known_weight, 0.0), 1.0)
    report = OverlapReport(
        funds=tuple(normalized),
        coverage={fund_id: prepared[fund_id][0] for fund_id in sorted(prepared)},
        pairwise=tuple(pairwise),
        exposure=PortfolioExposure(exposure, known_weight, max(0.0, 1.0 - known_weight)),
    )
    return report


__all__ = [
    "GIORNI_DATATI", "QUOTA_TOLLERANZA", "FundCoverage", "FundHoldings",
    "HoldingPosition", "OverlapReport", "PairOverlap", "PortfolioExposure",
    "analyze_overlap",
]
