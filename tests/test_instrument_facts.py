import datetime as dt
import unittest

from comparatore.instrument_facts import (
    InstrumentFacts,
    RelatedQuote,
    candidate,
)


class InstrumentFactsTests(unittest.TestCase):
    def test_candidate_normalizes_dates_and_non_finite_numbers(self) -> None:
        fact = candidate(
            {"amount": float("nan"), "as_of": dt.date(2026, 8, 14)},
            "YAHOO",
            observed_at=dt.datetime(2026, 8, 13, 12, 30),
            acquired_at=dt.datetime(2026, 8, 14, 9, 10),
        )

        self.assertEqual(fact.source, "yahoo")
        self.assertEqual(fact.observed_at, "2026-08-13")
        self.assertEqual(fact.acquired_at, "2026-08-14T09:10:00")
        self.assertEqual(fact.value, {"amount": None, "as_of": "2026-08-14"})

    def test_ter_priority_and_conflict_are_explicit(self) -> None:
        facts = InstrumentFacts.merge({
            "ter": [
                candidate(0.002, "yahoo", acquired_at="2026-08-14"),
                candidate(0.0014, "justetf", acquired_at="2026-08-14"),
                candidate(0.001, "eodhd", acquired_at="2026-08-14"),
            ]
        })

        self.assertEqual(facts.values["ter"].source, "justetf")
        self.assertEqual([item.source for item in facts.alternatives["ter"]], ["yahoo", "eodhd"])

    def test_manual_value_wins_over_automatic_and_latest_local_wins(self) -> None:
        facts = InstrumentFacts.merge({
            "ter": [
                candidate(0.002, "yahoo", acquired_at="2026-08-14T08:00:00"),
                candidate(0.001, "manual", acquired_at="2026-08-14T09:00:00"),
                candidate(0.0015, "kid", acquired_at="2026-08-14T10:00:00"),
            ]
        })

        self.assertEqual(facts.values["ter"].source, "kid")
        self.assertEqual(facts.values["ter"].value, 0.0015)
        self.assertEqual(
            {item.source for item in facts.alternatives["ter"]},
            {"manual", "yahoo"},
        )

    def test_equal_values_are_not_reported_as_conflicts(self) -> None:
        facts = InstrumentFacts.merge({
            "issuer": [
                candidate("Vanguard", "yahoo"),
                candidate(" vanguard ", "eodhd"),
            ]
        })

        self.assertNotIn("issuer", facts.alternatives)

    def test_empty_candidates_are_ignored_and_numeric_equivalence_is_stable(self) -> None:
        facts = InstrumentFacts.merge({
            "aum": [
                candidate("", "yahoo"),
                candidate(100, "eodhd"),
                candidate(100.0, "justetf"),
            ]
        })

        self.assertEqual(facts.values["aum"].value, 100.0)
        self.assertNotIn("aum", facts.alternatives)

    def test_related_quotes_are_deduplicated(self) -> None:
        facts = InstrumentFacts.merge({}, [
            RelatedQuote("VWCE.MI", "MI", "EUR", "openfigi", "IE00BK5BQT80"),
            RelatedQuote("VWCE.MI", "MI", "EUR", "eodhd", "IE00BK5BQT80"),
            RelatedQuote("VWCE.DE", "XETRA", "EUR", "openfigi", "IE00BK5BQT80"),
        ])

        self.assertEqual([quote.symbol for quote in facts.related_quotes], ["VWCE.MI", "VWCE.DE"])

    def test_malformed_payload_degrades_to_empty(self) -> None:
        facts = InstrumentFacts.from_dict({
            "values": {"ter": {"value": 0.002}},
            "alternatives": {"issuer": "not-a-list"},
            "related_quotes": [{"exchange": "MI"}],
        })

        self.assertEqual(facts.values, {})
        self.assertEqual(facts.alternatives, {})
        self.assertEqual(facts.related_quotes, [])


if __name__ == "__main__":
    unittest.main()
