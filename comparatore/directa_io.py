"""Lettura neutrale di esportazioni di posizioni da broker.

Directa non pubblica uno schema stabile per l'export del portafoglio. Il
modulo quindi separa lettura tabellare e mappatura delle colonne: la UI puo'
mostrare un'anteprima e scegliere i campi senza importare Streamlit qui dentro.
"""

from __future__ import annotations

import csv
import io
import math
import re
import unicodedata
from dataclasses import dataclass, field

import pandas as pd

from .sources.base import is_isin


class DirectaParseError(ValueError):
    """File o mappatura Directa non leggibile."""


@dataclass(frozen=True)
class DirectaColumnMap:
    """Nomi delle colonne selezionate dall'utente nell'anteprima."""

    value: str
    isin: str = ""
    ticker: str = ""
    name: str = ""
    currency: str = ""
    quantity: str = ""
    average_price: str = ""


@dataclass(frozen=True)
class DirectaPosition:
    row: int
    identifier: str
    isin: str = ""
    ticker: str = ""
    name: str = ""
    currency: str = ""
    current_value: float = 0.0
    quantity: float | None = None
    average_price: float | None = None


@dataclass(frozen=True)
class DirectaIssue:
    row: int
    column: str
    message: str
    code: str = ""


@dataclass(frozen=True)
class DirectaParseResult:
    positions: tuple[DirectaPosition, ...]
    issues: tuple[DirectaIssue, ...] = field(default_factory=tuple)


def _text(value) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return str(value).strip()


def normalizza_intestazione(value) -> str:
    """Riduce un'intestazione a parole confrontabili anche con gli accenti."""
    testo = unicodedata.normalize("NFKD", _text(value)).encode(
        "ascii", "ignore"
    ).decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", testo.casefold())


