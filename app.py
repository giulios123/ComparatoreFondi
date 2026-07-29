"""Comparatore Fondi - backtester per fondi ed ETF su piu' fonti dati."""

from __future__ import annotations

import datetime as dt
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comparatore import cache as disk_cache
from comparatore import covip
from comparatore import fx
from comparatore import horizons as hz
from comparatore import keys as api_keys_store
from comparatore import metrics as mt
from comparatore import proxies as px
from comparatore.engine import (
    FeeMode,
    Holding,
    Rebalance,
    coverage_warnings,
    rebalance_dates,
    run_backtest,
)
from comparatore.sources import AUTO, CsvParseError, Registry, is_isin, parse_csv

st.set_page_config(page_title="Comparatore Fondi", page_icon="📈", layout="wide")

CURRENCIES = ["EUR", "USD", "GBP", "CHF", "JPY"]
SYMBOLS = {"EUR": "€", "USD": "$", "GBP": "£", "CHF": "CHF ", "JPY": "¥"}

REBALANCE_LABELS = {
    "Nessuno (buy & hold)": Rebalance.NONE,
    "Mensile": Rebalance.MONTHLY,
    "Trimestrale": Rebalance.QUARTERLY,
    "Annuale": Rebalance.YEARLY,
}

REBALANCE_HELP = (
    "Riporta periodicamente i pesi a quelli impostati, vendendo ciò che è "
    "cresciuto di più per ricomprare ciò che è rimasto indietro.\n\n"
    "- **Nessuno (buy & hold)**: si compra una volta sola e non si tocca più "
    "nulla. I pesi derivano: il fondo che rende di più finisce per pesare "
    "sempre di più, e il portafoglio diventa via via più concentrato.\n"
    "- **Mensile / Trimestrale / Annuale**: al primo giorno di borsa di ogni "
    "periodo i pesi tornano ai valori impostati.\n\n"
    "Il backtest non applica commissioni di negoziazione né tassazione sulle "
    "plusvalenze realizzate: ribilanciare spesso risulta quindi più "
    "conveniente di quanto sarebbe nella realtà."
)

# Etichetta mostrata nella tabella -> nome interno della fonte.
SOURCE_LABELS = {
    "Automatica": AUTO,
    "Yahoo Finance": "yahoo",
    "justETF": "justetf",
    "EODHD": "eodhd",
    "Twelve Data": "twelvedata",
    "CSV caricato": "csv",
}
SOURCE_BY_NAME = {v: k for k, v in SOURCE_LABELS.items()}

NO_PROXY = "(nessuno)"
PROXY_OPTIONS = [NO_PROXY] + list(px.CATALOG)

PALETTE = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed",
           "#0891b2", "#db2777", "#65a30d", "#4b5563", "#ea580c"]

MIN_DATE = dt.date(1970, 1, 1)
DEFAULT_YEARS = 20


# --------------------------------------------------------------------------
# Stato e accesso ai dati
# --------------------------------------------------------------------------

if "selected" not in st.session_state:
    st.session_state.selected = []  # dizionari: symbol, name, isin, weight, ...
if "csv_series" not in st.session_state:
    st.session_state.csv_series = {}  # chiave -> (serie, valuta)
# Le date vivono nello stato perche' i pulsanti rapidi le riscrivono. I widget
# le leggono solo tramite `key`: passare anche `value` farebbe litigare
# Streamlit fra valore predefinito e stato.
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
    st.session_state.enable_justetf = False


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
    return f"{SYMBOLS.get(ccy, '')}{v:,.0f}".replace(",", ".")


def fmt_pct(v: float, decimals: int = 2) -> str:
    return "n/d" if pd.isna(v) else f"{v * 100:.{decimals}f}%"


def metric_help(risk_free: float, initial_value: float, ccy: str) -> dict[str, str]:
    """Spiegazione di ogni metrica, riusata da tooltip e legenda.

    E' una funzione e non una costante perche' i testi citano i valori
    correnti (il risk-free impostato, il capitale iniziale): un glossario
    che dice "il risk-free impostato è il 2,0%" insegna più di uno generico.
    """
    capitale = fmt_money(initial_value, ccy)
    rf_pct = fmt_pct(risk_free)
    return {
        "Valore finale": (
            f"Quanto sarebbero diventati i {capitale} iniziali a fine periodo, "
            "al netto del TER."
        ),
        "Rendimento totale": (
            "Variazione complessiva sull'intero periodo, **non** annualizzata."
        ),
        "CAGR": (
            "Rendimento medio annuo composto: il tasso costante che, applicato "
            "ogni anno, porta dal valore iniziale a quello finale nello stesso "
            "tempo impiegato realmente."
        ),
        "Volatilita": (
            "Oscillazione annualizzata dei rendimenti giornalieri (deviazione "
            "standard × √252). Dice quanto si è mosso il percorso, non quanto "
            "si è guadagnato: due curve con lo stesso CAGR possono avere "
            "volatilità molto diverse."
        ),
        "Sharpe": (
            f"Rendimento in eccesso sul tasso risk-free (oggi impostato al "
            f"{rf_pct}) per unità di volatilità sopportata. Sopra 1 è "
            "generalmente considerato un buon risultato."
        ),
        "Sortino": (
            f"Come lo Sharpe (risk-free al {rf_pct}), ma al denominatore conta "
            "solo l'oscillazione al ribasso: non penalizza i rialzi bruschi, "
            "solo le discese."
        ),
        "Max drawdown": (
            "La peggior discesa dal massimo storico precedente al minimo "
            "successivo: la perdita più profonda che si sarebbe dovuta "
            "sopportare restando investiti."
        ),
        "Calmar": (
            "CAGR diviso il max drawdown in valore assoluto: rendimento "
            "ottenuto per unità di perdita massima subita."
        ),
        "Miglior anno": "Il miglior rendimento su anno solare nel periodo.",
        "Peggior anno": "Il peggior rendimento su anno solare nel periodo.",
        "Costo TER": (
            f"Differenza, in {ccy}, a fine periodo fra il montante senza "
            "commissioni (curva lorda) e quello realmente ottenuto (curva "
            "netta)."
        ),
        "Ricostruito": (
            "La riga include un tratto stimato con uno strumento proxy, non "
            "dati reali del fondo: le sue metriche vanno lette come "
            "indicative."
        ),
    }


