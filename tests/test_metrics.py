import unittest

import pandas as pd

from comparatore import metrics as mt

CHIAVI_ATTESE = {
    "final_value", "total_return", "cagr", "volatility", "sharpe", "sortino",
    "max_drawdown", "calmar", "best_year", "worst_year",
}


class TestSummarizeKeys(unittest.TestCase):
    def test_le_chiavi_sono_id_inglesi_stabili(self):
        # Queste chiavi diventano nomi di colonna e chiavi di lookup nelle
        # etichette tradotte dell'interfaccia (comparatore.i18n.METRICHE):
        # un revert bene intenzionato a stringhe italiane romperebbe quel
        # collegamento in silenzio.
        curva = pd.Series(
            [100.0, 105.0, 98.0, 110.0],
            index=pd.date_range("2020-01-01", periods=4, freq="YE"),
        )
        self.assertEqual(set(mt.summarize(curva)), CHIAVI_ATTESE)


if __name__ == "__main__":
    unittest.main()
