"""La versione vive in comparatore/__init__.py (vedi il commento li'): questo
file verifica che pyproject.toml e desktop/comparatore.spec non se ne
allontanino, visto che nessun type checker li collega fra loro."""

import tomllib
import unittest
from pathlib import Path

from comparatore import __version__

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestVersioneAllineata(unittest.TestCase):
    def test_pyproject_corrisponde_a_comparatore(self):
        payload = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(payload["project"]["version"], __version__)

    def test_comparatore_spec_non_ha_piu_una_versione_scritta_a_mano(self):
        sorgente = (PROJECT_ROOT / "desktop" / "comparatore.spec").read_text(encoding="utf-8")
        self.assertIn("_versione_app()", sorgente)
        self.assertIn('"CFBundleShortVersionString": VERSIONE', sorgente)


if __name__ == "__main__":
    unittest.main()
