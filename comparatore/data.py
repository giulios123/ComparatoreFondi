"""Facciata sulle fonti dati e sulla conversione valutaria.

Questo modulo era l'implementazione Yahoo dell'applicazione. Ora che le fonti
sono piu' d'una, l'implementazione vive in `comparatore.sources` e i cambi in
`comparatore.fx`; qui restano i nomi storici, perche' erano l'interfaccia
pubblica del pacchetto e continuano a funzionare identici per chi li usa da
script.

Per il codice nuovo conviene passare direttamente da `sources.Registry`, che
sceglie la fonte e sa dire quale ha risposto.
"""

from __future__ import annotations

from .fx import FxResult, convert_currency
from .sources.base import Instrument, is_isin
from .sources.yahoo import FUND_TYPES, get_metadata, get_prices, search

__all__ = [
    "FUND_TYPES",
    "FxResult",
    "Instrument",
    "convert_currency",
    "get_metadata",
    "get_prices",
    "is_isin",
    "search",
]
