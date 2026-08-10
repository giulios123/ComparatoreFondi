import io
import unittest

import pandas as pd

from comparatore.directa_io import (
    DirectaColumnMap,
    DirectaParseError,
    parse_number,
    parse_positions,
    read_table,
)


class DirectaIoTests(unittest.TestCase):
    def test_parse_number_local_and_international(self):
        self.assertEqual(parse_number("1.234,56 €"), 1234.56)
        self.assertEqual(parse_number("1,234.56"), 1234.56)
        self.assertEqual(parse_number("(12,50)"), -12.5)

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


if __name__ == "__main__":
    unittest.main()
