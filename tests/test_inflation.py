import datetime as dt
import unittest
from unittest import mock

import numpy as np
import pandas as pd

from comparatore import inflation as inf


def payload(unit="I25", values=None):
    values = values or [100.0, 110.0, 121.0]
    return {
        "version": "2.0",
        "class": "dataset",
        "updated": "2026-08-01T10:00:00+0200",
        "id": ["freq", "unit", "coicop18", "geo", "time"],
        "size": [1, 2, 1, 1, len(values)],
        "dimension": {
            "freq": {"category": {"index": {"M": 0}}},
            "unit": {"category": {"index": {"I15": 0, unit: 1}}},
            "coicop18": {"category": {"index": {"TOTAL": 0}}},
            "geo": {"category": {"index": {"IT": 0}}},
            "time": {"category": {"index": {f"2020-{i + 1:02d}": i for i in range(len(values))}}},
        },
        # Indici piatti: l'unita' I25 occupa il secondo blocco di `time`.
        "value": {str(len(values) + i): value for i, value in enumerate(values)},
    }


class Response:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self.body


def cache_entry(series, start=dt.date(2020, 1, 1), end=dt.date(2020, 3, 31), age=0):
    return inf.cache.CacheEntry(
        series=series,
        req_start=start,
        req_end=end,
        fetched_at=dt.datetime.now() - dt.timedelta(hours=age),
    )


class InflationTests(unittest.TestCase):
    def test_parse_selects_latest_index_unit(self):
        result = inf.parse_jsonstat(payload())
        self.assertEqual(result.unit, "I25")
        self.assertEqual(result.series.iloc[-1], 121.0)

    def test_parse_accepts_dense_json_stat_values(self):
        body = payload()
        body["value"] = [None] * 3 + [100.0, 110.0, 121.0]
        result = inf.parse_jsonstat(body, "IT")
        np.testing.assert_allclose(result.series.to_numpy(), [100.0, 110.0, 121.0])

    def test_deflate_curve_uses_first_covered_month_as_base(self):
        idx = pd.to_datetime(["2020-01-15", "2020-02-15", "2020-03-15"])
        nominal = pd.Series([100.0, 110.0, 121.0], index=idx)
        hicp = pd.Series(
            [100.0, 110.0, 121.0],
            index=pd.date_range("2020-01-31", periods=3, freq="ME"),
        )
        real, factors = inf.deflate_curve(nominal, hicp)
        np.testing.assert_allclose(real.to_numpy(), [100.0, 100.0, 100.0])
        np.testing.assert_allclose(factors.to_numpy(), [1.0, 1.1, 1.21])

    def test_fetch_falls_back_to_stale_cache(self):
        with mock.patch("comparatore.inflation.cache.read", return_value=None):
            result = inf.fetch_hicp("XX", dt.date(2020, 1, 1), dt.date(2020, 2, 1))
        self.assertFalse(result.ok)
        self.assertIn("non supportata", result.error)

    def test_fetch_uses_fresh_cache_without_http(self):
        series = pd.Series(
            [100.0, 110.0], index=pd.date_range("2020-01-31", periods=2, freq="ME")
        )
        entry = cache_entry(series)
        with (
            mock.patch("comparatore.inflation.cache.read", return_value=entry),
            mock.patch("comparatore.inflation.cache.read_meta", return_value={"unit": "I25"}),
        ):
            result = inf.fetch_hicp(
                "IT", dt.date(2020, 1, 1), dt.date(2020, 2, 29),
                http_get=mock.Mock(side_effect=AssertionError("rete inattesa")),
            )
        self.assertTrue(result.ok)
        self.assertEqual(len(result.series), 2)

    def test_fetch_refreshes_expired_cache_and_keeps_stale_on_error(self):
        series = pd.Series(
            [100.0, 110.0], index=pd.date_range("2020-01-31", periods=2, freq="ME")
        )
        entry = cache_entry(series, age=48)
        with (
            mock.patch("comparatore.inflation.cache.read", return_value=entry),
            mock.patch("comparatore.inflation.cache.read_meta", return_value={"unit": "I25"}),
        ):
            result = inf.fetch_hicp(
                "IT", dt.date(2020, 1, 1), dt.date(2020, 3, 31),
                http_get=mock.Mock(side_effect=RuntimeError("offline")),
            )
        self.assertTrue(result.stale)
        self.assertIn("offline", result.error)

    def test_fetch_reports_network_error_without_cache(self):
        with mock.patch("comparatore.inflation.cache.read", return_value=None):
            result = inf.fetch_hicp(
                "IT", dt.date(2020, 1, 1), dt.date(2020, 2, 29),
                http_get=mock.Mock(side_effect=RuntimeError("offline")),
            )
        self.assertFalse(result.ok)
        self.assertIn("offline", result.error)

    def test_pac_real_invested_is_flow_by_flow(self):
        idx = pd.date_range("2020-01-31", periods=3, freq="ME")
        nav = pd.Series([100, 110, 121], index=idx)
        invested = pd.Series([100, 200, 300], index=idx)
        hicp = pd.Series([100, 110, 121], index=idx)
        _, real_invested, _ = inf.deflate_pac(
            nav, invested,
            [(idx[0], -100), (idx[1], -100), (idx[2], -100)], hicp,
        )
        np.testing.assert_allclose(real_invested.to_numpy(), [100, 190.91, 273.55], rtol=1e-3)

    def test_pac_keeps_initial_capital_when_hicp_starts_later(self):
        nav_idx = pd.date_range("2020-01-31", periods=3, freq="ME")
        nav = pd.Series([100, 110, 121], index=nav_idx)
        hicp_idx = pd.date_range("2020-02-29", periods=2, freq="ME")
        hicp = pd.Series([110, 121], index=hicp_idx)
        _, real_invested, factors = inf.deflate_pac(
            nav, nav, [(nav_idx[0], -100), (nav_idx[1], -100)], hicp
        )
        np.testing.assert_allclose(factors.to_numpy(), [1.0, 1.1])
        self.assertEqual(real_invested.index[0], nav_idx[1])
        self.assertAlmostEqual(real_invested.iloc[0], 200.0)


if __name__ == "__main__":
    unittest.main()
