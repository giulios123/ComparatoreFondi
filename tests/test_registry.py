import datetime as dt
import unittest

import pandas as pd

from comparatore.sources.base import PriceSeries
from comparatore.sources.registry import Registry


class _Source:
    def __init__(self, name: str, result: PriceSeries | None = None) -> None:
        self.name = name
        self.result = result
        self.calls = 0

    def available(self) -> bool:
        return True

    def prices(self, *args, **kwargs) -> PriceSeries | None:
        self.calls += 1
        return self.result


def _series(source: str) -> PriceSeries:
    prices = pd.Series([100.0], index=[pd.Timestamp("2025-01-02")])
    return PriceSeries("TEST", prices, "EUR", source)


class RegistryJustEtfTests(unittest.TestCase):
    def setUp(self) -> None:
        self.start = dt.date(2025, 1, 1)
        self.end = dt.date(2025, 1, 3)

    def test_automatic_resolution_skips_justetf_by_default(self) -> None:
        registry = Registry()
        registry.csv = _Source("csv")
        registry.justetf = _Source("justetf", _series("justetf"))
        registry.yahoo = _Source("yahoo", _series("yahoo"))
        registry.eodhd = _Source("eodhd")
        registry.twelvedata = _Source("twelvedata")

        result = registry.resolve(
            "TEST", self.start, self.end, "EUR", isin="IE00B3XXRP09"
        )

        self.assertEqual(result.series.source, "yahoo")
        self.assertEqual(registry.justetf.calls, 0)

    def test_explicit_justetf_selection_is_an_opt_in(self) -> None:
        registry = Registry()
        registry.justetf = _Source("justetf", _series("justetf"))

        result = registry.resolve(
            "TEST",
            self.start,
            self.end,
            "EUR",
            isin="IE00B3XXRP09",
            preferred="justetf",
        )

        self.assertEqual(result.series.source, "justetf")
        self.assertEqual(registry.justetf.calls, 1)

    def test_automatic_resolution_uses_justetf_after_opt_in(self) -> None:
        registry = Registry(enable_justetf=True)
        registry.csv = _Source("csv")
        registry.justetf = _Source("justetf", _series("justetf"))
        registry.yahoo = _Source("yahoo", _series("yahoo"))

        result = registry.resolve(
            "TEST", self.start, self.end, "EUR", isin="IE00B3XXRP09"
        )

        self.assertEqual(result.series.source, "justetf")
        self.assertEqual(registry.justetf.calls, 1)


if __name__ == "__main__":
    unittest.main()