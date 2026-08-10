"""Fonte EOD Historical Data (a chiave).

E' la fonte con la copertura migliore sui fondi europei, inclusi molti fondi
comuni non quotati che ne' Yahoo ne' justETF vedono, e con un TER affidabile.
Richiede una registrazione: senza chiave la fonte si dichiara non disponibile e
il registry la salta senza rumore.

La chiave si legge da `EODHD_API_KEY` oppure viene passata dall'applicazione,
che a sua volta la prende da `st.secrets`. Non deve mai finire nel codice.
"""

from __future__ import annotations

import datetime as dt
import os

import pandas as pd
import requests

from .. import allocazione, cache
from .base import Instrument, PriceSeries, is_isin, naive_index

BASE_URL = "https://eodhd.com/api"
TIMEOUT = 30

# Suffisso Yahoo per ogni piazza EODHD elencata in `_EXCHANGE_RANK` qui sotto.
# Un fondo aggiunto da una ricerca EODHD porta il simbolo `Codice.Borsa` di
# EODHD (`REET.US`, `VWCE.XETRA`), che Yahoo non riconosce cosi' com'e' - si
# aspetta `REET`, `VWCE.DE`. Senza la traduzione lo strumento resta bloccato
# su EODHD anche quando Yahoo lo coprirebbe meglio: valuta, TER e
# classificazione inclusi. Tabella separata da `openfigi.EXCHANGE_SUFFIX`,
# che parla il vocabolario Bloomberg (`IM`, `GR`, `LN`) e non e' riusabile qui.
_YAHOO_SUFFIX = {
    "MI": ".MI",
    "XETRA": ".DE",
    "F": ".F",
    "AS": ".AS",
    "LSE": ".L",
    "PA": ".PA",
    "SW": ".SW",
    "MC": ".MC",
    "US": "",
}


def to_yahoo_symbol(symbol: str) -> str:
    """Equivalente Yahoo di un simbolo EODHD, o "" se non c'e' una traduzione.

    "" quando il simbolo non ha un punto, quando la piazza non e' mappata
    (es. `EUFUND`, i fondi comuni non quotati) o quando la traduzione
    coinciderebbe con l'originale.
    """
    if "." not in symbol:
        return ""
    code, exch = symbol.rsplit(".", 1)
    if exch not in _YAHOO_SUFFIX:
        return ""
    candidate = f"{code}{_YAHOO_SUFFIX[exch]}"
    return candidate if candidate != symbol else ""


