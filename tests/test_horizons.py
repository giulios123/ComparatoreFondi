"""Test di comparatore.horizons: proiezioni a tasso costante.

`capitale_finale` non era chiamata da nessuna parte prima del PAC - qui si
fissa sia il comportamento originale (capitale unico) sia l'estensione
all'annualita' (versamenti periodici), che e' la parte nuova e quindi quella
piu' a rischio di un errore di formula.
"""

import unittest

from comparatore import horizons as hz


class CapitaleFinaleTests(unittest.TestCase):
    def test_nessun_rendimento_da_none(self):
        self.assertIsNone(hz.capitale_finale(None, 10, 10_000.0))

    def test_capitale_unico_formula_di_base(self):
        montante = hz.capitale_finale(0.05, 10, 10_000.0)
        self.assertAlmostEqual(montante, 10_000.0 * 1.05**10, places=6)

    def test_versamenti_periodici_coincidono_con_lannualita_ordinaria(self):
        # Senza capitale iniziale, con versamenti mensili, il montante e'
        # l'annualita' ordinaria classica: FV = P*((1+i)^n - 1)/i.
        tasso_annuo = 0.06
        montante = hz.capitale_finale(tasso_annuo, 5, 0.0, versamento_periodico=100.0, rate_annue=12)

        tasso_mensile = (1.0 + tasso_annuo) ** (1.0 / 12) - 1.0
        n = 5 * 12
        atteso = 100.0 * ((1.0 + tasso_mensile) ** n - 1.0) / tasso_mensile
        self.assertAlmostEqual(montante, atteso, places=6)

    def test_capitale_iniziale_e_versamenti_si_sommano(self):
        solo_capitale = hz.capitale_finale(0.04, 8, 5_000.0)
        solo_versamenti = hz.capitale_finale(0.04, 8, 0.0, versamento_periodico=50.0, rate_annue=4)
        combinato = hz.capitale_finale(0.04, 8, 5_000.0, versamento_periodico=50.0, rate_annue=4)
        self.assertAlmostEqual(combinato, solo_capitale + solo_versamenti, places=6)

    def test_tasso_zero_i_versamenti_si_sommano_senza_crescere(self):
        montante = hz.capitale_finale(0.0, 3, 1_000.0, versamento_periodico=100.0, rate_annue=4)
        self.assertAlmostEqual(montante, 1_000.0 + 100.0 * 12, places=6)


class CostoCumulatoTests(unittest.TestCase):
    def test_nessun_isc_da_none(self):
        self.assertIsNone(hz.costo_cumulato(None, 10, 10_000.0))

    def test_erosione_su_capitale_statico(self):
        eroso = hz.costo_cumulato(0.01, 10, 10_000.0)
        atteso = 10_000.0 - 10_000.0 * 0.99**10
        self.assertAlmostEqual(eroso, atteso, places=6)


if __name__ == "__main__":
    unittest.main()
