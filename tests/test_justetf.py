import datetime as dt
import os
import tempfile
import unittest
from unittest.mock import patch

from fixtures import FakeResponse

from comparatore.sources.justetf import JustEtfSource

ISIN = "IE00B3RBWM25"


class PricesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_cache_dir = os.environ.get("COMPARATORE_CACHE_DIR")
        os.environ["COMPARATORE_CACHE_DIR"] = self.temp_dir.name
        # Giovedi'/venerdi': niente filtro dei giorni feriali a confondere l'attesa.
        self.start = dt.date(2025, 1, 2)
        self.end = dt.date(2025, 1, 3)

    def tearDown(self) -> None:
        if self.previous_cache_dir is None:
            os.environ.pop("COMPARATORE_CACHE_DIR", None)
        else:
            os.environ["COMPARATORE_CACHE_DIR"] = self.previous_cache_dir
        self.temp_dir.cleanup()

    def test_non_isin_returns_none_without_a_network_call(self) -> None:
        with patch("requests.get") as mock_get:
            result = JustEtfSource().prices("VWCE", self.start, self.end, isin="")
        self.assertIsNone(result)
        mock_get.assert_not_called()

    def test_resolves_prices_in_the_requested_currency(self) -> None:
        payload = {
            "series": [
                {"date": "2025-01-02", "value": {"raw": 100.0}},
                {"date": "2025-01-03", "value": {"raw": 101.5}},
            ]
        }
        with patch("requests.get", return_value=FakeResponse(status_code=200, json_data=payload)):
            result = JustEtfSource().prices(
                "VWCE", self.start, self.end, base_ccy="eur", isin=ISIN
            )

        self.assertIsNotNone(result)
        self.assertEqual(result.currency, "EUR")
        self.assertEqual(result.isin, ISIN)
        self.assertEqual(len(result.prices), 2)

    def test_404_returns_none(self) -> None:
        with patch(
            "requests.get",
            return_value=FakeResponse(status_code=404, content=b""),
        ):
            result = JustEtfSource().prices("VWCE", self.start, self.end, isin=ISIN)
        self.assertIsNone(result)

    def test_empty_body_returns_none(self) -> None:
        # ISIN esistente ma non un ETF: 200 con corpo vuoto.
        with patch(
            "requests.get",
            return_value=FakeResponse(status_code=200, content=b"   "),
        ):
            result = JustEtfSource().prices("VWCE", self.start, self.end, isin=ISIN)
        self.assertIsNone(result)

    def test_network_exception_returns_none(self) -> None:
        with patch("requests.get", side_effect=ConnectionError("offline")):
            result = JustEtfSource().prices("VWCE", self.start, self.end, isin=ISIN)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
