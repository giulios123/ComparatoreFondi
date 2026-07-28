"""Ordine delle fonti, ripiego automatico e diagnostica.

Nessuna fonte, presa da sola, copre tutti i casi: Yahoo ha la ricerca ma buchi
sugli ETF europei, justETF ha gli ETF europei ma vuole l'ISIN e non ha ricerca,
il CSV copre tutto ma va caricato a mano. Il registry le prova in ordine e si
ferma alla prima che risponde, tenendo traccia di **cosa ha tentato e come e'
andata**: quando una serie non arriva, l'utente deve poter vedere perche' e non
trovarsi un grafico vuoto senza spiegazione.

Ordine predefinito:

  1. CSV caricato   - indicazione esplicita dell'utente, prevale su tutto
  2. justETF        - se c'e' un ISIN; miglior copertura sugli ETF UCITS
  3. Yahoo          - fonte generalista, sempre disponibile
  4. EODHD          - se configurata con chiave
  5. Twelve Data    - se configurata con chiave
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import pandas as pd

from .base import Instrument, PriceSeries, is_isin
from .csv_source import CsvSource
from .eodhd import EodhdSource
from .justetf import JustEtfSource
from .twelvedata import TwelveDataSource
from .yahoo import YahooSource

AUTO = "auto"


@dataclass
class Attempt:
    source: str
    outcome: str  # "ok" | "nessun dato" | "non configurata" | "serve l'ISIN"


@dataclass
class Resolution:
    symbol: str
    series: PriceSeries | None
    attempts: list[Attempt] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.series is not None and not self.series.empty


@dataclass
class FrameResult:
    prices: pd.DataFrame
    currencies: dict[str, str] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)
    resolutions: dict[str, Resolution] = field(default_factory=dict)

    @property
    def missing(self) -> list[str]:
        return [s for s, r in self.resolutions.items() if not r.ok]


class Registry:
    def __init__(
        self,
        eodhd_key: str | None = None,
        twelvedata_key: str | None = None,
    ) -> None:
        self.csv = CsvSource()
        self.justetf = JustEtfSource()
        self.yahoo = YahooSource()
        self.eodhd = EodhdSource(eodhd_key)
        self.twelvedata = TwelveDataSource(twelvedata_key)

    # ------------------------------------------------------------------ setup

    @property
    def all_sources(self) -> list:
        return [self.csv, self.justetf, self.yahoo, self.eodhd, self.twelvedata]

    def source_by_name(self, name: str):
        return next((s for s in self.all_sources if s.name == name), None)

    def available_names(self) -> list[str]:
        return [s.name for s in self.all_sources if s.available()]

    # ---------------------------------------------------------------- ricerca

    def search(
        self, query: str, limit: int = 15, funds_only: bool = True
    ) -> list[Instrument]:
        """Cerca su Yahoo, integrando con le fonti a chiave se configurate.

        Se la query e' un ISIN si prova anche la risoluzione OpenFIGI, che
        spesso trova la quotazione giusta quando la ricerca Yahoo non la
        restituisce (CSPX.MI non esiste: il simbolo di Milano e' CSSPX.MI).
        """
        query = (query or "").strip()
        if not query:
            return []

        found: list[Instrument] = []
        seen: set[str] = set()

        def _add(items: list[Instrument]) -> None:
            for item in items:
                if item.symbol.upper() in seen:
                    continue
                seen.add(item.symbol.upper())
                found.append(item)

        _add(self.yahoo.search(query, limit, funds_only))

        if is_isin(query):
            isin = query.upper()
            for item in found:
                item.isin = item.isin or isin
            _add(self._from_isin(isin, seen))

        for source in (self.eodhd, self.twelvedata):
            if source.available() and len(found) < limit:
                _add(source.search(query, limit - len(found), funds_only))

        return found[:limit]

    def _from_isin(self, isin: str, seen: set[str]) -> list[Instrument]:
        """Quotazioni ricavate dall'ISIN via OpenFIGI, non trovate da Yahoo."""
        from . import openfigi

        out: list[Instrument] = []
        for symbol in openfigi.isin_to_symbols(isin)[:4]:
            if symbol.upper() in seen:
                continue
            out.append(
                Instrument(
                    symbol=symbol,
                    name=f"{isin} · {symbol}",
                    quote_type="ETF",
                    exchange="da ISIN",
                    isin=isin,
                )
            )
        return out

    # --------------------------------------------------------------- metadati

    def metadata(self, symbol: str, isin: str = "") -> Instrument:
        """Metadati del fondo, integrando il TER dalle fonti che lo espongono."""
        info = self.yahoo.metadata(symbol) or Instrument(
            symbol=symbol, name=symbol, quote_type=""
        )
        if info.ter is None and self.eodhd.available():
            richer = self.eodhd.metadata(symbol)
            if richer is not None and richer.ter is not None:
                info.ter, info.ter_source = richer.ter, richer.ter_source
        if isin and not info.isin:
            info.isin = isin
        return info

    # ---------------------------------------------------------------- prezzi

    def resolve(
        self,
        symbol: str,
        start: dt.date,
        end: dt.date,
        base_ccy: str,
        isin: str = "",
        preferred: str = AUTO,
    ) -> Resolution:
        """Prima fonte che restituisce dati per un fondo."""
        res = Resolution(symbol=symbol, series=None)

        if preferred and preferred != AUTO:
            source = self.source_by_name(preferred)
            candidates = [source] if source else []
        else:
            candidates = [
                self.csv,
                self.justetf,
                self.yahoo,
                self.eodhd,
                self.twelvedata,
            ]

        for source in candidates:
            if source is None:
                continue
            if not source.available():
                res.attempts.append(Attempt(source.name, "non configurata"))
                continue
            if source is self.justetf and not is_isin(isin or symbol):
                res.attempts.append(Attempt(source.name, "serve l'ISIN"))
                continue

            series = source.prices(symbol, start, end, base_ccy, isin=isin)
            if series is not None and not series.empty:
                res.series = series
                res.attempts.append(Attempt(source.name, "ok"))
                return res
            res.attempts.append(Attempt(source.name, "nessun dato"))

        return res

    def resolve_many(
        self,
        specs: list[dict],
        start: dt.date,
        end: dt.date,
        base_ccy: str,
    ) -> FrameResult:
        """Risolve piu' fondi e monta il frame dei prezzi.

        Ogni `spec` e' un dizionario con almeno `symbol`, opzionalmente `isin`
        e `source` (per forzare una fonte). Le colonne del frame sono i simboli,
        cosi' il motore di backtest non cambia.
        """
        columns: dict[str, pd.Series] = {}
        out = FrameResult(prices=pd.DataFrame())

        for spec in specs:
            symbol = spec["symbol"]
            res = self.resolve(
                symbol,
                start,
                end,
                base_ccy,
                isin=spec.get("isin", "") or "",
                preferred=spec.get("source", AUTO) or AUTO,
            )
            out.resolutions[symbol] = res
            if not res.ok:
                continue
            columns[symbol] = res.series.prices
            out.currencies[symbol] = res.series.currency
            out.sources[symbol] = res.series.source

        if columns:
            frame = pd.DataFrame(columns).sort_index()
            out.prices = frame.dropna(how="all")
        return out
