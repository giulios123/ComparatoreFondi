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

from .. import cache
from .base import Instrument, PriceSeries, is_isin, naive_index

BASE_URL = "https://eodhd.com/api"
TIMEOUT = 30


class EodhdSource:
    name = "eodhd"
    label = "EOD Historical Data"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = (api_key or os.environ.get("EODHD_API_KEY") or "").strip()

    def available(self) -> bool:
        return bool(self.api_key)

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

    # --------------------------------------------------------------- metadati

    def metadata(self, symbol: str) -> Instrument | None:
        if not self.available():
            return None
        try:
            r = requests.get(
                f"{BASE_URL}/fundamentals/{symbol}",
                params={"api_token": self.api_key, "fmt": "json"},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            payload = r.json() or {}
        except Exception:
            return None

        general = payload.get("General") or {}
        etf_data = payload.get("ETF_Data") or {}

        ter = None
        for field in ("NetExpenseRatio", "AnnualHoldingsTurnover", "TER"):
            raw = etf_data.get(field)
            try:
                value = float(raw)
            except (TypeError, ValueError):
                continue
            if field == "NetExpenseRatio" and value > 0:
                # EODHD lo espone in percentuale (0.07 == 0,07%).
                ter = value / 100.0
                break

        return Instrument(
            symbol=symbol,
            name=general.get("Name") or symbol,
            quote_type=(general.get("Type") or "").upper(),
            exchange=general.get("Exchange") or "",
            currency=(general.get("CurrencyCode") or "").upper(),
            ter=ter,
            ter_source="eodhd" if ter else "",
            isin=(general.get("ISIN") or "").upper(),
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
            # Gia' un simbolo di borsa: si usa com'e'.
            return symbol

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
