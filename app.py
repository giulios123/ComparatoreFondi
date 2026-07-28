"""Comparatore Fondi - backtester per fondi ed ETF con dati Yahoo Finance."""

from __future__ import annotations

import datetime as dt

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comparatore import data as dl
from comparatore import metrics as mt
from comparatore.engine import FeeMode, Holding, Rebalance, coverage_warnings, run_backtest

st.set_page_config(page_title="Comparatore Fondi", page_icon="📈", layout="wide")

CURRENCIES = ["EUR", "USD", "GBP", "CHF", "JPY"]
SYMBOLS = {"EUR": "€", "USD": "$", "GBP": "£", "CHF": "CHF ", "JPY": "¥"}

REBALANCE_LABELS = {
    "Nessuno (buy & hold)": Rebalance.NONE,
    "Mensile": Rebalance.MONTHLY,
    "Trimestrale": Rebalance.QUARTERLY,
    "Annuale": Rebalance.YEARLY,
}

PALETTE = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed",
           "#0891b2", "#db2777", "#65a30d", "#4b5563", "#ea580c"]


# --------------------------------------------------------------------------
# Cached data access
# --------------------------------------------------------------------------


@st.cache_data(show_spinner=False, ttl=3600)
def cached_search(query: str, funds_only: bool) -> list[dict]:
    return [vars(i) for i in dl.search(query, limit=15, funds_only=funds_only)]


@st.cache_data(show_spinner=False, ttl=3600)
def cached_metadata(symbol: str) -> dict:
    return vars(dl.get_metadata(symbol))


@st.cache_data(show_spinner=False, ttl=1800)
def cached_prices(symbols: tuple[str, ...], start: dt.date, end: dt.date):
    return dl.get_prices(list(symbols), start, end)


@st.cache_data(show_spinner=False, ttl=1800)
def cached_converted(symbols: tuple[str, ...], start: dt.date, end: dt.date, base: str):
    prices, ccy = cached_prices(symbols, start, end)
    if prices.empty:
        return prices, ccy, [], []
    res = dl.convert_currency(prices, ccy, base, start, end)
    return res.prices, ccy, res.converted, res.failed


def fmt_money(v: float, ccy: str) -> str:
    return f"{SYMBOLS.get(ccy, '')}{v:,.0f}".replace(",", ".")


def fmt_pct(v: float, decimals: int = 2) -> str:
    return "n/d" if pd.isna(v) else f"{v * 100:.{decimals}f}%"


# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------

if "selected" not in st.session_state:
    st.session_state.selected = []  # list of dicts: symbol,name,weight,ter,extra


def add_fund(symbol: str, name: str):
    if any(f["symbol"] == symbol for f in st.session_state.selected):
        st.toast(f"{symbol} è già nel portafoglio", icon="⚠️")
        return
    meta = cached_metadata(symbol)
    st.session_state.selected.append({
        "symbol": symbol,
        "name": meta.get("name") or name,
        "currency": meta.get("currency") or "",
        "weight": 0.0,
        "ter": (meta.get("ter") or 0.0) * 100,  # stored as percent for the UI
        "ter_auto": meta.get("ter") is not None,
        "extra": 0.0,
    })
    equalize_weights()
    st.toast(f"Aggiunto {symbol}", icon="✅")


def equalize_weights():
    n = len(st.session_state.selected)
    if n:
        for f in st.session_state.selected:
            f["weight"] = round(100 / n, 2)


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Parametri")

    today = dt.date.today()
    col_a, col_b = st.columns(2)
    start_date = col_a.date_input(
        "Data inizio", value=today - dt.timedelta(days=365 * 10),
        min_value=dt.date(1970, 1, 1), max_value=today, format="DD/MM/YYYY",
    )
    end_date = col_b.date_input(
        "Data fine", value=today, min_value=dt.date(1970, 1, 1),
        max_value=today, format="DD/MM/YYYY",
    )

    initial_value = st.number_input(
        "Valore iniziale del portafoglio", min_value=100.0, value=10_000.0,
        step=1_000.0, format="%.0f",
    )
    base_ccy = st.selectbox("Valuta di riferimento", CURRENCIES, index=0)
    rebalance = REBALANCE_LABELS[
        st.selectbox("Ribilanciamento", list(REBALANCE_LABELS), index=0)
    ]

    st.divider()
    st.subheader("Costi")
    st.caption(
        "I NAV pubblicati da Yahoo sono **già al netto del TER**. "
        "La curva *lorda* ricostruisce il fondo senza commissioni: "
        "la distanza fra le due curve è il costo del TER."
    )
    show_gross = st.checkbox("Mostra anche la curva lorda (senza TER)", value=True)

    st.divider()
    risk_free = st.number_input(
        "Tasso risk-free annuo (per Sharpe)", min_value=0.0, max_value=0.20,
        value=0.02, step=0.005, format="%.3f",
    )

