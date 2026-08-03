"""Copre solo il confine di rete di `covip.py` (`_fetch_json`/`_fetch_excel`):
sono le uniche due funzioni che parlano con `covip.it`, e quelle rimaste a
0% secondo l'audit. Il parsing dei fogli rendimenti/ISC (`_parse_rendimenti`,
`_parse_isc`, `catalogo()`) resta fuori da questo file - dipende dal layout
esatto delle celle unite di COVIP, servirebbe una fixture molto più grande per
imitarlo fedelmente, e non è dove l'audit segnalava copertura zero.

A differenza delle altre fonti, qui `_fetch_json`/`_fetch_excel` **non**
catturano le proprie eccezioni: chi le chiama (dentro `catalogo()`) lo fa per
ogni singolo file, cosi' che un file mancante non porti giu' l'intero
catalogo. I test riflettono questo: un errore HTTP si propaga, non sparisce.
"""

import io
import unittest
from unittest.mock import patch

import pandas as pd
import requests
from fixtures import FakeResponse

from comparatore import covip


class FetchJsonTests(unittest.TestCase):
    def test_list_payload_is_returned_as_is(self) -> None:
        payload = [{"denominazione": "Fondo Alfa"}, {"denominazione": "Fondo Beta"}]
        with patch("requests.get", return_value=FakeResponse(json_data=payload)):
            self.assertEqual(covip._fetch_json("albo-fondi-pensione-negoziali"), payload)

    def test_dict_payload_returns_the_first_list_value(self) -> None:
        payload = {"metadata": {"count": 2}, "records": [{"a": 1}, {"b": 2}]}
        with patch("requests.get", return_value=FakeResponse(json_data=payload)):
            self.assertEqual(covip._fetch_json("albo-fondi-pensione-aperti"), payload["records"])

    def test_http_error_propagates(self) -> None:
        with patch("requests.get", return_value=FakeResponse(status_code=404)):
            with self.assertRaises(requests.HTTPError):
                covip._fetch_json("nome-inesistente")


class FetchExcelTests(unittest.TestCase):
    @staticmethod
    def _xlsx_bytes(frame: pd.DataFrame) -> bytes:
        buf = io.BytesIO()
        frame.to_excel(buf, sheet_name="Foglio1", header=False, index=False)
        return buf.getvalue()

    def test_reads_the_first_sheet_without_a_header(self) -> None:
        original = pd.DataFrame([["Società", "Fondo", "Albo"], ["Acme", "Fondo Alfa", "123"]])
        with patch(
            "requests.get",
            return_value=FakeResponse(status_code=200, content=self._xlsx_bytes(original)),
        ):
            frame = covip._fetch_excel("rendimenti-negoziali")

        self.assertEqual(frame.shape, original.shape)
        self.assertEqual(frame.iloc[1, 1], "Fondo Alfa")

    def test_http_error_propagates(self) -> None:
        with patch("requests.get", return_value=FakeResponse(status_code=500)):
            with self.assertRaises(requests.HTTPError):
                covip._fetch_excel("rendimenti-negoziali")


if __name__ == "__main__":
    unittest.main()
