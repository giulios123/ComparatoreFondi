import datetime as dt
import unittest

import pandas as pd

from comparatore.sources.base import Instrument, PriceSeries
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


class _MetadataSource:
    def __init__(self, meta: Instrument | None = None) -> None:
        self.meta = meta
        self.name = "stub"

    def available(self) -> bool:
        return self.meta is not None

    def metadata(self, *args, **kwargs) -> Instrument | None:
        return self.meta

    def resolve_symbol(self, symbol: str, isin: str = "") -> str:
        return symbol

    def currency_from_search(self, symbol: str) -> str:
        return ""


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


class RegistryMetadataTests(unittest.TestCase):
    def test_mixed_allocation_keeps_the_original_source_label(self) -> None:
        registry = Registry()
        registry.yahoo = _MetadataSource(
            Instrument(
                symbol="TEST",
                name="Test Fund",
                quote_type="ETF",
                allocation={
                    "classe": {"Azionario": 1.0},
                    "settore": {"Tecnologia": 1.0},
                },
                allocation_source="yahoo",
            )
        )
        registry.eodhd = _MetadataSource(
            Instrument(
                symbol="TEST",
                name="Test Fund",
                quote_type="ETF",
                allocation={"area": {"Globale": 1.0}},
                allocation_source="eodhd",
            )
        )

        info = registry.metadata("TEST")

        self.assertEqual(
            info.allocation,
            {
                "classe": {"Azionario": 1.0},
                "settore": {"Tecnologia": 1.0},
                "area": {"Globale": 1.0},
            },
        )
        self.assertEqual(info.allocation_source, "yahoo")

    def test_metadata_resolution_reports_found_and_unconfigured(self) -> None:
        registry = Registry()
        registry.yahoo = _MetadataSource(
            Instrument("TEST", "Test Fund", "ETF", ter=0.002, ter_source="annual")
        )
        result = registry.metadata_resolution("TEST")
        self.assertEqual(result.attempts[0].outcome, "found")
        self.assertEqual(
            next(attempt for attempt in result.attempts if attempt.source == "eodhd").outcome,
            "not_configured",
        )

    def test_metadata_resolution_uses_opt_in_justetf_before_eodhd(self) -> None:
        registry = Registry(enable_justetf=True)
        registry.yahoo = _MetadataSource(Instrument("TEST", "Test Fund", "ETF"))
        registry.justetf = _MetadataSource(
            Instrument(
                "TEST", "Test Fund", "ETF",
                ter=0.0014, ter_source="justetf", ter_origin="justetf",
            )
        )
        result = registry.metadata_resolution("TEST", "IE00B3XXRP09")
        self.assertEqual(result.instrument.ter_origin, "justetf")
        self.assertEqual(result.attempts[1].outcome, "found")


if __name__ == "__main__":
    unittest.main()
