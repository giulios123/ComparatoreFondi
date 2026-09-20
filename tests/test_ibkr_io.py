import unittest

from comparatore.ibkr_io import IbkrParseError, parse_statement

FIXTURE = "tests/fixtures/ibkr_statement.csv"


class IbkrIoTests(unittest.TestCase):
    def test_fixture_sezioni_summary_lot_join_e_cambio(self):
        with open(FIXTURE, "rb") as handle:
            result = parse_statement(handle.read(), "U00000000_20250101_20250131.csv")

        self.assertEqual(len(result.positions), 3)
        self.assertEqual(result.base_currency, "EUR")
        self.assertEqual(result.report_end.isoformat(), "2025-01-31")
        self.assertAlmostEqual(result.fx_hints["USD"], 0.9)
        self.assertEqual(result.base_total, 325.0)
        self.assertEqual(result.skipped["lot"], 1)
        self.assertEqual(result.skipped["total"], 3)
        self.assertEqual(result.positions[0].isin, "US0378331005")
        self.assertEqual(result.positions[1].instrument_type, "ETF")
        self.assertEqual([issue.code for issue in result.issues], ["missing_instrument"])
        self.assertFalse(result.issues[0].blocking)

    def test_alias_inglesi_e_nome_file_senza_periodo(self):
        content = (
            b"Statement,Header,Field Name,Field Value\n"
            b"Statement,Data,Period,2025-02-01 - 2025-02-28\n"
            b"Account Information,Header,Field Name,Field Value\n"
            b"Account Information,Data,Base Currency,EUR\n"
            b"Open Positions,Header,DataDiscriminator,Asset Class,Currency,Symbol,"
            b"Quantity,Value,Side\n"
            b"Open Positions,Data,Summary,Stocks,EUR,AAA,2,20,Long\n"
            b"Net Asset Value,Header,Asset Class,Prior Total,Long Current,Short Current,"
            b"Current Total,Change\n"
            b"Net Asset Value,Data,Stocks,10,20,0,20,10\n"
            b"Financial Instrument Information,Header,Asset Class,Symbol,Description,"
            b"Security ID,Type\n"
            b"Financial Instrument Information,Data,Stocks,AAA,A,US0378331005,COMMON\n"
        )
        result = parse_statement(content, "statement.csv")
        self.assertEqual(len(result.positions), 1)
        self.assertEqual(result.base_currency, "EUR")
        self.assertEqual(result.report_start.isoformat(), "2025-02-01")
        self.assertEqual(result.report_end.isoformat(), "2025-02-28")
        self.assertEqual(result.positions[0].isin, "US0378331005")

    def test_rifiuta_file_privo_di_posizioni(self):
        content = b"Statement,Header,Field Name,Field Value\nStatement,Data,Base Currency,EUR\n"
        with self.assertRaises(IbkrParseError):
            parse_statement(content)

    def test_short_valore_non_positivo_e_derivato_non_diventano_posizioni(self):
        content = (
            b"Open Positions,Header,DataDiscriminator,Asset Class,Currency,Symbol,"
            b"Quantity,Value,Side\n"
            b"Open Positions,Data,Summary,Stocks,EUR,OK,1,10,Long\n"
            b"Open Positions,Data,Summary,Stocks,EUR,SHORT,1,10,Short\n"
            b"Open Positions,Data,Summary,Options,EUR,OPT,1,10,Long\n"
            b"Open Positions,Data,Summary,Stocks,EUR,ZERO,1,0,Long\n"
            b"Open Positions,Data,Summary,Stocks,EUR,,1,10,Long\n"
            b"Open Positions,Data,Summary,Stocks,,BAD,1,10,Long\n"
            b"Open Positions,Data,Summary,Cash,EUR,EUR,1,10,Long\n"
        )
        result = parse_statement(content)
        self.assertEqual([position.ticker for position in result.positions], ["OK"])
        self.assertEqual(
            {issue.code for issue in result.issues},
            {
                "missing_instrument", "unsupported_short", "unsupported_asset",
                "invalid_value", "missing_identifier", "invalid_currency",
                "cash_excluded",
            },
        )

    def test_anagrafica_duplicata_resta_avviso_e_ticker_fallback(self):
        content = (
            b"Open Positions,Header,DataDiscriminator,Asset Class,Currency,Symbol,"
            b"Quantity,Value,Side\n"
            b"Open Positions,Data,Summary,Stocks,EUR,DUP,1,10,Long\n"
            b"Open Positions,Data,Summary,Stocks,EUR,MISS,1,5,Long\n"
            b"Financial Instrument Information,Header,Asset Class,Symbol,Description,"
            b"Security ID,Type\n"
            b"Financial Instrument Information,Data,Stocks,DUP,First,US0378331005,COMMON\n"
            b"Financial Instrument Information,Data,Stocks,DUP,Second,US5949181045,COMMON\n"
        )
        result = parse_statement(content)
        self.assertEqual(result.positions[0].identifier, "ticker:DUP:EUR")
        self.assertEqual(result.positions[1].identifier, "ticker:MISS:EUR")
        self.assertEqual(
            {(issue.code, issue.blocking) for issue in result.issues},
            {("ambiguous_instrument", False), ("missing_instrument", False)},
        )


if __name__ == "__main__":
    unittest.main()
