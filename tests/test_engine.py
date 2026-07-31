"""Test del motore di backtest: simulazione, PAC, per-fondo.

Prima di questo file `simulate` e `run_backtest` non avevano copertura: sono
la matematica su cui si basa ogni numero mostrato dall'app, quindi i casi qui
sotto fissano sia il comportamento di sempre (nessun PAC) sia quello nuovo.
"""

import datetime as dt
import unittest

import numpy as np
import pandas as pd

from comparatore import metrics as mt
from comparatore.engine import (
    Frequency,
    Holding,
    Pac,
    Rebalance,
    contribution_schedule,
    run_backtest,
    simulate,
)


def _prezzi(giorni: int, tassi_giornalieri: dict[str, float], inizio="2020-01-01") -> pd.DataFrame:
    """Prezzi a crescita composta costante, un asset per chiave del dizionario."""
    index = pd.bdate_range(inizio, periods=giorni)
    dati = {
        simbolo: 100.0 * (1.0 + tasso) ** np.arange(giorni)
        for simbolo, tasso in tassi_giornalieri.items()
    }
    return pd.DataFrame(dati, index=index)


class SimulateSenzaPacTests(unittest.TestCase):
    def test_portafoglio_a_due_asset_coincide_con_la_formula_chiusa(self):
        # Senza PAC il valore ha una formula chiusa: initial * sum(w_i * ratio_i^t).
        # E' la non-regressione che protegge chi il PAC non lo accende mai.
        prezzi = _prezzi(60, {"A": 0.001, "B": -0.0005})
        valore, _ = simulate(prezzi, {"A": 0.6, "B": 0.4}, 10_000.0, Rebalance.NONE)

        t = np.arange(60)
        atteso = 10_000.0 * (0.6 * 1.001**t + 0.4 * 0.9995**t)
        np.testing.assert_allclose(valore.to_numpy(), atteso, rtol=1e-10)

    def test_nav_e_lo_stesso_oggetto_del_portafoglio_senza_pac(self):
        # L'identita' di oggetto (non solo l'uguaglianza numerica) e' cio' che
        # rende la non-regressione esatta invece che approssimata.
        prezzi = _prezzi(30, {"A": 0.0008})
        holdings = [Holding(symbol="A", label="Fondo A", weight=1.0)]
        res = run_backtest(prezzi, holdings, 10_000.0, pac=None)
        self.assertIs(res.nav, res.portfolio)
        self.assertIs(res.nav_gross, res.portfolio_gross)


class ContributionScheduleTests(unittest.TestCase):
    # Un range di 13 mesi (gennaio 2020 - gennaio 2021): il primo giorno di
    # borsa cade nel mese/trimestre/anno "zero", che viene sempre escluso
    # perche' e' il capitale iniziale, non un versamento. Cosi' la stessa
    # finestra da' 12 rate mensili, 4 trimestrali, 1 annuale.
    INDEX = pd.bdate_range("2020-01-01", "2021-01-31")

    def test_dodici_rate_mensili(self):
        contrib = contribution_schedule(self.INDEX, Pac(amount=200.0, frequency=Frequency.MONTHLY))
        self.assertEqual(int((contrib > 0).sum()), 12)
        self.assertEqual(contrib[0], 0.0)  # il giorno zero non e' un versamento

    def test_quattro_rate_trimestrali(self):
        contrib = contribution_schedule(self.INDEX, Pac(amount=600.0, frequency=Frequency.QUARTERLY))
        self.assertEqual(int((contrib > 0).sum()), 4)

    def test_una_rata_annuale(self):
        contrib = contribution_schedule(self.INDEX, Pac(amount=2_400.0, frequency=Frequency.YEARLY))
        self.assertEqual(int((contrib > 0).sum()), 1)

    def test_nessun_pac_da_vettore_di_zeri(self):
        contrib = contribution_schedule(self.INDEX, None)
        self.assertEqual(contrib.sum(), 0.0)

    def test_finestra_di_versamento_rispettata(self):
        pac = Pac(
            amount=200.0, frequency=Frequency.MONTHLY,
            start=dt.date(2020, 6, 1), end=dt.date(2020, 9, 30),
        )
        contrib = contribution_schedule(self.INDEX, pac)
        date_versate = self.INDEX[contrib > 0]
        self.assertEqual(len(date_versate), 4)  # giu, lug, ago, set
        self.assertTrue(all(pd.Timestamp("2020-06-01") <= d <= pd.Timestamp("2020-09-30") for d in date_versate))

    def test_rivalutazione_annua_scatta_alla_tredicesima_rata(self):
        index = pd.bdate_range("2020-01-01", "2021-06-30")
        contrib = contribution_schedule(index, Pac(amount=100.0, frequency=Frequency.MONTHLY, step_up=0.10))
        importi = contrib[contrib > 0]
        self.assertEqual(len(importi), 17)  # feb 2020 - giu 2021
        np.testing.assert_allclose(importi[:12], [100.0] * 12)
        self.assertAlmostEqual(importi[12], 110.0, places=6)


