import unittest

import numpy as np
import pandas as pd

from comparatore.engine import Frequency, Holding, Pac, Rebalance, run_backtest
from comparatore.frontier import _batch_metrics, evaluate_weights, search_frontier


def _prices(periods=520):
    index = pd.bdate_range("2020-01-01", periods=periods)
    a = 100.0 * np.cumprod(1.0 + np.full(periods, 0.0003))
    b = 100.0 * np.cumprod(1.0 + np.where(np.arange(periods) % 7 == 0, -0.0002, 0.0001))
    return pd.DataFrame({"A": a, "B": b}, index=index)


class FrontierTests(unittest.TestCase):
    def test_batch_e_engine_coincidono_con_pac_e_ribilanciamento(self):
        prices = _prices()
        pac = Pac(amount=20.0, frequency=Frequency.MONTHLY, step_up=0.02)
        weights = np.asarray([[0.6, 0.4]])
        batch = _batch_metrics(prices, weights, 1000.0, Rebalance.YEARLY, pac, 0.02)
        holdings = [Holding("A", "A", 0.6), Holding("B", "B", 0.4)]
        result = run_backtest(prices, holdings, 1000.0, Rebalance.YEARLY, pac=pac)
        expected_cagr = (result.nav.iloc[-1] / result.nav.iloc[0]) ** (
            365.25 / (result.end - result.start).days
        ) - 1
        self.assertAlmostEqual(batch.iloc[0].cagr, expected_cagr)
        expected_drawdown = -float((result.nav / result.nav.cummax() - 1).min())
        self.assertAlmostEqual(batch.iloc[0].drawdown, expected_drawdown)
        single = evaluate_weights(
            prices, ["A", "B"], 1000.0, Rebalance.YEARLY, pac, 0.02,
            {"A": 0.6, "B": 0.4},
        )
        self.assertAlmostEqual(single.cagr, batch.iloc[0].cagr)
        self.assertAlmostEqual(single.volatility, batch.iloc[0].volatility)

    def test_ricerca_riproducibile_e_con_vincoli(self):
        prices = _prices(300)
        kwargs = dict(
            prices=prices, symbols=["A", "B"], initial_value=1000.0,
            rebalance=Rebalance.NONE, pac=None, risk_free=0.02, sample_count=1000,
            lower={"A": 0.2, "B": 0.1}, upper={"A": 0.8, "B": 0.9},
            current_weights={"A": 0.6, "B": 0.4},
        )
        first = search_frontier(**kwargs)
        second = search_frontier(**kwargs)
        pd.testing.assert_frame_equal(first.weights, second.weights)
        np.testing.assert_allclose(first.weights.sum(axis=1).to_numpy(), 1.0)
        self.assertTrue((first.weights >= 0.2 - 1e-9).all().all())
        self.assertTrue((first.weights <= 0.9 + 1e-9).all().all())
        self.assertIn("cagr_max", first.extrema)
        self.assertGreaterEqual(first.evaluations, 1000)

    def test_limiti_impossibili_vengono_rifiutati(self):
        with self.assertRaises(ValueError):
            search_frontier(
                _prices(20), ["A", "B"], 1000.0, Rebalance.NONE, None, 0.0,
                lower={"A": 0.8, "B": 0.8}, upper={"A": 1.0, "B": 1.0},
                sample_count=1000,
            )

    def test_unica_allocazione_non_inventa_una_frontiera(self):
        prices = pd.DataFrame(
            {"A": [100.0, 101.0, 102.0], "B": [100.0, 100.5, 101.0]},
            index=pd.date_range("2020-01-01", periods=3),
        )
        result = search_frontier(
            prices, ["A", "B"], 1000.0, Rebalance.NONE, None, 0.0,
            lower={"A": 0.6, "B": 0.4}, upper={"A": 0.6, "B": 0.4},
            sample_count=1000,
        )
        self.assertEqual(len(result.weights), 1)
        self.assertEqual(len(result.pareto_ids), 1)


if __name__ == "__main__":
    unittest.main()
