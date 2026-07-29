import os
import tempfile
import unittest

from comparatore import cache
from comparatore.sources.eodhd import EodhdSource, to_yahoo_symbol


class ToYahooSymbolTests(unittest.TestCase):
    def test_us_listing_drops_the_suffix(self) -> None:
        self.assertEqual(to_yahoo_symbol("REET.US"), "REET")

    def test_xetra_becomes_the_yahoo_de_suffix(self) -> None:
        self.assertEqual(to_yahoo_symbol("VWCE.XETRA"), "VWCE.DE")

    def test_unmapped_exchange_has_no_translation(self) -> None:
        # I fondi comuni non quotati (EUFUND) non hanno un equivalente Yahoo.
        self.assertEqual(to_yahoo_symbol("LU0157178582.EUFUND"), "")

    def test_symbol_without_a_dot_has_no_translation(self) -> None:
        self.assertEqual(to_yahoo_symbol("REET"), "")

    def test_a_symbol_already_in_yahoo_format_is_not_rewritten(self) -> None:
        # "MI" e' sia un codice di borsa EODHD sia gia' il suffisso Yahoo:
        # tradurlo darebbe lo stesso identico simbolo, quindi "" (nessun
        # secondo giro su Yahoo inutile), non un simbolo identico a se' stesso.
        self.assertEqual(to_yahoo_symbol("VWCE.MI"), "")


class FundamentalsBlockedTests(unittest.TestCase):
    """`fundamentals_blocked()` legge un flag che `metadata()` scrive su un 403.

    Si esercita direttamente il contratto con la cache invece di simulare una
    risposta HTTP: e' il flag - non la chiamata di rete che lo produce - a
    dover restare stabile.
    """

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

    def test_unblocked_by_default(self) -> None:
        self.assertFalse(EodhdSource(api_key="x").fundamentals_blocked())

    def test_blocked_after_metadata_records_a_403(self) -> None:
        cache.write_meta("eodhd-fundamentals-blocked", {"bloccato": True})
        self.assertTrue(EodhdSource(api_key="x").fundamentals_blocked())


if __name__ == "__main__":
    unittest.main()
