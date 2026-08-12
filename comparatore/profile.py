"""Profilo locale e facoltativo dell'investitore.

Il profilo e' una preferenza privata, non una parte del portafoglio esportato.
Il file puo' mancare o essere corrotto senza impedire il backtest: in quel caso
si usa un profilo vuoto e la diagnosi mostra esplicitamente i campi mancanti.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA = "comparatore-fondi/profilo-investitore"
VERSION = 1
OBJECTIVES = ("growth", "income", "preservation")
PREFERENCES = ("simplicity", "balanced", "diversification")


class ProfileError(ValueError):
    """Profilo non valido o di versione non supportata."""


def _optional_fraction(value: object, field_name: str) -> float | None:
    if value in (None, ""):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ProfileError(f"{field_name} non e' numerico") from exc
    if not 0.0 <= result <= 1.0:
        raise ProfileError(f"{field_name} deve essere fra 0 e 1")
    return result


def _optional_bool(value: object, field_name: str) -> bool | None:
    if value is None or value == "":
        return None
    if not isinstance(value, bool):
        raise ProfileError(f"{field_name} deve essere booleano")
    return value


@dataclass(frozen=True)
class InvestorProfile:
    horizon_years: int | None = None
    objective: str | None = None
    max_temporary_loss: float | None = None
    withdrawals: bool | None = None
    max_position_weight: float | None = None
    preference: str | None = None
    bonds_allowed: bool | None = None
    excluded_classes: tuple[str, ...] = field(default_factory=tuple)
    excluded_sectors: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if (
            self.horizon_years is not None
            and (isinstance(self.horizon_years, bool)
                 or not isinstance(self.horizon_years, int)
                 or not 1 <= self.horizon_years <= 100)
        ):
            raise ProfileError("horizon_years deve essere fra 1 e 100")
        if self.objective not in (None, *OBJECTIVES):
            raise ProfileError("objective non riconosciuto")
        if self.preference not in (None, *PREFERENCES):
            raise ProfileError("preference non riconosciuta")
        for name in ("max_temporary_loss", "max_position_weight"):
            _optional_fraction(getattr(self, name), name)
        _optional_bool(self.withdrawals, "withdrawals")
        _optional_bool(self.bonds_allowed, "bonds_allowed")
        object.__setattr__(self, "excluded_classes", _codes(self.excluded_classes))
        object.__setattr__(self, "excluded_sectors", _codes(self.excluded_sectors))

    @property
    def is_empty(self) -> bool:
        return not self.to_dict()

    def to_dict(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for key in (
            "horizon_years", "objective", "max_temporary_loss", "withdrawals",
            "max_position_weight", "preference", "bonds_allowed",
        ):
            value = getattr(self, key)
            if value is not None:
                values[key] = value
        if self.excluded_classes:
            values["excluded_classes"] = list(self.excluded_classes)
        if self.excluded_sectors:
            values["excluded_sectors"] = list(self.excluded_sectors)
        return values

    @classmethod
    def from_dict(cls, value: object) -> InvestorProfile:
        if not isinstance(value, dict):
            raise ProfileError("il profilo non e' un oggetto")
        aliases = {
            "orizzonte_anni": "horizon_years", "obiettivo": "objective",
            "perdita_tollerata": "max_temporary_loss", "prelievi": "withdrawals",
            "limite_posizione": "max_position_weight", "preferenza": "preference",
            "obbligazioni": "bonds_allowed", "classi_escluse": "excluded_classes",
            "settori_esclusi": "excluded_sectors",
        }
        data = {aliases.get(key, key): item for key, item in value.items()}
        horizon = data.get("horizon_years")
        if horizon not in (None, ""):
            try:
                horizon = int(horizon)
            except (TypeError, ValueError) as exc:
                raise ProfileError("horizon_years non e' intero") from exc
        return cls(
            horizon_years=horizon,
            objective=str(data["objective"]).strip() if data.get("objective") else None,
            max_temporary_loss=_optional_fraction(
                data.get("max_temporary_loss"), "max_temporary_loss"
            ),
            withdrawals=_optional_bool(data.get("withdrawals"), "withdrawals"),
            max_position_weight=_optional_fraction(
                data.get("max_position_weight"), "max_position_weight"
            ),
            preference=str(data["preference"]).strip() if data.get("preference") else None,
            bonds_allowed=_optional_bool(data.get("bonds_allowed"), "bonds_allowed"),
            excluded_classes=tuple(data.get("excluded_classes") or ()),
            excluded_sectors=tuple(data.get("excluded_sectors") or ()),
        )


def _codes(values: object) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        values = (values,)
    if not isinstance(values, (list, tuple, set, frozenset)):
        raise ProfileError("le esclusioni devono essere codici")
    return tuple(sorted({str(value).strip() for value in values if str(value).strip()}))


def profile_file() -> Path:
    env = os.environ.get("COMPARATORE_PROFILE_FILE")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / ".streamlit" / "investor_profile.json"


profile_path = profile_file


def load() -> InvestorProfile:
    path = profile_file()
    if not path.exists():
        return InvestorProfile()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
            return InvestorProfile()
        if payload.get("version", VERSION) > VERSION:
            return InvestorProfile()
        return InvestorProfile.from_dict(payload.get("profile", {}))
    except (OSError, json.JSONDecodeError, ProfileError, TypeError, ValueError):
        return InvestorProfile()


def save(profile: InvestorProfile | dict[str, Any]) -> None:
    if not isinstance(profile, InvestorProfile):
        profile = InvestorProfile.from_dict(profile)
    path = profile_file()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"schema": SCHEMA, "version": VERSION, "profile": profile.to_dict()},
                       indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    except OSError:
        # Una preferenza locale non deve impedire il normale backtest.
        pass


def clear() -> None:
    try:
        profile_file().unlink(missing_ok=True)
    except OSError:
        pass


__all__ = [
    "OBJECTIVES", "PREFERENCES", "ProfileError", "InvestorProfile", "clear",
    "load", "profile_file", "save",
    "profile_path",
]
