import datetime as dt
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from comparatore import benchmark_portfolios as bp
from comparatore import fx
from comparatore.engine import Frequency, Pac, Rebalance, simulate


class TestBenchmarkCatalog(unittest.TestCase):
    def test_catalogo_esatto_e_pesi(self):
        self.assertEqual(len(bp.PORTFOLIO_CATALOG), 25)
        self.assertEqual(len(set(bp.PORTFOLIO_IDS)), 25)
        self.assertEqual(bp.PORTFOLIO_IDS[5], "golden_butterfly")
        for definition in bp.PORTFOLIO_CATALOG:
            self.assertAlmostEqual(sum(x.weight for x in definition.canonical), 100)
            self.assertAlmostEqual(sum(x.weight for x in definition.executable), 100)
            self.assertTrue(definition.source_url.startswith("https://"))
            self.assertTrue(all(x.source_url.startswith("https://") for x in definition.executable))
            self.assertIn(definition.kind, {"composite", "managed"})

    def test_allocazioni_canoniche_bloccate(self):
        expected = {
            "golden_butterfly": {"US-L": 20, "US-SV": 20, "UST-L": 20, "UST-S": 20, "GOLD": 20},
            "dragon": {"US-L": 24, "UST-I": 18, "GOLD": 19, "KMLM": 18, "CAOS": 21},
            "gone_fishin": {"US-T": 15, "US-S": 15, "EU": 10, "PAC": 10, "EM": 10,
                            "US-AGG": 10, "HY": 10, "TIPS": 10, "REIT": 5, "GOLD": 5},
        }
        for portfolio_id, allocation in expected.items():
            definition = bp.get_portfolio(portfolio_id)
            self.assertIsNotNone(definition)
            self.assertEqual(
                {item.sleeve: item.weight for item in definition.canonical}, allocation
            )

    def test_duplicati_eseguibili_vengono_fusi(self):
        definition = bp.get_portfolio("gone_fishin")
        weights = bp.executable_weights(definition)
        self.assertAlmostEqual(weights["SXR8.DE"], 12.75)
        self.assertAlmostEqual(weights["ZPRR.DE"], 17.25)
        self.assertAlmostEqual(sum(weights.values()), 100)

    def test_catalogo_unknown(self):
        self.assertIsNone(bp.get_portfolio("not-a-portfolio"))


class TestBenchmarkSimulation(unittest.TestCase):
    def test_conversione_valutaria_senza_backfill(self):
        index = pd.DatetimeIndex(["2024-01-02", "2024-01-03"])
        prices = pd.DataFrame({"USD": [100.0, 110.0]}, index=index)
        rates = fx.RateSeries(
            pd.Series([1.1, 1.1], index=index), "synthetic", dt.date(2024, 1, 2)
        )
        with patch("comparatore.fx.rates", return_value=rates):
            converted = fx.convert_currency(
                prices, {"USD": "USD"}, "EUR", dt.date(2024, 1, 2), dt.date(2024, 1, 3)
            )
        self.assertEqual(converted.failed, [])
        self.assertEqual(len(converted.prices["USD"]), 2)
        self.assertAlmostEqual(converted.prices["USD"].iloc[0], 110.0)
        self.assertAlmostEqual(converted.prices["USD"].iloc[1], 121.0)

    def test_ribilanciamento_annuale_al_primo_giorno(self):
        index = pd.DatetimeIndex([
            "2024-01-02", "2024-06-03", "2025-01-02", "2025-06-03"
        ])
        prices = pd.DataFrame({
            "A": [100, 200, 200, 200],
            "B": [100, 100, 100, 200],
        }, index=index, dtype=float)
        value, sleeves = simulate(prices, {"A": 50, "B": 50}, 1000, Rebalance.YEARLY)
        self.assertAlmostEqual(value.iloc[1], 1500)
        # Il primo giorno del 2025 riporta entrambe le sleeve a 50/50.
        self.assertAlmostEqual(sleeves.loc[index[2], "A"], 750)
        self.assertAlmostEqual(sleeves.loc[index[2], "B"], 750)

    def test_pac_con_stesso_capitale_e_calendario(self):
        index = pd.date_range("2024-01-02", periods=4, freq="MS")
        prices = pd.DataFrame({"A": np.arange(100, 104, dtype=float)}, index=index)
        pac = Pac(amount=100, frequency=Frequency.MONTHLY, start=dt.date(2024, 2, 1))
        value, _ = simulate(prices, {"A": 100}, 1000, Rebalance.YEARLY, pac)
        self.assertGreater(value.iloc[-1], value.iloc[0] + 300)


if __name__ == "__main__":
    unittest.main()
