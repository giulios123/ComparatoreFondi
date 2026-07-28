"""Cambi giornalieri: tassi ufficiali BCE, con Yahoo come ripiego.

Perche' non bastava Yahoo
-------------------------
La versione precedente prendeva i cambi dalle coppie Yahoo `EURUSD=X` e
riempiva i buchi con `.ffill().bfill()`. Il `bfill()` e' il problema: Yahoo
pubblica `EURUSD=X` **solo dal 2003-12-01**, quindi un fondo statunitense
analizzato dal 1990 veniva convertito per tredici anni con il cambio del
dicembre 2003 - senza alcun avviso, e con un errore che cresce quanto piu' si
allunga il periodo.

Qui i tassi arrivano dalla BCE (via Frankfurter, senza chiave API), che
pubblica dal **1999-01-04**. Il `ffill` resta perche' corretto - nei giorni di
chiusura vale l'ultimo cambio pubblicato - ma il `bfill` sparisce: prima della
prima data disponibile non si inventa nulla, si lascia NaN. Il motore parte
gia' dalla prima data valida di tutte le colonne, quindi un NaN iniziale
accorcia la finestra invece di falsarla.

Restano coperte da Yahoo le valute fuori dal paniere BCE, per non perdere
copertura rispetto a prima.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import pandas as pd
import requests

from . import cache

FRANKFURTER = "https://api.frankfurter.dev/v1"
# Generoso di proposito: la prima richiesta su un intervallo lungo puo' costare
# decine di secondi finche' la CDN di Frankfurter non l'ha in cache (misurati
# 27s a freddo, 0,1s a caldo). Con un timeout stretto si ripiegherebbe su Yahoo
# proprio nei periodi lunghi, cioe' dove i cambi BCE servono davvero.
TIMEOUT = 60

# Prima data di pubblicazione dei cambi di riferimento BCE.
ECB_START = dt.date(1999, 1, 4)

# Paniere BCE, usato se l'endpoint /currencies non risponde.
_FALLBACK_CURRENCIES = {
    "AUD", "BGN", "BRL", "CAD", "CHF", "CNY", "CZK", "DKK", "EUR", "GBP",
    "HKD", "HUF", "IDR", "ILS", "INR", "ISK", "JPY", "KRW", "MXN", "MYR",
    "NOK", "NZD", "PHP", "PLN", "RON", "SEK", "SGD", "THB", "TRY", "USD",
    "ZAR",
}

_currencies_cache: set[str] | None = None


def supported_currencies() -> set[str]:
    """Valute coperte dalla BCE."""
    global _currencies_cache
    if _currencies_cache is not None:
        return _currencies_cache
    try:
        r = requests.get(f"{FRANKFURTER}/currencies", timeout=TIMEOUT)
        r.raise_for_status()
        _currencies_cache = {c.upper() for c in r.json()}
    except Exception:
        _currencies_cache = set(_FALLBACK_CURRENCIES)
    return _currencies_cache


def _naive_index(idx: pd.Index) -> pd.DatetimeIndex:
    idx = pd.DatetimeIndex(idx)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    return idx.normalize()


# --------------------------------------------------------------------------
# Sorgenti dei tassi
# --------------------------------------------------------------------------


def _ecb_rates(src: str, dst: str, start: dt.date, end: dt.date) -> pd.Series | None:
    """Tasso giornaliero BCE per cui moltiplicare un importo in `src`."""
    start = max(start, ECB_START)
    if start > end:
        return None

    url = f"{FRANKFURTER}/{start.isoformat()}..{end.isoformat()}"
    try:
        r = requests.get(
            url, params={"base": src, "symbols": dst}, timeout=TIMEOUT
        )
        r.raise_for_status()
        payload = r.json()
    except Exception:
        return None

    rows = payload.get("rates") or {}
    values = {
        pd.Timestamp(day): float(vals[dst])
        for day, vals in rows.items()
        if dst in vals
    }
    if not values:
        return None
    return pd.Series(values).sort_index()


def _yahoo_rates(src: str, dst: str, start: dt.date, end: dt.date) -> pd.Series | None:
    """Ripiego su Yahoo per le valute fuori dal paniere BCE."""
    import yfinance as yf

    for symbol, invert in ((f"{src}{dst}=X", False), (f"{dst}{src}=X", True)):
        try:
            hist = yf.Ticker(symbol).history(
                start=start, end=end + dt.timedelta(days=1), auto_adjust=False
            )
        except Exception:
            continue
        if hist is None or hist.empty or "Close" not in hist:
            continue
        rate = hist["Close"].dropna()
        if rate.empty:
            continue
        rate.index = _naive_index(rate.index)
        return (1.0 / rate) if invert else rate
    return None


@dataclass
class RateSeries:
    rates: pd.Series
    source: str  # "ecb" | "yahoo"
    first_available: dt.date


def rates(
    src: str, dst: str, start: dt.date, end: dt.date, use_cache: bool = True
) -> RateSeries | None:
    """Tasso giornaliero per convertire da `src` a `dst`, BCE con ripiego Yahoo."""
    src, dst = src.upper(), dst.upper()
    if src == dst:
        idx = pd.date_range(start, end, freq="D")
        return RateSeries(pd.Series(1.0, index=idx), "identita", start)

    ecb_ok = {src, dst} <= supported_currencies()
    source = "ecb" if ecb_ok else "yahoo"
    fetcher = _ecb_rates if ecb_ok else _yahoo_rates

    def _fetch(s: dt.date, e: dt.date) -> pd.Series | None:
        return fetcher(src, dst, s, e)

    key = f"fx/{source}/{src}{dst}"
    series = (
        cache.get_or_fetch(key, start, end, _fetch) if use_cache else _fetch(start, end)
    )

    if series is None or series.empty:
        # La BCE copre la coppia ma la chiamata e' fallita: si tenta Yahoo
        # comunque, prima di dichiarare il fondo non convertibile.
        if ecb_ok:
            series = _yahoo_rates(src, dst, start, end)
            source = "yahoo"
        if series is None or series.empty:
            return None

    return RateSeries(
        rates=series.sort_index(),
        source=source,
        first_available=series.index[0].date(),
    )


# --------------------------------------------------------------------------
# Conversione di un frame di prezzi
# --------------------------------------------------------------------------


@dataclass
class FxResult:
    prices: pd.DataFrame
    converted: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    # simbolo -> data da cui esiste davvero un cambio, quando posteriore
    # all'inizio richiesto: serve all'interfaccia per spiegare l'accorciamento.
    truncated: dict[str, dt.date] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)


def convert_currency(
    prices: pd.DataFrame,
    currencies: dict[str, str],
    base: str,
    start: dt.date,
    end: dt.date,
) -> FxResult:
    """Converte ogni colonna in `base` ai cambi giornalieri.

    Le colonne la cui valuta non e' risolvibile vengono scartate: mescolare
    valute diverse produrrebbe una curva semplicemente sbagliata. Le date
    precedenti al primo cambio disponibile restano NaN, cosi' il backtest
    parte da li' invece di usare un tasso retro-riempito.
    """
    base = base.upper()
    out = prices.copy()
    res = FxResult(prices=out)

    for sym in list(out.columns):
        ccy = (currencies.get(sym) or "").strip()

        # Yahoo quota le listate a Londra in penny: si normalizza a sterline.
        if ccy == "GBp":
            out[sym] = out[sym] / 100.0
            ccy = "GBP"
        ccy = ccy.upper()

        if not ccy:
            res.failed.append(sym)
            out = out.drop(columns=[sym])
            continue
        if ccy == base:
            continue

        rs = rates(ccy, base, start, end)
        if rs is None:
            res.failed.append(sym)
            out = out.drop(columns=[sym])
            continue

        # Solo ffill: nei giorni di chiusura vale l'ultimo cambio pubblicato.
        # Niente bfill, per non inventare tassi prima della prima quotazione.
        aligned = rs.rates.reindex(out.index.union(rs.rates.index)).ffill()
        aligned = aligned.reindex(out.index)

        first_rate = pd.Timestamp(rs.first_available)
        if first_rate > out.index[0]:
            res.truncated[sym] = rs.first_available

        converted_col = out[sym] * aligned
        if converted_col.dropna().empty:
            # Il fondo e' interamente precedente ai cambi disponibili.
            res.failed.append(sym)
            out = out.drop(columns=[sym])
            continue

        out[sym] = converted_col
        res.converted.append(sym)
        res.sources[sym] = rs.source

    res.prices = out
    return res
