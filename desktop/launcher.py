"""Entry point per il bundle standalone (PyInstaller).

Avvia il server Streamlit incorporato e apre il browser di sistema, come
farebbe `streamlit run app.py` da terminale. Usato solo dall'eseguibile
pacchettizzato: per lo sviluppo normale si continua a usare `uv run
streamlit run app.py`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _user_data_dir() -> Path:
    """Cartella dati utente per cache e chiavi API.

    Un bundle firmato (macOS) o installato in Program Files (Windows) vive
    in una posizione di sola lettura: cache e chiavi API non possono stare
    accanto al codice come avviene nello sviluppo da sorgente.
    """
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "ComparatoreFondi"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home()))) / "ComparatoreFondi"
    else:
        base = (
            Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
            / "ComparatoreFondi"
        )
    base.mkdir(parents=True, exist_ok=True)
    return base


def _redirect_output_to_log(data_dir: Path) -> None:
    """Manda stdout/stderr su file quando l'app gira senza terminale.

    Con `console=False` (niente finestra nera dietro l'app), un doppio click
    da Finder/Esplora risorse non ha stdout/stderr utilizzabili: un errore
    all'avvio sparirebbe nel nulla, senza modo per l'utente di segnalarlo.
    """
    log_path = data_dir / "comparatore.log"
    log_file = open(log_path, "w", buffering=1, encoding="utf-8")
    sys.stdout = log_file
    sys.stderr = log_file


def main() -> None:
    data_dir = _user_data_dir()
    if getattr(sys, "frozen", False) and (sys.stdout is None or sys.stderr is None):
        _redirect_output_to_log(data_dir)

    # setdefault: chi lancia da sorgente con le env var già impostate non
    # viene sovrascritto.
    os.environ.setdefault("COMPARATORE_CACHE_DIR", str(data_dir / "cache"))
    os.environ.setdefault("COMPARATORE_KEYS_FILE", str(data_dir / "api_keys.json"))
    os.environ.setdefault("COMPARATORE_PREFS_FILE", str(data_dir / "prefs.json"))
    os.environ.setdefault("COMPARATORE_PROFILE_FILE", str(data_dir / "investor_profile.json"))

    # PyInstaller (onedir) estrae i dati accanto all'eseguibile e imposta
    # sys._MEIPASS su quella cartella, dove il .spec colloca app.py alla
    # radice. Fuori da un bundle, app.py sta nella cartella del progetto,
    # una sopra questo script.
    base_path = Path(
        getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)
    )
    app_script = base_path / "app.py"

    # Import ritardato: streamlit e' pesante e non serve finche' non si
    # avvia davvero il server.
    import streamlit.web.cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        str(app_script),
        "--server.headless=false",
        "--server.port=" + os.environ.get("COMPARATORE_STREAMLIT_PORT", "8765"),
        "--server.address=localhost",
        # Niente prompt email al primo avvio: nessun terminale e' collegato
        # per rispondere.
        "--server.showEmailPrompt=false",
        "--browser.gatherUsageStats=false",
        "--client.toolbarMode=viewer",
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
