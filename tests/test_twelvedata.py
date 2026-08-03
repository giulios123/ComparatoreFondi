import datetime as dt
import os
import tempfile
import unittest
from unittest.mock import patch

from fixtures import FakeResponse

from comparatore.sources.twelvedata import TwelveDataSource


class SearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_cache_dir = os.environ.get("COMPARATORE_CACHE_DIR")
        os.environ["COMPARATORE_CACHE_DIR"] = self.temp_dir.name

    def tearDown(self) -> None:
        if self.previous_cache_dir is None:
            os.environ.pop("COMPARATORE_CACHE_DIR", None)
        else:
            os.environ["COMPARATORE_CACHE_DIR"] = self.previous_cache_dir
        self.temp_dir.cleanup()

    def test_no_query_returns_empty_without_a_network_call(self) -> None:
        with patch("requests.get") as mock_get:
            self.assertEqual(TwelveDataSource(api_key="k").search("  "), [])
        mock_get.assert_not_called()

    def test_no_api_key_returns_empty_without_a_network_call(self) -> None:
        with patch("requests.get") as mock_get:
            self.assertEqual(TwelveDataSource(api_key="").search("vwce"), [])
        mock_get.assert_not_called()

    def test_filters_to_funds(self) -> None:
        payload = {
            "data": [
                {
                    "symbol": "VWCE", "instrument_name": "Vanguard FTSE All-World",
                    "instrument_type": "ETF", "exchange": "XETRA", "currency": "eur",
                },
                {"symbol": "AAPL", "instrument_name": "Apple", "instrument_type": "Common Stock"},
            ]
        }
        with patch("requests.get", return_value=FakeResponse(json_data=payload)):
            out = TwelveDataSource(api_key="k").search("vwce")

        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].symbol, "VWCE")
        self.assertEqual(out[0].currency, "EUR")

    def test_http_error_returns_empty_list(self) -> None:
        with patch("requests.get", return_value=FakeResponse(status_code=500)):
            self.assertEqual(TwelveDataSource(api_key="k").search("vwce"), [])


class PricesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_cache_dir = os.environ.get("COMPARATORE_CACHE_DIR")
        os.environ["COMPARATORE_CACHE_DIR"] = self.temp_dir.name
        self.start = dt.date(2025, 1, 1)
        self.end = dt.date(2025, 1, 5)

    def tearDown(self) -> None:
        if self.previous_cache_dir is None:
            os.environ.pop("COMPARATORE_CACHE_DIR", None)
        else:
            os.environ["COMPARATORE_CACHE_DIR"] = self.previous_cache_dir
        self.temp_dir.cleanup()

    def test_resolves_prices_and_currency(self) -> None:
        payload = {
            "status": "ok",
            "meta": {"currency": "eur"},
            "values": [
                {"datetime": "2025-01-02", "close": "100.0"},
                {"datetime": "2025-01-03", "close": "101.5"},
            ],
        }
        with patch("requests.get", return_value=FakeResponse(json_data=payload)):
            result = TwelveDataSource(api_key="k").prices("VWCE", self.start, self.end)

        self.assertIsNotNone(result)
        self.assertEqual(result.currency, "EUR")
        self.assertEqual(len(result.prices), 2)
        self.assertAlmostEqual(result.prices.iloc[0], 100.0)

    def test_error_status_in_payload_returns_none(self) -> None:
        # Twelve Data risponde 200 anche sugli errori applicativi: lo stato
        # va letto dal corpo, non dallo status HTTP.
        payload = {"status": "error", "message": "simbolo sconosciuto"}
        with patch("requests.get", return_value=FakeResponse(json_data=payload)):
            result = TwelveDataSource(api_key="k").prices("NOPE", self.start, self.end)

        self.assertIsNone(result)

    def test_http_error_returns_none(self) -> None:
        with patch("requests.get", return_value=FakeResponse(status_code=500)):
            result = TwelveDataSource(api_key="k").prices("VWCE", self.start, self.end)

        self.assertIsNone(result)

    def test_no_api_key_returns_none_without_a_network_call(self) -> None:
        with patch("requests.get") as mock_get:
            result = TwelveDataSource(api_key="").prices("VWCE", self.start, self.end)
        self.assertIsNone(result)
        mock_get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