def add_fund(symbol: str, name: str, isin: str = ""):
    if any(f["symbol"] == symbol for f in st.session_state.selected):
        st.toast(f"{symbol} è già nel portafoglio", icon="⚠️")
        return
    meta = cached_metadata(symbol, isin, api_key("EODHD_API_KEY"))
    fund_name = meta.get("name") or name
    proxy = px.suggest_proxy(fund_name, symbol)
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
    })
    equalize_weights()
    st.toast(f"Aggiunto {symbol}", icon="✅")


def equalize_weights():
    n = len(st.session_state.selected)
    if n:
        for f in st.session_state.selected:
            f["weight"] = round(100 / n, 2)


def set_period(years: int | None):
    """Imposta il periodo dai pulsanti rapidi."""
    today = dt.date.today()
    st.session_state.start_date = (
        MIN_DATE if years is None else today - dt.timedelta(days=365 * years)
    )
    st.session_state.end_date = today


# --------------------------------------------------------------------------
# Barra laterale
# --------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Parametri")

    today = dt.date.today()
    st.caption("Periodo")
    preset_cols = st.columns(5)
    for col, (label, years) in zip(
        preset_cols, [("1a", 1), ("5a", 5), ("10a", 10), ("20a", 20), ("Max", None)]
    ):
        col.button(
            label,
            key=f"preset_{label}",
            on_click=set_period,
            args=(years,),
            width="stretch",
        )

    col_a, col_b = st.columns(2)
    start_date = col_a.date_input(
        "Data inizio", min_value=MIN_DATE, max_value=today,
        format="DD/MM/YYYY", key="start_date",
    )
    end_date = col_b.date_input(
        "Data fine", min_value=MIN_DATE, max_value=today,
        format="DD/MM/YYYY", key="end_date",
    )

    initial_value = st.number_input(
        "Valore iniziale del portafoglio", min_value=100.0, value=10_000.0,
        step=1_000.0, format="%.0f", key="initial_value",
    )
    base_ccy = st.selectbox(
        "Valuta di riferimento", CURRENCIES, index=0, key="base_ccy"
    )
    rebalance = REBALANCE_LABELS[
        st.selectbox(
            "Ribilanciamento", list(REBALANCE_LABELS), index=0, key="rebalance",
            help=REBALANCE_HELP,
        )
    ]
    st.caption(
        "I pesi impostati sono un punto di partenza: senza ribilanciamento "
        "derivano nel tempo con i rendimenti relativi dei fondi."
        if rebalance is Rebalance.NONE else
        "I pesi tornano a quelli impostati al primo giorno di borsa di ogni "
        "periodo (nessun costo di negoziazione applicato)."
    )

    st.divider()
    st.subheader("Costi")
    st.caption(
        "I NAV pubblicati sono **già al netto del TER**. "
        "La curva *lorda* ricostruisce il fondo senza commissioni: "
        "la distanza fra le due curve è il costo del TER."
    )
    show_gross = st.checkbox(
        "Mostra anche la curva lorda (senza TER)", value=True, key="show_gross"
    )

    st.divider()
    st.subheader("Storico esteso")
    extend_history = st.checkbox(
        "Ricostruisci il periodo precedente alla nascita del fondo",
        key="extend_history",
        help="Prolunga all'indietro la serie usando un indice o un fondo più "
             "anziano. È una ricostruzione, non un dato reale: nei grafici "
             "compare tratteggiata.",
    )
    if extend_history:
        st.caption(
            f"⚠️ I proxy sono quotati in dollari. Con valuta di riferimento "
            f"diversa da USD la ricostruzione non può scendere sotto il "
            f"**{fx.ECB_START.year}**, prima data dei cambi ufficiali BCE."
            if base_ccy != "USD" else
            "Valuta USD: la ricostruzione può usare tutta la profondità del proxy."
        )

    st.divider()
    st.subheader("Fonti dati")

    st.info(
        "**Cosa comporta abilitare justETF**\n\n"
        "justETF non offre un'API pubblica documentata per questa funzione. "
        "Se attivi l'integrazione, per gli ETF identificati da ISIN l'app la "
        "proverà automaticamente **prima di Yahoo** e invierà dal computer o "
        "server che esegue l'app:\n\n"
        "- ISIN dell'ETF, intervallo di date e valuta richiesta;\n"
        "- indirizzo IP e normali dati tecnici della connessione HTTP.\n\n"
        "Non vengono inviati capitale, pesi del portafoglio, file CSV o chiavi "
        "API. Le serie ricevute vengono conservate nella cache locale. "
        "L'endpoint può cambiare o smettere di funzionare e il suo utilizzo "
        "resta soggetto alle [condizioni justETF]"
        "(https://www.justetf.com/it/about/legal-terms.html) e ai diritti dei "
        "fornitori dei dati. Il consenso vale per questa sessione; lasciando "
        "la casella spenta, justETF verrà contattato solo se lo scegli "
        "esplicitamente come fonte di un singolo fondo."
    )
    st.checkbox(
        "Acconsento alle richieste automatiche a justETF",
        key="enable_justetf",
        help="Aggiunge justETF prima di Yahoo nell'ordine automatico per gli "
             "ETF con ISIN. Puoi revocare il consenso deselezionando la casella.",
    )

    with st.expander("🔑 Chiavi API (EODHD, Twelve Data)"):
        st.caption(
            "Restano solo su questo computer, in `.streamlit/api_keys.json` "
            "(permessi riservati al tuo utente, già escluso dal repository). "
            "Sopravvivono al riavvio e a **Svuota cache**, qui sotto."
        )
        with st.form("api_keys_form"):
            eodhd_input = st.text_input(
                "Chiave EODHD", value=st.session_state.api_keys.get("EODHD_API_KEY", ""),
                type="password", key="eodhd_key_input",
            )
            td_input = st.text_input(
                "Chiave Twelve Data",
                value=st.session_state.api_keys.get("TWELVEDATA_API_KEY", ""),
                type="password", key="td_key_input",
            )
            if st.form_submit_button("Salva", width="stretch"):
                st.session_state.api_keys = {
                    "EODHD_API_KEY": eodhd_input.strip(),
                    "TWELVEDATA_API_KEY": td_input.strip(),
                }
                api_keys_store.save(st.session_state.api_keys)
                st.toast("Chiavi salvate", icon="🔑")
                st.rerun()
        if any((v or "").strip() for v in st.session_state.api_keys.values()):
            if st.button("Dimentica le chiavi salvate", width="stretch"):
                st.session_state.api_keys = {}
                api_keys_store.clear()
                disk_cache.clear_prefixes(("eodhd", "twelvedata"))
                st.cache_data.clear()
                st.toast("Chiavi e relative cache rimosse", icon="🗑️")
                st.rerun()

    reg_probe = build_registry()
    for source in reg_probe.all_sources:
        justetf_disabled = source is reg_probe.justetf and not reg_probe.enable_justetf
        ready = source.available() and not justetf_disabled
        st.caption(f"{'🟢' if ready else '⚪'} {source.label}"
                   + ("" if ready else (
                       " — opt-in disattivato" if justetf_disabled
                       else " — non configurata"
                   )))
    st.caption(
        "Ordine automatico: CSV → Yahoo → EODHD → Twelve Data; justETF entra "
        "solo con l'opt-in qui sopra. Si può sempre forzare una fonte per "
        "singolo fondo dalla tabella. Le cache EODHD e Twelve Data scadono "
        f"dopo {disk_cache.restricted_retention_days()} giorni."
    )
    if not reg_probe.eodhd.available():
        st.info(
            "Per i **fondi collocati in Italia** (Mediolanum, Fineco, banche) "
            "conviene configurare EODHD: Yahoo ne copre solo una parte e con "
            "storico dal 2018. Inserisci la chiave qui sopra, in "
            "**🔑 Chiavi API**.",
            icon="🇮🇹",
        )

    with st.expander("📄 Carica una serie da CSV"):
        st.caption(
            "Per i fondi che nessuna fonte copre. Due colonne: data e valore "
            "della quota. Separatore, decimale e formato data riconosciuti "
            "da soli."
        )
        csv_key = st.text_input(
            "Simbolo o ISIN a cui associarla", key="csv_key",
            placeholder="es. IT0001234567",
        )
        csv_ccy = st.selectbox("Valuta della serie", CURRENCIES, key="csv_ccy")
        uploaded = st.file_uploader("File CSV", type=["csv", "txt"])
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
                    f"{len(series)} osservazioni dal {series.index[0].date()} "
                    f"al {series.index[-1].date()}."
                )
        if st.session_state.csv_series:
            st.caption("Caricate: " + ", ".join(st.session_state.csv_series))
            if st.button("Rimuovi le serie caricate", width="stretch"):
                st.session_state.csv_series = {}
                st.rerun()

    st.divider()
    n_cached, mb_cached = disk_cache.stats()
    st.caption(f"💾 Cache su disco: {n_cached} serie, {mb_cached:.1f} MB")
    if st.button("Svuota cache", width="stretch"):
        disk_cache.clear()
        st.cache_data.clear()
        st.toast("Cache svuotata", icon="🧹")
        st.rerun()

    st.divider()
    risk_free = st.number_input(
        "Tasso risk-free annuo (per Sharpe)", min_value=0.0, max_value=0.20,
        value=0.02, step=0.005, format="%.3f",
    )

