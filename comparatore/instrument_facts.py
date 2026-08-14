"""Fatti descrittivi normalizzati di uno strumento finanziario.

I provider restituiscono gli stessi concetti con nomi, unita' e date diverse.
Questo modulo conserva il valore scelto, le alternative discordanti e la
provenienza senza conoscere Streamlit o il formato interno del portafoglio.
"""

from __future__ import annotations

import datetime as dt
import json
import math
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

QUALITY_REPORTED = "reported"
QUALITY_DOCUMENT = "document"
QUALITY_MANUAL = "manual"
QUALITY_DERIVED = "derived"
QUALITIES = {
    QUALITY_REPORTED,
    QUALITY_DOCUMENT,
    QUALITY_MANUAL,
    QUALITY_DERIVED,
}


def _json_safe(value: Any) -> Any:
    """Riduce un valore a tipi JSON senza serializzare payload del provider."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
            if item is not None
        }
    return str(value)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _date_text(value: Any) -> str:
    """Accetta solo date ISO, cosi' la persistenza resta deterministica."""
    if isinstance(value, dt.datetime):
        value = value.date()
    if isinstance(value, dt.date):
        return value.isoformat()
    raw = _text(value)
    if not raw:
        return ""
    try:
        return dt.date.fromisoformat(raw[:10]).isoformat()
    except ValueError:
        return ""


def _timestamp_text(value: Any) -> str:
    if isinstance(value, dt.datetime):
        return value.isoformat(timespec="seconds")
    if isinstance(value, dt.date):
        return value.isoformat()
    raw = _text(value)
    if not raw:
        return ""
    try:
        return dt.datetime.fromisoformat(raw).isoformat(timespec="seconds")
    except ValueError:
        return _date_text(raw)


@dataclass(frozen=True)
class FactValue:
    """Un candidato normalizzato per un singolo fatto."""

    value: Any
    source: str
    observed_at: str = ""
    acquired_at: str = ""
    quality: str = QUALITY_REPORTED

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _json_safe(self.value))
        object.__setattr__(self, "source", _text(self.source).lower())
        object.__setattr__(self, "observed_at", _date_text(self.observed_at))
        object.__setattr__(self, "acquired_at", _timestamp_text(self.acquired_at))
        quality = self.quality if self.quality in QUALITIES else QUALITY_REPORTED
        object.__setattr__(self, "quality", quality)

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": _json_safe(self.value),
            "source": self.source,
            "observed_at": self.observed_at,
            "acquired_at": self.acquired_at,
            "quality": self.quality,
        }

    @classmethod
    def from_dict(cls, value: Any) -> FactValue | None:
        if not isinstance(value, dict) or "value" not in value:
            return None
        source = _text(value.get("source"))
        if not source:
            return None
        return cls(
            value=value.get("value"),
            source=source,
            observed_at=value.get("observed_at", ""),
            acquired_at=value.get("acquired_at", ""),
            quality=value.get("quality", QUALITY_REPORTED),
        )


@dataclass(frozen=True)
class RelatedQuote:
    """Quotazione collegata allo stesso strumento economico."""

    symbol: str
    exchange: str = ""
    currency: str = ""
    source: str = ""
    isin: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", _text(self.symbol))
        object.__setattr__(self, "exchange", _text(self.exchange))
        object.__setattr__(self, "currency", _text(self.currency).upper())
        object.__setattr__(self, "source", _text(self.source).lower())
        object.__setattr__(self, "isin", _text(self.isin).upper())

    def to_dict(self) -> dict[str, str]:
        return {
            "symbol": self.symbol,
            "exchange": self.exchange,
            "currency": self.currency,
            "source": self.source,
            "isin": self.isin,
        }

    @classmethod
    def from_dict(cls, value: Any) -> RelatedQuote | None:
        if not isinstance(value, dict) or not _text(value.get("symbol")):
            return None
        return cls(
            symbol=value.get("symbol", ""),
            exchange=value.get("exchange", ""),
            currency=value.get("currency", ""),
            source=value.get("source", ""),
            isin=value.get("isin", ""),
        )