def _decode_csv(content: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1252", "latin1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise DirectaParseError("Codifica del CSV non riconosciuta.")


def _csv_delimiter(text: str) -> str:
    sample = text[:8192]
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,\t|").delimiter
    except csv.Error:
        return ";" if sample.count(";") >= sample.count(",") else ","


_VALUE_COLUMN_HINTS = {
    "controvalore", "valore", "valoreattuale", "valoredimercato",
    "marketvalue", "currentvalue", "patrimonio", "importo", "importoeuro",
}


def _has_value_hint(intestazioni: set[str]) -> bool:
    return any(
        hint in column
        for column in intestazioni
        for hint in _VALUE_COLUMN_HINTS
    )


def suggest_header_row(
    content: bytes,
    filename: str,
    *,
    sheet: str | int = 0,
    max_rows: int = 200,
) -> int:
    """Trova la prima riga che sembra un'intestazione di portafoglio Directa.

    Alcuni export hanno conto, date e note prima della tabella. La scansione
    serve solo a preselezionare la riga nella UI: l'utente puo' comunque
    correggerla e il parser continua a non imporre uno schema proprietario.
    """
    if not content:
        raise DirectaParseError("Il file Directa e' vuoto.")
    lower = filename.lower()
    try:
        if lower.endswith(".xlsx"):
            raw = pd.read_excel(
                io.BytesIO(content), sheet_name=sheet, header=None, nrows=max_rows
            )
        elif lower.endswith((".csv", ".txt")):
            text = _decode_csv(content)
            raw = pd.read_csv(
                io.StringIO(text), sep=_csv_delimiter(text), header=None,
                nrows=max_rows, dtype=str,
            )
        else:
            raise DirectaParseError("Formato Directa non supportato: usa CSV o XLSX.")
    except DirectaParseError:
        raise
    except Exception as exc:
        raise DirectaParseError("Il file Directa non contiene una tabella leggibile.") from exc

    for index, row in raw.iterrows():
        intestazioni = {normalizza_intestazione(value) for value in row.tolist()}
        intestazioni.discard("")
        ha_identificatore = bool(intestazioni & {"isin", "ticker", "symbol"})
        ha_valore = _has_value_hint(intestazioni)
        if ha_identificatore and ha_valore:
            return int(index)
    return 0


def detect_export_kind(frame: pd.DataFrame) -> str:
    """Classifica una tabella senza reinterpretare uno storico movimenti."""
    intestazioni = {normalizza_intestazione(column) for column in frame.columns}
    if (
        {"dataoperazione", "tipooperazione"}.issubset(intestazioni)
        and any(value.startswith("importo") for value in intestazioni)
    ):
        return "movements"
    if (
        bool(intestazioni & {"isin", "ticker", "symbol"})
        and _has_value_hint(intestazioni)
    ):
        return "positions"
    return "unknown"


def sheet_names(content: bytes, filename: str) -> list[str]:
    """Nomi dei fogli XLSX; per CSV restituisce un unico foglio virtuale."""
    if filename.lower().endswith(".xlsx"):
        try:
            return pd.ExcelFile(io.BytesIO(content)).sheet_names
        except Exception as exc:
            raise DirectaParseError("Il file Excel non e' leggibile.") from exc
    if filename.lower().endswith((".csv", ".txt")):
        return ["CSV"]
    raise DirectaParseError("Formato Directa non supportato: usa CSV o XLSX.")


def read_table(
    content: bytes,
    filename: str,
    *,
    sheet: str | int = 0,
    header_row: int = 0,
) -> pd.DataFrame:
    """Legge una tabella senza assumere delimitatore o codifica del CSV."""
    if not content:
        raise DirectaParseError("Il file Directa e' vuoto.")
    if header_row < 0:
        raise DirectaParseError("La riga delle intestazioni non puo' essere negativa.")
    lower = filename.lower()
    try:
        if lower.endswith(".xlsx"):
            frame = pd.read_excel(io.BytesIO(content), sheet_name=sheet, header=header_row)
        elif lower.endswith((".csv", ".txt")):
            text = _decode_csv(content)
            frame = pd.read_csv(
                io.StringIO(text), sep=_csv_delimiter(text), header=header_row
            )
        else:
            raise DirectaParseError("Formato Directa non supportato: usa CSV o XLSX.")
    except DirectaParseError:
        raise
    except Exception as exc:
        raise DirectaParseError("Il file Directa non contiene una tabella leggibile.") from exc
    frame.columns = [str(column).strip() for column in frame.columns]
    if frame.empty or not len(frame.columns):
        raise DirectaParseError("La tabella Directa non contiene righe o colonne.")
    return frame


_CLEAN_NUMBER = re.compile(r"[^0-9,.'+()\- ]")


def parse_number(value, *, prefer_decimal: bool = False) -> float | None:
    """Numero locale/internazionale; `prefer_decimal` serve ai prezzi a 3 decimali."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value) if math.isfinite(float(value)) else None
    text = _CLEAN_NUMBER.sub("", str(value)).strip().replace(" ", "")
    if not text:
        return None
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    if "," in text and "." in text:
        decimal = "," if text.rfind(",") > text.rfind(".") else "."
        thousands = "." if decimal == "," else ","
        text = text.replace(thousands, "").replace(decimal, ".")
    elif "," in text or "." in text:
        separator = "," if "," in text else "."
        chunks = text.split(separator)
        # Un solo separatore e tre cifre dopo e' quasi sempre migliaia; due o
        # meno cifre rappresentano invece i centesimi della valuta.
        if (
            len(chunks) == 2 and len(chunks[1]) == 3 and len(chunks[0]) >= 1
            and not prefer_decimal
        ):
            text = "".join(chunks)
        else:
            text = text.replace(separator, ".")
    try:
        number = float(text)
    except ValueError:
        return None
    if negative:
        number = -number
    return number if math.isfinite(number) else None


def _column(frame: pd.DataFrame, name: str) -> pd.Series:
    return frame[name] if name and name in frame.columns else pd.Series([None] * len(frame))


def _is_summary_row(row, mapping: DirectaColumnMap) -> bool:
    """Riconosce il totale in coda degli export posizione senza generalizzarlo."""
    value_column = normalizza_intestazione(mapping.value)
    if "valore" not in value_column and "controvalore" not in value_column:
        return False
    if mapping.name and _text(row.get(mapping.name)):
        return False
    if mapping.quantity:
        quantity = parse_number(row.get(mapping.quantity))
        if quantity not in (None, 0.0):
            return False
    return True


def parse_positions(
    frame: pd.DataFrame,
    mapping: DirectaColumnMap,
    *,
    header_row: int = 0,
) -> DirectaParseResult:
    """Normalizza le righe mappate e aggrega duplicati per identificatore."""
    if header_row < 0:
        raise DirectaParseError("La riga delle intestazioni non puo' essere negativa.")
    if not mapping.value or mapping.value not in frame.columns:
        raise DirectaParseError("Serve una colonna di controvalore attuale.")
    if not mapping.isin and not mapping.ticker:
        raise DirectaParseError("Serve almeno una colonna ISIN o ticker.")

    issues: list[DirectaIssue] = []
    merged: dict[str, DirectaPosition] = {}
    for offset, (_, row) in enumerate(frame.iterrows(), start=header_row + 2):
        row_number = offset
        values = row.tolist()
        if all(not _text(value) for value in values):
            continue
        raw_isin = _text(row.get(mapping.isin)) if mapping.isin else ""
        isin = raw_isin.upper().replace(" ", "")
        if isin and not is_isin(isin):
            issues.append(
                DirectaIssue(row_number, mapping.isin, "ISIN non valido.", "invalid_isin")
            )
            continue
        ticker = _text(row.get(mapping.ticker)) if mapping.ticker else ""
        if not isin and not ticker:
            if _is_summary_row(row, mapping):
                issues.append(
                    DirectaIssue(
                        row_number, mapping.value,
                        "Riga riepilogativa senza uno strumento.", "summary_row",
                    )
                )
                continue
            issues.append(
                DirectaIssue(
                    row_number, mapping.isin or mapping.ticker,
                    "Manca ISIN o ticker.", "missing_identifier",
                )
            )
            continue
        value = parse_number(row.get(mapping.value))
        if value is None or value <= 0:
            issues.append(
                DirectaIssue(
                    row_number, mapping.value,
                    "Il controvalore deve essere positivo.", "invalid_value",
                )
            )
            continue
        quantity = parse_number(row.get(mapping.quantity)) if mapping.quantity else None
        if mapping.quantity and _text(row.get(mapping.quantity)) and (
            quantity is None or quantity <= 0
        ):
            issues.append(
                DirectaIssue(
                    row_number, mapping.quantity,
                    "La quantità deve essere positiva.", "invalid_quantity",
                )
            )
            continue
        average = (
            parse_number(row.get(mapping.average_price), prefer_decimal=True)
            if mapping.average_price else None
        )
        if mapping.average_price and _text(row.get(mapping.average_price)) and (
            average is None or average <= 0
        ):
            issues.append(
                DirectaIssue(
                    row_number, mapping.average_price,
                    "Il prezzo medio di carico deve essere positivo.", "invalid_average",
                )
            )
            continue
        identifier = f"isin:{isin}" if isin else f"ticker:{ticker.upper()}"
        position = DirectaPosition(
            row=row_number,
            identifier=identifier,
            isin=isin,
            ticker=ticker,
            name=_text(row.get(mapping.name)) if mapping.name else "",
            currency=_text(row.get(mapping.currency)).upper() if mapping.currency else "",
            current_value=value,
            quantity=quantity,
            average_price=average,
        )
        previous = merged.get(identifier)
        if previous is None:
            merged[identifier] = position
        else:
            quantity_total = None
            if previous.quantity is not None or position.quantity is not None:
                quantity_total = (previous.quantity or 0.0) + (position.quantity or 0.0)
            average_price = previous.average_price
            if (
                previous.average_price is not None
                and position.average_price is not None
                and previous.quantity is not None
                and position.quantity is not None
                and quantity_total
            ):
                average_price = (
                    previous.average_price * previous.quantity
                    + position.average_price * position.quantity
                ) / quantity_total
            merged[identifier] = DirectaPosition(
                row=previous.row,
                identifier=identifier,
                isin=previous.isin or position.isin,
                ticker=previous.ticker or position.ticker,
                name=previous.name or position.name,
                currency=previous.currency or position.currency,
                current_value=previous.current_value + position.current_value,
                quantity=quantity_total,
                average_price=average_price,
            )
    return DirectaParseResult(tuple(merged.values()), tuple(issues))


__all__ = [
    "DirectaColumnMap",
    "DirectaIssue",
    "DirectaParseError",
    "DirectaParseResult",
    "DirectaPosition",
    "detect_export_kind",
    "normalizza_intestazione",
    "parse_number",
    "parse_positions",
    "read_table",
    "sheet_names",
    "suggest_header_row",
]
