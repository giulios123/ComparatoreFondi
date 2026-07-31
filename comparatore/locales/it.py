"""Catalogo italiano - lingua di riferimento: ogni chiave qui e' quella che
`comparatore.i18n.traduci()` ripiega su di essa quando manca in un'altra
lingua, quindi deve restare sempre completo."""

LINGUA = "it"
NOME = "Italiano"

MESSAGGI: dict[str, str] = {
    # --- Intestazione -------------------------------------------------
    "app.page_title": "Comparatore Fondi",
    "app.title": "📈 Comparatore Fondi",
    "app.subtitle": "Backtest di fondi ed ETF su più fonti dati, con impatto del TER.",

    # --- Ribilanciamento (help della tendina) --------------------------
    "rebalance.help": (
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
    ),

    # --- Sidebar: parametri generali ------------------------------------
    "sidebar.header": "⚙️ Parametri",
    "sidebar.lingua_label": "Lingua",
    "sidebar.periodo_caption": "Periodo",
    "preset.1y": "1a",
    "preset.5y": "5a",
    "preset.10y": "10a",
    "preset.20y": "20a",
    "preset.max": "Max",
    "sidebar.data_inizio": "Data inizio",
    "sidebar.data_fine": "Data fine",
    "sidebar.valore_iniziale": "Valore iniziale del portafoglio",
    "sidebar.valuta_riferimento": "Valuta di riferimento",
    "sidebar.ribilanciamento_label": "Ribilanciamento",
    "sidebar.rebalance_caption_none": (
        "I pesi impostati sono un punto di partenza: senza ribilanciamento "
        "derivano nel tempo con i rendimenti relativi dei fondi."
    ),
    "sidebar.rebalance_caption_active": (
        "I pesi tornano a quelli impostati al primo giorno di borsa di ogni "
        "periodo (nessun costo di negoziazione applicato)."
    ),

    # --- Sidebar: costi --------------------------------------------------
    "costs.subheader": "Costi",
    "costs.caption": (
        "I NAV pubblicati sono **già al netto del TER**. "
        "La curva *lorda* ricostruisce il fondo senza commissioni: "
        "la distanza fra le due curve è il costo del TER."
    ),
    "costs.show_gross_checkbox": "Mostra anche la curva lorda (senza TER)",

    # --- Sidebar: storico esteso ------------------------------------------
    "history.subheader": "Storico esteso",
    "history.checkbox": "Ricostruisci il periodo precedente alla nascita del fondo",
    "history.help": (
        "Prolunga all'indietro la serie usando un indice o un fondo più "
        "anziano. È una ricostruzione, non un dato reale: nei grafici "
        "compare tratteggiata."
    ),
    "history.caption_non_usd": (
        "⚠️ I proxy sono quotati in dollari. Con valuta di riferimento "
        "diversa da USD la ricostruzione non può scendere sotto il "
        "**{anno}**, prima data dei cambi ufficiali BCE."
    ),
    "history.caption_usd": "Valuta USD: la ricostruzione può usare tutta la profondità del proxy.",

    # --- Sidebar: fonti dati -----------------------------------------------
    "sources.subheader": "Fonti dati",
    "sources.justetf_info": (
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
        "fornitori dei dati. Il consenso viene ricordato su questo computer "
        "finché non lo revochi; lasciando la casella spenta, justETF verrà "
        "contattato solo se lo scegli "
        "esplicitamente come fonte di un singolo fondo."
    ),
    "sources.justetf_checkbox": "Acconsento alle richieste automatiche a justETF",
    "sources.justetf_help": (
        "Aggiunge justETF prima di Yahoo nell'ordine automatico per gli "
        "ETF con ISIN. Puoi revocare il consenso deselezionando la casella."
    ),
    "sources.status_optin_off": " — opt-in disattivato",
    "sources.status_not_configured": " — non configurata",
    "sources.order_caption": (
        "Ordine automatico: CSV → Yahoo → EODHD → Twelve Data; justETF entra "
        "solo con l'opt-in qui sopra. Si può sempre forzare una fonte per "
        "singolo fondo dalla tabella. Le cache EODHD e Twelve Data scadono "
        "dopo {giorni} giorni."
    ),
    "sources.eodhd_hint": (
        "Per i **fondi collocati in Italia** (Mediolanum, Fineco, banche) "
        "conviene configurare EODHD: Yahoo ne copre solo una parte e con "
        "storico dal 2018. Inserisci la chiave qui sopra, in "
        "**🔑 Chiavi API**."
    ),
    "sources.used_caption": "📚 Fonti usate: {elenco}",

    # --- Sidebar: chiavi API -------------------------------------------------
    "api_keys.expander": "🔑 Chiavi API (EODHD, Twelve Data)",
    "api_keys.caption": (
        "Restano solo su questo computer, in `.streamlit/api_keys.json` "
        "(permessi riservati al tuo utente, già escluso dal repository). "
        "Sopravvivono al riavvio e a **Svuota cache**, qui sotto."
    ),
    "api_keys.eodhd_label": "Chiave EODHD",
    "api_keys.td_label": "Chiave Twelve Data",
    "api_keys.save_button": "Salva",
    "api_keys.saved_toast": "Chiavi salvate",
    "api_keys.saved_caption": "Chiavi salvate: {elenco}",
    "api_keys.forget_button": "Dimentica le chiavi salvate",
    "api_keys.forgotten_toast": "Chiavi e relative cache rimosse",

    # --- Sidebar: CSV ---------------------------------------------------------
    "csv.expander": "📄 Carica una serie da CSV",
    "csv.caption": (
        "Per i fondi che nessuna fonte copre. Due colonne: data e valore "
        "della quota. Separatore, decimale e formato data riconosciuti "
        "da soli."
    ),
    "csv.symbol_label": "Simbolo o ISIN a cui associarla",
    "csv.symbol_placeholder": "es. IT0001234567",
    "csv.currency_label": "Valuta della serie",
    "csv.file_label": "File CSV",
    "csv.success": "{n} osservazioni dal {inizio} al {fine}.",
    "csv.loaded_caption": "Caricate: {elenco}",
    "csv.remove_button": "Rimuovi le serie caricate",

    # --- Sidebar: cache, licenze, risk-free ------------------------------------
    "cache.caption": "💾 Cache su disco: {n} serie, {mb:.1f} MB",
    "cache.clear_button": "Svuota cache",
    "cache.cleared_toast": "Cache svuotata",
    "sidebar.risk_free_label": "Tasso risk-free annuo (per Sharpe)",

    # --- Sidebar: informazioni e licenze --------------------------------------
    "about.expander": "ℹ️ Informazioni e licenze",
    "about.version": "Comparatore Fondi versione {versione}",
    "about.license_caption": (
        "Codice sorgente distribuito con licenza "
        "[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)."
    ),
    "about.third_party_header": "Librerie di terze parti",
    "about.third_party_caption": (
        "Il progetto usa le librerie elencate sotto, ciascuna con la propria "
        "licenza. Il testo completo, incluse le note legali, è nel file scaricabile."
    ),
    "about.third_party_missing": (
        "Elenco delle licenze non disponibile in questa installazione."
    ),
    "about.download_button": "⬇️ Scarica le licenze di terze parti (.txt)",
    "about.col_package": "Pacchetto",
    "about.col_version": "Versione",
    "about.col_license": "Licenza",

    # --- Sidebar: portafoglio (export/import) ---------------------------------
    "portfolio_io.expander": "💼 Portafoglio: salva e carica",
    "portfolio_io.caption": (
        "Salva su file i fondi, i pesi e i parametri del backtest, per "
        "riaprirli in un'altra sessione o su un altro computer."
    ),
    "portfolio_io.download_button": "⬇️ Scarica il portafoglio (.json)",
    "portfolio_io.download_empty_hint": "Aggiungi almeno un fondo per poterlo scaricare.",
    "portfolio_io.upload_label": "Carica un portafoglio (.json)",
    "portfolio_io.import_success": "Portafoglio caricato: {n} fondi.",
    "portfolio_io.import_error": "File non valido: {errore}",

    # --- Ricerca --------------------------------------------------------------
    "search.expander": "🔎 Cerca fondi ed ETF",
    "search.query_label": "Nome, ticker o ISIN",
    "search.query_placeholder": "es. 'Vanguard S&P 500', 'VUSA.AS' oppure 'IE00B3XXRP09'",
    "search.funds_only_toggle": "Solo fondi/ETF",
    "search.spinner": "Ricerca in corso…",
    "search.no_results": "Nessun risultato. Prova con l'ISIN o con il ticker completo.",
    "search.isin_hint": (
        "🔗 L'ISIN permette di usare justETF solo se hai attivato "
        "l'opt-in nelle Fonti dati o scegli la fonte sul singolo fondo."
    ),
    "search.add_button": "Aggiungi",

    # --- Toast ------------------------------------------------------------------
    "toast.fund_exists": "{symbol} è già nel portafoglio",
    "toast.fund_added": "Aggiunto {symbol}",
    "toast.fund_removed": "Rimosso {elenco}",

    # --- Composizione del portafoglio ---------------------------------------------
    "portfolio.subheader": "Composizione del portafoglio",
    "portfolio.empty_hint": "Cerca e aggiungi almeno un fondo per iniziare.",

    "editor.col_rimuovi": "Rimuovi",
    "editor.col_fondo": "Fondo",
    "editor.col_simbolo": "Simbolo",
    "editor.col_isin": "ISIN",
    "editor.col_valuta": "Valuta",
    "editor.col_peso": "Peso %",
    "editor.col_importo": "Importo ({ccy})",
    "editor.col_ter": "TER %",
    "editor.col_extra": "Costi extra %",
    "editor.col_fonte": "Fonte",
    "editor.col_proxy": "Proxy storico",
    "editor.rimuovi_help": (
        "Toglie il fondo dal portafoglio e ridistribuisce il suo peso sugli altri, "
        "mantenendone le proporzioni."
    ),
    "editor.isin_help": (
        "Serve per usare justETF quando la fonte è abilitata o "
        "selezionata esplicitamente sul fondo."
    ),
    "editor.peso_help": (
        "Quota del portafoglio assegnata al fondo. Modificandola, gli altri pesi "
        "si adeguano da soli in proporzione fra loro, così il totale resta 100%."
    ),
    "editor.importo_help": (
        "Capitale assegnato al fondo in questa valuta. Modificandolo si aggiornano "
        "i pesi e il valore iniziale del portafoglio."
    ),
    "editor.ter_help": (
        "Spesa corrente annua. Precompilato quando la fonte lo espone: "
        "verifica sempre sul KID del fondo."
    ),
    "editor.extra_help": (
        "Costi annui NON già inclusi nel NAV (custodia, consulenza). "
        "Vengono sottratti dalla performance."
    ),
    "editor.fonte_help": "'Automatica' prova le fonti in ordine di priorità.",
    "editor.proxy_help": (
        "Strumento più anziano con cui ricostruire il periodo "
        "precedente alla nascita del fondo."
    ),
    "editor.equalize_button": "⚖️ Pesi uguali",
    "editor.clear_button": "🗑️ Svuota",
    "editor.total_weight_metric": "Totale pesi",
    "editor.total_value_metric": "Capitale investito",

    # --- Avvisi su TER, pesi, date -------------------------------------------------
    "ter_warning.reason_eodhd_blocked": (
        "il piano EODHD configurato non include `/fundamentals` (serve un "
        "piano a pagamento), quindi né TER né classificazione arrivano da lì. "
    ),
    "ter_warning.reason_none": "nessuna fonte configurata lo espone per questi strumenti. ",
    "ter_warning.message": (
        "TER non trovato per: {elenco}. {motivo}"
        "Inseriscilo a mano dal KID per vedere l'impatto dei costi."
    ),
    "weight.error_zero": "Assegna almeno un peso maggiore di zero.",
    "weight.warning_normalized": "I pesi sommano a {tot:.1f}%: verranno normalizzati a 100%.",
    "weight.error_importo_min": "Il capitale totale del portafoglio non può scendere sotto {minimo}.",
    "dates.error_order": "La data di inizio deve precedere la data di fine.",

    # --- Recupero prezzi -----------------------------------------------------------
    "prices.spinner": "Scarico le serie storiche…",
    "prices.error_none": "Nessun dato di prezzo disponibile per i fondi selezionati.",
    "prices.missing_expander": "🚫 {n} fondi senza dati",
    "prices.missing_hint": (
        "Suggerimento: carica una serie CSV oppure, dopo aver verificato "
        "le condizioni del servizio, abilita justETF e compila l'ISIN."
    ),

    # --- Conversione valutaria -------------------------------------------------------
    "fx.error_none": "Nessuna serie convertibile nella valuta di riferimento.",
    "fx.error_failed": "Esclusi dal backtest (valuta non risolvibile): {elenco}.",
    "fx.error_failed_eodhd_cause": (
        " Il piano EODHD configurato non include `/fundamentals` (serve un "
        "piano a pagamento): se questi fondi vengono da una ricerca EODHD, "
        "verifica se esistono anche su Yahoo con un altro simbolo, oppure "
        "carica una serie CSV indicando tu la valuta."
    ),
    "fx.converted_caption": "💱 Convertiti in {ccy} ai cambi giornalieri: {elenco}",
    "fx.truncated_detail_item": "{symbol} dal {data}",
    "fx.truncated_warning": (
        "Cambi disponibili solo da una data successiva a quella richiesta: {dettaglio}. "
        "Il periodo è stato accorciato invece di usare un tasso retro-riempito."
    ),

    # --- Storico esteso (blocco di esecuzione) ------------------------------------------
    "history.expander": "🧩 Storico ricostruito",
    "history.reconstructing_spinner": "Ricostruisco lo storico di {symbol} con {proxy}…",
    "history.proxy_unavailable": "{symbol}: proxy {proxy} non disponibile",
    "history.proxy_not_older": (
        "{symbol}: {proxy} non è più anziano del fondo, niente da ricostruire"
    ),
    "history.reconstructed_note": "**{symbol}** ricostruito dal {data} con {proxy_label}{caveat}",
    "history.reconstructed_caption": (
        "I tratti ricostruiti sono stime basate su uno strumento diverso "
        "dal fondo, non dati reali. Nei grafici compaiono tratteggiati."
    ),
    "proxy.caveat_price_only": (
        "indice di solo prezzo: il tratto ricostruito esclude i dividendi "
        "e sottostima il rendimento"
    ),
    "coverage_warning": "{symbol}: dati disponibili solo dal {data}",

    # --- Risultati del backtest --------------------------------------------------------
    "results.subheader": "Risultati · {inizio} → {fine}",
    "results.reconstructed_info": (
        "🧩 Le metriche qui sopra includono il periodo ricostruito "
        "({inizio} → {fine}): sono indicative, non la performance realmente "
        "ottenuta dai fondi."
    ),
    "metrics.explainer_expander": "❓ Come si leggono queste metriche",
    "costs.impact_info": (
        "💸 **Impatto del TER**: su {anni:.1f} anni le commissioni correnti sono "
        "costate **{costo}**, pari al **{pct}** del montante che avresti avuto "
        "senza costi ({lordo} lordi contro {netto} netti)."
    ),

    # --- Testi delle metriche (help) ---------------------------------------------------
    "help.valore_finale": (
        "Quanto sarebbero diventati i {capitale} iniziali a fine periodo, "
        "al netto del TER."
    ),
    "help.rendimento_totale": (
        "Variazione complessiva sull'intero periodo, **non** annualizzata."
    ),
    "help.cagr": (
        "Rendimento medio annuo composto: il tasso costante che, applicato "
        "ogni anno, porta dal valore iniziale a quello finale nello stesso "
        "tempo impiegato realmente."
    ),
    "help.volatilita": (
        "Oscillazione annualizzata dei rendimenti giornalieri (deviazione "
        "standard × √252). Dice quanto si è mosso il percorso, non quanto "
        "si è guadagnato: due curve con lo stesso CAGR possono avere "
        "volatilità molto diverse."
    ),
    "help.sharpe": (
        "Rendimento in eccesso sul tasso risk-free (oggi impostato al "
        "{rf_pct}) per unità di volatilità sopportata. Sopra 1 è "
        "generalmente considerato un buon risultato."
    ),
    "help.sortino": (
        "Come lo Sharpe (risk-free al {rf_pct}), ma al denominatore conta "
        "solo l'oscillazione al ribasso: non penalizza i rialzi bruschi, "
        "solo le discese."
    ),
    "help.max_drawdown": (
        "La peggior discesa dal massimo storico precedente al minimo "
        "successivo: la perdita più profonda che si sarebbe dovuta "
        "sopportare restando investiti."
    ),
    "help.calmar": (
        "CAGR diviso il max drawdown in valore assoluto: rendimento "
        "ottenuto per unità di perdita massima subita."
    ),
    "help.miglior_anno": "Il miglior rendimento su anno solare nel periodo.",
    "help.peggior_anno": "Il peggior rendimento su anno solare nel periodo.",
    "help.costo_ter": (
        "Differenza, in {ccy}, a fine periodo fra il montante senza "
        "commissioni (curva lorda) e quello realmente ottenuto (curva "
        "netta)."
    ),
    "help.ricostruito": (
        "La riga include un tratto stimato con uno strumento proxy, non "
        "dati reali del fondo: le sue metriche vanno lette come "
        "indicative."
    ),

    # --- Grafici (tab Portafoglio) -----------------------------------------------------
    "chart.legend_reconstructed": "Portafoglio (ricostruito)",
    "chart.legend_net": "Portafoglio (netto TER)",
    "chart.legend_gross": "Portafoglio (lordo, senza TER)",
    "chart.hover_reconstructed_suffix": " (ricostruito)",
    "chart.annotation_real_start": "inizio dati reali",
    "chart.annotation_initial_capital": "capitale iniziale",
    "chart.legend_synthetic": "{comparto} (sintetica)",
    "chart.hover_constant_growth": " · crescita costante",
    "chart.yaxis_value": "Valore ({ccy})",
    "chart.composition_header": "**Composizione nel tempo**",
    "chart.synthetic_caption": (
        "⚠️ Le curve dei fondi pensione sono **rette a crescita costante**, "
        "ricavate dal rendimento medio annuo COVIP: mostrano dove si "
        "sarebbe arrivati, non come ci si è arrivati. Il percorso reale ha "
        "oscillato, ma COVIP non pubblica le serie storiche."
    ),
    "chart.weights_set_final": "Pesi impostati: {pesi} → a fine periodo: {pesi_finali}.",
    "chart.rebalance_caption_active": (
        "Ribilanciamento {tipo}: {n} interventi nel periodo, l'ultimo il {data} "
        "(pesi impostati: {pesi})."
    ),
    "chart.rebalance_caption_none_yet": (
        "Ribilanciamento {tipo}: nessun intervento ancora scattato, il periodo "
        "scelto è più corto della prima scadenza."
    ),

    # --- Tab -----------------------------------------------------------------------------
    "tab.portafoglio": "📊 Portafoglio",
    "tab.bilanciamento": "⚖️ Bilanciamento",
    "tab.confronto": "🆚 Confronto fondi",
    "tab.drawdown": "📉 Drawdown",
    "tab.dati": "📋 Dati",
    "tab.previdenza": "🏦 Fondi pensione",

    # --- Tab Bilanciamento -----------------------------------------------------------------
    "bilancio.header": "**Classificazione**",
    "bilancio.col_classe": "Classe",
    "bilancio.col_area": "Area",
    "bilancio.col_settore": "Settore",
    "bilancio.col_valuta": "Valuta",
    "bilancio.peso_help": "Si modifica nella tabella di composizione, in cima alla pagina.",
    "bilancio.tendina_help": (
        "**{automatica}** conserva la classificazione dedotta, che può "
        "ripartirsi su più voci (un fondo mondiale non è tutto su un'area "
        "sola). Scegliendo una voce le si attribuisce l'intero strumento."
    ),
    "bilancio.provenienza_prefix": "🏷️ Classificazione: ",
    "bilancio.provenienza_eodhd": "**{n}** da EODHD",
    "bilancio.provenienza_yahoo": "**{n}** da Yahoo",
    "bilancio.provenienza_nome": "**{n}** dedotti dal nome",
    "bilancio.provenienza_manuali": "**{n}** con correzioni manuali",
    "bilancio.titolo_classe": "Classe di attivo",
    "bilancio.titolo_area": "Area geografica",
    "bilancio.titolo_settore": "Settore",
    "bilancio.titolo_valuta": "Valuta di quotazione",
    "bilancio.titolo_paesi": "Paesi (stima dalle prime posizioni)",
    "bilancio.dettaglio_expander": "🔍 Dettaglio per strumento",
    "bilancio.col_strumento": "Strumento",
    "bilancio.posizioni_expander": "📌 Principali posizioni",
    "bilancio.posizioni_caption": (
        "Le prime posizioni lette da Yahoo per ciascun fondo (ETF e fondi "
        "comuni riconosciuti come tali): la base della stima geografica "
        "qui sopra, utile anche per vedere le sovrapposizioni fra fondi "
        "diversi."
    ),
    "bilancio.col_titolo": "Titolo",
    "bilancio.col_peso_nel_fondo": "Peso nel fondo",
    "bilancio.posizioni_none": (
        "Nessuna posizione disponibile per i fondi in portafoglio: "
        "servono dati di composizione da Yahoo, non sempre presenti."
    ),
    "bilancio.esclusi_caption_one": (
        "ℹ️ {elenco}: conta nella ripartizione ma non nel backtest, per mancanza di prezzi."
    ),
    "bilancio.esclusi_caption_many": (
        "ℹ️ {elenco}: contano nella ripartizione ma non nel backtest, per mancanza di prezzi."
    ),
    "bilancio.disclaimer": (
        "⚠️ La classificazione automatica è **indicativa** e va verificata sul "
        "KID: senza EODHD (a chiave) e senza dati di composizione da Yahoo "
        "viene dedotta dal nome del fondo, che spesso non basta. La "
        "ciambella **Paesi** è una stima sulle sole prime posizioni lette da "
        "Yahoo (in genere un quinto o un quarto del fondo): la ripartizione "
        "geografica completa richiede un piano EODHD a pagamento. La "
        "**valuta** è quella di quotazione, non l'esposizione valutaria: un "
        "ETF sul mercato mondiale quotato in euro resta esposto al dollaro."
    ),

    # --- Tab Confronto fondi -----------------------------------------------------------------
    "confronto.caption": (
        "Andamento di {capitale} investiti interamente in ciascun fondo, "
        "per un confronto a parità di capitale."
    ),
    "confronto.legend_reconstructed": "{col} (ricostruito)",
    "confronto.legend_gross": "{col} (lordo)",
    "confronto.col_valore_finale": "Valore finale (da {capitale})",
    "confronto.stesso_capitale_caption": (
        "Tutte le righe partono dallo stesso capitale: **{capitale}** "
        "investiti al 100% in un solo fondo, e gli stessi "
        "**{capitale}** investiti nel portafoglio con i pesi "
        "impostati e il ribilanciamento scelto. I valori finali sono quindi "
        "confrontabili direttamente riga per riga."
    ),
    "confronto.footnote": (
        "La colonna *Ricostruito* segnala le righe le cui metriche "
        "comprendono un periodo stimato da un proxy."
    ),
    "confronto.riga_portafoglio": "🎯 PORTAFOGLIO",
    "si": "sì",
    "no": "no",
    "nd": "n/d",

    # --- Tab Drawdown -----------------------------------------------------------------------
    "drawdown.legend_portafoglio": "Portafoglio",
    "drawdown.yaxis": "Drawdown (%)",
    "drawdown.yearly_header": "**Rendimenti per anno solare**",
    "drawdown.yaxis_yearly": "Rendimento (%)",

    # --- Tab Dati -----------------------------------------------------------------------------
    "dati.col_netto": "Portafoglio (netto)",
    "dati.col_lordo": "Portafoglio (lordo)",
    "dati.col_solo_prefix": "Solo ",
    "dati.download_button": "⬇️ Scarica CSV completo",

    # --- Tab Fondi pensione -----------------------------------------------------------------
    "previdenza.header_con_anno": "### Previdenza complementare · dati COVIP al 31/12/{anno}",
    "previdenza.header_senza_anno": "### Previdenza complementare · dati COVIP",
    "previdenza.fiscalita_warning": (
        "**Il confronto non considera la fiscalità.** I fondi pensione godono "
        "di deducibilità fino a 5.164,57 € l'anno, tassazione dei rendimenti al "
        "20% invece del 26% e imposta finale che scende dal 15% al 9%. Sono "
        "vantaggi che giocano a loro favore, quindi i numeri qui sotto li "
        "**sottostimano**."
    ),
    "previdenza.rendimenti_caption": (
        "COVIP pubblica solo rendimenti medi annui su orizzonti fissi, non le "
        "serie storiche: per questi strumenti volatilità, drawdown e Sharpe non "
        "sono calcolabili da nessun dato pubblico. Per averli, carica il valore "
        "quota del tuo fondo con l'uploader CSV nella barra laterale."
    ),
    "previdenza.catalogo_error": (
        "Catalogo COVIP non disponibile: controlla la connessione e riprova."
    ),
    # "Tutte", "negoziale", "aperto", "PIP" restano sempre in italiano: sono
    # le categorie regolamentari COVIP passate cosi' come sono a `covip.cerca()`,
    # e tradurre l'etichetta di un `st.selectbox` che non usa `format_func`
    # cambierebbe il valore stesso dell'opzione, con lo stesso rischio di
    # corruzione dello stato descritto per `rebalance` (vedi sotto).
    "previdenza.forma_label": "Forma pensionistica",
    "previdenza.col_tipo": "Tipo",
    "previdenza.riga_portafoglio": "🎯 IL TUO PORTAFOGLIO",
    "previdenza.categoria_label": "Categoria",
    "previdenza.cerca_label": "Cerca per nome del fondo o della società",
    "previdenza.cerca_placeholder": "es. 'previgest', 'cometa', 'mediolanum'",
    "previdenza.risultati_caption": "{n} comparti corrispondono ai filtri.",
    "previdenza.comparti_label": "Comparti da confrontare",
    "previdenza.seleziona_hint": (
        "Seleziona uno o più comparti per confrontarli con il tuo portafoglio."
    ),
    "previdenza.rendimento_header": "**Rendimento medio annuo, sulle stesse finestre COVIP**",
    "previdenza.col_help_orizzonte": (
        "Rendimento medio annuo COVIP sulla finestra a {anni} anni ({periodo})."
    ),
    "previdenza.col_isc": "ISC 10a",
    "previdenza.col_help_isc": (
        "L'equivalente del TER per la previdenza: incidenza annua "
        "dei costi sull'orizzonte a 10 anni."
    ),
    "previdenza.mancanti_caption": (
        "Il tuo portafoglio risulta **n/d** su {elenco_anni} perché non copre "
        "l'intera finestra ({dettaglio}). Calcolarlo su un periodo più corto "
        "darebbe un numero non confrontabile."
    ),
    "previdenza.anni_suffix": "{a} anni",
    "previdenza.il_tuo_portafoglio": "Il tuo portafoglio",
    "previdenza.yaxis_rendimento": "Rendimento medio annuo (%)",
    "previdenza.costi_header": "**Quanto pesano i costi**",
    "previdenza.col_comparto": "Comparto",
    "previdenza.col_isc_annuo": "ISC annuo",
    "previdenza.col_rendimento_10a": "Rendimento 10a",
    "previdenza.col_eroso": "Eroso su {capitale} in 10 anni",
    "previdenza.col_quota_rendimento": "Quota del rendimento",
    "previdenza.costi_caption": (
        "L'ISC è l'equivalente del TER per la previdenza. L'ultima "
        "colonna mostra che frazione del rendimento netto ottenuto "
        "viene assorbita ogni anno dai costi."
    ),
    "previdenza.curve_checkbox": "Mostra le curve dei fondi pensione nel grafico del portafoglio",
    "previdenza.curve_help": (
        "Rette a crescita costante ricavate dal rendimento medio "
        "annuo: mostrano il punto d'arrivo, non il percorso."
    ),
    "previdenza.orizzonte_label": "Orizzonte da cui ricavare il tasso",
    "previdenza.fonte_caption": (
        "Fonte: [COVIP](https://www.covip.it/open-data), open data con licenza "
        "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Il progetto "
        "normalizza e aggrega i dataset e calcola confronti e curve sintetiche; "
        "queste elaborazioni non sono dati COVIP originali."
    ),

    # --- Piè di pagina --------------------------------------------------------------------------
    "footer.disclaimer": (
        "Prezzi *total return* (dividendi reinvestiti). I NAV dei fondi sono già al "
        "netto del TER; la curva lorda è una ricostruzione teorica. I cambi sono "
        "quelli ufficiali BCE dal 1999, ottenuti tramite Frankfurter, con ripiego "
        "su Yahoo per le valute fuori paniere. Non sono considerati costi di "
        "ingresso/uscita, spread né fiscalità. Le performance passate non sono "
        "indicative di quelle future."
    ),
}

