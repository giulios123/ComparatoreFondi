import datetime as dt
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
from fixtures import FakeResponse

from comparatore import fx


class _CacheAndCurrencyCacheIsolated(unittest.TestCase):
    """Isola sia la cache su disco sia `fx._currencies_cache` (globale di
    modulo, popolato una volta sola per processo): senza il reset una
    `supported_currencies()` vera in un test precedente farebbe leggere agli
    altri un valore gia' in memoria, mai la funzione mockata."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_cache_dir = os.environ.get("COMPARATORE_CACHE_DIR")
        os.environ["COMPARATORE_CACHE_DIR"] = self.temp_dir.name
        self.previous_currencies_cache = fx._currencies_cache
        fx._currencies_cache = None

    def tearDown(self) -> None:
        if self.previous_cache_dir is None:
            os.environ.pop("COMPARATORE_CACHE_DIR", None)
        else:
            os.environ["COMPARATORE_CACHE_DIR"] = self.previous_cache_dir
        self.temp_dir.cleanup()
        fx._currencies_cache = self.previous_currencies_cache


class SupportedCurrenciesTests(_CacheAndCurrencyCacheIsolated):
    def test_parses_and_uppercases_the_list(self) -> None:
        with patch("requests.get", return_value=FakeResponse(json_data=["eur", "usd", "gbp"])):
            self.assertEqual(fx.supported_currencies(), {"EUR", "USD", "GBP"})

    def test_falls_back_to_the_ecb_basket_on_http_error(self) -> None:
        with patch("requests.get", return_value=FakeResponse(status_code=500)):
            out = fx.supported_currencies()
        self.assertEqual(out, fx._FALLBACK_CURRENCIES)

    def test_second_call_uses_the_module_level_cache(self) -> None:
        with patch("requests.get", return_value=FakeResponse(json_data=["eur"])) as mock_get:
            fx.supported_currencies()
            fx.supported_currencies()
        mock_get.assert_called_once()


class EcbRatesTests(_CacheAndCurrencyCacheIsolated):
    def test_parses_daily_rates(self) -> None:
        payload = {"rates": {"2025-01-02": {"USD": 1.08}, "2025-01-03": {"USD": 1.09}}}
        with patch("requests.get", return_value=FakeResponse(json_data=payload)):
            series = fx._ecb_rates("EUR", "USD", dt.date(2025, 1, 2), dt.date(2025, 1, 3))

        self.assertIsNotNone(series)
        self.assertEqual(len(series), 2)
        self.assertAlmostEqual(series.iloc[0], 1.08)

    def test_http_error_returns_none(self) -> None:
        with patch("requests.get", return_value=FakeResponse(status_code=500)):
            series = fx._ecb_rates("EUR", "USD", dt.date(2025, 1, 2), dt.date(2025, 1, 3))
        self.assertIsNone(series)

    def test_window_entirely_before_ecb_start_skips_the_network_call(self) -> None:
        # Prima del 1999-01-04 la BCE non pubblica nulla: il clamp porta
        # `start` oltre `end` e la funzione deve accorgersene da sola.
        with patch("requests.get") as mock_get:
            series = fx._ecb_rates("EUR", "USD", dt.date(1990, 1, 1), dt.date(1995, 1, 1))
        self.assertIsNone(series)
        mock_get.assert_not_called()


class YahooRatesTests(_CacheAndCurrencyCacheIsolated):
    @staticmethod
    def _history(values: dict[str, float]) -> pd.DataFrame:
        return pd.DataFrame(
            {"Close": list(values.values())},
            index=pd.to_datetime(list(values.keys())),
        )

    def test_uses_the_direct_pair_when_available(self) -> None:
        history = self._history({"2025-01-02": 1.08})
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = history
        with patch("yfinance.Ticker", return_value=mock_ticker):
            series = fx._yahoo_rates("EUR", "USD", dt.date(2025, 1, 2), dt.date(2025, 1, 2))

        self.assertIsNotNone(series)
        self.assertAlmostEqual(series.iloc[0], 1.08)

    def test_falls_back_to_the_inverted_pair(self) -> None:
        def _by_symbol(symbol: str) -> MagicMock:
            m = MagicMock()
            if symbol == "USDEUR=X":
                m.history.side_effect = Exception("simbolo inesistente")
            else:
                m.history.return_value = self._history({"2025-01-02": 1.08})
            return m

        with patch("yfinance.Ticker", side_effect=_by_symbol):
            series = fx._yahoo_rates("USD", "EUR", dt.date(2025, 1, 2), dt.date(2025, 1, 2))

        self.assertIsNotNone(series)
        self.assertAlmostEqual(series.iloc[0], 1.0 / 1.08)

    def test_both_symbols_failing_returns_none(self) -> None:
        with patch("yfinance.Ticker", side_effect=Exception("offline")):
            series = fx._yahoo_rates("USD", "EUR", dt.date(2025, 1, 2), dt.date(2025, 1, 2))
        self.assertIsNone(series)


class RatesOrchestrationTests(_CacheAndCurrencyCacheIsolated):
    """`rates()` sceglie la fonte e ripiega su Yahoo se la BCE non risponde:
    si mockano `_ecb_rates`/`_yahoo_rates` direttamente, non l'HTTP sotto -
    quella parte e' gia' coperta da `EcbRatesTests`/`YahooRatesTests`."""

    def test_identical_currencies_return_a_constant_series_without_fetching(self) -> None:
        with patch("comparatore.fx._ecb_rates") as mock_ecb:
            rs = fx.rates("EUR", "EUR", dt.date(2025, 1, 1), dt.date(2025, 1, 3))
        self.assertEqual(rs.source, "identita")
        self.assertTrue((rs.rates == 1.0).all())
        mock_ecb.assert_not_called()

    def test_supported_pair_uses_the_ecb(self) -> None:
        series = pd.Series([1.08], index=[pd.Timestamp("2025-01-02")])
        with (
            patch("comparatore.fx.supported_currencies", return_value={"EUR", "USD"}),
            patch("comparatore.fx._ecb_rates", return_value=series) as mock_ecb,
            patch("comparatore.fx._yahoo_rates") as mock_yahoo,
        ):
            rs = fx.rates("EUR", "USD", dt.date(2025, 1, 2), dt.date(2025, 1, 2))

        self.assertEqual(rs.source, "ecb")
        mock_ecb.assert_called_once()
        mock_yahoo.assert_not_called()

    def test_ecb_pair_falls_back_to_yahoo_when_the_ecb_call_fails(self) -> None:
        series = pd.Series([1.08], index=[pd.Timestamp("2025-01-02")])
        with (
            patch("comparatore.fx.supported_currencies", return_value={"EUR", "USD"}),
            patch("comparatore.fx._ecb_rates", return_value=None),
            patch("comparatore.fx._yahoo_rates", return_value=series) as mock_yahoo,
        ):
            rs = fx.rates("EUR", "USD", dt.date(2025, 1, 2), dt.date(2025, 1, 2))

        self.assertEqual(rs.source, "yahoo")
        mock_yahoo.assert_called()

    def test_unsupported_pair_goes_straight_to_yahoo(self) -> None:
        series = pd.Series([21.5], index=[pd.Timestamp("2025-01-02")])
        with (
            patch("comparatore.fx.supported_currencies", return_value={"EUR", "USD"}),
            patch("comparatore.fx._ecb_rates") as mock_ecb,
            patch("comparatore.fx._yahoo_rates", return_value=series),
        ):
            rs = fx.rates("EUR", "ZAR", dt.date(2025, 1, 2), dt.date(2025, 1, 2))

        self.assertEqual(rs.source, "yahoo")
        mock_ecb.assert_not_called()


class ConvertCurrencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.idx = pd.date_range("2025-01-01", periods=3, freq="D")
        self.prices = pd.DataFrame({"FUND_USD": [100.0, 101.0, 102.0]}, index=self.idx)

    def test_converts_a_column_using_the_daily_rate(self) -> None:
        rate_series = pd.Series(2.0, index=self.idx)
        with patch(
            "comparatore.fx.rates",
            return_value=fx.RateSeries(rate_series, "ecb", self.idx[0].date()),
        ):
            res = fx.convert_currency(
                self.prices, {"FUND_USD": "USD"}, "EUR", self.idx[0].date(), self.idx[-1].date()
            )

        self.assertIn("FUND_USD", res.converted)
        self.assertEqual(list(res.prices["FUND_USD"]), [200.0, 202.0, 204.0])

    def test_gbp_pence_are_normalised_before_conversion(self) -> None:
        prices = pd.DataFrame({"FUND_GB": [10000.0, 10100.0, 10200.0]}, index=self.idx)
        rate_series = pd.Series(1.0, index=self.idx)
        with patch(
            "comparatore.fx.rates",
            return_value=fx.RateSeries(rate_series, "ecb", self.idx[0].date()),
        ):
            res = fx.convert_currency(
                prices, {"FUND_GB": "GBp"}, "GBP", self.idx[0].date(), self.idx[-1].date()
            )

        # 10000 pence / 100 = 100 sterline, poi moltiplicato per il cambio 1:1.
        self.assertAlmostEqual(res.prices["FUND_GB"].iloc[0], 100.0)

    def test_missing_currency_drops_the_column_and_is_reported_as_failed(self) -> None:
        res = fx.convert_currency(
            self.prices, {}, "EUR", self.idx[0].date(), self.idx[-1].date()
        )
        self.assertEqual(res.failed, ["FUND_USD"])
        self.assertNotIn("FUND_USD", res.prices.columns)

    def test_unresolvable_rate_drops_the_column_and_is_reported_as_failed(self) -> None:
        with patch("comparatore.fx.rates", return_value=None):
            res = fx.convert_currency(
                self.prices, {"FUND_USD": "USD"}, "EUR", self.idx[0].date(), self.idx[-1].date()
            )
        self.assertEqual(res.failed, ["FUND_USD"])
        self.assertNotIn("FUND_USD", res.prices.columns)


if __name__ == "__main__":
    unittest.main()