class MontanteTests(unittest.TestCase):
    def test_montante_coincide_con_la_formula_dell_annualita(self):
        # Un indice mensile (un business-day per mese) rende ogni riga un
        # periodo di versamento: la simulazione diventa un'annualita'
        # ordinaria da confrontare con la formula chiusa FV = P*((1+i)^n-1)/i.
        n_periodi = 60
        tasso_mensile = 1.06 ** (1 / 12) - 1
        index = pd.bdate_range("2020-01-01", periods=n_periodi + 1, freq="BMS")
        prezzi = pd.DataFrame(
            {"A": 100.0 * (1.0 + tasso_mensile) ** np.arange(n_periodi + 1)}, index=index
        )
        pac = Pac(amount=100.0, frequency=Frequency.MONTHLY)
        valore, _ = simulate(prezzi, {"A": 1.0}, 0.0, Rebalance.NONE, pac)

        atteso = 100.0 * ((1.0 + tasso_mensile) ** n_periodi - 1.0) / tasso_mensile
        self.assertAlmostEqual(valore.iloc[-1], atteso, places=6)


class NavInvarianteAiFlussiTests(unittest.TestCase):
    def test_nav_su_singolo_asset_coincide_con_il_prezzo_normalizzato(self):
        # Il test decisivo: su un solo asset la NAV toglie esattamente
        # l'effetto dei versamenti, qualunque sia l'andamento del prezzo -
        # non solo nel caso a crescita costante.
        giorni = 300
        t = np.arange(giorni)
        ritorni = 0.002 * np.sin(t / 5.0)
        prezzo = 100.0 * np.cumprod(1.0 + ritorni)
        prezzi = pd.DataFrame({"A": prezzo}, index=pd.bdate_range("2020-01-01", periods=giorni))

        holdings = [Holding(symbol="A", label="A", weight=1.0)]
        pac = Pac(amount=150.0, frequency=Frequency.MONTHLY, step_up=0.03)
        res = run_backtest(prezzi, holdings, 5_000.0, Rebalance.NONE, pac=pac)

        atteso = prezzi["A"] / prezzi["A"].iloc[0] * 5_000.0
        np.testing.assert_allclose(res.nav.to_numpy(), atteso.to_numpy(), rtol=1e-8)


class XirrTests(unittest.TestCase):
    def test_pac_su_serie_piatta_da_xirr_vicino_a_zero(self):
        # Capitale iniziale a 100, come minimo imposto dall'app: a zero il
        # portafoglio parte da valore nullo e la NAV (non usata qui, ma
        # calcolata comunque da run_backtest) dividerebbe per zero.
        giorni = 400
        prezzi = pd.DataFrame({"A": [100.0] * giorni}, index=pd.bdate_range("2020-01-01", periods=giorni))
        holdings = [Holding(symbol="A", label="A", weight=1.0)]
        pac = Pac(amount=100.0, frequency=Frequency.MONTHLY)
        res = run_backtest(prezzi, holdings, 100.0, Rebalance.NONE, pac=pac)

        rate = mt.xirr(res.cashflows, res.portfolio.iloc[-1], res.end)
        self.assertAlmostEqual(rate, 0.0, places=3)

    def test_lump_sum_senza_pac_da_xirr_uguale_al_cagr(self):
        prezzi = _prezzi(1500, {"A": 0.0003})
        holdings = [Holding(symbol="A", label="A", weight=1.0)]
        res = run_backtest(prezzi, holdings, 10_000.0, Rebalance.NONE, pac=None)

        rate = mt.xirr(res.cashflows, res.portfolio.iloc[-1], res.end)
        self.assertAlmostEqual(rate, mt.cagr(res.portfolio), places=4)


