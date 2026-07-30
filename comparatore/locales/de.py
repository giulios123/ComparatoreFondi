"""Deutscher Katalog. Die Schlüssel müssen exakt mit
`comparatore.locales.it` übereinstimmen - `tests/test_i18n.py` prüft, dass
die vier Kataloge synchron bleiben."""

LINGUA = "de"
NOME = "Deutsch"

MESSAGGI: dict[str, str] = {
    # --- Kopfzeile -------------------------------------------------
    "app.page_title": "Fondsvergleich",
    "app.title": "📈 Fondsvergleich",
    "app.subtitle": "Backtest von Fonds und ETFs über mehrere Datenquellen, mit TER-Kostenwirkung.",

    # --- Rebalancing (Hilfe zur Auswahl) --------------------------
    "rebalance.help": (
        "Bringt die Gewichte periodisch auf die Zielwerte zurück, indem "
        "verkauft wird, was am meisten gewachsen ist, um zurückzukaufen, "
        "was zurückgeblieben ist.\n\n"
        "- **Keines (Buy & Hold)**: einmal gekauft und nie mehr angefasst. "
        "Die Gewichte driften: der Fonds mit der besten Performance "
        "gewinnt immer mehr Anteil, und das Portfolio wird zunehmend "
        "konzentrierter.\n"
        "- **Monatlich / Vierteljährlich / Jährlich**: am ersten "
        "Börsentag jeder Periode werden die Gewichte auf die "
        "Zielwerte zurückgesetzt.\n\n"
        "Der Backtest berücksichtigt weder Handelsgebühren noch die "
        "Besteuerung realisierter Kursgewinne: häufiges Rebalancing ist "
        "hier daher vorteilhafter, als es in der Realität wäre."
    ),

    # --- Seitenleiste: allgemeine Parameter ------------------------------------
    "sidebar.header": "⚙️ Parameter",
    "sidebar.lingua_label": "Sprache",
    "sidebar.periodo_caption": "Zeitraum",
    "preset.1y": "1J",
    "preset.5y": "5J",
    "preset.10y": "10J",
    "preset.20y": "20J",
    "preset.max": "Max",
    "sidebar.data_inizio": "Startdatum",
    "sidebar.data_fine": "Enddatum",
    "sidebar.valore_iniziale": "Anfangswert des Portfolios",
    "sidebar.valuta_riferimento": "Referenzwährung",
    "sidebar.ribilanciamento_label": "Rebalancing",
    "sidebar.rebalance_caption_none": (
        "Die eingestellten Gewichte sind ein Ausgangspunkt: ohne "
        "Rebalancing driften sie mit der Zeit entsprechend der relativen "
        "Renditen der Fonds."
    ),
    "sidebar.rebalance_caption_active": (
        "Die Gewichte kehren am ersten Börsentag jeder Periode zu den "
        "eingestellten Werten zurück (keine Handelskosten berücksichtigt)."
    ),

    # --- Seitenleiste: Kosten --------------------------------------------------
    "costs.subheader": "Kosten",
    "costs.caption": (
        "Die veröffentlichten NAVs sind **bereits netto der TER**. "
        "Die *Brutto*-Kurve rekonstruiert den Fonds ohne Gebühren: "
        "der Abstand zwischen den beiden Kurven ist die Kostenwirkung der TER."
    ),
    "costs.show_gross_checkbox": "Auch die Brutto-Kurve anzeigen (ohne TER)",

    # --- Seitenleiste: erweiterte Historie ------------------------------------
    "history.subheader": "Erweiterte Historie",
    "history.checkbox": "Zeitraum vor Auflegung des Fonds rekonstruieren",
    "history.help": (
        "Verlängert die Reihe rückwirkend mit einem älteren Index oder "
        "Fonds. Dies ist eine Rekonstruktion, keine echten Daten: sie "
        "erscheint in den Diagrammen gestrichelt."
    ),
    "history.caption_non_usd": (
        "⚠️ Proxys werden in Dollar notiert. Bei einer Referenzwährung "
        "ungleich USD kann die Rekonstruktion nicht vor **{anno}** "
        "zurückreichen, dem ersten Datum der offiziellen EZB-Wechselkurse."
    ),
    "history.caption_usd": "Währung USD: die Rekonstruktion kann die volle Tiefe des Proxys nutzen.",

    # --- Seitenleiste: Datenquellen -----------------------------------------------
    "sources.subheader": "Datenquellen",
    "sources.justetf_info": (
        "**Was die Aktivierung von justETF bedeutet**\n\n"
        "justETF bietet für diese Funktion keine dokumentierte "
        "öffentliche API. Wenn Sie die Integration aktivieren, versucht "
        "die App es für ISIN-identifizierte ETFs automatisch **vor "
        "Yahoo** und sendet vom Computer oder Server, auf dem die App "
        "läuft:\n\n"
        "- die ISIN des ETF, den angefragten Zeitraum und die Währung;\n"
        "- IP-Adresse und übliche technische Verbindungsdaten der "
        "HTTP-Verbindung.\n\n"
        "Es werden weder Kapital noch Portfoliogewichte, CSV-Dateien "
        "oder API-Schlüssel gesendet. Die empfangenen Reihen werden im "
        "lokalen Cache gespeichert. Der Endpunkt kann sich ändern oder "
        "seinen Dienst einstellen, seine Nutzung unterliegt den "
        "[justETF-Bedingungen]"
        "(https://www.justetf.com/it/about/legal-terms.html) und den "
        "Rechten der Datenanbieter. Die Zustimmung wird auf diesem Computer "
        "gespeichert, bis Sie sie widerrufen; bleibt das Kästchen deaktiviert, "
        "wird justETF nur kontaktiert, wenn Sie es explizit als Quelle für einen "
        "einzelnen Fonds wählen."
    ),
    "sources.justetf_checkbox": "Ich stimme automatischen Anfragen an justETF zu",
    "sources.justetf_help": (
        "Stellt justETF vor Yahoo in die automatische Reihenfolge für "
        "ISIN-identifizierte ETFs. Sie können die Zustimmung durch "
        "Deaktivieren des Kästchens widerrufen."
    ),
    "sources.status_optin_off": " — Opt-in deaktiviert",
    "sources.status_not_configured": " — nicht konfiguriert",
    "sources.order_caption": (
        "Automatische Reihenfolge: CSV → Yahoo → EODHD → Twelve Data; "
        "justETF kommt nur mit dem obigen Opt-in hinzu. Eine Quelle kann "
        "in der Tabelle immer pro Fonds erzwungen werden. Die Caches von "
        "EODHD und Twelve Data laufen nach {giorni} Tagen ab."
    ),
    "sources.eodhd_hint": (
        "Für **in Italien aufgelegte Fonds** (Mediolanum, Fineco, Banken) "
        "lohnt sich die Konfiguration von EODHD: Yahoo deckt nur einen "
        "Teil davon ab, mit Historie ab 2018. Geben Sie den Schlüssel "
        "oben ein, unter **🔑 API-Schlüssel**."
    ),
    "sources.used_caption": "📚 Verwendete Quellen: {elenco}",

    # --- Seitenleiste: API-Schlüssel -------------------------------------------------
    "api_keys.expander": "🔑 API-Schlüssel (EODHD, Twelve Data)",
    "api_keys.caption": (
        "Bleiben nur auf diesem Computer, in "
        "`.streamlit/api_keys.json` (Berechtigungen auf Ihren Benutzer "
        "beschränkt, bereits vom Repository ausgeschlossen). Sie "
        "überstehen einen Neustart und **Cache leeren** weiter unten."
    ),
    "api_keys.eodhd_label": "EODHD-Schlüssel",
    "api_keys.td_label": "Twelve-Data-Schlüssel",
    "api_keys.save_button": "Speichern",
    "api_keys.saved_toast": "Schlüssel gespeichert",
    "api_keys.saved_caption": "Gespeicherte Schlüssel: {elenco}",
    "api_keys.forget_button": "Gespeicherte Schlüssel vergessen",
    "api_keys.forgotten_toast": "Schlüssel und zugehöriger Cache entfernt",

    # --- Seitenleiste: CSV ---------------------------------------------------------
    "csv.expander": "📄 Eine Reihe aus CSV laden",
    "csv.caption": (
        "Für Fonds, die von keiner Quelle abgedeckt werden. Zwei Spalten: "
        "Datum und Anteilswert. Trennzeichen, Dezimalzeichen und "
        "Datumsformat werden automatisch erkannt."
    ),
    "csv.symbol_label": "Symbol oder ISIN, dem sie zugeordnet werden soll",
    "csv.symbol_placeholder": "z. B. IT0001234567",
    "csv.currency_label": "Währung der Reihe",
    "csv.file_label": "CSV-Datei",
    "csv.success": "{n} Beobachtungen vom {inizio} bis {fine}.",
    "csv.loaded_caption": "Geladen: {elenco}",
    "csv.remove_button": "Geladene Reihen entfernen",

    # --- Seitenleiste: Cache, Lizenzen, risikofreier Zins ------------------------------------
    "cache.caption": "💾 Cache auf Festplatte: {n} Reihen, {mb:.1f} MB",
    "cache.clear_button": "Cache leeren",
    "cache.cleared_toast": "Cache geleert",
    "sidebar.risk_free_label": "Jährlicher risikofreier Zins (für Sharpe)",

    # --- Seitenleiste: Informationen und Lizenzen --------------------------------------
    "about.expander": "ℹ️ Informationen und Lizenzen",
    "about.version": "Fondsvergleich Version {versione}",
    "about.license_caption": (
        "Quellcode lizenziert unter "
        "[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)."
    ),
    "about.third_party_header": "Bibliotheken von Drittanbietern",
    "about.third_party_caption": (
        "Das Projekt verwendet die unten aufgeführten Bibliotheken, jede "
        "unter ihrer eigenen Lizenz. Der vollständige Text, einschließlich "
        "rechtlicher Hinweise, befindet sich in der herunterladbaren Datei."
    ),
    "about.third_party_missing": (
        "Lizenzliste in dieser Installation nicht verfügbar."
    ),
    "about.download_button": "⬇️ Lizenzen von Drittanbietern herunterladen (.txt)",
    "about.col_package": "Paket",
    "about.col_version": "Version",
    "about.col_license": "Lizenz",

    # --- Seitenleiste: Portfolio (Export/Import) ---------------------------------
    "portfolio_io.expander": "💼 Portfolio: speichern und laden",
    "portfolio_io.caption": (
        "Speichert Fonds, Gewichte und Backtest-Parameter in einer Datei, "
        "um sie in einer anderen Sitzung oder auf einem anderen Computer "
        "wieder zu öffnen."
    ),
    "portfolio_io.download_button": "⬇️ Portfolio herunterladen (.json)",
    "portfolio_io.download_empty_hint": "Fügen Sie mindestens einen Fonds hinzu, um es herunterzuladen.",
    "portfolio_io.upload_label": "Ein Portfolio laden (.json)",
    "portfolio_io.import_success": "Portfolio geladen: {n} Fonds.",
    "portfolio_io.import_error": "Ungültige Datei: {errore}",

    # --- Suche --------------------------------------------------------------
    "search.expander": "🔎 Fonds und ETFs suchen",
    "search.query_label": "Name, Ticker oder ISIN",
    "search.query_placeholder": "z. B. 'Vanguard S&P 500', 'VUSA.AS' oder 'IE00B3XXRP09'",
    "search.funds_only_toggle": "Nur Fonds/ETFs",
    "search.spinner": "Suche läuft…",
    "search.no_results": "Keine Ergebnisse. Versuchen Sie die ISIN oder den vollständigen Ticker.",
    "search.isin_hint": (
        "🔗 Die ISIN erlaubt die Nutzung von justETF nur, wenn Sie das "
        "Opt-in unter Datenquellen aktiviert oder die Quelle für den "
        "einzelnen Fonds gewählt haben."
    ),
    "search.add_button": "Hinzufügen",

    # --- Toast ------------------------------------------------------------------
    "toast.fund_exists": "{symbol} ist bereits im Portfolio",
    "toast.fund_added": "{symbol} hinzugefügt",
    "toast.fund_removed": "{elenco} entfernt",

    # --- Portfoliozusammensetzung ---------------------------------------------------
    "portfolio.subheader": "Portfoliozusammensetzung",
    "portfolio.empty_hint": "Suchen und fügen Sie mindestens einen Fonds hinzu, um zu beginnen.",

    "editor.col_fondo": "Fonds",
    "editor.col_simbolo": "Symbol",
    "editor.col_isin": "ISIN",
    "editor.col_valuta": "Währung",
    "editor.col_peso": "Gewicht %",
    "editor.col_ter": "TER %",
    "editor.col_extra": "Zusatzkosten %",
    "editor.col_fonte": "Quelle",
    "editor.col_proxy": "Historien-Proxy",
    "editor.isin_help": (
        "Wird benötigt, um justETF zu nutzen, wenn die Quelle aktiviert "
        "oder explizit für den Fonds ausgewählt ist."
    ),
    "editor.peso_help": "Dem Fonds zugewiesener Anteil des Portfolios.",
    "editor.ter_help": (
        "Laufende jährliche Kosten. Vorausgefüllt, wenn die Quelle sie "
        "liefert: immer im KID des Fonds prüfen."
    ),
    "editor.extra_help": (
        "Jährliche Kosten, die NICHT bereits im NAV enthalten sind "
        "(Verwahrung, Beratung). Werden von der Performance abgezogen."
    ),
    "editor.fonte_help": "'Automatisch' probiert die Quellen in Prioritätsreihenfolge.",
    "editor.proxy_help": (
        "Älteres Instrument, mit dem der Zeitraum vor Auflegung des "
        "Fonds rekonstruiert wird."
    ),
    "editor.equalize_button": "⚖️ Gleiche Gewichte",
    "editor.clear_button": "🗑️ Leeren",
    "editor.total_weight_metric": "Gesamtgewicht",

    # --- Warnungen zu TER, Gewichten, Daten -------------------------------------------------
    "ter_warning.reason_eodhd_blocked": (
        "der konfigurierte EODHD-Plan enthält `/fundamentals` nicht (ein "
        "kostenpflichtiger Plan ist erforderlich), daher stammen weder "
        "TER noch Klassifikation von dort. "
    ),
    "ter_warning.reason_none": "keine konfigurierte Quelle stellt sie für diese Instrumente bereit. ",
    "ter_warning.message": (
        "TER nicht gefunden für: {elenco}. {motivo}"
        "Tragen Sie sie manuell aus dem KID ein, um die Kostenwirkung zu sehen."
    ),
    "weight.error_zero": "Weisen Sie mindestens ein Gewicht größer als null zu.",
    "weight.warning_normalized": "Die Gewichte summieren sich auf {tot:.1f}%: sie werden auf 100% normiert.",
    "dates.error_order": "Das Startdatum muss vor dem Enddatum liegen.",

    # --- Kursabruf -----------------------------------------------------------------
    "prices.spinner": "Historische Reihen werden heruntergeladen…",
    "prices.error_none": "Keine Kursdaten für die ausgewählten Fonds verfügbar.",
    "prices.missing_expander": "🚫 {n} Fonds ohne Daten",
    "prices.missing_hint": (
        "Vorschlag: eine CSV-Reihe laden oder, nach Prüfung der "
        "Nutzungsbedingungen, justETF aktivieren und die ISIN eingeben."
    ),

    # --- Währungsumrechnung -------------------------------------------------------
    "fx.error_none": "Keine in die Referenzwährung konvertierbare Reihe.",
    "fx.error_failed": "Vom Backtest ausgeschlossen (Währung nicht auflösbar): {elenco}.",
    "fx.error_failed_eodhd_cause": (
        " Der konfigurierte EODHD-Plan enthält `/fundamentals` nicht (ein "
        "kostenpflichtiger Plan ist erforderlich): falls diese Fonds aus "
        "einer EODHD-Suche stammen, prüfen Sie, ob sie auch bei Yahoo "
        "unter einem anderen Symbol existieren, oder laden Sie eine "
        "CSV-Reihe und geben Sie die Währung selbst an."
    ),
    "fx.converted_caption": "💱 Zu {ccy} umgerechnet, zu täglichen Wechselkursen: {elenco}",
    "fx.truncated_detail_item": "{symbol} ab dem {data}",
    "fx.truncated_warning": (
        "Wechselkurse nur ab einem späteren Datum als dem angeforderten "
        "verfügbar: {dettaglio}. Der Zeitraum wurde verkürzt, statt einen "
        "rückwirkend aufgefüllten Kurs zu verwenden."
    ),

    # --- Erweiterte Historie (Ausführungsblock) ------------------------------------------
    "history.expander": "🧩 Rekonstruierte Historie",
    "history.reconstructing_spinner": "Historie von {symbol} wird mit {proxy} rekonstruiert…",
    "history.proxy_unavailable": "{symbol}: Proxy {proxy} nicht verfügbar",
    "history.proxy_not_older": (
        "{symbol}: {proxy} ist nicht älter als der Fonds, nichts zu rekonstruieren"
    ),
    "history.reconstructed_note": "**{symbol}** ab {data} rekonstruiert mit {proxy_label}{caveat}",
    "history.reconstructed_caption": (
        "Rekonstruierte Abschnitte sind Schätzungen auf Basis eines "
        "anderen Instruments als des Fonds, keine echten Daten. Sie "
        "erscheinen in den Diagrammen gestrichelt."
    ),
    "proxy.caveat_price_only": (
        "reiner Kursindex: der rekonstruierte Abschnitt schließt "
        "Dividenden aus und unterschätzt die Rendite"
    ),
    "coverage_warning": "{symbol}: Daten erst ab {data} verfügbar",

    # --- Backtest-Ergebnisse --------------------------------------------------------
    "results.subheader": "Ergebnisse · {inizio} → {fine}",
    "results.reconstructed_info": (
        "🧩 Die obigen Kennzahlen beziehen den rekonstruierten Zeitraum "
        "({inizio} → {fine}) mit ein: sie sind indikativ, nicht die "
        "tatsächlich von den Fonds erzielte Performance."
    ),
    "metrics.explainer_expander": "❓ Wie diese Kennzahlen zu lesen sind",
    "costs.impact_info": (
        "💸 **TER-Auswirkung**: über {anni:.1f} Jahre haben die laufenden "
        "Gebühren **{costo}** gekostet, entsprechend **{pct}** des "
        "Betrags, den Sie ohne Kosten gehabt hätten ({lordo} brutto "
        "gegenüber {netto} netto)."
    ),

    # --- Hilfetexte zu den Kennzahlen ---------------------------------------------------
    "help.valore_finale": (
        "Wie viel aus den anfänglichen {capitale} am Ende des Zeitraums "
        "geworden wäre, netto der TER."
    ),
    "help.rendimento_totale": (
        "Gesamtveränderung über den gesamten Zeitraum, **nicht** annualisiert."
    ),
    "help.cagr": (
        "Durchschnittliche jährliche Wachstumsrate: der konstante Zinssatz, "
        "der, jedes Jahr angewendet, vom Anfangswert zum Endwert in der "
        "tatsächlich verstrichenen Zeit führt."
    ),
    "help.volatilita": (
        "Annualisierte Schwankung der Tagesrenditen (Standardabweichung × "
        "√252). Zeigt, wie unruhig der Verlauf war, nicht wie viel "
        "verdient wurde: zwei Kurven mit demselben CAGR können sehr "
        "unterschiedliche Volatilität haben."
    ),
    "help.sharpe": (
        "Überschussrendite über dem risikofreien Zins (derzeit "
        "{rf_pct}) pro Einheit eingegangener Volatilität. Über 1 gilt "
        "generell als gutes Ergebnis."
    ),
    "help.sortino": (
        "Wie Sharpe (risikofreier Zins {rf_pct}), aber im Nenner zählt "
        "nur die Abwärtsschwankung: bestraft keine starken Anstiege, "
        "nur Rückgänge."
    ),
    "help.max_drawdown": (
        "Der schlimmste Rückgang von einem vorherigen historischen Hoch "
        "bis zum darauffolgenden Tief: der tiefste Verlust, den man "
        "investiert bleibend hätte ertragen müssen."
    ),
    "help.calmar": (
        "CAGR geteilt durch den Max Drawdown im Absolutwert: erzielte "
        "Rendite pro Einheit erlittenen maximalen Verlusts."
    ),
    "help.miglior_anno": "Die beste Kalenderjahres-Rendite im Zeitraum.",
    "help.peggior_anno": "Die schlechteste Kalenderjahres-Rendite im Zeitraum.",
    "help.costo_ter": (
        "Differenz, in {ccy}, am Ende des Zeitraums zwischen dem Betrag "
        "ohne Gebühren (Brutto-Kurve) und dem tatsächlich erzielten "
        "(Netto-Kurve)."
    ),
    "help.ricostruito": (
        "Diese Zeile enthält einen mit einem Proxy-Instrument geschätzten "
        "Abschnitt, keine echten Fondsdaten: ihre Kennzahlen sind als "
        "indikativ zu lesen."
    ),

    # --- Diagramme (Tab Portfolio) -----------------------------------------------------
    "chart.legend_reconstructed": "Portfolio (rekonstruiert)",
    "chart.legend_net": "Portfolio (netto TER)",
    "chart.legend_gross": "Portfolio (brutto, ohne TER)",
    "chart.hover_reconstructed_suffix": " (rekonstruiert)",
    "chart.annotation_real_start": "Beginn echter Daten",
    "chart.annotation_initial_capital": "Anfangskapital",
    "chart.legend_synthetic": "{comparto} (synthetisch)",
    "chart.hover_constant_growth": " · konstantes Wachstum",
    "chart.yaxis_value": "Wert ({ccy})",
    "chart.composition_header": "**Zusammensetzung im Zeitverlauf**",
    "chart.synthetic_caption": (
        "⚠️ Die Kurven der Pensionsfonds sind **Geraden mit konstantem "
        "Wachstum**, abgeleitet aus der durchschnittlichen jährlichen "
        "COVIP-Rendite: sie zeigen, wo man angekommen wäre, nicht wie man "
        "dorthin gelangt wäre. Der reale Verlauf schwankte, aber COVIP "
        "veröffentlicht keine historischen Reihen."
    ),
    "chart.weights_set_final": "Eingestellte Gewichte: {pesi} → am Ende des Zeitraums: {pesi_finali}.",
    "chart.rebalance_caption_active": (
        "{tipo} Rebalancing: {n} Eingriffe im Zeitraum, der letzte am "
        "{data} (eingestellte Gewichte: {pesi})."
    ),
    "chart.rebalance_caption_none_yet": (
        "{tipo} Rebalancing: noch kein Eingriff ausgelöst, der gewählte "
        "Zeitraum ist kürzer als die erste Fälligkeit."
    ),

    # --- Tabs -----------------------------------------------------------------------------
    "tab.portafoglio": "📊 Portfolio",
    "tab.bilanciamento": "⚖️ Aufteilung",
    "tab.confronto": "🆚 Fondsvergleich",
    "tab.drawdown": "📉 Drawdown",
    "tab.dati": "📋 Daten",
    "tab.previdenza": "🏦 Pensionsfonds",

    # --- Tab Aufteilung -----------------------------------------------------------------
    "bilancio.header": "**Klassifikation**",
    "bilancio.col_classe": "Klasse",
    "bilancio.col_area": "Region",
    "bilancio.col_settore": "Sektor",
    "bilancio.col_valuta": "Währung",
    "bilancio.peso_help": "Wird in der Zusammensetzungstabelle oben auf der Seite bearbeitet.",
    "bilancio.tendina_help": (
        "**{automatica}** behält die abgeleitete Klassifikation bei, die "
        "sich auf mehrere Einträge aufteilen kann (ein globaler Fonds "
        "ist nicht vollständig einer Region zuzuordnen). Die Wahl eines "
        "Eintrags weist ihm das gesamte Instrument zu."
    ),
    "bilancio.provenienza_prefix": "🏷️ Klassifikation: ",
    "bilancio.provenienza_eodhd": "**{n}** von EODHD",
    "bilancio.provenienza_yahoo": "**{n}** von Yahoo",
    "bilancio.provenienza_nome": "**{n}** aus dem Namen abgeleitet",
    "bilancio.provenienza_manuali": "**{n}** mit manuellen Korrekturen",
    "bilancio.titolo_classe": "Anlageklasse",
    "bilancio.titolo_area": "Geografische Region",
    "bilancio.titolo_settore": "Sektor",
    "bilancio.titolo_valuta": "Notierungswährung",
    "bilancio.titolo_paesi": "Länder (Schätzung anhand der Top-Positionen)",
    "bilancio.dettaglio_expander": "🔍 Detail je Instrument",
    "bilancio.col_strumento": "Instrument",
    "bilancio.posizioni_expander": "📌 Wichtigste Positionen",
    "bilancio.posizioni_caption": (
        "Die von Yahoo für jeden Fonds gelesenen Top-Positionen (ETFs und "
        "als solche erkannte Investmentfonds): die Grundlage der "
        "geografischen Schätzung oben, auch nützlich, um Überschneidungen "
        "zwischen verschiedenen Fonds zu sehen."
    ),
    "bilancio.col_titolo": "Titel",
    "bilancio.col_peso_nel_fondo": "Gewicht im Fonds",
    "bilancio.posizioni_none": (
        "Keine Positionen für die Fonds im Portfolio verfügbar: dafür "
        "sind Zusammensetzungsdaten von Yahoo nötig, die nicht immer "
        "vorhanden sind."
    ),
    "bilancio.esclusi_caption_one": (
        "ℹ️ {elenco}: zählt in der Aufteilung, aber nicht im Backtest, "
        "mangels Kursen."
    ),
    "bilancio.esclusi_caption_many": (
        "ℹ️ {elenco}: zählen in der Aufteilung, aber nicht im Backtest, "
        "mangels Kursen."
    ),
    "bilancio.disclaimer": (
        "⚠️ Die automatische Klassifikation ist **indikativ** und sollte "
        "im KID überprüft werden: ohne EODHD (mit Schlüssel) und ohne "
        "Zusammensetzungsdaten von Yahoo wird sie aus dem Namen des "
        "Fonds abgeleitet, was oft nicht ausreicht. Das **Länder**-Donut "
        "ist eine Schätzung nur anhand der von Yahoo gelesenen "
        "Top-Positionen (in der Regel ein Fünftel oder Viertel des "
        "Fonds): die vollständige geografische Aufteilung erfordert "
        "einen kostenpflichtigen EODHD-Plan. Die **Währung** ist die "
        "Notierungswährung, nicht das Währungsrisiko: ein auf den "
        "Weltmarkt ausgerichteter, in Euro notierter ETF bleibt dem "
        "Dollar ausgesetzt."
    ),

    # --- Tab Fondsvergleich -----------------------------------------------------------------
    "confronto.caption": (
        "Verlauf von {capitale}, vollständig in jeden Fonds investiert, "
        "für einen Vergleich bei gleichem Kapital."
    ),
    "confronto.legend_reconstructed": "{col} (rekonstruiert)",
    "confronto.legend_gross": "{col} (brutto)",
    "confronto.col_valore_finale": "Endwert (von {capitale})",
    "confronto.stesso_capitale_caption": (
        "Jede Zeile startet mit demselben Kapital: **{capitale}**, zu 100% "
        "in einen einzigen Fonds investiert, und dieselben **{capitale}**, "
        "in das Portfolio mit den eingestellten Gewichten und dem "
        "gewählten Rebalancing investiert. Die Endwerte sind daher Zeile "
        "für Zeile direkt vergleichbar."
    ),
    "confronto.footnote": (
        "Die Spalte *Rekonstruiert* markiert Zeilen, deren Kennzahlen "
        "einen von einem Proxy geschätzten Zeitraum enthalten."
    ),
    "confronto.riga_portafoglio": "🎯 PORTFOLIO",
    "si": "ja",
    "no": "nein",
    "nd": "k. A.",

    # --- Tab Drawdown -----------------------------------------------------------------------
    "drawdown.legend_portafoglio": "Portfolio",
    "drawdown.yaxis": "Drawdown (%)",
    "drawdown.yearly_header": "**Renditen nach Kalenderjahr**",
    "drawdown.yaxis_yearly": "Rendite (%)",

    # --- Tab Daten -----------------------------------------------------------------------------
    "dati.col_netto": "Portfolio (netto)",
    "dati.col_lordo": "Portfolio (brutto)",
    "dati.col_solo_prefix": "Nur ",
    "dati.download_button": "⬇️ Vollständige CSV herunterladen",

    # --- Tab Pensionsfonds -----------------------------------------------------------------
    "previdenza.header_con_anno": "### Betriebliche Altersvorsorge · COVIP-Daten zum 31.12.{anno}",
    "previdenza.header_senza_anno": "### Betriebliche Altersvorsorge · COVIP-Daten",
    "previdenza.fiscalita_warning": (
        "**Der Vergleich berücksichtigt keine Besteuerung.** "
        "Pensionsfonds genießen eine Abzugsfähigkeit bis 5.164,57 € pro "
        "Jahr, eine Besteuerung der Erträge mit 20% statt 26% und eine "
        "Abgeltungssteuer, die von 15% auf 9% sinkt. Das sind Vorteile "
        "zu ihren Gunsten, daher **unterschätzen** die untenstehenden "
        "Zahlen sie."
    ),
    "previdenza.rendimenti_caption": (
        "COVIP veröffentlicht nur durchschnittliche jährliche Renditen "
        "über feste Horizonte, keine historischen Reihen: für diese "
        "Instrumente können Volatilität, Drawdown und Sharpe aus keinen "
        "öffentlichen Daten berechnet werden. Um sie zu erhalten, laden "
        "Sie den Anteilswert Ihres Fonds über den CSV-Upload in der "
        "Seitenleiste hoch."
    ),
    "previdenza.catalogo_error": (
        "COVIP-Katalog nicht verfügbar: Verbindung prüfen und erneut versuchen."
    ),
    "previdenza.forma_label": "Vorsorgeform",
    "previdenza.col_tipo": "Typ",
    "previdenza.riga_portafoglio": "🎯 IHR PORTFOLIO",
    "previdenza.categoria_label": "Kategorie",
    "previdenza.cerca_label": "Nach Fonds- oder Gesellschaftsname suchen",
    "previdenza.cerca_placeholder": "z. B. 'previgest', 'cometa', 'mediolanum'",
    "previdenza.risultati_caption": "{n} Teilfonds entsprechen den Filtern.",
    "previdenza.comparti_label": "Zu vergleichende Teilfonds",
    "previdenza.seleziona_hint": (
        "Wählen Sie einen oder mehrere Teilfonds, um sie mit Ihrem "
        "Portfolio zu vergleichen."
    ),
    "previdenza.rendimento_header": "**Durchschnittliche jährliche Rendite, auf denselben COVIP-Fenstern**",
    "previdenza.col_help_orizzonte": (
        "Durchschnittliche jährliche COVIP-Rendite über das {anni}-Jahres-Fenster ({periodo})."
    ),
    "previdenza.col_isc": "ISC 10J",
    "previdenza.col_help_isc": (
        "Das Äquivalent der TER für die Altersvorsorge: jährliche "
        "Kostenwirkung über den 10-Jahres-Horizont."
    ),
    "previdenza.mancanti_caption": (
        "Ihr Portfolio zeigt **k. A.** für {elenco_anni}, da es das "
        "gesamte Fenster nicht abdeckt ({dettaglio}). Eine Berechnung "
        "über einen kürzeren Zeitraum würde eine nicht vergleichbare "
        "Zahl ergeben."
    ),
    "previdenza.anni_suffix": "{a} Jahre",
    "previdenza.il_tuo_portafoglio": "Ihr Portfolio",
    "previdenza.yaxis_rendimento": "Durchschnittliche jährliche Rendite (%)",
    "previdenza.costi_header": "**Wie stark die Kosten wiegen**",
    "previdenza.col_comparto": "Teilfonds",
    "previdenza.col_isc_annuo": "Jährliche ISC",
    "previdenza.col_rendimento_10a": "Rendite 10J",
    "previdenza.col_eroso": "Aufgezehrt bei {capitale} über 10 Jahre",
    "previdenza.col_quota_rendimento": "Anteil der Rendite",
    "previdenza.costi_caption": (
        "Die ISC ist das Äquivalent der TER für die Altersvorsorge. Die "
        "letzte Spalte zeigt, welcher Anteil der erzielten Nettorendite "
        "jedes Jahr durch Kosten aufgezehrt wird."
    ),
    "previdenza.curve_checkbox": "Pensionsfonds-Kurven im Portfoliodiagramm anzeigen",
    "previdenza.curve_help": (
        "Geraden mit konstantem Wachstum, abgeleitet aus der "
        "durchschnittlichen jährlichen Rendite: sie zeigen den Endpunkt, "
        "nicht den Verlauf."
    ),
    "previdenza.orizzonte_label": "Horizont, aus dem der Zinssatz abgeleitet wird",
    "previdenza.fonte_caption": (
        "Quelle: [COVIP](https://www.covip.it/open-data), offene Daten "
        "unter der Lizenz "
        "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Das "
        "Projekt normalisiert und aggregiert die Datensätze und berechnet "
        "Vergleiche und synthetische Kurven; diese Auswertungen sind "
        "keine originalen COVIP-Daten."
    ),

    # --- Fußzeile --------------------------------------------------------------------------
    "footer.disclaimer": (
        "*Total-Return*-Kurse (Dividenden reinvestiert). Die NAVs der "
        "Fonds sind bereits netto der TER; die Brutto-Kurve ist eine "
        "theoretische Rekonstruktion. Die Wechselkurse sind die "
        "offiziellen EZB-Kurse seit 1999, bezogen über Frankfurter, mit "
        "Rückgriff auf Yahoo für Währungen außerhalb des Korbs. Ein- und "
        "Ausstiegskosten, Spreads und Besteuerung werden nicht "
        "berücksichtigt. Vergangene Performance ist kein Indikator für "
        "zukünftige Ergebnisse."
    ),
}

