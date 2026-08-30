# ruff: noqa: E501

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

    # --- Sidebar: PAC (recurring contributions) ---------------------------
    "pac.rebalance_caption": (
        "A recurring contribution goes in at the target weights: it's a "
        "soft rebalance, so with \"None\" the portfolio drifts less than it "
        "would without a PAC."
    ),
    "pac.expander": "📅 Recurring contributions (PAC)",
    "pac.enable_checkbox": "Enable the contribution plan",
    "pac.help": (
        "Adds recurring contributions on top of the initial capital. With "
        "the PAC on, the instrument's return (CAGR, Sharpe, drawdown, ...) "
        "still excludes the contributions; XIRR instead measures the "
        "return on your money, contributions included."
    ),
    "pac.amount_label": "Amount per instalment",
    "pac.amount_help": "The instalment paid at each due date, in the base currency.",
    "pac.frequency_label": "Frequency",
    "pac.step_up_label": "Annual instalment increase (%)",
    "pac.step_up_help": (
        "Increases the instalment by this percentage once a year, e.g. to "
        "track inflation or salary growth."
    ),
    "pac.limit_window_checkbox": "Limit contributions to a period",
    "pac.start_label": "First instalment",
    "pac.end_label": "Last instalment",

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
        "providers' rights. Consent is remembered on this computer until "
        "you revoke it; leaving the checkbox off, justETF will only be "
        "contacted if you "
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
    "api_keys.saved_caption": "Saved keys: {elenco}",
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
    "sidebar.risk_free_label": "Annual risk-free rate % (for Sharpe)",

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
    "about.credit": "Made with curiosity by [Giulio](https://www.gshake.net)",

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

    "editor.col_rimuovi": "Remove",
    "editor.col_fondo": "Fund",
    "editor.col_simbolo": "Symbol",
    "editor.col_isin": "ISIN",
    "editor.col_valuta": "Currency",
    "editor.col_distribuzione": "Distribution",
    "editor.col_replica": "Replication",
    "editor.col_peso": "Weight %",
    "editor.col_importo": "Amount ({ccy})",
    "editor.col_ter": "TER %",
    "editor.col_extra": "Extra costs %",
    "editor.col_fonte": "Source",
    "editor.col_proxy": "History proxy",
    "metadata.distribution_accumulating": "Accumulating",
    "metadata.distribution_distributing": "Distributing",
    "metadata.replication_physical": "Physical",
    "metadata.replication_synthetic": "Synthetic",
    "editor.rimuovi_help": (
        "Removes the fund from the portfolio and redistributes its weight to the "
        "others, keeping their proportions."
    ),
    "editor.isin_help": (
        "Needed to use justETF when the source is enabled or "
        "explicitly selected for the fund."
    ),
    "editor.peso_help": (
        "Share of the portfolio assigned to the fund. Changing it adjusts the "
        "other weights automatically, in proportion to each other, so the total "
        "stays at 100%."
    ),
    "editor.importo_help": (
        "Capital assigned to the fund in this currency. Changing it updates the "
        "weights and the portfolio's initial value."
    ),
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
    "editor.total_value_metric": "Invested capital",

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
    "weight.error_importo_min": "The portfolio's total capital cannot fall below {minimo}.",
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
    "history.reconstructed_note": (
        "**{symbol}** reconstructed from {data} with {proxy_label}{caveat}"
    ),
    "history.reconstructed_caption": (
        "Reconstructed stretches are estimates based on a different "
        "instrument than the fund, not real data. They appear dashed in the charts."
    ),
    "proxy.caveat_price_only": (
        "price-only index: the reconstructed stretch excludes dividends "
        "and underestimates the return"
    ),
    "coverage_warning": "{symbol}: data available only from {data}",

    # --- Backtest integrity -----------------------------------------------------
    "engine.error_quote_non_valide": (
        "Invalid quotes (zero, negative, or non-finite) for: {elenco}."
    ),
    "engine.error_date_duplicate": "Duplicate dates in the price history for: {elenco}.",
    "engine.error_simboli_duplicati": "Duplicate symbols in the portfolio: {elenco}.",
    "engine.error_simboli_senza_prezzi": "No price data available for: {elenco}.",
    "engine.error_pesi_non_validi": "Invalid weight for: {elenco}.",
    "integrita.error_fondi_assenti": (
        "🚫 The backtest can't run: no price data for {elenco}. A temporary "
        "issue with the source would otherwise change the allocation "
        "actually simulated without you choosing it."
    ),
    "integrita.allocazione_reale": (
        "Removing these funds, the portfolio would become: {elenco}."
    ),
    "integrita.button_rimuovi": "Remove the funds with no data and continue",

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
    "help.pac_saldo": (
        "What the portfolio is worth at the end, contributions included: "
        "the sum of what you paid in and the gain."
    ),
    "help.pac_versato": "Initial capital plus every contribution made so far.",
    "help.pac_guadagno": "Final portfolio value minus the total amount contributed.",
    "help.pac_xirr": (
        "Annual return on your money (XIRR): unlike CAGR, it accounts for "
        "when each contribution came in, not just the initial capital."
    ),

    # --- Charts (Portfolio tab) -----------------------------------------------------
    "chart.legend_reconstructed": "Portfolio (reconstructed)",
    "chart.legend_net": "Portfolio (net of TER)",
    "chart.legend_gross": "Portfolio (gross, without TER)",
    "chart.hover_reconstructed_suffix": " (reconstructed)",
    "chart.annotation_real_start": "real data starts",
    "chart.annotation_initial_capital": "initial capital",
    "chart.legend_invested": "Cumulative amount invested",
    "chart.legend_pic": "Lump sum (all at once)",
    "chart.pic_caption": (
        "The **lump sum** line shows how it would have gone paying in, on day "
        "one and in a single go, the same total the plan pays in over time "
        "({totale}): **{valore_pic}** against **{valore_pac}** for the plan. "
        "It is a hypothetical comparison: it assumes you had the whole sum "
        "available straight away."
    ),
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

    "bilancio.overlap_expander": "🔗 Holdings overlap",
    "bilancio.overlap_caption": (
        "Overlap sums only recognized positions: with partial coverage it is a "
        "lower bound and the unknown portion remains explicit."
    ),
    "bilancio.overlap_fund": "Fund",
    "bilancio.overlap_coverage": "Known coverage",
    "bilancio.overlap_source": "Holdings source",
    "bilancio.overlap_date": "Date",
    "bilancio.overlap_note": "Note",
    "bilancio.overlap_unknown_date": "date not exposed",
    "bilancio.overlap_stale": "stale data",
    "bilancio.overlap_ambiguous": "{n} ambiguous identities",
    "bilancio.overlap_unavailable": "insufficient data",
    "bilancio.overlap_ok": "available",
    "bilancio.overlap_matrix_header": "**Matrix: observed overlap (lower bound)**",
    "bilancio.overlap_lower_bound": "lower bound, not complete overlap",
    "bilancio.overlap_pair": "Pair",
    "bilancio.overlap_value": "Observed overlap",
    "bilancio.overlap_pair_coverage": "Coverage",
    "bilancio.overlap_exposure_header": "**Aggregated exposure to known holdings**",
    "bilancio.overlap_position": "Holding",
    "bilancio.overlap_portfolio_weight": "Portfolio weight",
    "bilancio.overlap_unknown": "Total uncovered portion: **{quota}**.",

    "profile.expander": "🧭 Personal profile (local only)",
    "profile.caption": "Optional: it separates observed facts from declared preferences.",
    "profile.horizon_label": "Time horizon",
    "profile.objective_label": "Objective",
    "profile.loss_enable": "Declare a maximum temporary loss",
    "profile.loss_label": "Maximum tolerated loss (%)",
    "profile.withdrawals_label": "Planned withdrawals",
    "profile.limit_enable": "Declare a limit for one position",
    "profile.limit_label": "Position limit (%)",
    "profile.preference_label": "Preference",
    "profile.bonds_label": "Bonds allowed",
    "profile.excluded_classes_label": "Excluded classes",
    "profile.excluded_sectors_label": "Excluded sectors",
    "profile.save_button": "Save local profile",
    "profile.saved_toast": "Profile saved only on this device.",
    "profile.invalid": "Profile not saved: {errore}",
    "profile.not_set": "Not set",
    "profile.years": "{n} years",
    "profile.yes": "Yes",
    "profile.no": "No",
    "profile.objective_growth": "Growth",
    "profile.objective_income": "Income",
    "profile.objective_preservation": "Preservation",
    "profile.preference_simplicity": "Simplicity",
    "profile.preference_balanced": "Balance",
    "profile.preference_diversification": "Diversification",
    "profile.class_equity": "Equity",
    "profile.class_bond": "Bonds",
    "profile.class_cash": "Cash",
    "profile.class_commodities": "Commodities",
    "profile.class_real_estate": "Real estate",
    "profile.sector_technology": "Technology",
    "profile.sector_finance": "Finance",
    "profile.sector_health": "Healthcare",
    "profile.sector_energy": "Energy",
    "profile.sector_industry": "Industrials",
    "profile.sector_consumer": "Consumer goods",
    "profile.sector_utilities": "Utilities",
    "profile.sector_real_estate": "Real estate",
    "profile.sector_materials": "Materials",
    "profile.sector_communication": "Communication",
    "tab.diagnosi": "🧭 Diagnosis",
    "tab.analisi": "📊 Analysis",
    "diagnostic.header": "**Local deterministic diagnosis**",
    "diagnostic.no_profile": "No personal profile: missing fields are {campi}.",
    "diagnostic.warning": "Warning against profile",
    "diagnostic.info": "Information",
    "diagnostic.portfolio": "Portfolio",
    "diagnostic.no_evidence": "No numeric evidence",
    "diagnostic.severity_column": "Type",
    "diagnostic.finding_column": "Finding",
    "diagnostic.asset_column": "Instrument",
    "diagnostic.evidence_column": "Evidence",
    "diagnostic.payload_header": "**Anonymous payload preview**",
    "diagnostic.payload_caption": (
        "This is the complete form that could be shared in the future; "
        "it is not sent here."
    ),
    "diagnostic.generic": "Report fact",
    "diagnostic.profile_missing": "Profile not filled: no personal threshold applied.",
    "diagnostic.weight_observation": "Observed portfolio weight.",
    "diagnostic.ter_missing": "TER is unavailable for this instrument.",
    "diagnostic.ter_observation": "TER and its source are available for this instrument.",
    "diagnostic.drawdown_observation": "Observed historical maximum drawdown.",
    "diagnostic.holdings_missing": "Underlying holdings are unavailable.",
    "diagnostic.position_limit_exceeded": "The weight exceeds the declared limit.",
    "diagnostic.drawdown_exceeds_tolerance": "Historical drawdown exceeds tolerated loss.",
    "diagnostic.history_shorter_than_horizon": "Observed history is shorter than the horizon.",
    "diagnostic.excluded_exposure": "Exposure to an excluded class or sector.",
    "diagnostic.bonds_not_allowed": "The profile does not allow bonds.",
    "diagnostic.correlation_observation": "Historical correlations are available.",
    "diagnostic.rolling_observation": "Historical rolling returns are available.",
    "diagnostic.benchmark_observation": "A historical benchmark comparison is available.",
    "diagnostic.inflation_observation": "Historical inflation data are available.",
    "diagnostic.overlap_observation": "Historical holdings-overlap analysis is available.",

    # --- Fund comparison tab -----------------------------------------------------------------
    "confronto.caption": (
        "Trajectory of {capitale} invested entirely in each fund, for a "
        "comparison at equal capital."
    ),
    "confronto.caption_pac": (
        "How {capitale} invested entirely in each fund would have gone, with "
        "the same contribution plan as the portfolio: the comparison stays "
        "like for like on both capital and instalments."
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
    "confronto.col_valore_finale_pac": "Final value (from {capitale} + contributions)",
    "confronto.stesso_capitale_caption_pac": (
        "Every row receives the same initial capital (**{capitale}**) and the "
        "same contribution plan. *Final value* is the actual balance at the "
        "end, contributions included, and *XIRR* is the return on your money, "
        "which accounts for when each instalment went in. Every other metric "
        "is computed **net of the contributions**: a contribution is not a "
        "market gain."
    ),
    "confronto.footnote": (
        "The *Reconstructed* column flags rows whose metrics include a "
        "period estimated by a proxy."
    ),
    "confronto.riga_portafoglio": "🎯 PORTFOLIO",
    "si": "yes",
    "no": "no",
    "nd": "n/a",
    "benchmark.expander": "🎯 Benchmark and comparative analysis",
    "benchmark.label": "Reference",
    "benchmark.option_none": "None",
    "benchmark.option_VT": "Global equities (VT, total return)",
    "benchmark.option_VFINX": "S&P 500 (VFINX, total return)",
    "benchmark.option_custom": "Search for an instrument",
    "benchmark.famous_open_button": "Open famous portfolios",
    "benchmark.search_label": "Search benchmark",
    "benchmark.search_placeholder": "Symbol, name or ISIN",
    "benchmark.selected": "Selected benchmark: **{symbol}**",
    "benchmark.remove_button": "Remove benchmark",
    "benchmark.failed": "Benchmark unavailable: {errore}",
    "benchmark.source": "Benchmark source: {source} · quote: {symbol}",
    "benchmark.attempts": "Resolution attempts: {elenco}",
    "benchmark.legend": "Benchmark {symbol}",
    "benchmark.metrics_header": "Comparison on the common period",
    "benchmark.metric": "Series",
    "benchmark.portfolio_label": "Your portfolio",
    "benchmark.growth": "Total return",
    "benchmark.cagr": "CAGR",
    "benchmark.volatility": "Volatility",
    "benchmark.max_drawdown": "Max drawdown",
    "benchmark.active_return": "Active return",
    "benchmark.tracking_error": "Tracking error",
    "benchmark.information_ratio": "Information ratio",
    "benchmark.common_period": "Common period: {start} → {end} · {n} monthly observations",
    "benchmark.common_period_short": "the common period has fewer than two observations",
    "benchmark.metric_reason": "Note: {motivo}.",
    "benchmark.reason_common_empty": "the common period is empty",
    "benchmark.reason_insufficient": "the monthly sample is insufficient",
    "benchmark.reason_tracking_error_zero": "tracking error is zero",
    "benchmark.reason_generic": "the metric cannot be calculated",
    "benchmark.correlation_header": "Monthly-return correlations",
    "benchmark.correlation_portfolio_header": "Correlations between portfolio and instruments",
    "benchmark.rolling_header": "Annualised rolling returns",
    "benchmark.rolling_period": "Window",
    "benchmark.rolling_worst": "Worst",
    "benchmark.rolling_median": "Median",
    "benchmark.rolling_best": "Best",
    "benchmark.rolling_positive": "Positive windows",
    "benchmark.rolling_observations": "Observations",
    "benchmark.years": "{n} years",
    "analysis.caption": "Historical analysis of the portfolio, benchmarks and selected instruments.",
    "analysis.portfolio": "Portfolio",
    "analysis.benchmark": "Benchmark",
    "analysis.mode_label": "View",
    "analysis.mode_heatmap": "Return heatmap",
    "analysis.mode_rolling": "Rolling returns",
    "analysis.mode_frontier": "Efficient frontier",
    "analysis.series_label": "Series",
    "analysis.show_all": "Show all years",
    "analysis.heatmap_header": "Monthly returns by year",
    "analysis.reconstruction_base": "Reconstruction base: {capitale} from {data}; the contribution plan follows the configured dates.",
    "analysis.proxy_note": "Series reconstructed with a proxy are flagged in the coverage; proxies are not used when the option is off.",
    "analysis.source_note": "Data source for the series: {elenco}. Different sources can produce different returns; select the same source in the composition for an apples-to-apples comparison.",
    "analysis.source_item": "{serie} → {fonte}",
    "analysis.heatmap_annual": "Year",
    "analysis.heatmap_partial": "Partial period",
    "analysis.heatmap_tooltip": "The cell uses the available month-end quote; — means missing data.",
    "analysis.heatmap_effective": "Last quote: {data}{parziale}",
    "analysis.heatmap_effective_year": "Compounded return {year}",
    "analysis.heatmap_partial_cell": " (partial)",
    "analysis.heatmap_ytd": "YTD",
    "analysis.heatmap_unavailable": "Heatmap unavailable: insufficient historical data.",
    "analysis.missing_cell": "—",
    "analysis.partial_series": "Some series or windows are unavailable because the required history is insufficient.",
    "analysis.month_1": "Jan", "analysis.month_2": "Feb", "analysis.month_3": "Mar",
    "analysis.month_4": "Apr", "analysis.month_5": "May", "analysis.month_6": "Jun",
    "analysis.month_7": "Jul", "analysis.month_8": "Aug", "analysis.month_9": "Sep",
    "analysis.month_10": "Oct", "analysis.month_11": "Nov", "analysis.month_12": "Dec",
    "analysis.mode_continuous": "Continuous",
    "analysis.mode_annual": "Annual",
    "analysis.mode_distribution": "Distribution",
    "analysis.metric_label": "Metric",
    "analysis.horizon_label": "Window",
    "analysis.rolling_header": "Rolling returns",
    "analysis.rolling_coverage": "Coverage: {start} → {end} · {n} observations",
    "analysis.rolling_common_coverage": "Common comparison period: {start} → {end}.",
    "analysis.rolling_distribution_note": "Windows overlap and are not independent observations.",
    "analysis.summary_p05": "5th percentile",
    "analysis.summary_p95": "95th percentile",
    "analysis.frontier_header": "Simulated historical frontier",
    "analysis.frontier_caption": "These are the best mixes found in the history, not a forecast or a future guarantee.",
    "analysis.frontier_samples": "Samples",
    "analysis.frontier_constraints": "Weight constraints",
    "analysis.frontier_min_weight": "Min %",
    "analysis.frontier_max_weight": "Max %",
    "analysis.frontier_run": "Calculate frontier",
    "analysis.frontier_running": "Simulation in progress…",
    "analysis.frontier_symbol": "Symbol",
    "analysis.frontier_current": "Current portfolio",
    "analysis.frontier_pareto": "Non-dominated mixes",
    "analysis.frontier_metric": "Metric",
    "analysis.frontier_min": "Minimum",
    "analysis.frontier_max": "Maximum",
    "analysis.frontier_axis_x": "X axis",
    "analysis.frontier_axis_y": "Y axis",
    "analysis.frontier_selected": "Selected mix",
    "analysis.frontier_mix": "Mix {id}",
    "analysis.frontier_weights": "Mix weights",
    "analysis.frontier_difference": "Difference from current portfolio",
    "analysis.frontier_apply": "Apply these weights",
    "analysis.frontier_apply_confirm": "I confirm that I want to change the portfolio weights",
    "analysis.frontier_export": "Export JSON variant",
    "analysis.frontier_stale": "Result cannot be applied: data, weights or parameters changed.",
    "analysis.frontier_no_data": "At least two valid historical series are required for the frontier.",
    "analysis.frontier_single": "The constraints leave a single possible allocation; no frontier is constructed.",
    "analysis.frontier_invalid": "Invalid constraints: minimums must total ≤ 100% and maximums ≥ 100%.",
    "analysis.frontier_not_available": "Frontier unavailable: {errore}",
    "analysis.frontier_disclaimer": "Drawdown is shown as a positive maximum loss; calculations are nominal and net.",
    "analysis.frontier_evaluations": "Allocations evaluated: {n}",
    "analysis.frontier_coverage": "Frontier history: {start} → {end} · {n} observations, matching the backtest.",
    "analysis.frontier_max_sharpe": "Maximum Sharpe",
    "analysis.frontier_min_sharpe": "Minimum Sharpe",
    "analysis.frontier_min_volatility": "Minimum volatility",
    "analysis.frontier_max_volatility": "Maximum volatility",
    "analysis.frontier_max_return": "Maximum return",
    "analysis.frontier_min_return": "Minimum return",
    "analysis.frontier_min_drawdown": "Minimum drawdown",
    "analysis.frontier_max_drawdown": "Maximum drawdown",
    "analysis.frontier_extreme_tooltip": "{tipo} · {mix}<br>Weights: {pesi}<br>{metriche}",
    "analysis.frontier_extreme_markers": "Stars mark the best cases and X markers the worst for each metric; hover over a point to see weights and values.",
    "inflation.expander": "📉 Real return and inflation",
    "inflation.enable_checkbox": "Show values after inflation",
    "inflation.enable_help": "Uses the official monthly Eurostat HICP index.",
    "inflation.area_label": "Purchasing-power area",
    "inflation.area_it": "Italy",
    "inflation.area_ea": "Euro area",
    "inflation.retry_button": "Retry Eurostat",
    "inflation.real_curve": "Portfolio in real purchasing power",
    "inflation.metrics_header": "Nominal and real comparison",
    "inflation.metric_kind": "Values",
    "inflation.metric_total_return": "Total return",
    "inflation.metric_cagr": "CAGR",
    "inflation.metric_final": "Final value",
    "inflation.nominal": "Nominal",
    "inflation.real": "Real",
    "inflation.coverage_caption": "Source: {source} · area: {area} · coverage: {first} → {last}",
    "inflation.pac_caption": "PAC paid in: {nominal} nominal · {real} at initial purchasing power.",
    "inflation.failed": "Real analysis unavailable: {errore}",
    "inflation.coverage_missing": "The HICP index does not cover the portfolio period.",
    "inflation.stale_caption": "Eurostat did not respond: cached data that may be stale are shown.",

    # --- Drawdown tab -----------------------------------------------------------------------
    "drawdown.legend_portafoglio": "Portfolio",
    "drawdown.yaxis": "Drawdown (%)",
    "drawdown.pac_caption": (
        "With the plan active, drawdown and yearly returns are computed net of "
        "the contributions: otherwise every instalment would show up as a "
        "market gain and the falls would look milder than they were."
    ),
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
    "previdenza.pac_caption": (
        "**With the plan active**, on this tab: the scheme curves on the "
        "portfolio chart receive the same contribution plan; your portfolio's "
        "return is the one net of contributions, because that is how COVIP "
        "computes its own; cost erosion and the projected balance use your "
        "instalment for ten years, held **constant** — the annual increase "
        "does not enter this projection."
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
    "previdenza.col_orizzonte": "{etichetta} · {periodo}",
    "previdenza.legenda_caption": (
        "Each column is a closed window of its own, not a cumulative period: "
        "the dates are in the header. A 10-year figure lower than the 5-year "
        "one means the first half of the decade returned less, not that the "
        "fund has got worse lately. **ISC 10a** is the synthetic cost "
        "indicator, the pension equivalent of the TER: how much costs weigh on "
        "average each year over a ten-year horizon."
    ),
    "previdenza.portafoglio_periodo_proprio": (
        "Your backtest covers **{inizio} → {fine}** ({anni} years) and returned "
        "**{rendimento}** a year: a number that is not comparable with the "
        "columns above. COVIP windows are **whole calendar years**, 1 January "
        "to 31 December: a period starting or ending mid-year does not cover "
        "them, even when the calendar years look the same."
    ),
    "previdenza.allinea_button": "📐 Set the period to {inizio} → {fine}",
    "previdenza.allinea_caption": (
        "Changes the backtest dates to cover the COVIP windows. The backtest "
        "still starts on the first date where **every** selected fund has "
        "data: the longer windows stay **n/d** if one fund is more recent."
    ),
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
    "previdenza.anno_suffix": "{a} year",
    "previdenza.anni_suffix": "{a} years",
    "previdenza.il_tuo_portafoglio": "Your portfolio",
    "previdenza.yaxis_rendimento": "Average annual return (%)",
    "previdenza.costi_header": "**How much costs weigh**",
    "previdenza.col_comparto": "Sub-fund",
    "previdenza.col_isc_annuo": "Annual ISC",
    "previdenza.col_rendimento_10a": "10y return",
    "previdenza.col_eroso": "Eroded on {capitale} over 10 years",
    "previdenza.col_eroso_pac": "Eroded on {capitale} paid in over 10 years",
    "previdenza.col_quota_rendimento": "Share of return",
    "previdenza.col_montante_pac_10a": "Projected amount (PAC, 10y)",
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

    "directa.expander": "Import Directa portfolio",
    "directa.caption": "Upload CSV/XLSX, map the columns and review the preview before importing.",
    "directa.upload_label": "File exported from Directa",
    "directa.sheet_label": "Sheet",
    "directa.header_row_label": "Header row (0 = first row)",
    "directa.header_row_help": "If descriptive rows precede the table, select the header row here.",
    "directa.file_error": "Directa file could not be read: {errore}",
    "directa.movements_file": (
        "This is a movements export, not a positions export: it contains "
        "trades and fees but no current market value. To import the portfolio, "
        "use Directa's positions/portfolio export."
    ),
    "directa.no_column": "(none)",
    "directa.value_column": "Current value column",
    "directa.isin_column": "ISIN column",
    "directa.ticker_column": "Ticker column",
    "directa.name_column": "Name column",
    "directa.currency_column": "Currency column (optional)",
    "directa.quantity_column": "Quantity column (optional)",
    "directa.average_column": "Average cost column (optional)",
    "directa.preview_identifier": "Identifier",
    "directa.preview_name": "Name",
    "directa.preview_value": "Current value",
    "directa.issue_row": "Row",
    "directa.issue_column": "Column",
    "directa.issue_message": "Problem",
    "directa.issue_invalid_isin": "Invalid ISIN.",
    "directa.issue_missing_identifier": "ISIN or ticker is missing.",
    "directa.issue_summary_row": "Summary row without an instrument: exclude it from the import.",
    "directa.issue_invalid_value": "Current value must be positive.",
    "directa.issue_invalid_quantity": "Quantity must be positive.",
    "directa.issue_invalid_average": "Average loading price must be positive.",
    "directa.value_currency": "Value currency",
    "directa.mapping_error": "Incomplete mapping: {errore}",
    "directa.issues": "{n} rows cannot be imported",
    "directa.instrument_label": "Listing for {nome}",
    "directa.exclude_unresolved": "Explicitly exclude rows that cannot be imported",
    "directa.unresolved": "Without a listing or unsupported: {elenco}",
    "directa.import_button": "Import resolved positions",
    "directa.import_success": "Imported {n} Directa positions",
    "costs.pic_expander": "PIC entry and exit costs",
    "costs.pic_caption": "Separate estimate: the backtest and its metrics do not change.",
    "costs.pic_enable": "Calculate the PIC cost estimate",
    "costs.mode_label": "Cost type",
    "costs.mode_none": "No cost",
    "costs.mode_fixed": "Fixed amount per order",
    "costs.mode_percentage": "Percentage per order",
    "costs.fixed_label": "Fixed amount",
    "costs.rate_label": "Percentage %",
    "costs.minimum_label": "Minimum",
    "costs.maximum_label": "Maximum (0 = no limit)",
    "costs.maximum_help": "Zero means no maximum cap is applied.",
    "costs.buy_title": "Entry",
    "costs.sell_title": "Exit",
    "costs.pic_error": "PIC costs could not be calculated: {errore}",
    "costs.pic_result_expander": "Estimated impact of PIC commissions",
    "costs.pic_result_caption": (
        "Entry costs are reserved inside the budget; exit costs are "
        "calculated per fund's final value."
    ),
    "costs.pic_budget": "Budget",
    "costs.pic_buy_total": "Total entry",
    "costs.pic_sell_total": "Total exit",
    "costs.pic_net_final": "Net amount",
    "costs.pic_line_investable": "Actually invested",
    "costs.pic_line_before_sell": "Amount before exit",
    "costs.pic_line_without": "Amount without costs",
    "costs.pic_line_difference": "Total difference",
    "costs.pic_column_item": "Item",
    "costs.pic_column_value": "Value",
    "costs.pic_column_side": "Operation",
    "costs.pic_column_symbol": "Symbol",
    "costs.pic_column_notional": "Order value",
    "costs.pic_column_fee": "Fee",
    "ter_warning.retry_button": "Retry TER retrieval",
    "ter_warning.attempts": "{symbol}: {esiti}",
    "ter_warning.sources": "TER source: {elenco}",
    "search.info_button": "Details",
    "editor.col_scheda": "Details",
    "editor.scheda_help": "Show descriptive data, sources, and conflicts for the instrument.",
    "instrument.title": "Instrument information",
    "instrument.loading": "Retrieving instrument data…",
    "instrument.not_available": "Not available",
    "instrument.date_not_available": "date not available",
    "instrument.date_placeholder": "YYYY-MM-DD",
    "instrument.fact_provenance": "Source: {source} · observed: {observed} · quality: {quality}",
    "instrument.fact_conflict_entry": "{source}: {value} · observed: {observed}",
    "instrument.quality_reported": "reported by source",
    "instrument.quality_document": "verified in document",
    "instrument.quality_manual": "entered manually",
    "instrument.quality_derived": "derived",
    "instrument.no_conflicts": "No conflict detected among acquired facts.",
    "instrument.fact_generic": "Fact",
    "instrument.fact_name": "Name",
    "instrument.fact_ter": "TER",
    "instrument.fact_issuer": "Issuer",
    "instrument.fact_category": "Category",
    "instrument.fact_index": "Tracked index",
    "instrument.fact_domicile": "Domicile",
    "instrument.fact_fund_currency": "Fund currency",
    "instrument.fact_inception": "Launch date",
    "instrument.fact_aum": "Assets",
    "instrument.fact_kid_url": "KID link",
    "instrument.fact_kid_date": "KID date",
    "instrument.fact_sri": "Synthetic risk (1–7)",
    "instrument.fact_history_start": "Observed coverage start",
    "instrument.fact_history_end": "Observed coverage end",
    "instrument.identity_section": "Identity and listing",
    "instrument.identity_field": "Field",
    "instrument.identity_value": "Value",
    "instrument.identity_symbol": "Active symbol",
    "instrument.identity_isin": "ISIN",
    "instrument.identity_exchange": "Market",
    "instrument.identity_currency": "Listing currency",
    "instrument.costs_section": "Costs and KID",
    "instrument.characteristics_section": "Characteristics",
    "instrument.allocation_section": "Allocation and holdings",
    "instrument.holdings_missing": "Top holdings are not available.",
    "instrument.holding_symbol": "Symbol",
    "instrument.holding_name": "Name",
    "instrument.holding_weight": "Weight",
    "instrument.history_section": "Historical coverage",
    "instrument.related_section": "Related listings",
    "instrument.related_missing": "No other listing with the same ISIN is available.",
    "instrument.related_symbol": "Symbol",
    "instrument.related_exchange": "Market",
    "instrument.related_currency": "Currency",
    "instrument.related_source": "Source",
    "instrument.sources_section": "Sources and conflicts",
    "instrument.attempt": "{source}: {outcome}",
    "instrument.kid_section": "KID-verified data",
    "instrument.kid_ter_enabled": "Set TER from KID",
    "instrument.kid_url_label": "KID URL",
    "instrument.kid_date_label": "Document date (YYYY-MM-DD)",
    "instrument.sri_label": "Synthetic risk indicator (1–7)",
    "instrument.kid_save": "Save KID data",
    "instrument.kid_url_invalid": "The URL must start with http:// or https://.",
    "instrument.kid_date_invalid": "The KID date must use YYYY-MM-DD format.",
    "instrument.kid_date_future": "The KID date cannot be in the future.",
    "instrument.kid_saved": "KID data saved.",
    "instrument.kid_clear": "Remove KID data",
    "instrument.retry_button": "Retry acquisition",
    "instrument.add_button": "Add to portfolio",
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
    "ulcer_index": "Ulcer Index",
    "best_year": "Best year",
    "worst_year": "Worst year",
    "ter_cost": "TER cost",
    "reconstructed": "Reconstructed",
    "balance": "Ending balance",
    "invested": "Invested",
    "gain": "Gain",
    "xirr": "XIRR",
}

ESITI: dict[str, str] = {
    "ok": "ok",
    "no_data": "no data",
    "not_configured": "not configured",
    "isin_required": "ISIN required",
    "found": "found",
    "no_ter": "TER unavailable",
    "blocked": "blocked by plan",
    "symbol_unresolved": "symbol not resolved",
    "temporary_error": "temporary error",
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
    "manual": "Entered manually",
    "kid": "KID",
    "missing": "Not available",
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

MESSAGGI.update({
    "benchmark.option_famous": "Famous portfolios",
    "benchmark.famous_search_label": "Search a famous portfolio",
    "benchmark.famous_search_placeholder": "Portfolio name or ID",
    "benchmark.famous_no_results": "No portfolio matches the search.",
    "benchmark.famous_selected": "Selected famous portfolio: **{name}**",
    "benchmark.famous_composition": "Composition",
    "benchmark.famous_proxy_notes": "Proxies and exceptions",
    "benchmark.famous_wrappers": "Wrappers",
    "benchmark.famous_source": "Composition source: {source}",
    "benchmark.famous_kind_composite": "Composite replica with EUR-listed proxies",
    "benchmark.famous_kind_managed": "Managed instrument: internal allocation is not reconstructed",
    "benchmark.famous_rebalance": "Model rebalance: yearly, on the first market day",
    "benchmark.famous_managed_rebalance": "Rebalanced internally by the managed product",
    "benchmark.famous_warning": "Warning: {warning}",
    "benchmark.famous_missing_component": "Missing component: {symbol}",
    "benchmark.famous_missing_atomic": "The benchmark is unavailable because at least one component is missing; your portfolio continues.",
    "benchmark.note_proxy": "Approximate proxy declared by the catalog.",
    "benchmark.note_us_sg": "US small growth approximated with US small blend.",
    "benchmark.note_us_t": "US total approximated with 85% large blend and 15% small blend.",
    "benchmark.note_gold": "Gold through a EUR-listed ETC, not an equity fund.",
    "benchmark.note_managed_us": "US ETF: listing currency and data source may limit historical availability.",
    "benchmark.warning_none": "No additional warning.",
    "benchmark.warning_dragon": "Approximate retail replica: includes KMLM, CAOS and a gold ETC.",
})

_BENCHMARK_PORTFOLIOS_EN = {
    "60_40": ("60/40 Portfolio", "60% US large cap and 40% intermediate Treasuries.", "60% US-L · 40% UST-I"),
    "80_20": ("80/20 Portfolio", "80% US equities and 20% intermediate Treasuries.", "80% US-L · 20% UST-I"),
    "global_equity_100": ("100% Global Equity", "100% global equities.", "100% GLB"),
    "bogleheads_three_fund": ("Bogleheads Three-Fund Portfolio", "US, international and bond funds.", "64% US-L · 16% DMxUS-L · 20% UST-I"),
    "permanent": ("Permanent Portfolio", "Equal shares of equities, bonds, cash and gold.", "25% US-L · 25% UST-L · 25% BILL · 25% GOLD"),
    "golden_butterfly": ("Golden Butterfly", "Large and small value equities, Treasuries, cash and gold.", "20% US-L · 20% US-SV · 20% UST-L · 20% UST-S · 20% GOLD"),
    "all_weather": ("All Weather Portfolio", "ALLW ETF with internal Bridgewater/State Street management.", "100% ALLW · internal management"),
    "all_seasons": ("All Seasons Portfolio", "Equities, Treasuries, gold and commodities.", "30% US-L · 40% UST-L · 15% UST-I · 8% GOLD · 7% COM"),
    "swensen": ("Swensen Portfolio", "US and international equities, emerging markets, bonds and REITs.", "30% US-L · 15% DMxUS-L · 5% EM · 30% UST-I · 20% REIT; source aggregates a TIPS share in bonds"),
    "coffeehouse": ("Coffeehouse Portfolio", "Diversified by size and style, with REITs and bonds.", "10% US-L · 10% US-LV · 10% US-S · 10% US-SV · 10% DMxUS-L · 10% REIT · 40% UST-I"),
    "ivy": ("Ivy Portfolio", "Five equal blocks of equities, bonds, REITs and commodities.", "20% US-L · 20% DMxUS-L · 20% UST-I · 20% REIT · 20% COM"),
    "seven_twelve": ("7Twelve Portfolio", "Twelve sleeves across equities, bonds, REITs and commodities.", "13% US-L · 12% US-S · 8% DMxUS-L · 8% EM · 17% UST-I · 9% BILL · 8% GOV-DM · 8% REIT · 17% COM"),
    "merriman_ultimate_buy_and_hold": ("Merriman Ultimate Buy and Hold", "Style- and region-diversified equities plus bonds and REITs.", "6% in nine equity sleeves · 20% UST-I · 20% UST-S · 6% REIT"),
    "larry": ("Larry Portfolio", "A bond-heavy allocation with small value and emerging markets.", "15% US-SV · 8% DMxUS-SV · 7% EM · 70% UST-I"),
    "dragon": ("Dragon Portfolio", "Retail replica of a multi-regime strategy with trend and convexity.", "24% US-L · 18% UST-I · 19% GOLD · 18% KMLM · 21% CAOS"),
    "risk_parity": ("Risk Parity Portfolio", "RPAR ETF with internal risk-parity allocation.", "100% RPAR · internal management"),
    "core_four": ("Core Four Portfolio", "US and international equities, bonds and REITs.", "48% US-L · 24% DMxUS-L · 20% UST-I · 8% REIT"),
    "pinwheel": ("Pinwheel Portfolio", "Eight sleeves across equities, bonds, cash, REITs and gold.", "15% US-L · 10% US-SV · 15% DMxUS-L · 10% EM · 15% UST-I · 10% BILL · 15% REIT · 10% GOLD"),
    "weird": ("Weird Portfolio", "Equal shares of small value, international small, bonds, REITs and gold.", "20% US-SV · 20% DMxUS-S · 20% UST-L · 20% REIT · 20% GOLD"),
    "sandwich": ("Sandwich Portfolio", "Layered mix of equities, bonds, cash, REITs and emerging markets.", "20% US-L · 8% US-S · 10% DMxUS-S · 6% DMxUS-L · 6% EM · 30% UST-I · 4% BILL · 11% GOV-DM · 5% REIT"),
    "gone_fishin": ("Gone Fishin’ Portfolio", "Diversified across markets, credit, inflation hedges and gold.", "15% US-T · 15% US-S · 10% EU · 10% PAC · 10% EM · 10% US-AGG · 10% HY · 10% TIPS · 5% REIT · 5% GOLD"),
    "ideal_index": ("Ideal Index Portfolio", "US style equities, international equities, Treasuries and REITs.", "9% US-LV · 9% US-SV · 7% US-L · 6% US-SG · 31% DMxUS-L · 30% UST-S · 8% REIT"),
    "global_market": ("Global Market Portfolio", "Global market with international government bonds, REITs and gold.", "38% DM-L · 7% DM-S · 5% EM · 44% GOV-DM · 4% REIT · 2% GOLD"),
    "trinity": ("Trinity Portfolio", "TRTY ETF with internal Cambria management.", "100% TRTY · internal management"),
    "no_brainer": ("No-Brainer Portfolio", "Four equal blocks of equities and short Treasuries.", "25% US-L · 25% US-S · 25% DMxUS-S · 25% UST-S"),
}
for _portfolio_id, (_name, _tooltip, _composition) in _BENCHMARK_PORTFOLIOS_EN.items():
    MESSAGGI[f"benchmark.portfolio.{_portfolio_id}.name"] = _name
    MESSAGGI[f"benchmark.portfolio.{_portfolio_id}.tooltip"] = _tooltip
    MESSAGGI[f"benchmark.portfolio.{_portfolio_id}.composition"] = _composition
