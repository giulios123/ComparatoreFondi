"""Ordine delle fonti, ripiego automatico e diagnostica.

Nessuna fonte, presa da sola, copre tutti i casi: Yahoo ha la ricerca ma buchi
sugli ETF europei, justETF ha gli ETF europei ma vuole l'ISIN e non ha ricerca,
il CSV copre tutto ma va caricato a mano. Il registry le prova in ordine e si
ferma alla prima che risponde, tenendo traccia di **cosa ha tentato e come e'
andata**: quando una serie non arriva, l'utente deve poter vedere perche' e non
trovarsi un grafico vuoto senza spiegazione.

Ordine predefinito:

  1. CSV caricato   - indicazione esplicita dell'utente, prevale su tutto
    2. Yahoo          - fonte generalista, sempre disponibile
    3. EODHD          - se configurata con chiave
    4. Twelve Data    - se configurata con chiave

justETF usa un endpoint interno non documentato: entra nell'ordine automatico
solo con opt-in, oppure quando l'utente la seleziona esplicitamente.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import pandas as pd

from .. import allocazione
from .base import Instrument, PriceSeries, is_isin
from .csv_source import CsvSource
from .eodhd import EodhdSource, to_yahoo_symbol
from .justetf import JustEtfSource
from .twelvedata import TwelveDataSource
from .yahoo import YahooSource

AUTO = "auto"


@dataclass
class Attempt:
    source: str
    # "ok" | "no_data" | "not_configured" | "isin_required"
    # vedi comparatore.i18n.etichetta_esito
    outcome: str


@dataclass
class MetadataAttempt:
    source: str
    # "found" | "no_ter" | "not_configured" | "blocked" |
    # "symbol_unresolved" | "temporary_error"
    outcome: str
    detail: str = ""


@dataclass
class MetadataResolution:
    symbol: str
    instrument: Instrument
    attempts: list[MetadataAttempt] = field(default_factory=list)


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
        enable_justetf: bool = False,
    ) -> None:
        self.enable_justetf = enable_justetf
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

        def _add(items: list[Instrument], source_name: str) -> None:
            for item in items:
                if item.symbol.upper() in seen:
                    continue
                seen.add(item.symbol.upper())
                item.source = item.source or source_name
                found.append(item)

        _add(self.yahoo.search(query, limit, funds_only), self.yahoo.name)

        if is_isin(query):
            isin = query.upper()
            for item in found:
                item.isin = item.isin or isin
            _add(self._from_isin(isin, seen), "openfigi")

        for source in (self.eodhd, self.twelvedata):
            if source.available() and len(found) < limit:
                _add(source.search(query, limit - len(found), funds_only), source.name)

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
                    exchange="",
                    isin=isin,
                )
            )
        return out

    # --------------------------------------------------------------- metadati

    def metadata(self, symbol: str, isin: str = "") -> Instrument:
        """Metadati del fondo, integrando TER e classificazione da EODHD."""
        info = self.yahoo.metadata(symbol) or Instrument(
            symbol=symbol, name=symbol, quote_type=""
        )
        if isin and not info.isin:
            info.isin = isin

        if not info.currency:
            # Il simbolo puo' essere nel formato EODHD (`REET.US`,
            # `VWCE.XETRA`): Yahoo non lo riconosce cosi' com'e' e restituisce
            # un Instrument vuoto. Il suo equivalente Yahoo spesso esiste e
            # porta con se' non solo la valuta ma anche nome, TER e
            # composizione.
            translated = to_yahoo_symbol(symbol)
            if translated:
                alt = self.yahoo.metadata(translated)
                if alt is not None and alt.currency:
                    info.currency = alt.currency
                    if info.name == symbol:
                        info.name = alt.name
                    if info.ter is None:
                        info.ter, info.ter_source = alt.ter, alt.ter_source
                        info.ter_origin = alt.ter_origin
                    if not info.quote_type:
                        info.quote_type = alt.quote_type
                    if not info.allocation and alt.allocation:
                        info.allocation = alt.allocation
                        info.allocation_source = alt.allocation_source
                    if not info.holdings and alt.holdings:
                        info.holdings = alt.holdings
                        info.holdings_source = alt.holdings_source

        # La ripartizione per area geografica la espone solo EODHD: la fonte
        # si interroga anche quando TER e composizione sono gia' arrivati da
        # Yahoo, se manca ancora quella dimensione. Senza chiave `available()`
        # e' False e non parte nessuna chiamata.
        manca_area = "area" not in (info.allocation or {})
        if info.ter is None and self.enable_justetf and not info.isin and self.eodhd.available():
            # La ricerca EODHD resta disponibile anche quando il piano blocca
            # l'endpoint fundamentals: serve qui solo a passare l'ISIN a justETF.
            eod_symbol = self.eodhd.resolve_metadata_symbol(symbol)
            if eod_symbol:
                ticker = symbol.rsplit(".", 1)[0].upper()
                for hit in self.eodhd.search(ticker, limit=20, funds_only=False):
                    if hit.symbol.upper() == eod_symbol.upper() and hit.isin:
                        info.isin = hit.isin
                        break

        if info.ter is None and self.enable_justetf:
            justetf_info = self.justetf.metadata(symbol, info.isin)
            if justetf_info is not None:
                if info.ter is None and justetf_info.ter is not None:
                    info.ter = justetf_info.ter
                    info.ter_source = justetf_info.ter_source
                    info.ter_origin = justetf_info.ter_origin
                if info.name == symbol and justetf_info.name:
                    info.name = justetf_info.name
                info.isin = info.isin or justetf_info.isin

        if (info.ter is None or not info.allocation or manca_area) and self.eodhd.available():
            # Il simbolo di Yahoo non e' quello di EODHD (VWCE.DE contro
            # VWCE.XETRA): senza la traduzione la richiesta cadrebbe nel vuoto
            # proprio nei casi in cui la fonte servirebbe. La corrispondenza
            # resta in cache, quindi si paga una volta sola per strumento.
            resolver = getattr(
                self.eodhd, "resolve_metadata_symbol", self.eodhd.resolve_symbol
            )
            eod_symbol = resolver(symbol, info.isin)
            if eod_symbol:
                richer = self.eodhd.metadata(eod_symbol)
                if richer is not None:
                    if info.ter is None and richer.ter is not None:
                        info.ter, info.ter_source = richer.ter, richer.ter_source
                        info.ter_origin = richer.ter_origin
                    if richer.allocation:
                        # EODHD vince per dimensione quando la copre (percentuali
                        # vere), Yahoo colma quelle che EODHD non ha - tipicamente
                        # `area`, che Yahoo non espone mai. Stessa combinazione
                        # che `app.classifica()` fa poi col nome.
                        fuso = allocazione.unisci(richer.allocation, info.allocation)
                        if fuso != info.allocation:
                            info.allocation = fuso
                            if fuso == richer.allocation:
                                info.allocation_source = richer.allocation_source
                if not info.currency:
                    # Stesso ripiego di `EodhdSource.prices()`: `/fundamentals`
                    # puo' essere bloccato dal piano (403), `/search` no.
                    info.currency = self.eodhd.currency_from_search(eod_symbol)
        return info

    def metadata_resolution(self, symbol: str, isin: str = "") -> MetadataResolution:
        """Metadati compatibili con una diagnostica leggibile dall'interfaccia.

        Il metodo riusa `metadata()` per non duplicare la fusione Yahoo/EODHD;
        gli esiti descrivono il risultato osservabile senza esporre traceback o
        dettagli delle chiavi API.
        """
        info = self.metadata(symbol, isin)
        attempts: list[MetadataAttempt] = []
        yahoo_empty = (
            info.name == symbol and not info.currency and not info.quote_type
            and info.ter is None and not info.allocation
        )
        yahoo_outcome = getattr(self.yahoo, "last_metadata_outcome", "")
        if info.ter_origin == "yahoo" or (info.ter is not None and info.ter_origin == ""):
            yahoo_outcome = "found"
        elif yahoo_outcome not in {"no_ter", "temporary_error"}:
            yahoo_outcome = "temporary_error" if yahoo_empty else "no_ter"
        attempts.append(MetadataAttempt("yahoo", yahoo_outcome))

        if not self.enable_justetf:
            justetf_outcome = "not_configured"
        elif info.ter_origin == "justetf":
            justetf_outcome = "found"
        else:
            justetf_outcome = getattr(
                self.justetf, "last_metadata_outcome", "temporary_error"
            )
            if justetf_outcome not in {
                "found", "no_ter", "symbol_unresolved", "temporary_error"
            }:
                justetf_outcome = "temporary_error"
        attempts.append(MetadataAttempt("justetf", justetf_outcome))

        if info.ter_origin == "eodhd":
            eodhd_outcome = "found"
        elif not self.eodhd.available():
            eodhd_outcome = "not_configured"
        else:
            eodhd_outcome = getattr(self.eodhd, "last_metadata_outcome", "temporary_error")
            if eodhd_outcome == "temporary_error" and getattr(
                self.eodhd, "fundamentals_blocked", lambda: False
            )():
                eodhd_outcome = "blocked"
            if eodhd_outcome == "temporary_error":
                exchange = symbol.rsplit(".", 1)[-1].upper() if "." in symbol else ""
                known_yahoo_exchange = exchange in {
                    "DE", "MI", "AS", "F", "L", "PA", "SW", "MC",
                }
                risolto = self.eodhd.resolve_symbol(symbol, isin)
                if (is_isin(isin or symbol) or known_yahoo_exchange) and not risolto:
                    eodhd_outcome = "symbol_unresolved"
            if eodhd_outcome not in {"found", "no_ter", "blocked", "symbol_unresolved"}:
                eodhd_outcome = "temporary_error"
        attempts.append(MetadataAttempt("eodhd", eodhd_outcome))
        return MetadataResolution(symbol=symbol, instrument=info, attempts=attempts)

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
            candidates = [self.csv]
            if self.enable_justetf:
                candidates.append(self.justetf)
            candidates.extend([self.yahoo, self.eodhd, self.twelvedata])

        for source in candidates:
            if source is None:
                continue
            if not source.available():
                res.attempts.append(Attempt(source.name, "not_configured"))
                continue
            if source is self.justetf and not is_isin(isin or symbol):
                res.attempts.append(Attempt(source.name, "isin_required"))
                continue

            series = source.prices(symbol, start, end, base_ccy, isin=isin)
            if series is not None and not series.empty:
                res.series = series
                res.attempts.append(Attempt(source.name, "ok"))
                return res
            res.attempts.append(Attempt(source.name, "no_data"))

            if source is self.yahoo:
                # Un simbolo nel formato EODHD (`REET.US`, `VWCE.XETRA`) non
                # esiste su Yahoo cosi' com'e': si ritenta col suo equivalente
                # prima di passare a EODHD, che su un piano gratuito puo' dare
                # i prezzi ma non la valuta ne' il TER.
                translated = to_yahoo_symbol(symbol)
                if translated:
                    alt = self.yahoo.prices(translated, start, end, base_ccy, isin=isin)
                    if alt is not None and not alt.empty:
                        # Verso l'esterno resta il simbolo scelto dall'utente:
                        # e' la chiave con cui il motore identifica la colonna.
                        alt.symbol = symbol
                        res.series = alt
                        res.attempts.append(Attempt(f"yahoo→{translated}", "ok"))
                        return res
                    res.attempts.append(Attempt(f"yahoo→{translated}", "no_data"))

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
