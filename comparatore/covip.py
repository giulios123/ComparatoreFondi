"""Previdenza complementare italiana: catalogo, rendimenti e costi da COVIP.

Cosa c'e' e cosa non c'e'
-------------------------
COVIP, l'autorita' di vigilanza, pubblica come open data (CC BY 4.0) l'albo di
tutti i fondi pensione italiani insieme ai rendimenti e all'Indicatore Sintetico
dei Costi. E' l'unica fonte completa e ufficiale su negoziali, aperti e PIP, che
non sono strumenti di mercato e non compaiono su nessuna API di quotazioni.

Il limite e' sostanziale e va capito prima di usare questo modulo: **i
rendimenti sono medie annue su orizzonti fissi** - ultimo anno, ultimi 3, 5, 10
e 20 anni - non serie storiche. Da cinque numeri annualizzati l'andamento anno
per anno non e' recuperabile: e' informazione irreversibilmente aggregata.

Ne consegue che per questi strumenti **non sono calcolabili** curva del
capitale, drawdown, volatilita', Sharpe, Sortino, Calmar ne' rendimenti per anno
solare. Chi vuole quelle misure deve procurarsi il valore quota dal sito del
proprio fondo e caricarlo con l'uploader CSV.

Il confronto che questo modulo abilita e' per orizzonti, ed e' rigoroso proprio
perche' non finge di avere dati che non esistono.

Perche' l'ISC conta
-------------------
L'ISC e' l'equivalente del TER per la previdenza. Per il Previgest Azionario di
Mediolanum vale 2,14% a dieci anni contro un rendimento decennale del 4,47%: i
costi si prendono circa un terzo del rendimento lordo. E' esattamente il genere
di divario che questa applicazione esiste per rendere visibile.
"""

from __future__ import annotations

import datetime as dt
import re
import unicodedata
from dataclasses import dataclass, field

import pandas as pd
import requests

from . import cache

# I file veri stanno qui. Gli URL registrati su dati.gov.it - del tipo
# covip.it/open-data/<nome>.csv - rispondono 404: il catalogo e' disallineato
# rispetto al sito, ed e' proprio quello che si trova cercando.
BASE_URL = "https://www.covip.it/sites/default/files/open-data"
TIMEOUT = 60
CACHE_TTL_DAYS = 7  # COVIP aggiorna con cadenza al piu' trimestrale

# Orizzonti pubblicati, in anni.
ORIZZONTI = (1, 3, 5, 10, 20)
ORIZZONTI_ISC = (2, 5, 10, 35)

TIPI = ("negoziale", "aperto", "PIP")

_HEADERS = {"User-Agent": "comparatore-fondi/0.3 (+https://localhost)"}

_ALBO_FILE = {
    "negoziale": "albo-fondi-pensione-negoziali",
    "aperto": "albo-fondi-pensione-aperti",
    "PIP": "albo-piani-individuali-pensionistici",
}
_REND_FILE = {
    "negoziale": "rendimenti-fondi-pensione-negoziali",
    "aperto": "rendimenti-fondi-pensione-aperti",
    "PIP": "rendimenti-piani-individuali-pensionistici",
}
_ISC_FILE = {
    "negoziale": "indicatori-sintetici-costi-fondi-pensione-negoziali",
    "aperto": "indicatori-sintetici-costi-fondi-pensione-aperti",
    "PIP": "indicatori-sintetici-costi-piani-individuali-pensionistici",
}

# Intestazioni delle colonne identificative, per tipo: i tre fogli hanno layout
# diversi fra loro, quindi si dichiarano invece di indovinarli. Il confronto e'
# per uguaglianza esatta dopo normalizzazione, altrimenti "COMPARTO"
# catturerebbe anche "CATEGORIA COMPARTO".
_REND_COLS = {
    "negoziale": {
        "albo": "N. ALBO", "fondo": "FONDO", "comparto": "COMPARTO",
        "categoria": "CATEGORIA", "societa": None,
    },
    "aperto": {
        "albo": "N. ALBO", "fondo": "FONDO PENSIONE APERTO", "comparto": "COMPARTO",
        "categoria": "CATEGORIA COMPARTO", "societa": "SOCIETA'",
    },
    "PIP": {
        "albo": "N. ALBO", "fondo": "PIP", "comparto": "LINEA",
        "categoria": "CATEGORIA LINEA", "societa": "SOCIETA'",
    },
}

