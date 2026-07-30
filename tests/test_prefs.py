import json
import os
import tempfile
import unittest
from pathlib import Path

from comparatore import prefs


class PrefsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "prefs.json"
        self.previous = os.environ.get("COMPARATORE_PREFS_FILE")
        os.environ["COMPARATORE_PREFS_FILE"] = str(self.path)

    def tearDown(self) -> None:
        if self.previous is None:
            os.environ.pop("COMPARATORE_PREFS_FILE", None)
        else:
            os.environ["COMPARATORE_PREFS_FILE"] = self.previous
        self.temp_dir.cleanup()

    def test_save_and_load_preserve_language_and_enabled_justetf(self) -> None:
        prefs.save({"lingua": "it", "enable_justetf": True})

        self.assertEqual(
            prefs.load(), {"lingua": "it", "enable_justetf": True}
        )

    def test_save_and_load_preserve_disabled_justetf(self) -> None:
        prefs.save({"lingua": "it", "enable_justetf": False})

        self.assertEqual(
            prefs.load(), {"lingua": "it", "enable_justetf": False}
        )

    def test_load_ignores_malformed_boolean(self) -> None:
        self.path.write_text(
            json.dumps({"lingua": "it", "enable_justetf": "true"}),
            encoding="utf-8",
        )

        self.assertEqual(prefs.load(), {"lingua": "it"})


if __name__ == "__main__":
    unittest.main()