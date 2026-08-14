import json
import unittest

from comparatore.diagnostics import diagnose
from comparatore.privacy import anonymize, validate_payload
from comparatore.profile import InvestorProfile


class TestPrivacy(unittest.TestCase):
    def test_allowlist_excludes_identifiers_and_amounts(self):
        assets = [{
            "asset_id": "Vanguard World IE00B3XXRP09 VWCE.DE",
            "name": "/Users/giulio/private/file.json",
            "symbol": "VWCE.DE",
            "isin": "IE00B3XXRP09",
            "weight": 0.75,
            "ter": 0.0022,
            "source": "yahoo",
        }]
        result = anonymize(
            diagnose({"assets": assets}, InvestorProfile(max_position_weight=0.5)),
            assets, "it",
        )
        encoded = result.to_json()
        self.assertIn("asset_1", encoded)
        for forbidden in ("Vanguard", "VWCE.DE", "IE00B3XXRP09", "/Users/", "private"):
            self.assertNotIn(forbidden, encoded)
        self.assertNotIn("asset_tokens", result.to_dict())
        validate_payload(result.payload)
        self.assertEqual(json.loads(encoded), result.payload)

    def test_map_is_local_and_payload_is_stable(self):
        assets = [{"asset_id": "A", "weight": 0.5}, {"asset_id": "B", "weight": 0.5}]
        report = diagnose({"assets": assets})
        first = anonymize(report, assets)
        second = anonymize(report, assets)
        self.assertEqual(first.to_json(), second.to_json())
        self.assertEqual(first.asset_tokens, {"A": "asset_1", "B": "asset_2"})


if __name__ == "__main__":
    unittest.main()
