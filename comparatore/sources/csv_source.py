"""Serie storiche caricate a mano dall'utente.

Perche' serve
-------------
I fondi comuni italiani non quotati non sono coperti da nessuna fonte gratuita:
Yahoo non li ha, justETF tratta solo ETF, e gli endpoint pubblici di
Morningstar non sono piu' raggiungibili senza un browser vero. L'unica strada
che funziona sempre e' lasciar caricare la serie che l'utente ha gia' - estratto
conto della banca, esportazione da Morningstar, foglio della SGR.

Ha priorita' massima nel registry: se l'utente carica un file per un fondo, e'
un'indicazione esplicita e prevale su qualsiasi fonte automatica.

Il parser e' volutamente tollerante sui formati italiani: separatore `;`,
decimale con la virgola, date `GG/MM/AAAA`.
"""

from __future__ import annotations

import datetime as dt
import io
import re

import pandas as pd

from .base import Instrument, PriceSeries


class CsvParseError(ValueError):
    """Il file non e' interpretabile come serie storica."""


def parse_csv(content: bytes | str, *, dayfirst: bool = True) -> pd.Series:
    """Legge una serie data/valore da un CSV.

    Si aspetta due colonne - data e valore - con o senza intestazione.
    Separatore, decimale e formato data vengono riconosciuti da soli.
    """
    if isinstance(content, bytes):
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise CsvParseError("Codifica del file non riconosciuta.")
    else:
        text = content

    frame = _read_any(text)
    if frame is None or frame.shape[1] < 2:
        raise CsvParseError(
            "Servono almeno due colonne: la data e il valore della quota."
        )

    dates_raw = frame.iloc[:, 0]
    values_raw = frame.iloc[:, 1]

    dates = _to_dates(dates_raw, dayfirst=dayfirst)
    values = _to_numeric(values_raw)

    series = pd.Series(values.to_numpy(), index=pd.DatetimeIndex(dates))
    series = series[series.index.notna() & series.notna()]
    if series.empty:
        raise CsvParseError(
            "Nessuna riga valida: controlla il formato delle date e dei numeri."
        )

    series.index = pd.DatetimeIndex(series.index).normalize()
    series = series[~series.index.duplicated(keep="last")].sort_index()
    if len(series) < 2:
        raise CsvParseError("Servono almeno due osservazioni per un backtest.")
    return series.astype(float)


_ISO_DATE = re.compile(r"^\s*\d{4}-\d{1,2}-\d{1,2}")


def _to_dates(col: pd.Series, dayfirst: bool = True) -> pd.Series:
    """Converte in date riconoscendo il formato ISO.

    `dayfirst=True` serve per le date italiane (`02/01/2020` = 2 gennaio), ma
    applicato a una data ISO la ribalta: `2020-01-02` diventerebbe il primo
    febbraio. Si guarda quindi la forma della colonna prima di decidere.
    """
    text = col.astype(str)
    looks_iso = text.str.match(_ISO_DATE).mean() > 0.5
    return pd.to_datetime(
        col, dayfirst=False if looks_iso else dayfirst, errors="coerce"
    )


def _score(frame: pd.DataFrame) -> int:
    """Quante righe hanno una data valida e un numero valido."""
    if frame is None or frame.shape[1] < 2 or frame.empty:
        return 0
    dates = _to_dates(frame.iloc[:, 0])
    values = _to_numeric(frame.iloc[:, 1])
    return int((dates.notna() & values.notna()).sum())


def _read_any(text: str) -> pd.DataFrame | None:
    """Sceglie il separatore che produce piu' righe valide.

    Lo sniffing automatico di pandas non basta: su `02/01/2020;12,34` sceglie la
    virgola e spezza il numero decimale invece del campo. Si provano quindi
    tutti i separatori plausibili e si tiene quello con il punteggio migliore.
    """
    best: pd.DataFrame | None = None
    best_score = 0

    for sep in (";", ",", "\t", r"\s+"):
        try:
            frame = pd.read_csv(
                io.StringIO(text),
                sep=sep,
                header=None,
                engine="python",
                skip_blank_lines=True,
            )
        except Exception:
            continue
        if frame is None or frame.shape[1] < 2 or frame.empty:
            continue

        # La prima riga e' un'intestazione se non contiene una data.
        first = _to_dates(frame.iloc[:1, 0])
        if first.isna().all() and len(frame) > 1:
            frame = frame.iloc[1:].reset_index(drop=True)

        score = _score(frame)
        if score > best_score:
            best, best_score = frame, score

    # Servono almeno due osservazioni utili perche' il file abbia senso.
    return best if best_score >= 2 else None


def _to_numeric(col: pd.Series) -> pd.Series:
    """Converte in numero gestendo la virgola decimale e il punto migliaia."""
    numeric = pd.to_numeric(col, errors="coerce")
    if numeric.notna().sum() >= max(1, int(len(col) * 0.5)):
        return numeric

    cleaned = (
        col.astype(str)
        .str.replace(r"[^\d,.\-]", "", regex=True)
        .str.replace(".", "", regex=False)  # separatore delle migliaia
        .str.replace(",", ".", regex=False)  # decimale italiano
    )
    return pd.to_numeric(cleaned, errors="coerce")


class CsvSource:
    """Fonte alimentata dalle serie caricate dall'utente.

    L'applicazione popola il dizionario `series` (chiave: simbolo o ISIN) e la
    fonte si limita a servirlo; nessuna dipendenza da Streamlit.
    """

    name = "csv"
    label = "CSV caricato"

    def __init__(self) -> None:
        # chiave -> (serie, valuta)
        self.series: dict[str, tuple[pd.Series, str]] = {}

    def add(self, key: str, series: pd.Series, currency: str) -> None:
        self.series[key.strip().upper()] = (series, currency.upper())

    def remove(self, key: str) -> None:
        self.series.pop(key.strip().upper(), None)

    def available(self) -> bool:
        return bool(self.series)

    def search(self, query: str, limit: int = 12, funds_only: bool = True):
        return []

    def metadata(self, symbol: str) -> Instrument | None:
        return None

    def prices(
        self,
        symbol: str,
        start: dt.date,
        end: dt.date,
        base_ccy: str = "",
        isin: str = "",
    ) -> PriceSeries | None:
        for key in (symbol, isin):
            entry = self.series.get((key or "").strip().upper())
            if entry is None:
                continue
            series, currency = entry
            window = series.loc[pd.Timestamp(start) : pd.Timestamp(end)]
            if window.empty:
                continue
            return PriceSeries(
                symbol=symbol or key,
                prices=window,
                currency=currency,
                source=self.name,
                isin=isin,
            )
        return None
