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

    def test_export_portafoglio_precede_il_backtest(self):
        sorgente = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")
        self.assertEqual(sorgente.count("portfolio_io.dump("), 1)
        self.assertLess(
            sorgente.index("portfolio_export = st.empty()"),
            sorgente.index("if not st.session_state.selected:"),
        )
        self.assertLess(
            sorgente.index("payload = portfolio_io.dump("),
            sorgente.index("res = run_backtest("),
        )


if __name__ == "__main__":
    unittest.main()
