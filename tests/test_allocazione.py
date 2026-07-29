import unittest

from comparatore import allocazione as al

# Estratto di una risposta EODHD `/fundamentals` per un ETF azionario: e' la
# forma che il parser deve reggere, con le percentuali annidate in dizionari e
# scritte come stringhe.
ETF_DATA = {
    "NetExpenseRatio": "0.2200",
    "Asset_Allocation": {
        "Cash": {"Long_%": "0.31", "Short_%": "0", "Net_Assets_%": "0.31"},
        "Stock US": {"Long_%": "62.11", "Short_%": "0", "Net_Assets_%": "62.11"},
        "Stock non-US": {"Long_%": "37.42", "Short_%": "0", "Net_Assets_%": "37.42"},
        "Bond": {"Long_%": "0", "Short_%": "0", "Net_Assets_%": "0"},
        "NotClassified": {"Long_%": "0.16", "Short_%": "0", "Net_Assets_%": "0.16"},
    },
    "World_Regions": {
        "North America": {"Equity_%": "64.20", "Relative_to_Category": "1.02"},
        "Japan": {"Equity_%": "6.10", "Relative_to_Category": "0.98"},
        "Europe Developed": {"Equity_%": "13.50", "Relative_to_Category": "1.00"},
        "United Kingdom": {"Equity_%": "3.70", "Relative_to_Category": "1.00"},
        "Asia Emerging": {"Equity_%": "8.50", "Relative_to_Category": "1.10"},
        "Latin America": {"Equity_%": "1.00", "Relative_to_Category": "0.90"},
        "Australasia": {"Equity_%": "3.00", "Relative_to_Category": "1.00"},
    },
    "Sector_Weights": {
        "Technology": {"Equity_%": "25.00", "Relative_to_Category": "1.05"},
        "Financial Services": {"Equity_%": "15.00", "Relative_to_Category": "1.00"},
        "Healthcare": {"Equity_%": "10.00", "Relative_to_Category": "0.95"},
    },
}


class ClassificaDaNomeTests(unittest.TestCase):
    def _prevalenti(self, nome: str, quote_type: str = "ETF") -> tuple[str, str, str]:
        alloc = al.classifica_da_nome(nome, quote_type=quote_type)
        return tuple(
            al.etichetta_prevalente(alloc[d]) for d in al.DIMENSIONI
        )

    def test_bond_wins_over_the_region_it_mentions(self) -> None:
        # Il caso che una tabella unica ordinata sbaglierebbe: senza tabelle per
        # dimensione, "Eurozone" catturerebbe il fondo come azionario europeo.
        classe, area, _ = self._prevalenti("Xtrackers II Eurozone Government Bond")
        self.assertEqual(classe, "Obbligazionario")
        self.assertEqual(area, "Europa")

    def test_money_market_is_not_read_as_a_bond(self) -> None:
        classe, _, _ = self._prevalenti("Amundi US Treasury Bill 0-1Y")
        self.assertEqual(classe, "Liquidità")

    def test_world_ex_us_stays_global(self) -> None:
        _, area, _ = self._prevalenti("Vanguard FTSE All-World ex-US")
        self.assertEqual(area, "Globale")

    def test_sector_fund_keeps_class_area_and_sector(self) -> None:
        self.assertEqual(
            self._prevalenti("Xtrackers MSCI World Information Technology"),
            ("Azionario", "Globale", "Tecnologia"),
        )

    def test_sector_is_left_out_for_non_equity(self) -> None:
        # Chiedersi in che settore investa un ETC sull'oro non porta da nessuna
        # parte: meglio dichiararlo non classificato.
        classe, _, settore = self._prevalenti("iShares Physical Gold ETC")
        self.assertEqual(classe, "Materie prime")
        self.assertEqual(settore, al.NON_CLASSIFICATO)

    def test_single_stock_is_equity_even_without_keywords(self) -> None:
        classe, _, _ = self._prevalenti("Apple Inc.", quote_type="EQUITY")
        self.assertEqual(classe, "Azionario")

    def test_unrecognisable_name_is_not_guessed(self) -> None:
        self.assertEqual(
            self._prevalenti("LU0292107645", quote_type="MUTUALFUND"),
            (al.NON_CLASSIFICATO, al.NON_CLASSIFICATO, al.NON_CLASSIFICATO),
        )

    def test_every_bucket_returned_is_part_of_the_vocabulary(self) -> None:
        # Un bucket fuori vocabolario non comparirebbe fra le opzioni della
        # tendina, e la correzione manuale diventerebbe impossibile.
        for nome in ["iShares Core MSCI Europe", "Amundi MSCI Emerging Markets",
                     "iShares Global Clean Energy", "SPDR Dow Jones Global Real Estate",
                     "Vanguard FTSE All-World"]:
            alloc = al.classifica_da_nome(nome)
            for dimensione in al.DIMENSIONI:
                for bucket in alloc[dimensione]:
                    self.assertIn(bucket, al.BUCKET[dimensione], f"{nome}/{dimensione}")


