import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

from comparatore import keys


class MaskedKeyTests(unittest.TestCase):
    def test_masks_empty_key(self) -> None:
        self.assertEqual(keys.masked("  "), "")

    def test_masks_short_key_completely(self) -> None:
        self.assertEqual(keys.masked("abc"), "***")

    def test_masks_long_key_except_last_four_characters(self) -> None:
        self.assertEqual(keys.masked("secret-value-1234"), "****1234")


class SaveLoadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "api_keys.json"
        self.previous = os.environ.get("COMPARATORE_KEYS_FILE")
        os.environ["COMPARATORE_KEYS_FILE"] = str(self.path)

    def tearDown(self) -> None:
        if self.previous is None:
            os.environ.pop("COMPARATORE_KEYS_FILE", None)
        else:
            os.environ["COMPARATORE_KEYS_FILE"] = self.previous
        self.temp_dir.cleanup()

    def test_save_and_load_round_trip(self) -> None:
        keys.save({"EODHD_API_KEY": "abc123", "TWELVEDATA_API_KEY": "def456"})

        self.assertEqual(
            keys.load(),
            {"EODHD_API_KEY": "abc123", "TWELVEDATA_API_KEY": "def456"},
        )

    def test_save_ignores_unknown_keys_and_blank_values(self) -> None:
        keys.save({"EODHD_API_KEY": "  ", "UNKNOWN_KEY": "x", "TWELVEDATA_API_KEY": "y"})

        self.assertEqual(keys.load(), {"TWELVEDATA_API_KEY": "y"})

    @unittest.skipIf(sys.platform == "win32", "i permessi POSIX non si applicano su Windows")
    def test_save_leaves_file_owner_only_readable(self) -> None:
        keys.save({"EODHD_API_KEY": "abc123"})

        mode = stat.S_IMODE(self.path.stat().st_mode)
        self.assertEqual(mode, 0o600)

    def test_clear_removes_file(self) -> None:
        keys.save({"EODHD_API_KEY": "abc123"})
        keys.clear()

        self.assertEqual(keys.load(), {})
        self.assertFalse(self.path.exists())

    def test_load_missing_file_returns_empty_dict(self) -> None:
        self.assertEqual(keys.load(), {})


if __name__ == "__main__":
    unittest.main()
