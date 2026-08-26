# ruff: noqa: E501

"""Catalogo statico dei portafogli famosi usati come benchmark.

Il modulo non conosce Streamlit, il registry o il portafoglio dell'utente:
descrive soltanto allocazioni dichiarate, proxy eseguibili e avvertenze. La
versione del catalogo entra nel JSON cosi' una modifica futura resta esplicita
e non cambia in silenzio i risultati di un file gia' esportato.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose

CATALOG_VERSION = 1
PORTFOLIO_CATALOG_VERSION = CATALOG_VERSION

PORTFOLIO_CHARTS_URL = "https://portfoliocharts.com/portfolios/"
GONE_FISHIN_URL = "https://www.gonefishinportfolio.com/annual-update.html"
ARTEMIS_URL = "https://www.artemiscm.com/research-papers"
ALL_WEATHER_URL = (
    "https://www.ssga.com/us/en/intermediary/etfs/"
    "state-street-bridgewater-all-weather-etf-allw"
)
RPAR_URL = "https://rparetf.com/rpar"
TRTY_URL = "https://cambriafunds.com/TRTY"


@dataclass(frozen=True)
class CanonicalAllocation:
    """Una voce dell'allocazione pubblicata dalla fonte del portafoglio."""

    sleeve: str
    weight: float


@dataclass(frozen=True)
class ExecutableComponent:
    """Un proxy quotabile per una sleeve canonica.

    `weight` e' in percentuale, come la definizione canonica. Per le sleeve
    composte (per esempio `DMxUS-L`) possono esistere piu' componenti con lo
    stesso `sleeve`; il calcolatore li aggrega per simbolo prima di simulare.
    """

    sleeve: str
    symbol: str
    weight: float
    isin: str = ""
    wrapper: str = "UCITS ETF"
    source_url: str = ""
    note_key: str = ""

    @property
    def canonical_sleeve(self) -> str:
        return self.sleeve


@dataclass(frozen=True)
class PortfolioDefinition:
    """Definizione completa e localizzabile di un benchmark catalogato."""

    portfolio_id: str
    name_key: str
    tooltip_key: str
    composition_key: str
    warning_key: str
    source_url: str
    kind: str
    canonical: tuple[CanonicalAllocation, ...]
    executable: tuple[ExecutableComponent, ...]
    rebalance: str = "yearly"

    @property
    def id(self) -> str:
        """Alias breve utile ai chiamanti che trattano il catalogo come mapping."""
        return self.portfolio_id

    @property
    def canonical_allocations(self) -> tuple[CanonicalAllocation, ...]:
        return self.canonical

    @property
    def executable_components(self) -> tuple[ExecutableComponent, ...]:
        return self.executable

    @property
    def is_managed(self) -> bool:
        return self.kind == "managed"


@dataclass(frozen=True)
class _Proxy:
    symbol: str
    ratio: float
    isin: str = ""
    wrapper: str = "UCITS ETF"
    note_key: str = ""


