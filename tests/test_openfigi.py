import os
import tempfile
import unittest
from unittest.mock import patch

from fixtures import FakeResponse

from comparatore import cache
from comparatore.sources import openfigi

ISIN = "IE00B3RBWM25"


class IsinToSymbolsTests(unittest.TestCase):
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

    def test_not_an_isin_returns_empty_without_touching_cache_or_network(self) -> None:
        with patch("requests.post") as mock_post:
            self.assertEqual(openfigi.isin_to_symbols("not-an-isin"), [])
        mock_post.assert_not_called()

    def test_cache_hit_skips_the_network_call(self) -> None:
        cache.write_meta(f"openfigi/{ISIN}", {"symbols": ["VWCE.MI"]})

        with patch("requests.post") as mock_post:
            self.assertEqual(openfigi.isin_to_symbols(ISIN), ["VWCE.MI"])
        mock_post.assert_not_called()

    def test_maps_exchange_codes_and_ranks_preferred_first(self) -> None:
        payload = [
            {
                "data": [
                    {"ticker": "VWCE", "exchCode": "GR"},  # .DE, meno preferito
                    {"ticker": "VWCE", "exchCode": "IM"},  # .MI, il piu' preferito
                    {"ticker": "XYZ", "exchCode": "ZZ"},  # borsa non mappata, scartata
                ]
            }
        ]
        with patch("requests.post", return_value=FakeResponse(json_data=payload)):
            out = openfigi.isin_to_symbols(ISIN)

        self.assertEqual(out, ["VWCE.MI", "VWCE.DE"])

    def test_result_is_cached_after_the_first_call(self) -> None:
        payload = [{"data": [{"ticker": "VWCE", "exchCode": "IM"}]}]
        with patch("requests.post", return_value=FakeResponse(json_data=payload)):
            openfigi.isin_to_symbols(ISIN)

        with patch("requests.post") as mock_post:
            out = openfigi.isin_to_symbols(ISIN)
        mock_post.assert_not_called()
        self.assertEqual(out, ["VWCE.MI"])

    def test_http_error_returns_empty_list(self) -> None:
        with patch("requests.post", return_value=FakeResponse(status_code=500)):
            self.assertEqual(openfigi.isin_to_symbols(ISIN), [])

    def test_network_exception_returns_empty_list(self) -> None:
        with patch("requests.post", side_effect=ConnectionError("offline")):
            self.assertEqual(openfigi.isin_to_symbols(ISIN), [])


if __name__ == "__main__":
    unittest.main()
