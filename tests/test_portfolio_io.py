import unittest

from comparatore import portfolio_io as pio

FONDO_MINIMO = {"symbol": "VWCE.DE", "name": "Vanguard FTSE All-World", "weight": 100.0}


class TestDumpLoad(unittest.TestCase):
    def test_round_trip(self):
        fondi = [dict(FONDO_MINIMO, ter=0.22, source="auto", proxy="(nessuno)")]
        parametri = {"base_ccy": "EUR", "rebalance": "monthly", "risk_free": 0.02}
        testo = pio.dump(fondi, parametri)
        fondi_ricaricati, parametri_ricaricati = pio.load(testo)
        self.assertEqual(fondi_ricaricati[0]["symbol"], "VWCE.DE")
        self.assertEqual(fondi_ricaricati[0]["ter"], 0.22)
        self.assertEqual(parametri_ricaricati, parametri)

    def test_load_backfills_alloc(self):
        testo = pio.dump([dict(FONDO_MINIMO)], {})
        fondi, _ = pio.load(testo)
        self.assertIn("alloc", fondi[0])
        self.assertIn("alloc_manuale", fondi[0])
        self.assertEqual(fondi[0]["alloc_manuale"], {"classe": "", "area": "", "settore": ""})

    def test_load_accepts_bytes(self):
        testo = pio.dump([dict(FONDO_MINIMO)], {})
        fondi, _ = pio.load(testo.encode("utf-8"))
        self.assertEqual(len(fondi), 1)


class TestLoadRejects(unittest.TestCase):
    def test_not_json(self):
        with self.assertRaises(pio.PortfolioError):
            pio.load("questo non è json")

    def test_wrong_schema(self):
        with self.assertRaises(pio.PortfolioError):
            pio.load('{"schema": "altro-schema", "versione": 1, "fondi": []}')

    def test_future_version(self):
        payload = pio.dump([dict(FONDO_MINIMO)], {})
        testo_futuro = payload.replace('"versione": 1', '"versione": 999')
        with self.assertRaises(pio.PortfolioError):
            pio.load(testo_futuro)

    def test_empty_fund_list(self):
        with self.assertRaises(pio.PortfolioError):
            pio.load('{"schema": "comparatore-fondi/portafoglio", "versione": 1, "fondi": []}')

    def test_fund_missing_required_field(self):
        payload = (
            '{"schema": "comparatore-fondi/portafoglio", "versione": 1, '
            '"fondi": [{"symbol": "X"}]}'
        )
        with self.assertRaises(pio.PortfolioError):
            pio.load(payload)

    def test_invalid_utf8_bytes(self):
        with self.assertRaises(pio.PortfolioError):
            pio.load(b"\xff\xfe\x00\x00not utf8")


if __name__ == "__main__":
    unittest.main()
