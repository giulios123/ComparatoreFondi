import unittest

from comparatore import pesi


class ArrotondaA100Tests(unittest.TestCase):
    def test_somma_esatta_su_tre_fondi(self):
        risultato = pesi.arrotonda_a_100([100 / 3] * 3)
        self.assertEqual(sum(risultato), 100.0)
        self.assertEqual(risultato, [33.34, 33.33, 33.33])

    def test_lista_vuota(self):
        self.assertEqual(pesi.arrotonda_a_100([]), [])

    def test_gia_esatto(self):
        self.assertEqual(pesi.arrotonda_a_100([50.0, 50.0]), [50.0, 50.0])


class UgualiTests(unittest.TestCase):
    def test_somma_100_per_ogni_n(self):
        for n in range(1, 8):
            risultato = pesi.uguali(n)
            self.assertEqual(len(risultato), n)
            self.assertAlmostEqual(sum(risultato), 100.0, places=6)

    def test_zero_fondi(self):
        self.assertEqual(pesi.uguali(0), [])


class RidistribuisciTests(unittest.TestCase):
    def test_un_solo_fondo_prende_tutto(self):
        self.assertEqual(pesi.ridistribuisci([100.0], {0: 30.0}), [100.0])

    def test_fisso_semplice_due_fondi(self):
        # 50/50 -> fondo 0 messo a 60 -> il residuo (40) va tutto al fondo 1.
        risultato = pesi.ridistribuisci([50.0, 50.0], {0: 60.0})
        self.assertEqual(risultato, [60.0, 40.0])

    def test_proporzione_mantenuta_su_liberi(self):
        # 3 fondi 20/30/50; si fissa il primo a 40 -> gli altri due (30 e 50,
        # rapporto 3:5) si dividono il residuo 60 nello stesso rapporto.
        risultato = pesi.ridistribuisci([20.0, 30.0, 50.0], {0: 40.0})
        self.assertAlmostEqual(sum(risultato), 100.0, places=6)
        self.assertEqual(risultato[0], 40.0)
        self.assertAlmostEqual(risultato[1] / risultato[2], 30 / 50, places=3)

    def test_aggiunta_fondo_comprime_esistenti_in_proporzione(self):
        # 70/30 + un terzo fondo che deve valere 100/3 -> i due esistenti si
        # comprimono mantenendo il rapporto 7:3 sul residuo (100 - 100/3).
        n = 3
        risultato = pesi.ridistribuisci([70.0, 30.0, 0.0], {2: 100.0 / n})
        self.assertAlmostEqual(sum(risultato), 100.0, places=6)
        self.assertAlmostEqual(risultato[0] / risultato[1], 70 / 30, places=3)

    def test_liberi_a_zero_si_dividono_in_parti_uguali(self):
        risultato = pesi.ridistribuisci([0.0, 0.0], {})
        self.assertEqual(risultato, [50.0, 50.0])

    def test_fissi_oltre_100_vengono_riscalati(self):
        risultato = pesi.ridistribuisci([50.0, 50.0, 0.0], {0: 80.0, 1: 80.0})
        self.assertAlmostEqual(sum(risultato), 100.0, places=6)
        self.assertEqual(risultato[0], risultato[1])
        self.assertEqual(risultato[2], 0.0)

    def test_indice_fisso_fuori_range_ignorato(self):
        risultato = pesi.ridistribuisci([50.0, 50.0], {5: 30.0})
        self.assertAlmostEqual(sum(risultato), 100.0, places=6)


class RinormalizzaTests(unittest.TestCase):
    def test_mantiene_le_proporzioni(self):
        # Dopo la rimozione di un terzo fondo restano pesi 30/50 (somma 80).
        risultato = pesi.rinormalizza([30.0, 50.0])
        self.assertAlmostEqual(sum(risultato), 100.0, places=6)
        self.assertAlmostEqual(risultato[0] / risultato[1], 30 / 50, places=3)

    def test_tutti_zero_diventano_uguali(self):
        self.assertEqual(pesi.rinormalizza([0.0, 0.0, 0.0]), pesi.uguali(3))

    def test_lista_vuota(self):
        self.assertEqual(pesi.rinormalizza([]), [])


class ImportiTests(unittest.TestCase):
    def test_andata_e_ritorno(self):
        pesi_iniziali = [50.0, 50.0]
        capitale = 10_000.0
        imp = pesi.importi(pesi_iniziali, capitale)
        self.assertEqual(imp, [5000.0, 5000.0])
        totale, pesi_calcolati = pesi.da_importi(imp)
        self.assertEqual(totale, capitale)
        self.assertEqual(pesi_calcolati, pesi_iniziali)

    def test_modifica_importo_singolo_fondo(self):
        # Esempio della richiesta: 10.000 su 50/50, poi 2.000 nel primo fondo.
        importi_correnti = [2000.0, 5000.0]
        totale, pesi_calcolati = pesi.da_importi(importi_correnti)
        self.assertEqual(totale, 7000.0)
        self.assertAlmostEqual(sum(pesi_calcolati), 100.0, places=6)
        self.assertAlmostEqual(pesi_calcolati[0], 2000 / 7000 * 100, places=1)

    def test_totale_zero_ripartisce_ugualmente(self):
        totale, pesi_calcolati = pesi.da_importi([0.0, 0.0])
        self.assertEqual(totale, 0.0)
        self.assertEqual(pesi_calcolati, [50.0, 50.0])


if __name__ == "__main__":
    unittest.main()
