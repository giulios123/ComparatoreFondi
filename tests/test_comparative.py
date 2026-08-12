import unittest

import numpy as np
import pandas as pd

from comparatore import comparative as cp


def curve(values, start="2020-01-31", freq="ME"):
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq=freq))


class ComparativeTests(unittest.TestCase):
    def test_common_period_does_not_backfill(self):
        a = curve([100, 110, 121], "2020-01-31")
        b = curve([200, 220], "2020-02-29")
        common = cp.common_period(a, b)
        self.assertEqual(
            list(common.index), list(pd.date_range("2020-02-29", periods=2, freq="ME"))
        )

    def test_active_metrics_and_tracking_error(self):
        a = curve([100] + [100 * 1.02**i for i in range(1, 25)])
        b = curve([100] + [100 * 1.01**i for i in range(1, 25)])
        result = cp.active_metrics(a, b)
        self.assertAlmostEqual(result.active_return, (0.02 - 0.01) * 12, places=8)
        self.assertTrue(np.isnan(result.tracking_error))
        self.assertTrue(np.isnan(result.information_ratio))
        self.assertEqual(result.reason, "tracking_error_zero")
        self.assertAlmostEqual(result.portfolio_total_return, 1.02**24 - 1, places=8)
        self.assertAlmostEqual(result.benchmark_total_return, 1.01**24 - 1, places=8)
        self.assertAlmostEqual(result.portfolio_max_drawdown, 0.0, places=8)

    def test_insufficient_months_returns_nan_metrics(self):
        result = cp.active_metrics(curve([1, 2]), curve([1, 2]))
        self.assertEqual(result.observations, 1)
        self.assertTrue(np.isnan(result.active_return))
        self.assertEqual(result.reason, "insufficient_observations")

    def test_correlations_use_complete_common_sample(self):
        idx = pd.date_range("2018-01-31", periods=24, freq="ME")
        factors = np.array([1.01, 0.99, 1.02, 1.005] * 6)
        cumulative = np.cumprod(factors)
        frame = pd.DataFrame({"a": cumulative, "b": 200 * cumulative}, index=idx)
        corr = cp.correlation_matrix(frame)
        self.assertAlmostEqual(corr.loc["a", "b"], 1.0)

    def test_rolling_summary(self):
        values = curve([100 * 1.01**i for i in range(25)])
        rolling = cp.rolling_returns(values, windows=(1, 2))[2]
        summary = cp.rolling_summary(rolling)
        self.assertEqual(summary["observations"], 2)
        self.assertGreater(summary["positive_pct"], 0.99)

    def test_rolling_does_not_compress_missing_calendar_months(self):
        idx = pd.to_datetime(
            ["2020-01-31", "2020-02-29", "2020-04-30"]
            + [f"{year}-01-31" for year in range(2021, 2023)]
        )
        values = pd.Series(np.arange(1, len(idx) + 1, dtype=float), index=idx)
        result = cp.rolling_returns(values, windows=(1,))
        self.assertNotIn(pd.Timestamp("2020-04-30"), result[1].index)


if __name__ == "__main__":
    unittest.main()
