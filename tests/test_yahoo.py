import datetime as dt
import os
import tempfile
import unittest
from unittest.mock import PropertyMock, patch

import pandas as pd

from comparatore import cache
from comparatore.sources.yahoo import YahooSource


class _CacheIsolated(unittest.TestCase):
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


class SearchTests(unittest.TestCase):
    def test_no_query_returns_empty_without_a_network_call(self) -> None:
        with patch("yfinance.Search") as mock_search:
            self.assertEqual(YahooSource().search("   "), [])
        mock_search.assert_not_called()

    def test_filters_to_funds_by_default(self) -> None:
        with patch("yfinance.Search") as mock_search:
            mock_search.return_value.quotes = [
                {
                    "quoteType": "ETF", "symbol": "VWCE.DE",
                    "longname": "Vanguard FTSE All-World", "exchDisp": "XETRA",
                },
                {"quoteType": "EQUITY", "symbol": "AAPL", "shortname": "Apple"},
            ]
            out = YahooSource().search("vwce")

        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].symbol, "VWCE.DE")
        self.assertEqual(out[0].exchange, "XETRA")

    def test_funds_only_false_keeps_equities_too(self) -> None:
        with patch("yfinance.Search") as mock_search:
            mock_search.return_value.quotes = [
                {"quoteType": "EQUITY", "symbol": "AAPL", "shortname": "Apple"},
            ]
            out = YahooSource().search("apple", funds_only=False)

        self.assertEqual(len(out), 1)

    def test_exception_returns_empty_list(self) -> None:
        with patch("yfinance.Search", side_effect=Exception("offline")):
            self.assertEqual(YahooSource().search("vwce"), [])


class MetadataTests(unittest.TestCase):
    def test_prefers_annual_report_expense_ratio_over_net_expense_ratio(self) -> None:
        with patch("yfinance.Ticker") as mock_ticker_cls:
            instance = mock_ticker_cls.return_value
            instance.info = {
                "longName": "Vanguard FTSE All-World", "currency": "EUR",
                "quoteType": "ETF", "fullExchangeName": "XETRA",
                "annualReportExpenseRatio": 0.0022, "netExpenseRatio": 99,
            }
            instance.funds_data.asset_classes = {}
            instance.funds_data.sector_weightings = {}
            instance.funds_data.top_holdings = pd.DataFrame()

            info = YahooSource().metadata("VWCE.DE")

        self.assertAlmostEqual(info.ter, 0.0022)
        self.assertEqual(info.ter_source, "annualReportExpenseRatio")
        self.assertEqual(info.currency, "EUR")

    def test_net_expense_ratio_is_read_as_a_percentage(self) -> None:
        with patch("yfinance.Ticker") as mock_ticker_cls:
            instance = mock_ticker_cls.return_value
            instance.info = {"quoteType": "EQUITY", "netExpenseRatio": 0.74}
            info = YahooSource().metadata("AAPL")

        self.assertAlmostEqual(info.ter, 0.0074)
        self.assertEqual(info.ter_source, "netExpenseRatio")

    def test_non_fund_quote_type_skips_the_composition_call(self) -> None:
        with patch("yfinance.Ticker") as mock_ticker_cls:
            instance = mock_ticker_cls.return_value
            instance.info = {"quoteType": "EQUITY", "currency": "USD"}
            info = YahooSource().metadata("AAPL")

        self.assertEqual(info.allocation, {})
        self.assertEqual(info.holdings, [])

    def test_currency_falls_back_to_history_metadata(self) -> None:
        with patch("yfinance.Ticker") as mock_ticker_cls:
            instance = mock_ticker_cls.return_value
            instance.info = {"quoteType": "EQUITY"}
            instance.history_metadata = {"currency": "USD"}
            info = YahooSource().metadata("AAPL")

        self.assertEqual(info.currency, "USD")

    def test_info_lookup_failure_still_returns_an_instrument(self) -> None:
        with patch("yfinance.Ticker") as mock_ticker_cls:
            instance = mock_ticker_cls.return_value
            type(instance).info = PropertyMock(side_effect=Exception("offline"))
            instance.history_metadata = {}
            info = YahooSource().metadata("AAPL")

        self.assertEqual(info.symbol, "AAPL")
        self.assertEqual(info.name, "AAPL")


class PricesTests(_CacheIsolated):
    def setUp(self) -> None:
        super().setUp()
        self.start = dt.date(2025, 1, 2)
        self.end = dt.date(2025, 1, 3)

    def test_resolves_prices_and_currency(self) -> None:
        history = pd.DataFrame(
            {"Close": [100.0, 101.0]},
            index=pd.to_datetime(["2025-01-02", "2025-01-03"]),
        )
        with patch("yfinance.Ticker") as mock_ticker_cls:
            instance = mock_ticker_cls.return_value
            instance.history.return_value = history
            instance.history_metadata = {"currency": "EUR"}

            result = YahooSource().prices("VWCE.DE", self.start, self.end)

        self.assertIsNotNone(result)
        self.assertEqual(result.currency, "EUR")
        self.assertEqual(len(result.prices), 2)

    def test_empty_history_returns_none(self) -> None:
        with patch("yfinance.Ticker") as mock_ticker_cls:
            mock_ticker_cls.return_value.history.return_value = pd.DataFrame()
            result = YahooSource().prices("VWCE.DE", self.start, self.end)
        self.assertIsNone(result)

    def test_history_exception_returns_none(self) -> None:
        with patch("yfinance.Ticker") as mock_ticker_cls:
            mock_ticker_cls.return_value.history.side_effect = Exception("offline")
            result = YahooSource().prices("VWCE.DE", self.start, self.end)
        self.assertIsNone(result)


class CurrencyOfTests(_CacheIsolated):
    def test_cache_hit_skips_the_network_call(self) -> None:
        cache.write_meta("yahoo-ccy/VWCE.DE", {"currency": "EUR"})

        with patch("yfinance.Ticker") as mock_ticker_cls:
            currency = YahooSource.currency_of("VWCE.DE")

        self.assertEqual(currency, "EUR")
        mock_ticker_cls.assert_not_called()

    def test_cache_miss_fetches_and_stores_the_currency(self) -> None:
        with patch("yfinance.Ticker") as mock_ticker_cls:
            mock_ticker_cls.return_value.history_metadata = {"currency": "GBP"}
            currency = YahooSource.currency_of("VOD.L")

        self.assertEqual(currency, "GBP")
        self.assertEqual(cache.read_meta("yahoo-ccy/VOD.L", 3650), {"currency": "GBP"})


if __name__ == "__main__":
    unittest.main()
