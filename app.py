"""Comparatore Fondi - backtester per fondi ed ETF su piu' fonti dati."""

from __future__ import annotations

import datetime as dt
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comparatore import allocazione as al
from comparatore import cache as disk_cache
from comparatore import covip
from comparatore import fx
from comparatore import horizons as hz
from comparatore import i18n
from comparatore import keys as api_keys_store
from comparatore import licenses
from comparatore import metrics as mt
from comparatore import pesi
from comparatore import portfolio_io
from comparatore import prefs
from comparatore import proxies as px
from comparatore.engine import (
    FeeMode,
    Frequency,
    Holding,
    Pac,
    Rebalance,
    coverage_warnings,
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


@st.cache_data(show_spinner=False, ttl=3600)
def cached_metadata(symbol: str, isin: str, eodhd: str) -> dict:
    reg = Registry(eodhd_key=eodhd)
    return vars(reg.metadata(symbol, isin))


def fmt_money(v: float, ccy: str) -> str:
    sep = i18n.separatore_migliaia(LINGUA)
    numero = f"{v:,.0f}"
    if sep != ",":
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


def add_fund(symbol: str, name: str, isin: str = ""):
    if any(f["symbol"] == symbol for f in st.session_state.selected):
        st.toast(t("toast.fund_exists", symbol=symbol), icon="⚠️")
        return
    meta = cached_metadata(symbol, isin, api_key("EODHD_API_KEY"))
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
    st.session_state.selected.append({
        "symbol": symbol,
        "name": fund_name,
        "currency": meta.get("currency") or "",
        "isin": (isin or meta.get("isin") or "").upper(),
        "weight": 0.0,
        "ter": (meta.get("ter") or 0.0) * 100,  # in percentuale per l'interfaccia
        "ter_auto": meta.get("ter") is not None,
        "extra": 0.0,
        "source": AUTO,
        "proxy": proxy.symbol if proxy else NO_PROXY,
        "alloc": alloc,  # {dimensione: {bucket: quota}}, dedotta + "paese" stimato
        "alloc_fonte": alloc_fonte,  # "eodhd" | "yahoo" | "nome"
        "alloc_manuale": {d: "" for d in al.DIMENSIONI},  # "" = usa la dedotta
        "holdings": holdings,  # prime posizioni: expander e stima del paese
    })
    # I fondi gia' presenti mantengono i loro rapporti reciproci: aggiungere
    # non deve piu' cancellare un'allocazione impostata a mano (era il
    # comportamento di `equalize_weights()`, chiamata qui in precedenza).
    for fondo, peso in zip(st.session_state.selected, pesi_ridistribuiti):
        fondo["weight"] = peso
    st.session_state.composizione_rev += 1
    st.toast(t("toast.fund_added", symbol=symbol), icon="✅")


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
    """Ricorda l'opt-in (o la sua revoca) fra un avvio e l'altro."""
    _salva_preferenze()


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
    st.subheader(t("costs.subheader"))
    st.caption(t("costs.caption"))
    show_gross = st.checkbox(
        t("costs.show_gross_checkbox"), key="show_gross"
    )

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
        try:
            import importlib.metadata as _ilm
            versione = _ilm.version("comparatore-fondi")
        except Exception:
            versione = "-"
        st.caption(t("about.version", versione=versione))
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
    disabled=["fondo", "simbolo", "valuta"],
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
for fondo, (_, row) in zip(st.session_state.selected, edited.iterrows()):
    fondo["ter"] = float(row["ter"])
    fondo["extra"] = float(row["extra"])
    fondo["isin"] = (row["isin"] or "").strip().upper()
    fondo["source"] = row["source"]
    fondo["proxy"] = row["proxy"]

pesi_originali = editor_df["peso"].tolist()
pesi_modificati = edited["peso"].tolist()
importi_originali = editor_df["importo"].tolist()
importi_modificati = edited["importo"].tolist()

_TOLLERANZA = 0.005
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
               if f["ter"] == 0 and not f["ter_auto"]]
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
    if f["symbol"] in prices.columns
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
except ValueError as exc:
    st.error(str(exc))
    st.stop()

st.divider()
st.subheader(
    t("results.subheader", inizio=res.start.strftime(FMT_DATA), fine=res.end.strftime(FMT_DATA))
)

