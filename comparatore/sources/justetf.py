"""Fonte justETF: serie storiche di ETF europei, indicizzate per ISIN.

Perche' vale la pena averla
---------------------------
E' la fonte che copre il buco piu' fastidioso di Yahoo, cioe' proprio gli ETF
UCITS a cui questa applicazione e' dedicata. Rispetto a Yahoo:

  - si interroga per **ISIN**, quindi niente caccia al ticker giusto fra
    `.MI`, `.DE`, `.AS`, `.L` (CSPX.MI su Yahoo semplicemente non esiste);
  - restituisce la serie gia' **convertita** nella valuta richiesta, quindi si
    salta del tutto il passaggio FX;
  - copre dall'inizio della quotazione dell'ETF.

Avvertenza importante
---------------------
Questa e' un'**API interna e non documentata** di justETF: non c'e' alcun
contratto di stabilita' e puo' cambiare o sparire senza preavviso. Per questo
non e' mai l'unica fonte di un fondo - sta dietro il registry, che ripiega su
Yahoo appena qualcosa non torna. Le richieste sono limitate a quanto serve e
tenute in cache su disco per non tempestare il sito.

Non espone una ricerca o un endpoint TER documentato: quando l'utente ha
attivato l'opt-in, i metadati leggono la pagina profilo dell'ETF per ISIN. La
ricerca resta a Yahoo.
"""

from __future__ import annotations

import datetime as dt
import html
import re
import unicodedata

import pandas as pd
import requests

from .. import cache
from .base import Instrument, PriceSeries, is_isin, to_business_days

BASE_URL = "https://www.justetf.com/api/etfs"
PROFILE_URL = "https://www.justetf.com/it/etf-profile.html"
TIMEOUT = 30
_TER_VALUE_RE = re.compile(
    r'data-testid=["\']etf-profile-header_ter-value["\'][^>]*>\s*([^<]+)',
    re.IGNORECASE,
)
_DISTRIBUTION_VALUE_RE = re.compile(
    r'data-testid=["\']etf-profile-header_distribution-policy-value["\']'
    r'[^>]*>\s*([^<]+)',
    re.IGNORECASE,
)
_REPLICATION_VALUE_RE = re.compile(
    r'data-testid=["\']etf-profile-header_replication-value["\']'
    r'[^>]*>\s*([^<]+)',
    re.IGNORECASE,
)
_TITLE_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


class JustEtfSource:
    name = "justetf"
    label = "justETF"

    def __init__(self) -> None:
        self.last_metadata_outcome = "not_configured"

    def available(self) -> bool:
        return True

    def search(self, query: str, limit: int = 12, funds_only: bool = True):
        # Nessun endpoint di ricerca pubblico: la ricerca resta a Yahoo.
        return []

    def metadata(self, symbol: str, isin: str = "") -> Instrument | None:
        """Legge TER e nome dalla pagina profilo, solo quando il registry opt-in."""
        code = (isin or symbol or "").strip().upper()
        if not is_isin(code):
            self.last_metadata_outcome = "symbol_unresolved"
            return None

        # La versione nel nome evita di riusare il vecchio cache record che
        # conteneva solo TER e nome, prima delle caratteristiche ETF.
        key = f"justetf/meta/v2/{code}"
        cached = cache.read_meta(key, retention_days=1)
        if cached is not None:
            self.last_metadata_outcome = cached.get("outcome", "no_ter")
            return Instrument(
                symbol=symbol or code,
                name=cached.get("name") or symbol or code,
                quote_type="ETF",
                ter=cached.get("ter"),
                ter_source="justetf" if cached.get("ter") is not None else "",
                ter_origin="justetf" if cached.get("ter") is not None else "",
                isin=code,
                distribution_policy=cached.get("distribution_policy") or "",
                replication_method=cached.get("replication_method") or "",
            )

        try:
            response = requests.get(
                PROFILE_URL,
                params={"isin": code},
                headers=_HEADERS,
                timeout=TIMEOUT,
            )
        except Exception:
            self.last_metadata_outcome = "temporary_error"
            return None
        if response.status_code != 200:
            self.last_metadata_outcome = (
                "symbol_unresolved"
                if response.status_code == 404 else "temporary_error"
            )
            return None

        title_match = _TITLE_RE.search(response.text)
        name = (
            html.unescape(re.sub(r"<[^>]+>", "", title_match.group(1))).strip()
            if title_match else symbol or code
        )
        ter_match = _TER_VALUE_RE.search(response.text)
        ter = _parse_percentage(ter_match.group(1)) if ter_match else None
        distribution_match = _DISTRIBUTION_VALUE_RE.search(response.text)
        replication_match = _REPLICATION_VALUE_RE.search(response.text)
        distribution_policy = _parse_distribution_policy(
            distribution_match.group(1) if distribution_match else ""
        )
        replication_method = _parse_replication_method(
            replication_match.group(1) if replication_match else ""
        )
        outcome = "found" if ter is not None else "no_ter"
        self.last_metadata_outcome = outcome
        cache.write_meta(
            key,
            {
                "name": name,
                "ter": ter,
                "outcome": outcome,
                "distribution_policy": distribution_policy,
                "replication_method": replication_method,
            },
        )
        return Instrument(
            symbol=symbol or code,
            name=name,
            quote_type="ETF",
            ter=ter,
            ter_source="justetf" if ter is not None else "",
            ter_origin="justetf" if ter is not None else "",
            isin=code,
            distribution_policy=distribution_policy,
            replication_method=replication_method,
        )

    def prices(
        self,
        symbol: str,
        start: dt.date,
        end: dt.date,
        base_ccy: str = "EUR",
        isin: str = "",
    ) -> PriceSeries | None:
        """Serie total-return giornaliera, gia' convertita in `base_ccy`."""
        code = (isin or symbol or "").strip().upper()
        if not is_isin(code):
            # Senza ISIN questa fonte non e' interrogabile.
            return None

        base_ccy = (base_ccy or "EUR").upper()

        def _fetch(s: dt.date, e: dt.date) -> pd.Series | None:
            return _fetch_series(code, s, e, base_ccy)

        series = cache.get_or_fetch(f"justetf/{code}/{base_ccy}", start, end, _fetch)
        if series is None or series.empty:
            return None

        return PriceSeries(
            symbol=symbol or code,
            # La risposta contiene i giorni di calendario, weekend compresi.
            prices=to_business_days(series),
            currency=base_ccy,
            source=self.name,
            isin=code,
        )


