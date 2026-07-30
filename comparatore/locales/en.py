"""English catalog. Keys must match `comparatore.locales.it` exactly -
`tests/test_i18n.py` checks the four catalogs stay in sync."""

LINGUA = "en"
NOME = "English"

MESSAGGI: dict[str, str] = {
    # --- Header -------------------------------------------------
    "app.page_title": "Fund Comparator",
    "app.title": "📈 Fund Comparator",
    "app.subtitle": "Backtest funds and ETFs across multiple data sources, with TER cost impact.",

    # --- Rebalancing (dropdown help) --------------------------
    "rebalance.help": (
        "Periodically brings weights back to the target, selling what has "
        "grown the most to buy back what has lagged.\n\n"
        "- **None (buy & hold)**: bought once and never touched again. "
        "Weights drift: the best-performing fund keeps growing its share, "
        "and the portfolio becomes progressively more concentrated.\n"
        "- **Monthly / Quarterly / Yearly**: on the first trading day of "
        "each period, weights are reset to the target values.\n\n"
        "The backtest does not apply trading fees or capital-gains tax: "
        "rebalancing often is therefore more advantageous here than it "
        "would be in reality."
    ),

    # --- Sidebar: general parameters ------------------------------------
    "sidebar.header": "⚙️ Parameters",
    "sidebar.lingua_label": "Language",
    "sidebar.periodo_caption": "Period",
    "preset.1y": "1y",
    "preset.5y": "5y",
    "preset.10y": "10y",
    "preset.20y": "20y",
    "preset.max": "Max",
    "sidebar.data_inizio": "Start date",
    "sidebar.data_fine": "End date",
    "sidebar.valore_iniziale": "Initial portfolio value",
    "sidebar.valuta_riferimento": "Reference currency",
    "sidebar.ribilanciamento_label": "Rebalancing",
    "sidebar.rebalance_caption_none": (
        "The weights you set are a starting point: without rebalancing "
        "they drift over time with the funds' relative returns."
    ),
    "sidebar.rebalance_caption_active": (
        "Weights return to the target values on the first trading day of "
        "each period (no trading costs applied)."
    ),

    # --- Sidebar: costs --------------------------------------------------
    "costs.subheader": "Costs",
    "costs.caption": (
        "Published NAVs are **already net of the TER**. "
        "The *gross* curve reconstructs the fund without fees: "
        "the gap between the two curves is the cost of the TER."
    ),
    "costs.show_gross_checkbox": "Also show the gross curve (without TER)",

    # --- Sidebar: extended history ------------------------------------------
    "history.subheader": "Extended history",
    "history.checkbox": "Reconstruct the period before the fund's inception",
    "history.help": (
        "Extends the series backward using an older index or fund. This is "
        "a reconstruction, not real data: it appears dashed in the charts."
    ),
    "history.caption_non_usd": (
        "⚠️ Proxies are quoted in dollars. With a reference currency other "
        "than USD the reconstruction cannot go earlier than **{anno}**, the "
        "first date of official ECB exchange rates."
    ),
    "history.caption_usd": "USD currency: the reconstruction can use the proxy's full depth.",

    # --- Sidebar: data sources -----------------------------------------------
    "sources.subheader": "Data sources",
    "sources.justetf_info": (
        "**What enabling justETF means**\n\n"
        "justETF does not offer a documented public API for this feature. "
        "If you enable the integration, for ETFs identified by ISIN the app "
        "will try it automatically **before Yahoo**, and will send from the "
        "computer or server running the app:\n\n"
        "- the ETF's ISIN, requested date range and currency;\n"
        "- IP address and standard technical connection data.\n\n"
        "No capital, portfolio weights, CSV files or API keys are sent. "
        "The series received are kept in the local cache. The endpoint may "
        "change or stop working, and its use remains subject to "
        "[justETF's terms]"
        "(https://www.justetf.com/it/about/legal-terms.html) and the data "
        "providers' rights. Consent applies to this session only; leaving "
        "the checkbox off, justETF will only be contacted if you "
        "explicitly choose it as the source for a single fund."
    ),
    "sources.justetf_checkbox": "I consent to automatic requests to justETF",
    "sources.justetf_help": (
        "Adds justETF before Yahoo in the automatic order for ISIN-identified "
        "ETFs. You can revoke consent by unchecking the box."
    ),
    "sources.status_optin_off": " — opt-in disabled",
    "sources.status_not_configured": " — not configured",
    "sources.order_caption": (
        "Automatic order: CSV → Yahoo → EODHD → Twelve Data; justETF joins "
        "only with the opt-in above. You can always force a source per "
        "fund from the table. EODHD and Twelve Data caches expire after "
        "{giorni} days."
    ),
    "sources.eodhd_hint": (
        "For **funds domiciled in Italy** (Mediolanum, Fineco, banks) it's "
        "worth configuring EODHD: Yahoo only covers part of them, with "
        "history from 2018. Enter the key above, in **🔑 API Keys**."
    ),
    "sources.used_caption": "📚 Sources used: {elenco}",

    # --- Sidebar: API keys -------------------------------------------------
    "api_keys.expander": "🔑 API keys (EODHD, Twelve Data)",
    "api_keys.caption": (
        "Kept only on this computer, in `.streamlit/api_keys.json` "
        "(permissions restricted to your user, already excluded from the "
        "repository). They survive restarts and **Clear cache**, below."
    ),
    "api_keys.eodhd_label": "EODHD key",
    "api_keys.td_label": "Twelve Data key",
    "api_keys.save_button": "Save",
    "api_keys.saved_toast": "Keys saved",
    "api_keys.forget_button": "Forget saved keys",
    "api_keys.forgotten_toast": "Keys and related cache removed",

    # --- Sidebar: CSV ---------------------------------------------------------
    "csv.expander": "📄 Upload a series from CSV",
    "csv.caption": (
        "For funds no source covers. Two columns: date and unit value. "
        "Separator, decimal point and date format are detected automatically."
    ),
    "csv.symbol_label": "Symbol or ISIN to associate it with",
    "csv.symbol_placeholder": "e.g. IT0001234567",
    "csv.currency_label": "Series currency",
    "csv.file_label": "CSV file",
    "csv.success": "{n} observations from {inizio} to {fine}.",
    "csv.loaded_caption": "Loaded: {elenco}",
    "csv.remove_button": "Remove loaded series",

    # --- Sidebar: cache, licenses, risk-free ------------------------------------
    "cache.caption": "💾 Disk cache: {n} series, {mb:.1f} MB",
    "cache.clear_button": "Clear cache",
    "cache.cleared_toast": "Cache cleared",
    "sidebar.risk_free_label": "Annual risk-free rate (for Sharpe)",

    # --- Sidebar: about and licenses --------------------------------------
    "about.expander": "ℹ️ About and licenses",
    "about.version": "Fund Comparator version {versione}",
    "about.license_caption": (
        "Source code distributed under the "
        "[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license."
    ),
    "about.third_party_header": "Third-party libraries",
    "about.third_party_caption": (
        "The project uses the libraries listed below, each under its own "
        "license. The full text, including legal notices, is in the "
        "downloadable file."
    ),
    "about.third_party_missing": (
        "License list not available in this installation."
    ),
    "about.download_button": "⬇️ Download third-party licenses (.txt)",
    "about.col_package": "Package",
    "about.col_version": "Version",
    "about.col_license": "License",

    # --- Sidebar: portfolio (export/import) ---------------------------------
    "portfolio_io.expander": "💼 Portfolio: save and load",
    "portfolio_io.caption": (
        "Save the funds, weights and backtest parameters to a file, to "
        "reopen them in another session or on another computer."
    ),
    "portfolio_io.download_button": "⬇️ Download portfolio (.json)",
    "portfolio_io.download_empty_hint": "Add at least one fund to download it.",
    "portfolio_io.upload_label": "Upload a portfolio (.json)",
    "portfolio_io.import_success": "Portfolio loaded: {n} funds.",
    "portfolio_io.import_error": "Invalid file: {errore}",

    # --- Search --------------------------------------------------------------
    "search.expander": "🔎 Search funds and ETFs",
    "search.query_label": "Name, ticker or ISIN",
    "search.query_placeholder": "e.g. 'Vanguard S&P 500', 'VUSA.AS' or 'IE00B3XXRP09'",
    "search.funds_only_toggle": "Funds/ETFs only",
    "search.spinner": "Searching…",
    "search.no_results": "No results. Try the ISIN or the full ticker.",
    "search.isin_hint": (
        "🔗 The ISIN allows using justETF only if you enabled the opt-in "
        "in Data sources, or chose the source for the individual fund."
    ),
    "search.add_button": "Add",

    # --- Toast ------------------------------------------------------------------
    "toast.fund_exists": "{symbol} is already in the portfolio",
    "toast.fund_added": "Added {symbol}",
    "toast.fund_removed": "Removed {elenco}",

    # --- Portfolio composition ---------------------------------------------------
    "portfolio.subheader": "Portfolio composition",
    "portfolio.empty_hint": "Search and add at least one fund to get started.",

    "editor.col_fondo": "Fund",
    "editor.col_simbolo": "Symbol",
    "editor.col_isin": "ISIN",
    "editor.col_valuta": "Currency",
    "editor.col_peso": "Weight %",
    "editor.col_ter": "TER %",
    "editor.col_extra": "Extra costs %",
    "editor.col_fonte": "Source",
    "editor.col_proxy": "History proxy",
    "editor.isin_help": (
        "Needed to use justETF when the source is enabled or "
        "explicitly selected for the fund."
    ),
    "editor.peso_help": "Share of the portfolio assigned to the fund.",
    "editor.ter_help": (
        "Current annual expense. Pre-filled when the source provides it: "
        "always verify against the fund's KID."
    ),
    "editor.extra_help": (
        "Annual costs NOT already included in the NAV (custody, advisory). "
        "Subtracted from performance."
    ),
    "editor.fonte_help": "'Automatic' tries the sources in priority order.",
    "editor.proxy_help": (
        "Older instrument used to reconstruct the period before the "
        "fund's inception."
    ),
    "editor.equalize_button": "⚖️ Equal weights",
    "editor.clear_button": "🗑️ Clear",
    "editor.total_weight_metric": "Total weight",

    # --- TER, weight and date warnings -------------------------------------------------
    "ter_warning.reason_eodhd_blocked": (
        "the configured EODHD plan does not include `/fundamentals` (a paid "
        "plan is required), so neither TER nor classification come from there. "
    ),
    "ter_warning.reason_none": "no configured source exposes it for these instruments. ",
    "ter_warning.message": (
        "TER not found for: {elenco}. {motivo}"
        "Enter it manually from the KID to see the cost impact."
    ),
    "weight.error_zero": "Assign at least one weight greater than zero.",
    "weight.warning_normalized": "Weights add up to {tot:.1f}%: they will be normalized to 100%.",
    "dates.error_order": "The start date must precede the end date.",

    # --- Price retrieval -----------------------------------------------------------
    "prices.spinner": "Downloading historical series…",
    "prices.error_none": "No price data available for the selected funds.",
    "prices.missing_expander": "🚫 {n} funds with no data",
    "prices.missing_hint": (
        "Suggestion: upload a CSV series, or after checking the terms of "
        "service, enable justETF and fill in the ISIN."
    ),

    # --- Currency conversion -------------------------------------------------------
    "fx.error_none": "No series convertible to the reference currency.",
    "fx.error_failed": "Excluded from the backtest (currency not resolvable): {elenco}.",
    "fx.error_failed_eodhd_cause": (
        " The configured EODHD plan does not include `/fundamentals` (a "
        "paid plan is required): if these funds come from an EODHD search, "
        "check whether they also exist on Yahoo under another symbol, or "
        "upload a CSV series indicating the currency yourself."
    ),
    "fx.converted_caption": "💱 Converted to {ccy} at daily exchange rates: {elenco}",
    "fx.truncated_detail_item": "{symbol} from {data}",
    "fx.truncated_warning": (
        "Exchange rates only available from a date later than requested: "
        "{dettaglio}. The period was shortened instead of using a "
        "backfilled rate."
    ),

    # --- Extended history (execution block) ------------------------------------------
    "history.expander": "🧩 Reconstructed history",
    "history.reconstructing_spinner": "Reconstructing {symbol}'s history with {proxy}…",
    "history.proxy_unavailable": "{symbol}: proxy {proxy} not available",
    "history.proxy_not_older": (
        "{symbol}: {proxy} is not older than the fund, nothing to reconstruct"
    ),
    "history.reconstructed_note": "**{symbol}** reconstructed from {data} with {proxy_label}{caveat}",
    "history.reconstructed_caption": (
        "Reconstructed stretches are estimates based on a different "
        "instrument than the fund, not real data. They appear dashed in the charts."
    ),
    "proxy.caveat_price_only": (
        "price-only index: the reconstructed stretch excludes dividends "
        "and underestimates the return"
    ),
    "coverage_warning": "{symbol}: data available only from {data}",

    # --- Backtest results --------------------------------------------------------
    "results.subheader": "Results · {inizio} → {fine}",
    "results.reconstructed_info": (
        "🧩 The metrics above include the reconstructed period "
        "({inizio} → {fine}): they are indicative, not the performance "
        "actually achieved by the funds."
    ),
    "metrics.explainer_expander": "❓ How to read these metrics",
    "costs.impact_info": (
        "💸 **TER impact**: over {anni:.1f} years, current fees cost "
        "**{costo}**, equal to **{pct}** of the amount you would have had "
        "without costs ({lordo} gross vs {netto} net)."
    ),

    # --- Metric help texts ---------------------------------------------------
    "help.valore_finale": (
        "How much the initial {capitale} would have become by the end of "
        "the period, net of the TER."
    ),
    "help.rendimento_totale": (
        "Overall change over the entire period, **not** annualized."
    ),
    "help.cagr": (
        "Compound annual growth rate: the constant rate that, applied "
        "every year, gets from the starting value to the final one in the "
        "same time actually elapsed."
    ),
    "help.volatilita": (
        "Annualized swing of daily returns (standard deviation × √252). "
        "Shows how bumpy the ride was, not how much was gained: two curves "
        "with the same CAGR can have very different volatility."
    ),
    "help.sharpe": (
        "Excess return over the risk-free rate (currently set to "
        "{rf_pct}) per unit of volatility taken on. Above 1 is generally "
        "considered a good result."
    ),
    "help.sortino": (
        "Like Sharpe (risk-free at {rf_pct}), but the denominator only "
        "counts downside swings: it doesn't penalize sharp gains, only drops."
    ),
    "help.max_drawdown": (
        "The worst decline from a previous historical peak to the "
        "following trough: the deepest loss you would have had to endure "
        "while staying invested."
    ),
    "help.calmar": (
        "CAGR divided by the max drawdown in absolute value: return "
        "obtained per unit of maximum loss suffered."
    ),
    "help.miglior_anno": "The best calendar-year return in the period.",
    "help.peggior_anno": "The worst calendar-year return in the period.",
    "help.costo_ter": (
        "Difference, in {ccy}, at the end of the period between the amount "
        "without fees (gross curve) and the one actually obtained (net curve)."
    ),
    "help.ricostruito": (
        "This row includes a stretch estimated with a proxy instrument, "
        "not real fund data: its metrics should be read as indicative."
    ),

    # --- Charts (Portfolio tab) -----------------------------------------------------
    "chart.legend_reconstructed": "Portfolio (reconstructed)",
    "chart.legend_net": "Portfolio (net of TER)",
    "chart.legend_gross": "Portfolio (gross, without TER)",
    "chart.hover_reconstructed_suffix": " (reconstructed)",
    "chart.annotation_real_start": "real data starts",
    "chart.annotation_initial_capital": "initial capital",
    "chart.legend_synthetic": "{comparto} (synthetic)",
    "chart.hover_constant_growth": " · constant growth",
    "chart.yaxis_value": "Value ({ccy})",
    "chart.composition_header": "**Composition over time**",
    "chart.synthetic_caption": (
        "⚠️ Pension fund curves are **constant-growth straight lines**, "
        "derived from COVIP's average annual return: they show where you "
        "would have ended up, not how you got there. The real path "
        "fluctuated, but COVIP does not publish historical series."
    ),
    "chart.weights_set_final": "Target weights: {pesi} → at period end: {pesi_finali}.",
    "chart.rebalance_caption_active": (
        "{tipo} rebalancing: {n} interventions in the period, the last on "
        "{data} (target weights: {pesi})."
    ),
    "chart.rebalance_caption_none_yet": (
        "{tipo} rebalancing: no intervention triggered yet, the chosen "
        "period is shorter than the first due date."
    ),

    # --- Tabs -----------------------------------------------------------------------------
    "tab.portafoglio": "📊 Portfolio",
    "tab.bilanciamento": "⚖️ Breakdown",
    "tab.confronto": "🆚 Fund comparison",
    "tab.drawdown": "📉 Drawdown",
    "tab.dati": "📋 Data",
    "tab.previdenza": "🏦 Pension funds",

    # --- Breakdown tab -----------------------------------------------------------------
    "bilancio.header": "**Classification**",
    "bilancio.col_classe": "Class",
    "bilancio.col_area": "Region",
    "bilancio.col_settore": "Sector",
    "bilancio.col_valuta": "Currency",
    "bilancio.peso_help": "Edited in the composition table, at the top of the page.",
    "bilancio.tendina_help": (
        "**{automatica}** keeps the deduced classification, which can "
        "split across several entries (a global fund isn't entirely one "
        "region). Choosing an entry assigns the whole instrument to it."
    ),
    "bilancio.provenienza_prefix": "🏷️ Classification: ",
    "bilancio.provenienza_eodhd": "**{n}** from EODHD",
    "bilancio.provenienza_yahoo": "**{n}** from Yahoo",
    "bilancio.provenienza_nome": "**{n}** deduced from name",
    "bilancio.provenienza_manuali": "**{n}** with manual corrections",
    "bilancio.titolo_classe": "Asset class",
    "bilancio.titolo_area": "Geographic region",
    "bilancio.titolo_settore": "Sector",
    "bilancio.titolo_valuta": "Listing currency",
    "bilancio.titolo_paesi": "Countries (estimate from top holdings)",
    "bilancio.dettaglio_expander": "🔍 Detail per instrument",
    "bilancio.col_strumento": "Instrument",
    "bilancio.posizioni_expander": "📌 Top holdings",
    "bilancio.posizioni_caption": (
        "The top holdings read from Yahoo for each fund (ETFs and mutual "
        "funds recognized as such): the basis for the geographic estimate "
        "above, also useful for seeing overlaps between different funds."
    ),
    "bilancio.col_titolo": "Holding",
    "bilancio.col_peso_nel_fondo": "Weight in fund",
    "bilancio.posizioni_none": (
        "No holdings available for the funds in the portfolio: this "
        "requires composition data from Yahoo, not always present."
    ),
    "bilancio.esclusi_caption_one": (
        "ℹ️ {elenco}: counted in the breakdown but not in the backtest, due to missing prices."
    ),
    "bilancio.esclusi_caption_many": (
        "ℹ️ {elenco}: counted in the breakdown but not in the backtest, due to missing prices."
    ),
    "bilancio.disclaimer": (
        "⚠️ Automatic classification is **indicative** and should be "
        "verified against the KID: without EODHD (with a key) and without "
        "composition data from Yahoo it is deduced from the fund's name, "
        "which is often not enough. The **Countries** donut is an estimate "
        "based only on the top holdings read from Yahoo (typically a "
        "fifth or a quarter of the fund): the full geographic breakdown "
        "requires a paid EODHD plan. The **currency** is the listing "
        "currency, not the currency exposure: a world-market ETF listed "
        "in euros remains exposed to the dollar."
    ),

    # --- Fund comparison tab -----------------------------------------------------------------
    "confronto.caption": (
        "Trajectory of {capitale} invested entirely in each fund, for a "
        "comparison at equal capital."
    ),
    "confronto.legend_reconstructed": "{col} (reconstructed)",
    "confronto.legend_gross": "{col} (gross)",
    "confronto.col_valore_finale": "Final value (from {capitale})",
    "confronto.stesso_capitale_caption": (
        "Every row starts from the same capital: **{capitale}** invested "
        "100% in a single fund, and the same **{capitale}** invested in "
        "the portfolio with the set weights and chosen rebalancing. Final "
        "values are therefore directly comparable row by row."
    ),
    "confronto.footnote": (
        "The *Reconstructed* column flags rows whose metrics include a "
        "period estimated by a proxy."
    ),
    "confronto.riga_portafoglio": "🎯 PORTFOLIO",
    "si": "yes",
    "no": "no",
    "nd": "n/a",

    # --- Drawdown tab -----------------------------------------------------------------------
    "drawdown.legend_portafoglio": "Portfolio",
    "drawdown.yaxis": "Drawdown (%)",
    "drawdown.yearly_header": "**Calendar-year returns**",
    "drawdown.yaxis_yearly": "Return (%)",

    # --- Data tab -----------------------------------------------------------------------------
    "dati.col_netto": "Portfolio (net)",
    "dati.col_lordo": "Portfolio (gross)",
    "dati.col_solo_prefix": "Only ",
    "dati.download_button": "⬇️ Download full CSV",

    # --- Pension funds tab -----------------------------------------------------------------
    "previdenza.header_con_anno": "### Complementary pensions · COVIP data as of 12/31/{anno}",
    "previdenza.header_senza_anno": "### Complementary pensions · COVIP data",
    "previdenza.fiscalita_warning": (
        "**The comparison does not account for taxation.** Pension funds "
        "enjoy tax deductibility up to €5,164.57 per year, 20% tax on "
        "returns instead of 26%, and a final tax rate that drops from 15% "
        "to 9%. These are advantages in their favor, so the figures below "
        "**underestimate** them."
    ),
    "previdenza.rendimenti_caption": (
        "COVIP only publishes average annual returns over fixed horizons, "
        "not historical series: for these instruments, volatility, "
        "drawdown and Sharpe cannot be computed from any public data. To "
        "get them, upload your fund's unit value with the CSV uploader in "
        "the sidebar."
    ),
    "previdenza.catalogo_error": (
        "COVIP catalog not available: check your connection and try again."
    ),
    "previdenza.forma_label": "Pension scheme type",
    "previdenza.col_tipo": "Type",
    "previdenza.riga_portafoglio": "🎯 YOUR PORTFOLIO",
    "previdenza.categoria_label": "Category",
    "previdenza.cerca_label": "Search by fund or company name",
    "previdenza.cerca_placeholder": "e.g. 'previgest', 'cometa', 'mediolanum'",
    "previdenza.risultati_caption": "{n} sub-funds match the filters.",
    "previdenza.comparti_label": "Sub-funds to compare",
    "previdenza.seleziona_hint": (
        "Select one or more sub-funds to compare them with your portfolio."
    ),
    "previdenza.rendimento_header": "**Average annual return, on the same COVIP windows**",
    "previdenza.col_help_orizzonte": (
        "COVIP average annual return over the {anni}-year window ({periodo})."
    ),
    "previdenza.col_isc": "ISC 10y",
    "previdenza.col_help_isc": (
        "The pension-fund equivalent of the TER: annual cost impact over "
        "the 10-year horizon."
    ),
    "previdenza.mancanti_caption": (
        "Your portfolio shows **n/a** for {elenco_anni} because it doesn't "
        "cover the full window ({dettaglio}). Computing it over a shorter "
        "period would give a non-comparable figure."
    ),
    "previdenza.anni_suffix": "{a} years",
    "previdenza.il_tuo_portafoglio": "Your portfolio",
    "previdenza.yaxis_rendimento": "Average annual return (%)",
    "previdenza.costi_header": "**How much costs weigh**",
    "previdenza.col_comparto": "Sub-fund",
    "previdenza.col_isc_annuo": "Annual ISC",
    "previdenza.col_rendimento_10a": "10y return",
    "previdenza.col_eroso": "Eroded on {capitale} over 10 years",
    "previdenza.col_quota_rendimento": "Share of return",
    "previdenza.costi_caption": (
        "The ISC is the pension-fund equivalent of the TER. The last "
        "column shows what fraction of the net return obtained is "
        "absorbed by costs each year."
    ),
    "previdenza.curve_checkbox": "Show pension fund curves in the portfolio chart",
    "previdenza.curve_help": (
        "Constant-growth straight lines derived from the average annual "
        "return: they show the endpoint, not the path."
    ),
    "previdenza.orizzonte_label": "Horizon to derive the rate from",
    "previdenza.fonte_caption": (
        "Source: [COVIP](https://www.covip.it/open-data), open data under "
        "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license. "
        "The project normalizes and aggregates the datasets and computes "
        "comparisons and synthetic curves; these elaborations are not "
        "original COVIP data."
    ),

    # --- Footer --------------------------------------------------------------------------
    "footer.disclaimer": (
        "*Total return* prices (dividends reinvested). Fund NAVs are "
        "already net of the TER; the gross curve is a theoretical "
        "reconstruction. Exchange rates are the official ECB rates from "
        "1999, obtained via Frankfurter, with a fallback to Yahoo for "
        "currencies outside the basket. Entry/exit costs, spreads and "
        "taxation are not considered. Past performance is not indicative "
        "of future results."
    ),
}