class ClassificaDaEodhdTests(unittest.TestCase):
    def test_asset_allocation_collapses_into_the_italian_buckets(self) -> None:
        alloc = al.classifica_da_eodhd(ETF_DATA)
        classe = alloc["classe"]
        # "Stock US" e "Stock non-US" confluiscono nello stesso bucket.
        self.assertAlmostEqual(classe["Azionario"], 0.9953, places=3)
        self.assertAlmostEqual(classe["Liquidità"], 0.0031, places=3)
        self.assertAlmostEqual(sum(classe.values()), 1.0, places=9)
        self.assertNotIn("Obbligazionario", classe)  # quota zero, non un bucket

    def test_regions_keep_more_than_one_bucket(self) -> None:
        # E' la ragione per cui il modello e' una distribuzione e non
        # un'etichetta: un fondo mondiale non e' "100% Nord America".
        area = al.classifica_da_eodhd(ETF_DATA)["area"]
        self.assertEqual(al.etichetta_prevalente(area), "Nord America")
        self.assertGreater(len(area), 1)
        self.assertAlmostEqual(area["Europa"], 0.172, places=3)  # UK + Europe Developed
        self.assertAlmostEqual(sum(area.values()), 1.0, places=9)

    def test_relative_to_category_is_never_read_as_a_weight(self) -> None:
        settore = al.classifica_da_eodhd(ETF_DATA)["settore"]
        self.assertAlmostEqual(settore["Tecnologia"], 0.5, places=9)

    def test_unknown_keys_land_in_non_classificato(self) -> None:
        alloc = al.classifica_da_eodhd(
            {"Asset_Allocation": {"Convertible": {"Net_Assets_%": "100"}}}
        )
        self.assertEqual(alloc["classe"], {al.NON_CLASSIFICATO: 1.0})

    def test_missing_blocks_are_omitted_not_invented(self) -> None:
        # Un obbligazionario non ha `Sector_Weights`: la dimensione deve restare
        # fuori, cosi' il ripiego sul nome puo' intervenire.
        alloc = al.classifica_da_eodhd(
            {"Asset_Allocation": {"Bond": {"Net_Assets_%": "100"}}}
        )
        self.assertEqual(set(alloc), {"classe"})

    def test_malformed_payloads_never_raise(self) -> None:
        for payload in [None, {}, [], "", {"Asset_Allocation": None},
                        {"Asset_Allocation": []},
                        {"World_Regions": {"Japan": None}},
                        {"World_Regions": {"Japan": {"Relative_to_Category": "1.0"}}},
                        {"Sector_Weights": {"Energy": "n/d"}},
                        {"Asset_Allocation": {"Cash": {"Net_Assets_%": "0"}}}]:
            self.assertEqual(al.classifica_da_eodhd(payload), {}, repr(payload))

    def test_plain_numbers_and_percent_strings_are_both_accepted(self) -> None:
        alloc = al.classifica_da_eodhd(
            {"Asset_Allocation": {"Bond": 60, "Stock US": "40%"}}
        )
        self.assertAlmostEqual(alloc["classe"]["Obbligazionario"], 0.6, places=9)
        self.assertAlmostEqual(alloc["classe"]["Azionario"], 0.4, places=9)


class RisolviTests(unittest.TestCase):
    def test_manual_choice_collapses_the_distribution(self) -> None:
        auto = {"Nord America": 0.6, "Europa": 0.4}
        self.assertEqual(al.risolvi(auto, "Europa"), {"Europa": 1.0})

    def test_the_sentinel_keeps_the_inferred_distribution(self) -> None:
        auto = {"Nord America": 0.6, "Europa": 0.4}
        self.assertEqual(al.risolvi(auto, al.AUTOMATICA), auto)
        self.assertEqual(al.risolvi(auto, ""), auto)

    def test_nothing_inferred_falls_back_to_non_classificato(self) -> None:
        self.assertEqual(al.risolvi(None, ""), {al.NON_CLASSIFICATO: 1.0})