# --------------------------------------------------------------------------
# Intestazione e ricerca
# --------------------------------------------------------------------------

st.title("📈 Comparatore Fondi")
st.caption("Backtest di fondi ed ETF su più fonti dati, con impatto del TER.")

with st.expander("🔎 Cerca fondi ed ETF", expanded=not st.session_state.selected):
    c1, c2 = st.columns([4, 1])
    query = c1.text_input(
        "Nome, ticker o ISIN",
        placeholder="es. 'Vanguard S&P 500', 'VUSA.AS' oppure 'IE00B3XXRP09'",
        label_visibility="collapsed",
    )
    funds_only = c2.toggle("Solo fondi/ETF", value=True)

    if query:
        with st.spinner("Ricerca in corso…"):
            results = cached_search(
                query, funds_only, api_key("EODHD_API_KEY"),
                api_key("TWELVEDATA_API_KEY"),
            )
        if not results:
            st.info("Nessun risultato. Prova con l'ISIN o con il ticker completo.")
        elif is_isin(query):
            st.caption(
                "🔗 L'ISIN permette di usare justETF solo se hai attivato "
                "l'opt-in nelle Fonti dati o scegli la fonte sul singolo fondo."
            )
        for r in results:
            cols = st.columns([5, 1.4, 1.4, 1])
            cols[0].markdown(f"**{r['name']}**  \n`{r['symbol']}`")
            cols[1].markdown(f"<small>{r['quote_type']}</small>", unsafe_allow_html=True)
            cols[2].markdown(f"<small>{r['exchange']}</small>", unsafe_allow_html=True)
            cols[3].button(
                "Aggiungi", key=f"add_{r['symbol']}",
                on_click=add_fund,
                args=(r["symbol"], r["name"], r.get("isin", "")),
                width="stretch",
            )

# --------------------------------------------------------------------------
# Composizione del portafoglio
# --------------------------------------------------------------------------

st.subheader("Composizione del portafoglio")

if not st.session_state.selected:
    st.info("Cerca e aggiungi almeno un fondo per iniziare.")
    st.stop()

editor_df = pd.DataFrame([
    {
        "Fondo": f["name"],
        "Simbolo": f["symbol"],
        "ISIN": f.get("isin", ""),
        "Valuta": f["currency"],
        "Peso %": f["weight"],
        "TER %": f["ter"],
        "Costi extra %": f["extra"],
        "Fonte": SOURCE_BY_NAME.get(f.get("source", AUTO), "Automatica"),
        "Proxy storico": f.get("proxy", NO_PROXY),
    }
    for f in st.session_state.selected
])

