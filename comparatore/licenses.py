"""Accesso ai file di licenza generati da `scripts/generate_third_party_notices.py`.

Risolve i percorsi con `Path(__file__)`, come `comparatore.keys`: funziona
sia in sviluppo (i file stanno nella radice del progetto) sia nel bundle
PyInstaller, dove finiscono nella stessa cartella `_internal/` di
`app.py` (vedi `desktop/comparatore.spec`). Degrada in silenzio - un file
mancante non deve impedire l'avvio dell'app.
"""

from __future__ import annotations

import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
NOTICES_PATH = _ROOT / "THIRD_PARTY_NOTICES.txt"
MANIFEST_PATH = _ROOT / "THIRD_PARTY_LICENSES.json"
LICENSE_PATH = _ROOT / "LICENSE"


def testo_notices() -> str | None:
    """Testo completo del file delle licenze di terze parti, o None se assente."""
    try:
        return NOTICES_PATH.read_text(encoding="utf-8")
    except Exception:
        return None


def manifest() -> list[dict[str, str]]:
    """Elenco {name, version, license, url} per la tabella riassuntiva, o [] se assente."""
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    return data if isinstance(data, list) else []
