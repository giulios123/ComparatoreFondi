"""Comparatore Fondi - backtester per fondi ed ETF su piu' fonti dati."""

from __future__ import annotations

import datetime as dt

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comparatore import cache as disk_cache
from comparatore import covip
from comparatore import fx
from comparatore import horizons as hz
from comparatore import metrics as mt
from comparatore import proxies as px
from comparatore.engine import FeeMode, Holding, Rebalance, coverage_warnings, run_backtest
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


def api_key(name: str) -> str:
    """Chiave API da st.secrets, con ripiego sull'ambiente.

    Non deve mai finire nel codice ne' nel repository.
    """
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return str(value or "").strip()


def build_registry() -> Registry:
    """Registry delle fonti, ricostruito a ogni rerun.

    E' un oggetto leggero: le serie stanno nella cache su disco, non qui
    dentro, quindi ricrearlo non costa nulla e non c'e' stato da invalidare.
    """
    reg = Registry(
        eodhd_key=api_key("EODHD_API_KEY"),
        twelvedata_key=api_key("TWELVEDATA_API_KEY"),
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
            "Ribilanciamento", list(REBALANCE_LABELS), index=0, key="rebalance"
        )
    ]

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
    reg_probe = build_registry()
    for source in reg_probe.all_sources:
        ready = source.available()
        st.caption(f"{'🟢' if ready else '⚪'} {source.label}"
                   + ("" if ready else " — non configurata"))
    st.caption(
        "Ordine: CSV → justETF (con ISIN) → Yahoo → EODHD → Twelve Data. "
        "Si può forzare la fonte per singolo fondo dalla tabella."
    )
    if not reg_probe.eodhd.available():
        st.info(
            "Per i **fondi collocati in Italia** (Mediolanum, Fineco, banche) "
            "conviene configurare EODHD: Yahoo ne copre solo una parte e con "
            "storico dal 2018. Serve una chiave in `.streamlit/secrets.toml` "
            "o nella variabile `EODHD_API_KEY`.",
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
                "🔗 Cercando per ISIN si abilita anche justETF, che copre gli "
                "ETF europei che Yahoo non ha."
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
            help="Compilalo per abilitare justETF su questo fondo: copre gli "
                 "ETF europei che Yahoo non ha.",
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
            "Suggerimento: compila l'ISIN per abilitare justETF, oppure carica "
            "la serie da CSV nella barra laterale."
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

k = st.columns(5)
k[0].metric("Valore finale", fmt_money(summary["Valore finale"], base_ccy),
            fmt_pct(summary["Rendimento totale"]))
k[1].metric("CAGR", fmt_pct(summary["CAGR"]))
k[2].metric("Volatilità", fmt_pct(summary["Volatilita"]))
k[3].metric("Max drawdown", fmt_pct(summary["Max drawdown"]))
k[4].metric("Sharpe", f"{summary['Sharpe']:.2f}")

if portfolio_splice is not None and portfolio_splice > res.start:
    st.info(
        f"🧩 Le metriche qui sopra includono il periodo ricostruito "
        f"({res.start.strftime('%d/%m/%Y')} → {portfolio_splice.strftime('%d/%m/%Y')}): "
        "sono indicative, non la performance realmente ottenuta dai fondi.",
        icon="🧩",
    )

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
    st.dataframe(styled, width="stretch")
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
            st.dataframe(pd.DataFrame(righe), hide_index=True, width="stretch")

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
        "CC BY 4.0. I dati si aggiornano una volta l'anno."
    )

st.divider()
st.caption(
    "Prezzi *total return* (dividendi reinvestiti). I NAV dei fondi sono già al "
    "netto del TER; la curva lorda è una ricostruzione teorica. I cambi sono "
    "quelli ufficiali BCE dal 1999, con ripiego su Yahoo per le valute fuori "
    "paniere. Non sono considerati costi di ingresso/uscita, spread né fiscalità. "
    "Le performance passate non sono indicative di quelle future."
)