METRICHE: dict[str, str] = {
    "final_value": "Endwert",
    "total_return": "Gesamtrendite",
    "cagr": "CAGR",
    "volatility": "Volatilität",
    "sharpe": "Sharpe",
    "sortino": "Sortino",
    "max_drawdown": "Max Drawdown",
    "calmar": "Calmar",
    "best_year": "Bestes Jahr",
    "worst_year": "Schlechtestes Jahr",
    "ter_cost": "TER-Kosten",
    "reconstructed": "Rekonstruiert",
}

ESITI: dict[str, str] = {
    "ok": "ok",
    "no_data": "keine Daten",
    "not_configured": "nicht konfiguriert",
    "isin_required": "ISIN erforderlich",
}

TERMINI: dict[str, str] = {
    "Azionario": "Aktien",
    "Obbligazionario": "Anleihen",
    "Liquidità": "Liquidität",
    "Materie prime": "Rohstoffe",
    "Immobiliare": "Immobilien",
    "Non classificato": "Nicht klassifiziert",
    "Globale": "Global",
    "Nord America": "Nordamerika",
    "Europa": "Europa",
    "Italia": "Italien",
    "Giappone": "Japan",
    "Asia-Pacifico": "Asien-Pazifik",
    "Mercati emergenti": "Schwellenländer",
    "Diversificato": "Diversifiziert",
    "Tecnologia": "Technologie",
    "Finanza": "Finanzwesen",
    "Sanità": "Gesundheitswesen",
    "Energia": "Energie",
    "Industria": "Industrie",
    "Beni di consumo": "Konsumgüter",
    "Utility": "Versorger",
    "Materiali": "Materialien",
    "Comunicazioni": "Kommunikation",
    "Resto del fondo": "Restlicher Fonds",
    "(automatica)": "(automatisch)",
    "(nessuno)": "(keiner)",
    "Taiwan": "Taiwan",
    "Hong Kong": "Hongkong",
    "Corea del Sud": "Südkorea",
    "India": "Indien",
    "Regno Unito": "Vereinigtes Königreich",
    "Svizzera": "Schweiz",
    "Australia": "Australien",
    "Paesi Bassi": "Niederlande",
    "Germania": "Deutschland",
    "Spagna": "Spanien",
    "Francia": "Frankreich",
    "Canada": "Kanada",
    "Cina": "China",
    "Danimarca": "Dänemark",
    "Svezia": "Schweden",
    "Norvegia": "Norwegen",
    "Brasile": "Brasilien",
    "Messico": "Mexiko",
    "Stati Uniti": "Vereinigte Staaten",
}

FONTI: dict[str, str] = {
    "auto": "Automatisch",
    "yahoo": "Yahoo Finance",
    "justetf": "justETF",
    "eodhd": "EODHD",
    "twelvedata": "Twelve Data",
    "csv": "Hochgeladene CSV",
    "openfigi": "OpenFIGI",
    "nome": "Aus dem Namen abgeleitet",
}

RIBILANCIAMENTO: dict[str, str] = {
    "none": "Keines (Buy & Hold)",
    "monthly": "Monatlich",
    "quarterly": "Vierteljährlich",
    "yearly": "Jährlich",
}
