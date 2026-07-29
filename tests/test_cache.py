import datetime as dt
import json
import os
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from comparatore import cache


class RestrictedCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_cache_dir = os.environ.get("COMPARATORE_CACHE_DIR")
        os.environ["COMPARATORE_CACHE_DIR"] = self.temp_dir.name
        self.start = dt.date(2025, 1, 1)
        self.end = dt.date(2025, 1, 2)

    def tearDown(self) -> None:
        if self.previous_cache_dir is None:
            os.environ.pop("COMPARATORE_CACHE_DIR", None)
        else:
            os.environ["COMPARATORE_CACHE_DIR"] = self.previous_cache_dir
        self.temp_dir.cleanup()

    def test_expired_entry_is_deleted_before_offline_fallback(self) -> None:
        key = "eodhd/TEST.US"
        prices = pd.Series([100.0], index=[pd.Timestamp("2025-01-02")])
        cache.write(key, prices, self.start, self.end)
        _, meta_path = cache._paths(key)
        metadata = json.loads(meta_path.read_text())
        metadata["fetched_at"] = "2025-01-01T00:00:00"
        meta_path.write_text(json.dumps(metadata))

        result = cache.get_or_fetch(
            key,
            self.start,
            self.end,
            lambda *_: None,
            retention_days=30,
        )

        self.assertIsNone(result)
        self.assertFalse(any(Path(self.temp_dir.name).iterdir()))

    def test_restricted_retention_cannot_exceed_thirty_days(self) -> None:
        previous = os.environ.get("COMPARATORE_RESTRICTED_CACHE_DAYS")
        try:
            os.environ["COMPARATORE_RESTRICTED_CACHE_DAYS"] = "90"
            self.assertEqual(cache.restricted_retention_days(), 30)
        finally:
            if previous is None:
                os.environ.pop("COMPARATORE_RESTRICTED_CACHE_DAYS", None)
            else:
                os.environ["COMPARATORE_RESTRICTED_CACHE_DAYS"] = previous

    def test_clear_prefixes_keeps_unrelated_sources(self) -> None:
        prices = pd.Series([100.0], index=[pd.Timestamp("2025-01-02")])
        for key in ("eodhd/TEST.US", "twelvedata/TEST", "yahoo/TEST"):
            cache.write(key, prices, self.start, self.end)

        removed = cache.clear_prefixes(("eodhd", "twelvedata"))

        self.assertEqual(removed, 4)
        self.assertIsNone(cache.read("eodhd/TEST.US"))
        self.assertIsNone(cache.read("twelvedata/TEST"))
        self.assertIsNotNone(cache.read("yahoo/TEST"))


if __name__ == "__main__":
    unittest.main()