edited = st.data_editor(
    editor_df,
    hide_index=True,
    width="stretch",
    # Solo cancellazione: le righe si aggiungono dalla ricerca, dove il fondo
    # viene risolto davvero. "dynamic" permetterebbe righe vuote inservibili.
    num_rows="delete",
    disabled=["Fondo", "Simbolo", "Valuta"],
    column_config={
        "ISIN": st.column_config.TextColumn(
            "ISIN", width="small",
              help="Serve per usare justETF quando la fonte è abilitata o "
                  "selezionata esplicitamente sul fondo.",
        ),
        "Peso %": st.column_config.NumberColumn(
            "Peso %", min_value=0.0, max_value=100.0, step=1.0, format="%.2f",
            help="Quota del portafoglio assegnata al fondo.",
        ),
        "TER %": st.column_config.NumberColumn(
            "TER %", min_value=0.0, max_value=10.0, step=0.01, format="%.3f",
            help="Spesa corrente annua. Precompilato quando la fonte lo espone: "
                 "verifica sempre sul KID del fondo.",
        ),
        "Costi extra %": st.column_config.NumberColumn(
            "Costi extra %", min_value=0.0, max_value=10.0, step=0.05, format="%.3f",
            help="Costi annui NON già inclusi nel NAV (custodia, consulenza). "
                 "Vengono sottratti dalla performance.",
        ),
        "Fonte": st.column_config.SelectboxColumn(
            "Fonte", options=list(SOURCE_LABELS), width="small",
            help="'Automatica' prova le fonti in ordine di priorità.",
        ),
        "Proxy storico": st.column_config.SelectboxColumn(
            "Proxy storico", options=PROXY_OPTIONS, width="small",
            help="Strumento più anziano con cui ricostruire il periodo "
                 "precedente alla nascita del fondo.",
        ),
    },
    # La chiave dipende dai simboli: sostituendo un fondo con un altro a parita'
    # di righe, Streamlit riapplicherebbe le modifiche della riga vecchia a
    # quella nuova.
    key="composition_" + "|".join(f["symbol"] for f in st.session_state.selected),
)

# Le modifiche si riportano nello stato **per simbolo**, non per posizione:
# cancellando una riga Streamlit conserva le etichette originali dell'indice
# lasciando dei buchi (0, 2, 3), e un ciclo posizionale scriverebbe sul fondo
# sbagliato o solleverebbe IndexError.
by_symbol = {f["symbol"]: f for f in st.session_state.selected}
survivors = []
for _, row in edited.iterrows():
    fund = by_symbol.get(row["Simbolo"])
    if fund is None:
        continue
    fund["weight"] = float(row["Peso %"])
    fund["ter"] = float(row["TER %"])
    fund["extra"] = float(row["Costi extra %"])
    fund["isin"] = (row["ISIN"] or "").strip().upper()
    fund["source"] = SOURCE_LABELS.get(row["Fonte"], AUTO)
    fund["proxy"] = row["Proxy storico"]
    survivors.append(fund)

if len(survivors) != len(st.session_state.selected):
    kept = {f["symbol"] for f in survivors}
    removed = [f["symbol"] for f in st.session_state.selected if f["symbol"] not in kept]
    st.session_state.selected = survivors
    st.toast(f"Rimosso {', '.join(removed)}", icon="🗑️")
    st.rerun()

total_weight = sum(f["weight"] for f in st.session_state.selected)

b1, b2, b3, b4 = st.columns([1, 1, 1, 3])
b1.button("⚖️ Pesi uguali", on_click=equalize_weights, width="stretch")
if b2.button("🗑️ Svuota", width="stretch"):
    st.session_state.selected = []
    st.rerun()
b3.metric("Totale pesi", f"{total_weight:.1f}%")

missing_ter = [f["symbol"] for f in st.session_state.selected
               if f["ter"] == 0 and not f["ter_auto"]]
if missing_ter:
    b4.warning(
        f"TER non trovato per: {', '.join(missing_ter)}. "
        "Inseriscilo a mano dal KID per vedere l'impatto dei costi.",
        icon="ℹ️",
    )

if total_weight <= 0:
    st.error("Assegna almeno un peso maggiore di zero.")
    st.stop()
if abs(total_weight - 100) > 0.5:
    st.warning(
        f"I pesi sommano a {total_weight:.1f}%: verranno normalizzati a 100%.", icon="⚠️"
    )
if start_date >= end_date:
    st.error("La data di inizio deve precedere la data di fine.")
    st.stop()

# --------------------------------------------------------------------------
# Recupero dei prezzi
# --------------------------------------------------------------------------

registry = build_registry()
specs = [
    {"symbol": f["symbol"], "isin": f.get("isin", ""), "source": f.get("source", AUTO)}
    for f in st.session_state.selected
]

with st.spinner("Scarico le serie storiche…"):
    frame = registry.resolve_many(specs, start_date, end_date, base_ccy)

if frame.prices.empty:
    st.error("Nessun dato di prezzo disponibile per i fondi selezionati.")
    for symbol, res in frame.resolutions.items():
        st.caption(
            f"**{symbol}** — " + ", ".join(f"{a.source}: {a.outcome}" for a in res.attempts)
        )
    st.stop()

if frame.missing:
    with st.expander(f"🚫 {len(frame.missing)} fondi senza dati", expanded=True):
        for symbol in frame.missing:
            attempts = frame.resolutions[symbol].attempts
            st.markdown(
                f"**{symbol}** — " + ", ".join(f"`{a.source}` {a.outcome}" for a in attempts)
            )
        st.caption(
            "Suggerimento: carica una serie CSV oppure, dopo aver verificato "
            "le condizioni del servizio, abilita justETF e compila l'ISIN."
        )

# Conversione valutaria: le fonti che restituiscono gia' la valuta richiesta
# (justETF, CSV in valuta base) attraversano questo passaggio senza modifiche.
fx_res = fx.convert_currency(
    frame.prices, frame.currencies, base_ccy, start_date, end_date
)
prices = fx_res.prices

if prices.empty:
    st.error("Nessuna serie convertibile nella valuta di riferimento.")
    st.stop()

if fx_res.failed:
    st.error(
        "Esclusi dal backtest (valuta non risolvibile): " + ", ".join(fx_res.failed),
        icon="🚫",
    )
if fx_res.converted:
    origins = ", ".join(
        f"{s} ({frame.currencies.get(s, '?')} via {fx_res.sources.get(s, '?')})"
        for s in fx_res.converted
    )
    st.caption(f"💱 Convertiti in {base_ccy} ai cambi giornalieri: {origins}")