# ISIN e proxy sono volutamente dati di catalogo, non una ricerca runtime:
# risolvere lo storico resta compito del Registry e delle fonti abilitate.
_P = {
    "US-L": (_Proxy("SXR8.DE", 1.0, "IE00B5BMR087"),),
    "US-LV": (_Proxy("QDVI.DE", 1.0, "IE00BD1F4M44"),),
    "US-S": (_Proxy("ZPRR.DE", 1.0, "IE00BJ38QD84"),),
    "US-SV": (_Proxy("ZPRV.DE", 1.0, "IE00BSPLC413"),),
    "DM-L": (_Proxy("EUNL.DE", 1.0, "IE00B4L5Y983"),),
    "DM-S": (_Proxy("ZPRS.DE", 1.0, "IE00BCBJG560"),),
    "EM": (_Proxy("IS3N.DE", 1.0, "IE00BKM4GZ66"),),
    "GLB": (_Proxy("VGWL.DE", 1.0, "IE00B3RBWM25"),),
    "EU": (_Proxy("VGEU.DE", 1.0, "IE00B945VV12"),),
    "DMxUS-L": (
        _Proxy("VGEU.DE", 0.50, "IE00B945VV12"),
        _Proxy("VJPN.DE", 0.20, "IE00B95PGT31"),
        _Proxy("VGEJ.DE", 0.15, "IE00B9F5YL18"),
        _Proxy("SXR2.DE", 0.15, "IE00B52SF786"),
    ),
    "PAC": (
        _Proxy("VJPN.DE", 0.60, "IE00B95PGT31"),
        _Proxy("CPXJ.DE", 0.40, "IE00B52MJY50"),
    ),
    "US-SG": (
        _Proxy("ZPRR.DE", 1.0, "IE00BJ38QD84", note_key="benchmark.note_us_sg"),
    ),
    "DMxUS-LV": (
        _Proxy("CEMS.DE", 1.0, "IE00BQN1K901", note_key="benchmark.note_proxy"),
    ),
    "DMxUS-S": (
        _Proxy("ZPRS.DE", 1.0, "IE00BCBJG560", note_key="benchmark.note_proxy"),
    ),
    "DMxUS-SV": (
        _Proxy("ZPRX.DE", 1.0, "IE00BSPLC298", note_key="benchmark.note_proxy"),
    ),
    "US-T": (
        _Proxy("SXR8.DE", 0.85, "IE00B5BMR087", note_key="benchmark.note_us_t"),
        _Proxy("ZPRR.DE", 0.15, "IE00BJ38QD84", note_key="benchmark.note_us_t"),
    ),
    "UST-I": (_Proxy("IUSM.DE", 1.0, "IE00B1FZS798"),),
    "UST-L": (_Proxy("IS04.DE", 1.0, "IE00BSKRJZ44"),),
    "UST-S": (_Proxy("IUSU.DE", 1.0, "IE00B14X4S71"),),
    "BILL": (_Proxy("IBC1.DE", 1.0, "IE00BGSF1X88"),),
    "GOV-DM": (_Proxy("EUN3.DE", 1.0, "IE00B3F81K65"),),
    "US-AGG": (_Proxy("EUNX.DE", 1.0, "IE00B44CGS96"),),
    "TIPS": (_Proxy("IUST.DE", 1.0, "IE00B1FZSC47"),),
    "HY": (_Proxy("IS0R.DE", 1.0, "IE00B66F4759"),),
    "REIT": (_Proxy("IQQ7.DE", 1.0, "IE00B1FZSF77"),),
    "GOLD": (
        _Proxy(
            "4GLD.DE", 1.0, "DE000A0S9GB0", "ETC", "benchmark.note_gold"
        ),
    ),
    "COM": (_Proxy("EXXY.DE", 1.0, "DE000A0H0728"),),
    "ALLW": (
        _Proxy(
            "ALLW", 1.0, "US8574927062", "US ETF", "benchmark.note_managed_us"
        ),
    ),
    "RPAR": (
        _Proxy(
            "RPAR", 1.0, "US74933W1062", "US ETF", "benchmark.note_managed_us"
        ),
    ),
    "TRTY": (
        _Proxy(
            "TRTY", 1.0, "US1320612011", "US ETF", "benchmark.note_managed_us"
        ),
    ),
    "KMLM": (
        _Proxy(
            "KMLM", 1.0, "US5007673065", "US ETF", "benchmark.note_managed_us"
        ),
    ),
    "CAOS": (
        _Proxy(
            "CAOS", 1.0, "US14161W1053", "US ETF", "benchmark.note_managed_us"
        ),
    ),
}


def _expand(
    canonical: tuple[CanonicalAllocation, ...], source_url: str
) -> tuple[ExecutableComponent, ...]:
    """Espande le sleeve in proxy quotabili senza cambiare la somma dei pesi."""
    expanded: list[ExecutableComponent] = []
    for allocation in canonical:
        proxies = _P[allocation.sleeve]
        for proxy in proxies:
            expanded.append(
                ExecutableComponent(
                    sleeve=allocation.sleeve,
                    symbol=proxy.symbol,
                    weight=allocation.weight * proxy.ratio,
                    isin=proxy.isin,
                    wrapper=proxy.wrapper,
                    source_url=source_url,
                    note_key=proxy.note_key,
                )
            )
    return tuple(expanded)