def _fetch_series(
    isin: str, start: dt.date, end: dt.date, currency: str
) -> pd.Series | None:
    params = {
        "locale": "it",
        "currency": currency,
        "valuesType": "MARKET_VALUE",
        "reduceData": "false",
        # Senza questo la serie e' solo prezzo e sottostima i fondi a
        # distribuzione: verificato che cambia il risultato finale.
        "includeDividends": "true",
        "dateFrom": start.isoformat(),
        "dateTo": end.isoformat(),
    }
    try:
        r = requests.get(
            f"{BASE_URL}/{isin}/performance-chart",
            params=params,
            headers=_HEADERS,
            timeout=TIMEOUT,
        )
    except Exception:
        return None

    # 404: ISIN sconosciuto. Corpo vuoto: ISIN esistente ma non e' un ETF
    # (i fondi comuni non quotati non sono coperti).
    if r.status_code != 200 or not r.content.strip():
        return None

    try:
        rows = (r.json() or {}).get("series") or []
    except ValueError:
        return None

    values = {}
    for row in rows:
        raw = (row.get("value") or {}).get("raw")
        day = row.get("date")
        if day is None or raw is None:
            continue
        values[pd.Timestamp(day)] = float(raw)

    if not values:
        return None
    return pd.Series(values).sort_index()


def _parse_percentage(value: str) -> float | None:
    """Converte una percentuale mostrata in formato locale in frazione annua."""
    match = re.search(r"\d+(?:[.,]\d+)?", value or "")
    if not match:
        return None
    raw = match.group(0).replace(",", ".")
    try:
        number = float(raw)
    except ValueError:
        return None
    return number / 100 if number >= 0 else None


def _normalizza_caratteristica(value: str) -> str:
    return unicodedata.normalize("NFKD", html.unescape(value or "")).encode(
        "ascii", "ignore"
    ).decode("ascii").casefold()


def _parse_distribution_policy(value: str) -> str:
    """Normalizza la dicitura locale in un codice persistibile."""
    normalizzato = _normalizza_caratteristica(value)
    if "accumul" in normalizzato or "thesaur" in normalizzato or "capitalis" in normalizzato:
        return "accumulating"
    if "distrib" in normalizzato or "ausschutt" in normalizzato:
        return "distributing"
    return ""


def _parse_replication_method(value: str) -> str:
    """Riduce la replica a fisica o sintetica senza inventare un valore."""
    normalizzato = _normalizza_caratteristica(value)
    if "fisic" in normalizzato or "physical" in normalizzato:
        return "physical"
    if "sintetic" in normalizzato or "synthetic" in normalizzato:
        return "synthetic"
    return ""
