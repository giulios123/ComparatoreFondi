import os
import tempfile
import unittest
from unittest.mock import patch

from comparatore.sources.justetf import JustEtfSource


class JustEtfMetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_cache_dir = os.environ.get("COMPARATORE_CACHE_DIR")
        os.environ["COMPARATORE_CACHE_DIR"] = self.temp_dir.name

    def tearDown(self) -> None:
        if self.previous_cache_dir is None:
            os.environ.pop("COMPARATORE_CACHE_DIR", None)
        else:
            os.environ["COMPARATORE_CACHE_DIR"] = self.previous_cache_dir
        self.temp_dir.cleanup()

    def test_extracts_ter_from_profile(self) -> None:
        response = type(
            "Response", (), {
                "status_code": 200,
                "text": (
                    '<h1>Vanguard ETF</h1>'
                    '<div data-testid="etf-profile-header_ter-value">0,14% p.a.</div>'
                    '<div data-testid="etf-profile-header_distribution-policy-value">'
                    'Accumulazione</div>'
                    '<div data-testid="etf-profile-header_replication-value">Fisica</div>'
                ),
            }
        )()
        with patch("comparatore.sources.justetf.requests.get", return_value=response):
            result = JustEtfSource().metadata("VWCE.MI", "IE00BK5BQT80")
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result.ter, 0.0014)
        self.assertEqual(result.ter_origin, "justetf")
        self.assertEqual(result.distribution_policy, "accumulating")
        self.assertEqual(result.replication_method, "physical")
        self.assertEqual(result.facts.values["name"].value, "Vanguard ETF")
        self.assertEqual(result.facts.values["ter"].source, "justetf")
        self.assertEqual(result.facts.values["distribution_policy"].value, "accumulating")

    def test_requires_isin(self) -> None:
        source = JustEtfSource()
        self.assertIsNone(source.metadata("VWCE.MI"))
        self.assertEqual(source.last_metadata_outcome, "symbol_unresolved")


if __name__ == "__main__":
    unittest.main()
