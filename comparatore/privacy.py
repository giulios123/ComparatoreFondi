"""Costruzione allowlist del rapporto anonimo.

Il payload viene creato da zero. Non si serializza il portafoglio per poi
provare a rimuovere i campi sensibili: cosi' una nuova chiave non puo' passare
per errore nel confine privacy.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from comparatore.diagnostics import DiagnosticReport, Evidence, PortfolioFinding

SCHEMA = "comparatore-fondi/anonymous-report"
VERSION = 1
LINGUE = {"it", "en", "fr", "de"}
_SAFE_SOURCES = {"yahoo", "eodhd", "justetf", "csv", "twelvedata", "manual", "missing"}
_FORBIDDEN_KEYS = {
    "name", "symbol", "ticker", "isin", "amount", "value_absolute", "currency",
    "path", "filename", "file", "credential", "api_key", "token", "secret",
}


@dataclass(frozen=True)
class AnonymousReport:
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return self.payload

    def to_json(self) -> str:
        return json.dumps(self.payload, indent=2, ensure_ascii=False, sort_keys=True)


@dataclass(frozen=True)
class AnonymizationResult:
    report: AnonymousReport
    asset_tokens: dict[str, str]

    @property
    def payload(self) -> dict[str, Any]:
        return self.report.payload

    def to_json(self) -> str:
        return self.report.to_json()

    def to_dict(self) -> dict[str, Any]:
        """Restituisce soltanto il payload; la mappa resta confinata in memoria."""
        return self.report.to_dict()


def _field(item: object, key: str, default: object = None) -> object:
    if isinstance(item, Mapping):
        return item.get(key, default)
    return getattr(item, key, default)


def _asset_id(item: object, index: int) -> str:
    value = _field(item, "asset_id", _field(item, "id", _field(item, "symbol")))
    return str(value or f"asset_{index}")


def _assets_map(assets: object) -> dict[str, str]:
    if isinstance(assets, Mapping):
        items = [dict(value, asset_id=key) if isinstance(value, Mapping) else value
                 for key, value in sorted(assets.items())]
    else:
        items = list(assets or ())
    return {_asset_id(item, index): f"asset_{index}" for index, item in enumerate(items, 1)}


def _safe_source(value: object) -> str:
    value = str(value or "").strip().casefold()
    return value if value in _SAFE_SOURCES else "unknown"


def _safe_number(value: object) -> int | float | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value == value:
        return value
    return None


def _safe_evidence(evidence: Evidence, tokens: Mapping[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {"code": evidence.code}
    if evidence.asset:
        out["asset"] = tokens.get(evidence.asset, "asset_unknown")
    number = _safe_number(evidence.value)
    if number is not None:
        out["value"] = number
    elif evidence.code in {"missing_profile_field", "overlap"} and isinstance(evidence.value, str):
        out["value"] = evidence.value[:40]
    if evidence.unit in {"fraction", "years", "percent"}:
        out["unit"] = evidence.unit
    if evidence.source:
        out["source"] = _safe_source(evidence.source)
    if evidence.period_years is not None:
        out["period_years"] = evidence.period_years
    if evidence.coverage is not None:
        out["coverage"] = evidence.coverage
    return out


def _safe_finding(finding: PortfolioFinding, tokens: Mapping[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "code": finding.code,
        "severity": finding.severity,
        "evidence": [_safe_evidence(item, tokens) for item in finding.evidence],
        "actions": [],
    }
    if finding.asset:
        out["asset"] = tokens.get(finding.asset, "asset_unknown")
    if finding.limit is not None:
        out["limit"] = finding.limit
    for action in finding.actions:
        safe_action: dict[str, Any] = {"code": action.code}
        if action.asset:
            safe_action["asset"] = tokens.get(action.asset, "asset_unknown")
        if action.other_asset:
            safe_action["other_asset"] = tokens.get(action.other_asset, "asset_unknown")
        if action.target_weight is not None:
            safe_action["target_weight"] = action.target_weight
        out["actions"].append(safe_action)
    return out


def _safe_asset(item: object, index: int, token: str) -> dict[str, Any]:
    out: dict[str, Any] = {"asset": token}
    for key in ("weight", "ter", "max_drawdown", "history_years", "coverage"):
        value = _safe_number(_field(item, key))
        if value is not None:
            out[key] = value
    for key in ("asset_class", "class", "sector"):
        value = _field(item, key)
        if isinstance(value, str) and value and len(value) <= 40:
            out[key] = value
    source = _field(item, "source", _field(item, "holdings_source"))
    if source:
        out["source"] = _safe_source(source)
    return out


def anonymize(
    report: DiagnosticReport,
    assets: object = (),
    language: str = "it",
) -> AnonymizationResult:
    """Costruisce payload e mappa locale senza includere identificatori reali."""
    tokens = _assets_map(assets)
    if isinstance(assets, Mapping):
        items = [dict(value, asset_id=key) if isinstance(value, Mapping) else value
                 for key, value in sorted(assets.items())]
    else:
        items = list(assets or ())
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "language": language if language in LINGUE else "it",
        "profile_present": report.profile_present,
        "missing_profile_fields": list(report.missing_profile_fields),
        "assets": [
            _safe_asset(item, index, tokens[_asset_id(item, index)])
            for index, item in enumerate(items, 1)
        ],
        "findings": [_safe_finding(finding, tokens) for finding in report.findings],
    }
    validate_payload(payload)
    return AnonymizationResult(AnonymousReport(payload), tokens)


def _walk(value: object, path: str = ""):
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key), item, path
            yield from _walk(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from _walk(item, f"{path}[{index}]")


def validate_payload(payload: Mapping[str, Any]) -> None:
    """Guardia riusabile dai test e dall'anteprima UI."""
    for key, value, _ in _walk(payload):
        if key.casefold() in _FORBIDDEN_KEYS:
            raise ValueError(f"chiave non ammessa nel payload: {key}")
        if isinstance(value, str):
            lowered = value.casefold()
            if key.casefold() != "schema" and (
                "/" in value or "\\" in value
                or re.search(r"[A-Z]{2}[A-Z0-9]{9}[0-9]", value)
            ):
                raise ValueError("valore identificativo nel payload")
            if any(secret in lowered for secret in ("api_key", "password", "secret")):
                raise ValueError("segreto nel payload")


__all__ = [
    "AnonymousReport", "AnonymizationResult", "anonymize", "validate_payload",
]
