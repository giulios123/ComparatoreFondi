import unittest

from scripts.generate_third_party_notices import audit


class LicenseAuditTests(unittest.TestCase):
    def test_rejects_license_outside_reviewed_allowlist(self) -> None:
        packages = [
            {
                "Name": "example",
                "Version": "1.0",
                "License": "EUPL-1.2",
                "LicenseText": "Example",
            }
        ]

        with self.assertRaises(SystemExit):
            audit(packages)

    def test_accepts_pyinstaller_bootloader_exception(self) -> None:
        packages = [
            {
                "Name": "pyinstaller",
                "Version": "6.21.0",
                "License": "GNU General Public License v2 (GPLv2)",
                "LicenseText": "Bootloader Exception",
            }
        ]

        audit(packages)


if __name__ == "__main__":
    unittest.main()