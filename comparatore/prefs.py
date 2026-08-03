"""Preferenze di interfaccia scelte dall'utente, ricordate fra un avvio e
l'altro.

Stesso trattamento di `comparatore.keys`: un file a parte, fuori da
`.cache/`, cosi' "Svuota cache" non le cancella. Degrada in silenzio - un
file assente o corrotto equivale a "nessuna preferenza salvata", non a un
errore che blocca l'avvio dell'app.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

CHIAVI_TESTUALI = ("lingua",)
CHIAVI_BOOLEANE = ("enable_justetf",)


def prefs_file() -> Path:
    """Percorso del file, sovrascrivibile via COMPARATORE_PREFS_FILE."""
    env = os.environ.get("COMPARATORE_PREFS_FILE")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / ".streamlit" / "prefs.json"


def load() -> dict[str, str | bool]:
    """Rilegge le preferenze salvate, o {} se assenti/illeggibili."""
    path = prefs_file()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, str | bool] = {}
    for k in CHIAVI_TESTUALI:
        v = str(data.get(k, "") or "").strip()
        if v:
            out[k] = v
    for k in CHIAVI_BOOLEANE:
        v = data.get(k)
        if isinstance(v, bool):
            out[k] = v
    return out


def save(values: dict[str, str | bool]) -> None:
    """Scrive le preferenze su disco.

    Passa da un file temporaneo nella stessa cartella e `os.replace` (atomico):
    un crash a meta' scrittura lascia intatto il file precedente invece di uno
    troncato che `load()` dovrebbe poi scartare come corrotto. Effetto
    collaterale voluto: `mkstemp` crea il temporaneo a permessi ristretti al
    proprietario, quindi anche `prefs.json` li eredita al posto del default
    - non e' un segreto, ma restringere non fa danno.
    """
    path = prefs_file()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        cleaned: dict[str, str | bool] = {}
        for k in CHIAVI_TESTUALI:
            v = values.get(k, "")
            if isinstance(v, str) and v.strip():
                cleaned[k] = v.strip()
        for k in CHIAVI_BOOLEANE:
            v = values.get(k)
            if isinstance(v, bool):
                cleaned[k] = v
        fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
        os.close(fd)
        tmp = Path(tmp_name)
        tmp.write_text(json.dumps(cleaned), encoding="utf-8")
        os.replace(tmp, path)
    except Exception:
        # Disco pieno o di sola lettura: la preferenza resta valida solo per
        # questa sessione, ma l'app non deve interrompersi per questo.
        pass
