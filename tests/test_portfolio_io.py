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
        self.assertEqual(fondi_ricaricati[0]["distribution_policy"], "")
        self.assertEqual(fondi_ricaricati[0]["replication_method"], "")
        self.assertEqual(parametri_ricaricati, parametri)

    def test_load_backfills_alloc(self):
        testo = pio.dump([dict(FONDO_MINIMO)], {})
        fondi, _ = pio.load(testo)
        self.assertIn("alloc", fondi[0])
        self.assertIn("alloc_manuale", fondi[0])
        self.assertEqual(fondi[0]["alloc_manuale"], {"classe": "", "area": "", "settore": ""})

    def test_load_backfills_ter_origin_without_losing_manual_value(self):
        testo = pio.dump([dict(FONDO_MINIMO, ter=0.37, ter_auto=False)], {})
        fondi, _ = pio.load(testo)
        self.assertEqual(fondi[0]["ter_origin"], "manual")

    def test_load_backfills_missing_ter_origin(self):
        testo = pio.dump([dict(FONDO_MINIMO, ter=0.0, ter_auto=False)], {})
        fondi, _ = pio.load(testo)
        self.assertEqual(fondi[0]["ter_origin"], "missing")

    def test_load_accepts_bytes(self):
        testo = pio.dump([dict(FONDO_MINIMO)], {})
        fondi, _ = pio.load(testo.encode("utf-8"))
        self.assertEqual(len(fondi), 1)

    def test_benchmark_round_trip_and_old_files(self):
        benchmark = {
            "kind": "preset", "symbol": "VT", "name": "Global", "preferred_source": "yahoo"
        }
        testo = pio.dump([dict(FONDO_MINIMO)], {"benchmark": benchmark})
        _, parametri = pio.load(testo)
        self.assertEqual(parametri["benchmark"]["symbol"], "VT")
        _, vecchi_parametri = pio.load(pio.dump([dict(FONDO_MINIMO)], {}))
        self.assertNotIn("benchmark", vecchi_parametri)

    def test_malformed_benchmark_degrades_to_none(self):
        testo = pio.dump([dict(FONDO_MINIMO)], {"benchmark": {"name": "missing symbol"}})
        _, parametri = pio.load(testo)
        self.assertIsNone(parametri["benchmark"])

    def test_benchmark_non_price_source_falls_back_to_auto(self):
        testo = pio.dump(
            [dict(FONDO_MINIMO)],
            {"benchmark": {"symbol": "VT", "preferred_source": "openfigi"}},
        )
        _, parametri = pio.load(testo)
        self.assertEqual(parametri["benchmark"]["preferred_source"], "auto")

    def test_instrument_facts_round_trip_and_transient_attempts_are_stripped(self):
        fondo = dict(
            FONDO_MINIMO,
            ter=0.14,
            ter_origin="kid",
            ter_attempts=[{"source": "yahoo", "outcome": "temporary_error"}],
            instrument_facts={
                "values": {
                    "ter": {
                        "value": 0.0014,
                        "source": "kid",
                        "observed_at": "2026-08-01",
                        "acquired_at": "2026-08-14T09:00:00",
                        "quality": "document",
                    }
                },
                "alternatives": {},
                "related_quotes": [{
                    "symbol": "VWCE.DE", "exchange": "XETRA", "currency": "EUR",
                    "source": "openfigi", "isin": "IE00BK5BQT80",
                }],
            },
        )

        testo = pio.dump([fondo], {})
        self.assertNotIn("ter_attempts", testo)
        fondi, _ = pio.load(testo)
        self.assertEqual(fondi[0]["instrument_facts"]["values"]["ter"]["source"], "kid")
        self.assertEqual(fondi[0]["related_quotes"][0]["symbol"], "VWCE.DE")

    def test_malformed_instrument_facts_are_backfilled_empty(self):
        testo = pio.dump([dict(FONDO_MINIMO, instrument_facts={"values": "bad"})], {})
        fondi, _ = pio.load(testo)
        self.assertEqual(fondi[0]["instrument_facts"]["values"], {})


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