# Nel foglio dei costi il nome del comparto sta in colonne diverse: i negoziali
# usano COMPARTO per il codice e COMPARTO_1 per il nome, gli altri il contrario.
_ISC_NAME_COL = {
    "negoziale": "COMPARTO_1",
    "aperto": "COMPARTO",
    "PIP": "COMPARTO",
}

_HEADER_ROW = 2  # riga delle intestazioni nei fogli dei rendimenti
_PERIOD_ROW = 4  # riga con "2025", "2023-2025", ...
_FIRST_DATA_ROW = 5


@dataclass(frozen=True)
class Comparto:
    """Un comparto (o linea, per i PIP) di un fondo pensione."""

    albo: str
    tipo: str  # "negoziale" | "aperto" | "PIP"
    fondo: str
    societa: str
    comparto: str
    categoria: str  # AZN | BIL | OBB MISTO | OBB PURO | GAR
    garanzia: bool = False
    rendimenti: dict[int, float] = field(default_factory=dict)  # anni -> % annua
    isc: dict[int, float] = field(default_factory=dict)  # anni -> %
    periodi: dict[int, str] = field(default_factory=dict)  # anni -> "2016-2025"

    @property
    def etichetta(self) -> str:
        return f"{self.fondo} · {self.comparto}"

    @property
    def chiave(self) -> str:
        return f"{self.tipo}|{self.albo}|{_norm(self.comparto)}"


# --------------------------------------------------------------------------
# Normalizzazione
# --------------------------------------------------------------------------


def _norm(value) -> str:
    """Maiuscolo, spazi compattati, accenti rimossi: per le giunzioni."""
    text = str(value or "").strip().upper()
    text = re.sub(r"\s+", " ", text)
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def _albo(value) -> str:
    """Numero d'albo come stringa: nei fogli compare sia '34' sia '34.0'."""
    text = str(value or "").strip()
    if not text or text.lower() == "nan":
        return ""
    try:
        return str(int(float(text)))
    except (TypeError, ValueError):
        return text


def _num(value) -> float | None:
    """Valore numerico, o None per le note fra parentesi tipo '(3)'."""
    number = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(number) else round(float(number), 4)


# --------------------------------------------------------------------------
# Scarico e lettura
# --------------------------------------------------------------------------