if fx_res.truncated:
    detail = ", ".join(f"{s} dal {d}" for s, d in fx_res.truncated.items())
    st.warning(
        f"Cambi disponibili solo da una data successiva a quella richiesta: {detail}. "
        "Il periodo è stato accorciato invece di usare un tasso retro-riempito.",
        icon="💱",
    )

used_sources = []
for symbol, src in frame.sources.items():
    if symbol not in prices.columns:
        continue
    source = registry.source_by_name(src)
    used_sources.append(f"{symbol} → **{source.label if source else src}**")
if used_sources:
    st.caption("📚 Fonti usate: " + ", ".join(used_sources))

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

        with st.spinner(f"Ricostruisco lo storico di {symbol} con {proxy.symbol}…"):
            proxy_series, _ = px.fetch_proxy_series(
                proxy, start_date, end_date, base_ccy
            )
        if proxy_series is None:
            notes.append(f"{symbol}: proxy {proxy.symbol} non disponibile")
            continue

        ext = px.extend_with_proxy(
            prices[symbol].dropna(), proxy_series, proxy, ter=fund["ter"] / 100
        )
        if ext is None:
            notes.append(
                f"{symbol}: {proxy.symbol} non è più anziano del fondo, niente da ricostruire"
            )
            continue

        extended_cols[symbol] = ext.series
        splice_dates[symbol] = ext.splice_date
        caveat = f" — {proxy.caveat}" if proxy.caveat else ""
        notes.append(
            f"**{symbol}** ricostruito dal {ext.series.index[0].date()} "
            f"con {proxy.label}{caveat}"
        )

    prices = pd.DataFrame(extended_cols).sort_index()

    if notes:
        with st.expander("🧩 Storico ricostruito", expanded=True):
            for note in notes:
                st.markdown("- " + note)
            st.caption(
                "I tratti ricostruiti sono stime basate su uno strumento diverso "
                "dal fondo, non dati reali. Nei grafici compaiono tratteggiati."
            )

for msg in coverage_warnings(prices, start_date):
    st.warning(msg, icon="📅")

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

try:
    res = run_backtest(prices, holdings, initial_value, rebalance, FeeMode.NET)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

st.divider()
st.subheader(
    f"Risultati · {res.start.strftime('%d/%m/%Y')} → {res.end.strftime('%d/%m/%Y')}"
)

# Etichetta -> data di innesto, per tratteggiare i grafici per fondo.
label_splice = {
    h.label: splice_dates[h.symbol]
    for h in holdings
    if h.symbol in splice_dates
}
portfolio_splice = max(label_splice.values()) if label_splice else None

summary = mt.summarize(res.portfolio, risk_free)
years = (res.end - res.start).days / 365.25

mhelp = metric_help(risk_free, initial_value, base_ccy)

k = st.columns(5)
k[0].metric("Valore finale", fmt_money(summary["Valore finale"], base_ccy),
            fmt_pct(summary["Rendimento totale"]), help=mhelp["Valore finale"])
k[1].metric("CAGR", fmt_pct(summary["CAGR"]), help=mhelp["CAGR"])
k[2].metric("Volatilità", fmt_pct(summary["Volatilita"]), help=mhelp["Volatilita"])
k[3].metric("Max drawdown", fmt_pct(summary["Max drawdown"]), help=mhelp["Max drawdown"])
k[4].metric("Sharpe", f"{summary['Sharpe']:.2f}", help=mhelp["Sharpe"])

if portfolio_splice is not None and portfolio_splice > res.start:
    st.info(
        f"🧩 Le metriche qui sopra includono il periodo ricostruito "
        f"({res.start.strftime('%d/%m/%Y')} → {portfolio_splice.strftime('%d/%m/%Y')}): "
        "sono indicative, non la performance realmente ottenuta dai fondi.",
        icon="🧩",
    )

with st.expander("❓ Come si leggono queste metriche"):
    for nome in ["Valore finale", "Rendimento totale", "CAGR", "Volatilita",
                 "Sharpe", "Sortino", "Max drawdown", "Calmar",
                 "Miglior anno", "Peggior anno", "Costo TER", "Ricostruito"]:
        etichetta = "Volatilità" if nome == "Volatilita" else nome
        st.markdown(f"- **{etichetta}** — {mhelp[nome]}")

# --- Impatto dei costi -----------------------------------------------------

if res.fee_drag > 0:
    pct_lost = res.fee_drag / res.portfolio_gross.iloc[-1]
    st.info(
        f"💸 **Impatto del TER**: su {years:.1f} anni le commissioni correnti sono "
        f"costate **{fmt_money(res.fee_drag, base_ccy)}**, pari al "
        f"**{fmt_pct(pct_lost)}** del montante che avresti avuto senza costi "
        f"({fmt_money(res.portfolio_gross.iloc[-1], base_ccy)} lordi contro "
        f"{fmt_money(res.portfolio.iloc[-1], base_ccy)} netti).",
        icon="💸",
    )

# --- Grafici ---------------------------------------------------------------


def split_at(series: pd.Series, splice: pd.Timestamp | None):
    """Divide una serie nel tratto ricostruito e in quello reale."""
    if splice is None:
        return None, series
    return series.loc[:splice], series.loc[splice:]


# I comparti scelti e l'interruttore della curva sintetica vivono nella scheda
# previdenza, che viene dopo il grafico del portafoglio. Streamlit riporta i
# valori dei widget con chiave in `session_state` **prima** di eseguire lo
# script, quindi qui si legge gia' la scelta corrente e non quella precedente.
_scelte = set(st.session_state.get("comparti_previdenza") or [])
comparti_scelti = (
    [c for c in covip.catalogo() if c.chiave in _scelte] if _scelte else []
)
mostra_sintetiche = bool(st.session_state.get("curve_sintetiche"))

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Portafoglio", "🆚 Confronto fondi", "📉 Drawdown", "📋 Dati",
     "🏦 Fondi pensione"]
)

