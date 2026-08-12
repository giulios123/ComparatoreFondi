import unittest

from comparatore.diagnostics import diagnose
from comparatore.profile import InvestorProfile


class TestDiagnostics(unittest.TestCase):
    def setUp(self):
        self.context = {
            "assets": [
                {"asset_id": "real-a", "weight": 0.7, "max_drawdown": -0.3,
                 "history_years": 3, "asset_class": "Azionario", "ter": None},
                {"asset_id": "real-b", "weight": 0.3, "max_drawdown": -0.1,
                 "history_years": 10, "asset_class": "Obbligazionario", "ter": 0.2},
            ],
            "correlations": {"a-b": 0.9},
        }

    def test_empty_profile_is_descriptive_only(self):
        report = diagnose(self.context)
        self.assertFalse(report.profile_present)
        self.assertTrue(any(f.code == "profile_missing" for f in report.findings))
        self.assertFalse(any(f.severity == "warning" for f in report.findings))

    def test_personal_rules_and_actions(self):
        report = diagnose(self.context, InvestorProfile(
            horizon_years=5, max_temporary_loss=0.2, max_position_weight=0.5,
            bonds_allowed=False,
        ))
        codes = {finding.code for finding in report.findings if finding.severity == "warning"}
        self.assertIn("position_limit_exceeded", codes)
        self.assertIn("drawdown_exceeds_tolerance", codes)
        self.assertIn("history_shorter_than_horizon", codes)
        self.assertIn("bonds_not_allowed", codes)

    def test_same_input_has_same_order(self):
        first = diagnose(self.context, InvestorProfile(max_position_weight=0.5)).as_dict()
        second = diagnose(self.context, InvestorProfile(max_position_weight=0.5)).as_dict()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