def _compare_key(value: Any) -> str:
    """Confronta strutture senza dipendere dall'ordine delle chiavi."""
    normalized = value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        normalized = format(float(value), ".15g")
    elif isinstance(value, str):
        normalized = " ".join(value.split()).casefold()
    elif isinstance(value, list):
        normalized = sorted(_compare_key(item) for item in value)
    elif isinstance(value, dict):
        normalized = {
            str(key).casefold(): _compare_key(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, default=str)


def _has_value(value: Any) -> bool:
    """Scarta candidati vuoti prima di scegliere o creare un conflitto."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    if isinstance(value, float):
        return math.isfinite(value)
    return True


def _source_rank(key: str, source: str) -> int:
    """Priorita' dei provider, distinta per il significato del campo."""
    source = source.casefold()
    if source in {"manual", "kid"}:
        return 1000
    if key == "ter":
        return {"justetf": 500, "yahoo": 400, "eodhd": 300}.get(source, 100)
    if key in {"distribution_policy", "replication_method"}:
        return {"justetf": 500, "eodhd": 400, "yahoo": 300}.get(source, 100)
    if key.startswith("allocation."):
        return {"eodhd": 500, "yahoo": 400, "derived": 100}.get(source, 50)
    return {"eodhd": 500, "yahoo": 400, "justetf": 300}.get(source, 100)


@dataclass
class InstrumentFacts:
    """Valori scelti, conflitti e quotazioni collegate di uno strumento."""

    values: dict[str, FactValue] = field(default_factory=dict)
    alternatives: dict[str, list[FactValue]] = field(default_factory=dict)
    related_quotes: list[RelatedQuote] = field(default_factory=list)

    @classmethod
    def merge(
        cls,
        candidates: dict[str, Iterable[FactValue]],
        related_quotes: Iterable[RelatedQuote] = (),
    ) -> InstrumentFacts:
        selected: dict[str, FactValue] = {}
        alternatives: dict[str, list[FactValue]] = {}
        for key, raw_items in candidates.items():
            items = [item for item in raw_items if item.source and _has_value(item.value)]
            if not items:
                continue
            items.sort(
                key=lambda item: (
                    _source_rank(key, item.source),
                    item.acquired_at,
                    item.observed_at,
                ),
                reverse=True,
            )
            winner = items[0]
            selected[key] = winner
            seen: set[str] = set()
            for item in items[1:]:
                marker = _compare_key(item.value)
                if marker == _compare_key(winner.value) or marker in seen:
                    continue
                seen.add(marker)
                alternatives.setdefault(key, []).append(item)

        quotes: list[RelatedQuote] = []
        seen_quotes: set[str] = set()
        for quote in related_quotes:
            if not quote.symbol:
                continue
            marker = f"{quote.symbol.casefold()}|{quote.isin}"
            if marker in seen_quotes:
                continue
            seen_quotes.add(marker)
            quotes.append(quote)
        return cls(selected, alternatives, quotes)

    @classmethod
    def combine(cls, *bundles: InstrumentFacts) -> InstrumentFacts:
        """Fonde bundle gia' normalizzati mantenendo anche le alternative."""
        candidates: dict[str, list[FactValue]] = {}
        quotes: list[RelatedQuote] = []
        for bundle in bundles:
            if bundle is None:
                continue
            for key, value in bundle.values.items():
                candidates.setdefault(key, []).append(value)
            for key, values in bundle.alternatives.items():
                candidates.setdefault(key, []).extend(values)
            quotes.extend(bundle.related_quotes)
        return cls.merge(candidates, quotes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "values": {key: value.to_dict() for key, value in self.values.items()},
            "alternatives": {
                key: [value.to_dict() for value in values]
                for key, values in self.alternatives.items()
            },
            "related_quotes": [quote.to_dict() for quote in self.related_quotes],
        }

    @classmethod
    def from_dict(cls, payload: Any) -> InstrumentFacts:
        if not isinstance(payload, dict):
            return cls()
        values: dict[str, FactValue] = {}
        raw_values = payload.get("values")
        if not isinstance(raw_values, dict):
            raw_values = {}
        for key, raw in raw_values.items():
            fact = FactValue.from_dict(raw)
            if fact is not None and _text(key):
                values[str(key)] = fact
        alternatives: dict[str, list[FactValue]] = {}
        raw_alternatives = payload.get("alternatives")
        if not isinstance(raw_alternatives, dict):
            raw_alternatives = {}
        for key, raw_items in raw_alternatives.items():
            if not isinstance(raw_items, list):
                continue
            facts = [FactValue.from_dict(item) for item in raw_items]
            valid = [fact for fact in facts if fact is not None]
            if valid and _text(key):
                alternatives[str(key)] = valid
        raw_quotes = payload.get("related_quotes", [])
        if not isinstance(raw_quotes, list):
            raw_quotes = []
        quotes = [RelatedQuote.from_dict(item) for item in raw_quotes]
        return cls(values, alternatives, [quote for quote in quotes if quote is not None])


def candidate(
    value: Any,
    source: str,
    *,
    observed_at: Any = "",
    acquired_at: Any = "",
    quality: str = QUALITY_REPORTED,
) -> FactValue:
    """Costruttore breve usato dagli adattatori dei provider."""
    return FactValue(value, source, observed_at, acquired_at, quality)


__all__ = [
    "FactValue",
    "InstrumentFacts",
    "RelatedQuote",
    "QUALITY_DERIVED",
    "QUALITY_DOCUMENT",
    "QUALITY_MANUAL",
    "QUALITY_REPORTED",
    "candidate",
]
