"""Fonte Yahoo Finance: ricerca, metadati (valuta / TER) e prezzi.

E' la fonte generalista dell'applicazione: copre azioni, ETF e fondi comuni
quotati su gran parte dei mercati, e resta l'unica con una ricerca testuale
utilizzabile. I suoi limiti - copertura irregolare sugli ETF europei, TER
spesso assente o arrotondato - sono la ragione per cui esistono le altre fonti.

Il codice qui dentro proviene dal `data.py` originale; e' stato riorganizzato
dietro l'interfaccia comune, non riscritto.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd
import yfinance as yf

from .. import allocazione, cache
from ..instrument_facts import InstrumentFacts, candidate
from .base import Instrument, PriceSeries, naive_index

# Tipi Yahoo che hanno senso in un comparatore di fondi.
FUND_TYPES = ("ETF", "MUTUALFUND")


def _extract_ter(info: dict) -> tuple[float | None, str]:
    """Estrae una spesa corrente dal dizionario `info` di Yahoo.

    Yahoo la espone in modo incoerente: `annualReportExpenseRatio` e' una
    frazione decimale (0.0074), `netExpenseRatio` una percentuale (0.74). La
    copertura sui fondi europei e' scarsa, quindi il valore resta un suggerimento.
    """
    val = info.get("annualReportExpenseRatio")
    if isinstance(val, (int, float)) and val > 0:
        return float(val), "annualReportExpenseRatio"

    val = info.get("netExpenseRatio")
    if isinstance(val, (int, float)) and val > 0:
        return float(val) / 100.0, "netExpenseRatio"

    return None, ""


def _fund_composition(ticker) -> tuple[dict[str, dict[str, float]], list[dict]]:
    """Asset class, settori e prime posizioni dal modulo `funds_data`.

    E' l'unica composizione reale disponibile senza chiave: niente paesi ne'
    ripartizione geografica vera, ma settori e prime posizioni bastano a
    `allocazione.paesi_da_posizioni` per una stima. Una richiesta di rete in
    piu' rispetto a `info` - accettabile perche' chiamata solo da
    `cached_metadata` (un'ora di cache), non a ogni rerun.
    """
    try:
        fd = ticker.funds_data
        asset_classes = fd.asset_classes or {}
        sector_weightings = fd.sector_weightings or {}
        top_holdings = fd.top_holdings
    except Exception:
        return {}, []

    alloc = allocazione.classifica_da_yahoo(asset_classes, sector_weightings)

    holdings: list[dict] = []
    if top_holdings is not None and not top_holdings.empty:
        for sym, row in top_holdings.iterrows():
            try:
                quota = float(row.get("Holding Percent"))
            except (TypeError, ValueError):
                continue
            if quota > 0:
                holdings.append(
                    {"symbol": str(sym), "name": str(row.get("Name") or sym), "quota": quota}
                )
    return alloc, holdings


def _fund_operation_value(operations: pd.DataFrame, label: str):
    """Legge una riga di `fund_operations` senza legarsi alla lingua."""
    if operations is None or operations.empty:
        return None
    for index in operations.index:
        if str(index).casefold() == label.casefold():
            try:
                return operations.loc[index].iloc[0]
            except (AttributeError, IndexError, KeyError):
                return None
    return None


def _epoch_date(value) -> str:
    try:
        if isinstance(value, (int, float)) and value > 0:
            return dt.datetime.fromtimestamp(value, tz=dt.UTC).date().isoformat()
    except (OverflowError, OSError, TypeError, ValueError):
        pass
    return ""


class YahooSource:
    name = "yahoo"
    label = "Yahoo Finance"

    def __init__(self) -> None:
        self.last_metadata_outcome = "temporary_error"

    def available(self) -> bool:
        return True

    # ----------------------------------------------------------------- ricerca

    def search(
        self, query: str, limit: int = 12, funds_only: bool = True
    ) -> list[Instrument]:
        """Cerca per nome, ticker o ISIN.

        La ricerca per ISIN funziona direttamente (IE00B3XXRP09 -> VUSA.L), che
        e' il modo abituale di identificare i fondi europei.
        """
        query = (query or "").strip()
        if not query:
            return []

        try:
            res = yf.Search(
                query,
                max_results=max(limit, 10),
                news_count=0,
                lists_count=0,
                enable_fuzzy_query=True,
                raise_errors=False,
            )
            quotes = res.quotes or []
        except Exception:
            return []

        out: list[Instrument] = []
        for row in quotes:
            qtype = (row.get("quoteType") or "").upper()
            if funds_only and qtype not in FUND_TYPES:
                continue
            symbol = row.get("symbol")
            if not symbol:
                continue
            out.append(
                Instrument(
                    symbol=symbol,
                    name=row.get("longname") or row.get("shortname") or symbol,
                    quote_type=qtype,
                    exchange=row.get("exchDisp") or row.get("exchange") or "",
                )
            )
            if len(out) >= limit:
                break
        return out

    # --------------------------------------------------------------- metadati

    def metadata(self, symbol: str) -> Instrument | None:
        """Nome, valuta, TER e composizione (per quanto possibile) di un simbolo."""
        ticker = yf.Ticker(symbol)
        try:
            info = ticker.info or {}
        except Exception:
            info = {}

        ter, source = _extract_ter(info)
        name = info.get("longName") or info.get("shortName") or symbol
        currency = info.get("currency") or ""
        quote_type = (info.get("quoteType") or "").upper()

        if not currency:
            # `info` puo' tornare vuoto sulle quotazioni sottili; i metadati di
            # prezzo sono piu' economici e piu' affidabili come ripiego.
            try:
                meta = ticker.history_metadata or {}
                currency = meta.get("currency") or ""
            except Exception:
                currency = ""

        allocation: dict[str, dict[str, float]] = {}
        holdings: list[dict] = []
        facts = {}
        if quote_type in FUND_TYPES:
            # Solo su ETF/fondi: sui titoli singoli l'endpoint di `funds_data`
            # risponde 404, e sarebbe una richiesta di rete sprecata a ogni
            # aggiunta.
            allocation, holdings = _fund_composition(ticker)

            # `funds_data` espone un piccolo profilo stabile oltre alle
            # partecipazioni. Se un modulo e' assente il fatto resta n/d.
            try:
                overview = ticker.funds_data.fund_overview or {}
                operations = ticker.funds_data.fund_operations
            except Exception:
                overview, operations = {}, pd.DataFrame()
            acquired = dt.date.today().isoformat()
            family = overview.get("family") or info.get("fundFamily")
            category = overview.get("categoryName") or info.get("category")
            aum = _fund_operation_value(operations, "Total Net Assets")
            if family:
                facts.setdefault("issuer", []).append(candidate(
                    family, "yahoo", acquired_at=acquired,
                ))
            if category:
                facts.setdefault("category", []).append(candidate(
                    category, "yahoo", acquired_at=acquired,
                ))
            if aum is None:
                aum = info.get("totalAssets")
            if isinstance(aum, (int, float)) and aum > 0:
                facts.setdefault("aum", []).append(candidate(
                    {"amount": float(aum), "currency": currency},
                    "yahoo", acquired_at=acquired,
                ))

            inception = _epoch_date(info.get("fundInceptionDate"))
            if inception:
                facts.setdefault("inception_date", []).append(candidate(
                    inception, "yahoo", observed_at=inception, acquired_at=acquired,
                ))
            for dimension, buckets in allocation.items():
                facts.setdefault(f"allocation.{dimension}", []).append(candidate(
                    buckets, "yahoo", acquired_at=acquired,
                ))
            if holdings:
                facts.setdefault("holdings", []).append(candidate(
                    holdings, "yahoo", acquired_at=acquired,
                ))

        acquired = dt.date.today().isoformat()
        if name:
            facts.setdefault("name", []).append(candidate(
                name, "yahoo", acquired_at=acquired,
            ))
        if ter is not None:
            facts.setdefault("ter", []).append(candidate(
                ter, "yahoo", acquired_at=acquired,
            ))

        self.last_metadata_outcome = (
            "temporary_error"
            if name == symbol and not currency and not quote_type and ter is None and not allocation
            else "found" if ter is not None else "no_ter"
        )

        return Instrument(
            symbol=symbol,
            name=name,
            quote_type=quote_type,
            exchange=info.get("fullExchangeName") or "",
            # Il maiuscolo/minuscolo conta: Londra e' quotata in "GBp" (penny).
            currency=currency,
            ter=ter,
            ter_source=source,
            ter_origin="yahoo" if ter is not None else "",
            allocation=allocation,
            allocation_source="yahoo" if allocation else "",
            holdings=holdings,
            holdings_source="yahoo" if holdings else "",
            facts=InstrumentFacts.merge(facts),
        )

    # ---------------------------------------------------------------- prezzi

    def prices(
        self,
        symbol: str,
        start: dt.date,
        end: dt.date,
        base_ccy: str = "",
        isin: str = "",
    ) -> PriceSeries | None:
        """Serie total-return di un simbolo, nella sua valuta nativa.

        La conversione la fa il chiamante: Yahoo non sa restituire una serie
        gia' convertita, e la valuta nativa serve comunque per la diagnostica.
        """
        currency_box: dict[str, str] = {}

        def _fetch(s: dt.date, e: dt.date) -> pd.Series | None:
            ticker = yf.Ticker(symbol)
            try:
                hist = ticker.history(
                    start=s,
                    # yfinance tratta `end` come estremo escluso.
                    end=e + dt.timedelta(days=1),
                    auto_adjust=True,  # total return: dividendi reinvestiti
                    actions=False,
                )
            except Exception:
                return None
            if hist is None or hist.empty or "Close" not in hist:
                return None
            # `history()` popola i metadati come effetto collaterale: la valuta
            # arriva senza una seconda chiamata di rete.
            try:
                currency_box["ccy"] = (ticker.history_metadata or {}).get(
                    "currency"
                ) or ""
            except Exception:
                pass
            close = hist["Close"].dropna()
            if close.empty:
                return None
            close.index = naive_index(close.index)
            return close.sort_index()

        series = cache.get_or_fetch(f"yahoo/{symbol}", start, end, _fetch)
        if series is None or series.empty:
            return None

        currency = currency_box.get("ccy", "")
        if currency:
            cache.write_meta(f"yahoo-ccy/{symbol}", {"currency": currency})
        else:
            # La serie e' arrivata dal disco: la valuta non e' stata rivista in
            # questo giro, e non vale una chiamata di rete solo per riottenerla.
            currency = self.currency_of(symbol)

        return PriceSeries(
            symbol=symbol,
            prices=series,
            currency=currency,
            source=self.name,
            isin=isin,
        )

    @staticmethod
    def currency_of(symbol: str) -> str:
        """Valuta di un simbolo, dalla cache dei metadati se gia' nota."""
        cached = cache.read_meta(f"yahoo-ccy/{symbol}")
        if cached and cached.get("currency"):
            return cached["currency"]
        try:
            meta = yf.Ticker(symbol).history_metadata or {}
            currency = meta.get("currency") or ""
        except Exception:
            currency = ""
        if currency:
            cache.write_meta(f"yahoo-ccy/{symbol}", {"currency": currency})
        return currency


# --------------------------------------------------------------------------
# Funzioni di modulo, mantenute per compatibilita' con il codice esistente
# --------------------------------------------------------------------------

_default = YahooSource()


def search(query: str, limit: int = 12, funds_only: bool = True) -> list[Instrument]:
    return _default.search(query, limit, funds_only)


def get_metadata(symbol: str) -> Instrument:
    return _default.metadata(symbol) or Instrument(symbol=symbol, name=symbol, quote_type="")


def get_prices(
    symbols: list[str], start: dt.date, end: dt.date
) -> tuple[pd.DataFrame, dict[str, str]]:
    """Scarica piu' simboli insieme, nelle rispettive valute native."""
    symbols = list(dict.fromkeys(symbols))
    if not symbols:
        return pd.DataFrame(), {}

    cols: dict[str, pd.Series] = {}
    currencies: dict[str, str] = {}
    for sym in symbols:
        ps = _default.prices(sym, start, end)
        if ps is None:
            continue
        cols[sym] = ps.prices
        currencies[sym] = ps.currency

    if not cols:
        return pd.DataFrame(), {}

    frame = pd.DataFrame(cols).sort_index()
    return frame.dropna(how="all"), currencies