# --------------------------------------------------------------------------
# Header + search
# --------------------------------------------------------------------------

st.title("📈 Comparatore Fondi")
st.caption("Backtest di fondi ed ETF su dati Yahoo Finance, con impatto del TER.")

with st.expander("🔎 Cerca fondi ed ETF", expanded=not st.session_state.selected):
    c1, c2 = st.columns([4, 1])
    query = c1.text_input(
        "Nome, ticker o ISIN",
        placeholder="es. 'Vanguard S&P 500', 'VUSA.AS' oppure 'IE00B3XXRP09'",
        label_visibility="collapsed",
    )
    funds_only = c2.toggle("Solo fondi/ETF", value=True)

    if query:
        with st.spinner("Ricerca su Yahoo Finance…"):
            results = cached_search(query, funds_only)
        if not results:
            st.info("Nessun risultato. Prova con l'ISIN o con il ticker completo.")
        for r in results:
            cols = st.columns([5, 1.4, 1.4, 1])
            cols[0].markdown(f"**{r['name']}**  \n`{r['symbol']}`")
            cols[1].markdown(f"<small>{r['quote_type']}</small>", unsafe_allow_html=True)
            cols[2].markdown(f"<small>{r['exchange']}</small>", unsafe_allow_html=True)
            cols[3].button(
                "Aggiungi", key=f"add_{r['symbol']}",
                on_click=add_fund, args=(r["symbol"], r["name"]),
                width='stretch',
            )

# --------------------------------------------------------------------------
# Portfolio composition
# --------------------------------------------------------------------------

st.subheader("Composizione del portafoglio")

if not st.session_state.selected:
    st.info("Cerca e aggiungi almeno un fondo per iniziare.")
    st.stop()

editor_df = pd.DataFrame([
    {
        "Fondo": f["name"],
        "Simbolo": f["symbol"],
        "Valuta": f["currency"],
        "Peso %": f["weight"],
        "TER %": f["ter"],
        "Costi extra %": f["extra"],
    }
    for f in st.session_state.selected
])

edited = st.data_editor(
    editor_df,
    hide_index=True,
    width='stretch',
    disabled=["Fondo", "Simbolo", "Valuta"],
    column_config={
        "Peso %": st.column_config.NumberColumn(
            "Peso %", min_value=0.0, max_value=100.0, step=1.0, format="%.2f",
            help="Quota del portafoglio assegnata al fondo.",
        ),
        "TER %": st.column_config.NumberColumn(
            "TER %", min_value=0.0, max_value=10.0, step=0.01, format="%.3f",
            help="Spesa corrente annua. Precompilato da Yahoo quando disponibile: "
                 "verifica sempre sul KID del fondo.",
        ),
        "Costi extra %": st.column_config.NumberColumn(
            "Costi extra %", min_value=0.0, max_value=10.0, step=0.05, format="%.3f",
            help="Costi annui NON già inclusi nel NAV (custodia, consulenza). "
                 "Vengono sottratti dalla performance.",
        ),
    },
    key="composition",
)

# Push edits back into state.
for i, row in edited.iterrows():
    st.session_state.selected[i]["weight"] = float(row["Peso %"])
    st.session_state.selected[i]["ter"] = float(row["TER %"])
    st.session_state.selected[i]["extra"] = float(row["Costi extra %"])

total_weight = sum(f["weight"] for f in st.session_state.selected)

b1, b2, b3, b4 = st.columns([1, 1, 1, 3])
b1.button("⚖️ Pesi uguali", on_click=equalize_weights, width='stretch')
if b2.button("🗑️ Svuota", width='stretch'):
    st.session_state.selected = []
    st.rerun()
b3.metric("Totale pesi", f"{total_weight:.1f}%")

missing_ter = [f["symbol"] for f in st.session_state.selected
               if f["ter"] == 0 and not f["ter_auto"]]
