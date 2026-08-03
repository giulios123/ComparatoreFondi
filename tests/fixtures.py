"""Doppi minimi per le chiamate di rete nei test delle fonti dati.

Nessuna libreria di mock in più (niente `responses`/`requests-mock`: non sono
fra le dipendenze, e `unittest.mock` della standard library basta). `requests`
si sostituisce con `unittest.mock.patch("requests.get", ...)` (o `.post`)
restituendo una `FakeResponse`; `yfinance` si sostituisce allo stesso modo
patchando `yfinance.Search`/`yfinance.Ticker` - ogni fonte fa `import
yfinance as yf` e poi `yf.Search(...)`/`yf.Ticker(...)`, quindi patchare
l'attributo sul modulo vero (non sul nome importato in ciascun modulo di fonte)
basta: `yf` è lo stesso oggetto modulo ovunque.

Non un file `test_*.py`: `unittest discover -p "test_*.py"` lo ignora, quindi
può contenere solo doppi da importare, non test da eseguire da soli.
"""

from __future__ import annotations

import json as _json

import requests


class FakeResponse:
    """Sostituto minimo di `requests.Response` per i test offline.

    Copre solo cio' che le fonti usano davvero: `status_code`, `.json()`,
    `.raise_for_status()`, `.content`/`.text`. Come nella `Response` vera,
    `.content` e' la fonte: se non e' passato esplicitamente ma c'e'
    `json_data`, si deriva serializzandolo - altrimenti un controllo su
    `.content` fatto *prima* di `.json()` (giustetf.py lo fa) vedrebbe sempre
    un corpo vuoto anche quando il JSON e' configurato.
    """

    def __init__(
        self,
        *,
        status_code: int = 200,
        json_data=None,
        content: bytes = b"",
        text: str = "",
    ) -> None:
        self.status_code = status_code
        self._json_data = json_data
        if content:
            self.content = content
        elif text:
            self.content = text.encode("utf-8")
        elif json_data is not None:
            self.content = _json.dumps(json_data).encode("utf-8")
        else:
            self.content = b""
        self.text = text or self.content.decode("utf-8", errors="replace")

    def json(self):
        if self._json_data is None:
            raise ValueError("FakeResponse senza json_data configurato")
        return self._json_data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} errore finto", response=self)
