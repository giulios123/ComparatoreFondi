"""Compila app.py: nessun modulo importa app.py (Streamlit lo esegue come
script, non lo importa), quindi senza questo controllo un errore di sintassi
può restare invisibile fino all'avvio manuale (vedi commit caa1c91)."""

import ast
import unittest
from pathlib import Path

from comparatore import i18n

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
        self.assertLess(
            sorgente.index("payload = portfolio_io.dump("),
            sorgente.index("res = run_backtest("),
        )

    def test_preset_periodo_non_vanno_a_capo(self):
        """Il contenitore con `key` e la regola CSS che ne dipende vivono a
        centinaia di righe di distanza: separati non servono a niente, e una
        riscrittura del blocco dei preset puo' portarne via uno solo senza che
        nulla protesti finche' qualcuno non stringe la barra laterale."""
        sorgente = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")

        self.assertIn('st.container(key="preset_periodo")', sorgente)
        self.assertIn(".st-key-preset_periodo .stButton p { white-space: nowrap; }", sorgente)
        self.assertIn(".st-key-preset_periodo .stButton button {", sorgente)
        self.assertIn("min-width: 3ch;", sorgente)

    def test_etichette_preset_stanno_in_tre_caratteri(self):
        """`min-width: 3ch` protegge le etichette solo finche' restano di tre
        caratteri: una traduzione piu' lunga tornerebbe ad andare a capo, e il
        posto dove accorgersene e' qui, non a video."""
        for codice in i18n.LINGUE:
            for chiave in ("preset.1y", "preset.5y", "preset.10y",
                           "preset.20y", "preset.max"):
                etichetta = i18n.traduci(codice, chiave)
                self.assertLessEqual(
                    len(etichetta), 3,
                    f"{codice}/{chiave} = {etichetta!r}: oltre i 3 caratteri "
                    "garantiti dalla CSS dei preset in app.py",
                )

    def test_preferenza_justetf_e_riepilogo_chiavi_sono_collegati(self):
        sorgente = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")

        self.assertIn('"enable_justetf": bool(', sorgente)
        self.assertIn("on_change=_cambia_justetf", sorgente)
        self.assertIn("api_keys_store.masked(value)", sorgente)
        self.assertIn('t("api_keys.saved_caption",', sorgente)

    def test_guardia_fondi_assenti_blocca_prima_del_backtest(self):
        """Un fondo senza prezzi risolti non deve sparire in silenzio dagli
        `Holding` costruiti per il backtest (audit-codebase-2026-08-01.md,
        P1): la guardia su 'assenti' deve fermare l'esecuzione con
        `st.stop()` prima che `run_backtest()` venga chiamato."""
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

        guardie = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.If)
            and isinstance(n.test, ast.Name) and n.test.id == "assenti"
        ]
        self.assertTrue(guardie, "manca il blocco 'if assenti:'")
        guardia = guardie[0]
        stop_calls = [
            n for n in ast.walk(guardia)
            if isinstance(n, ast.Call) and chain(n.func) == ["st", "stop"]
        ]
        self.assertTrue(stop_calls, "la guardia sui fondi assenti non chiama st.stop()")

        backtest_calls = [
            n.lineno
            for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name) and n.func.id == "run_backtest"
        ]
        self.assertTrue(backtest_calls)
        self.assertLess(guardia.lineno, min(backtest_calls))

    def test_colonne_del_backtest_restano_per_simbolo(self):
        """Il motore non deve tornare a rinominare le colonne di `per_fund` /
        `contributions` con l'etichetta visuale: due fondi con lo stesso nome
        rompevano il PAC (audit-codebase-2026-08-01.md, P1). `res.labels' e'
        l'unica traduzione verso un nome leggibile ammessa."""
        sorgente = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("res.labels", sorgente)
        self.assertNotIn("label_splice", sorgente)

    def test_nuovi_flussi_restano_nell_interfaccia(self):
        sorgente = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("directa_io.parse_positions", sorgente)
        self.assertIn("cached_metadata(", sorgente)
        self.assertIn("ter_warning.retry_button", sorgente)
        self.assertIn("pic_costs.estimate_pic_costs", sorgente)
        self.assertIn("pac is None", sorgente)


if __name__ == "__main__":
    unittest.main()