METRICHE: dict[str, str] = {
    "final_value": "Final value",
    "total_return": "Total return",
    "cagr": "CAGR",
    "volatility": "Volatility",
    "sharpe": "Sharpe",
    "sortino": "Sortino",
    "max_drawdown": "Max drawdown",
    "calmar": "Calmar",
    "best_year": "Best year",
    "worst_year": "Worst year",
    "ter_cost": "TER cost",
    "reconstructed": "Reconstructed",
}

ESITI: dict[str, str] = {
    "ok": "ok",
    "no_data": "no data",
    "not_configured": "not configured",
    "isin_required": "ISIN required",
}

TERMINI: dict[str, str] = {
    "Azionario": "Equity",
    "Obbligazionario": "Bonds",
    "Liquidità": "Cash",
    "Materie prime": "Commodities",
    "Immobiliare": "Real estate",
    "Non classificato": "Unclassified",
    "Globale": "Global",
    "Nord America": "North America",
    "Europa": "Europe",
    "Italia": "Italy",
    "Giappone": "Japan",
    "Asia-Pacifico": "Asia-Pacific",
    "Mercati emergenti": "Emerging markets",
    "Diversificato": "Diversified",
    "Tecnologia": "Technology",
    "Finanza": "Financials",
    "Sanità": "Healthcare",
    "Energia": "Energy",
    "Industria": "Industrials",
    "Beni di consumo": "Consumer goods",
    "Utility": "Utilities",
    "Materiali": "Materials",
    "Comunicazioni": "Communications",
    "Resto del fondo": "Rest of fund",
    "(automatica)": "(automatic)",
    "(nessuno)": "(none)",
    "Taiwan": "Taiwan",
    "Hong Kong": "Hong Kong",
    "Corea del Sud": "South Korea",
    "India": "India",
    "Regno Unito": "United Kingdom",
    "Svizzera": "Switzerland",
    "Australia": "Australia",
    "Paesi Bassi": "Netherlands",
    "Germania": "Germany",
    "Spagna": "Spain",
    "Francia": "France",
    "Canada": "Canada",
    "Cina": "China",
    "Danimarca": "Denmark",
    "Svezia": "Sweden",
    "Norvegia": "Norway",
    "Brasile": "Brazil",
    "Messico": "Mexico",
    "Stati Uniti": "United States",
}

FONTI: dict[str, str] = {
    "auto": "Automatic",
    "yahoo": "Yahoo Finance",
    "justetf": "justETF",
    "eodhd": "EODHD",
    "twelvedata": "Twelve Data",
    "csv": "Uploaded CSV",
    "openfigi": "OpenFIGI",
    "nome": "Deduced from name",
}

RIBILANCIAMENTO: dict[str, str] = {
    "none": "None (buy & hold)",
    "monthly": "Monthly",
    "quarterly": "Quarterly",
    "yearly": "Yearly",
}
