"""Preferenze di interfaccia (lingua) scelte dall'utente, ricordate fra un
avvio e l'altro.

Stesso trattamento di `comparatore.keys`: un file a parte, fuori da
`.cache/`, cosi' "Svuota cache" non le cancella. Degrada in silenzio - un
file assente o corrotto equivale a "nessuna preferenza salvata", non a un
errore che blocca l'avvio dell'app.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

CHIAVI = ("lingua",)


def prefs_file() -> Path:
    """Percorso del file, sovrascrivibile via COMPARATORE_PREFS_FILE."""
    env = os.environ.get("COMPARATORE_PREFS_FILE")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / ".streamlit" / "prefs.json"


def load() -> dict[str, str]:
    """Rilegge le preferenze salvate, o {} se assenti/illeggibili."""
    path = prefs_file()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, str] = {}
    for k in CHIAVI:
        v = str(data.get(k, "") or "").strip()
        if v:
            out[k] = v
    return out


def save(values: dict[str, str]) -> None:
    """Scrive le preferenze su disco."""
    path = prefs_file()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        cleaned = {k: v.strip() for k, v in values.items() if k in CHIAVI and v.strip()}
        path.write_text(json.dumps(cleaned))
    except Exception:
        # Disco pieno o di sola lettura: la preferenza resta valida solo per
        # questa sessione, ma l'app non deve interrompersi per questo.
        pass