def _a(*items: tuple[str, float]) -> tuple[CanonicalAllocation, ...]:
    return tuple(CanonicalAllocation(sleeve, weight) for sleeve, weight in items)


def _portfolio(
    portfolio_id: str,
    canonical: tuple[CanonicalAllocation, ...],
    source_url: str = PORTFOLIO_CHARTS_URL,
    kind: str = "composite",
    rebalance: str = "yearly",
    warning_key: str = "benchmark.warning_none",
) -> PortfolioDefinition:
    prefix = f"benchmark.portfolio.{portfolio_id}"
    return PortfolioDefinition(
        portfolio_id=portfolio_id,
        name_key=f"{prefix}.name",
        tooltip_key=f"{prefix}.tooltip",
        composition_key=f"{prefix}.composition",
        warning_key=warning_key,
        source_url=source_url,
        kind=kind,
        canonical=canonical,
        executable=_expand(canonical, source_url),
        rebalance=rebalance,
    )


PORTFOLIO_CATALOG: tuple[PortfolioDefinition, ...] = (
    _portfolio("60_40", _a(("US-L", 60), ("UST-I", 40))),
    _portfolio("80_20", _a(("US-L", 80), ("UST-I", 20))),
    _portfolio("global_equity_100", _a(("GLB", 100))),
    _portfolio(
        "bogleheads_three_fund",
        _a(("US-L", 64), ("DMxUS-L", 16), ("UST-I", 20)),
    ),
    _portfolio("permanent", _a(("US-L", 25), ("UST-L", 25), ("BILL", 25), ("GOLD", 25))),
    _portfolio(
        "golden_butterfly",
        _a(("US-L", 20), ("US-SV", 20), ("UST-L", 20), ("UST-S", 20), ("GOLD", 20)),
    ),
    _portfolio(
        "all_weather", _a(("ALLW", 100)), kind="managed", rebalance="none",
        source_url=ALL_WEATHER_URL,
    ),
    _portfolio(
        "all_seasons",
        _a(("US-L", 30), ("UST-L", 40), ("UST-I", 15), ("GOLD", 8), ("COM", 7)),
    ),
    _portfolio(
        "swensen",
        _a(("US-L", 30), ("DMxUS-L", 15), ("EM", 5), ("UST-I", 30), ("REIT", 20)),
    ),
    _portfolio(
        "coffeehouse",
        _a(("US-L", 10), ("US-LV", 10), ("US-S", 10), ("US-SV", 10),
           ("DMxUS-L", 10), ("REIT", 10), ("UST-I", 40)),
    ),
    _portfolio("ivy", _a(("US-L", 20), ("DMxUS-L", 20), ("UST-I", 20), ("REIT", 20), ("COM", 20))),
    _portfolio(
        "seven_twelve",
        _a(("US-L", 13), ("US-S", 12), ("DMxUS-L", 8), ("EM", 8), ("UST-I", 17),
           ("BILL", 9), ("GOV-DM", 8), ("REIT", 8), ("COM", 17)),
    ),
    _portfolio(
        "merriman_ultimate_buy_and_hold",
        _a(("US-L", 6), ("US-LV", 6), ("US-S", 6), ("US-SV", 6),
           ("DMxUS-L", 6), ("DMxUS-LV", 6), ("DMxUS-S", 6), ("DMxUS-SV", 6),
           ("EM", 6), ("UST-I", 20), ("UST-S", 20), ("REIT", 6)),
    ),
    _portfolio("larry", _a(("US-SV", 15), ("DMxUS-SV", 8), ("EM", 7), ("UST-I", 70))),
    _portfolio(
        "dragon",
        _a(("US-L", 24), ("UST-I", 18), ("GOLD", 19), ("KMLM", 18), ("CAOS", 21)),
        source_url=ARTEMIS_URL,
        warning_key="benchmark.warning_dragon",
    ),
    _portfolio(
        "risk_parity", _a(("RPAR", 100)), kind="managed", rebalance="none", source_url=RPAR_URL,
    ),
    _portfolio("core_four", _a(("US-L", 48), ("DMxUS-L", 24), ("UST-I", 20), ("REIT", 8))),
    _portfolio(
        "pinwheel",
        _a(("US-L", 15), ("US-SV", 10), ("DMxUS-L", 15), ("EM", 10), ("UST-I", 15),
           ("BILL", 10), ("REIT", 15), ("GOLD", 10)),
    ),
    _portfolio("weird", _a(("US-SV", 20), ("DMxUS-S", 20), ("UST-L", 20), ("REIT", 20), ("GOLD", 20))),
    _portfolio(
        "sandwich",
        _a(("US-L", 20), ("US-S", 8), ("DMxUS-S", 10), ("DMxUS-L", 6), ("EM", 6),
           ("UST-I", 30), ("BILL", 4), ("GOV-DM", 11), ("REIT", 5)),
    ),
    _portfolio("gone_fishin", _a(("US-T", 15), ("US-S", 15), ("EU", 10), ("PAC", 10),
                                  ("EM", 10), ("US-AGG", 10), ("HY", 10), ("TIPS", 10),
                                  ("REIT", 5), ("GOLD", 5)), source_url=GONE_FISHIN_URL),
    _portfolio("ideal_index", _a(("US-LV", 9), ("US-SV", 9), ("US-L", 7), ("US-SG", 6),
                                  ("DMxUS-L", 31), ("UST-S", 30), ("REIT", 8))),
    _portfolio("global_market", _a(("DM-L", 38), ("DM-S", 7), ("EM", 5), ("GOV-DM", 44),
                                    ("REIT", 4), ("GOLD", 2))),
    _portfolio("trinity", _a(("TRTY", 100)), kind="managed", rebalance="none", source_url=TRTY_URL),
    _portfolio("no_brainer", _a(("US-L", 25), ("US-S", 25), ("DMxUS-S", 25), ("UST-S", 25))),
)

