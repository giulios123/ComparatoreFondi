import datetime as dt
import os
import tempfile
import unittest
from unittest.mock import patch

from fixtures import FakeResponse

from comparatore import cache
from comparatore.sources.eodhd import EodhdSource, to_yahoo_symbol


class ToYahooSymbolTests(unittest.TestCase):
    def test_us_listing_drops_the_suffix(self) -> None:
        self.assertEqual(to_yahoo_symbol("REET.US"), "REET")

    def test_xetra_becomes_the_yahoo_de_suffix(self) -> None:
        self.assertEqual(to_yahoo_symbol("VWCE.XETRA"), "VWCE.DE")

    def test_unmapped_exchange_has_no_translation(self) -> None:
        # I fondi comuni non quotati (EUFUND) non hanno un equivalente Yahoo.
        self.assertEqual(to_yahoo_symbol("LU0157178582.EUFUND"), "")

    def test_symbol_without_a_dot_has_no_translation(self) -> None:
        self.assertEqual(to_yahoo_symbol("REET"), "")

    def test_a_symbol_already_in_yahoo_format_is_not_rewritten(self) -> None:
        # "MI" e' sia un codice di borsa EODHD sia gia' il suffisso Yahoo:
        # tradurlo darebbe lo stesso identico simbolo, quindi "" (nessun
        # secondo giro su Yahoo inutile), non un simbolo identico a se' stesso.
        self.assertEqual(to_yahoo_symbol("VWCE.MI"), "")


class FundamentalsBlockedTests(unittest.TestCase):
    """`fundamentals_blocked()` legge un flag che `metadata()` scrive su un 403.

    Si esercita direttamente il contratto con la cache invece di simulare una
    risposta HTTP: e' il flag - non la chiamata di rete che lo produce - a
    dover restare stabile.
    """

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

    def test_unblocked_by_default(self) -> None:
        self.assertFalse(EodhdSource(api_key="x").fundamentals_blocked())

    def test_blocked_after_metadata_records_a_403(self) -> None:
        cache.write_meta("eodhd-fundamentals-blocked", {"bloccato": True})
        self.assertTrue(EodhdSource(api_key="x").fundamentals_blocked())


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
            self.assertEqual(EodhdSource(api_key="k").search("   "), [])
        mock_get.assert_not_called()

    def test_no_api_key_returns_empty_without_a_network_call(self) -> None:
        with patch("requests.get") as mock_get:
            self.assertEqual(EodhdSource(api_key="").search("vwce"), [])
        mock_get.assert_not_called()

    def test_filters_to_funds_and_translates_fields(self) -> None:
        payload = [
            {
                "Code": "VWCE", "Exchange": "XETRA", "Name": "Vanguard FTSE All-World",
                "Type": "ETF", "Currency": "eur", "ISIN": "ie00b3rbwm25",
            },
            {"Code": "AAPL", "Exchange": "US", "Name": "Apple", "Type": "Common Stock"},
        ]
        with patch("requests.get", return_value=FakeResponse(json_data=payload)):
            out = EodhdSource(api_key="k").search("vwce")

        self.assertEqual(len(out), 1)
        hit = out[0]
        self.assertEqual(hit.symbol, "VWCE.XETRA")
        self.assertEqual(hit.currency, "EUR")
        self.assertEqual(hit.isin, "IE00B3RBWM25")

    def test_http_error_returns_empty_list(self) -> None:
        with patch("requests.get", return_value=FakeResponse(status_code=500)):
            self.assertEqual(EodhdSource(api_key="k").search("vwce"), [])

    def test_network_exception_returns_empty_list(self) -> None:
        with patch("requests.get", side_effect=ConnectionError("offline")):
            self.assertEqual(EodhdSource(api_key="k").search("vwce"), [])


class MetadataTests(unittest.TestCase):
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

    def test_extracts_ter_as_a_fraction_and_currency(self) -> None:
        payload = {
            "General": {
                "Name": "Vanguard FTSE All-World", "Type": "ETF",
                "Exchange": "XETRA", "CurrencyCode": "eur", "ISIN": "ie00b3rbwm25",
            },
            "ETF_Data": {"NetExpenseRatio": "0.22"},
        }
        with patch("requests.get", return_value=FakeResponse(json_data=payload)):
            info = EodhdSource(api_key="k").metadata("VWCE.XETRA")

        self.assertIsNotNone(info)
        self.assertAlmostEqual(info.ter, 0.0022)
        self.assertEqual(info.ter_source, "eodhd")
        self.assertEqual(info.currency, "EUR")

    def test_403_sets_the_fundamentals_blocked_flag(self) -> None:
        with patch("requests.get", return_value=FakeResponse(status_code=403)):
            info = EodhdSource(api_key="k").metadata("VWCE.XETRA")

        self.assertIsNone(info)
        self.assertTrue(EodhdSource(api_key="k").fundamentals_blocked())

    def test_http_error_returns_none(self) -> None:
        with patch("requests.get", return_value=FakeResponse(status_code=500)):
            self.assertIsNone(EodhdSource(api_key="k").metadata("VWCE.XETRA"))

    def test_no_api_key_returns_none_without_a_network_call(self) -> None:
        with patch("requests.get") as mock_get:
            self.assertIsNone(EodhdSource(api_key="").metadata("VWCE.XETRA"))
        mock_get.assert_not_called()


class PricesTests(unittest.TestCase):
    """`prices()` incatena fino a due chiamate (`/eod`, poi `/fundamentals`
    per la valuta): il doppio instrada per URL invece di restituire sempre la
    stessa risposta."""

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

    @staticmethod
    def _routed_get(url, params=None, timeout=None, **kwargs):
        if "/eod/" in url:
            return FakeResponse(json_data=[
                {"date": "2025-01-02", "adjusted_close": 100.0},
                {"date": "2025-01-03", "adjusted_close": 101.5},
            ])
        if "/fundamentals/" in url:
            return FakeResponse(json_data={"General": {"CurrencyCode": "eur"}, "ETF_Data": {}})
        raise AssertionError(f"URL non atteso nel test: {url}")

    def test_resolves_prices_and_currency(self) -> None:
        with patch("requests.get", side_effect=self._routed_get):
            result = EodhdSource(api_key="k").prices("VWCE.XETRA", self.start, self.end)

        self.assertIsNotNone(result)
        self.assertEqual(result.currency, "EUR")
        self.assertEqual(result.symbol, "VWCE.XETRA")
        self.assertEqual(len(result.prices), 2)
        self.assertAlmostEqual(result.prices.iloc[0], 100.0)

    def test_no_price_rows_returns_none(self) -> None:
        with patch("requests.get", return_value=FakeResponse(json_data=[])):
            result = EodhdSource(api_key="k").prices("VWCE.XETRA", self.start, self.end)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
