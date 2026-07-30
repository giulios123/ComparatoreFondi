import unittest

from comparatore import i18n
from comparatore.locales import de, en, fr, it

CATALOGHI = {"it": it, "en": en, "fr": fr, "de": de}
MAPPE = ("MESSAGGI", "METRICHE", "TERMINI", "FONTI", "RIBILANCIAMENTO", "ESITI")


class TestCataloghiSincronizzati(unittest.TestCase):
    def test_stesse_chiavi_in_ogni_mappa(self):
        for nome_mappa in MAPPE:
            chiavi_it = set(getattr(it, nome_mappa))
            for lingua, modulo in CATALOGHI.items():
                if lingua == "it":
                    continue
                chiavi = set(getattr(modulo, nome_mappa))
                mancanti = chiavi_it - chiavi
                estranee = chiavi - chiavi_it
                self.assertFalse(
                    mancanti, f"{nome_mappa}[{lingua}]: chiavi mancanti {mancanti}"
                )
                self.assertFalse(
                    estranee, f"{nome_mappa}[{lingua}]: chiavi estranee {estranee}"
                )

    def test_nessuna_stringa_vuota(self):
        for lingua, modulo in CATALOGHI.items():
            for nome_mappa in MAPPE:
                for chiave, valore in getattr(modulo, nome_mappa).items():
                    self.assertTrue(
                        valore, f"{nome_mappa}[{lingua}][{chiave}] e' vuota"
                    )


class TestTraduci(unittest.TestCase):
    def test_ripiega_su_italiano_se_manca(self):
        self.assertEqual(
            i18n.traduci("en", "app.title"), en.MESSAGGI["app.title"]
        )

    def test_chiave_sconosciuta_ritorna_se_stessa(self):
        self.assertEqual(i18n.traduci("it", "chiave.inesistente"), "chiave.inesistente")

    def test_interpolazione(self):
        self.assertEqual(
            i18n.traduci("it", "toast.fund_added", symbol="VWCE"),
            "Aggiunto VWCE",
        )

    def test_placeholder_mancante_non_solleva(self):
        # Se manca un kwarg atteso dal template, meglio il testo non
        # interpolato che un KeyError che blocca l'interfaccia.
        testo = i18n.traduci("it", "toast.fund_added")
        self.assertIn("{symbol}", testo)


class TestRilevamento(unittest.TestCase):
    def test_accept_language_semplice(self):
        self.assertEqual(i18n.rileva(accept_language="fr-FR,fr;q=0.9,en;q=0.8"), "fr")

    def test_accept_language_qualita(self):
        self.assertEqual(i18n.rileva(accept_language="de;q=0.5,en;q=0.9"), "en")

    def test_accept_language_lingua_non_supportata(self):
        self.assertEqual(i18n.rileva(accept_language="ja,ja-JP;q=0.9"), "it")

    def test_locale_di_sistema(self):
        self.assertEqual(i18n.rileva(locale_sistema="de_DE.UTF-8"), "de")

    def test_default_italiano(self):
        self.assertEqual(i18n.rileva(), "it")

    def test_accept_language_ha_priorita_su_locale(self):
        self.assertEqual(
            i18n.rileva(accept_language="fr-FR", locale_sistema="de_DE.UTF-8"), "fr"
        )

    def test_browser_locale_ha_priorita_su_tutto(self):
        self.assertEqual(
            i18n.rileva(
                browser_locale="de-DE",
                accept_language="fr-FR",
                locale_sistema="en_US.UTF-8",
            ),
            "de",
        )

    def test_browser_locale_non_supportato_ripiega(self):
        self.assertEqual(
            i18n.rileva(browser_locale="ja-JP", accept_language="fr-FR"), "fr"
        )


class TestEtichette(unittest.TestCase):
    def test_etichetta_metrica(self):
        self.assertEqual(i18n.etichetta_metrica("en", "volatility"), "Volatility")

    def test_etichetta_termine(self):
        self.assertEqual(i18n.etichetta_termine("de", "Azionario"), "Aktien")

    def test_etichetta_fonte(self):
        self.assertEqual(i18n.etichetta_fonte("fr", "yahoo"), "Yahoo Finance")

    def test_etichetta_ribilanciamento_da_enum(self):
        from comparatore.engine import Rebalance

        self.assertEqual(i18n.etichetta_ribilanciamento("en", Rebalance.MONTHLY), "Monthly")

    def test_etichetta_esito(self):
        self.assertEqual(i18n.etichetta_esito("en", "no_data"), "no data")


if __name__ == "__main__":
    unittest.main()