if missing_ter:
    b4.warning(
        f"TER non trovato su Yahoo per: {', '.join(missing_ter)}. "
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
# Backtest
# --------------------------------------------------------------------------

symbols = tuple(f["symbol"] for f in st.session_state.selected)

with st.spinner("Scarico le serie storiche…"):
    prices, raw_ccy, converted, failed = cached_converted(
        symbols, start_date, end_date, base_ccy
    )

if prices.empty:
    st.error("Nessun dato di prezzo scaricato per i simboli selezionati.")
    st.stop()
if failed:
    st.error(
        "Esclusi dal backtest (valuta non convertibile): " + ", ".join(failed), icon="🚫"
    )
if converted:
    st.caption(
        "💱 Convertiti in " + base_ccy + " ai cambi giornalieri: "
        + ", ".join(f"{s} ({raw_ccy.get(s, '?')})" for s in converted)
    )

for msg in coverage_warnings(prices, start_date):
    st.warning(msg, icon="📅")

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

summary = mt.summarize(res.portfolio, risk_free)
years = (res.end - res.start).days / 365.25

k = st.columns(5)
k[0].metric("Valore finale", fmt_money(summary["Valore finale"], base_ccy),
            fmt_pct(summary["Rendimento totale"]))
k[1].metric("CAGR", fmt_pct(summary["CAGR"]))
k[2].metric("Volatilità", fmt_pct(summary["Volatilita"]))
k[3].metric("Max drawdown", fmt_pct(summary["Max drawdown"]))
k[4].metric("Sharpe", f"{summary['Sharpe']:.2f}")

# --- Cost impact -----------------------------------------------------------

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

# --- Charts ----------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Portafoglio", "🆚 Confronto fondi", "📉 Drawdown", "📋 Dati"]
)

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=res.portfolio.index, y=res.portfolio.values, name="Portafoglio (netto TER)",
        line=dict(color=PALETTE[0], width=2.5),
        hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.0f}<extra></extra>",
    ))
    if show_gross:
        fig.add_trace(go.Scatter(
            x=res.portfolio_gross.index, y=res.portfolio_gross.values,
            name="Portafoglio (lordo, senza TER)",
            line=dict(color=PALETTE[0], width=1.5, dash="dot"),
            hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.0f}<extra></extra>",
        ))
    fig.add_hline(y=initial_value, line=dict(color="#9ca3af", width=1, dash="dash"),
                  annotation_text="capitale iniziale", annotation_position="bottom right")
    fig.update_layout(
        height=460, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title=f"Valore ({base_ccy})", xaxis_title=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig, width='stretch')

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
    st.plotly_chart(area, width='stretch')

with tab2:
    st.caption(
        f"Andamento di {fmt_money(initial_value, base_ccy)} investiti interamente "
        "in ciascun fondo, per un confronto a parità di capitale."
    )
    fig2 = go.Figure()
    for i, col in enumerate(res.per_fund.columns):
        color = PALETTE[i % len(PALETTE)]
        fig2.add_trace(go.Scatter(
            x=res.per_fund.index, y=res.per_fund[col], name=col,
            line=dict(color=color, width=2),
            hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.0f}<extra>" + col + "</extra>",
        ))
        if show_gross:
            fig2.add_trace(go.Scatter(
                x=res.per_fund_gross.index, y=res.per_fund_gross[col],
                name=f"{col} (lordo)", line=dict(color=color, width=1, dash="dot"),
                opacity=0.55, showlegend=False, hoverinfo="skip",
            ))
    fig2.update_layout(
        height=460, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title=f"Valore ({base_ccy})",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig2, width='stretch')

    rows = {}
    for col in res.per_fund.columns:
        s = mt.summarize(res.per_fund[col], risk_free)
        gross_final = res.per_fund_gross[col].iloc[-1]
        s["Costo TER"] = gross_final - res.per_fund[col].iloc[-1]
        rows[col] = s
    rows["🎯 PORTAFOGLIO"] = {**summary, "Costo TER": res.fee_drag}

    table = pd.DataFrame(rows).T
    styled = table.copy()
    styled["Valore finale"] = styled["Valore finale"].map(lambda v: fmt_money(v, base_ccy))
    styled["Costo TER"] = styled["Costo TER"].map(lambda v: fmt_money(v, base_ccy))
    for c in ["Rendimento totale", "CAGR", "Volatilita", "Max drawdown",
              "Miglior anno", "Peggior anno"]:
        styled[c] = styled[c].map(lambda v: fmt_pct(v))
    for c in ["Sharpe", "Sortino", "Calmar"]:
        styled[c] = styled[c].map(lambda v: "n/d" if pd.isna(v) else f"{v:.2f}")
    st.dataframe(styled, width='stretch')

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
    dd_fig.update_layout(
        height=420, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title="Drawdown (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(dd_fig, width='stretch')

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
    st.plotly_chart(ybars, width='stretch')

with tab4:
    out = pd.DataFrame({
        "Portafoglio (netto)": res.portfolio,
        "Portafoglio (lordo)": res.portfolio_gross,
    }).join(res.per_fund.add_prefix("Solo "))
    st.dataframe(out.tail(500).iloc[::-1].round(2), width='stretch', height=420)
    st.download_button(
        "⬇️ Scarica CSV completo",
        out.to_csv().encode("utf-8"),
        file_name=f"backtest_{res.start.date()}_{res.end.date()}.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Dati Yahoo Finance, prezzi *total return* (dividendi reinvestiti). "
    "I NAV dei fondi sono già al netto del TER; la curva lorda è una ricostruzione "
    "teorica. Non sono considerati costi di ingresso/uscita, spread né fiscalità. "
    "Le performance passate non sono indicative di quelle future."
)
