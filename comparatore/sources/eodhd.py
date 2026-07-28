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
from .base import Instrument, PriceSeries, naive_index

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

        def _fetch(s: dt.date, e: dt.date) -> pd.Series | None:
            try:
                r = requests.get(
                    f"{BASE_URL}/eod/{symbol}",
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

        series = cache.get_or_fetch(f"eodhd/{symbol}", start, end, _fetch)
        if series is None or series.empty:
            return None

        meta = cache.read_meta(f"eodhd-ccy/{symbol}")
        currency = (meta or {}).get("currency", "")
        if not currency:
            info = self.metadata(symbol)
            currency = info.currency if info else ""
            if currency:
                cache.write_meta(f"eodhd-ccy/{symbol}", {"currency": currency})

        return PriceSeries(
            symbol=symbol,
            prices=series,
            currency=currency,
            source=self.name,
            isin=isin,
        )