class PerFundTests(unittest.TestCase):
    def test_per_fund_senza_pac_coincide_con_la_vecchia_divisione_secca(self):
        prezzi = _prezzi(400, {"A": 0.0006, "B": -0.0002})
        holdings = [
            Holding(symbol="A", label="A", weight=0.5),
            Holding(symbol="B", label="B", weight=0.5),
        ]
        res = run_backtest(prezzi, holdings, 10_000.0, Rebalance.NONE, pac=None)

        atteso = prezzi / prezzi.iloc[0] * 10_000.0
        np.testing.assert_allclose(res.per_fund["A"].to_numpy(), atteso["A"].to_numpy(), rtol=1e-9)
        np.testing.assert_allclose(res.per_fund["B"].to_numpy(), atteso["B"].to_numpy(), rtol=1e-9)

    def test_per_fund_nav_e_lo_stesso_oggetto_senza_pac(self):
        prezzi = _prezzi(120, {"A": 0.0004})
        holdings = [Holding(symbol="A", label="A", weight=1.0)]
        res = run_backtest(prezzi, holdings, 10_000.0, pac=None)
        self.assertIs(res.per_fund_nav, res.per_fund)

    def test_per_fund_nav_toglie_i_versamenti(self):
        # Prezzo piatto: il fondo non rende nulla, quindi la curva depurata
        # dai versamenti deve restare ferma al capitale iniziale mentre
        # quella grezza cresce di tutto il versato. E' la differenza che
        # rendeva "pesantemente sbagliate" le metriche della tabella.
        giorni = 400
        prezzi = pd.DataFrame(
            {"A": [100.0] * giorni}, index=pd.bdate_range("2020-01-01", periods=giorni)
        )
        holdings = [Holding(symbol="A", label="A", weight=1.0)]
        pac = Pac(amount=100.0, frequency=Frequency.MONTHLY)
        res = run_backtest(prezzi, holdings, 10_000.0, Rebalance.NONE, pac=pac)

        np.testing.assert_allclose(
            res.per_fund_nav["A"].to_numpy(), np.full(giorni, 10_000.0), rtol=1e-9
        )
        self.assertAlmostEqual(
            res.per_fund["A"].iloc[-1], res.invested.iloc[-1], places=6
        )


class PicTests(unittest.TestCase):
    def test_nessun_pic_senza_pac(self):
        prezzi = _prezzi(120, {"A": 0.0004})
        holdings = [Holding(symbol="A", label="A", weight=1.0)]
        res = run_backtest(prezzi, holdings, 10_000.0, pac=None)
        self.assertIsNone(res.pic)

    def test_pic_parte_dal_totale_versato_e_lo_fa_crescere_dal_primo_giorno(self):
        prezzi = _prezzi(400, {"A": 0.0005})
        holdings = [Holding(symbol="A", label="A", weight=1.0)]
        pac = Pac(amount=100.0, frequency=Frequency.MONTHLY)
        res = run_backtest(prezzi, holdings, 10_000.0, Rebalance.NONE, pac=pac)

        totale = float(res.invested.iloc[-1])
        self.assertAlmostEqual(res.pic.iloc[0], totale, places=6)
        # Stesso denaro, entrato prima: su una serie che sale il PIC arriva
        # piu' in alto del PAC.
        self.assertGreater(res.pic.iloc[-1], res.portfolio.iloc[-1])
        atteso = prezzi["A"] / prezzi["A"].iloc[0] * totale
        np.testing.assert_allclose(res.pic.to_numpy(), atteso.to_numpy(), rtol=1e-9)


if __name__ == "__main__":
    unittest.main()
