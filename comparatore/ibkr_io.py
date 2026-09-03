"""Lettura pura dei rendiconti Activity Statement di Interactive Brokers.

Il CSV di IBKR non e' una tabella: ogni sezione ha la propria intestazione e
le righe possono avere un numero diverso di colonne. Qui si isolano le
posizioni `Summary` e l'anagrafica degli strumenti, lasciando fuori movimenti,
liquidita' e dettagli contabili che appartengono a un registro diverso.
"""

from __future__ import annotations

import csv
import datetime as dt
import io
import math
import re
from dataclasses import dataclass, field

from .directa_io import normalizza_intestazione, parse_number
from .sources.base import is_isin


class IbkrParseError(ValueError):
    """Rendiconto IBKR vuoto o privo di una sezione di posizioni leggibile."""


@dataclass(frozen=True)
class IbkrPosition:
    """Posizione normalizzata dal riepilogo `Open Positions`."""

    row: int
    identifier: str
    asset_type: str = ""
    instrument_type: str = ""
    ticker: str = ""
    isin: str = ""
    name: str = ""
    exchange: str = ""
    currency: str = ""
    current_value: float = 0.0
    quantity: float | None = None
    average_price: float | None = None


@dataclass(frozen=True)
class IbkrIssue:
    """Diagnosi associata a una riga, con blocco distinto dagli avvisi."""

    row: int
    column: str
    message: str
    code: str = ""
    blocking: bool = True


@dataclass(frozen=True)
class IbkrTotal:
    """Totale letto da una sezione, utile per la riconciliazione visibile."""

    row: int
    asset_type: str
    currency: str
    value: float


@dataclass(frozen=True)
class IbkrImportResult:
    """Risultato serializzabile solo in memoria: niente dati del conto."""

    positions: tuple[IbkrPosition, ...]
    issues: tuple[IbkrIssue, ...] = field(default_factory=tuple)
    base_currency: str = ""
    report_start: dt.date | None = None
    report_end: dt.date | None = None
    native_totals: dict[str, float] = field(default_factory=dict)
    base_total: float | None = None
    fx_hints: dict[str, float] = field(default_factory=dict)
    totals: tuple[IbkrTotal, ...] = field(default_factory=tuple)
    skipped: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class _Header:
    section: str
    fields: dict[str, int]


_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
_FILENAME_DATE_RE = re.compile(r"(?<!\d)(20\d{6})(?!\d)")
_MONTHS = {
    # IBKR localizza il periodo, mentre il nome del file resta numerico.
    "january": 1, "janvier": 1, "januar": 1, "gennaio": 1,
    "february": 2, "fevrier": 2, "februar": 2, "febbraio": 2,
    "march": 3, "mars": 3, "marz": 3, "marzo": 3,
    "april": 4, "avril": 4, "aprile": 4,
    "may": 5, "mai": 5, "maggio": 5,
    "june": 6, "juin": 6, "juni": 6, "giugno": 6,
    "july": 7, "juillet": 7, "juli": 7, "luglio": 7,
    "august": 8, "aout": 8, "augusto": 8, "agosto": 8,
    "september": 9, "septembre": 9, "settembre": 9,
    "october": 10, "octobre": 10, "oktober": 10, "ottobre": 10,
    "november": 11, "novembre": 11,
    "december": 12, "decembre": 12, "dezember": 12, "dicembre": 12,
}
_SUMMARY_VALUES = {"summary", "riepilogo"}
_LOT_VALUES = {"lot", "lotto"}
_TOTAL_VALUES = {"total", "totale"}
_HEADER_VALUES = {"header", "intestazione"}
_DATA_VALUES = {"data", "dati"}
_DERIVATIVE_HINTS = {
    "bond", "bonds", "obbligazioni", "options", "option", "opzioni",
    "future", "futures", "futuro", "warrant", "warrants", "cfd", "forex",
    "derivative", "derivatives", "derivato", "derivati",
}
_CASH_HINTS = {"cash", "cassa", "cashbalance", "cashandcash", "liquidity", "liquidita"}


def _text(value) -> str:
    return "" if value is None else str(value).strip()


def _norm(value) -> str:
    return normalizza_intestazione(_text(value))


