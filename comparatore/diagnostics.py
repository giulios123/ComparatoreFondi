"""Diagnosi deterministica del portafoglio.

Le regole qui dentro ordinano fatti gia' calcolati dall'app e segnalano solo
conflitti con preferenze dichiarate. Non esistono soglie universali e nessuna
azione e' eseguibile: le azioni sono descrizioni di scenari da verificare a
parte.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from comparatore.profile import InvestorProfile


@dataclass(frozen=True)
class Evidence:
    code: str
    value: float | int | str | bool | None = None
    unit: str = ""
    asset: str = ""
    source: str = ""
    period_years: float | None = None
    coverage: float | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"code": self.code}
        for key in ("value", "unit", "asset", "source", "period_years", "coverage"):
            value = getattr(self, key)
            if value not in (None, ""):
                out[key] = value
        return out


@dataclass(frozen=True)
class SimulationAction:
    code: str
    asset: str = ""
    other_asset: str = ""
    target_weight: float | None = None

    def as_dict(self) -> dict[str, Any]:
        out = {"code": self.code}
        if self.asset:
            out["asset"] = self.asset
        if self.other_asset:
            out["other_asset"] = self.other_asset
        if self.target_weight is not None:
            out["target_weight"] = self.target_weight
        return out


@dataclass(frozen=True)
class PortfolioFinding:
    code: str
    severity: str
    evidence: tuple[Evidence, ...] = ()
    limit: float | None = None
    asset: str = ""
    actions: tuple[SimulationAction, ...] = ()
    message_key: str = ""

    def __post_init__(self) -> None:
        if self.severity not in {"info", "warning"}:
            raise ValueError("severity deve essere info o warning")
        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "actions", tuple(self.actions))

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "evidence": [item.as_dict() for item in self.evidence],
            "actions": [item.as_dict() for item in self.actions],
        }
        for key, value in (
            ("limit", self.limit), ("asset", self.asset), ("message_key", self.message_key)
        ):
            if value not in (None, ""):
                out[key] = value
        return out


@dataclass(frozen=True)
class DiagnosticReport:
    findings: tuple[PortfolioFinding, ...] = ()
    missing_profile_fields: tuple[str, ...] = ()
    profile_present: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "findings",
            tuple(sorted(self.findings, key=_finding_sort_key)),
        )
        object.__setattr__(
            self, "missing_profile_fields", tuple(sorted(self.missing_profile_fields))
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "profile_present": self.profile_present,
            "missing_profile_fields": list(self.missing_profile_fields),
            "findings": [finding.as_dict() for finding in self.findings],
        }


def _value(item: object, key: str, default: object = None) -> object:
    if isinstance(item, Mapping):
        return item.get(key, default)
    return getattr(item, key, default)


def _float(value: object) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _has_data(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, bytes, Mapping, list, tuple, set, frozenset)):
        return bool(value)
    empty = getattr(value, "empty", None)
    if isinstance(empty, bool):
        return not empty
    return True


def _assets(context: object) -> list[object]:
    raw = _value(context, "assets", ())
    if isinstance(raw, Mapping):
        return [dict(value, asset_id=key) if isinstance(value, Mapping) else value
                for key, value in sorted(raw.items())]
    return list(raw or ())


def _asset_id(asset: object, index: int) -> str:
    value = _value(asset, "asset_id", _value(asset, "id", _value(asset, "symbol")))
    return str(value or f"asset_{index}")


def _finding_sort_key(finding: PortfolioFinding) -> tuple[int, str, str, str]:
    return (
        0 if finding.severity == "warning" else 1,
        finding.code,
        finding.asset,
        repr(finding.evidence),
    )


def _missing_profile(profile: InvestorProfile) -> tuple[str, ...]:
    keys = (
        "horizon_years", "objective", "max_temporary_loss", "withdrawals",
        "max_position_weight", "preference", "bonds_allowed",
        "excluded_classes", "excluded_sectors",
    )
    return tuple(key for key in keys if getattr(profile, key) in (None, ()))


def _asset_facts(asset: object, asset_id: str) -> list[PortfolioFinding]:
    findings: list[PortfolioFinding] = []
    weight = _float(_value(asset, "weight"))
    if weight is not None:
        if weight > 1:
            weight /= 100.0
        findings.append(PortfolioFinding(
            "weight_observation", "info",
            (Evidence("portfolio_weight", weight, "fraction", asset_id),),
            asset=asset_id, message_key="diagnostic.weight_observation",
        ))
    if _value(asset, "ter") in (None, ""):
        findings.append(PortfolioFinding(
            "ter_missing", "info", (Evidence("ter", None, asset=asset_id),),
            asset=asset_id, actions=(SimulationAction("check_missing_data", asset_id),),
            message_key="diagnostic.ter_missing",
        ))
    else:
        ter = _float(_value(asset, "ter"))
        if ter is not None:
            findings.append(PortfolioFinding(
                "ter_observation", "info",
                (Evidence(
                    "ter", ter, "fraction", asset_id,
                    str(_value(asset, "ter_source", _value(asset, "source", "")) or ""),
                ),),
                asset=asset_id, message_key="diagnostic.ter_observation",
            ))
    max_drawdown = _float(_value(asset, "max_drawdown"))
    if max_drawdown is not None:
        findings.append(PortfolioFinding(
            "drawdown_observation", "info",
            (Evidence("max_drawdown", max_drawdown, "fraction", asset_id),),
            asset=asset_id, message_key="diagnostic.drawdown_observation",
        ))
    holdings = _value(asset, "holdings")
    if holdings is not None and not holdings:
        findings.append(PortfolioFinding(
            "holdings_missing", "info", (Evidence("holdings", None, asset=asset_id),),
            asset=asset_id, actions=(SimulationAction("check_missing_data", asset_id),),
            message_key="diagnostic.holdings_missing",
        ))
    return findings


def _personal_findings(
    asset: object, asset_id: str, profile: InvestorProfile
) -> list[PortfolioFinding]:
    findings: list[PortfolioFinding] = []
    weight = _float(_value(asset, "weight"))
    if weight is not None and weight > 1:
        weight /= 100.0
    if (
        weight is not None
        and profile.max_position_weight is not None
        and weight > profile.max_position_weight
    ):
        findings.append(PortfolioFinding(
            "position_limit_exceeded", "warning",
            (Evidence("portfolio_weight", weight, "fraction", asset_id),),
            limit=profile.max_position_weight, asset=asset_id,
            actions=(SimulationAction(
                "simulate_weight_limit", asset_id,
                target_weight=profile.max_position_weight,
            ),),
            message_key="diagnostic.position_limit_exceeded",
        ))
    drawdown = _float(_value(asset, "max_drawdown"))
    if (
        drawdown is not None
        and profile.max_temporary_loss is not None
        and abs(drawdown) > profile.max_temporary_loss
    ):
        findings.append(PortfolioFinding(
            "drawdown_exceeds_tolerance", "warning",
            (Evidence("max_drawdown", drawdown, "fraction", asset_id),),
            limit=profile.max_temporary_loss, asset=asset_id,
            actions=(SimulationAction("simulate_period", asset_id),),
            message_key="diagnostic.drawdown_exceeds_tolerance",
        ))
    history = _float(_value(asset, "history_years"))
    if (
        history is not None
        and profile.horizon_years is not None
        and history < profile.horizon_years
    ):
        findings.append(PortfolioFinding(
            "history_shorter_than_horizon", "warning",
            (Evidence("history_years", history, "years", asset_id),),
            limit=float(profile.horizon_years), asset=asset_id,
            actions=(SimulationAction("simulate_period", asset_id),),
            message_key="diagnostic.history_shorter_than_horizon",
        ))
    asset_class = str(_value(asset, "asset_class", _value(asset, "class", "")) or "")
    sector = str(_value(asset, "sector", "") or "")
    if asset_class in profile.excluded_classes or sector in profile.excluded_sectors:
        findings.append(PortfolioFinding(
            "excluded_exposure", "warning",
            (Evidence("asset_class", asset_class or sector, asset=asset_id),),
            asset=asset_id, message_key="diagnostic.excluded_exposure",
        ))
    if profile.bonds_allowed is False and asset_class in {"Obbligazionario", "bond", "bonds"}:
        findings.append(PortfolioFinding(
            "bonds_not_allowed", "warning",
            (Evidence("asset_class", asset_class, asset=asset_id),),
            asset=asset_id, message_key="diagnostic.bonds_not_allowed",
        ))
    return findings


def _context_facts(context: object) -> list[PortfolioFinding]:
    findings: list[PortfolioFinding] = []
    for key, code, message in (
        ("rolling", "rolling_observation", "diagnostic.rolling_observation"),
        ("benchmark", "benchmark_observation", "diagnostic.benchmark_observation"),
        ("inflation", "inflation_observation", "diagnostic.inflation_observation"),
    ):
        value = _value(context, key)
        if _has_data(value):
            findings.append(PortfolioFinding(
                code, "info", (Evidence(code, str(value)[:160]),), message_key=message,
            ))
    correlations = _value(context, "correlations")
    if isinstance(correlations, Mapping):
        numeric = []
        for pair, value in correlations.items():
            number = _float(value)
            if number is not None:
                numeric.append((abs(number), str(pair), number))
        for _, pair, number in sorted(numeric, reverse=True)[:3]:
            findings.append(PortfolioFinding(
                "correlation_observation", "info",
                (Evidence("correlation", number, "fraction", pair),),
                message_key="diagnostic.correlation_observation",
            ))
    elif _has_data(correlations):
        findings.append(PortfolioFinding(
            "correlation_observation", "info",
            (Evidence("correlations", "available"),),
            message_key="diagnostic.correlation_observation",
        ))
    overlap = _value(context, "overlap")
    if _has_data(overlap):
        findings.append(PortfolioFinding(
            "overlap_observation", "info", (Evidence("overlap", "available"),),
            message_key="diagnostic.overlap_observation",
        ))
    return findings


def diagnose(context: object, profile: InvestorProfile | None = None) -> DiagnosticReport:
    """Produce sempre lo stesso rapporto a parita' di input."""
    if profile is None:
        profile = InvestorProfile()
    elif not isinstance(profile, InvestorProfile):
        profile = InvestorProfile.from_dict(profile)
    assets = _assets(context)
    findings: list[PortfolioFinding] = []
    for index, asset in enumerate(assets, 1):
        asset_id = _asset_id(asset, index)
        findings.extend(_asset_facts(asset, asset_id))
        if not profile.is_empty:
            findings.extend(_personal_findings(asset, asset_id, profile))
    findings.extend(_context_facts(context))
    missing = _missing_profile(profile)
    if profile.is_empty:
        findings.insert(0, PortfolioFinding(
            "profile_missing", "info",
            tuple(Evidence("missing_profile_field", field) for field in missing),
            message_key="diagnostic.profile_missing",
        ))
    return DiagnosticReport(tuple(findings), missing, not profile.is_empty)


__all__ = [
    "DiagnosticReport", "Evidence", "PortfolioFinding", "SimulationAction", "diagnose",
]
