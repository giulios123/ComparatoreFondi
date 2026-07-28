"""Fonte Twelve Data (a chiave).

Piano gratuito piu' generoso di EODHD e copertura su una cinquantina di
mercati, ma piu' debole sui fondi comuni non quotati. Senza chiave la fonte si
dichiara non disponibile e il registry la salta.

La chiave si legge da `TWELVEDATA_API_KEY` oppure viene passata
dall'applicazione da `st.secrets`.

Limite noto: l'endpoint accetta al massimo 5000 osservazioni per richiesta,
circa diciannove anni di giorni di contrattazione. Le finestre piu' lunghe
vengono scaricate a blocchi e ricucite, cosi' il tetto non si traduce in
storico perso.
"""

from __future__ import annotations

import datetime as dt
import os

import pandas as pd
import requests

from .. import cache
from .base import Instrument, PriceSeries, naive_index

BASE_URL = "https://api.twelvedata.com"
TIMEOUT = 30
MAX_POINTS = 5000
# Giorni di calendario che stanno comodamente sotto MAX_POINTS di giorni feriali.
_CHUNK_DAYS = 365 * 15


class TwelveDataSource:
    name = "twelvedata"
    label = "Twelve Data"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = (api_key or os.environ.get("TWELVEDATA_API_KEY") or "").strip()

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
                f"{BASE_URL}/symbol_search",
                params={"symbol": query.strip(), "outputsize": limit},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            rows = (r.json() or {}).get("data") or []
        except Exception:
            return []

        out: list[Instrument] = []
        for row in rows:
            qtype = (row.get("instrument_type") or "").upper()
            if funds_only and "ETF" not in qtype and "FUND" not in qtype:
                continue
            symbol = row.get("symbol")
            if not symbol:
                continue
            out.append(
                Instrument(
                    symbol=symbol,
                    name=row.get("instrument_name") or symbol,
                    quote_type=qtype,
                    exchange=row.get("exchange") or "",
                    currency=(row.get("currency") or "").upper(),
                )
            )
            if len(out) >= limit:
                break
        return out

    def metadata(self, symbol: str) -> Instrument | None:
        # Twelve Data non espone il TER su piano gratuito: si usa solo la
        # valuta, che arriva insieme alla serie.
        return None

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

        currency_box: dict[str, str] = {}

        def _fetch(s: dt.date, e: dt.date) -> pd.Series | None:
            chunks: list[pd.Series] = []
            cursor = s
            while cursor <= e:
                stop = min(e, cursor + dt.timedelta(days=_CHUNK_DAYS))
                part = self._fetch_window(symbol, cursor, stop, currency_box)
                if part is not None and not part.empty:
                    chunks.append(part)
                cursor = stop + dt.timedelta(days=1)
            if not chunks:
                return None
            series = pd.concat(chunks)
            return series[~series.index.duplicated(keep="last")].sort_index()

        series = cache.get_or_fetch(f"twelvedata/{symbol}", start, end, _fetch)
        if series is None or series.empty:
            return None

        currency = currency_box.get("ccy", "")
        if currency:
            cache.write_meta(f"twelvedata-ccy/{symbol}", {"currency": currency})
        else:
            currency = (cache.read_meta(f"twelvedata-ccy/{symbol}") or {}).get(
                "currency", ""
            )

        return PriceSeries(
            symbol=symbol,
            prices=series,
            currency=currency,
            source=self.name,
            isin=isin,
        )

    def _fetch_window(
        self, symbol: str, start: dt.date, end: dt.date, currency_box: dict[str, str]
    ) -> pd.Series | None:
        try:
            r = requests.get(
                f"{BASE_URL}/time_series",
                params={
                    "symbol": symbol,
                    "interval": "1day",
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                    "outputsize": MAX_POINTS,
                    "apikey": self.api_key,
                    "order": "ASC",
                },
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            payload = r.json() or {}
        except Exception:
            return None

        if str(payload.get("status", "ok")).lower() == "error":
            return None

        meta = payload.get("meta") or {}
        if meta.get("currency"):
            currency_box["ccy"] = str(meta["currency"]).upper()

        values = {}
        for row in payload.get("values") or []:
            day = row.get("datetime")
            raw = row.get("close")
            if day is None or raw is None:
                continue
            try:
                values[pd.Timestamp(day)] = float(raw)
            except (TypeError, ValueError):
                continue
        if not values:
            return None
        series = pd.Series(values).sort_index()
        series.index = naive_index(series.index)
        return series