# Traduzione dei nomi di metrica: chiavi = quelle di `comparatore.metrics.summarize()`
# (stabili, inglesi per contratto - vedi `comparatore/metrics.py`), piu' le due
# aggiunte a livello di interfaccia (`ter_cost`, `reconstructed`).
METRICHE: dict[str, str] = {
    "final_value": "Valore finale",
    "total_return": "Rendimento totale",
    "cagr": "CAGR",
    "volatility": "Volatilità",
    "sharpe": "Sharpe",
    "sortino": "Sortino",
    "max_drawdown": "Max drawdown",
    "calmar": "Calmar",
    "best_year": "Miglior anno",
    "worst_year": "Peggior anno",
    "ter_cost": "Costo TER",
    "reconstructed": "Ricostruito",
}

# Traduzione degli esiti di risoluzione di un simbolo (comparatore.sources.registry.Attempt).
ESITI: dict[str, str] = {
    "ok": "ok",
    "no_data": "nessun dato",
    "not_configured": "non configurata",
    "isin_required": "serve l'ISIN",
}

# Traduzione dei termini di dominio: bucket di `comparatore.allocazione`
# (classe, area, settore, paese) e le loro sentinelle.
TERMINI: dict[str, str] = {
    "Azionario": "Azionario",
    "Obbligazionario": "Obbligazionario",
    "Liquidità": "Liquidità",
    "Materie prime": "Materie prime",
    "Immobiliare": "Immobiliare",
    "Non classificato": "Non classificato",
    "Globale": "Globale",
    "Nord America": "Nord America",
    "Europa": "Europa",
    "Italia": "Italia",
    "Giappone": "Giappone",
    "Asia-Pacifico": "Asia-Pacifico",
    "Mercati emergenti": "Mercati emergenti",
    "Diversificato": "Diversificato",
    "Tecnologia": "Tecnologia",
    "Finanza": "Finanza",
    "Sanità": "Sanità",
    "Energia": "Energia",
    "Industria": "Industria",
    "Beni di consumo": "Beni di consumo",
    "Utility": "Utility",
    "Materiali": "Materiali",
    "Comunicazioni": "Comunicazioni",
    "Resto del fondo": "Resto del fondo",
    "(automatica)": "(automatica)",
    "(nessuno)": "(nessuno)",
    # Paesi stimati dai suffissi di borsa (comparatore.allocazione._SUFFISSO_PAESE)
    "Taiwan": "Taiwan",
    "Hong Kong": "Hong Kong",
    "Corea del Sud": "Corea del Sud",
    "India": "India",
    "Regno Unito": "Regno Unito",
    "Svizzera": "Svizzera",
    "Australia": "Australia",
    "Paesi Bassi": "Paesi Bassi",
    "Germania": "Germania",
    "Spagna": "Spagna",
    "Francia": "Francia",
    "Canada": "Canada",
    "Cina": "Cina",
    "Danimarca": "Danimarca",
    "Svezia": "Svezia",
    "Norvegia": "Norvegia",
    "Brasile": "Brasile",
    "Messico": "Messico",
    "Stati Uniti": "Stati Uniti",
}

# Traduzione dell'etichetta di fonte: chiavi = `PriceSource.name` / `Instrument.source`
# ("nome" per la classificazione dedotta dal nome, senza fonte dati).
FONTI: dict[str, str] = {
    "auto": "Automatica",
    "yahoo": "Yahoo Finance",
    "justetf": "justETF",
    "eodhd": "EODHD",
    "twelvedata": "Twelve Data",
    "csv": "CSV caricato",
    "openfigi": "OpenFIGI",
    "nome": "Dedotto dal nome",
}

# Traduzione del ribilanciamento: chiavi = valori dell'enum `Rebalance` (engine.py).
RIBILANCIAMENTO: dict[str, str] = {
    "none": "Nessuno (buy & hold)",
    "monthly": "Mensile",
    "quarterly": "Trimestrale",
    "yearly": "Annuale",
}
