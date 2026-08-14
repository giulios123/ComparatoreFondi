"""Export/import di un portafoglio: fondi, pesi e parametri del backtest in
un file JSON versionato, indipendente dalla lingua dell'interfaccia.

Nessun import di Streamlit qui dentro: la lettura/scrittura del file e'
testabile da sola, l'applicazione allo stato di sessione resta in `app.py`.
"""

from __future__ import annotations

import json

from comparatore import allocazione as al
from comparatore.instrument_facts import InstrumentFacts

SCHEMA = "comparatore-fondi/portafoglio"
VERSIONE = 1

# Senza questi tre l'editor di composizione non ha nulla da mostrare per la
# riga; tutto il resto (alloc, fonte, proxy, ...) e' back-fillato da
# `assicura_alloc()`, come gia' avviene per i fondi salvati da versioni
# precedenti dell'app.
_CHIAVI_FONDO_OBBLIGATORIE = ("symbol", "name", "weight")
_FONTI_PREZZI = {"auto", "csv", "yahoo", "eodhd", "twelvedata", "justetf"}


class PortfolioError(Exception):
    """File di portafoglio mancante, corrotto o di versione non supportata."""


def normalizza_benchmark(value: object) -> dict | None:
    """Valida il riferimento opzionale senza rendere fragili i JSON vecchi."""
    if value is None:
        return None
    if not isinstance(value, dict):
        return None
    symbol = str(value.get("symbol", "")).strip()
    if not symbol:
        return None
    preferred_source = str(value.get("preferred_source", "") or "")
    if preferred_source not in _FONTI_PREZZI:
        preferred_source = "auto"
    out = {
        "kind": str(value.get("kind", "custom") or "custom"),
        "symbol": symbol,
        "name": str(value.get("name", "") or symbol),
        "isin": str(value.get("isin", "") or "").upper(),
        "preferred_source": preferred_source,
    }
    if out["kind"] not in {"preset", "custom"}:
        out["kind"] = "custom"
    return out


def assicura_alloc(fund: dict) -> dict:
    """Completa i fondi rimasti nello stato - o importati da file - da prima
    della classificazione, o con campi mancanti."""
    alloc = fund.get("alloc")
    if not isinstance(alloc, dict) or not alloc:
        fund["alloc"] = al.classifica_da_nome(fund.get("name", ""), fund["symbol"])
        fund["alloc_fonte"] = "nome"
    manuale = fund.get("alloc_manuale")
    if not isinstance(manuale, dict):
        manuale = {}
        fund["alloc_manuale"] = manuale
    for dimensione in al.DIMENSIONI:
        manuale.setdefault(dimensione, "")
    holdings = fund.get("holdings")
    if not isinstance(holdings, list):
        holdings = []
        fund["holdings"] = holdings
    fund.setdefault("holdings_source", "")
    fund.setdefault("holdings_as_of", None)
    fund["alloc"].setdefault("paese", al.paesi_da_posizioni(holdings))
    fund.setdefault("currency", "")
    fund.setdefault("isin", "")
    fund.setdefault("quote_type", "")
    fund.setdefault("exchange", "")
    fund.setdefault("distribution_policy", "")
    fund.setdefault("replication_method", "")
    fund["instrument_facts"] = InstrumentFacts.from_dict(
        fund.get("instrument_facts")
    ).to_dict()
    if not isinstance(fund.get("related_quotes"), list):
        fund["related_quotes"] = fund["instrument_facts"].get("related_quotes", [])
    fund.setdefault("ter", 0.0)
    fund.setdefault("ter_auto", False)
    if not isinstance(fund.get("ter_attempts"), list):
        fund["ter_attempts"] = []
    if "ter_origin" not in fund:
        fund["ter_origin"] = (
            "auto" if fund.get("ter_auto") else "manual" if fund.get("ter") else "missing"
        )
    fund.setdefault("extra", 0.0)
    fund.setdefault("source", "auto")
    fund.setdefault("proxy", "(nessuno)")
    return fund


def dump(fondi: list[dict], parametri: dict) -> str:
    """Serializza fondi e parametri in JSON indentato, pronto per il download."""
    parametri = dict(parametri)
    if "benchmark" in parametri:
        parametri["benchmark"] = normalizza_benchmark(parametri["benchmark"])
    fondi_persistibili = []
    for fondo in fondi:
        persistibile = dict(fondo)
        # Tentativi, errori e stato della cache sono diagnostica della sessione,
        # non fatti utili da trasferire in un portafoglio.
        persistibile.pop("ter_attempts", None)
        persistibile["instrument_facts"] = InstrumentFacts.from_dict(
            persistibile.get("instrument_facts")
        ).to_dict()
        payload_facts = persistibile.get("instrument_facts") or {}
        persistibile["related_quotes"] = payload_facts.get("related_quotes") or (
            persistibile.get("related_quotes") or []
        )
        fondi_persistibili.append(persistibile)
    payload = {
        "schema": SCHEMA,
        "versione": VERSIONE,
        "fondi": fondi_persistibili,
        "parametri": parametri,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def load(testo: str | bytes) -> tuple[list[dict], dict]:
    """Fondi e parametri da un file esportato in precedenza.

    Solleva `PortfolioError` per qualunque file mancante, non-JSON, non nel
    nostro schema, di versione futura, o con un fondo senza i campi minimi -
    mai un traceback che arrivi fino all'interfaccia.
    """
    if isinstance(testo, bytes):
        try:
            testo = testo.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PortfolioError("il file non è testo UTF-8 valido") from exc
    try:
        payload = json.loads(testo)
    except json.JSONDecodeError as exc:
        raise PortfolioError(f"JSON non valido ({exc.msg})") from exc

    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise PortfolioError("il file non è un portafoglio di Comparatore Fondi")
    if not isinstance(payload.get("versione"), int) or payload["versione"] > VERSIONE:
        raise PortfolioError("versione del file non supportata da questa versione dell'app")

    fondi = payload.get("fondi")
    if not isinstance(fondi, list) or not fondi:
        raise PortfolioError("nessun fondo nel file")
    for fondo in fondi:
        if not isinstance(fondo, dict) or any(
            k not in fondo for k in _CHIAVI_FONDO_OBBLIGATORIE
        ):
            raise PortfolioError("un fondo nel file non ha i campi minimi richiesti")
        assicura_alloc(fondo)

    parametri = payload.get("parametri")
    if not isinstance(parametri, dict):
        parametri = {}
    if "benchmark" in parametri:
        parametri["benchmark"] = normalizza_benchmark(parametri["benchmark"])
    return fondi, parametri
