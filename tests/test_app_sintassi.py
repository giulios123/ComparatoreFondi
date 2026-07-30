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
        tree = ast.parse(sorgente, filename="app.py")

        def chain(node):
            parts = []
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
                return list(reversed(parts))
            return None

        export_empty = [
            n.lineno
            for n in ast.walk(tree)
            if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "portfolio_export" for t in n.targets)
            and isinstance(n.value, ast.Call)
            and isinstance(n.value.func, ast.Attribute)
            and chain(n.value.func) == ["st", "empty"]
        ]
        empty_guard = [
            n.lineno
            for n in ast.walk(tree)
            if isinstance(n, ast.If)
            and isinstance(n.test, ast.UnaryOp)
            and isinstance(n.test.op, ast.Not)
            and chain(n.test.operand) == ["st", "session_state", "selected"]
        ]
        dump_calls = [
            n.lineno
            for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and chain(n.func) == ["portfolio_io", "dump"]
        ]
        backtest_calls = [
            n.lineno
            for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "run_backtest"
        ]

        self.assertTrue(export_empty)
        self.assertTrue(empty_guard)
        self.assertLess(min(export_empty), min(empty_guard))
        self.assertTrue(dump_calls)
        self.assertTrue(backtest_calls)
        self.assertLess(min(dump_calls), min(backtest_calls))
            sorgente.index("if not st.session_state.selected:"),
        )
        self.assertLess(
            sorgente.index("payload = portfolio_io.dump("),
            sorgente.index("res = run_backtest("),
        )


if __name__ == "__main__":
    unittest.main()