# Etichetta -> data di innesto, per tratteggiare i grafici per fondo.
label_splice = {
    h.label: splice_dates[h.symbol]
    for h in holdings
    if h.symbol in splice_dates
}
portfolio_splice = max(label_splice.values()) if label_splice else None

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
                      annotation_text=t("chart.annotation_initial_capital"), annotation_position="bottom right")
    fig.update_layout(
        height=460, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title=t("chart.yaxis_value", ccy=base_ccy), xaxis_title=None,
        xaxis=ASSE_TEMPO,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig, width="stretch")

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
        area.add_trace(go.Scatter(
            x=res.contributions.index, y=res.contributions[col], name=col,
            stackgroup="one", line=dict(width=0.5, color=PALETTE[i % len(PALETTE)]),
            hovertemplate="%{y:,.0f}<extra>" + col + "</extra>",
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
    set_weights = " · ".join(f"{h.label} {h.weight * 100:.0f}%" for h in holdings)
    final_alloc = res.contributions.iloc[-1]
    final_total = final_alloc.sum()
    if rebalance is Rebalance.NONE:
        if final_total > 0:
            final_weights = " · ".join(
                f"{label} {value / final_total * 100:.0f}%"
                for label, value in final_alloc.items()
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
            ("classe", t("bilancio.titolo_classe"), al.aggrega(pesi_per_simbolo, effettive["classe"])),
            ("area", t("bilancio.titolo_area"), al.aggrega(pesi_per_simbolo, effettive["area"])),
            ("settore", t("bilancio.titolo_settore"), al.aggrega(pesi_per_simbolo, effettive["settore"])),
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
                    "classe": i18n.etichetta_termine(LINGUA, al.descrivi(effettive["classe"][f["symbol"]])),
                    "area": i18n.etichetta_termine(LINGUA, al.descrivi(effettive["area"][f["symbol"]])),
                    "settore": i18n.etichetta_termine(LINGUA, al.descrivi(effettive["settore"][f["symbol"]])),
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
    fig2 = go.Figure()
    for i, col in enumerate(res.per_fund.columns):
        color = PALETTE[i % len(PALETTE)]
        recon, real = split_at(res.per_fund[col], label_splice.get(col))
        if recon is not None and len(recon) > 1:
            fig2.add_trace(go.Scatter(
                x=recon.index, y=recon.values, name=t("confronto.legend_reconstructed", col=col),
                line=dict(color=color, width=1.5, dash="dot"), opacity=0.7,
                showlegend=False,
                hovertemplate=f"%{{x|{FMT_DATA}}}<br>%{{y:,.0f}}"
                              f"{t('chart.hover_reconstructed_suffix')}"
                              "<extra>" + col + "</extra>",
            ))
        fig2.add_trace(go.Scatter(
            x=real.index, y=real.values, name=col,
            line=dict(color=color, width=2),
            hovertemplate=f"%{{x|{FMT_DATA}}}<br>%{{y:,.0f}}<extra>" + col + "</extra>",
        ))
        if show_gross:
            fig2.add_trace(go.Scatter(
                x=res.per_fund_gross.index, y=res.per_fund_gross[col],
                name=t("confronto.legend_gross", col=col),
                line=dict(color=color, width=1, dash="dash"),
                opacity=0.45, showlegend=False, hoverinfo="skip",
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
        s["reconstructed"] = t("si") if col in label_splice else t("no")
        rows[col] = s
    riga_portafoglio = {
        **summary,
        "final_value": float(res.portfolio.iloc[-1]),
        "ter_cost": res.fee_drag,
        "reconstructed": t("si") if label_splice else t("no"),
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
    if label_splice:
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
        d = mt.drawdown_series(res.per_fund_nav[col])
        dd_fig.add_trace(go.Scatter(
            x=d.index, y=d.values * 100, name=col,
            line=dict(color=PALETTE[(i + 1) % len(PALETTE)], width=1), opacity=0.7,
            hovertemplate="%{y:.2f}%<extra>" + col + "</extra>",
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
        yearly[col] = mt.calendar_year_returns(res.per_fund_nav[col])
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
    }).join(res.per_fund.add_prefix(t("dati.col_solo_prefix")))
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
                st.caption(t("previdenza.mancanti_caption", elenco_anni=elenco_anni, dettaglio=dettaglio))
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
