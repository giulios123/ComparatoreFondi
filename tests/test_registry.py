import datetime as dt
import unittest

import pandas as pd

from comparatore.instrument_facts import InstrumentFacts, RelatedQuote, candidate
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

    def test_opt_in_justetf_enriches_and_replaces_yahoo_ter(self) -> None:
        registry = Registry(enable_justetf=True)
        registry.yahoo = _MetadataSource(
            Instrument("TEST", "Test Fund", "ETF", ter=0.001)
        )
        registry.justetf = _MetadataSource(
            Instrument(
                "TEST", "Test Fund", "ETF",
                ter=0.0017, ter_source="justetf", ter_origin="justetf",
                distribution_policy="accumulating", replication_method="physical",
            )
        )

        info = registry.metadata("TEST", "IE00B3XXRP09")

        self.assertEqual(info.ter, 0.0017)
        self.assertEqual(info.ter_origin, "justetf")
        self.assertEqual(info.distribution_policy, "accumulating")
        self.assertEqual(info.replication_method, "physical")

    def test_complete_resolution_exposes_facts_and_related_quotes(self) -> None:
        registry = Registry()
        registry.yahoo = _MetadataSource(Instrument(
            "TEST", "Test Fund", "ETF", isin="IE00B3XXRP09",
            facts=InstrumentFacts.merge({
                "issuer": [candidate("Example issuer", "yahoo", acquired_at="2026-08-14")],
            }),
        ))
        registry.related_quotes = lambda isin, active_symbol="": [  # type: ignore[method-assign]
            RelatedQuote("TEST.DE", "XETRA", "EUR", "openfigi", isin)
        ]

        result = registry.metadata_resolution("TEST", complete=True)

        self.assertEqual(result.facts.values["issuer"].value, "Example issuer")
        self.assertEqual(result.related_quotes[0].symbol, "TEST.DE")

    def test_related_quotes_require_the_same_validated_isin_and_keep_active_quote(self) -> None:
        registry = Registry()
        registry.search = lambda *args, **kwargs: [  # type: ignore[method-assign]
            Instrument("TEST.DE", "Test Fund", "ETF", isin="IE00B3XXRP09", exchange="XETRA"),
            Instrument("TEST.AS", "Test Fund", "ETF", isin="IE00B3XXRP09", exchange="AMS"),
            Instrument("TEST.MI", "Test Fund", "ETF", isin="IE00OTHER000", exchange="MI"),
            Instrument("TEST.L", "Test Fund", "ETF", exchange="LSE"),
        ]

        quotes = registry.related_quotes("IE00B3XXRP09", active_symbol="TEST.DE")

        self.assertEqual([quote.symbol for quote in quotes], ["TEST.AS"])


if __name__ == "__main__":
    unittest.main()
