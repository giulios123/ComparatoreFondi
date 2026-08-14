import datetime as dt
import json
import unittest

from comparatore.overlap import (
    FundHoldings,
    HoldingPosition,
    analyze_overlap,
)


class TestOverlap(unittest.TestCase):
    def test_pairwise_non_renormalized_and_coverage(self):
        report = analyze_overlap([
            FundHoldings("a", (
                HoldingPosition(0.4, symbol="AAA"), HoldingPosition(0.2, symbol="BBB"),
            ), 0.5),
            FundHoldings("b", (
                HoldingPosition(0.1, symbol="AAA"), HoldingPosition(0.3, symbol="CCC"),
            ), 0.5),
        ])
        pair = report.pair("a", "b")
        self.assertIsNotNone(pair)
        self.assertAlmostEqual(pair.overlap, 0.1)
        self.assertAlmostEqual(pair.coverage_a, 0.6)
        self.assertAlmostEqual(pair.coverage_b, 0.4)
        self.assertTrue(pair.lower_bound)

    def test_missing_holdings_is_not_zero(self):
        report = analyze_overlap([
            FundHoldings("a", ()),
            FundHoldings("b", (HoldingPosition(1.0, symbol="AAA"),)),
        ])
        self.assertIsNone(report.pair("a", "b").overlap)
        self.assertEqual(report.coverage["a"].reason, "no_holdings")

    def test_duplicate_symbol_is_summed_and_over_100_is_invalid(self):
        good = analyze_overlap([FundHoldings("a", (
            HoldingPosition(0.2, symbol="AAA"), HoldingPosition(0.3, symbol="AAA"),
        ))])
        self.assertAlmostEqual(good.coverage["a"].coverage, 0.5)
        bad = analyze_overlap([FundHoldings("a", (
            HoldingPosition(0.7, symbol="AAA"), HoldingPosition(0.4, symbol="AAA"),
        ))])
        self.assertFalse(bad.coverage["a"].valid)
        self.assertEqual(bad.coverage["a"].reason, "coverage_over_100")

    def test_name_collision_is_ambiguous(self):
        report = analyze_overlap([
            FundHoldings("a", (HoldingPosition(0.5, symbol="AAA", name="Acme"),)),
            FundHoldings("b", (HoldingPosition(0.5, symbol="BBB", name="Acme"),)),
        ])
        pair = report.pair("a", "b")
        self.assertEqual(pair.overlap, 0.0)
        self.assertGreater(pair.ambiguous_count, 0)

    def test_weights_are_normalized_and_unknown_is_exposed(self):
        report = analyze_overlap([
            FundHoldings("a", (HoldingPosition(0.5, symbol="AAA"),), 80),
            FundHoldings("b", (HoldingPosition(1.0, symbol="BBB"),), 20),
        ])
        self.assertAlmostEqual(report.exposure.known_weight, 0.6)
        self.assertAlmostEqual(report.exposure.unknown_weight, 0.4)
        self.assertAlmostEqual(report.exposure.exposures["symbol||aaa"], 0.4)

    def test_stale_date_and_anonymous_summary_are_stable(self):
        report = analyze_overlap([
            FundHoldings(
                "real", (HoldingPosition(1.0, stable_id="ID1", stable_id_type="isin"),),
                1, as_of=dt.date.today() - dt.timedelta(days=181),
            ),
            FundHoldings(
                "other", (HoldingPosition(1.0, stable_id="ID1", stable_id_type="isin"),), 1,
            ),
        ])
        self.assertTrue(report.coverage["real"].stale)
        first = json.dumps(report.anonymous_summary(), sort_keys=True)
        second = json.dumps(report.anonymous_summary(), sort_keys=True)
        self.assertEqual(first, second)
        self.assertNotIn("ID1", first)


if __name__ == "__main__":
    unittest.main()