def _decode_csv(content: bytes | str) -> str:
    if isinstance(content, str):
        return content
    for encoding in ("utf-8-sig", "cp1252", "latin1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise IbkrParseError("Codifica del CSV IBKR non riconosciuta.")


def _delimiter(text: str) -> str:
    try:
        return csv.Sniffer().sniff(text[:8192], delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def _fields(row: list[str]) -> dict[str, int]:
    fields: dict[str, int] = {}
    for index, value in enumerate(row[2:], start=2):
        key = _norm(value)
        if key and key not in fields:
            fields[key] = index
    return fields


def _find(fields: dict[str, int], *aliases: str) -> int | None:
    for alias in aliases:
        key = _norm(alias)
        if key in fields:
            return fields[key]
    return None


def _find_contains(fields: dict[str, int], *parts: str) -> int | None:
    normalized = tuple(_norm(part) for part in parts)
    for key, index in fields.items():
        if any(part and part in key for part in normalized):
            return index
    return None


def _position_header(row: list[str]) -> _Header | None:
    fields = _fields(row)
    required = {
        "detail": _find(fields, "DataDiscriminator", "Level of Detail", "Livello di dettaglio"),
        "asset": _find(
            fields, "Tipo di attivo", "Classe di attività", "Asset Category",
            "Asset Class", "Classe di asset",
        ),
        "currency": _find(fields, "Valuta", "Currency"),
        "symbol": _find(fields, "Simbolo", "Symbol"),
        "quantity": _find(fields, "Quantità", "Quantity"),
        "value": _find(fields, "Valore", "Value", "Position Value", "Market Value"),
    }
    if any(value is None for value in required.values()):
        return None
    optional = {
        "isin": _find(fields, "ISIN"),
        "security_id": _find(fields, "ID titolo", "Security ID"),
        "name": _find(fields, "Descrizione", "Description"),
        "exchange": _find(fields, "Mercato finanziario", "Listing Exch", "Exchange"),
        "average": _find(fields, "Prezzo di costo", "Cost Basis Price", "Open Price"),
        "side": _find(fields, "Side", "Lato"),
        "fx_rate": _find(fields, "FX Rate to Base"),
    }
    return _Header(row[0], {**required, **optional})


def _instrument_header(row: list[str]) -> _Header | None:
    fields = _fields(row)
    required = {
        "asset": _find(
            fields, "Tipo di attivo", "Classe di attività", "Asset Category", "Asset Class"
        ),
        "symbol": _find(fields, "Simbolo", "Symbol"),
        "description": _find(fields, "Descrizione", "Description"),
        "security_id": _find(fields, "ID titolo", "Security ID", "ISIN"),
        "type": _find(fields, "Tipo", "Type"),
    }
    if any(value is None for value in required.values()):
        return None
    return _Header(row[0], required | {
        "isin": _find(fields, "ISIN"),
        "exchange": _find(fields, "Mercato finanziario", "Listing Exch", "Exchange"),
    })


def _nav_header(row: list[str]) -> _Header | None:
    fields = _fields(row)
    asset = _find(
        fields, "Classe di asset", "Classe di attività", "Asset Class", "Asset Category"
    )
    current = _find(fields, "Totale corrente", "Current Total", "Current Value")
    if asset is None or current is None:
        return None
    return _Header(row[0], {"asset": asset, "current": current})


def _account_header(row: list[str]) -> _Header | None:
    fields = _fields(row)
    field_name = _find(fields, "Nome del campo", "Field Name", "Name")
    value = _find(fields, "Valore del campo", "Valore del cmapo", "Field Value", "Value")
    if field_name is None or value is None:
        return None
    return _Header(row[0], {"field": field_name, "value": value})


def _date_from_text(value: str) -> dt.date | None:
    text = _text(value)
    for pattern in (
        r"(?<!\d)(\d{4})[/-](\d{1,2})[/-](\d{1,2})(?!\d)",
        r"(?<!\d)(\d{1,2})[./-](\d{1,2})[./-](\d{4})(?!\d)",
    ):
        matches = list(re.finditer(pattern, text))
        match = matches[-1] if matches else None
        if match:
            groups = [int(item) for item in match.groups()]
            y, m, d = groups if len(str(groups[0])) == 4 else (groups[2], groups[1], groups[0])
            try:
                return dt.date(y, m, d)
            except ValueError:
                return None
    month_pattern = re.compile(
        r"([A-Za-zÀ-ÿ]+)\s+(\d{1,2}),?\s+(\d{4})", re.IGNORECASE
    )
    matches = list(month_pattern.finditer(text))
    if matches:
        match = matches[-1]
        month = _MONTHS.get(_norm(match.group(1)))
        if month:
            try:
                return dt.date(int(match.group(3)), month, int(match.group(2)))
            except ValueError:
                return None
    reverse_pattern = re.compile(
        r"(\d{1,2})[.]?\s+([A-Za-zÀ-ÿ]+)\s+(\d{4})", re.IGNORECASE
    )
    matches = list(reverse_pattern.finditer(text))
    if matches:
        match = matches[-1]
        month = _MONTHS.get(_norm(match.group(2)))
        if month:
            try:
                return dt.date(int(match.group(3)), month, int(match.group(1)))
            except ValueError:
                return None
    return None


def _filename_dates(filename: str) -> tuple[dt.date | None, dt.date | None]:
    filename = _text(filename)
    dates = []
    for match in _FILENAME_DATE_RE.findall(filename):
        try:
            dates.append(dt.datetime.strptime(match, "%Y%m%d").date())
        except ValueError:
            continue
    if not dates:
        return None, None
    return min(dates), max(dates)


def _row_value(row: list[str], index: int | None) -> str:
    return _text(row[index]) if index is not None and index < len(row) else ""


def _is_derivative(asset_type: str, instrument_type: str) -> bool:
    values = {_norm(asset_type), _norm(instrument_type)}
    return any(
        hint in value
        for value in values if value
        for hint in _DERIVATIVE_HINTS
    )


def _is_cash(asset_type: str, instrument_type: str) -> bool:
    values = {_norm(asset_type), _norm(instrument_type)}
    return any(
        hint in value
        for value in values if value
        for hint in _CASH_HINTS
    )


def _currency(value: str) -> str:
    candidate = _text(value).upper()
    return candidate if _CURRENCY_RE.fullmatch(candidate) else ""


def _parse_account_value(pairs: list[tuple[str, str]], *parts: str) -> str:
    normalized_parts = tuple(_norm(part) for part in parts)
    for field_name, value in pairs:
        normalized = _norm(field_name)
        if normalized and all(part in normalized for part in normalized_parts):
            return _text(value)
    return ""


def parse_statement(content: bytes | str, filename: str = "statement.csv") -> IbkrImportResult:
    """Normalizza le posizioni correnti senza importare la cronologia."""
    if not content:
        raise IbkrParseError("Il file IBKR e' vuoto.")
    try:
        text = _decode_csv(content)
        rows = [list(row) for row in csv.reader(io.StringIO(text), delimiter=_delimiter(text))]
    except IbkrParseError:
        raise
    except Exception as exc:
        raise IbkrParseError("Il rendiconto IBKR non e' leggibile.") from exc
    if not rows:
        raise IbkrParseError("Il rendiconto IBKR non contiene righe.")

    active_position: _Header | None = None
    active_instrument: _Header | None = None
    active_nav: _Header | None = None
    active_account: _Header | None = None
    raw_positions: list[tuple[int, list[str], _Header]] = []
    raw_instruments: list[tuple[int, list[str], _Header]] = []
    raw_nav: list[tuple[int, list[str], _Header]] = []
    account_pairs: list[tuple[str, str]] = []
    totals: list[IbkrTotal] = []
    skipped: dict[str, int] = {}
    statement_period = ""

    for line_number, row in enumerate(rows, start=1):
        if len(row) < 2:
            continue
        row_type = _norm(row[1])
        section = row[0]
        section_key = _norm(section)
        if row_type in _HEADER_VALUES:
            active_position = _position_header(row)
            active_instrument = _instrument_header(row)
            active_nav = _nav_header(row)
            active_account = _account_header(row)
            continue
        if active_position and section_key == _norm(active_position.section):
            if row_type in _DATA_VALUES:
                raw_positions.append((line_number, row, active_position))
            elif row_type in _LOT_VALUES:
                skipped["lot"] = skipped.get("lot", 0) + 1
            elif row_type in _TOTAL_VALUES:
                currency = _currency(_row_value(row, active_position.fields["currency"]))
                value = parse_number(_row_value(row, active_position.fields["value"]))
                if value is not None:
                    totals.append(IbkrTotal(
                        line_number,
                        _row_value(row, active_position.fields["asset"]),
                        currency,
                        value,
                    ))
                skipped["total"] = skipped.get("total", 0) + 1
        if (
            active_instrument and section_key == _norm(active_instrument.section)
            and row_type in _DATA_VALUES
        ):
            raw_instruments.append((line_number, row, active_instrument))
        if active_nav and section_key == _norm(active_nav.section) and row_type in _DATA_VALUES:
            raw_nav.append((line_number, row, active_nav))
        if (
            active_account and section_key == _norm(active_account.section)
            and row_type in _DATA_VALUES
        ):
            field_name = _row_value(row, active_account.fields["field"])
            value = _row_value(row, active_account.fields["value"])
            if field_name:
                account_pairs.append((field_name, value))
                if "period" in _norm(field_name) or "daterange" in _norm(field_name):
                    statement_period = value

    if not raw_positions:
        raise IbkrParseError("Il rendiconto non contiene una sezione Posizioni aperte leggibile.")

    instrument_map: dict[tuple[str, str], list[dict[str, str]]] = {}
    for _, row, header in raw_instruments:
        asset = _row_value(row, header.fields["asset"])
        symbol = _row_value(row, header.fields["symbol"])
        if not asset or not symbol:
            continue
        security_id = _row_value(row, header.fields.get("security_id"))
        isin = _row_value(row, header.fields.get("isin"))
        if not is_isin(isin) and is_isin(security_id):
            isin = security_id.upper().replace(" ", "")
        item = {
            "isin": isin.upper().replace(" ", "") if is_isin(isin) else "",
            "name": _row_value(row, header.fields.get("description")),
            "exchange": _row_value(row, header.fields.get("exchange")),
            "instrument_type": _row_value(row, header.fields.get("type")),
        }
        key = (_norm(asset), _norm(symbol))
        instrument_map.setdefault(key, []).append(item)

    issues: list[IbkrIssue] = []
    positions: list[IbkrPosition] = []
    for line_number, row, header in raw_positions:
        detail = _norm(_row_value(row, header.fields["detail"]))
        if detail in _LOT_VALUES:
            skipped["lot"] = skipped.get("lot", 0) + 1
            continue
        if detail not in _SUMMARY_VALUES:
            issues.append(IbkrIssue(
                line_number, "DataDiscriminator",
                "Dettaglio posizione non supportato.", "unsupported_detail",
            ))
            continue

        asset = _row_value(row, header.fields["asset"])
        ticker = _row_value(row, header.fields["symbol"])
        currency = _currency(_row_value(row, header.fields["currency"]))
        if _is_cash(asset, ""):
            issues.append(IbkrIssue(
                line_number, "Asset Class", "La liquidita' viene esclusa dall'import.",
                "cash_excluded", False,
            ))
            continue
        if not ticker:
            issues.append(IbkrIssue(
                line_number, "Symbol", "Manca il simbolo della posizione.",
                "missing_identifier",
            ))
            continue
        if not currency:
            issues.append(IbkrIssue(
                line_number, "Currency", "Manca o non e' valida la valuta.",
                "invalid_currency",
            ))
            continue
        value = parse_number(_row_value(row, header.fields["value"]))
        if value is None or value <= 0:
            issues.append(IbkrIssue(
                line_number, "Value", "Il valore della posizione deve essere positivo.",
                "invalid_value",
            ))
            continue
        quantity = parse_number(_row_value(row, header.fields["quantity"]))
        side = _norm(_row_value(row, header.fields.get("side")))
        if (
            quantity is None or quantity <= 0 or side in {"short", "scoperto"}
            or "short" in _norm(asset)
        ):
            issues.append(IbkrIssue(
                line_number, "Quantity",
                "Le posizioni short o con quantita' non positiva non sono importabili.",
                "unsupported_short",
            ))
            continue

        isin = _row_value(row, header.fields.get("isin"))
        security_id = _row_value(row, header.fields.get("security_id"))
        if not is_isin(isin) and is_isin(security_id):
            isin = security_id
        isin = isin.upper().replace(" ", "") if is_isin(isin) else ""

        matches = instrument_map.get((_norm(asset), _norm(ticker)), [])
        if len(matches) > 1 and isin:
            isin_matches = [item for item in matches if item.get("isin") == isin]
            if len(isin_matches) == 1:
                matches = isin_matches
        if len(matches) > 1:
            issues.append(IbkrIssue(
                line_number, "Symbol", "Anagrafica IBKR ambigua per il simbolo.",
                "ambiguous_instrument", False,
            ))
        instrument = matches[0] if len(matches) == 1 else {}
        instrument_type = instrument.get("instrument_type", "")
        if _is_derivative(asset, instrument_type):
            issues.append(IbkrIssue(
                line_number, "Asset Class",
                "Strumenti derivati o obbligazionari non supportati.",
                "unsupported_asset",
            ))
            continue
        isin = isin or instrument.get("isin", "")
        if not instrument and not isin:
            issues.append(IbkrIssue(
                line_number, "Symbol",
                "Anagrafica strumento non trovata: il ticker resta utilizzabile.",
                "missing_instrument", False,
            ))
        average = parse_number(_row_value(row, header.fields.get("average")), prefer_decimal=True)
        identifier = f"isin:{isin}" if isin else f"ticker:{ticker.upper()}:{currency}"
        positions.append(IbkrPosition(
            row=line_number,
            identifier=identifier,
            asset_type=asset,
            instrument_type=instrument_type,
            ticker=ticker,
            isin=isin,
            name=instrument.get("name", "") or _row_value(row, header.fields.get("name")),
            exchange=instrument.get("exchange", "") or _row_value(
                row, header.fields.get("exchange")
            ),
            currency=currency,
            current_value=float(value),
            quantity=quantity,
            average_price=average,
        ))

    if not positions:
        raise IbkrParseError("Nessuna posizione long importabile nel rendiconto IBKR.")

    base_currency = _currency(_parse_account_value(account_pairs, "valuta", "base"))
    if not base_currency:
        base_currency = _currency(_parse_account_value(account_pairs, "base", "currency"))
    report_start, report_end = _filename_dates(filename)
    if report_end is None and statement_period:
        period_parts = re.split(r"\s+[-–]\s+", statement_period, maxsplit=1)
        if len(period_parts) == 2:
            report_start = _date_from_text(period_parts[0])
            report_end = _date_from_text(period_parts[1])
        else:
            report_end = _date_from_text(statement_period)

    native_totals: dict[str, float] = {}
    for position in positions:
        native_totals[position.currency] = (
            native_totals.get(position.currency, 0.0) + position.current_value
        )

    base_total = None
    if base_currency:
        for total in reversed(totals):
            if total.currency == base_currency:
                base_total = total.value
                break
    position_assets = {_norm(position.asset_type) for position in positions}
    if base_total is None:
        for _, row, header in raw_nav:
            asset = _norm(_row_value(row, header.fields["asset"]))
            if asset in position_assets or asset in {"total", "totale"}:
                candidate = parse_number(_row_value(row, header.fields["current"]))
                if candidate is not None:
                    base_total = float(candidate)
                    if asset in position_assets:
                        break

    fx_hints: dict[str, float] = {}
    foreign = [currency for currency in native_totals if currency != base_currency]
    if base_total is not None and len(foreign) == 1 and native_totals.get(foreign[0], 0.0) > 0:
        foreign_value = native_totals[foreign[0]]
        base_native = native_totals.get(base_currency, 0.0)
        rate = (base_total - base_native) / foreign_value
        if math.isfinite(rate) and rate > 0:
            fx_hints[foreign[0]] = rate

    if totals:
        skipped["total"] = max(skipped.get("total", 0), len(totals))
    skipped.setdefault("lot", 0)
    return IbkrImportResult(
        positions=tuple(positions),
        issues=tuple(issues),
        base_currency=base_currency,
        report_start=report_start,
        report_end=report_end,
        native_totals=native_totals,
        base_total=base_total,
        fx_hints=fx_hints,
        totals=tuple(totals),
        skipped=skipped,
    )


__all__ = [
    "IbkrImportResult",
    "IbkrIssue",
    "IbkrParseError",
    "IbkrPosition",
    "IbkrTotal",
    "parse_statement",
]
