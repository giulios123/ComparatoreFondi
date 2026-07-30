"""Compila app.py: nessun modulo importa app.py (Streamlit lo esegue come
script, non lo importa), quindi senza questo controllo un errore di sintassi
può restare invisibile fino all'avvio manuale (vedi commit caa1c91)."""

import ast
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestSintassiApp(unittest.TestCase):
    def test_app_compila(self):
        sorgente = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")
        ast.parse(sorgente, filename="app.py")


if __name__ == "__main__":
    unittest.main()