def _fetch_json(name: str) -> list[dict]:
    r = requests.get(f"{BASE_URL}/{name}.json", headers=_HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    payload = r.json()
    if isinstance(payload, list):
        return payload
    return next((v for v in payload.values() if isinstance(v, list)), [])


def _fetch_excel(name: str) -> pd.DataFrame:
    import io

    r = requests.get(f"{BASE_URL}/{name}.xlsx", headers=_HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name=0, header=None)


def _find_col(header: pd.Series, wanted: str) -> int | None:
    target = _norm(wanted)
    for idx, value in header.items():
        if _norm(value) == target:
            return int(idx)
    return None


def _parse_rendimenti(frame: pd.DataFrame, tipo: str) -> tuple[list[dict], dict[int, str]]:
    """Legge un foglio dei rendimenti.

    Le colonne identificative - societa', fondo, numero d'albo - compaiono solo
    sulla riga del primo comparto, perche' le celle sono unite in verticale:
    vanno riportate in avanti, altrimenti tutti i comparti successivi al primo
    resterebbero orfani del proprio fondo.
    """
    header = frame.iloc[_HEADER_ROW]
    spec = _REND_COLS[tipo]

    cols = {key: (_find_col(header, name) if name else None)
            for key, name in spec.items()}
    if cols["comparto"] is None or cols["albo"] is None:
        raise ValueError(f"COVIP: intestazioni non riconosciute nel foglio {tipo}")

    # I rendimenti occupano cinque colonne a partire da "RENDIMENTI MEDI ANNUI".
    start = next(
        (int(i) for i, v in header.items() if _norm(v).startswith("RENDIMENTI")), None
    )
    if start is None:
        raise ValueError(f"COVIP: colonna dei rendimenti assente nel foglio {tipo}")

    # I periodi si leggono dal file, non si ricavano dalla data odierna: sono
    # cio' che permette di confrontare il portafoglio sulle stesse finestre.
    period_row = frame.iloc[_PERIOD_ROW]
    periodi = {}
    for offset, anni in enumerate(ORIZZONTI):
        value = period_row.get(start + offset)
        if value is not None and str(value).lower() != "nan":
            periodi[anni] = str(value).strip()

    body = frame.iloc[_FIRST_DATA_ROW:].copy()
    for key in ("societa", "fondo", "albo"):
        col = cols.get(key)
        if col is not None:
            body[col] = body[col].ffill()

    out: list[dict] = []
    for _, row in body.iterrows():
        comparto = str(row.get(cols["comparto"]) or "").strip()
        albo = _albo(row.get(cols["albo"]))
        if not comparto or comparto.lower() == "nan" or not albo:
            continue
        rend = {}
        for offset, anni in enumerate(ORIZZONTI):
            value = _num(row.get(start + offset))
            if value is not None:
                rend[anni] = value
        out.append({
            "albo": albo,
            "tipo": tipo,
            "fondo": str(row.get(cols["fondo"]) or "").strip(),
            "societa": str(row.get(cols["societa"]) or "").strip()
            if cols.get("societa") is not None else "",
            "comparto": comparto,
            "categoria": str(row.get(cols["categoria"]) or "").strip()
            if cols.get("categoria") is not None else "",
            "rendimenti": rend,
            "periodi": periodi,
        })
    return out, periodi


def _parse_isc(frame: pd.DataFrame, tipo: str) -> dict[tuple[str, str], dict]:
    """Legge un foglio dei costi. Tabella piatta, intestazione sulla prima riga."""
    header = frame.iloc[0]
    col_albo = _find_col(header, "N. ALBO")
    col_name = _find_col(header, _ISC_NAME_COL[tipo])
    col_gar = _find_col(header, "GARANZIA")
    if col_albo is None or col_name is None:
        return {}

    col_isc = {}
    for anni in ORIZZONTI_ISC:
        col = _find_col(header, f"ISC {anni} ANNI")
        if col is not None:
            col_isc[anni] = col

    out: dict[tuple[str, str], dict] = {}
    for _, row in frame.iloc[1:].iterrows():
        albo = _albo(row.get(col_albo))
        name = str(row.get(col_name) or "").strip()
        if not albo or not name or name.lower() == "nan":
            continue
        values = {}
        for anni, col in col_isc.items():
            value = _num(row.get(col))
            if value is not None:
                values[anni] = value
        garanzia = _norm(row.get(col_gar)) in {"SI", "S"} if col_gar is not None else False
        out[(albo, _norm(name))] = {"isc": values, "garanzia": garanzia}
    return out


# --------------------------------------------------------------------------
# Catalogo
# --------------------------------------------------------------------------


def _build() -> dict:
    """Scarica e ricompone il catalogo completo."""
    comparti: list[dict] = []
    periodi_globali: dict[int, str] = {}
    anagrafica: dict[tuple[str, str], dict] = {}

    for tipo in TIPI:
        try:
            for row in _fetch_json(_ALBO_FILE[tipo]):
                albo = _albo(row.get("NumeroIscrizioneAlboFondo"))
                if albo:
                    anagrafica[(tipo, albo)] = {
                        "denominazione": (row.get("DenominazioneFondo") or "").strip(),
                        "societa": (row.get("DenominazioneSocieta") or "").strip(),
                    }
        except Exception:
            # L'albo arricchisce i nomi ma non e' indispensabile: i fogli dei
            # rendimenti contengono gia' fondo e societa'.
            pass

    for tipo in TIPI:
        try:
            frame = _fetch_excel(_REND_FILE[tipo])
            rows, periodi = _parse_rendimenti(frame, tipo)
        except Exception:
            continue
        periodi_globali.update(periodi)

        try:
            isc = _parse_isc(_fetch_excel(_ISC_FILE[tipo]), tipo)
        except Exception:
            isc = {}

        for row in rows:
            extra = isc.get((row["albo"], _norm(row["comparto"])), {})
            row["isc"] = extra.get("isc", {})
            row["garanzia"] = extra.get("garanzia", False)
            info = anagrafica.get((tipo, row["albo"]))
            if info:
                row["fondo"] = row["fondo"] or info["denominazione"]
                row["societa"] = row["societa"] or info["societa"]
            comparti.append(row)

    return {
        "comparti": comparti,
        "periodi": {str(k): v for k, v in periodi_globali.items()},
        "scaricato": dt.datetime.now().isoformat(timespec="seconds"),
    }


def _cached_payload(force: bool = False) -> dict:
    if not force:
        stored = cache.read_meta("covip/catalogo")
        if stored and stored.get("comparti"):
            try:
                age = dt.datetime.now() - dt.datetime.fromisoformat(stored["scaricato"])
                if age < dt.timedelta(days=CACHE_TTL_DAYS):
                    return stored
            except Exception:
                pass

    payload = _build()
    if payload["comparti"]:
        cache.write_meta("covip/catalogo", payload)
        return payload

    # Rete assente o COVIP irraggiungibile: meglio dati vecchi che nessun dato.
    stored = cache.read_meta("covip/catalogo")
    return stored if stored and stored.get("comparti") else payload


def catalogo(force: bool = False) -> list[Comparto]:
    """Tutti i comparti di fondi negoziali, aperti e PIP."""
    payload = _cached_payload(force)
    out = []
    for row in payload.get("comparti", []):
        out.append(
            Comparto(
                albo=row["albo"],
                tipo=row["tipo"],
                fondo=row["fondo"],
                societa=row["societa"],
                comparto=row["comparto"],
                categoria=row["categoria"],
                garanzia=bool(row.get("garanzia")),
                # Il round trip JSON trasforma le chiavi intere in stringhe.
                rendimenti={int(k): v for k, v in (row.get("rendimenti") or {}).items()},
                isc={int(k): v for k, v in (row.get("isc") or {}).items()},
                periodi={int(k): v for k, v in (row.get("periodi") or {}).items()},
            )
        )
    return out


def cerca(
    query: str = "",
    tipo: str | None = None,
    categoria: str | None = None,
    limit: int = 200,
) -> list[Comparto]:
    """Filtra il catalogo per testo, tipo di forma pensionistica e categoria."""
    needle = _norm(query)
    out = []
    for c in catalogo():
        if tipo and c.tipo != tipo:
            continue
        if categoria and _norm(c.categoria) != _norm(categoria):
            continue
        if needle:
            blob = _norm(f"{c.fondo} {c.societa} {c.comparto} {c.categoria}")
            if needle not in blob:
                continue
        out.append(c)
        if len(out) >= limit:
            break
    return out


def periodi() -> dict[int, str]:
    """Finestre di riferimento pubblicate, per esempio {10: '2016-2025'}."""
    payload = _cached_payload()
    return {int(k): v for k, v in (payload.get("periodi") or {}).items()}


def anno_riferimento() -> int | None:
    """Ultimo anno coperto dai dati COVIP."""
    for value in periodi().values():
        match = re.search(r"(\d{4})\s*$", str(value))
        if match:
            return int(match.group(1))
    return None


def finestra(anni: int) -> tuple[dt.date, dt.date] | None:
    """Intervallo di date di un orizzonte, letto dai periodi pubblicati.

    "2016-2025" -> (2016-01-01, 2025-12-31); "2025" -> (2025-01-01, 2025-12-31).
    """
    value = periodi().get(anni)
    if not value:
        return None
    years = re.findall(r"\d{4}", str(value))
    if not years:
        return None
    first, last = int(years[0]), int(years[-1])
    return dt.date(first, 1, 1), dt.date(last, 12, 31)


# --------------------------------------------------------------------------
# Curva sintetica
# --------------------------------------------------------------------------


def serie_sintetica(
    rendimento_annuo: float,
    inizio: dt.date,
    fine: dt.date,
    capitale: float = 10_000.0,
) -> pd.Series:
    """Crescita costante al tasso annuo indicato.

    Serve solo a rendere confrontabile a colpo d'occhio il **punto d'arrivo**
    con le curve reali. Non e' un andamento: e' una retta, e il percorso vero ha
    oscillato. Per questo la serie non va data in pasto al motore di backtest,
    dove produrrebbe volatilita' nulla, drawdown nullo e uno Sharpe privo di
    senso, facendo apparire un comparto azionario come privo di rischio.
    """
    index = pd.bdate_range(inizio, fine)
    if len(index) == 0:
        return pd.Series(dtype=float)
    anni = (index - index[0]).days.to_numpy() / 365.25
    return pd.Series(capitale * (1.0 + rendimento_annuo) ** anni, index=index)
