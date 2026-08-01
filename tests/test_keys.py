import unittest

from comparatore import keys


class MaskedKeyTests(unittest.TestCase):
    def test_masks_empty_key(self) -> None:
        self.assertEqual(keys.masked("  "), "")

    def test_masks_short_key_completely(self) -> None:
        self.assertEqual(keys.masked("abc"), "***")

    def test_masks_long_key_except_last_four_characters(self) -> None:
        self.assertEqual(keys.masked("secret-value-1234"), "****1234")


if __name__ == "__main__":
    unittest.main()
