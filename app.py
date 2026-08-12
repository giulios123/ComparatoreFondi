"""Comparatore Fondi - backtester per fondi ed ETF su piu' fonti dati."""

from __future__ import annotations

import datetime as dt
import math
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comparatore import (
    __version__,
    comparative,
    covip,
    directa_io,
    fx,
    i18n,
    inflation,
    licenses,
    overlap,
    pesi,
    pic_costs,
    portfolio_io,
    prefs,
)
from comparatore import allocazione as al
from comparatore import cache as disk_cache
from comparatore import horizons as hz
from comparatore import keys as api_keys_store
from comparatore import metrics as mt
from comparatore import proxies as px
from comparatore.engine import (
    BacktestInputError,
    FeeMode,
    Frequency,
    Holding,
    Pac,
    Rebalance,
    contribution_schedule,
    coverage_warnings,
    nav_curve,
    rebalance_dates,
    run_backtest,
    simulate,
)
from comparatore.portfolio_io import assicura_alloc
from comparatore.sources import AUTO, CsvParseError, Registry, is_isin, parse_csv

# --------------------------------------------------------------------------
# Stato e accesso ai dati
# --------------------------------------------------------------------------

saved_prefs = prefs.load()

if "selected" not in st.session_state:
    st.session_state.selected = []  # dizionari: symbol, name, isin, weight, ...
if "csv_series" not in st.session_state:
    st.session_state.csv_series = {}  # chiave -> (serie, valuta)
if "directa_upload_visto" not in st.session_state:
    st.session_state.directa_upload_visto = None
if "directa_file" not in st.session_state:
    st.session_state.directa_file = None
if "directa_filename" not in st.session_state:
    st.session_state.directa_filename = ""
if "directa_sheet" not in st.session_state:
    st.session_state.directa_sheet = "CSV"
if "directa_header_row" not in st.session_state:
    st.session_state.directa_header_row = 0
if "ter_refresh_rev" not in st.session_state:
    st.session_state.ter_refresh_rev = 0
if "ter_refresh_pending" not in st.session_state:
    st.session_state.ter_refresh_pending = False
if "pic_costs_enabled" not in st.session_state:
    st.session_state.pic_costs_enabled = False
for _key, _value in {
    "pic_buy_mode": "none", "pic_buy_amount": 0.0, "pic_buy_rate_pct": 0.0,
    "pic_buy_min": 0.0, "pic_buy_max": 0.0,
    "pic_sell_mode": "none", "pic_sell_amount": 0.0, "pic_sell_rate_pct": 0.0,
    "pic_sell_min": 0.0, "pic_sell_max": 0.0,
}.items():
    if _key not in st.session_state:
        st.session_state[_key] = _value
# Le date vivono nello stato perche' i pulsanti rapidi le riscrivono. I widget
# le leggono solo tramite `key`: passare anche `value` farebbe litigare
# Streamlit fra valore predefinito e stato. Stesso trattamento per
# initial_value/base_ccy/rebalance/show_gross/risk_free, che l'import di un
# portafoglio (vedi sotto) deve poter sovrascrivere allo stesso modo.
if "start_date" not in st.session_state:
    st.session_state.start_date = dt.date.today() - dt.timedelta(days=365 * 20)
if "end_date" not in st.session_state:
    st.session_state.end_date = dt.date.today()
if "extend_history" not in st.session_state:
    st.session_state.extend_history = False
if "comparti_previdenza" not in st.session_state:
    st.session_state.comparti_previdenza = []
if "curve_sintetiche" not in st.session_state:
    st.session_state.curve_sintetiche = False
if "api_keys" not in st.session_state:
    # Chiavi salvate dall'interfaccia in un run precedente (vedi comparatore.keys).
    st.session_state.api_keys = api_keys_store.load()
if "enable_justetf" not in st.session_state:
    st.session_state.enable_justetf = bool(saved_prefs.get("enable_justetf", False))
if "inflation_enabled" not in st.session_state:
    st.session_state.inflation_enabled = bool(saved_prefs.get("inflation_enabled", False))
if "inflation_area" not in st.session_state:
    st.session_state.inflation_area = str(saved_prefs.get("inflation_area", "IT") or "IT")
if "inflation_refresh_rev" not in st.session_state:
    st.session_state.inflation_refresh_rev = 0
if "benchmark_config" not in st.session_state:
    st.session_state.benchmark_config = None
if "benchmark_choice" not in st.session_state:
    st.session_state.benchmark_choice = "none"
if "initial_value" not in st.session_state:
    st.session_state.initial_value = 10_000.0
if "base_ccy" not in st.session_state:
    st.session_state.base_ccy = "EUR"
if "rebalance" not in st.session_state:
    st.session_state.rebalance = Rebalance.NONE.value
if "show_gross" not in st.session_state:
    st.session_state.show_gross = True
# Le percentuali dell'interfaccia vivono in percentuale (2.0 = 2%) e vengono
# divise per cento al confine con il motore, come gia' fanno TER e costi extra
# della tabella di composizione. Il suffisso `_pct` nel nome della chiave e'
# quello che evita di ereditare, in una sessione gia' aperta, il valore in
# frazione scritto dalla versione precedente.
if "risk_free_pct" not in st.session_state:
    st.session_state.risk_free_pct = 2.0
# Il PAC e' una funzione avanzata, opt-in: `pac_enabled` e' un interruttore a
# se', non dedotto da `pac_amount > 0`, cosi' spegnerlo non fa perdere i
# parametri gia' configurati (stesso trattamento di `show_gross`).
if "pac_enabled" not in st.session_state:
    st.session_state.pac_enabled = False
if "pac_amount" not in st.session_state:
    st.session_state.pac_amount = 100.0
if "pac_frequency" not in st.session_state:
    st.session_state.pac_frequency = Frequency.MONTHLY.value
if "pac_step_up_pct" not in st.session_state:
    st.session_state.pac_step_up_pct = 0.0
if "pac_limit_window" not in st.session_state:
    st.session_state.pac_limit_window = False
if "pac_start" not in st.session_state:
    st.session_state.pac_start = st.session_state.start_date
if "pac_end" not in st.session_state:
    st.session_state.pac_end = st.session_state.end_date
if "_pending_state" not in st.session_state:
    st.session_state._pending_state = {}
if "_import_visto" not in st.session_state:
    st.session_state._import_visto = None  # file_id dell'ultimo portafoglio importato
if "composizione_rev" not in st.session_state:
    # Incrementato ad ogni riscrittura *programmatica* di pesi/importi (non
    # dall'utente): forza il data_editor a rigenerare la chiave, cosi'
    # Streamlit non riapplica un buffer di modifiche ormai superato (vedi
    # commento sulla chiave dell'editor di composizione, piu' sotto).
    st.session_state.composizione_rev = 0


def _applica_pending() -> None:
    """Scrive lo stato in attesa PRIMA che i widget di questo run vengano
    istanziati: e' l'unico momento in cui si puo' assegnare
    `st.session_state[chiave]` per una chiave di widget senza sollevare
    un'eccezione. Alimentato dal cambio di lingua (sotto) e dall'import di
    un portafoglio (nella barra laterale)."""
    for chiave, valore in st.session_state._pending_state.items():
        st.session_state[chiave] = valore
    st.session_state._pending_state = {}


_applica_pending()

# --------------------------------------------------------------------------
# Lingua
# --------------------------------------------------------------------------
# Risolta una sola volta per sessione (poi la sceglie l'utente dal selettore
# in barra laterale): locale del browser (st.context.locale, cioe'
# navigator.language - copre sia l'uso via browser sia il bundle desktop, che
# apre comunque il browser di sistema) -> intestazione Accept-Language
# (cintura) -> locale di sistema -> italiano. Va risolta sopra
# `set_page_config` perche' il titolo della pagina e' traducibile; leggere
# `st.context` non accoda nulla, quindi e' lecito farlo qui.
if "lang" not in st.session_state:
    pref = str(saved_prefs.get("lingua", "") or "")
    if pref in i18n.LINGUE:
        st.session_state.lang = pref
    else:
        try:
            _browser_locale = st.context.locale or ""
        except Exception:
            _browser_locale = ""
        try:
            _headers = st.context.headers
            _accept_language = _headers.get("Accept-Language", "") if _headers else ""
        except Exception:
            _accept_language = ""
        st.session_state.lang = i18n.rileva(
            browser_locale=_browser_locale,
            accept_language=_accept_language,
            locale_sistema=i18n.locale_di_sistema(),
        )

LINGUA = st.session_state.lang


def t(chiave: str, **kwargs) -> str:
    return i18n.traduci(LINGUA, chiave, **kwargs)


FMT_DATA = i18n.formato_data_strftime(LINGUA)  # per strftime() e hovertemplate Plotly
FMT_DATA_INPUT = i18n.formato_data(LINGUA)  # per st.date_input(format=...)

st.set_page_config(page_title=t("app.page_title"), page_icon="📈", layout="wide")