with tab1:
    fig = go.Figure()
    recon, real = split_at(res.portfolio, portfolio_splice)
    if recon is not None and len(recon) > 1:
        fig.add_trace(go.Scatter(
            x=recon.index, y=recon.values, name="Portafoglio (ricostruito)",
            line=dict(color=PALETTE[0], width=2, dash="dot"), opacity=0.75,
            hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.0f} (ricostruito)<extra></extra>",
        ))
    fig.add_trace(go.Scatter(
        x=real.index, y=real.values, name="Portafoglio (netto TER)",
        line=dict(color=PALETTE[0], width=2.5),
        hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.0f}<extra></extra>",
    ))
    if show_gross:
        fig.add_trace(go.Scatter(
            x=res.portfolio_gross.index, y=res.portfolio_gross.values,
            name="Portafoglio (lordo, senza TER)",
            line=dict(color=PALETTE[0], width=1.5, dash="dash"), opacity=0.6,
            hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.0f}<extra></extra>",
        ))
    if portfolio_splice is not None and portfolio_splice > res.start:
        fig.add_vline(
            x=portfolio_splice, line=dict(color="#6b7280", width=1, dash="dot"),
            annotation_text="inizio dati reali", annotation_position="top left",
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
            curva = covip.serie_sintetica(
                rendimento / 100, res.start.date(), res.end.date(), initial_value
            )
            fig.add_trace(go.Scatter(
                x=curva.index, y=curva.values,
                name=f"{comparto.comparto} (sintetica)",
                line=dict(color=PALETTE[(i + 4) % len(PALETTE)], width=1.5, dash="dashdot"),
                opacity=0.8,
                hovertemplate="%{y:,.0f}<extra>" + comparto.comparto
                              + " · crescita costante</extra>",
            ))

    fig.add_hline(y=initial_value, line=dict(color="#9ca3af", width=1, dash="dash"),
                  annotation_text="capitale iniziale", annotation_position="bottom right")
    fig.update_layout(
        height=460, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title=f"Valore ({base_ccy})", xaxis_title=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig, width="stretch")

    if mostra_sintetiche and comparti_scelti:
        st.caption(
            "⚠️ Le curve dei fondi pensione sono **rette a crescita costante**, "
            "ricavate dal rendimento medio annuo COVIP: mostrano dove si "
            "sarebbe arrivati, non come ci si è arrivati. Il percorso reale ha "
            "oscillato, ma COVIP non pubblica le serie storiche."
        )

    st.markdown("**Composizione nel tempo**")
    area = go.Figure()
    for i, col in enumerate(res.contributions.columns):
        area.add_trace(go.Scatter(
            x=res.contributions.index, y=res.contributions[col], name=col,
            stackgroup="one", line=dict(width=0.5, color=PALETTE[i % len(PALETTE)]),
            hovertemplate="%{y:,.0f}<extra>" + col + "</extra>",
        ))
    area.update_layout(
        height=300, hovermode="x unified", margin=dict(l=0, r=0, t=10, b=0),
        yaxis_title=f"Valore ({base_ccy})",
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
            st.caption(
                f"Pesi impostati: {set_weights} → a fine periodo: {final_weights}."
            )
    else:
        rb_dates = sorted(rebalance_dates(res.prices.index, rebalance))
        label_rebal = st.session_state.rebalance.lower()
        if rb_dates:
            st.caption(
                f"Ribilanciamento {label_rebal}: {len(rb_dates)} interventi nel "
                f"periodo, l'ultimo il {rb_dates[-1].strftime('%d/%m/%Y')} "
                f"(pesi impostati: {set_weights})."
            )
        else:
            st.caption(
                f"Ribilanciamento {label_rebal}: nessun intervento ancora "
                "scattato, il periodo scelto è più corto della prima scadenza."
            )

with tab2:
    st.caption(
        f"Andamento di {fmt_money(initial_value, base_ccy)} investiti interamente "
        "in ciascun fondo, per un confronto a parità di capitale."
    )
    fig2 = go.Figure()
    for i, col in enumerate(res.per_fund.columns):
        color = PALETTE[i % len(PALETTE)]
        recon, real = split_at(res.per_fund[col], label_splice.get(col))
        if recon is not None and len(recon) > 1:
            fig2.add_trace(go.Scatter(
                x=recon.index, y=recon.values, name=f"{col} (ricostruito)",
                line=dict(color=color, width=1.5, dash="dot"), opacity=0.7,
                showlegend=False,
                hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.0f} (ricostruito)"
                              "<extra>" + col + "</extra>",
            ))
        fig2.add_trace(go.Scatter(
            x=real.index, y=real.values, name=col,
            line=dict(color=color, width=2),
            hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.0f}<extra>" + col + "</extra>",
        ))
        if show_gross:
            fig2.add_trace(go.Scatter(
                x=res.per_fund_gross.index, y=res.per_fund_gross[col],
                name=f"{col} (lordo)", line=dict(color=color, width=1, dash="dash"),
                opacity=0.45, showlegend=False, hoverinfo="skip",
            ))
    fig2.update_layout(
        height=460, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title=f"Valore ({base_ccy})",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig2, width="stretch")

    rows = {}
    for col in res.per_fund.columns:
        s = mt.summarize(res.per_fund[col], risk_free)
        gross_final = res.per_fund_gross[col].iloc[-1]
        s["Costo TER"] = gross_final - res.per_fund[col].iloc[-1]
        s["Ricostruito"] = "sì" if col in label_splice else "no"
        rows[col] = s
    rows["🎯 PORTAFOGLIO"] = {
        **summary,
        "Costo TER": res.fee_drag,
        "Ricostruito": "sì" if label_splice else "no",
    }

    table = pd.DataFrame(rows).T
    styled = table.copy()
    styled["Valore finale"] = styled["Valore finale"].map(lambda v: fmt_money(v, base_ccy))
    styled["Costo TER"] = styled["Costo TER"].map(lambda v: fmt_money(v, base_ccy))
    for c in ["Rendimento totale", "CAGR", "Volatilita", "Max drawdown",
              "Miglior anno", "Peggior anno"]:
        styled[c] = styled[c].map(lambda v: fmt_pct(v))
    for c in ["Sharpe", "Sortino", "Calmar"]:
        styled[c] = styled[c].map(lambda v: "n/d" if pd.isna(v) else f"{v:.2f}")
    styled.index.name = "Strumento"

    capitale_confronto = fmt_money(initial_value, base_ccy)
    st.caption(
        f"Tutte le righe partono dallo stesso capitale: **{capitale_confronto}** "
        "investiti al 100% in un solo fondo, e gli stessi "
        f"**{capitale_confronto}** investiti nel portafoglio con i pesi "
        "impostati e il ribilanciamento scelto. I valori finali sono quindi "
        "confrontabili direttamente riga per riga."
    )
    st.dataframe(
        styled, width="stretch",
        column_config={
            "Valore finale": st.column_config.TextColumn(
                f"Valore finale (da {capitale_confronto})",
                help=mhelp["Valore finale"],
            ),
            "Volatilita": st.column_config.TextColumn(
                "Volatilità", help=mhelp["Volatilita"]
            ),
            **{
                nome: st.column_config.TextColumn(nome, help=mhelp[nome])
                for nome in [
                    "Rendimento totale", "CAGR", "Sharpe", "Sortino",
                    "Max drawdown", "Calmar", "Miglior anno", "Peggior anno",
                    "Costo TER", "Ricostruito",
                ]
            },
        },
    )
    if label_splice:
        st.caption(
            "La colonna *Ricostruito* segnala le righe le cui metriche "
            "comprendono un periodo stimato da un proxy."
        )

