import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from comparatore import profile


class TestProfile(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "investor_profile.json"
        self.previous = os.environ.get("COMPARATORE_PROFILE_FILE")
        os.environ["COMPARATORE_PROFILE_FILE"] = str(self.path)

    def tearDown(self):
        if self.previous is None:
            os.environ.pop("COMPARATORE_PROFILE_FILE", None)
        else:
            os.environ["COMPARATORE_PROFILE_FILE"] = self.previous
        self.temp_dir.cleanup()

    def test_round_trip_and_permissions(self):
        value = profile.InvestorProfile(
            horizon_years=15, objective="growth", max_temporary_loss=0.25,
            withdrawals=False, max_position_weight=0.4, preference="diversification",
            bonds_allowed=True, excluded_classes=("crypto",), excluded_sectors=("tobacco",),
        )
        profile.save(value)
        self.assertEqual(profile.load(), value)
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
        payload = json.loads(self.path.read_text())
        self.assertNotIn("symbol", payload)

    def test_missing_corrupt_and_clear_degrade(self):
        self.assertEqual(profile.load(), profile.InvestorProfile())
        self.path.write_text("not json")
        self.assertEqual(profile.load(), profile.InvestorProfile())
        profile.save(profile.InvestorProfile(horizon_years=2))
        profile.clear()
        self.assertFalse(self.path.exists())

    def test_validation_rejects_invalid_values(self):
        with self.assertRaises(profile.ProfileError):
            profile.InvestorProfile(horizon_years=0)
        with self.assertRaises(profile.ProfileError):
            profile.InvestorProfile(max_position_weight=1.1)


if __name__ == "__main__":
    unittest.main()
