import io
import unittest

import pandas as pd

from comparatore.directa_io import (
    DirectaColumnMap,
    DirectaParseError,
    detect_export_kind,
    parse_number,
    parse_positions,
    read_table,
    suggest_header_row,
)


class DirectaIoTests(unittest.TestCase):
    def test_parse_number_local_and_international(self):
        self.assertEqual(parse_number("1.234,56 €"), 1234.56)
        self.assertEqual(parse_number("1,234.56"), 1234.56)
        self.assertEqual(parse_number("(12,50)"), -12.5)
        self.assertEqual(parse_number("11,618", prefer_decimal=True), 11.618)

    def test_parse_positions_validates_and_aggregates_isin(self):
        frame = pd.DataFrame(
            {
                "ISIN": ["IE00B3XXRP09", "IE00B3XXRP09", "bad"],
                "Valore": ["1.000,00", "500,00", "10"],
                "Nome": ["ETF", "ETF", "X"],
            }
        )
        result = parse_positions(frame, DirectaColumnMap("Valore", isin="ISIN", name="Nome"))
        self.assertEqual(len(result.positions), 1)
        self.assertEqual(result.positions[0].current_value, 1500)
        self.assertEqual(len(result.issues), 1)

    def test_identifier_and_value_are_required(self):
        frame = pd.DataFrame({"Value": [100]})
        with self.assertRaises(DirectaParseError):
            parse_positions(frame, DirectaColumnMap("Value"))

    def test_read_csv_detects_semicolon_and_encoding(self):
        content = "ISIN;Valore\nIE00B3XXRP09;1.234,50\n".encode("cp1252")
        frame = read_table(content, "directa.csv")
        self.assertEqual(frame.iloc[0, 1], "1.234,50")

    def test_read_xlsx(self):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pd.DataFrame({"ISIN": ["IE00B3XXRP09"], "Value": [10]}).to_excel(
                writer, index=False
            )
        frame = read_table(output.getvalue(), "directa.xlsx")
        self.assertEqual(frame.iloc[0, 0], "IE00B3XXRP09")

    def test_campione_movimenti_trova_intestazione_e_non_e_posizioni(self):
        content = (
            "Conto : campione;;;;;;;;;;;\n"
            "Data estrazione : 10-8-2026 17:59:28;;;;;;;;;;;\n"
            ";;;;;;;;;;;\n"
            "Tutti i movimenti ordinati per Data Operazione;;;;;;;;;;;\n"
            "Dal : 03-08-2026;;;;;;;;;;;\n"
            "al : 10-08-2026;;;;;;;;;;;\n"
            ";;;;;;;;;;;\n"
            "Il file include i primi 3000 movimenti;;;;;;;;;;;\n"
            ";;;;;;;;;;;\n"
            "Data operazione;Data valuta;Tipo operazione;Ticker;Isin;"
            "Protocollo;Descrizione;Quantità;Importo euro;Importo Divisa;"
            "Divisa;Riferimento ordine\n"
            "10-08-2026;12-08-2026;Acquisto;IMIE;IE00B3YLTY66;;"
            "SPDR MSCI All Country World In;40;-464,72;0;EUR;123\n"
            "10-08-2026;12-08-2026;Commissioni;IMIE;IE00B3YLTY66;;"
            "SPDR MSCI All Country World In;0;-1,5;0;EUR;123\n"
            "09-08-2026;09-08-2026;Conferimento con bonifico;;;19317133;;"
            "0;500;0;EUR;\n"
        ).encode("utf-8-sig")
        self.assertEqual(suggest_header_row(content, "Movimenti.csv"), 9)
        frame = read_table(content, "Movimenti.csv", header_row=9)
        self.assertEqual(detect_export_kind(frame), "movements")
        result = parse_positions(
            frame,
            DirectaColumnMap(
                "Importo euro", isin="Isin", ticker="Ticker", name="Descrizione",
                currency="Divisa", quantity="Quantità",
            ),
            header_row=9,
        )
        self.assertFalse(result.positions)
        self.assertEqual([issue.row for issue in result.issues], [11, 12, 13])

    def test_header_alias_con_accenti_e_posizioni(self):
        frame = pd.DataFrame(
            {"Ticker": ["VWCE.MI"], "Controvalore attuale": ["1.000,00"], "Quantità": [2]}
        )
        self.assertEqual(detect_export_kind(frame), "positions")

    def test_campione_posizioni_trova_valore_attuale_e_totale(self):
        content = (
            "Portafoglio : TOTALE;;;;;;;;;;;;;;\n"
            "Conto : campione;;;;;;;;;;;;;;\n"
            "Data estrazione : 2026/08/10 18:0:6;;;;;;;;;;;;;;\n"
            ";;;;;;;;;;;;;;\n"
            "Valore portafoglio : 464,64€;;;;;;;;;;;;;;\n"
            ";;;;;;;;;;;;;;\n"
            ";;;;;;;;;;;;;;\n"
            "Strumento;Ticker;Isin;Prezzo;Trend %;Quantita;Valore di carico;"
            "Valore attuale;Gain/Loss €;Gain/Loss %;Gain/Loss € Intraday;"
            "Prezzo medio;Bid;Ask;Divisa\n"
            "SPDR MSCI All Country World Investable;IMIE;IE00B3YLTY66;"
            "11,616;0,03;40;464,72;464,64;-0,08;-0,02;0,16;11,618;0;0;EUR\n"
            ";;;;;;464,72;464,64;-0,08;-0,02;0,16;;;;\n"
        ).encode("utf-8-sig")
        self.assertEqual(suggest_header_row(content, "P_TOTALE.csv"), 7)
        frame = read_table(content, "P_TOTALE.csv", header_row=7)
        self.assertEqual(detect_export_kind(frame), "positions")
        result = parse_positions(
            frame,
            DirectaColumnMap(
                "Valore attuale", isin="Isin", ticker="Ticker", name="Strumento",
                currency="Divisa", quantity="Quantita", average_price="Prezzo medio",
            ),
            header_row=7,
        )
        self.assertEqual(len(result.positions), 1)
        self.assertAlmostEqual(result.positions[0].current_value, 464.64)
        self.assertAlmostEqual(result.positions[0].average_price, 11.618)
        self.assertEqual([issue.row for issue in result.issues], [10])
        self.assertEqual(result.issues[0].code, "summary_row")


if __name__ == "__main__":
    unittest.main()
