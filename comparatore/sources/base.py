"""Interfaccia comune alle fonti di prezzo.

Ogni fonte espone la stessa forma - ricerca, metadati, prezzi - cosi' che il
registry possa provarle in ordine e ripiegare sulla successiva quando una non
copre lo strumento richiesto. Nessuna fonte e' obbligata a implementare tutto:
justETF per esempio non ha ne' ricerca ne' TER, e restituisce liste vuote.

`PriceSeries.currency` e' il punto di raccordo con la conversione valutaria:
alcune fonti (justETF, EODHD) sanno restituire la serie gia' nella valuta
richiesta, e in quel caso il passaggio FX - il piu' lento e fragile della
catena - si salta del tutto.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import pandas as pd

# Struttura di un ISIN: 2 lettere paese, 9 alfanumerici, 1 cifra di controllo.
_ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")


def is_isin(value: str) -> bool:
    return bool(_ISIN_RE.match((value or "").strip().upper()))


@dataclass
class Instrument:
    symbol: str
    name: str
    quote_type: str
    exchange: str = ""
    currency: str = ""
    ter: float | None = None  # frazione annua, es. 0.0022 == 0,22%
    ter_source: str = ""
    isin: str = ""
    # Ripartizione dello strumento: {dimensione: {bucket: quota}}, con le quote
    # di ogni dimensione che sommano a 1. Vuota quando la fonte non la espone -
    # oggi EODHD e Yahoo (via `funds_data`). Le chiavi sono quelle di
    # `comparatore.allocazione`.
    allocation: dict[str, dict[str, float]] = field(default_factory=dict)
    allocation_source: str = ""  # "eodhd" | "yahoo" | ""
    # Prime posizioni del fondo: [{"symbol", "name", "quota"}, ...], quota una
    # frazione di 1. Non e' una ripartizione - non copre l'intero strumento e
    # non ha senso forzarla nella forma {bucket: quota} di `allocation` - ma e'
    # il punto di partenza per una stima geografica quando nessuna fonte da'
    # la ripartizione per paese (vedi `comparatore.allocazione.paesi_da_posizioni`).
    holdings: list[dict] = field(default_factory=list)
    holdings_source: str = ""  # "yahoo" | ""
    # Fonte che ha restituito *questo risultato di ricerca* - distinto da
    # `ter_source`/`allocation_source`, che riguardano i metadati recuperati
    # dopo l'aggiunta al portafoglio. Valorizzato da `Registry.search()`,
    # vuoto per gli `Instrument` costruiti altrove (es. `metadata()`).
    source: str = ""
    # Provenienza normalizzata del valore: "yahoo", "eodhd" o "".
    # `ter_source` resta il dettaglio storico del campo restituito dalla fonte.
    ter_origin: str = ""

    @property
    def label(self) -> str:
        return f"{self.name} ({self.symbol})" if self.name else self.symbol


@dataclass
class PriceSeries:
    """Serie total-return giornaliera restituita da una fonte."""

    symbol: str
    prices: pd.Series
    currency: str  # valuta della serie; "" se ignota
    source: str  # "yahoo" | "justetf" | "eodhd" | "twelvedata" | "csv"
    isin: str = ""

    @property
    def empty(self) -> bool:
        return self.prices is None or self.prices.empty


@runtime_checkable
class PriceSource(Protocol):
    name: str
    label: str

    def available(self) -> bool:
        """False se la fonte non e' configurata (per esempio manca la chiave)."""
        ...

    def search(self, query: str, limit: int, funds_only: bool) -> list[Instrument]:
        ...

    def metadata(self, symbol: str) -> Instrument | None:
        ...

    def prices(
        self, symbol: str, start: dt.date, end: dt.date, base_ccy: str, isin: str = ""
    ) -> PriceSeries | None:
        ...


def naive_index(idx: pd.Index) -> pd.DatetimeIndex:
    """Indice di date senza fuso orario, normalizzato a mezzanotte."""
    idx = pd.DatetimeIndex(idx)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    return idx.normalize()


def to_business_days(series: pd.Series) -> pd.Series:
    """Riallinea una serie ai giorni feriali.

    Alcune fonti (justETF) restituiscono giorni di calendario, weekend inclusi,
    con il valore dell'ultima chiusura ripetuto. Il motore ragiona a passi di
    contrattazione e calcola la volatilita' annualizzando sui giorni presenti:
    lasciare dentro i weekend gonfierebbe il conteggio dei periodi e falserebbe
    le metriche di rischio.
    """
    if series is None or series.empty:
        return series
    return series[series.index.dayofweek < 5]
