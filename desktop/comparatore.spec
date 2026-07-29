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

from pathlib import Path

from PyInstaller.utils.hooks import collect_all

PROJECT_ROOT = Path(SPECPATH).resolve().parent

block_cipher = None

# Pacchetti con dati non-Python (frontend statico, template, .so vendorizzate,
# file di metadata letti a runtime via importlib.metadata) che l'analisi
# statica non troverebbe da sola.
_COLLECT_ALL = ["streamlit", "plotly", "pyarrow", "curl_cffi", "yfinance"]

datas = [
    (str(PROJECT_ROOT / "app.py"), "."),
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
    icon=None,
    bundle_identifier="com.giuliosciarappa.comparatorefondi",
    info_plist={
        "NSHighResolutionCapable": True,
        "CFBundleShortVersionString": "0.2.0",
    },
)