PORTFOLIO_BY_ID = {definition.portfolio_id: definition for definition in PORTFOLIO_CATALOG}
PORTFOLIO_IDS = tuple(definition.portfolio_id for definition in PORTFOLIO_CATALOG)


def get_portfolio(portfolio_id: str) -> PortfolioDefinition | None:
    """Restituisce un portafoglio solo se appartiene alla versione corrente."""
    return PORTFOLIO_BY_ID.get(str(portfolio_id or "").strip())


def executable_weights(definition: PortfolioDefinition) -> dict[str, float]:
    """Aggrega simboli duplicati mantenendo i pesi in percentuale."""
    weights: dict[str, float] = {}
    for component in definition.executable:
        weights[component.symbol] = weights.get(component.symbol, 0.0) + component.weight
    return weights


def validate_catalog() -> None:
    """Blocca errori di catalogo prima che possano produrre un grafico."""
    if len(PORTFOLIO_CATALOG) != 25 or len(PORTFOLIO_BY_ID) != 25:
        raise ValueError("il catalogo dei portafogli famosi deve contenere 25 ID unici")
    for definition in PORTFOLIO_CATALOG:
        if not definition.portfolio_id or definition.kind not in {"composite", "managed"}:
            raise ValueError(f"definizione non valida: {definition.portfolio_id!r}")
        if not definition.source_url.startswith("https://"):
            raise ValueError(f"fonte non HTTPS: {definition.portfolio_id}")
        canonical_total = sum(item.weight for item in definition.canonical)
        executable_total = sum(item.weight for item in definition.executable)
        if not isclose(canonical_total, 100.0, abs_tol=1e-9):
            raise ValueError(f"pesi canonici non al 100%: {definition.portfolio_id}")
        if not isclose(executable_total, 100.0, abs_tol=1e-9):
            raise ValueError(f"pesi eseguibili non al 100%: {definition.portfolio_id}")
        if any(item.weight <= 0 or not item.symbol for item in definition.executable):
            raise ValueError(f"componente eseguibile non valida: {definition.portfolio_id}")
        if definition.kind == "managed" and definition.rebalance != "none":
            raise ValueError(f"portafoglio managed senza ribilanciamento interno: {definition.portfolio_id}")


validate_catalog()