# Unico foglio di stile dell'app, e per una sola ragione: nessuna opzione di
# Streamlit permette di dire "questo pulsante non si spezza". Resta agganciato
# a `.st-key-preset_periodo` - la classe che Streamlit emette per un
# `st.container(key=...)` - invece che a `.stButton` in generale, cosi' vale
# solo dove serve e non tocca gli altri pulsanti della pagina.
#
# `min-width: 3ch` e' il vincolo vero: le etichette dei preset sono lunghe al
# massimo tre caratteri in tutte e quattro le lingue ("10a", "20a", "Max",
# "10J"), quindi garantire tre caratteri di larghezza equivale a garantire che
# non vadano mai a capo. In `ch` e non in pixel perche' l'unita' segue il font
# effettivo: la garanzia regge anche se il tema cambia corpo o famiglia. Il
# `gap` piu' stretto non e' estetica: e' spazio restituito ai pulsanti, e
# rimanda il punto in cui il `min-width` deve sfondare la colonna per tenere
# fede alla garanzia.
st.markdown(
    """
    <style>
    .st-key-preset_periodo [data-testid="stHorizontalBlock"] { gap: 0.4rem; }
    .st-key-preset_periodo .stButton p { white-space: nowrap; }
    .st-key-preset_periodo .stButton button {
        min-width: 3ch;
        padding-left: 0.25rem;
        padding-right: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CURRENCIES = ["EUR", "USD", "GBP", "CHF", "JPY"]
SYMBOLS = {"EUR": "€", "USD": "$", "GBP": "£", "CHF": "CHF ", "JPY": "¥"}

REBALANCE_OPTIONS = [r.value for r in Rebalance]

# `Frequency` condivide i valori "monthly"/"quarterly"/"yearly" con
# `Rebalance`: la tendina di frequenza del PAC riusa `etichetta_ribilanciamento`
# per il `format_func`, niente nuovo catalogo di traduzioni da mantenere.
PAC_FREQUENCY_OPTIONS = [f.value for f in Frequency]
PAC_RATE_ANNUE = {Frequency.MONTHLY: 12, Frequency.QUARTERLY: 4, Frequency.YEARLY: 1}

# Opzioni della colonna "Fonte": nomi interni, tradotti solo a video via
# `i18n.etichetta_fonte()` (vedi editor di composizione).
SOURCE_OPTIONS = [AUTO, "yahoo", "justetf", "eodhd", "twelvedata", "csv"]

NO_PROXY = "(nessuno)"
PROXY_OPTIONS = [NO_PROXY] + list(px.CATALOG)

PALETTE = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed",
           "#0891b2", "#db2777", "#65a30d", "#4b5563", "#ea580c"]

# Asse delle date, pensato per una pagina stretta. Un formato esplicito e a
# riga singola per ogni livello di zoom evita le etichette composite di Plotly
# (mese e anno impilati) e le tiene coerenti con la lingua scelta; con
# l'angolo bloccato a zero Plotly dirada i tick invece di accavallarli, e
# `automargin` gli lascia comunque lo spazio per non finire tagliati.
ASSE_TEMPO = dict(
    tickformatstops=[
        dict(dtickrange=[None, "M1"], value=FMT_DATA),
        dict(dtickrange=["M1", "M12"], value=i18n.formato_mese_anno(LINGUA)),
        dict(dtickrange=["M12", None], value="%Y"),
    ],
    tickangle=0,
    automargin=True,
)
# Gli assi con gli anni come categorie non hanno lo stesso problema (Plotly
# ruota le etichette da solo), ma senza margine automatico le taglia.
ASSE_CATEGORIE = dict(automargin=True)

MIN_DATE = dt.date(1970, 1, 1)
DEFAULT_YEARS = 20


def api_key(name: str) -> str:
    """Chiave API: prima quella inserita nell'interfaccia, poi st.secrets,
    poi la variabile d'ambiente.

    Non deve mai finire nel codice ne' nel repository.
    """
    from_ui = str(st.session_state.get("api_keys", {}).get(name, "") or "").strip()
    if from_ui:
        return from_ui
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    value = str(value or "").strip()
    if value:
        return value
    return str(os.environ.get(name, "") or "").strip()


def build_registry() -> Registry:
    """Registry delle fonti, ricostruito a ogni rerun.

    E' un oggetto leggero: le serie stanno nella cache su disco, non qui
    dentro, quindi ricrearlo non costa nulla e non c'e' stato da invalidare.
    """
    retention_days = disk_cache.restricted_retention_days()
    disk_cache.purge_expired(("eodhd", "twelvedata"), retention_days)
    reg = Registry(
        eodhd_key=api_key("EODHD_API_KEY"),
        twelvedata_key=api_key("TWELVEDATA_API_KEY"),
        enable_justetf=bool(st.session_state.get("enable_justetf", False)),
    )
    for key, (series, currency) in st.session_state.csv_series.items():
        reg.csv.add(key, series, currency)
    return reg


@st.cache_data(show_spinner=False, ttl=3600)
def cached_search(query: str, funds_only: bool, eodhd: str, td: str) -> list[dict]:
    reg = Registry(eodhd_key=eodhd, twelvedata_key=td)
    return [vars(i) for i in reg.search(query, limit=15, funds_only=funds_only)]


@st.cache_data(show_spinner=False, ttl=300)
def cached_metadata(
    symbol: str,
    isin: str,
    eodhd: str,
    refresh_rev: int = 0,
    justetf: bool = False,
) -> dict:
    reg = Registry(eodhd_key=eodhd, enable_justetf=justetf)
    resolution = reg.metadata_resolution(symbol, isin)
    result = vars(resolution.instrument).copy()
    result["ter_attempts"] = [vars(attempt) for attempt in resolution.attempts]
    return result


def fmt_money(v: float, ccy: str, decimals: int = 0) -> str:
    sep = i18n.separatore_migliaia(LINGUA)
    numero = f"{v:,.{decimals}f}"
    if decimals:
        intero, frazione = numero.rsplit(".", 1)
        if sep != ",":
            intero = intero.replace(",", sep)
        numero = f"{intero}{i18n.separatore_decimale(LINGUA)}{frazione}"
    elif sep != ",":
        numero = numero.replace(",", sep)
    return f"{SYMBOLS.get(ccy, '')}{numero}"


def fmt_pct(v: float, decimals: int = 2) -> str:
    return t("nd") if pd.isna(v) else f"{v * 100:.{decimals}f}%"


def etichetta_anni(a: int) -> str:
    """"1 anno" al singolare, "{a} anni" al plurale: gli orizzonti COVIP
    partono da uno e l'intestazione della tabella lo mostra a video."""
    return t("previdenza.anno_suffix" if a == 1 else "previdenza.anni_suffix", a=a)


def metric_help(risk_free: float, initial_value: float, ccy: str) -> dict[str, str]:
    """Spiegazione di ogni metrica, riusata da tooltip e legenda.

    E' una funzione e non una costante perche' i testi citano i valori
    correnti (il risk-free impostato, il capitale iniziale): un glossario
    che dice "il risk-free impostato è il 2,0%" insegna più di uno generico.
    """
    capitale = fmt_money(initial_value, ccy)
    rf_pct = fmt_pct(risk_free)
    return {
        "final_value": t("help.valore_finale", capitale=capitale),
        "total_return": t("help.rendimento_totale"),
        "cagr": t("help.cagr"),
        "volatility": t("help.volatilita"),
        "sharpe": t("help.sharpe", rf_pct=rf_pct),
        "sortino": t("help.sortino", rf_pct=rf_pct),
        "max_drawdown": t("help.max_drawdown"),
        "calmar": t("help.calmar"),
        "best_year": t("help.miglior_anno"),
        "worst_year": t("help.peggior_anno"),
        "ter_cost": t("help.costo_ter", ccy=ccy),
        "reconstructed": t("help.ricostruito"),
        "balance": t("help.pac_saldo"),
        "invested": t("help.pac_versato"),
        "gain": t("help.pac_guadagno"),
        "xirr": t("help.pac_xirr"),
    }


def _regola_commissione(prefix: str, titolo: str) -> pic_costs.TransactionFeeRule:
    """Editor comune per carico e scarico, con percentuali nello stato UI."""
    st.markdown(f"**{titolo}**")
    mode = st.selectbox(
        t("costs.mode_label"), [m.value for m in pic_costs.TransactionFeeMode],
        key=f"pic_{prefix}_mode", format_func=lambda v: t(f"costs.mode_{v}"),
        filter_mode=None,
    )
    if mode == pic_costs.TransactionFeeMode.FIXED.value:
        return pic_costs.TransactionFeeRule(
            mode=pic_costs.TransactionFeeMode.FIXED,
            amount=st.number_input(
                t("costs.fixed_label"), min_value=0.0, step=0.50, format="%.2f",
                key=f"pic_{prefix}_amount",
            ),
        )
    if mode == pic_costs.TransactionFeeMode.PERCENTAGE.value:
        rate = st.number_input(
            t("costs.rate_label"), min_value=0.0, max_value=100.0, step=0.05,
            format="%.3f", key=f"pic_{prefix}_rate_pct",
        )
        minimum = st.number_input(
            t("costs.minimum_label"), min_value=0.0, step=0.50, format="%.2f",
            key=f"pic_{prefix}_min",
        )
        maximum = st.number_input(
            t("costs.maximum_label"), min_value=0.0, step=0.50, format="%.2f",
            key=f"pic_{prefix}_max", help=t("costs.maximum_help"),
        )
        return pic_costs.TransactionFeeRule(
            mode=pic_costs.TransactionFeeMode.PERCENTAGE,
            rate=rate / 100, minimum=minimum, maximum=maximum or None,
        )
    return pic_costs.TransactionFeeRule()


def classifica(nome: str, symbol: str, meta: dict) -> tuple[dict, str]:
    """Classificazione dello strumento e provenienza del dato.

    Le sorgenti si sommano invece di escludersi: ne' EODHD ne' Yahoo
    restituiscono i settori di un obbligazionario o le regioni di un
    monetario, e su quelle dimensioni la deduzione dal nome resta meglio di
    un buco.
    """
    da_nome = al.classifica_da_nome(nome, symbol, meta.get("quote_type") or "")
    da_fonte = meta.get("allocation") or {}
    if not da_fonte:
        return da_nome, "nome"
    return al.unisci(da_fonte, da_nome), meta.get("allocation_source") or "nome"


def _etichetta_caratteristica(valore: str, gruppo: str) -> str:
    """Traduce i codici stabili delle caratteristiche ETF oppure mostra n/d."""
    chiave = {
        ("distribution", "accumulating"): "metadata.distribution_accumulating",
        ("distribution", "distributing"): "metadata.distribution_distributing",
        ("replication", "physical"): "metadata.replication_physical",
        ("replication", "synthetic"): "metadata.replication_synthetic",
    }.get((gruppo, valore))
    return t(chiave) if chiave else t("nd")


def _fondo_da_meta(
    symbol: str,
    name: str,
    isin: str,
    meta: dict,
    proxy=None,
    alloc: dict | None = None,
    alloc_fonte: str = "nome",
    holdings: list | None = None,
) -> dict:
    """Forma persistita comune a ricerca e import Directa."""
    holdings = holdings or meta.get("holdings") or []
    alloc = dict(alloc or meta.get("allocation") or {})
    alloc["paese"] = al.paesi_da_posizioni(holdings)
    ter = meta.get("ter")
    return {
        "symbol": symbol,
        "name": meta.get("name") or name or symbol,
        "currency": meta.get("currency") or "",
        "isin": (isin or meta.get("isin") or "").upper(),
        "weight": 0.0,
        "ter": (ter or 0.0) * 100,
        "ter_auto": ter is not None,
        "ter_origin": meta.get("ter_origin") or ("auto" if ter is not None else "missing"),
        "ter_attempts": meta.get("ter_attempts", []),
        "distribution_policy": meta.get("distribution_policy") or "",
        "replication_method": meta.get("replication_method") or "",
        "extra": 0.0,
        "source": AUTO,
        "proxy": proxy.symbol if proxy else NO_PROXY,
        "alloc": alloc,
        "alloc_fonte": alloc_fonte or meta.get("allocation_source") or "nome",
        "alloc_manuale": {d: "" for d in al.DIMENSIONI},
        "holdings": holdings,
        "holdings_source": meta.get("holdings_source") or "",
        "holdings_as_of": meta.get("holdings_as_of"),
    }


def _aggiorna_ter(fondo: dict, meta: dict) -> bool:
    """Aggiorna solo un TER automatico, lasciando intatto l'override manuale."""
    for chiave in ("distribution_policy", "replication_method"):
        if meta.get(chiave):
            fondo[chiave] = meta[chiave]
    if fondo.get("ter_origin") == "manual":
        return False
    ter = meta.get("ter")
    fondo["ter_attempts"] = meta.get("ter_attempts", [])
    if ter is None:
        # Non degradare un TER già presente per errori temporanei delle fonti.
        if fondo.get("ter_origin", "missing") == "missing":
            fondo["ter_origin"] = "missing"
            fondo["ter_auto"] = False
        return False
    fondo["ter"] = float(ter) * 100
    fondo["ter_origin"] = meta.get("ter_origin") or "auto"
    fondo["ter_auto"] = True
    fondo["ter_attempts"] = meta.get("ter_attempts", [])
    return True


def _mancano_metadati_etf(fondo: dict) -> bool:
    """Stabilisce se un cambio fonte puo' ancora arricchire la riga."""
    return (
        fondo.get("ter_origin", "missing") == "missing"
        or not fondo.get("distribution_policy")
        or not fondo.get("replication_method")
    )


def add_fund(symbol: str, name: str, isin: str = ""):
    if any(f["symbol"] == symbol for f in st.session_state.selected):
        st.toast(t("toast.fund_exists", symbol=symbol), icon="⚠️")
        return
    meta = cached_metadata(
        symbol, isin, api_key("EODHD_API_KEY"), st.session_state.ter_refresh_rev,
        justetf=bool(st.session_state.enable_justetf),
    )
    fund_name = meta.get("name") or name
    proxy = px.suggest_proxy(fund_name, symbol)
    alloc, alloc_fonte = classifica(fund_name, symbol, meta)
    holdings = meta.get("holdings") or []
    # Fuori da `classifica()`: il paese non e' una delle tre dimensioni
    # corrette a mano (vedi `al.DIMENSIONE_PAESE`), e' solo una stima che
    # vive nello stesso dizionario per comodita' di lettura.
    alloc["paese"] = al.paesi_da_posizioni(holdings)
    n = len(st.session_state.selected) + 1
    pesi_ridistribuiti = pesi.ridistribuisci(
        [f["weight"] for f in st.session_state.selected] + [0.0],
        fissi={n - 1: 100.0 / n},
    )
    st.session_state.selected.append(_fondo_da_meta(
        symbol=symbol,
        name=fund_name, isin=isin, meta=meta, proxy=proxy,
        alloc=alloc, alloc_fonte=alloc_fonte, holdings=holdings,
    ))
    # I fondi gia' presenti mantengono i loro rapporti reciproci: aggiungere
    # non deve piu' cancellare un'allocazione impostata a mano (era il
    # comportamento di `equalize_weights()`, chiamata qui in precedenza).
    for fondo, peso in zip(st.session_state.selected, pesi_ridistribuiti):
        fondo["weight"] = peso
    st.session_state.composizione_rev += 1
    st.toast(t("toast.fund_added", symbol=symbol), icon="✅")


def _colonna_suggerita(colonne: list[str], *parole: str) -> str:
    """Preseleziona un'intestazione ovvia senza imporre il formato Directa."""
    normalizzate = [directa_io.normalizza_intestazione(colonna) for colonna in colonne]
    cercate = [directa_io.normalizza_intestazione(parola) for parola in parole]
    for parola in cercate:
        for colonna, normalizzata in zip(colonne, normalizzate):
            if normalizzata == parola:
                return colonna
    for colonna, normalizzata in zip(colonne, normalizzate):
        if any(parola in normalizzata for parola in cercate):
            return colonna
    return ""


def _risultati_directa(posizione: directa_io.DirectaPosition) -> list[dict]:
    query = posizione.isin or posizione.ticker
    risultati = cached_search(
        query, True, api_key("EODHD_API_KEY"), api_key("TWELVEDATA_API_KEY")
    )
    if posizione.isin:
        esatti = [r for r in risultati if (r.get("isin") or "").upper() == posizione.isin]
        if esatti:
            return esatti
    ticker = posizione.ticker.upper()
    esatti = [r for r in risultati if (r.get("symbol") or "").upper() == ticker]
    return esatti or risultati


def _testo_issue_directa(issue: directa_io.DirectaIssue) -> str:
    """Traduce i codici del parser senza importare la lingua nella libreria."""
    chiavi = {
        "invalid_isin": "directa.issue_invalid_isin",
        "missing_identifier": "directa.issue_missing_identifier",
        "summary_row": "directa.issue_summary_row",
        "invalid_value": "directa.issue_invalid_value",
        "invalid_quantity": "directa.issue_invalid_quantity",
        "invalid_average": "directa.issue_invalid_average",
    }
    chiave = chiavi.get(issue.code)
    return t(chiave) if chiave else issue.message


def equalize_weights():
    """Reset esplicito a pesi uguali: l'unico modo per perdere volutamente
    un'allocazione personalizzata (pulsante "⚖️ Pesi uguali")."""
    n = len(st.session_state.selected)
    if n:
        for fondo, peso in zip(st.session_state.selected, pesi.uguali(n)):
            fondo["weight"] = peso
        st.session_state.composizione_rev += 1


def rimuovi_fondo(indice: int):
    """Toglie il fondo in posizione `indice` e rinormalizza i pesi dei rimasti
    mantenendo le proporzioni reciproche; il capitale resta investito (il
    valore iniziale del portafoglio non cambia)."""
    if not (0 <= indice < len(st.session_state.selected)):
        return
    rimosso = st.session_state.selected.pop(indice)
    nuovi_pesi = pesi.rinormalizza([f["weight"] for f in st.session_state.selected])
    for fondo, peso in zip(st.session_state.selected, nuovi_pesi):
        fondo["weight"] = peso
    st.session_state.composizione_rev += 1
    st.toast(t("toast.fund_removed", elenco=rimosso["symbol"]), icon="🗑️")


def rimuovi_fondi_assenti(simboli: list[str]):
    """Toglie dal portafoglio i fondi senza prezzi risolti e rinormalizza i
    pesi dei rimasti - stesso schema di `rimuovi_fondo`, ma per un elenco di
    simboli invece che per posizione: e' l'azione dietro il pulsante che
    segue il blocco del backtest quando una fonte non risponde (vedi
    audit-codebase-2026-08-01.md, P1)."""
    da_togliere = set(simboli)
    st.session_state.selected = [
        f for f in st.session_state.selected if f["symbol"] not in da_togliere
    ]
    nuovi_pesi = pesi.rinormalizza([f["weight"] for f in st.session_state.selected])
    for fondo, peso in zip(st.session_state.selected, nuovi_pesi):
        fondo["weight"] = peso
    st.session_state.composizione_rev += 1
    st.toast(t("toast.fund_removed", elenco=", ".join(sorted(simboli))), icon="🗑️")


def set_period(years: int | None):
    """Imposta il periodo dai pulsanti rapidi."""
    today = dt.date.today()
    st.session_state.start_date = (
        MIN_DATE if years is None else today - dt.timedelta(days=365 * years)
    )
    st.session_state.end_date = today


def allinea_periodo_covip(inizio: dt.date, fine: dt.date):
    """Porta il periodo del backtest sulle finestre COVIP, che sono anni
    solari interi. E' la differenza fra un backtest agosto 2021 - luglio 2025
    e la finestra "5 anni = 2021-2025": gli anni di calendario coincidono, la
    copertura no, e senza questo pulsante l'unico modo di accorgersene e'
    leggere le date una per una."""
    st.session_state.start_date = inizio
    st.session_state.end_date = fine


def _salva_preferenze() -> None:
    prefs.save({
        "lingua": str(st.session_state.get("lang", "") or ""),
        "enable_justetf": bool(st.session_state.get("enable_justetf", False)),
        "inflation_enabled": bool(st.session_state.get("inflation_enabled", False)),
        "inflation_area": str(st.session_state.get("inflation_area", "IT") or "IT"),
    })


def _cambia_lingua() -> None:
    """`on_change` del selettore di lingua: gira prima che il resto dello
    script rilegga i widget, quindi qui `st.session_state.rebalance` e'
    ancora il valore buono dell'ultimo run.

    `rebalance` (e allo stesso modo `pac_frequency`, che ne riusa le
    etichette) usa un `format_func` tradotto: al cambio di lingua Streamlit
    proverebbe a deserializzare l'etichetta ormai stale della lingua
    precedente, non la troverebbe fra le nuove opzioni formattate
    (`SelectboxSerde.deserialize`) e la scriverebbe cosi' com'e' in
    `session_state.rebalance` - una stringa che non e' piu' un valore valido
    di `Rebalance`. Rimetterli in coda per `_applica_pending()` lo previene.
    """
    _salva_preferenze()
    st.session_state._pending_state["rebalance"] = st.session_state.get(
        "rebalance", Rebalance.NONE.value
    )
    st.session_state._pending_state["pac_frequency"] = st.session_state.get(
        "pac_frequency", Frequency.MONTHLY.value
    )


def _cambia_justetf() -> None:
    """Ricorda l'opt-in e riprova i metadati mancanti quando viene attivato."""
    _salva_preferenze()
    st.session_state.ter_refresh_rev += 1
    if st.session_state.enable_justetf:
        for fondo in st.session_state.selected:
            if (
                fondo.get("ter_origin", "missing") != "manual"
                or not fondo.get("distribution_policy")
                or not fondo.get("replication_method")
            ):
                _aggiorna_ter(
                    fondo,
                    cached_metadata(
                        fondo["symbol"], fondo.get("isin", ""),
                        api_key("EODHD_API_KEY"), st.session_state.ter_refresh_rev,
                        justetf=True,
                    ),
                )


def _cambia_inflazione() -> None:
    """Ricorda l'opt-in HICP senza rendere obbligatoria la rete."""
    _salva_preferenze()
    st.session_state.inflation_refresh_rev += 1


def _seleziona_benchmark(result: dict) -> None:
    """Salva solo i metadati del benchmark, mai una holding del portafoglio."""
    preferred_source = str(result.get("source", "") or "")
    # OpenFIGI arricchisce la ricerca ISIN ma non e' una fonte di prezzi:
    # conserva le preferenze delle fonti quotazioni e torna all'ordine
    # automatico per quel solo metadato di risoluzione.
    if preferred_source not in SOURCE_OPTIONS:
        preferred_source = AUTO
    st.session_state.benchmark_config = {
        "kind": "custom",
        "symbol": result.get("symbol", ""),
        "name": result.get("name", result.get("symbol", "")),
        "isin": result.get("isin", ""),
        "preferred_source": preferred_source,
    }
    st.session_state.benchmark_choice = "custom"


# --------------------------------------------------------------------------
# Barra laterale
# --------------------------------------------------------------------------

with st.sidebar:
    st.selectbox(
        t("sidebar.lingua_label"), list(i18n.LINGUE), key="lang",
        format_func=lambda code: i18n.LINGUE.get(code, code),
        on_change=_cambia_lingua,
        filter_mode=None,
    )

    st.header(t("sidebar.header"))

    today = dt.date.today()
    st.caption(t("sidebar.periodo_caption"))
    # Due difese contro la stessa cosa: la barra laterale si trascina fino a
    # diventare piu' stretta dell'etichetta di un pulsante, e allora "10a" si
    # spezza in "10" sopra e "a" sotto, che non si legge piu'.
    #
    # La prima e' il layout su due file da tre e da due invece che cinque
    # colonne in fila: ogni pulsante parte con quasi il doppio dello spazio.
    # Non basta pero', perche' la barra si puo' stringere ancora - da qui la
    # seconda, il contenitore con `key` che espone alla CSS in cima al file la
    # classe `.st-key-preset_periodo` e le impone tre caratteri di larghezza
    # minima, che e' quanto serve all'etichetta piu' lunga.
    presets = [
        ("preset.1y", 1), ("preset.5y", 5), ("preset.10y", 10),
        ("preset.20y", 20), ("preset.max", None),
    ]
    with st.container(key="preset_periodo"):
        for riga in (presets[:3], presets[3:]):
            preset_cols = st.columns(3)
            for col, (chiave_label, years) in zip(preset_cols, riga):
                col.button(
                    t(chiave_label),
                    key=f"preset_{years if years is not None else 'max'}",
                    on_click=set_period,
                    args=(years,),
                    width="stretch",
                )

    col_a, col_b = st.columns(2)
    start_date = col_a.date_input(
        t("sidebar.data_inizio"), min_value=MIN_DATE, max_value=today,
        format=FMT_DATA_INPUT, key="start_date",
    )
    end_date = col_b.date_input(
        t("sidebar.data_fine"), min_value=MIN_DATE, max_value=today,
        format=FMT_DATA_INPUT, key="end_date",
    )

    initial_value = st.number_input(
        t("sidebar.valore_iniziale"), min_value=100.0,
        step=1_000.0, format="%.0f", key="initial_value",
    )
    base_ccy = st.selectbox(
        t("sidebar.valuta_riferimento"), CURRENCIES, key="base_ccy",
        filter_mode=None,
    )
    rebalance = Rebalance(
        st.selectbox(
            t("sidebar.ribilanciamento_label"), REBALANCE_OPTIONS, key="rebalance",
            format_func=lambda v: i18n.etichetta_ribilanciamento(LINGUA, v),
            help=t("rebalance.help"),
            filter_mode=None,
        )
    )
    st.caption(
        t("sidebar.rebalance_caption_none") if rebalance is Rebalance.NONE
        else t("sidebar.rebalance_caption_active")
    )
    if st.session_state.get("pac_enabled") and st.session_state.get("pac_amount"):
        # Un versamento periodico e' un ribilanciamento morbido: ogni rata
        # entra ai pesi obiettivo, quindi con "Nessuno" il portafoglio
        # deriva meno di quanto farebbe senza PAC. Vale solo quando il PAC e'
        # davvero attivo: a interruttore spento questa riga non compare.
        st.caption(t("pac.rebalance_caption"))

    st.divider()
    # Sezione avanzata e collassata: chi non la apre non la incontra. Se il
    # PAC arriva gia' attivo - ad esempio da un portafoglio importato -
    # l'expander si apre da solo, cosi' non resta un PAC acceso ma invisibile
    # che produce numeri diversi da quelli attesi senza spiegazione visibile.
    with st.expander(
        t("pac.expander"), expanded=bool(st.session_state.get("pac_enabled"))
    ):
        st.checkbox(t("pac.enable_checkbox"), key="pac_enabled", help=t("pac.help"))
        if st.session_state.pac_enabled:
            st.number_input(
                t("pac.amount_label"), min_value=0.0, step=50.0, format="%.0f",
                key="pac_amount", help=t("pac.amount_help"),
            )
            st.selectbox(
                t("pac.frequency_label"), PAC_FREQUENCY_OPTIONS, key="pac_frequency",
                format_func=lambda v: i18n.etichetta_ribilanciamento(LINGUA, v),
                filter_mode=None,
            )
            st.number_input(
                t("pac.step_up_label"), min_value=0.0, max_value=20.0,
                step=0.25, format="%.2f", key="pac_step_up_pct",
                help=t("pac.step_up_help"),
            )
            st.checkbox(t("pac.limit_window_checkbox"), key="pac_limit_window")
            if st.session_state.pac_limit_window:
                pac_col_a, pac_col_b = st.columns(2)
                pac_col_a.date_input(
                    t("pac.start_label"), min_value=MIN_DATE, max_value=today,
                    format=FMT_DATA_INPUT, key="pac_start",
                )
                pac_col_b.date_input(
                    t("pac.end_label"), min_value=MIN_DATE, max_value=today,
                    format=FMT_DATA_INPUT, key="pac_end",
                )

    st.divider()
    with st.expander(
        t("benchmark.expander"),
        expanded=bool(st.session_state.get("benchmark_config")),
    ):
        benchmark_choices = ["none", "VT", "VFINX", "custom"]
        benchmark_choice = st.selectbox(
            t("benchmark.label"), benchmark_choices, key="benchmark_choice",
            format_func=lambda value: t(f"benchmark.option_{value}"), filter_mode=None,
        )
        if benchmark_choice == "none":
            st.session_state.benchmark_config = None
        elif benchmark_choice in {"VT", "VFINX"}:
            preset_name = t(f"benchmark.option_{benchmark_choice}")
            st.session_state.benchmark_config = {
                "kind": "preset", "symbol": benchmark_choice, "name": preset_name,
                "isin": "", "preferred_source": "yahoo",
            }
        else:
            benchmark_query = st.text_input(
                t("benchmark.search_label"), placeholder=t("benchmark.search_placeholder"),
                key="benchmark_query",
            )
            if benchmark_query:
                benchmark_results = cached_search(
                    benchmark_query, False, api_key("EODHD_API_KEY"),
                    api_key("TWELVEDATA_API_KEY"),
                )
                for i, result in enumerate(benchmark_results):
                    st.button(
                        f"{result['name']} ({result['symbol']})",
                        key=f"benchmark_add_{i}_{result['symbol']}",
                        on_click=_seleziona_benchmark, args=(result,), width="stretch",
                    )
            selected_benchmark = st.session_state.get("benchmark_config")
            if selected_benchmark:
                st.caption(t("benchmark.selected", symbol=selected_benchmark["symbol"]))
                if st.button(t("benchmark.remove_button"), key="benchmark_remove", width="stretch"):
                    st.session_state.benchmark_config = None
                    st.session_state.benchmark_choice = "none"
                    st.rerun()

    with st.expander(t("inflation.expander"), expanded=bool(st.session_state.inflation_enabled)):
        st.checkbox(
            t("inflation.enable_checkbox"), key="inflation_enabled",
            on_change=_cambia_inflazione, help=t("inflation.enable_help"),
        )
        st.selectbox(
            t("inflation.area_label"), ["IT", "EA"], key="inflation_area",
            format_func=lambda value: t(f"inflation.area_{value.lower()}"),
            on_change=_cambia_inflazione, filter_mode=None,
        )
        if st.session_state.inflation_enabled and st.button(
            t("inflation.retry_button"), key="inflation_retry", width="stretch"
        ):
            st.session_state.inflation_refresh_rev += 1
            st.rerun()

    st.divider()
    st.subheader(t("costs.subheader"))
    st.caption(t("costs.caption"))
    show_gross = st.checkbox(
        t("costs.show_gross_checkbox"), key="show_gross"
    )
    with st.expander(t("costs.pic_expander")):
        st.caption(t("costs.pic_caption"))
        st.checkbox(t("costs.pic_enable"), key="pic_costs_enabled")
        if st.session_state.pic_costs_enabled:
            cost_col_a, cost_col_b = st.columns(2)
            with cost_col_a:
                pic_buy_rule = _regola_commissione("buy", t("costs.buy_title"))
            with cost_col_b:
                pic_sell_rule = _regola_commissione("sell", t("costs.sell_title"))
        else:
            pic_buy_rule = pic_costs.TransactionFeeRule()
            pic_sell_rule = pic_costs.TransactionFeeRule()

    st.divider()
    st.subheader(t("history.subheader"))
    extend_history = st.checkbox(
        t("history.checkbox"),
        key="extend_history",
        help=t("history.help"),
    )
    if extend_history:
        st.caption(
            t("history.caption_non_usd", anno=fx.ECB_START.year)
            if base_ccy != "USD" else
            t("history.caption_usd")
        )

    st.divider()
    st.subheader(t("sources.subheader"))

    st.info(t("sources.justetf_info"))
    st.checkbox(
        t("sources.justetf_checkbox"),
        key="enable_justetf",
        help=t("sources.justetf_help"),
        on_change=_cambia_justetf,
    )

    with st.expander(t("api_keys.expander")):
        st.caption(t("api_keys.caption"))
        with st.form("api_keys_form"):
            eodhd_input = st.text_input(
                t("api_keys.eodhd_label"), value=st.session_state.api_keys.get("EODHD_API_KEY", ""),
                type="password", key="eodhd_key_input",
            )
            td_input = st.text_input(
                t("api_keys.td_label"),
                value=st.session_state.api_keys.get("TWELVEDATA_API_KEY", ""),
                type="password", key="td_key_input",
            )
            if st.form_submit_button(t("api_keys.save_button"), width="stretch"):
                st.session_state.api_keys = {
                    "EODHD_API_KEY": eodhd_input.strip(),
                    "TWELVEDATA_API_KEY": td_input.strip(),
                }
                api_keys_store.save(st.session_state.api_keys)
                st.session_state.ter_refresh_rev += 1
                for fondo in st.session_state.selected:
                    if _mancano_metadati_etf(fondo):
                        _aggiorna_ter(
                            fondo,
                            cached_metadata(
                                fondo["symbol"], fondo.get("isin", ""),
                                api_key("EODHD_API_KEY"), st.session_state.ter_refresh_rev,
                                justetf=bool(st.session_state.enable_justetf),
                            ),
                        )
                st.toast(t("api_keys.saved_toast"), icon="🔑")
                st.rerun()
        saved_keys = []
        for key, label in (
            ("EODHD_API_KEY", t("api_keys.eodhd_label")),
            ("TWELVEDATA_API_KEY", t("api_keys.td_label")),
        ):
            value = st.session_state.api_keys.get(key, "")
            if value:
                saved_keys.append(f"{label}: {api_keys_store.masked(value)}")
        if saved_keys:
            st.caption(t("api_keys.saved_caption", elenco="; ".join(saved_keys)))
        if any((v or "").strip() for v in st.session_state.api_keys.values()):
            if st.button(t("api_keys.forget_button"), width="stretch"):
                st.session_state.api_keys = {}
                api_keys_store.clear()
                disk_cache.clear_prefixes(("eodhd", "twelvedata"))
                st.cache_data.clear()
                st.toast(t("api_keys.forgotten_toast"), icon="🗑️")
                st.rerun()

    reg_probe = build_registry()
    for source in reg_probe.all_sources:
        justetf_disabled = source is reg_probe.justetf and not reg_probe.enable_justetf
        ready = source.available() and not justetf_disabled
        st.caption(f"{'🟢' if ready else '⚪'} {i18n.etichetta_fonte(LINGUA, source.name)}"
                   + ("" if ready else (
                       t("sources.status_optin_off") if justetf_disabled
                       else t("sources.status_not_configured")
                   )))
    st.caption(t("sources.order_caption", giorni=disk_cache.restricted_retention_days()))
    if not reg_probe.eodhd.available():
        st.info(t("sources.eodhd_hint"), icon="🇮🇹")

    with st.expander(t("csv.expander")):
        st.caption(t("csv.caption"))
        csv_key = st.text_input(
            t("csv.symbol_label"), key="csv_key",
            placeholder=t("csv.symbol_placeholder"),
        )
        csv_ccy = st.selectbox(
            t("csv.currency_label"), CURRENCIES, key="csv_ccy",
            filter_mode=None,
        )
        uploaded = st.file_uploader(t("csv.file_label"), type=["csv", "txt"])
        if uploaded is not None and csv_key.strip():
            try:
                series = parse_csv(uploaded.getvalue())
            except CsvParseError as exc:
                st.error(str(exc))
            else:
                st.session_state.csv_series[csv_key.strip().upper()] = (
                    series, csv_ccy
                )
                st.success(
                    t(
                        "csv.success",
                        n=len(series),
                        inizio=series.index[0].strftime(FMT_DATA),
                        fine=series.index[-1].strftime(FMT_DATA),
                    )
                )
        if st.session_state.csv_series:
            st.caption(t("csv.loaded_caption", elenco=", ".join(st.session_state.csv_series)))
            if st.button(t("csv.remove_button"), width="stretch"):
                st.session_state.csv_series = {}
                st.rerun()

    st.divider()
    n_cached, mb_cached = disk_cache.stats()
    st.caption(t("cache.caption", n=n_cached, mb=mb_cached))
    if st.button(t("cache.clear_button"), width="stretch"):
        disk_cache.clear()
        st.cache_data.clear()
        st.toast(t("cache.cleared_toast"), icon="🧹")
        st.rerun()

    st.divider()
    # In percentuale a video, in frazione per il motore e per `metric_help()`.
    risk_free = st.number_input(
        t("sidebar.risk_free_label"), min_value=0.0, max_value=20.0,
        step=0.25, format="%.2f", key="risk_free_pct",
    ) / 100

    st.divider()
    with st.expander(t("about.expander")):
        st.caption(t("about.version", versione=__version__))
        st.caption(t("about.license_caption"))
        st.markdown(f"**{t('about.third_party_header')}**")
        st.caption(t("about.third_party_caption"))
        pacchetti = licenses.manifest()
        if pacchetti:
            st.dataframe(
                pd.DataFrame(pacchetti)[["name", "version", "license"]],
                hide_index=True, width="stretch",
                column_config={
                    "name": t("about.col_package"),
                    "version": t("about.col_version"),
                    "license": t("about.col_license"),
                },
            )
        else:
            st.caption(t("about.third_party_missing"))
        testo_licenze = licenses.testo_notices()
        if testo_licenze:
            st.download_button(
                t("about.download_button"), testo_licenze.encode("utf-8"),
                file_name="THIRD_PARTY_NOTICES.txt", mime="text/plain",
            )

    with st.expander(t("directa.expander")):
        st.caption(t("directa.caption"))
        directa_upload = st.file_uploader(
            t("directa.upload_label"), type=["csv", "xlsx"], key="directa_upload"
        )
        if directa_upload is not None:
            if directa_upload.file_id != st.session_state.directa_upload_visto:
                st.session_state.directa_upload_visto = directa_upload.file_id
                st.session_state.directa_file = directa_upload.getvalue()
                st.session_state.directa_filename = directa_upload.name
                st.session_state.directa_sheet = "CSV"
                try:
                    st.session_state.directa_header_row = directa_io.suggest_header_row(
                        st.session_state.directa_file,
                        st.session_state.directa_filename,
                    )
                except directa_io.DirectaParseError:
                    st.session_state.directa_header_row = 0
            try:
                fogli = directa_io.sheet_names(
                    st.session_state.directa_file, st.session_state.directa_filename
                )
                if st.session_state.directa_sheet not in fogli:
                    st.session_state.directa_sheet = fogli[0]
                if len(fogli) > 1:
                    st.selectbox(t("directa.sheet_label"), fogli, key="directa_sheet")
                frame_directa = directa_io.read_table(
                    st.session_state.directa_file,
                    st.session_state.directa_filename,
                    sheet=st.session_state.directa_sheet,
                    header_row=st.session_state.directa_header_row,
                )
            except directa_io.DirectaParseError as exc:
                st.error(t("directa.file_error", errore=str(exc)))
                frame_directa = None
            if frame_directa is not None:
                tipo_export = directa_io.detect_export_kind(frame_directa)
                if tipo_export == "movements":
                    st.warning(t("directa.movements_file"), icon="ℹ️")
                st.number_input(
                    t("directa.header_row_label"), min_value=0, max_value=20, step=1,
                    key="directa_header_row", help=t("directa.header_row_help"),
                )
                # La riga delle intestazioni viene riletta al rerun successivo
                # quando l'utente la cambia; cosi' il widget resta nel suo ordine
                # naturale e non si assegnano chiavi Streamlit gia' istanziate.
                colonne = list(frame_directa.columns)
                nessuna = t("directa.no_column")
                opzioni = [nessuna] + colonne
                col_a, col_b = st.columns(2)
                map_value = col_a.selectbox(
                    t("directa.value_column"), colonne,
                    index=(
                        colonne.index(_colonna_suggerita(
                            colonne, "controvalore", "valoreattuale", "marketvalue",
                            "currentvalue", "valore", "patrimonio", "importo",
                        ))
                        if _colonna_suggerita(
                            colonne, "controvalore", "valoreattuale", "marketvalue",
                            "currentvalue", "valore", "patrimonio", "importo",
                        ) in colonne else 0
                    ),
                    key=f"directa_value_{st.session_state.directa_upload_visto}",
                )
                map_isin = col_b.selectbox(
                    t("directa.isin_column"), opzioni,
                    index=(opzioni.index(_colonna_suggerita(colonne, "isin"))
                           if _colonna_suggerita(colonne, "isin") in opzioni else 0),
                    key=f"directa_isin_{st.session_state.directa_upload_visto}",
                )
                col_c, col_d = st.columns(2)
                map_ticker = col_c.selectbox(
                    t("directa.ticker_column"), opzioni,
                    index=(
                        opzioni.index(_colonna_suggerita(colonne, "ticker", "symbol", "codice"))
                        if _colonna_suggerita(colonne, "ticker", "symbol", "codice") in opzioni
                        else 0
                    ),
                    key=f"directa_ticker_{st.session_state.directa_upload_visto}",
                )
                map_name = col_d.selectbox(
                    t("directa.name_column"), opzioni,
                    index=(
                        opzioni.index(_colonna_suggerita(
                            colonne, "nome", "descrizione", "strumento", "name",
                        ))
                        if _colonna_suggerita(
                            colonne, "nome", "descrizione", "strumento", "name",
                        ) in opzioni
                        else 0
                    ),
                    key=f"directa_name_{st.session_state.directa_upload_visto}",
                )
                col_e, col_f = st.columns(2)
                map_currency = col_e.selectbox(
                    t("directa.currency_column"), opzioni,
                    index=(
                        opzioni.index(_colonna_suggerita(
                            colonne, "valuta", "divisa", "currency", "ccy",
                        ))
                        if _colonna_suggerita(
                            colonne, "valuta", "divisa", "currency", "ccy",
                        ) in opzioni else 0
                    ),
                    key=f"directa_currency_{st.session_state.directa_upload_visto}",
                )
                directa_ccy = col_f.selectbox(
                    t("directa.value_currency"), CURRENCIES, key="directa_value_currency",
                    filter_mode=None,
                )
                col_g, col_h = st.columns(2)
                map_quantity = col_g.selectbox(
                    t("directa.quantity_column"), opzioni,
                    index=(
                        opzioni.index(_colonna_suggerita(colonne, "quantita", "quantity"))
                        if _colonna_suggerita(colonne, "quantita", "quantity") in opzioni else 0
                    ),
                    key=f"directa_quantity_{st.session_state.directa_upload_visto}",
                )
                map_average = col_h.selectbox(
                    t("directa.average_column"), opzioni,
                    index=(
                        opzioni.index(_colonna_suggerita(
                            colonne, "prezzomedio", "carico", "medio", "average",
                        ))
                        if _colonna_suggerita(
                            colonne, "prezzomedio", "carico", "medio", "average",
                        ) in opzioni
                        else 0
                    ),
                    key=f"directa_average_{st.session_state.directa_upload_visto}",
                )
                mapping = directa_io.DirectaColumnMap(
                    value=map_value,
                    isin="" if map_isin == nessuna else map_isin,
                    ticker="" if map_ticker == nessuna else map_ticker,
                    name="" if map_name == nessuna else map_name,
                    currency="" if map_currency == nessuna else map_currency,
                    quantity="" if map_quantity == nessuna else map_quantity,
                    average_price="" if map_average == nessuna else map_average,
                )
                try:
                    parsed_directa = directa_io.parse_positions(
                        frame_directa,
                        mapping,
                        header_row=st.session_state.directa_header_row,
                    )
                except directa_io.DirectaParseError as exc:
                    st.warning(t("directa.mapping_error", errore=str(exc)), icon="⚠️")
                    parsed_directa = None
                if parsed_directa is not None:
                    if parsed_directa.issues:
                        st.warning(
                            t("directa.issues", n=len(parsed_directa.issues)), icon="⚠️"
                        )
                        st.dataframe(
                            pd.DataFrame([
                                {
                                    t("directa.issue_row"): issue.row,
                                    t("directa.issue_column"): issue.column,
                                    t("directa.issue_message"): _testo_issue_directa(issue),
                                }
                                for issue in parsed_directa.issues
                            ]),
                            hide_index=True, width="stretch",
                        )
                    if parsed_directa.positions:
                        st.dataframe(
                            pd.DataFrame([
                                {
                                    t("directa.preview_identifier"): p.identifier,
                                    t("directa.preview_name"): p.name or p.ticker or p.isin,
                                    t("directa.preview_value"): p.current_value,
                                }
                                for p in parsed_directa.positions
                            ]),
                            hide_index=True, width="stretch",
                        )
                    scelte_directa = {}
                    irrisolti = []
                    for posizione in parsed_directa.positions:
                        candidati = _risultati_directa(posizione)
                        if not candidati:
                            irrisolti.append(posizione)
                            continue
                        labels = [
                            f"{c.get('name') or c.get('symbol')} ({c.get('symbol')})"
                            for c in candidati
                        ]
                        scelta = st.selectbox(
                            t(
                                "directa.instrument_label",
                                nome=posizione.name or posizione.identifier,
                            ),
                            range(len(candidati)),
                            format_func=lambda i, labels=labels: labels[i],
                            key=f"directa_choice_{posizione.identifier}_{st.session_state.directa_upload_visto}",
                        )
                        scelte_directa[posizione.identifier] = candidati[scelta]
                    escludi = st.checkbox(t("directa.exclude_unresolved"), key="directa_exclude")
                    if irrisolti:
                        st.warning(
                            t(
                                "directa.unresolved",
                                elenco=", ".join(p.identifier for p in irrisolti),
                            ),
                            icon="🚫",
                        )
                    pronto = bool(scelte_directa) and (
                        not irrisolti or escludi
                    ) and (not parsed_directa.issues or escludi) and tipo_export != "movements"
                    if st.button(t("directa.import_button"), disabled=not pronto, width="stretch"):
                        fondi_directa = []
                        valori = []
                        for posizione in parsed_directa.positions:
                            candidato = scelte_directa.get(posizione.identifier)
                            if candidato is None:
                                continue
                            meta = cached_metadata(
                                candidato["symbol"], posizione.isin or candidato.get("isin", ""),
                                api_key("EODHD_API_KEY"), st.session_state.ter_refresh_rev,
                                justetf=bool(st.session_state.enable_justetf),
                            )
                            nome = meta.get("name") or posizione.name or candidato.get("name", "")
                            alloc, fonte_alloc = classifica(nome, candidato["symbol"], meta)
                            fondo = _fondo_da_meta(
                                candidato["symbol"], nome,
                                posizione.isin or candidato.get("isin", ""), meta,
                                proxy=px.suggest_proxy(nome, candidato["symbol"]),
                                alloc=alloc, alloc_fonte=fonte_alloc,
                            )
                            fondo["currency"] = directa_ccy
                            fondi_directa.append(fondo)
                            valori.append(posizione.current_value)
                        if fondi_directa:
                            for fondo, peso in zip(fondi_directa, pesi.rinormalizza(valori)):
                                fondo["weight"] = peso
                            st.session_state._pending_state.update({
                                "selected": fondi_directa,
                                "initial_value": float(sum(valori)),
                                "base_ccy": directa_ccy,
                            })
                            st.session_state.composizione_rev += 1
                            st.toast(t("directa.import_success", n=len(fondi_directa)), icon="💼")
                            st.rerun()

    with st.expander(t("portfolio_io.expander")):
        st.caption(t("portfolio_io.caption"))
        importato = st.file_uploader(
            t("portfolio_io.upload_label"), type=["json"], key="portfolio_upload",
        )
        portfolio_export = st.empty()
        # `file_uploader` restituisce lo stesso file a ogni rerun finche' resta
        # caricato: senza questo controllo l'import (o l'errore) si ripeterebbe
        # a ogni singolo rerun, non solo quando l'utente carica qualcosa di nuovo.
        if importato is not None and importato.file_id != st.session_state._import_visto:
            st.session_state._import_visto = importato.file_id
            try:
                fondi_importati, parametri_importati = portfolio_io.load(importato.getvalue())
            except portfolio_io.PortfolioError as exc:
                st.error(t("portfolio_io.import_error", errore=str(exc)))
            else:
                # I file salvati da versioni precedenti (o modificati a mano)
                # possono non sommare a 100: l'invariante dell'editor lo
                # richiede da subito, non solo alla prima modifica.
                pesi_normalizzati = pesi.rinormalizza(
                    [f["weight"] for f in fondi_importati]
                )
                for fondo, peso in zip(fondi_importati, pesi_normalizzati):
                    fondo["weight"] = peso
                st.session_state.composizione_rev += 1
                pending = {"selected": fondi_importati}
                if "start_date" in parametri_importati:
                    try:
                        pending["start_date"] = dt.date.fromisoformat(
                            str(parametri_importati["start_date"])
                        )
                    except (TypeError, ValueError):
                        pass
                if "end_date" in parametri_importati:
                    try:
                        pending["end_date"] = dt.date.fromisoformat(
                            str(parametri_importati["end_date"])
                        )
                    except (TypeError, ValueError):
                        pass
                if isinstance(parametri_importati.get("initial_value"), (int, float)):
                    pending["initial_value"] = float(parametri_importati["initial_value"])
                if parametri_importati.get("base_ccy") in CURRENCIES:
                    pending["base_ccy"] = parametri_importati["base_ccy"]
                if parametri_importati.get("rebalance") in REBALANCE_OPTIONS:
                    pending["rebalance"] = parametri_importati["rebalance"]
                if isinstance(parametri_importati.get("show_gross"), bool):
                    pending["show_gross"] = parametri_importati["show_gross"]
                if isinstance(parametri_importati.get("extend_history"), bool):
                    pending["extend_history"] = parametri_importati["extend_history"]
                benchmark_importato = portfolio_io.normalizza_benchmark(
                    parametri_importati.get("benchmark")
                )
                pending["benchmark_config"] = benchmark_importato
                pending["benchmark_choice"] = (
                    benchmark_importato.get("kind") == "preset"
                    and benchmark_importato.get("symbol")
                    or "custom"
                ) if benchmark_importato else "none"
                # Nel file le percentuali restano in frazione (0.02 = 2%): e'
                # il formato dei portafogli gia' esportati e non ha ambiguita'
                # di unita'. La conversione in percentuale avviene qui, al
                # confine con lo stato dei widget.
                if isinstance(parametri_importati.get("risk_free"), (int, float)):
                    pending["risk_free_pct"] = round(
                        float(parametri_importati["risk_free"]) * 100, 6
                    )
                # PAC: se il file lo salva attivo, deve tornare attivo
                # all'import - altrimenti si ricaricherebbe un portafoglio
                # che produce numeri diversi da quelli con cui e' stato
                # salvato, senza che nulla lo segnali.
                if isinstance(parametri_importati.get("pac_enabled"), bool):
                    pending["pac_enabled"] = parametri_importati["pac_enabled"]
                if isinstance(parametri_importati.get("pic_costs_enabled"), bool):
                    pending["pic_costs_enabled"] = parametri_importati["pic_costs_enabled"]
                else:
                    # I file precedenti all'introduzione del prospetto non
                    # contengono regole: importarli deve spegnere un eventuale
                    # profilo rimasto attivo nella sessione corrente.
                    pending["pic_costs_enabled"] = False
                modes = {m.value for m in pic_costs.TransactionFeeMode}
                for key in ("pic_buy_mode", "pic_sell_mode"):
                    if parametri_importati.get(key) in modes:
                        pending[key] = parametri_importati[key]
                    else:
                        pending[key] = pic_costs.TransactionFeeMode.NONE.value
                for key in (
                    "pic_buy_amount", "pic_buy_rate_pct", "pic_buy_min", "pic_buy_max",
                    "pic_sell_amount", "pic_sell_rate_pct", "pic_sell_min", "pic_sell_max",
                ):
                    value = parametri_importati.get(key)
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        if math.isfinite(float(value)) and float(value) >= 0:
                            pending[key] = float(value)
                if isinstance(parametri_importati.get("pac_amount"), (int, float)):
                    pending["pac_amount"] = float(parametri_importati["pac_amount"])
                if parametri_importati.get("pac_frequency") in PAC_FREQUENCY_OPTIONS:
                    pending["pac_frequency"] = parametri_importati["pac_frequency"]
                if isinstance(parametri_importati.get("pac_step_up"), (int, float)):
                    pending["pac_step_up_pct"] = round(
                        float(parametri_importati["pac_step_up"]) * 100, 6
                    )
                if isinstance(parametri_importati.get("pac_limit_window"), bool):
                    pending["pac_limit_window"] = parametri_importati["pac_limit_window"]
                if "pac_start" in parametri_importati:
                    try:
                        pending["pac_start"] = dt.date.fromisoformat(
                            str(parametri_importati["pac_start"])
                        )
                    except (TypeError, ValueError):
                        pass
                if "pac_end" in parametri_importati:
                    try:
                        pending["pac_end"] = dt.date.fromisoformat(
                            str(parametri_importati["pac_end"])
                        )
                    except (TypeError, ValueError):
                        pass
                st.session_state._pending_state.update(pending)
                st.toast(t("portfolio_io.import_success", n=len(fondi_importati)), icon="💼")
                st.rerun()

    st.divider()
    st.caption(t("about.credit"))

# --------------------------------------------------------------------------
# Intestazione e ricerca
# --------------------------------------------------------------------------

st.title(t("app.title"))
st.caption(t("app.subtitle"))

with st.expander(t("search.expander"), expanded=not st.session_state.selected):
    c1, c2 = st.columns([4, 1])
    query = c1.text_input(
        t("search.query_label"),
        placeholder=t("search.query_placeholder"),
        label_visibility="collapsed",
    )
    funds_only = c2.toggle(t("search.funds_only_toggle"), value=True)

    if query:
        with st.spinner(t("search.spinner")):
            results = cached_search(
                query, funds_only, api_key("EODHD_API_KEY"),
                api_key("TWELVEDATA_API_KEY"),
            )
        if not results:
            st.info(t("search.no_results"))
        elif is_isin(query):
            st.caption(t("search.isin_hint"))
        for r in results:
            cols = st.columns([4.3, 1.3, 1.3, 1.1, 1])
            cols[0].markdown(f"**{r['name']}**  \n`{r['symbol']}`")
            cols[1].markdown(f"<small>{r['quote_type']}</small>", unsafe_allow_html=True)
            cols[2].markdown(f"<small>{r['exchange']}</small>", unsafe_allow_html=True)
            fonte = r.get("source", "")
            cols[3].markdown(
                f"<small>{i18n.etichetta_fonte(LINGUA, fonte)}</small>" if fonte else "",
                unsafe_allow_html=True,
            )
            cols[4].button(
                t("search.add_button"), key=f"add_{r['symbol']}",
                on_click=add_fund,
                args=(r["symbol"], r["name"], r.get("isin", "")),
                width="stretch",
            )

# --------------------------------------------------------------------------
# Composizione del portafoglio
# --------------------------------------------------------------------------

st.subheader(t("portfolio.subheader"))

if not st.session_state.selected:
    with portfolio_export:
        st.caption(t("portfolio_io.download_empty_hint"))
    st.info(t("portfolio.empty_hint"))
    st.stop()

def _click_rimuovi_fondo():
    click = st.session_state.get("composizione_rimuovi")
    if click is not None:
        rimuovi_fondo(click["row"])


editor_df = pd.DataFrame([
    {
        "rimuovi": "🗑️",
        "fondo": f["name"],
        "simbolo": f["symbol"],
        "isin": f.get("isin", ""),
        "valuta": f["currency"],
        "distribuzione": _etichetta_caratteristica(
            f.get("distribution_policy", ""), "distribution"
        ),
        "replica": _etichetta_caratteristica(
            f.get("replication_method", ""), "replication"
        ),
        "peso": f["weight"],
        "importo": f["weight"] / 100 * st.session_state.initial_value,
        "ter": f["ter"],
        "extra": f["extra"],
        "source": f.get("source", AUTO),
        "proxy": f.get("proxy", NO_PROXY),
    }
    for f in st.session_state.selected
])

edited = st.data_editor(
    editor_df,
    hide_index=True,
    width="stretch",
    # Righe fisse: l'unico modo di togliere un fondo e' il pulsante nella
    # colonna "rimuovi", sempre visibile. Con "delete" la cancellazione era
    # affidata a una checkbox invisibile a riposo in una colonna vuota e a
    # un cestino che compariva solo in un overlay al passaggio del mouse.
    num_rows="fixed",
    disabled=["fondo", "simbolo", "valuta", "distribuzione", "replica"],
    column_config={
        "rimuovi": st.column_config.ButtonColumn(
            t("editor.col_rimuovi"), width="small", pinned=True,
            alignment="center", type="tertiary",
            help=t("editor.rimuovi_help"),
            on_click=_click_rimuovi_fondo, key="composizione_rimuovi",
        ),
        "fondo": t("editor.col_fondo"),
        "simbolo": t("editor.col_simbolo"),
        "valuta": t("editor.col_valuta"),
        "distribuzione": t("editor.col_distribuzione"),
        "replica": t("editor.col_replica"),
        "isin": st.column_config.TextColumn(
            t("editor.col_isin"), width="small", help=t("editor.isin_help"),
        ),
        "peso": st.column_config.NumberColumn(
            t("editor.col_peso"), min_value=0.0, max_value=100.0, step=1.0, format="%.2f",
            help=t("editor.peso_help"),
        ),
        "importo": st.column_config.NumberColumn(
            t("editor.col_importo", ccy=base_ccy), min_value=0.0, step=100.0,
            format="%,.0f", help=t("editor.importo_help"),
        ),
        "ter": st.column_config.NumberColumn(
            t("editor.col_ter"), min_value=0.0, max_value=10.0, step=0.01, format="%.3f",
            help=t("editor.ter_help"),
        ),
        "extra": st.column_config.NumberColumn(
            t("editor.col_extra"), min_value=0.0, max_value=10.0, step=0.05, format="%.3f",
            help=t("editor.extra_help"),
        ),
        "source": st.column_config.SelectboxColumn(
            t("editor.col_fonte"), options=SOURCE_OPTIONS, width="small",
            format_func=lambda v: i18n.etichetta_fonte(LINGUA, v),
            help=t("editor.fonte_help"),
        ),
        "proxy": st.column_config.SelectboxColumn(
            t("editor.col_proxy"), options=PROXY_OPTIONS, width="small",
            format_func=lambda k: (
                i18n.etichetta_termine(LINGUA, NO_PROXY) if k == NO_PROXY
                else px.CATALOG[k].label
            ),
            help=t("editor.proxy_help"),
        ),
    },
    # La chiave include la revisione e il capitale oltre ai simboli: i pesi e
    # gli importi vengono qui riscritti *a programma* (ridistribuzione,
    # importo->pesi, valore iniziale->importi). Senza questi due elementi
    # Streamlit riapplicherebbe il buffer di modifica della cella gia'
    # committato in un run precedente sopra al nuovo valore calcolato,
    # annullando silenziosamente la ridistribuzione appena fatta.
    key=(
        f"composition_{st.session_state.composizione_rev}_"
        f"{st.session_state.initial_value:.2f}_"
        + "|".join(f["symbol"] for f in st.session_state.selected)
    ),
)

# Con righe fisse la posizione nell'editor coincide sempre con quella in
# `st.session_state.selected`: nessun buco d'indice possibile (la rimozione
# passa dal pulsante/callback sopra, non da qui).
# Scritti subito e incondizionatamente: se peso/importo sono cambiati nello
# stesso batch (vedi sotto), il `st.rerun()` di quel ramo interromperebbe lo
# script prima di un eventuale secondo passaggio su questi campi.
_TOLLERANZA = 0.005
for fondo, (_, row) in zip(st.session_state.selected, edited.iterrows()):
    ter_nuovo = float(row["ter"])
    if abs(ter_nuovo - float(fondo.get("ter", 0.0))) > _TOLLERANZA:
        fondo["ter_origin"] = "manual"
        fondo["ter_auto"] = False
    fondo["ter"] = ter_nuovo
    fondo["extra"] = float(row["extra"])
    isin_nuovo = (row["isin"] or "").strip().upper()
    if isin_nuovo != fondo.get("isin", ""):
        fondo["isin"] = isin_nuovo
        if fondo.get("ter_origin") != "manual":
            st.session_state.ter_refresh_rev += 1
            _aggiorna_ter(
                fondo,
                cached_metadata(
                    fondo["symbol"], isin_nuovo, api_key("EODHD_API_KEY"),
                    st.session_state.ter_refresh_rev,
                    justetf=bool(st.session_state.enable_justetf),
                ),
            )
    fondo["source"] = row["source"]
    fondo["proxy"] = row["proxy"]

pesi_originali = editor_df["peso"].tolist()
pesi_modificati = edited["peso"].tolist()
importi_originali = editor_df["importo"].tolist()
importi_modificati = edited["importo"].tolist()

importo_cambiato = any(
    abs(nuovo - vecchio) > _TOLLERANZA
    for nuovo, vecchio in zip(importi_modificati, importi_originali)
)
peso_cambiato = any(
    abs(nuovo - vecchio) > _TOLLERANZA
    for nuovo, vecchio in zip(pesi_modificati, pesi_originali)
)

if importo_cambiato:
    nuovo_totale, nuovi_pesi = pesi.da_importi(importi_modificati)
    if nuovo_totale < 100.0:
        st.toast(t("weight.error_importo_min", minimo=fmt_money(100.0, base_ccy)), icon="⚠️")
    else:
        for fondo, peso in zip(st.session_state.selected, nuovi_pesi):
            fondo["weight"] = peso
        st.session_state._pending_state["initial_value"] = nuovo_totale
    st.session_state.composizione_rev += 1
    st.rerun()
elif peso_cambiato:
    fissi = {
        i: nuovo
        for i, (nuovo, vecchio) in enumerate(zip(pesi_modificati, pesi_originali))
        if abs(nuovo - vecchio) > _TOLLERANZA
    }
    nuovi_pesi = pesi.ridistribuisci(pesi_originali, fissi=fissi)
    for fondo, peso in zip(st.session_state.selected, nuovi_pesi):
        fondo["weight"] = peso
    st.session_state.composizione_rev += 1
    st.rerun()

parametri_correnti = {
    "start_date": st.session_state.start_date.isoformat(),
    "end_date": st.session_state.end_date.isoformat(),
    "initial_value": st.session_state.initial_value,
    "base_ccy": st.session_state.base_ccy,
    "rebalance": st.session_state.rebalance,
    "show_gross": st.session_state.show_gross,
    "extend_history": st.session_state.extend_history,
    "risk_free": st.session_state.risk_free_pct / 100,
    "pac_enabled": st.session_state.pac_enabled,
    "pac_amount": st.session_state.pac_amount,
    "pac_frequency": st.session_state.pac_frequency,
    "pac_step_up": st.session_state.pac_step_up_pct / 100,
    "pac_limit_window": st.session_state.pac_limit_window,
    "pac_start": st.session_state.pac_start.isoformat(),
    "pac_end": st.session_state.pac_end.isoformat(),
    "pic_costs_enabled": st.session_state.pic_costs_enabled,
    "pic_buy_mode": st.session_state.pic_buy_mode,
    "pic_buy_amount": st.session_state.pic_buy_amount,
    "pic_buy_rate_pct": st.session_state.pic_buy_rate_pct,
    "pic_buy_min": st.session_state.pic_buy_min,
    "pic_buy_max": st.session_state.pic_buy_max,
    "pic_sell_mode": st.session_state.pic_sell_mode,
    "pic_sell_amount": st.session_state.pic_sell_amount,
    "pic_sell_rate_pct": st.session_state.pic_sell_rate_pct,
    "pic_sell_min": st.session_state.pic_sell_min,
    "pic_sell_max": st.session_state.pic_sell_max,
    "benchmark": st.session_state.get("benchmark_config"),
}
payload = portfolio_io.dump(st.session_state.selected, parametri_correnti)
with portfolio_export:
    st.download_button(
        t("portfolio_io.download_button"), payload.encode("utf-8"),
        file_name=f"portafoglio_{dt.date.today().isoformat()}.json",
        mime="application/json",
    )

total_weight = sum(f["weight"] for f in st.session_state.selected)

b1, b2, b3, b4, b5 = st.columns([1, 1, 1, 1, 2])
b1.button(t("editor.equalize_button"), on_click=equalize_weights, width="stretch")
if b2.button(t("editor.clear_button"), width="stretch"):
    st.session_state.selected = []
    st.rerun()
b3.metric(t("editor.total_weight_metric"), f"{total_weight:.1f}%")
b4.metric(t("editor.total_value_metric"), fmt_money(st.session_state.initial_value, base_ccy))

missing_ter = [f["symbol"] for f in st.session_state.selected
               if f.get("ter_origin", "missing") == "missing"]
ter_sources = [
    f"{f['symbol']}: {i18n.etichetta_fonte(LINGUA, f.get('ter_origin', ''))}"
    for f in st.session_state.selected
    if f.get("ter_origin") in {"manual", "yahoo", "justetf", "eodhd"}
]
if ter_sources:
    st.caption(t("ter_warning.sources", elenco="; ".join(ter_sources)))
if missing_ter:
    eodhd_probe = Registry(eodhd_key=api_key("EODHD_API_KEY")).eodhd
    if eodhd_probe.available() and eodhd_probe.fundamentals_blocked():
        motivo = t("ter_warning.reason_eodhd_blocked")
    else:
        motivo = t("ter_warning.reason_none")
    b5.warning(
        t("ter_warning.message", elenco=", ".join(missing_ter), motivo=motivo),
        icon="ℹ️",
    )
    for fondo in st.session_state.selected:
        if fondo.get("ter_origin", "missing") != "missing":
            continue
        tentativi = fondo.get("ter_attempts") or []
        if tentativi:
            esiti = " · ".join(
                f"{i18n.etichetta_fonte(LINGUA, a.get('source', ''))}: "
                f"{i18n.etichetta_esito(LINGUA, a.get('outcome', ''))}"
                for a in tentativi
            )
            st.caption(t("ter_warning.attempts", symbol=fondo["symbol"], esiti=esiti))
    if b5.button(t("ter_warning.retry_button"), width="stretch"):
        st.session_state.ter_refresh_rev += 1
        for fondo in st.session_state.selected:
            if fondo.get("ter_origin", "missing") != "missing":
                continue
            _aggiorna_ter(
                fondo,
                cached_metadata(
                    fondo["symbol"], fondo.get("isin", ""), api_key("EODHD_API_KEY"),
                    st.session_state.ter_refresh_rev,
                    justetf=bool(st.session_state.enable_justetf),
                ),
            )
        st.rerun()

if total_weight <= 0:
    st.error(t("weight.error_zero"))
    st.stop()
if abs(total_weight - 100) > 0.5:
    st.warning(t("weight.warning_normalized", tot=total_weight), icon="⚠️")
if start_date >= end_date:
    st.error(t("dates.error_order"))
    st.stop()

# --------------------------------------------------------------------------
# Recupero dei prezzi
# --------------------------------------------------------------------------

registry = build_registry()
specs = [
    {"symbol": f["symbol"], "isin": f.get("isin", ""), "source": f.get("source", AUTO)}
    for f in st.session_state.selected
]

with st.spinner(t("prices.spinner")):
    frame = registry.resolve_many(specs, start_date, end_date, base_ccy)

if frame.prices.empty:
    st.error(t("prices.error_none"))
    for symbol, res in frame.resolutions.items():
        st.caption(
            f"**{symbol}** — " + ", ".join(
                f"{a.source}: {i18n.etichetta_esito(LINGUA, a.outcome)}" for a in res.attempts
            )
        )
    st.stop()

if frame.missing:
    with st.expander(t("prices.missing_expander", n=len(frame.missing)), expanded=True):
        for symbol in frame.missing:
            attempts = frame.resolutions[symbol].attempts
            st.markdown(
                f"**{symbol}** — " + ", ".join(
                    f"`{a.source}` {i18n.etichetta_esito(LINGUA, a.outcome)}" for a in attempts
                )
            )
        st.caption(t("prices.missing_hint"))

# Conversione valutaria: le fonti che restituiscono gia' la valuta richiesta
# (justETF, CSV in valuta base) attraversano questo passaggio senza modifiche.
fx_res = fx.convert_currency(
    frame.prices, frame.currencies, base_ccy, start_date, end_date
)
prices = fx_res.prices

if prices.empty:
    st.error(t("fx.error_none"))
    st.stop()

if fx_res.failed:
    causa = ""
    if registry.eodhd.available() and registry.eodhd.fundamentals_blocked():
        causa = t("fx.error_failed_eodhd_cause")
    st.error(
        t("fx.error_failed", elenco=", ".join(fx_res.failed)) + causa,
        icon="🚫",
    )
if fx_res.converted:
    origins = ", ".join(
        f"{s} ({frame.currencies.get(s, '?')} via "
        f"{i18n.etichetta_fonte(LINGUA, fx_res.sources.get(s, ''))})"
        for s in fx_res.converted
    )
    st.caption(t("fx.converted_caption", ccy=base_ccy, elenco=origins))
if fx_res.truncated:
    detail = ", ".join(
        t("fx.truncated_detail_item", symbol=s, data=d.strftime(FMT_DATA))
        for s, d in fx_res.truncated.items()
    )
    st.warning(t("fx.truncated_warning", dettaglio=detail), icon="💱")

used_sources = []
for symbol, src in frame.sources.items():
    if symbol not in prices.columns:
        continue
    used_sources.append(f"{symbol} → **{i18n.etichetta_fonte(LINGUA, src)}**")
if used_sources:
    st.caption(t("sources.used_caption", elenco=", ".join(used_sources)))

# --------------------------------------------------------------------------
# Estensione dello storico
# --------------------------------------------------------------------------

splice_dates: dict[str, pd.Timestamp] = {}

if extend_history:
    notes: list[str] = []
    # Le serie estese si raccolgono in un dizionario e il frame si ricostruisce
    # alla fine: assegnare una serie piu' lunga a una colonna esistente non
    # allunga l'indice del DataFrame, pandas allinea e scarta il di piu'.
    extended_cols: dict[str, pd.Series] = {c: prices[c] for c in prices.columns}

    for fund in st.session_state.selected:
        symbol = fund["symbol"]
        proxy_key = fund.get("proxy", NO_PROXY)
        if symbol not in prices.columns or proxy_key == NO_PROXY:
            continue
        proxy = px.CATALOG.get(proxy_key)
        if proxy is None:
            continue

        with st.spinner(t("history.reconstructing_spinner", symbol=symbol, proxy=proxy.symbol)):
            proxy_series, _ = px.fetch_proxy_series(
                proxy, start_date, end_date, base_ccy
            )
        if proxy_series is None:
            notes.append(t("history.proxy_unavailable", symbol=symbol, proxy=proxy.symbol))
            continue

        ext = px.extend_with_proxy(
            prices[symbol].dropna(), proxy_series, proxy, ter=fund["ter"] / 100
        )
        if ext is None:
            notes.append(t("history.proxy_not_older", symbol=symbol, proxy=proxy.symbol))
            continue

        extended_cols[symbol] = ext.series
        splice_dates[symbol] = ext.splice_date
        caveat = f" — {t('proxy.caveat_price_only')}" if proxy.caveat else ""
        notes.append(
            t(
                "history.reconstructed_note",
                symbol=symbol, data=ext.series.index[0].strftime(FMT_DATA),
                proxy_label=proxy.label, caveat=caveat,
            )
        )

    prices = pd.DataFrame(extended_cols).sort_index()

    if notes:
        with st.expander(t("history.expander"), expanded=True):
            for note in notes:
                st.markdown("- " + note)
            st.caption(t("history.reconstructed_caption"))

for symbol, prima_data in coverage_warnings(prices, start_date):
    st.warning(t("coverage_warning", symbol=symbol, data=prima_data.strftime(FMT_DATA)), icon="📅")

# --------------------------------------------------------------------------
# Integrità del backtest: nessun fondo si esclude in silenzio
# --------------------------------------------------------------------------
# Un fondo senza prezzi risolti (fonte irraggiungibile, cambio non
# risolvibile) non deve sparire dal calcolo senza che sia una scelta
# esplicita: il motore rinormalizzerebbe i pesi dei rimasti e il backtest
# mostrerebbe un risultato valido ma riferito a un portafoglio diverso da
# quello impostato (vedi audit-codebase-2026-08-01.md, P1). Si blocca e si
# offre un'unica azione esplicita per procedere senza quei fondi.
assenti = [f["symbol"] for f in st.session_state.selected if f["symbol"] not in prices.columns]
if assenti:
    rimasti = [f for f in st.session_state.selected if f["symbol"] not in assenti]
    pesi_reali = pesi.rinormalizza([f["weight"] for f in rimasti])
    allocazione = " · ".join(f"{f['name']} {p:.0f}%" for f, p in zip(rimasti, pesi_reali))
    st.error(t("integrita.error_fondi_assenti", elenco=", ".join(assenti)))
    if allocazione:
        st.caption(t("integrita.allocazione_reale", elenco=allocazione))
    st.button(t("integrita.button_rimuovi"), on_click=rimuovi_fondi_assenti, args=(assenti,))
    st.stop()

# --------------------------------------------------------------------------
# Backtest
# --------------------------------------------------------------------------

holdings = [
    Holding(
        symbol=f["symbol"],
        label=f["name"],
        weight=f["weight"] / 100,
        ter=f["ter"] / 100,
        extra_cost=f["extra"] / 100,
    )
    for f in st.session_state.selected
]

# `pac` resta None quando la sezione avanzata e' spenta o la rata e' zero: e'
# cio' che fa prendere a `run_backtest` esattamente il percorso di codice di
# sempre, con `res.nav` identica a `res.portfolio` per costruzione.
pac = None
if st.session_state.pac_enabled and st.session_state.pac_amount:
    pac = Pac(
        amount=st.session_state.pac_amount,
        frequency=Frequency(st.session_state.pac_frequency),
        step_up=st.session_state.pac_step_up_pct / 100,
        start=st.session_state.pac_start if st.session_state.pac_limit_window else None,
        end=st.session_state.pac_end if st.session_state.pac_limit_window else None,
    )

try:
    res = run_backtest(prices, holdings, initial_value, rebalance, FeeMode.NET, pac)
except BacktestInputError as exc:
    st.error(t(f"engine.error_{exc.kind}", elenco=", ".join(exc.symbols)))
    st.stop()
except ValueError as exc:
    st.error(str(exc))
    st.stop()

# --------------------------------------------------------------------------
# Benchmark e rendimento reale: viste derivate, mai parte del backtest base
# --------------------------------------------------------------------------

benchmark_resolution = None
benchmark_curve = None
benchmark_nav = None
benchmark_analysis = None
benchmark_error = ""
portfolio_correlation = pd.DataFrame()
benchmark_config = portfolio_io.normalizza_benchmark(
    st.session_state.get("benchmark_config")
)
if benchmark_config:
    benchmark_resolution = registry.resolve(
        benchmark_config["symbol"], start_date, end_date, base_ccy,
        isin=benchmark_config.get("isin", ""),
        preferred=benchmark_config.get("preferred_source", "") or AUTO,
    )
    if benchmark_resolution.ok:
        raw_benchmark = benchmark_resolution.series.prices
        converted_benchmark = fx.convert_currency(
            raw_benchmark.to_frame(benchmark_config["symbol"]),
            {benchmark_config["symbol"]: benchmark_resolution.series.currency},
            base_ccy, start_date, end_date,
        )
        if benchmark_config["symbol"] in converted_benchmark.prices:
            raw_benchmark = converted_benchmark.prices[benchmark_config["symbol"]].dropna()
        else:
            raw_benchmark = pd.Series(dtype=float)
        # Il forward-fill e' ammesso solo fra due quotazioni reali: non si
        # prolunga il benchmark oltre l'ultima data pubblicata.
        common_index = res.nav.index[
            (res.nav.index >= raw_benchmark.index.min())
            & (res.nav.index <= raw_benchmark.index.max())
        ] if not raw_benchmark.empty else pd.DatetimeIndex([])
        if len(common_index) >= 2:
            benchmark_prices = raw_benchmark.reindex(common_index).ffill().dropna()
            # Si ricrea anche il portafoglio sul calendario comune: cosi' la
            # prima quota, le rate PAC e gli eventuali ribilanciamenti hanno
            # esattamente gli stessi riferimenti temporali sui due lati.
            common_prices = prices.reindex(common_index).ffill().dropna(how="any")
            common_res = run_backtest(
                common_prices, holdings, initial_value, rebalance, FeeMode.NET, pac
            )
            benchmark_curve, _ = simulate(
                benchmark_prices.to_frame("__benchmark"), {"__benchmark": 1.0},
                initial_value, rebalance, pac,
            )
            benchmark_nav = nav_curve(
                benchmark_curve,
                contribution_schedule(benchmark_prices.index, pac),
                initial_value,
            )
            benchmark_analysis = comparative.compare(
                common_res.nav, benchmark_nav,
            )
            st.caption(t(
                "benchmark.source",
                source=i18n.etichetta_fonte(
                    LINGUA, benchmark_resolution.series.source
                ),
                symbol=benchmark_config["symbol"],
            ))
            tentativi_benchmark = " · ".join(
                f"{i18n.etichetta_fonte(LINGUA, attempt.source)}: "
                f"{i18n.etichetta_esito(LINGUA, attempt.outcome)}"
                for attempt in benchmark_resolution.attempts
            )
            if tentativi_benchmark:
                st.caption(t("benchmark.attempts", elenco=tentativi_benchmark))
        else:
            benchmark_error = t("benchmark.common_period_short")
    else:
        benchmark_error = " · ".join(
            f"{i18n.etichetta_fonte(LINGUA, attempt.source)}: "
            f"{i18n.etichetta_esito(LINGUA, attempt.outcome)}"
            for attempt in benchmark_resolution.attempts
        )

portfolio_curves = res.per_fund_nav.rename(columns=res.labels).copy()
portfolio_curves[t("benchmark.portfolio_label")] = res.nav
if benchmark_nav is not None:
    portfolio_curves[benchmark_config["name"]] = benchmark_nav
portfolio_correlation = comparative.correlation_matrix(portfolio_curves)
if benchmark_config is None:
    benchmark_analysis = comparative.compare(res.nav)

inflation_result = inflation.HICPResult(
    pd.Series(dtype=float), st.session_state.get("inflation_area", "IT")
)
real_nav = pd.Series(dtype=float)
real_invested = pd.Series(dtype=float)
inflation_factors = pd.Series(dtype=float)
if st.session_state.get("inflation_enabled"):
    inflation_result = inflation.fetch_hicp(
        st.session_state.inflation_area, start_date, end_date,
        force=bool(st.session_state.inflation_refresh_rev),
    )
    st.session_state.inflation_refresh_rev = 0
    if not inflation_result.series.empty:
        real_nav, real_invested, inflation_factors = inflation.deflate_pac(
            res.nav, res.invested, res.cashflows, inflation_result.series,
        )

pic_estimate = None
if st.session_state.pic_costs_enabled and pac is None:
    try:
        pic_estimate = pic_costs.estimate_pic_costs(
            initial_value,
            {f["symbol"]: f["weight"] / 100 for f in st.session_state.selected},
            {symbol: float(value) for symbol, value in res.contributions.iloc[-1].items()},
            pic_buy_rule,
            pic_sell_rule,
            currency=base_ccy,
        )
    except pic_costs.PicCostError as exc:
        st.error(t("costs.pic_error", errore=str(exc)))
    else:
        with st.expander(t("costs.pic_result_expander"), expanded=True):
            st.caption(t("costs.pic_result_caption"))
            metric_a, metric_b, metric_c, metric_d = st.columns(4)
            metric_a.metric(t("costs.pic_budget"), fmt_money(pic_estimate.budget, base_ccy))
            metric_b.metric(
                t("costs.pic_buy_total"),
                fmt_money(pic_estimate.buy_cost, base_ccy, decimals=2),
            )
            metric_c.metric(
                t("costs.pic_sell_total"),
                fmt_money(pic_estimate.sell_cost, base_ccy, decimals=2),
            )
            metric_d.metric(
                t("costs.pic_net_final"),
                fmt_money(pic_estimate.final_net, base_ccy, decimals=2),
            )
            st.dataframe(
                pd.DataFrame([
                    {
                        t("costs.pic_column_item"): t("costs.pic_line_investable"),
                        t("costs.pic_column_value"): pic_estimate.investable,
                    },
                    {
                        t("costs.pic_column_item"): t("costs.pic_line_before_sell"),
                        t("costs.pic_column_value"): pic_estimate.final_before_sell,
                    },
                    {
                        t("costs.pic_column_item"): t("costs.pic_line_without"),
                        t("costs.pic_column_value"): pic_estimate.final_without_costs,
                    },
                    {
                        t("costs.pic_column_item"): t("costs.pic_line_difference"),
                        t("costs.pic_column_value"): pic_estimate.difference,
                    },
                ]),
                hide_index=True, width="stretch",
                column_config={
                    t("costs.pic_column_item"): t("costs.pic_column_item"),
                    t("costs.pic_column_value"): st.column_config.NumberColumn(
                        t("costs.pic_column_value"), format="%.2f",
                    ),
                },
            )
            dettagli_pic = [
                {
                    t("costs.pic_column_side"): t("costs.pic_buy_title"),
                    t("costs.pic_column_symbol"): line.symbol,
                    t("costs.pic_column_notional"): line.notional,
                    t("costs.pic_column_fee"): line.fee,
                }
                for line in pic_estimate.buy_lines
            ] + [
                {
                    t("costs.pic_column_side"): t("costs.pic_sell_title"),
                    t("costs.pic_column_symbol"): line.symbol,
                    t("costs.pic_column_notional"): line.notional,
                    t("costs.pic_column_fee"): line.fee,
                }
                for line in pic_estimate.sell_lines
            ]
            st.dataframe(
                pd.DataFrame(dettagli_pic),
                hide_index=True,
                width="stretch",
                column_config={
                    t("costs.pic_column_notional"): st.column_config.NumberColumn(
                        t("costs.pic_column_notional"), format="%.2f",
                    ),
                    t("costs.pic_column_fee"): st.column_config.NumberColumn(
                        t("costs.pic_column_fee"), format="%.2f",
                    ),
                },
            )

st.divider()
st.subheader(
    t("results.subheader", inizio=res.start.strftime(FMT_DATA), fine=res.end.strftime(FMT_DATA))
)

# `splice_dates` e' gia' per simbolo, la stessa chiave con cui `res.per_fund`
# e le altre colonne del risultato sono indicizzate: nessuna conversione a
# etichetta serve piu' per tratteggiare i grafici per fondo.
portfolio_splice = max(splice_dates.values()) if splice_dates else None

# Metriche calcolate sulla NAV, non sul valore grezzo del portafoglio: senza
# PAC le due curve sono lo stesso oggetto, quindi questa riga non cambia
# nulla di cio' che si vedeva prima. Con il PAC attivo e' cio' che tiene
# total_return/CAGR/volatilita'/Sharpe/drawdown veri, invece che gonfiati da
# ogni versamento letto come un guadagno di mercato.
summary = mt.summarize(res.nav, risk_free)
years = (res.end - res.start).days / 365.25

mhelp = metric_help(risk_free, initial_value, base_ccy)

k = st.columns(5)
k[0].metric(i18n.etichetta_metrica(LINGUA, "final_value"),
            fmt_money(summary["final_value"], base_ccy),
            fmt_pct(summary["total_return"]), help=mhelp["final_value"])
k[1].metric(i18n.etichetta_metrica(LINGUA, "cagr"), fmt_pct(summary["cagr"]), help=mhelp["cagr"])
k[2].metric(i18n.etichetta_metrica(LINGUA, "volatility"),
            fmt_pct(summary["volatility"]), help=mhelp["volatility"])
k[3].metric(i18n.etichetta_metrica(LINGUA, "max_drawdown"),
            fmt_pct(summary["max_drawdown"]), help=mhelp["max_drawdown"])
k[4].metric(i18n.etichetta_metrica(LINGUA, "sharpe"),
            f"{summary['sharpe']:.2f}", help=mhelp["sharpe"])

if pac is not None:
    # Il portafoglio (non la NAV) e' il saldo vero del conto: qui la
    # domanda e' "quanto ho versato" e "quanto ha reso il mio denaro", non
    # "come si e' comportato lo strumento" - quella e' sopra. Il saldo apre
    # la riga perche' senza di lui resterebbe implicito (versato + guadagno)
    # ed e' lo stesso numero della colonna "Valore finale" nel confronto.
    saldo = float(res.portfolio.iloc[-1])
    versato = float(res.invested.iloc[-1])
    guadagno = saldo - versato
    tasso_xirr = mt.xirr(res.cashflows, saldo, res.end)
    kp = st.columns(4)
    kp[0].metric(i18n.etichetta_metrica(LINGUA, "balance"),
                 fmt_money(saldo, base_ccy), help=mhelp["balance"])
    kp[1].metric(i18n.etichetta_metrica(LINGUA, "invested"),
                 fmt_money(versato, base_ccy), help=mhelp["invested"])
    kp[2].metric(i18n.etichetta_metrica(LINGUA, "gain"),
                 fmt_money(guadagno, base_ccy), help=mhelp["gain"])
    kp[3].metric(i18n.etichetta_metrica(LINGUA, "xirr"),
                 fmt_pct(tasso_xirr), help=mhelp["xirr"])

if portfolio_splice is not None and portfolio_splice > res.start:
    st.info(
        t(
            "results.reconstructed_info",
            inizio=res.start.strftime(FMT_DATA), fine=portfolio_splice.strftime(FMT_DATA),
        ),
        icon="🧩",
    )

with st.expander(t("metrics.explainer_expander")):
    nomi_metriche = [
        "final_value", "total_return", "cagr", "volatility", "sharpe", "sortino",
        "max_drawdown", "calmar", "best_year", "worst_year", "ter_cost", "reconstructed",
    ]
    if pac is not None:
        nomi_metriche += ["balance", "invested", "gain", "xirr"]
    for nome in nomi_metriche:
        st.markdown(f"- **{i18n.etichetta_metrica(LINGUA, nome)}** — {mhelp[nome]}")

# --- Impatto dei costi -----------------------------------------------------

if res.fee_drag > 0:
    pct_lost = res.fee_drag / res.portfolio_gross.iloc[-1]
    st.info(
        t(
            "costs.impact_info",
            anni=years, costo=fmt_money(res.fee_drag, base_ccy), pct=fmt_pct(pct_lost),
            lordo=fmt_money(res.portfolio_gross.iloc[-1], base_ccy),
            netto=fmt_money(res.portfolio.iloc[-1], base_ccy),
        ),
        icon="💸",
    )

# --- Grafici ---------------------------------------------------------------


def split_at(series: pd.Series, splice: pd.Timestamp | None):
    """Divide una serie nel tratto ricostruito e in quello reale."""
    if splice is None:
        return None, series
    return series.loc[:splice], series.loc[splice:]


def curva_sintetica_covip(
    rendimento_annuo: float, inizio: dt.date, fine: dt.date, capitale: float, pac: Pac | None,
) -> pd.Series:
    """Crescita costante al rendimento COVIP, con lo stesso PAC del portafoglio.

    Senza PAC e' `covip.serie_sintetica` cosi' com'e'. Con il PAC attivo, una
    retta ferma al solo capitale iniziale farebbe apparire il portafoglio
    (che riceve versamenti) sempre piu' in vantaggio per un motivo che non ha
    nulla a che fare col rendimento: il confronto sarebbe visivamente falso.
    Si passa quindi la stessa serie sintetica, come prezzo, allo stesso
    motore di simulazione con lo stesso piano di versamenti.
    """
    if pac is None:
        return covip.serie_sintetica(rendimento_annuo, inizio, fine, capitale)
    prezzi = covip.serie_sintetica(rendimento_annuo, inizio, fine, capitale=1.0)
    if prezzi.empty:
        return prezzi
    valore, _ = simulate(prezzi.to_frame("x"), {"x": 1.0}, capitale, Rebalance.NONE, pac)
    return valore


def ciambella(quote: dict[str, float]) -> go.Figure:
    """Ciambella di una ripartizione, dalla quota maggiore alla minore.

    "Non classificato" e "Resto del fondo" sono sempre grigi e mai colorati
    con la palette: non sono una categoria come le altre - il primo dice "non
    so cosa sia", il secondo "non e' fra le prime posizioni lette" - e non
    devono sembrarlo.
    """
    etichette = list(quote)
    grigi = {al.NON_CLASSIFICATO, al.RESTO_FONDO}
    colori = [
        "#9ca3af" if e in grigi else PALETTE[i % len(PALETTE)]
        for i, e in enumerate(etichette)
    ]
    fig = go.Figure(go.Pie(
        labels=[i18n.etichetta_termine(LINGUA, e) for e in etichette],
        values=[quote[e] for e in etichette],
        hole=0.55,
        sort=False,  # `aggrega` ordina gia' per quota decrescente
        direction="clockwise",
        marker=dict(colors=colori),
        textinfo="percent",
        hovertemplate="%{label}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="top", y=-0.02, x=0),
    )
    return fig


# I comparti scelti e l'interruttore della curva sintetica vivono nella scheda
# previdenza, che viene dopo il grafico del portafoglio. Streamlit riporta i
# valori dei widget con chiave in `session_state` **prima** di eseguire lo
# script, quindi qui si legge gia' la scelta corrente e non quella precedente.
_scelte = set(st.session_state.get("comparti_previdenza") or [])
comparti_scelti = (
    [c for c in covip.catalogo() if c.chiave in _scelte] if _scelte else []
)
mostra_sintetiche = bool(st.session_state.get("curve_sintetiche"))

tab1, tab_bil, tab2, tab3, tab4, tab5 = st.tabs([
    t("tab.portafoglio"), t("tab.bilanciamento"), t("tab.confronto"),
    t("tab.drawdown"), t("tab.dati"), t("tab.previdenza"),
])

with tab1:
    fig = go.Figure()
    recon, real = split_at(res.portfolio, portfolio_splice)
    if recon is not None and len(recon) > 1:
        fig.add_trace(go.Scatter(
            x=recon.index, y=recon.values, name=t("chart.legend_reconstructed"),
            line=dict(color=PALETTE[0], width=2, dash="dot"), opacity=0.75,
            hovertemplate=f"%{{x|{FMT_DATA}}}<br>%{{y:,.0f}}"
                          f"{t('chart.hover_reconstructed_suffix')}<extra></extra>",
        ))
    fig.add_trace(go.Scatter(
        x=real.index, y=real.values, name=t("chart.legend_net"),
        line=dict(color=PALETTE[0], width=2.5),
        hovertemplate=f"%{{x|{FMT_DATA}}}<br>%{{y:,.0f}}<extra></extra>",
    ))
    if show_gross:
        fig.add_trace(go.Scatter(
            x=res.portfolio_gross.index, y=res.portfolio_gross.values,
            name=t("chart.legend_gross"),
            line=dict(color=PALETTE[0], width=1.5, dash="dash"), opacity=0.6,
            hovertemplate=f"%{{x|{FMT_DATA}}}<br>%{{y:,.0f}}<extra></extra>",
        ))
    if not real_nav.empty:
        fig.add_trace(go.Scatter(
            x=real_nav.index, y=real_nav.values,
            name=t("inflation.real_curve"),
            line=dict(color="#d97706", width=2, dash="dot"),
            hovertemplate=f"%{{x|{FMT_DATA}}}<br>%{{y:,.0f}}<extra></extra>",
        ))
    if portfolio_splice is not None and portfolio_splice > res.start:
        fig.add_vline(
            x=portfolio_splice, line=dict(color="#6b7280", width=1, dash="dot"),
            annotation_text=t("chart.annotation_real_start"), annotation_position="top left",
        )

    # Curve dei fondi pensione: crescita costante al rendimento COVIP. Non
    # passano dal motore di backtest, dove una retta perfetta darebbe
    # volatilita' e drawdown nulli e uno Sharpe senza senso.
    if mostra_sintetiche and comparti_scelti:
        orizzonte_curva = st.session_state.get("orizzonte_curva", 10)
        for i, comparto in enumerate(comparti_scelti):
            rendimento = comparto.rendimenti.get(orizzonte_curva)
            if rendimento is None:
                continue
            curva = curva_sintetica_covip(
                rendimento / 100, res.start.date(), res.end.date(), initial_value, pac
            )
            fig.add_trace(go.Scatter(
                x=curva.index, y=curva.values,
                name=t("chart.legend_synthetic", comparto=comparto.comparto),
                line=dict(color=PALETTE[(i + 4) % len(PALETTE)], width=1.5, dash="dashdot"),
                opacity=0.8,
                hovertemplate="%{y:,.0f}<extra>" + comparto.comparto
                              + t("chart.hover_constant_growth") + "</extra>",
            ))

    if pac is not None:
        # Con i versamenti in corso una riga ferma al capitale iniziale
        # mentirebbe: la curva del versato cresce nel tempo.
        fig.add_trace(go.Scatter(
            x=res.invested.index, y=res.invested.values,
            name=t("chart.legend_invested"),
            line=dict(color="#9ca3af", width=1, dash="dash"),
            hovertemplate="%{y:,.0f}<extra>" + t("chart.legend_invested") + "</extra>",
        ))
        if res.pic is not None:
            # Lo stesso denaro totale versato tutto il primo giorno: il
            # termine di paragone naturale del PAC.
            fig.add_trace(go.Scatter(
                x=res.pic.index, y=res.pic.values, name=t("chart.legend_pic"),
                line=dict(color=PALETTE[4], width=1.5, dash="dot"), opacity=0.8,
                hovertemplate=f"%{{x|{FMT_DATA}}}<br>%{{y:,.0f}}"
                              "<extra>" + t("chart.legend_pic") + "</extra>",
            ))
    else:
        fig.add_hline(y=initial_value, line=dict(color="#9ca3af", width=1, dash="dash"),
                      annotation_text=t("chart.annotation_initial_capital"),
                      annotation_position="bottom right")
    fig.update_layout(
        height=460, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title=t("chart.yaxis_value", ccy=base_ccy), xaxis_title=None,
        xaxis=ASSE_TEMPO,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig, width="stretch")

    if st.session_state.get("inflation_enabled"):
        if inflation_result.error and real_nav.empty:
            st.warning(t("inflation.failed", errore=inflation_result.error), icon="⚠️")
        elif real_nav.empty:
            st.warning(t("inflation.coverage_missing"), icon="⚠️")
        elif not real_nav.empty:
            # Per rendere il confronto nominale/reale simmetrico si usa lo
            # stesso tratto coperto dall'HICP; le metriche nominali principali
            # sopra restano invece calcolate sull'intero backtest.
            nominal_covered = res.nav.reindex(real_nav.index).dropna()
            nominal_summary = mt.summarize(nominal_covered)
            real_summary = mt.summarize(real_nav)
            st.markdown(t("inflation.metrics_header"))
            metric_frame = pd.DataFrame([
                {
                    t("inflation.metric_total_return"): fmt_pct(nominal_summary["total_return"]),
                    t("inflation.metric_cagr"): fmt_pct(nominal_summary["cagr"]),
                    t("inflation.metric_final"): fmt_money(
                        float(nominal_covered.iloc[-1]), base_ccy
                    ),
                    t("inflation.metric_kind"): t("inflation.nominal"),
                },
                {
                    t("inflation.metric_total_return"): fmt_pct(real_summary["total_return"]),
                    t("inflation.metric_cagr"): fmt_pct(real_summary["cagr"]),
                    t("inflation.metric_final"): fmt_money(float(real_nav.iloc[-1]), base_ccy),
                    t("inflation.metric_kind"): t("inflation.real"),
                },
            ])
            st.dataframe(metric_frame, hide_index=True, width="stretch")
            st.caption(t(
                "inflation.coverage_caption",
                area=t(f"inflation.area_{inflation_result.area.lower()}"),
                source=inflation_result.dataset,
                first=(
                    inflation_result.first_date.strftime(FMT_DATA)
                    if inflation_result.first_date else t("nd")
                ),
                last=(
                    inflation_result.last_date.strftime(FMT_DATA)
                    if inflation_result.last_date else t("nd")
                ),
            ))
            if inflation_result.stale:
                st.caption(t("inflation.stale_caption"))
            if pac is not None and not real_invested.empty:
                invested_covered = res.invested.reindex(real_invested.index).dropna()
                st.caption(t(
                    "inflation.pac_caption",
                    nominal=fmt_money(float(invested_covered.iloc[-1]), base_ccy),
                    real=fmt_money(float(real_invested.iloc[-1]), base_ccy),
                ))

    if res.pic is not None:
        st.caption(t(
            "chart.pic_caption",
            totale=fmt_money(float(res.invested.iloc[-1]), base_ccy),
            valore_pic=fmt_money(float(res.pic.iloc[-1]), base_ccy),
            valore_pac=fmt_money(float(res.portfolio.iloc[-1]), base_ccy),
        ))

    if mostra_sintetiche and comparti_scelti:
        st.caption(t("chart.synthetic_caption"))

    st.markdown(t("chart.composition_header"))
    area = go.Figure()
    for i, col in enumerate(res.contributions.columns):
        nome = res.labels[col]
        area.add_trace(go.Scatter(
            x=res.contributions.index, y=res.contributions[col], name=nome,
            stackgroup="one", line=dict(width=0.5, color=PALETTE[i % len(PALETTE)]),
            hovertemplate="%{y:,.0f}<extra>" + nome + "</extra>",
        ))
    area.update_layout(
        height=300, hovermode="x unified", margin=dict(l=0, r=0, t=10, b=0),
        yaxis_title=t("chart.yaxis_value", ccy=base_ccy), xaxis=ASSE_TEMPO,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(area, width="stretch")

    # Effetto tangibile della scelta di ribilanciamento: senza, i pesi
    # derivano con i rendimenti; con, si può contare quante volte sono
    # stati riportati a quelli impostati.
    set_weights = " · ".join(f"{res.labels[h.symbol]} {h.weight * 100:.0f}%" for h in holdings)
    final_alloc = res.contributions.iloc[-1]
    final_total = final_alloc.sum()
    if rebalance is Rebalance.NONE:
        if final_total > 0:
            final_weights = " · ".join(
                f"{res.labels[symbol]} {value / final_total * 100:.0f}%"
                for symbol, value in final_alloc.items()
            )
            st.caption(t("chart.weights_set_final", pesi=set_weights, pesi_finali=final_weights))
    else:
        rb_dates = sorted(rebalance_dates(res.prices.index, rebalance))
        label_rebal = i18n.etichetta_ribilanciamento(LINGUA, rebalance).lower()
        if rb_dates:
            st.caption(
                t(
                    "chart.rebalance_caption_active",
                    tipo=label_rebal, n=len(rb_dates),
                    data=rb_dates[-1].strftime(FMT_DATA), pesi=set_weights,
                )
            )
        else:
            st.caption(t("chart.rebalance_caption_none_yet", tipo=label_rebal))

with tab_bil:
    fondi = [assicura_alloc(f) for f in st.session_state.selected]
    # Non chiamarla `pesi`: quel nome e' il modulo `comparatore.pesi` importato
    # in testa al file, usato dai callback (equalize_weights, rimuovi_fondo)
    # nella tabella di composizione. Sovrascriverlo qui come variabile locale
    # rebinderebbe il nome nel namespace globale dello script per il resto
    # del run, e i callback lo risolvono al momento del click (non alla
    # definizione), rompendoli con un AttributeError sul dict al posto del modulo.
    pesi_per_simbolo = {f["symbol"]: f["weight"] for f in fondi}

    # I grafici stanno sopra la tabella ma vanno calcolati dopo, altrimenti
    # mostrerebbero la classificazione precedente alla correzione appena fatta:
    # il contenitore si dichiara qui e si riempie in fondo.
    grafici = st.container()

    st.markdown(t("bilancio.header"))
    class_df = pd.DataFrame([
        {
            "fondo": f["name"],
            "simbolo": f["symbol"],
            "peso": f["weight"],
            "classe": f["alloc_manuale"].get("classe") or al.AUTOMATICA,
            "area": f["alloc_manuale"].get("area") or al.AUTOMATICA,
            "settore": f["alloc_manuale"].get("settore") or al.AUTOMATICA,
        }
        for f in fondi
    ])

    tendina_help = t("bilancio.tendina_help", automatica=al.AUTOMATICA)
    class_edited = st.data_editor(
        class_df,
        hide_index=True,
        width="stretch",
        disabled=["fondo", "simbolo", "peso"],
        column_config={
            "fondo": t("editor.col_fondo"),
            "simbolo": st.column_config.TextColumn(t("editor.col_simbolo"), width="small"),
            "peso": st.column_config.NumberColumn(
                t("editor.col_peso"), format="%.2f", width="small",
                help=t("bilancio.peso_help"),
            ),
            "classe": st.column_config.SelectboxColumn(
                t("bilancio.col_classe"), options=al.OPZIONI["classe"],
                format_func=lambda v: i18n.etichetta_termine(LINGUA, v), help=tendina_help,
            ),
            "area": st.column_config.SelectboxColumn(
                t("bilancio.col_area"), options=al.OPZIONI["area"],
                format_func=lambda v: i18n.etichetta_termine(LINGUA, v), help=tendina_help,
            ),
            "settore": st.column_config.SelectboxColumn(
                t("bilancio.col_settore"), options=al.OPZIONI["settore"],
                format_func=lambda v: i18n.etichetta_termine(LINGUA, v), help=tendina_help,
            ),
        },
        key="classificazione_" + "|".join(f["symbol"] for f in fondi),
    )

    # Stesso accorgimento della tabella di composizione: le modifiche si
    # riportano nello stato **per simbolo**, mai per posizione.
    per_simbolo = {f["symbol"]: f for f in fondi}
    for _, row in class_edited.iterrows():
        fondo = per_simbolo.get(row["simbolo"])
        if fondo is None:
            continue
        for dimensione in al.DIMENSIONI:
            scelta = row[dimensione]
            fondo["alloc_manuale"][dimensione] = (
                "" if scelta == al.AUTOMATICA else scelta
            )

    # Distribuzione effettiva: la scelta manuale prevale su quella dedotta.
    effettive = {
        dimensione: {
            f["symbol"]: al.risolvi(
                f["alloc"].get(dimensione), f["alloc_manuale"].get(dimensione, "")
            )
            for f in fondi
        }
        for dimensione in al.DIMENSIONI
    }
    # La valuta e' gia' nello stato: nessuna deduzione, nessuna correzione.
    valute = {
        f["symbol"]: {f["currency"] or al.NON_CLASSIFICATO: 1.0} for f in fondi
    }
    # Il paese e' fuori da `DIMENSIONI` (non e' correggibile a mano, vedi
    # `al.paesi_da_posizioni`), quindi niente `risolvi`: si legge cosi' com'e'.
    paesi = {f["symbol"]: f["alloc"].get("paese") or {} for f in fondi}

    with grafici:
        da_eodhd = sum(1 for f in fondi if f.get("alloc_fonte") == "eodhd")
        da_yahoo = sum(1 for f in fondi if f.get("alloc_fonte") == "yahoo")
        da_nome = len(fondi) - da_eodhd - da_yahoo
        corretti = sum(
            1 for f in fondi
            if any(f["alloc_manuale"].get(d) for d in al.DIMENSIONI)
        )
        provenienza = []
        if da_eodhd:
            provenienza.append(t("bilancio.provenienza_eodhd", n=da_eodhd))
        if da_yahoo:
            provenienza.append(t("bilancio.provenienza_yahoo", n=da_yahoo))
        if da_nome:
            provenienza.append(t("bilancio.provenienza_nome", n=da_nome))
        if corretti:
            provenienza.append(t("bilancio.provenienza_manuali", n=corretti))
        st.caption(t("bilancio.provenienza_prefix") + ", ".join(provenienza) + ".")

        ripartizioni = [
            ("classe", t("bilancio.titolo_classe"),
             al.aggrega(pesi_per_simbolo, effettive["classe"])),
            ("area", t("bilancio.titolo_area"),
             al.aggrega(pesi_per_simbolo, effettive["area"])),
            ("settore", t("bilancio.titolo_settore"),
             al.aggrega(pesi_per_simbolo, effettive["settore"])),
            ("valuta", t("bilancio.titolo_valuta"), al.aggrega(pesi_per_simbolo, valute)),
            ("paesi", t("bilancio.titolo_paesi"), al.aggrega(pesi_per_simbolo, paesi)),
        ]
        for riga in range(0, len(ripartizioni), 2):
            colonne = st.columns(2)
            for colonna, (id_dim, titolo, quote) in zip(colonne, ripartizioni[riga:riga + 2]):
                with colonna:
                    st.markdown(f"**{titolo}**")
                    # `key` esplicita ed indipendente dal contenuto: due
                    # ciambelle con la stessa distribuzione (frequente con
                    # pochi fondi, es. valuta e paese coincidenti)
                    # produrrebbero altrimenti figure Plotly identiche, e
                    # Streamlit assegna l'id in base al contenuto quando
                    # manca una key esplicita.
                    st.plotly_chart(ciambella(quote), width="stretch", key=f"ciambella_{id_dim}")

    with st.expander(t("bilancio.dettaglio_expander")):
        st.dataframe(
            pd.DataFrame([
                {
                    "strumento": f["name"],
                    "peso": f"{f['weight']:.2f}",
                    "classe": i18n.etichetta_termine(
                        LINGUA, al.descrivi(effettive["classe"][f["symbol"]])),
                    "area": i18n.etichetta_termine(
                        LINGUA, al.descrivi(effettive["area"][f["symbol"]])),
                    "settore": i18n.etichetta_termine(
                        LINGUA, al.descrivi(effettive["settore"][f["symbol"]])),
                    "valuta": f["currency"] or t("nd"),
                }
                for f in fondi
            ]),
            hide_index=True,
            width="stretch",
            column_config={
                "strumento": t("bilancio.col_strumento"),
                "peso": t("editor.col_peso"),
                "classe": t("bilancio.col_classe"),
                "area": t("bilancio.col_area"),
                "settore": t("bilancio.col_settore"),
                "valuta": t("bilancio.col_valuta"),
            },
        )

    with st.expander(t("bilancio.posizioni_expander")):
        st.caption(t("bilancio.posizioni_caption"))
        righe_posizioni = [
            {
                "fondo": f["name"],
                "titolo": h.get("name") or h.get("symbol") or "",
                "simbolo": h.get("symbol") or "",
                "peso_nel_fondo": f"{float(h.get('quota') or 0) * 100:.2f}%",
            }
            for f in fondi
            for h in (f.get("holdings") or [])
        ]
        if righe_posizioni:
            st.dataframe(
                pd.DataFrame(righe_posizioni), hide_index=True, width="stretch",
                column_config={
                    "fondo": t("editor.col_fondo"),
                    "titolo": t("bilancio.col_titolo"),
                    "simbolo": t("editor.col_simbolo"),
                    "peso_nel_fondo": t("bilancio.col_peso_nel_fondo"),
                },
            )
        else:
            st.caption(t("bilancio.posizioni_none"))

    # L'overlap e' una vista derivata: non modifica la classificazione manuale
    # ne' le serie usate dal backtest. Le quote restano quelle osservate dalla
    # fonte, quindi una coppia parziale viene mostrata come limite inferiore.
    overlap_report = overlap.analyze_overlap([
        {
            "fund_id": f["symbol"],
            "name": f.get("name", ""),
            "weight": f.get("weight", 0.0),
            "holdings": f.get("holdings") or [],
            "holdings_source": f.get("holdings_source", ""),
            "holdings_as_of": f.get("holdings_as_of"),
        }
        for f in fondi
    ])
    with st.expander(t("bilancio.overlap_expander"), expanded=True):
        st.caption(t("bilancio.overlap_caption"))
        coverage_rows = []
        for fund in overlap_report.funds:
            item = overlap_report.coverage[fund.fund_id]
            data = ""
            if item.as_of:
                data = item.as_of.strftime(FMT_DATA)
            elif item.source:
                data = t("bilancio.overlap_unknown_date")
            flags = []
            if item.stale:
                flags.append(t("bilancio.overlap_stale"))
            if item.ambiguous_count:
                flags.append(t("bilancio.overlap_ambiguous", n=item.ambiguous_count))
            if not item.valid:
                flags.append(t("bilancio.overlap_unavailable"))
            coverage_rows.append({
                "fondo": fund.name or fund.fund_id,
                "copertura": fmt_pct(item.coverage),
                "fonte": item.source or t("nd"),
                "data": data or t("nd"),
                "nota": "; ".join(flags) or t("bilancio.overlap_ok"),
            })
        st.dataframe(pd.DataFrame(coverage_rows), hide_index=True, width="stretch",
                     column_config={
                         "fondo": t("bilancio.overlap_fund"),
                         "copertura": t("bilancio.overlap_coverage"),
                         "fonte": t("bilancio.overlap_source"),
                         "data": t("bilancio.overlap_date"),
                         "nota": t("bilancio.overlap_note"),
                     })

        if overlap_report.pairwise:
            names = {fund.fund_id: fund.name or fund.fund_id for fund in overlap_report.funds}
            matrix = pd.DataFrame(index=[names[f.fund_id] for f in overlap_report.funds],
                                  columns=[names[f.fund_id] for f in overlap_report.funds])
            for fund in overlap_report.funds:
                matrix.loc[names[fund.fund_id], names[fund.fund_id]] = "—"
            for pair in overlap_report.pairwise:
                value = t("nd") if pair.overlap is None else fmt_pct(pair.overlap)
                matrix.loc[names[pair.fund_a], names[pair.fund_b]] = value
                matrix.loc[names[pair.fund_b], names[pair.fund_a]] = value
            st.markdown(t("bilancio.overlap_matrix_header"))
            st.dataframe(matrix, width="stretch")
            pair_rows = []
            for pair in sorted(overlap_report.pairwise,
                               key=lambda p: p.overlap if p.overlap is not None else -1,
                               reverse=True):
                pair_rows.append({
                    "coppia": f"{names[pair.fund_a]} · {names[pair.fund_b]}",
                    "overlap": t("nd") if pair.overlap is None else fmt_pct(pair.overlap),
                    "copertura": f"{fmt_pct(pair.coverage_a)} · {fmt_pct(pair.coverage_b)}",
                    "nota": (
                        t("bilancio.overlap_lower_bound") if pair.overlap is not None
                        else t("bilancio.overlap_unavailable")
                    ) + (f"; {t('bilancio.overlap_ambiguous', n=pair.ambiguous_count)}"
                         if pair.ambiguous_count else ""),
                })
            st.dataframe(pd.DataFrame(pair_rows), hide_index=True, width="stretch",
                         column_config={
                             "coppia": t("bilancio.overlap_pair"),
                             "overlap": t("bilancio.overlap_value"),
                             "copertura": t("bilancio.overlap_pair_coverage"),
                             "nota": t("bilancio.overlap_note"),
                         })

        st.markdown(t("bilancio.overlap_exposure_header"))
        exposure_rows = [
            {"partecipazione": key.rsplit("|", 1)[-1], "peso": fmt_pct(value)}
            for key, value in sorted(
                overlap_report.exposure.exposures.items(), key=lambda item: item[1], reverse=True
            )
        ]
        if exposure_rows:
            st.dataframe(pd.DataFrame(exposure_rows), hide_index=True, width="stretch",
                         column_config={
                             "partecipazione": t("bilancio.overlap_position"),
                             "peso": t("bilancio.overlap_portfolio_weight"),
                         })
        st.caption(t("bilancio.overlap_unknown", quota=fmt_pct(
            overlap_report.exposure.unknown_weight
        )))

    esclusi = [f["symbol"] for f in fondi if f["symbol"] not in prices.columns]
    if esclusi:
        chiave_esclusi = (
            "bilancio.esclusi_caption_one" if len(esclusi) == 1
            else "bilancio.esclusi_caption_many"
        )
        st.caption(t(chiave_esclusi, elenco=", ".join(esclusi)))

    st.caption(t("bilancio.disclaimer"))

with tab2:
    st.caption(t(
        "confronto.caption_pac" if pac is not None else "confronto.caption",
        capitale=fmt_money(initial_value, base_ccy),
    ))
    if benchmark_config:
        if benchmark_curve is None or benchmark_analysis is None:
            st.warning(
                t("benchmark.failed", errore=benchmark_error or t("nd")), icon="⚠️"
            )
        else:
            benchmark_metrics = benchmark_analysis["metrics"]
            st.markdown(t("benchmark.metrics_header"))
            metric_rows = [{
                t("benchmark.metric"): t("benchmark.portfolio_label"),
                t("benchmark.growth"): fmt_pct(benchmark_metrics.portfolio_total_return),
                t("benchmark.cagr"): fmt_pct(benchmark_metrics.portfolio_cagr),
                t("benchmark.volatility"): fmt_pct(benchmark_metrics.portfolio_volatility),
                t("benchmark.max_drawdown"): fmt_pct(benchmark_metrics.portfolio_max_drawdown),
                t("benchmark.active_return"): t("nd"),
                t("benchmark.tracking_error"): t("nd"),
                t("benchmark.information_ratio"): t("nd"),
            }, {
                t("benchmark.metric"): benchmark_config["name"],
                t("benchmark.growth"): fmt_pct(benchmark_metrics.benchmark_total_return),
                t("benchmark.cagr"): fmt_pct(benchmark_metrics.benchmark_cagr),
                t("benchmark.volatility"): fmt_pct(benchmark_metrics.benchmark_volatility),
                t("benchmark.max_drawdown"): fmt_pct(benchmark_metrics.benchmark_max_drawdown),
                t("benchmark.active_return"): fmt_pct(benchmark_metrics.active_return),
                t("benchmark.tracking_error"): fmt_pct(benchmark_metrics.tracking_error),
                t("benchmark.information_ratio"): (
                    t("nd") if pd.isna(benchmark_metrics.information_ratio)
                    else f"{benchmark_metrics.information_ratio:.2f}"
                ),
            }]
            st.dataframe(pd.DataFrame(metric_rows), hide_index=True, width="stretch")
            st.caption(t(
                "benchmark.common_period",
                start=benchmark_metrics.start.strftime(FMT_DATA),
                end=benchmark_metrics.end.strftime(FMT_DATA),
                n=benchmark_metrics.observations,
            ))
            if benchmark_metrics.reason:
                reason_key = {
                    "common_period_empty": "benchmark.reason_common_empty",
                    "insufficient_observations": "benchmark.reason_insufficient",
                    "tracking_error_zero": "benchmark.reason_tracking_error_zero",
                }.get(benchmark_metrics.reason, "benchmark.reason_generic")
                st.caption(t("benchmark.metric_reason", motivo=t(reason_key)))
            correlation = benchmark_analysis["correlation"]
            if not correlation.empty and not correlation.isna().all().all():
                st.markdown(t("benchmark.correlation_header"))
                st.dataframe(correlation.round(3), width="stretch")
            st.markdown(t("benchmark.rolling_header"))
            rolling_rows = []
            for years, values in benchmark_analysis["rolling"].items():
                summary = comparative.rolling_summary(values)
                rolling_rows.append({
                    t("benchmark.rolling_period"): t("benchmark.years", n=years),
                    t("benchmark.rolling_worst"): fmt_pct(summary["worst"]),
                    t("benchmark.rolling_median"): fmt_pct(summary["median"]),
                    t("benchmark.rolling_best"): fmt_pct(summary["best"]),
                    t("benchmark.rolling_positive"): fmt_pct(summary["positive_pct"]),
                    t("benchmark.rolling_observations"): summary["observations"],
                })
            for years, values in benchmark_analysis["rolling_benchmark"].items():
                summary = comparative.rolling_summary(values)
                rolling_rows.append({
                    t("benchmark.rolling_period"): (
                        f"{benchmark_config['name']} · "
                        f"{t('benchmark.years', n=years)}"
                    ),
                    t("benchmark.rolling_worst"): fmt_pct(summary["worst"]),
                    t("benchmark.rolling_median"): fmt_pct(summary["median"]),
                    t("benchmark.rolling_best"): fmt_pct(summary["best"]),
                    t("benchmark.rolling_positive"): fmt_pct(summary["positive_pct"]),
                    t("benchmark.rolling_observations"): summary["observations"],
                })
            if rolling_rows:
                st.dataframe(pd.DataFrame(rolling_rows), hide_index=True, width="stretch")
    if not portfolio_correlation.empty and not portfolio_correlation.isna().all().all():
        st.markdown(t("benchmark.correlation_portfolio_header"))
        st.dataframe(portfolio_correlation.round(3), width="stretch")
    if not benchmark_config and benchmark_analysis:
        st.markdown(t("benchmark.rolling_header"))
        rolling_rows = []
        for years, values in benchmark_analysis["rolling"].items():
            summary = comparative.rolling_summary(values)
            rolling_rows.append({
                t("benchmark.rolling_period"): t("benchmark.years", n=years),
                t("benchmark.rolling_worst"): fmt_pct(summary["worst"]),
                t("benchmark.rolling_median"): fmt_pct(summary["median"]),
                t("benchmark.rolling_best"): fmt_pct(summary["best"]),
                t("benchmark.rolling_positive"): fmt_pct(summary["positive_pct"]),
                t("benchmark.rolling_observations"): summary["observations"],
            })
        if rolling_rows:
            st.dataframe(pd.DataFrame(rolling_rows), hide_index=True, width="stretch")
    fig2 = go.Figure()
    for i, col in enumerate(res.per_fund.columns):
        nome = res.labels[col]
        color = PALETTE[i % len(PALETTE)]
        recon, real = split_at(res.per_fund[col], splice_dates.get(col))
        if recon is not None and len(recon) > 1:
            fig2.add_trace(go.Scatter(
                x=recon.index, y=recon.values, name=t("confronto.legend_reconstructed", col=nome),
                line=dict(color=color, width=1.5, dash="dot"), opacity=0.7,
                showlegend=False,
                hovertemplate=f"%{{x|{FMT_DATA}}}<br>%{{y:,.0f}}"
                              f"{t('chart.hover_reconstructed_suffix')}"
                              "<extra>" + nome + "</extra>",
            ))
        fig2.add_trace(go.Scatter(
            x=real.index, y=real.values, name=nome,
            line=dict(color=color, width=2),
            hovertemplate=f"%{{x|{FMT_DATA}}}<br>%{{y:,.0f}}<extra>" + nome + "</extra>",
        ))
        if show_gross:
            fig2.add_trace(go.Scatter(
                x=res.per_fund_gross.index, y=res.per_fund_gross[col],
                name=t("confronto.legend_gross", col=nome),
                line=dict(color=color, width=1, dash="dash"),
                opacity=0.45, showlegend=False, hoverinfo="skip",
            ))
    if benchmark_curve is not None:
        fig2.add_trace(go.Scatter(
            x=benchmark_curve.index, y=benchmark_curve.values,
            name=t("benchmark.legend", symbol=benchmark_config["symbol"]),
            line=dict(color="#7c3aed", width=2, dash="dashdot"),
            hovertemplate=f"%{{x|{FMT_DATA}}}<br>%{{y:,.0f}}<extra></extra>",
        ))
    fig2.update_layout(
        height=460, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title=t("chart.yaxis_value", ccy=base_ccy), xaxis=ASSE_TEMPO,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig2, width="stretch")

    # Ogni riga risponde a due domande diverse con la serie giusta: le
    # metriche di rischio/rendimento vengono dalla curva al netto dei
    # versamenti (`per_fund_nav`, `res.nav` per il portafoglio), il valore
    # finale dal saldo vero. Senza PAC le due serie sono lo stesso oggetto e
    # la tabella e' identica a prima; con il PAC, prenderle entrambe dalla
    # curva grezza metteva metriche gonfiate dai versamenti accanto a quelle
    # gia' depurate del portafoglio - righe non confrontabili fra loro.
    rows = {}
    for col in res.per_fund.columns:
        s = mt.summarize(res.per_fund_nav[col], risk_free)
        saldo_fondo = float(res.per_fund[col].iloc[-1])
        s["final_value"] = saldo_fondo
        if pac is not None:
            s["xirr"] = mt.xirr(res.cashflows, saldo_fondo, res.end)
        s["ter_cost"] = res.per_fund_gross[col].iloc[-1] - saldo_fondo
        s["reconstructed"] = t("si") if col in splice_dates else t("no")
        rows[res.labels[col]] = s
    riga_portafoglio = {
        **summary,
        "final_value": float(res.portfolio.iloc[-1]),
        "ter_cost": res.fee_drag,
        "reconstructed": t("si") if splice_dates else t("no"),
    }
    if pac is not None:
        riga_portafoglio["xirr"] = tasso_xirr
    rows[t("confronto.riga_portafoglio")] = riga_portafoglio

    # XIRR accanto al CAGR: sono la stessa domanda posta ai due denari
    # diversi (quello dello strumento e il tuo).
    colonne = [
        "final_value", "total_return", "cagr",
        *(["xirr"] if pac is not None else []),
        "sharpe", "sortino", "volatility", "max_drawdown", "calmar",
        "best_year", "worst_year", "ter_cost", "reconstructed",
    ]
    styled = pd.DataFrame(rows).T[colonne]
    styled["final_value"] = styled["final_value"].map(lambda v: fmt_money(v, base_ccy))
    styled["ter_cost"] = styled["ter_cost"].map(lambda v: fmt_money(v, base_ccy))
    for c in colonne:
        if c in ("total_return", "cagr", "xirr", "volatility", "max_drawdown",
                 "best_year", "worst_year"):
            styled[c] = styled[c].map(lambda v: fmt_pct(v))
        elif c in ("sharpe", "sortino", "calmar"):
            styled[c] = styled[c].map(lambda v: t("nd") if pd.isna(v) else f"{v:.2f}")
    styled.index.name = t("bilancio.col_strumento")

    capitale_confronto = fmt_money(initial_value, base_ccy)
    st.caption(t(
        "confronto.stesso_capitale_caption_pac" if pac is not None
        else "confronto.stesso_capitale_caption",
        capitale=capitale_confronto,
    ))
    st.dataframe(
        styled, width="stretch",
        column_config={
            "final_value": st.column_config.TextColumn(
                t(
                    "confronto.col_valore_finale_pac" if pac is not None
                    else "confronto.col_valore_finale",
                    capitale=capitale_confronto,
                ),
                help=mhelp["balance"] if pac is not None else mhelp["final_value"],
            ),
            **{
                nome: st.column_config.TextColumn(
                    i18n.etichetta_metrica(LINGUA, nome), help=mhelp[nome]
                )
                for nome in colonne if nome != "final_value"
            },
        },
    )
    if splice_dates:
        st.caption(t("confronto.footnote"))

with tab3:
    # Curve al netto dei versamenti (senza PAC sono le stesse di sempre): su
    # quella grezza un versamento risalirebbe il drawdown come se il mercato
    # fosse rimbalzato, e un anno di sole rate comparirebbe come un anno di
    # rendimento.
    dd_fig = go.Figure()
    dd = mt.drawdown_series(res.nav)
    dd_fig.add_trace(go.Scatter(
        x=dd.index, y=dd.values * 100, name=t("drawdown.legend_portafoglio"), fill="tozeroy",
        line=dict(color=PALETTE[0], width=1.5),
        hovertemplate=f"%{{x|{FMT_DATA}}}<br>%{{y:.2f}}%<extra></extra>",
    ))
    for i, col in enumerate(res.per_fund_nav.columns):
        nome = res.labels[col]
        d = mt.drawdown_series(res.per_fund_nav[col])
        dd_fig.add_trace(go.Scatter(
            x=d.index, y=d.values * 100, name=nome,
            line=dict(color=PALETTE[(i + 1) % len(PALETTE)], width=1), opacity=0.7,
            hovertemplate="%{y:.2f}%<extra>" + nome + "</extra>",
        ))
    if portfolio_splice is not None and portfolio_splice > res.start:
        dd_fig.add_vline(
            x=portfolio_splice, line=dict(color="#6b7280", width=1, dash="dot"),
            annotation_text=t("chart.annotation_real_start"), annotation_position="top left",
        )
    dd_fig.update_layout(
        height=420, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title=t("drawdown.yaxis"), xaxis=ASSE_TEMPO,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(dd_fig, width="stretch")
    if pac is not None:
        st.caption(t("drawdown.pac_caption"))

    st.markdown(t("drawdown.yearly_header"))
    yearly = pd.DataFrame({t("drawdown.legend_portafoglio"): mt.calendar_year_returns(res.nav)})
    for col in res.per_fund_nav.columns:
        yearly[res.labels[col]] = mt.calendar_year_returns(res.per_fund_nav[col])
    ybars = go.Figure()
    for i, col in enumerate(yearly.columns):
        ybars.add_trace(go.Bar(
            x=yearly.index.astype(str), y=yearly[col] * 100, name=col,
            marker_color=PALETTE[i % len(PALETTE)],
            hovertemplate="%{y:.2f}%<extra>" + col + "</extra>",
        ))
    ybars.update_layout(
        height=320, barmode="group", margin=dict(l=0, r=0, t=10, b=0),
        yaxis_title=t("drawdown.yaxis_yearly"), xaxis=ASSE_CATEGORIE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(ybars, width="stretch")

with tab4:
    out = pd.DataFrame({
        t("dati.col_netto"): res.portfolio,
        t("dati.col_lordo"): res.portfolio_gross,
    }).join(res.per_fund.rename(columns=res.labels).add_prefix(t("dati.col_solo_prefix")))
    st.dataframe(out.tail(500).iloc[::-1].round(2), width="stretch", height=420)
    st.download_button(
        t("dati.download_button"),
        out.to_csv().encode("utf-8"),
        file_name=f"backtest_{res.start.date()}_{res.end.date()}.csv",
        mime="text/csv",
    )

with tab5:
    anno_rif = covip.anno_riferimento()
    st.markdown(
        t("previdenza.header_con_anno", anno=anno_rif) if anno_rif
        else t("previdenza.header_senza_anno")
    )

    st.warning(t("previdenza.fiscalita_warning"), icon="⚖️")
    st.caption(t("previdenza.rendimenti_caption"))
    if pac is not None:
        # Il PAC tocca tre cose in questa scheda; senza dirlo, i numeri
        # cambierebbero rispetto a un run senza versamenti senza che nulla
        # spieghi perche'.
        st.caption(t("previdenza.pac_caption"))

    catalogo = covip.catalogo()
    if not catalogo:
        st.error(t("previdenza.catalogo_error"))
    else:
        f1, f2, f3 = st.columns([1.2, 1.2, 2.6])
        # "Tutte"/"negoziale"/"aperto"/"PIP" restano sempre in italiano: sono
        # le categorie regolamentari COVIP passate cosi' come sono a
        # `covip.cerca()`. Tradurre l'etichetta di un selectbox che non usa
        # `format_func` ne cambierebbe il valore stesso al cambio di lingua,
        # con lo stesso rischio di stato corrotto descritto per `rebalance`.
        tipo_sel = f1.selectbox(
            t("previdenza.forma_label"), ["Tutte", "negoziale", "aperto", "PIP"],
            key="tipo_previdenza",
            filter_mode=None,
        )
        categorie = ["Tutte"] + sorted({c.categoria for c in catalogo if c.categoria})
        cat_sel = f2.selectbox(
            t("previdenza.categoria_label"), categorie, key="categoria_previdenza",
            filter_mode=None,
        )
        testo = f3.text_input(
            t("previdenza.cerca_label"),
            placeholder=t("previdenza.cerca_placeholder"),
            key="testo_previdenza",
        )

        trovati = covip.cerca(
            testo,
            tipo=None if tipo_sel == "Tutte" else tipo_sel,
            categoria=None if cat_sel == "Tutte" else cat_sel,
        )
        st.caption(t("previdenza.risultati_caption", n=len(trovati)))

        # Le opzioni sono le chiavi stabili dei comparti, non le etichette: cosi'
        # il widget scrive direttamente in `comparti_previdenza` e il grafico del
        # portafoglio, che viene prima nello script, legge la scelta corrente.
        etichetta = {
            c.chiave: f"[{c.tipo}] {c.fondo} · {c.comparto}"
                      + (f" ({c.categoria})" if c.categoria else "")
            for c in catalogo
        }
        gia_scelti = list(st.session_state.get("comparti_previdenza", []))
        opzioni = [c.chiave for c in trovati]
        # I comparti gia' selezionati restano fra le opzioni anche quando i
        # filtri cambiano, altrimenti Streamlit li scarterebbe in silenzio.
        opzioni += [k for k in gia_scelti if k not in opzioni]

        st.multiselect(
            t("previdenza.comparti_label"),
            options=opzioni,
            format_func=lambda k: etichetta.get(k, k),
            key="comparti_previdenza",
        )

        if not comparti_scelti:
            st.info(t("previdenza.seleziona_hint"))
        else:
            finestre = {a: covip.finestra(a) for a in covip.ORIZZONTI}
            finestre = {a: w for a, w in finestre.items() if w}
            # NAV, non il valore grezzo: qui il portafoglio va confrontato
            # con rendimenti COVIP time-weighted, e senza questo la riga
            # "il tuo portafoglio" risulterebbe sistematicamente gonfiata da
            # ogni versamento del PAC letto come un guadagno di mercato -
            # proprio accanto a rendimenti ufficiali pubblicati.
            rend_port = hz.rendimenti_per_orizzonte(res.nav, finestre)

            righe = []
            for c in comparti_scelti:
                riga = {"strumento": f"{c.fondo} · {c.comparto}", "tipo": c.tipo,
                        "categoria": c.categoria}
                for anni in covip.ORIZZONTI:
                    valore = c.rendimenti.get(anni)
                    riga[f"{anni}a"] = t("nd") if valore is None else f"{valore:.2f}%"
                isc10 = c.isc.get(10)
                riga["isc_10a"] = t("nd") if isc10 is None else f"{isc10:.2f}%"
                righe.append(riga)

            riga_port = {"strumento": t("previdenza.riga_portafoglio"), "tipo": "—",
                         "categoria": "—"}
            for anni in covip.ORIZZONTI:
                valore = rend_port.get(anni)
                riga_port[f"{anni}a"] = t("nd") if valore is None else f"{valore * 100:.2f}%"
            riga_port["isc_10a"] = "—"
            righe.append(riga_port)

            st.markdown(t("previdenza.rendimento_header"))
            # Il periodo va nell'intestazione, non solo nel tooltip: senza,
            # "10 anni" e "5 anni" sembrano periodi cumulativi e un decennio
            # piu' basso del quinquennio sembra una contraddizione invece di
            # quello che e' - due finestre diverse, con la prima meta' del
            # decennio piu' fiacca.
            periodi_covip = covip.periodi()
            etichetta_orizzonte = {
                anni: (
                    t(
                        "previdenza.col_orizzonte",
                        etichetta=etichetta_anni(anni), periodo=periodi_covip[anni],
                    )
                    if periodi_covip.get(anni) else etichetta_anni(anni)
                )
                for anni in covip.ORIZZONTI
            }
            covip_column_config = {
                "strumento": t("bilancio.col_strumento"),
                "tipo": t("previdenza.col_tipo"),
                "categoria": t("previdenza.categoria_label"),
                **{
                    f"{anni}a": st.column_config.TextColumn(
                        etichetta_orizzonte[anni],
                        help=t(
                            "previdenza.col_help_orizzonte",
                            anni=anni, periodo=periodi_covip.get(anni, ""),
                        ),
                    )
                    for anni in covip.ORIZZONTI
                },
                "isc_10a": st.column_config.TextColumn(
                    t("previdenza.col_isc"), help=t("previdenza.col_help_isc"),
                ),
            }
            st.dataframe(
                pd.DataFrame(righe), hide_index=True, width="stretch",
                column_config=covip_column_config,
            )
            st.caption(t("previdenza.legenda_caption"))

            mancanti = [a for a in covip.ORIZZONTI if rend_port.get(a) is None]
            if mancanti:
                elenco_anni = ", ".join(etichetta_anni(a) for a in mancanti)
                dettaglio = ", ".join(f"{a}a = {periodi_covip.get(a)}" for a in mancanti)
                st.caption(t("previdenza.mancanti_caption",
                             elenco_anni=elenco_anni, dettaglio=dettaglio))
                # Una colonna di "n/d" senza altro non dice nulla: qui almeno
                # il numero c'e', con scritto perche' non e' confrontabile e
                # cosa fare per renderlo tale.
                st.info(
                    t(
                        "previdenza.portafoglio_periodo_proprio",
                        inizio=res.start.strftime(FMT_DATA),
                        fine=res.end.strftime(FMT_DATA),
                        anni=f"{years:.1f}",
                        rendimento=fmt_pct(summary["cagr"]),
                    ),
                    icon="📐",
                )
                # La finestra piu' ampia fra quelle pubblicate: coprirla
                # significa coprire anche tutte le altre, perche' finiscono
                # tutte lo stesso 31 dicembre.
                covip_inizio = min(w[0] for w in finestre.values())
                covip_fine = max(w[1] for w in finestre.values())
                if (st.session_state.start_date, st.session_state.end_date) != (
                    covip_inizio, covip_fine
                ):
                    st.button(
                        t(
                            "previdenza.allinea_button",
                            inizio=covip_inizio.strftime(FMT_DATA),
                            fine=covip_fine.strftime(FMT_DATA),
                        ),
                        key="allinea_covip",
                        on_click=allinea_periodo_covip,
                        args=(covip_inizio, covip_fine),
                    )
                    st.caption(t("previdenza.allinea_caption"))

            # --- grafico a barre ---
            bars = go.Figure()
            orizzonti_utili = [a for a in covip.ORIZZONTI if finestre.get(a)]
            for i, c in enumerate(comparti_scelti):
                bars.add_trace(go.Bar(
                    name=f"{c.comparto[:24]}",
                    x=[etichetta_anni(a) for a in orizzonti_utili],
                    y=[c.rendimenti.get(a) for a in orizzonti_utili],
                    marker_color=PALETTE[(i + 4) % len(PALETTE)],
                    hovertemplate="%{y:.2f}%<extra>" + c.comparto + "</extra>",
                ))
            bars.add_trace(go.Bar(
                name=t("previdenza.il_tuo_portafoglio"),
                x=[etichetta_anni(a) for a in orizzonti_utili],
                y=[None if rend_port.get(a) is None else rend_port[a] * 100
                   for a in orizzonti_utili],
                marker_color=PALETTE[0],
                hovertemplate="%{y:.2f}%<extra>" + t("previdenza.il_tuo_portafoglio") + "</extra>",
            ))
            bars.update_layout(
                height=360, barmode="group", margin=dict(l=0, r=0, t=30, b=0),
                yaxis_title=t("previdenza.yaxis_rendimento"), xaxis=ASSE_CATEGORIE,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            )
            st.plotly_chart(bars, width="stretch")

            # --- impatto dell'ISC ---
            st.markdown(t("previdenza.costi_header"))
            # Con il PAC attivo il capitale esposto all'ISC in 10 anni non e'
            # il capitale iniziale ma il totale versato in quell'orizzonte -
            # stesse rate, stessa frequenza del PAC configurato, per 10 anni.
            # A PAC spento resta `initial_value`: comportamento invariato.
            rata_isc = st.session_state.pac_amount if pac is not None else 0.0
            rate_annue_isc = PAC_RATE_ANNUE[pac.frequency] if pac is not None else 12
            capitale_isc_10a = initial_value + rata_isc * rate_annue_isc * 10
            costi = []
            for c in comparti_scelti:
                isc10 = c.isc.get(10)
                if isc10 is None:
                    continue
                # Le rate entrano una per una, non tutte il primo giorno:
                # quella del nono anno subisce un anno di costi, non dieci.
                eroso = hz.costo_cumulato(
                    isc10 / 100, 10, initial_value, rata_isc, rate_annue_isc
                )
                lordo = c.rendimenti.get(10)
                riga_costo = {
                    "comparto": f"{c.fondo} · {c.comparto}",
                    "isc_annuo": f"{isc10:.2f}%",
                    "rendimento_10a": t("nd") if lordo is None else f"{lordo:.2f}%",
                    "eroso": fmt_money(eroso, base_ccy),
                    "quota_rendimento": t("nd") if not lordo or lordo <= 0
                        else f"{isc10 / lordo * 100:.0f}%",
                }
                if pac is not None:
                    # Proiezione, non retrospettiva come le altre colonne: cosa
                    # accumuleresti in 10 anni versando il tuo PAC configurato
                    # al rendimento netto storico di questo comparto. E' l'uso
                    # concreto dell'annualita' di `hz.capitale_finale`.
                    if lordo is None:
                        riga_costo["montante_pac_10a"] = t("nd")
                    else:
                        montante = hz.capitale_finale(
                            (lordo - isc10) / 100, 10, initial_value,
                            rata_isc, rate_annue_isc,
                        )
                        riga_costo["montante_pac_10a"] = fmt_money(montante, base_ccy)
                costi.append(riga_costo)
            if costi:
                costi_column_config = {
                    "comparto": t("previdenza.col_comparto"),
                    "isc_annuo": t("previdenza.col_isc_annuo"),
                    "rendimento_10a": t("previdenza.col_rendimento_10a"),
                    "eroso": t(
                        "previdenza.col_eroso_pac" if pac is not None
                        else "previdenza.col_eroso",
                        capitale=fmt_money(capitale_isc_10a, base_ccy),
                    ),
                    "quota_rendimento": t("previdenza.col_quota_rendimento"),
                }
                if pac is not None:
                    costi_column_config["montante_pac_10a"] = t("previdenza.col_montante_pac_10a")
                st.dataframe(
                    pd.DataFrame(costi), hide_index=True, width="stretch",
                    column_config=costi_column_config,
                )
                st.caption(t("previdenza.costi_caption"))

            st.divider()
            st.checkbox(
                t("previdenza.curve_checkbox"),
                key="curve_sintetiche",
                help=t("previdenza.curve_help"),
            )
            if st.session_state.get("curve_sintetiche"):
                # Format_func volutamente senza la parola "anni"/"years": e'
                # invariante rispetto alla lingua (solo numero e periodo), a
                # differenza di `rebalance` non ha bisogno della protezione
                # via `_pending_state` per sopravvivere a un cambio di lingua.
                st.selectbox(
                    t("previdenza.orizzonte_label"),
                    covip.ORIZZONTI, index=3, key="orizzonte_curva",
                    format_func=lambda a: f"{a} ({covip.periodi().get(a, '')})",
                    filter_mode=None,
                )

    st.caption(t("previdenza.fonte_caption"))

st.divider()
st.caption(t("footer.disclaimer"))
