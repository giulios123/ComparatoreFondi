# -*- mode: python ; coding: utf-8 -*-
"""Build PyInstaller (onedir) per Comparatore Fondi.

Uso:
    uv run pyinstaller desktop/comparatore.spec --noconfirm --clean

Produce dist/ComparatoreFondi/ (Windows) o dist/ComparatoreFondi.app (macOS,
oltre alla cartella onedir da cui e' costruito). Un solo file di spec serve
entrambe le piattaforme: BUNDLE() sotto e' un no-op fuori da macOS.

Multi-script analysis
----------------------
Streamlit non importa app.py: lo legge come testo e lo esegue a runtime
(vedi streamlit.web.bootstrap). L'analisi statica di PyInstaller, che decide
cosa impacchettare seguendo gli `import` a partire dal solo launcher.py, non
vedrebbe quindi ne' app.py ne' il pacchetto `comparatore` che importa.
Elencare app.py come secondo script in Analysis() risolve il problema: viene
analizzato per gli import (cosi' pandas/plotly/comparatore/* vengono
raccolti) ma resta il launcher, non app.py, l'eseguibile che parte.
"""

import ast
from pathlib import Path
import subprocess
import sys

from PyInstaller.utils.hooks import collect_all, copy_metadata

PROJECT_ROOT = Path(SPECPATH).resolve().parent


def _versione_app() -> str:
    """Legge `__version__` da comparatore/__init__.py senza importarlo: in
    fase di build servirebbe l'intero pacchetto (pandas, streamlit, ...) solo
    per una stringa. E' la stessa fonte che usa app.py a runtime -
    tests/test_versione.py verifica che resti allineata a pyproject.toml."""
    sorgente = (PROJECT_ROOT / "comparatore" / "__init__.py").read_text(encoding="utf-8")
    albero = ast.parse(sorgente, filename="comparatore/__init__.py")
    for nodo in ast.walk(albero):
        if (
            isinstance(nodo, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "__version__" for t in nodo.targets)
            and isinstance(nodo.value, ast.Constant)
        ):
            return str(nodo.value.value)
    raise RuntimeError("__version__ non trovata in comparatore/__init__.py")


VERSIONE = _versione_app()

# Generate via `uv run python scripts/generate_icons.py` (solo macOS: usa il
# font di sistema Apple Color Emoji + iconutil). I file sono committati in
# assets/ perche' il runner Windows della CI non puo' rigenerarli.
ICON_ICNS = str(PROJECT_ROOT / "assets" / "icon.icns")  # macOS, per BUNDLE()
ICON_ICO = str(PROJECT_ROOT / "assets" / "icon.ico")  # Windows, per EXE()

# Il notice riflette le distribuzioni effettivamente installate sulla
# piattaforma di build (incluse le dipendenze native o condizionali).
subprocess.run(
    [sys.executable, str(PROJECT_ROOT / "scripts" / "generate_third_party_notices.py")],
    check=True,
)

block_cipher = None

# Pacchetti con dati non-Python (frontend statico, template, .so vendorizzate,
# file di metadata letti a runtime via importlib.metadata) che l'analisi
# statica non troverebbe da sola.
_COLLECT_ALL = ["streamlit", "plotly", "pyarrow", "curl_cffi", "yfinance"]

# collect_all() non porta con se' la cartella *.dist-info: questi pacchetti
# leggono pero' la propria versione con importlib.metadata.version(...) a
# livello di modulo (streamlit/version.py, plotly/__init__.py,
# altair/__init__.py - quest'ultimo importato da streamlit per i grafici
# nativi), fuori da un try/except. Senza il dist-info l'eseguibile va in
# crash al primo avvio con PackageNotFoundError, visto solo su Windows perche'
# nessuno aveva ancora provato il bundle li'.
_COPY_METADATA = ["streamlit", "plotly", "altair"]

datas = [
    (str(PROJECT_ROOT / "app.py"), "."),
    (str(PROJECT_ROOT / "LICENSE"), "."),
    (str(PROJECT_ROOT / "THIRD_PARTY_NOTICES.txt"), "."),
    (str(PROJECT_ROOT / "THIRD_PARTY_LICENSES.json"), "."),
    (str(PROJECT_ROOT / ".streamlit" / "config.toml"), ".streamlit"),
]
binaries = []
hiddenimports = []

for pkg in _COLLECT_ALL:
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    # I sotto-pacchetti di test (es. pyarrow.tests) tirano dentro hypothesis
    # e pytest per niente: non servono a un'app confezionata.
    hiddenimports += [
        m for m in pkg_hiddenimports if ".tests" not in m and ".testing" not in m
    ]

for pkg in _COPY_METADATA:
    datas += copy_metadata(pkg)

a = Analysis(
    [str(PROJECT_ROOT / "desktop" / "launcher.py"), str(PROJECT_ROOT / "app.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ComparatoreFondi",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_ICO,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ComparatoreFondi",
)

# No-op su Windows/Linux: BUNDLE() produce un .app solo quando il build gira
# su macOS.
app = BUNDLE(
    coll,
    name="ComparatoreFondi.app",
    icon=ICON_ICNS,
    bundle_identifier="com.giuliosciarappa.comparatorefondi",
    info_plist={
        "NSHighResolutionCapable": True,
        "CFBundleShortVersionString": VERSIONE,
    },
)
