import unittest

import numpy as np
import pandas as pd

from comparatore import analytics, metrics


class AnalyticsTests(unittest.TestCase):
    def test_ulcer_index_penalizza_la_durata_del_drawdown(self):
        curve = pd.Series(
            [100.0, 90.0, 90.0, 100.0],
            index=pd.date_range("2020-01-01", periods=4, freq="D"),
        )
        self.assertAlmostEqual(metrics.ulcer_index(curve), np.sqrt(0.02 / 4))

    def test_sortino_include_i_periodi_sopra_soglia_nel_denominatore(self):
        curve = pd.Series(
            [100.0, 110.0, 99.0, 108.9],
            index=pd.date_range("2020-01-01", periods=4, freq="D"),
        )
        expected = (0.1 - 0.1 + 0.1) / 3 / np.sqrt(0.1**2 / 3) * np.sqrt(252)
        self.assertAlmostEqual(metrics.sortino(curve), expected)

    def test_heatmap_compone_i_mesi_e_l_anno(self):
        index = pd.to_datetime(["2020-01-15", "2020-01-31"] + [
            f"2020-{month:02d}-28" for month in range(2, 13)
        ] + ["2021-01-31", "2021-02-28"])
        values = [100.0, 110.0]
        values.extend([110.0 * 1.1**month for month in range(1, 12)])
        values.extend([110.0 * 1.1**12, 110.0 * 1.1**13])
        curve = pd.Series(values, index=index)
        result = analytics.calendar_heatmap(curve, show_all=True)
        self.assertAlmostEqual(result.monthly.loc[2020, 1], 0.1)
        self.assertAlmostEqual(result.monthly.loc[2020, 2], 0.1)
        self.assertAlmostEqual(result.annual.loc[2020], 1.1**12 - 1)
        self.assertIn(pd.Timestamp("2020-01-31"), result.partial_months)

    def test_rolling_giornaliero_usa_il_pregresso_e_non_comprime_i_buchi(self):
        index = pd.bdate_range("2019-01-01", "2022-12-30")
        values = pd.Series(100.0 * 1.0002 ** np.arange(len(index)), index=index)
        rolling = analytics.rolling_metric(values, 1, "cagr")
        self.assertGreater(len(rolling), 700)
        self.assertTrue((rolling > 0).all())

        broken = values.drop(index[(index >= "2020-06-01") & (index <= "2020-07-31")])
        invalid = analytics.rolling_metric(broken, 1, "cagr")
        self.assertFalse(
            any(
                pd.Timestamp("2020-06-01") <= date <= pd.Timestamp("2021-07-31")
                for date in invalid.index
            )
        )

    def test_rolling_annuale_si_ferma_a_dicembre(self):
        index = pd.bdate_range("2018-01-01", "2022-12-30")
        values = pd.Series(100.0 * 1.0002 ** np.arange(len(index)), index=index)
        rolling = analytics.rolling_metric(values, 1, "cagr", mode="annual")
        self.assertTrue(len(rolling) >= 3)
        self.assertTrue(all(date.month == 12 for date in rolling.index))

    def test_annuale_non_accetta_dicembre_troncato(self):
        index = pd.to_datetime(["2020-12-30", "2021-12-20", "2022-12-20"])
        curve = pd.Series([100.0, 110.0, 121.0], index=index)
        annual = analytics.rolling_metric(curve, 1, mode="annual")
        self.assertTrue(annual.empty)

    def test_heatmap_non_marca_anno_completo_come_parziale(self):
        index = pd.date_range("2020-01-01", periods=24, freq="ME")
        curve = pd.Series(np.arange(1.0, 25.0), index=index)
        result = analytics.calendar_heatmap(curve, show_all=True)
        self.assertNotIn(2021, result.partial_years)

    def test_finestra_usa_il_giorno_piu_vicino_in_un_anno_bisestile(self):
        index = pd.to_datetime(["2020-02-29", "2020-03-31", "2021-02-28"])
        curve = pd.Series([100.0, 110.0, 120.0], index=index)
        rolling = analytics.rolling_metric(curve, 1, "cagr")
        self.assertIn(pd.Timestamp("2021-02-28"), rolling.index)

    def test_rolling_esponde_copertura_e_motivo_se_vuoto(self):
        curve = pd.Series(
            [100.0, 101.0],
            index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
        )
        rolling = analytics.rolling_metric(curve, 20, "cagr")
        self.assertEqual(rolling.attrs["reason"], "insufficient_history_or_gaps")
        self.assertEqual(rolling.attrs["coverage"], (curve.index[0], curve.index[-1]))


if __name__ == "__main__":
    unittest.main()
