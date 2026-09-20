import datetime as dt
import unittest
from unittest.mock import patch

import pandas as pd

from comparatore import fx


class FxRateAtTests(unittest.TestCase):
    def test_prende_ultimo_cambio_precedente_e_ne_conserva_la_data(self):
        series = fx.RateSeries(
            pd.Series(
                [0.88, 0.89],
                index=pd.to_datetime(["2025-01-29", "2025-01-30"]),
            ),
            "ecb",
            dt.date(2025, 1, 29),
        )
        with patch("comparatore.fx.rates", return_value=series) as mocked:
            quote = fx.rate_at("USD", "EUR", dt.date(2025, 1, 31))

        self.assertEqual(quote, fx.FxQuote(0.89, "ecb", dt.date(2025, 1, 30)))
        mocked.assert_called_once_with(
            "USD", "EUR", dt.date(2025, 1, 24), dt.date(2025, 1, 31), use_cache=True
        )

    def test_cambio_mancante_restituisce_none(self):
        with patch("comparatore.fx.rates", return_value=None):
            self.assertIsNone(fx.rate_at("USD", "EUR", dt.date(2025, 1, 31)))


if __name__ == "__main__":
    unittest.main()
