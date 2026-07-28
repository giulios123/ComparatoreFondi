"""Risoluzione ISIN -> ticker tramite OpenFIGI.

A cosa serve
------------
Le fonti parlano linguaggi diversi: justETF ragiona per ISIN, Yahoo per ticker
con suffisso di borsa. `yfinance.Ticker(...).isin` restituisce `"-"` su tutti i
simboli provati, quindi non c'e' modo di risalire all'ISIN partendo da Yahoo.

OpenFIGI copre la direzione utile - da ISIN ai ticker delle varie borse - senza
chiave API. Serve quando l'utente cerca per ISIN: si ottiene l'ISIN per
justETF e, con questa mappatura, anche un simbolo Yahoo su cui ripiegare.

L'endpoint anonimo e' limitato a poche richieste al minuto: i risultati vanno
in cache su disco e non scadono, perche' la corrispondenza fra ISIN e ticker
non cambia.
"""

from __future__ import annotations

import requests

from .. import cache
from .base import is_isin

URL = "https://api.openfigi.com/v3/mapping"
TIMEOUT = 20

# Codici di borsa OpenFIGI -> suffisso Yahoo. Coperte le piazze dove sono
# quotati gli ETF UCITS che interessano qui.
EXCHANGE_SUFFIX = {
    "LN": ".L",  # Londra
    "GR": ".DE",  # Xetra
    "GY": ".DE",  # Germania
    "GF": ".F",  # Francoforte
    "NA": ".AS",  # Amsterdam
    "IM": ".MI",  # Milano
    "FP": ".PA",  # Parigi
    "SW": ".SW",  # SIX Svizzera
    "VX": ".SW",
    "SM": ".MC",  # Madrid
    "SS": ".ST",  # Stoccolma
    "DC": ".CO",  # Copenaghen
    "NO": ".OL",  # Oslo
    "US": "",  # Stati Uniti, nessun suffisso
    "UN": "",
    "UQ": "",
    "UW": "",
}

# Ordine di preferenza: prima le piazze piu' liquide per un investitore europeo.
_PREFERRED = [".MI", ".DE", ".AS", ".L", ".PA", ".SW", "", ".F", ".MC"]


def isin_to_symbols(isin: str) -> list[str]:
    """Simboli Yahoo plausibili per un ISIN, dal piu' al meno preferibile."""
    isin = (isin or "").strip().upper()
    if not is_isin(isin):
        return []

    cached = cache.read_meta(f"openfigi/{isin}")
    if cached is not None:
        return cached.get("symbols", [])

    try:
        r = requests.post(
            URL,
            json=[{"idType": "ID_ISIN", "idValue": isin}],
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        payload = r.json()
    except Exception:
        return []

    rows = []
    if isinstance(payload, list) and payload:
        rows = payload[0].get("data") or []

    seen: list[str] = []
    for row in rows:
        ticker = (row.get("ticker") or "").strip().upper()
        exch = (row.get("exchCode") or "").strip().upper()
        if not ticker or exch not in EXCHANGE_SUFFIX:
            continue
        candidate = f"{ticker}{EXCHANGE_SUFFIX[exch]}"
        if candidate not in seen:
            seen.append(candidate)

    seen.sort(key=lambda s: _rank(s))
    cache.write_meta(f"openfigi/{isin}", {"symbols": seen})
    return seen


def _rank(symbol: str) -> int:
    for i, suffix in enumerate(_PREFERRED):
        if suffix and symbol.endswith(suffix):
            return i
    return len(_PREFERRED) if "." in symbol else _PREFERRED.index("")
