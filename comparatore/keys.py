"""Chiavi API inserite dall'interfaccia, ricordate fra un avvio e l'altro.

Perche' un file a parte e non dentro `.cache/`
-----------------------------------------------
`cache.clear()` cancella l'intera directory della cache con `shutil.rmtree`:
se le chiavi vivessero li' dentro, "Svuota cache" le butterebbe via insieme
alle serie storiche. Stanno invece accanto a `secrets.toml`, con lo stesso
trattamento riservato: mai nel repository, permessi ristretti al solo utente.

Ogni funzione qui dentro degrada in silenzio (nessuna eccezione visibile):
un file assente o corrotto equivale a "nessuna chiave salvata", non a un
errore che blocca l'avvio dell'app.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

KEYS = ("EODHD_API_KEY", "TWELVEDATA_API_KEY")


def keys_file() -> Path:
    """Percorso del file, sovrascrivibile via COMPARATORE_KEYS_FILE."""
    env = os.environ.get("COMPARATORE_KEYS_FILE")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / ".streamlit" / "api_keys.json"


def load() -> dict[str, str]:
    """Rilegge le chiavi salvate, o {} se assenti/illeggibili."""
    path = keys_file()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}
    return {k: str(data.get(k, "") or "").strip() for k in KEYS if data.get(k)}


def save(values: dict[str, str]) -> None:
    """Scrive le chiavi su disco con permessi ristretti al proprietario."""
    path = keys_file()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        cleaned = {k: v.strip() for k, v in values.items() if k in KEYS and v.strip()}
        path.write_text(json.dumps(cleaned))
        os.chmod(path, 0o600)
    except Exception:
        # Disco pieno o di sola lettura: la chiave resta valida solo per
        # questa sessione, ma l'app non deve interrompersi per questo.
        pass


def clear() -> None:
    """Rimuove il file delle chiavi salvate."""
    try:
        keys_file().unlink(missing_ok=True)
    except Exception:
        pass