with tab3:
    dd_fig = go.Figure()
    dd = mt.drawdown_series(res.portfolio)
    dd_fig.add_trace(go.Scatter(
        x=dd.index, y=dd.values * 100, name="Portafoglio", fill="tozeroy",
        line=dict(color=PALETTE[0], width=1.5),
        hovertemplate="%{x|%d/%m/%Y}<br>%{y:.2f}%<extra></extra>",
    ))
    for i, col in enumerate(res.per_fund.columns):
        d = mt.drawdown_series(res.per_fund[col])
        dd_fig.add_trace(go.Scatter(
            x=d.index, y=d.values * 100, name=col,
            line=dict(color=PALETTE[(i + 1) % len(PALETTE)], width=1), opacity=0.7,
            hovertemplate="%{y:.2f}%<extra>" + col + "</extra>",
        ))
    if portfolio_splice is not None and portfolio_splice > res.start:
        dd_fig.add_vline(
            x=portfolio_splice, line=dict(color="#6b7280", width=1, dash="dot"),
            annotation_text="inizio dati reali", annotation_position="top left",
        )
    dd_fig.update_layout(
        height=420, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title="Drawdown (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(dd_fig, width="stretch")

    st.markdown("**Rendimenti per anno solare**")
    yearly = pd.DataFrame({"Portafoglio": mt.calendar_year_returns(res.portfolio)})
    for col in res.per_fund.columns:
        yearly[col] = mt.calendar_year_returns(res.per_fund[col])
    ybars = go.Figure()
    for i, col in enumerate(yearly.columns):
        ybars.add_trace(go.Bar(
            x=yearly.index.astype(str), y=yearly[col] * 100, name=col,
            marker_color=PALETTE[i % len(PALETTE)],
            hovertemplate="%{y:.2f}%<extra>" + col + "</extra>",
        ))
    ybars.update_layout(
        height=320, barmode="group", margin=dict(l=0, r=0, t=10, b=0),
        yaxis_title="Rendimento (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(ybars, width="stretch")

with tab4:
    out = pd.DataFrame({
        "Portafoglio (netto)": res.portfolio,
        "Portafoglio (lordo)": res.portfolio_gross,
    }).join(res.per_fund.add_prefix("Solo "))
    st.dataframe(out.tail(500).iloc[::-1].round(2), width="stretch", height=420)
    st.download_button(
        "⬇️ Scarica CSV completo",
        out.to_csv().encode("utf-8"),
        file_name=f"backtest_{res.start.date()}_{res.end.date()}.csv",
        mime="text/csv",
    )

with tab5:
    anno_rif = covip.anno_riferimento()
    st.markdown(
        f"### Previdenza complementare · dati COVIP al 31/12/{anno_rif}"
        if anno_rif else "### Previdenza complementare · dati COVIP"
    )

    st.warning(
        "**Il confronto non considera la fiscalità.** I fondi pensione godono "
        "di deducibilità fino a 5.164,57 € l'anno, tassazione dei rendimenti al "
        "20% invece del 26% e imposta finale che scende dal 15% al 9%. Sono "
        "vantaggi che giocano a loro favore, quindi i numeri qui sotto li "
        "**sottostimano**.",
        icon="⚖️",
    )
    st.caption(
        "COVIP pubblica solo rendimenti medi annui su orizzonti fissi, non le "
        "serie storiche: per questi strumenti volatilità, drawdown e Sharpe non "
        "sono calcolabili da nessun dato pubblico. Per averli, carica il valore "
        "quota del tuo fondo con l'uploader CSV nella barra laterale."
    )

    catalogo = covip.catalogo()
    if not catalogo:
        st.error(
            "Catalogo COVIP non disponibile: controlla la connessione e riprova."
        )
    else:
        f1, f2, f3 = st.columns([1.2, 1.2, 2.6])
        tipo_sel = f1.selectbox(
            "Forma pensionistica", ["Tutte", "negoziale", "aperto", "PIP"],
            key="tipo_previdenza",
        )
        categorie = ["Tutte"] + sorted({c.categoria for c in catalogo if c.categoria})
        cat_sel = f2.selectbox("Categoria", categorie, key="categoria_previdenza")
        testo = f3.text_input(
            "Cerca per nome del fondo o della società",
            placeholder="es. 'previgest', 'cometa', 'mediolanum'",
            key="testo_previdenza",
        )

        trovati = covip.cerca(
            testo,
            tipo=None if tipo_sel == "Tutte" else tipo_sel,
            categoria=None if cat_sel == "Tutte" else cat_sel,
        )
        st.caption(f"{len(trovati)} comparti corrispondono ai filtri.")

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
            "Comparti da confrontare",
            options=opzioni,
            format_func=lambda k: etichetta.get(k, k),
            key="comparti_previdenza",
        )

        if not comparti_scelti:
            st.info(
                "Seleziona uno o più comparti per confrontarli con il tuo portafoglio."
            )
        else:
            finestre = {a: covip.finestra(a) for a in covip.ORIZZONTI}
            finestre = {a: w for a, w in finestre.items() if w}
            rend_port = hz.rendimenti_per_orizzonte(res.portfolio, finestre)

            righe = []
            for c in comparti_scelti:
                riga = {"Strumento": f"{c.fondo} · {c.comparto}", "Tipo": c.tipo,
                        "Categoria": c.categoria}
                for anni in covip.ORIZZONTI:
                    valore = c.rendimenti.get(anni)
                    riga[f"{anni}a"] = "n/d" if valore is None else f"{valore:.2f}%"
                isc10 = c.isc.get(10)
                riga["ISC 10a"] = "n/d" if isc10 is None else f"{isc10:.2f}%"
                righe.append(riga)

            riga_port = {"Strumento": "🎯 IL TUO PORTAFOGLIO", "Tipo": "—",
                         "Categoria": "—"}
            for anni in covip.ORIZZONTI:
                valore = rend_port.get(anni)
                riga_port[f"{anni}a"] = "n/d" if valore is None else f"{valore * 100:.2f}%"
            riga_port["ISC 10a"] = "—"
            righe.append(riga_port)

            st.markdown("**Rendimento medio annuo, sulle stesse finestre COVIP**")
            covip_column_config = {
                f"{anni}a": st.column_config.TextColumn(
                    f"{anni}a",
                    help=f"Rendimento medio annuo COVIP sulla finestra a {anni} anni "
                         f"({covip.periodi().get(anni, '')}).",
                )
                for anni in covip.ORIZZONTI
            }
            covip_column_config["ISC 10a"] = st.column_config.TextColumn(
                "ISC 10a",
                help="L'equivalente del TER per la previdenza: incidenza annua "
                     "dei costi sull'orizzonte a 10 anni.",
            )
            st.dataframe(
                pd.DataFrame(righe), hide_index=True, width="stretch",
                column_config=covip_column_config,
            )

            mancanti = [a for a in covip.ORIZZONTI if rend_port.get(a) is None]
            if mancanti:
                st.caption(
                    "Il tuo portafoglio risulta **n/d** su "
                    + ", ".join(f"{a} anni" for a in mancanti)
                    + f" perché non copre l'intera finestra ("
                    + ", ".join(f"{a}a = {covip.periodi().get(a)}" for a in mancanti)
                    + "). Calcolarlo su un periodo più corto darebbe un numero "
                      "non confrontabile."
                )

            # --- grafico a barre ---
            bars = go.Figure()
            orizzonti_utili = [a for a in covip.ORIZZONTI if finestre.get(a)]
            for i, c in enumerate(comparti_scelti):
                bars.add_trace(go.Bar(
                    name=f"{c.comparto[:24]}",
                    x=[f"{a} anni" for a in orizzonti_utili],
                    y=[c.rendimenti.get(a) for a in orizzonti_utili],
                    marker_color=PALETTE[(i + 4) % len(PALETTE)],
                    hovertemplate="%{y:.2f}%<extra>" + c.comparto + "</extra>",
                ))
            bars.add_trace(go.Bar(
                name="Il tuo portafoglio",
                x=[f"{a} anni" for a in orizzonti_utili],
                y=[None if rend_port.get(a) is None else rend_port[a] * 100
                   for a in orizzonti_utili],
                marker_color=PALETTE[0],
                hovertemplate="%{y:.2f}%<extra>portafoglio</extra>",
            ))
            bars.update_layout(
                height=360, barmode="group", margin=dict(l=0, r=0, t=30, b=0),
                yaxis_title="Rendimento medio annuo (%)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            )
            st.plotly_chart(bars, width="stretch")

            # --- impatto dell'ISC ---
            st.markdown("**Quanto pesano i costi**")
            costi = []
            for c in comparti_scelti:
                isc10 = c.isc.get(10)
                if isc10 is None:
                    continue
                eroso = hz.costo_cumulato(isc10 / 100, 10, initial_value)
                lordo = c.rendimenti.get(10)
                costi.append({
                    "Comparto": f"{c.fondo} · {c.comparto}",
                    "ISC annuo": f"{isc10:.2f}%",
                    "Rendimento 10a": "n/d" if lordo is None else f"{lordo:.2f}%",
                    f"Eroso su {fmt_money(initial_value, base_ccy)} in 10 anni":
                        fmt_money(eroso, base_ccy),
                    "Quota del rendimento": "n/d" if not lordo or lordo <= 0
                        else f"{isc10 / lordo * 100:.0f}%",
                })
            if costi:
                st.dataframe(pd.DataFrame(costi), hide_index=True, width="stretch")
                st.caption(
                    "L'ISC è l'equivalente del TER per la previdenza. L'ultima "
                    "colonna mostra che frazione del rendimento netto ottenuto "
                    "viene assorbita ogni anno dai costi."
                )

            st.divider()
            st.checkbox(
                "Mostra le curve dei fondi pensione nel grafico del portafoglio",
                key="curve_sintetiche",
                help="Rette a crescita costante ricavate dal rendimento medio "
                     "annuo: mostrano il punto d'arrivo, non il percorso.",
            )
            if st.session_state.get("curve_sintetiche"):
                st.selectbox(
                    "Orizzonte da cui ricavare il tasso",
                    covip.ORIZZONTI, index=3, key="orizzonte_curva",
                    format_func=lambda a: f"{a} anni ({covip.periodi().get(a, '')})",
                )

    st.caption(
        "Fonte: [COVIP](https://www.covip.it/open-data), open data con licenza "
        "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Il progetto "
        "normalizza e aggrega i dataset e calcola confronti e curve sintetiche; "
        "queste elaborazioni non sono dati COVIP originali."
    )

st.divider()
st.caption(
    "Prezzi *total return* (dividendi reinvestiti). I NAV dei fondi sono già al "
    "netto del TER; la curva lorda è una ricostruzione teorica. I cambi sono "
    "quelli ufficiali BCE dal 1999, ottenuti tramite Frankfurter, con ripiego "
    "su Yahoo per le valute fuori paniere. Non sono considerati costi di "
    "ingresso/uscita, spread né fiscalità. Le performance passate non sono "
    "indicative di quelle future."
)
