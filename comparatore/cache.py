"""Cache su disco delle serie storiche.

Perche' su disco e non solo `st.cache_data`
-------------------------------------------
La cache di Streamlit vive nel processo: muore a ogni riavvio e non protegge
dal rate-limiting di Yahoo. Con un periodo di default di vent'anni e piu' fondi
in portafoglio, ogni riavvio ripagherebbe l'intero download.

La cache qui e' **accumulativa**: per ogni (fonte, simbolo, valuta) il file
contiene *tutto lo storico mai scaricato*, non la singola finestra richiesta.
Una richiesta piu' larga di quanto gia' in cache allarga il file; una richiesta
contenuta viene servita da disco senza toccare la rete. Chiedere periodi lunghi
diventa quindi progressivamente piu' economico, che e' esattamente il caso d'uso
di questa applicazione.

Accanto a ogni parquet c'e' un sidecar JSON con l'intervallo *richiesto* (non
quello dei dati): senza di esso un fondo nato nel 2012 e interrogato dal 1990
risulterebbe perennemente "non coperto" e verrebbe riscaricato ogni volta.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

DEFAULT_TTL_HOURS = 24

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def cache_dir() -> Path:
    """Directory della cache, sovrascrivibile via COMPARATORE_CACHE_DIR."""
    env = os.environ.get("COMPARATORE_CACHE_DIR")
    base = Path(env) if env else Path(__file__).resolve().parent.parent / ".cache"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _paths(key: str) -> tuple[Path, Path]:
    """File parquet e sidecar JSON per una chiave di cache.

    I simboli contengono caratteri che non possono finire in un nome di file
    (`^GSPC`, `EURUSD=X`, `IE00B3XXRP09`): si normalizza e si aggiunge un hash
    corto della chiave originale per escludere collisioni.
    """
    slug = _SAFE.sub("_", key).strip("_")[:60]
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:8]
    stem = f"{slug}-{digest}"
    d = cache_dir()
    return d / f"{stem}.parquet", d / f"{stem}.json"


@dataclass
class CacheEntry:
    series: pd.Series
    req_start: dt.date  # inizio piu' remoto mai richiesto
    req_end: dt.date  # fine piu' recente mai richiesta
    fetched_at: dt.datetime


def read(key: str) -> CacheEntry | None:
    """Rilegge una voce dalla cache, o None se assente o illeggibile."""
    parquet, meta_path = _paths(key)
    if not parquet.exists() or not meta_path.exists():
        return None
    try:
        meta = json.loads(meta_path.read_text())
        frame = pd.read_parquet(parquet)
        series = frame.iloc[:, 0]
        series.index = pd.DatetimeIndex(series.index)
        return CacheEntry(
            series=series.sort_index(),
            req_start=dt.date.fromisoformat(meta["req_start"]),
            req_end=dt.date.fromisoformat(meta["req_end"]),
            fetched_at=dt.datetime.fromisoformat(meta["fetched_at"]),
        )
    except Exception:
        # Una cache corrotta non deve mai far cadere l'applicazione: si tratta
        # come assente e verra' riscritta al prossimo download.
        return None


def write(key: str, series: pd.Series, req_start: dt.date, req_end: dt.date) -> None:
    """Scrive la serie e i metadati dell'intervallo richiesto."""
    if series is None or series.empty:
        return
    parquet, meta_path = _paths(key)
    try:
        series.sort_index().to_frame(name="value").to_parquet(parquet)
        meta_path.write_text(
            json.dumps(
                {
                    "key": key,
                    "req_start": req_start.isoformat(),
                    "req_end": req_end.isoformat(),
                    "fetched_at": dt.datetime.now().isoformat(timespec="seconds"),
                }
            )
        )
    except Exception:
        # Il disco pieno o di sola lettura degrada la velocita', non la correttezza.
        pass


def get_or_fetch(
    key: str,
    start: dt.date,
    end: dt.date,
    fetch,
    ttl_hours: int = DEFAULT_TTL_HOURS,
) -> pd.Series | None:
    """Serve la finestra [start, end] da cache, scaricando solo se necessario.

    `fetch(start, end) -> pd.Series | None` viene invocata al massimo una volta,
    sempre sull'unione fra quanto richiesto e quanto gia' in cache, cosi' che il
    file cresca invece di essere sostituito.
    """
    entry = read(key)

    if entry is not None:
        covered = entry.req_start <= start and end <= entry.req_end
        age = dt.datetime.now() - entry.fetched_at
        fresh = age < dt.timedelta(hours=ttl_hours)
        if covered and fresh:
            return _slice(entry.series, start, end)

    # Si allarga sempre l'intervallo: la cache non deve mai restringersi.
    fetch_start = min(start, entry.req_start) if entry else start
    fetch_end = max(end, entry.req_end) if entry else end

    try:
        fresh_series = fetch(fetch_start, fetch_end)
    except Exception:
        fresh_series = None

    if fresh_series is None or fresh_series.empty:
        # La rete e' caduta o la fonte non risponde: meglio dati vecchi che
        # nessun dato, purche' coprano quanto chiesto.
        if entry is not None and entry.req_start <= start and end <= entry.req_end:
            return _slice(entry.series, start, end)
        return None

    merged = fresh_series
    if entry is not None and not entry.series.empty:
        # In caso di sovrapposizione vince il dato appena scaricato.
        merged = pd.concat([entry.series, fresh_series])
        merged = merged[~merged.index.duplicated(keep="last")].sort_index()

    write(key, merged, fetch_start, fetch_end)
    return _slice(merged, start, end)


def _slice(series: pd.Series, start: dt.date, end: dt.date) -> pd.Series:
    return series.loc[pd.Timestamp(start) : pd.Timestamp(end)]


# --------------------------------------------------------------------------
# Metadati leggeri (valuta di un simbolo, TER, ...)
# --------------------------------------------------------------------------


def read_meta(key: str) -> dict | None:
    """Rilegge un dizionario di metadati, o None se assente o scaduto."""
    path = cache_dir() / f"meta-{_paths(key)[1].stem}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def write_meta(key: str, value: dict) -> None:
    """Salva un dizionario di metadati accanto alle serie."""
    path = cache_dir() / f"meta-{_paths(key)[1].stem}.json"
    try:
        path.write_text(json.dumps(value))
    except Exception:
        pass


def clear() -> int:
    """Svuota la cache. Restituisce il numero di file rimossi."""
    d = cache_dir()
    n = len(list(d.glob("*.parquet"))) + len(list(d.glob("*.json")))
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True, exist_ok=True)
    return n


def stats() -> tuple[int, float]:
    """Numero di serie in cache e spazio occupato in MB."""
    d = cache_dir()
    files = list(d.glob("*.parquet"))
    size = sum(f.stat().st_size for f in files) / (1024 * 1024)
    return len(files), size