class EodhdSource:
    name = "eodhd"
    label = "EOD Historical Data"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = (api_key or os.environ.get("EODHD_API_KEY") or "").strip()
        self.last_metadata_outcome = "not_configured" if not self.api_key else "temporary_error"

    def available(self) -> bool:
        return bool(self.api_key)

    def fundamentals_blocked(self) -> bool:
        """True se l'ultima `/fundamentals` e' stata rifiutata dal piano (403).

        Usato dall'interfaccia per spiegare perche' TER e classificazione
        mancano invece di lasciarlo un mistero: la causa e' contrattuale, non
        uno strumento non coperto.
        """
        payload = cache.read_meta("eodhd-fundamentals-blocked", retention_days=1) or {}
        return bool(payload.get("bloccato"))

    # ----------------------------------------------------------------- ricerca

    def search(
        self, query: str, limit: int = 12, funds_only: bool = True
    ) -> list[Instrument]:
        if not self.available() or not (query or "").strip():
            return []
        try:
            r = requests.get(
                f"{BASE_URL}/search/{query.strip()}",
                params={"api_token": self.api_key, "fmt": "json", "limit": limit},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            rows = r.json() or []
        except Exception:
            return []

        out: list[Instrument] = []
        for row in rows:
            qtype = (row.get("Type") or "").upper()
            if funds_only and "ETF" not in qtype and "FUND" not in qtype:
                continue
            code, exch = row.get("Code"), row.get("Exchange")
            if not code:
                continue
            out.append(
                Instrument(
                    symbol=f"{code}.{exch}" if exch else code,
                    name=row.get("Name") or code,
                    quote_type=qtype,
                    exchange=exch or "",
                    currency=(row.get("Currency") or "").upper(),
                    isin=(row.get("ISIN") or "").upper(),
                )
            )
            if len(out) >= limit:
                break
        return out

    def currency_from_search(self, eod_symbol: str) -> str:
        """Valuta di un simbolo `Codice.Borsa` dall'endpoint `/search`.

        A differenza di `/fundamentals`, `/search` risponde anche sui piani
        gratuiti: e' un ripiego piu' povero (niente TER, niente
        classificazione) ma basta a non perdere lo strumento nella
        conversione valutaria quando `/fundamentals` e' bloccato (403).
        """
        for hit in self.search(eod_symbol, limit=5, funds_only=False):
            if hit.symbol.upper() == eod_symbol.upper():
                return hit.currency
        return ""

    # --------------------------------------------------------------- metadati

    def metadata(self, symbol: str) -> Instrument | None:
        if not self.available():
            self.last_metadata_outcome = "not_configured"
            return None
        try:
            r = requests.get(
                f"{BASE_URL}/fundamentals/{symbol}",
                params={"api_token": self.api_key, "fmt": "json"},
                timeout=TIMEOUT,
            )
            if r.status_code == 403:
                # Il piano gratuito vede `/search` e `/eod` ma non
                # `/fundamentals`: senza questo flag l'errore resta invisibile
                # dietro il generico "TER non trovato", e l'utente non puo'
                # distinguere "questo strumento non ha TER" da "la chiave non
                # puo' vederlo". Riverificato ogni giorno, cosi' un upgrade di
                # piano si riflette da solo senza bisogno di riavviare l'app.
                cache.write_meta("eodhd-fundamentals-blocked", {"bloccato": True})
                self.last_metadata_outcome = "blocked"
                return None
            r.raise_for_status()
            payload = r.json() or {}
        except Exception:
            # Un 403 precedente non deve continuare a spiegare un errore
            # temporaneo per un'intera giornata: l'esito piu' recente vince.
            cache.write_meta("eodhd-fundamentals-blocked", {"bloccato": False})
            self.last_metadata_outcome = "temporary_error"
            return None

        cache.write_meta("eodhd-fundamentals-blocked", {"bloccato": False})

        general = payload.get("General") or {}
        etf_data = payload.get("ETF_Data") or {}

        ter = None
        for field in (
            "NetExpenseRatio",
            # Equivalente UCITS di NetExpenseRatio: pensato per il mercato
            # USA, su un fondo europeo (VWCE compreso) resta spesso a zero,
            # mentre "Ongoing_Charge" e' la voce che i KID chiamano TER.
            # `AnnualHoldingsTurnover` non e' un costo ma il tasso di
            # rotazione del portafoglio: leggerlo come TER sarebbe un dato
            # sbagliato, non solo mancante.
            "Ongoing_Charge",
        ):
            raw = etf_data.get(field)
            try:
                value = float(raw)
            except (TypeError, ValueError):
                continue
            if value > 0:
                # EODHD lo espone in percentuale (0.07 == 0,07%), per entrambi i campi.
                ter = value / 100.0
                break

        # Nello stesso payload ci sono `Asset_Allocation`, `World_Regions` e
        # `Sector_Weights`: e' l'unica fonte che dice *che cosa* e' uno
        # strumento, e la chiamata e' gia' stata pagata per il TER.
        alloc = allocazione.classifica_da_eodhd(etf_data)
        self.last_metadata_outcome = "found" if ter is not None else "no_ter"

        return Instrument(
            symbol=symbol,
            name=general.get("Name") or symbol,
            quote_type=(general.get("Type") or "").upper(),
            exchange=general.get("Exchange") or "",
            currency=(general.get("CurrencyCode") or "").upper(),
            ter=ter,
            ter_source="eodhd" if ter is not None else "",
            ter_origin="eodhd" if ter is not None else "",
            isin=(general.get("ISIN") or "").upper(),
            allocation=alloc,
            allocation_source="eodhd" if alloc else "",
        )

    # ---------------------------------------------------------------- prezzi

    # Piazze preferite quando un ISIN e' quotato su piu' mercati: prima quelle
    # di interesse per un investitore europeo, poi il resto.
    _EXCHANGE_RANK = ["MI", "XETRA", "F", "AS", "LSE", "PA", "SW", "MC", "US"]

    def resolve_symbol(self, symbol: str, isin: str = "") -> str | None:
        """Traduce un ISIN nel simbolo EODHD `Codice.Borsa`.

        Senza questo passaggio la fonte era inutilizzabile proprio nel caso per
        cui serve: partendo da un ISIN si sarebbe chiamato `/eod/IE00BCZNHK63`,
        che non e' un simbolo valido, e il registry sarebbe passato oltre senza
        che EODHD avesse avuto una possibilita' reale.

        La corrispondenza fra ISIN e ticker non cambia mai, quindi si conserva
        in cache senza scadenza, come fa openfigi.py per la stessa ragione.
        """
        code = (isin or symbol or "").strip().upper()
        if not is_isin(code):
            # Un ticker Yahoo puo' avere una piazza diversa da quella EODHD
            # (VWCE.DE contro VWCE.XETRA). Si cerca il codice EODHD solo quando
            # la conversione della piazza e' univoca; altrimenti si mantiene
            # il comportamento precedente e si prova il simbolo originale.
            if "." not in symbol:
                return symbol
            ticker, yahoo_exchange = symbol.rsplit(".", 1)
            exchange = {
                "DE": "XETRA", "MI": "MI", "AS": "AS", "F": "F",
                "L": "LSE", "PA": "PA", "SW": "SW", "MC": "MC",
            }.get(yahoo_exchange)
            if not exchange:
                return symbol
            hits = self.search(ticker, limit=20, funds_only=False)
            exact = [
                hit for hit in hits
                if hit.exchange.upper() == exchange
                and to_yahoo_symbol(hit.symbol).upper() == symbol.upper()
            ]
            # Restituire il ticker Yahoo in caso di mancata corrispondenza era
            # pericoloso: EODHD lo avrebbe poi interrogato come se fosse un
            # proprio simbolo, mascherando un mapping fallito come un errore
            # generico della fonte. Per le piazze riconoscibili, nessun match
            # esatto significa davvero "simbolo non risolto".
            return exact[0].symbol if exact else None

        retention_days = cache.restricted_retention_days()
        cached = cache.read_meta(f"eodhd-sym/{code}", retention_days)
        if cached is not None:
            trovato = cached.get("symbol") or ""
            if trovato:
                return trovato
            # L'esito negativo si conserva solo per un giorno: una ricerca puo'
            # essere fallita per una chiave sbagliata, per la quota esaurita o
            # per un disservizio, e memorizzarla per sempre renderebbe l'ISIN
            # introvabile anche dopo aver configurato una chiave valida.
            try:
                scaduto = dt.datetime.now() - dt.datetime.fromisoformat(
                    cached["visto"]
                ) > dt.timedelta(days=1)
            except Exception:
                scaduto = True
            if not scaduto:
                return None

        hits = self.search(code, limit=10, funds_only=False)
        if "." in symbol and symbol.rsplit(".", 1)[1].upper() in {
            "DE", "MI", "AS", "F", "L", "PA", "SW", "MC",
        }:
            # L'ISIN può avere più quotazioni. L'ordine di EODHD non è una
            # garanzia: si accetta soltanto quella che torna esattamente al
            # ticker Yahoo originale, e solo in assenza di piazza nel ticker
            # si usa il ranking europeo qui sotto.
            exact = [
                hit for hit in hits
                if to_yahoo_symbol(hit.symbol).upper() == symbol.upper()
            ]
            if not exact:
                cache.write_meta(
                    f"eodhd-sym/{code}",
                    {"symbol": "", "visto": dt.datetime.now().isoformat(timespec="seconds")},
                )
                return None
            hits = exact
        resolved = None
        if hits:
            def rank(instrument) -> int:
                exch = (instrument.exchange or "").upper()
                return (
                    self._EXCHANGE_RANK.index(exch)
                    if exch in self._EXCHANGE_RANK
                    else len(self._EXCHANGE_RANK)
                )

            resolved = sorted(hits, key=rank)[0].symbol

        cache.write_meta(
            f"eodhd-sym/{code}",
            {
                "symbol": resolved or "",
                "visto": dt.datetime.now().isoformat(timespec="seconds"),
            },
        )
        return resolved

    def prices(
        self,
        symbol: str,
        start: dt.date,
        end: dt.date,
        base_ccy: str = "",
        isin: str = "",
    ) -> PriceSeries | None:
        if not self.available():
            return None

        eod_symbol = self.resolve_symbol(symbol, isin)
        if not eod_symbol:
            return None

        def _fetch(s: dt.date, e: dt.date) -> pd.Series | None:
            try:
                r = requests.get(
                    f"{BASE_URL}/eod/{eod_symbol}",
                    params={
                        "api_token": self.api_key,
                        "fmt": "json",
                        "period": "d",
                        "from": s.isoformat(),
                        "to": e.isoformat(),
                    },
                    timeout=TIMEOUT,
                )
                r.raise_for_status()
                rows = r.json() or []
            except Exception:
                return None
            values = {}
            for row in rows:
                day = row.get("date")
                # `adjusted_close` incorpora i dividendi: e' la colonna
                # total-return, coerente con auto_adjust di Yahoo.
                raw = row.get("adjusted_close", row.get("close"))
                if day is None or raw is None:
                    continue
                values[pd.Timestamp(day)] = float(raw)
            if not values:
                return None
            series = pd.Series(values).sort_index()
            series.index = naive_index(series.index)
            return series

        retention_days = cache.restricted_retention_days()
        series = cache.get_or_fetch(
            f"eodhd/{eod_symbol}",
            start,
            end,
            _fetch,
            retention_days=retention_days,
        )
        if series is None or series.empty:
            return None

        meta = cache.read_meta(f"eodhd-ccy/{eod_symbol}", retention_days)
        currency = (meta or {}).get("currency", "")
        if not currency:
            info = self.metadata(eod_symbol)
            currency = info.currency if info else ""
            if not currency:
                # `/fundamentals` puo' essere bloccato dal piano (403):
                # `/search` e' piu' povero ma resta gratuito, e basta a non
                # scartare lo strumento dal backtest per valuta sconosciuta.
                currency = self.currency_from_search(eod_symbol)
            if currency:
                cache.write_meta(f"eodhd-ccy/{eod_symbol}", {"currency": currency})

        return PriceSeries(
            # Verso l'esterno resta il simbolo scelto dall'utente: e' la chiave
            # con cui il motore identifica la colonna.
            symbol=symbol,
            prices=series,
            currency=currency,
            source=self.name,
            isin=isin,
        )
