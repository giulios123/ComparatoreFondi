import unittest

from comparatore.pic_costs import (
    PicCostError,
    TransactionFeeMode,
    TransactionFeeRule,
    estimate_pic_costs,
)


class PicCostsTests(unittest.TestCase):
    def test_fixed_cost_reserves_budget_per_order(self):
        result = estimate_pic_costs(
            1_000,
            {"A": 0.5, "B": 0.5},
            {"A": 600, "B": 600},
            TransactionFeeRule(TransactionFeeMode.FIXED, amount=5),
            TransactionFeeRule(TransactionFeeMode.FIXED, amount=3),
        )
        self.assertEqual(result.buy_cost, 10)
        self.assertEqual(result.investable, 990)
        self.assertEqual(result.sell_cost, 6)
        self.assertEqual(result.final_net, 1182)

    def test_percentage_minimum_and_maximum(self):
        rule = TransactionFeeRule(
            TransactionFeeMode.PERCENTAGE, rate=0.01, minimum=5, maximum=8
        )
        self.assertEqual(rule.fee(100), 5)
        self.assertEqual(rule.fee(600), 6)
        self.assertEqual(rule.fee(2_000), 8)

    def test_budget_exhausted_by_fixed_cost(self):
        with self.assertRaises(PicCostError):
            estimate_pic_costs(
                10,
                {"A": 0.5, "B": 0.5},
                {"A": 10, "B": 10},
                TransactionFeeRule(TransactionFeeMode.FIXED, amount=10),
            )

    def test_none_rules_are_identity(self):
        result = estimate_pic_costs(100, {"A": 1}, {"A": 125})
        self.assertEqual(result.investable, 100)
        self.assertEqual(result.final_net, 125)
        self.assertEqual(result.total_cost, 0)


if __name__ == "__main__":
    unittest.main()