class AggregaTests(unittest.TestCase):
    def test_weights_are_normalised_like_the_backtest_does(self) -> None:
        # I pesi sommano a 97: la torta deve comunque chiudere al 100%.
        quote = al.aggrega(
            {"A": 60.0, "B": 37.0},
            {"A": {"Azionario": 1.0}, "B": {"Obbligazionario": 1.0}},
        )
        self.assertAlmostEqual(sum(quote.values()), 1.0, places=9)
        self.assertAlmostEqual(quote["Azionario"], 60 / 97, places=9)

    def test_distributions_are_combined_across_instruments(self) -> None:
        quote = al.aggrega(
            {"A": 50.0, "B": 50.0},
            {
                "A": {"Nord America": 0.6, "Europa": 0.4},
                "B": {"Europa": 1.0},
            },
        )
        self.assertAlmostEqual(quote["Europa"], 0.7, places=9)
        self.assertAlmostEqual(quote["Nord America"], 0.3, places=9)

    def test_result_is_ordered_by_decreasing_share(self) -> None:
        quote = al.aggrega(
            {"A": 10.0, "B": 60.0, "C": 30.0},
            {"A": {"Liquidità": 1.0}, "B": {"Azionario": 1.0},
             "C": {"Obbligazionario": 1.0}},
        )
        self.assertEqual(list(quote), ["Azionario", "Obbligazionario", "Liquidità"])

    def test_an_unclassified_instrument_still_takes_up_its_share(self) -> None:
        # Scartarlo calcolerebbe le percentuali su un portafoglio piu' piccolo
        # di quello vero, gonfiando tutte le altre voci.
        quote = al.aggrega({"A": 50.0, "B": 50.0}, {"A": {"Azionario": 1.0}})
        self.assertAlmostEqual(quote["Azionario"], 0.5, places=9)
        self.assertAlmostEqual(quote[al.NON_CLASSIFICATO], 0.5, places=9)

    def test_zero_and_negative_weights_are_ignored(self) -> None:
        quote = al.aggrega(
            {"A": 100.0, "B": 0.0}, {"A": {"Azionario": 1.0}, "B": {"Liquidità": 1.0}}
        )
        self.assertEqual(quote, {"Azionario": 1.0})

    def test_no_weight_at_all_gives_an_empty_breakdown(self) -> None:
        self.assertEqual(al.aggrega({}, {}), {})
        self.assertEqual(al.aggrega({"A": 0.0}, {"A": {"Azionario": 1.0}}), {})


class DescriviTests(unittest.TestCase):
    def test_a_single_bucket_is_shown_bare(self) -> None:
        self.assertEqual(al.descrivi({"Azionario": 1.0}), "Azionario")

    def test_several_buckets_are_listed_with_their_share(self) -> None:
        self.assertEqual(
            al.descrivi({"Nord America": 0.62, "Europa": 0.38}),
            "Nord America 62% · Europa 38%",
        )

    def test_the_tail_is_counted_not_listed(self) -> None:
        self.assertEqual(
            al.descrivi(
                {"A": 0.4, "B": 0.3, "C": 0.2, "D": 0.05, "E": 0.05}, max_voci=3
            ),
            "A 40% · B 30% · C 20% · +2",
        )

    def test_nothing_to_describe(self) -> None:
        self.assertEqual(al.descrivi(None), al.NON_CLASSIFICATO)
        self.assertEqual(al.descrivi({}), al.NON_CLASSIFICATO)


class UnisciTests(unittest.TestCase):
    def test_the_fallback_only_fills_the_missing_dimensions(self) -> None:
        # E' il caso reale dell'obbligazionario: EODHD da' classe e area, il
        # settore resta quello dedotto dal nome.
        unito = al.unisci(
            {"classe": {"Obbligazionario": 1.0}, "area": {"Europa": 1.0}},
            {"classe": {"Azionario": 1.0}, "area": {"Globale": 1.0},
             "settore": {al.NON_CLASSIFICATO: 1.0}},
        )
        self.assertEqual(unito["classe"], {"Obbligazionario": 1.0})
        self.assertEqual(unito["settore"], {al.NON_CLASSIFICATO: 1.0})


class VocabolarioTests(unittest.TestCase):
    def test_every_dimension_has_options_led_by_the_sentinel(self) -> None:
        for dimensione in al.DIMENSIONI:
            self.assertEqual(al.OPZIONI[dimensione][0], al.AUTOMATICA)
            self.assertEqual(al.OPZIONI[dimensione][1:], al.BUCKET[dimensione])
            self.assertIn(al.NON_CLASSIFICATO, al.BUCKET[dimensione])

    def test_eodhd_maps_only_point_at_known_buckets(self) -> None:
        for mappa, dimensione in (
            (al._EODHD_CLASSI, "classe"),
            (al._EODHD_AREE, "area"),
            (al._EODHD_SETTORI, "settore"),
        ):
            for bucket in mappa.values():
                self.assertIn(bucket, al.BUCKET[dimensione])

    def test_name_patterns_only_point_at_known_buckets(self) -> None:
        for patterns, dimensione in (
            (al._CLASSI_PATTERNS, "classe"),
            (al._AREE_PATTERNS, "area"),
            (al._SETTORI_PATTERNS, "settore"),
        ):
            for _, bucket in patterns:
                self.assertIn(bucket, al.BUCKET[dimensione])


if __name__ == "__main__":
    unittest.main()
