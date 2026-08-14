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

    # --- Seitenleiste: Sparplan (PAC) -------------------------------------
    "pac.rebalance_caption": (
        "Eine wiederkehrende Einzahlung fließt zu den Zielgewichten: das "
        "wirkt wie ein sanftes Rebalancing, daher driftet das Portfolio im "
        "Rebalancing-Modus Keines weniger, als es ohne Sparplan tun würde."
    ),
    "pac.expander": "📅 Wiederkehrende Einzahlungen (Sparplan)",
    "pac.enable_checkbox": "Sparplan aktivieren",
    "pac.help": (
        "Fügt dem Anfangskapital wiederkehrende Einzahlungen hinzu. Bei "
        "aktivem Sparplan bleibt die Rendite des Instruments (CAGR, "
        "Sharpe, Drawdown, ...) ohne die Einzahlungen berechnet; der XIRR "
        "misst dagegen die Rendite Ihres Geldes, Einzahlungen inbegriffen."
    ),
    "pac.amount_label": "Betrag je Einzahlung",
    "pac.amount_help": "Der bei jeder Fälligkeit eingezahlte Betrag, in der Basiswährung.",
    "pac.frequency_label": "Häufigkeit",
    "pac.step_up_label": "Jährliche Erhöhung der Rate (%)",
    "pac.step_up_help": (
        "Erhöht die Rate einmal im Jahr um diesen Prozentsatz, z. B. um "
        "die Inflation oder das Gehaltswachstum abzubilden."
    ),
    "pac.limit_window_checkbox": "Einzahlungen auf einen Zeitraum begrenzen",
    "pac.start_label": "Erste Einzahlung",
    "pac.end_label": "Letzte Einzahlung",

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
    "history.caption_usd": (
        "Währung USD: die Rekonstruktion kann die volle Tiefe des Proxys nutzen."
    ),

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
    "sidebar.risk_free_label": "Jährlicher risikofreier Zins % (für Sharpe)",

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
    "about.credit": "Mit Neugier erstellt von [Giulio](https://www.gshake.net)",

    # --- Seitenleiste: Portfolio (Export/Import) ---------------------------------
    "portfolio_io.expander": "💼 Portfolio: speichern und laden",
    "portfolio_io.caption": (
        "Speichert Fonds, Gewichte und Backtest-Parameter in einer Datei, "
        "um sie in einer anderen Sitzung oder auf einem anderen Computer "
        "wieder zu öffnen."
    ),
    "portfolio_io.download_button": "⬇️ Portfolio herunterladen (.json)",
    "portfolio_io.download_empty_hint": (
        "Fügen Sie mindestens einen Fonds hinzu, um es herunterzuladen."
    ),
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

    "editor.col_rimuovi": "Entfernen",
    "editor.col_fondo": "Fonds",
    "editor.col_simbolo": "Symbol",
    "editor.col_isin": "ISIN",
    "editor.col_valuta": "Währung",
    "editor.col_distribuzione": "Ausschüttung",
    "editor.col_replica": "Replikation",
    "editor.col_peso": "Gewicht %",
    "editor.col_importo": "Betrag ({ccy})",
    "editor.col_ter": "TER %",
    "editor.col_extra": "Zusatzkosten %",
    "editor.col_fonte": "Quelle",
    "editor.col_proxy": "Historien-Proxy",
    "metadata.distribution_accumulating": "Thesaurierend",
    "metadata.distribution_distributing": "Ausschüttend",
    "metadata.replication_physical": "Physisch",
    "metadata.replication_synthetic": "Synthetisch",
    "editor.rimuovi_help": (
        "Entfernt den Fonds aus dem Portfolio und verteilt sein Gewicht "
        "proportional auf die übrigen."
    ),
    "editor.isin_help": (
        "Wird benötigt, um justETF zu nutzen, wenn die Quelle aktiviert "
        "oder explizit für den Fonds ausgewählt ist."
    ),
    "editor.peso_help": (
        "Dem Fonds zugewiesener Anteil des Portfolios. Bei Änderung passen "
        "sich die anderen Gewichte automatisch im Verhältnis zueinander an, "
        "sodass die Summe bei 100% bleibt."
    ),
    "editor.importo_help": (
        "Dem Fonds zugewiesenes Kapital in dieser Währung. Bei Änderung werden "
        "die Gewichte und der Anfangswert des Portfolios aktualisiert."
    ),
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
    "editor.total_value_metric": "Investiertes Kapital",

    # --- Warnungen zu TER, Gewichten, Daten -------------------------------------------------
    "ter_warning.reason_eodhd_blocked": (
        "der konfigurierte EODHD-Plan enthält `/fundamentals` nicht (ein "
        "kostenpflichtiger Plan ist erforderlich), daher stammen weder "
        "TER noch Klassifikation von dort. "
    ),
    "ter_warning.reason_none": (
        "keine konfigurierte Quelle stellt sie für diese Instrumente bereit. "
    ),
    "ter_warning.message": (
        "TER nicht gefunden für: {elenco}. {motivo}"
        "Tragen Sie sie manuell aus dem KID ein, um die Kostenwirkung zu sehen."
    ),
    "weight.error_zero": "Weisen Sie mindestens ein Gewicht größer als null zu.",
    "weight.warning_normalized": (
        "Die Gewichte summieren sich auf {tot:.1f}%: sie werden auf 100% normiert."
    ),
    "weight.error_importo_min": (
        "Das Gesamtkapital des Portfolios darf nicht unter {minimo} fallen."
    ),
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

    # --- Integrität des Backtests --------------------------------------------------------
    "engine.error_quote_non_valide": (
        "Ungültige Kurse (null, negativ oder nicht endlich) für: {elenco}."
    ),
    "engine.error_date_duplicate": "Doppelte Daten in der Kurshistorie für: {elenco}.",
    "engine.error_simboli_duplicati": "Doppelte Symbole im Portfolio: {elenco}.",
    "engine.error_simboli_senza_prezzi": "Keine Kursdaten verfügbar für: {elenco}.",
    "engine.error_pesi_non_validi": "Ungültige Gewichtung für: {elenco}.",
    "integrita.error_fondi_assenti": (
        "🚫 Der Backtest kann nicht starten: keine Kursdaten für {elenco}. Ein "
        "vorübergehendes Problem der Quelle würde sonst die tatsächlich "
        "simulierte Allokation ändern, ohne dass Sie es entscheiden."
    ),
    "integrita.allocazione_reale": (
        "Ohne diese Fonds würde das Portfolio so aussehen: {elenco}."
    ),
    "integrita.button_rimuovi": "Fonds ohne Daten entfernen und fortfahren",

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
    "help.pac_saldo": (
        "Was das Portfolio am Ende wert ist, Einzahlungen inklusive: "
        "die Summe aus Eingezahltem und Gewinn."
    ),
    "help.pac_versato": "Anfangskapital plus alle bisher geleisteten Einzahlungen.",
    "help.pac_guadagno": "Endwert des Portfolios abzüglich der insgesamt eingezahlten Summe.",
    "help.pac_xirr": (
        "Jährliche Rendite Ihres Geldes (XIRR): anders als der CAGR "
        "berücksichtigt sie den Zeitpunkt jeder Einzahlung, nicht nur das "
        "Anfangskapital."
    ),

    # --- Diagramme (Tab Portfolio) -----------------------------------------------------
    "chart.legend_reconstructed": "Portfolio (rekonstruiert)",
    "chart.legend_net": "Portfolio (netto TER)",
    "chart.legend_gross": "Portfolio (brutto, ohne TER)",
    "chart.hover_reconstructed_suffix": " (rekonstruiert)",
    "chart.annotation_real_start": "Beginn echter Daten",
    "chart.annotation_initial_capital": "Anfangskapital",
    "chart.legend_invested": "Kumulierte Einzahlungen",
    "chart.legend_pic": "Einmalanlage",
    "chart.pic_caption": (
        "Die Linie **Einmalanlage** zeigt, wie es gelaufen wäre, wenn derselbe "
        "Betrag, den der Sparplan über die Zeit einzahlt ({totale}), am ersten "
        "Tag auf einen Schlag angelegt worden wäre: **{valore_pic}** gegenüber "
        "**{valore_pac}** beim Sparplan. Ein hypothetischer Vergleich: er "
        "setzt voraus, dass die ganze Summe sofort verfügbar war."
    ),
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
    "chart.weights_set_final": (
        "Eingestellte Gewichte: {pesi} → am Ende des Zeitraums: {pesi_finali}."
    ),
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

    "bilancio.overlap_expander": "🔗 Überschneidung der Positionen",
    "bilancio.overlap_caption": (
        "Die Überschneidung summiert nur erkannte Positionen: Bei teilweiser "
        "Abdeckung ist sie eine Untergrenze; der unbekannte Anteil bleibt sichtbar."
    ),
    "bilancio.overlap_fund": "Fonds",
    "bilancio.overlap_coverage": "Bekannte Abdeckung",
    "bilancio.overlap_source": "Quelle der Positionen",
    "bilancio.overlap_date": "Datum",
    "bilancio.overlap_note": "Hinweis",
    "bilancio.overlap_unknown_date": "Datum nicht angegeben",
    "bilancio.overlap_stale": "veraltete Daten",
    "bilancio.overlap_ambiguous": "{n} mehrdeutige Identitäten",
    "bilancio.overlap_unavailable": "unzureichende Daten",
    "bilancio.overlap_ok": "verfügbar",
    "bilancio.overlap_matrix_header": "**Matrix: beobachtete Überschneidung (Untergrenze)**",
    "bilancio.overlap_lower_bound": "Untergrenze, keine vollständige Überschneidung",
    "bilancio.overlap_pair": "Paar",
    "bilancio.overlap_value": "Beobachtete Überschneidung",
    "bilancio.overlap_pair_coverage": "Abdeckung",
    "bilancio.overlap_exposure_header": "**Aggregierte Exposition gegenüber bekannten Positionen**",
    "bilancio.overlap_position": "Position",
    "bilancio.overlap_portfolio_weight": "Portfolioanteil",
    "bilancio.overlap_unknown": "Nicht abgedeckter Gesamtanteil: **{quota}**.",

    "profile.expander": "🧭 Persönliches Profil (nur lokal)",
    "profile.caption": "Optional: trennt beobachtete Fakten von erklärten Präferenzen.",
    "profile.horizon_label": "Zeithorizont",
    "profile.objective_label": "Ziel",
    "profile.loss_enable": "Maximalen temporären Verlust angeben",
    "profile.loss_label": "Maximal tolerierter Verlust (%)",
    "profile.withdrawals_label": "Geplante Entnahmen",
    "profile.limit_enable": "Limit für eine einzelne Position angeben",
    "profile.limit_label": "Positionslimit (%)",
    "profile.preference_label": "Präferenz",
    "profile.bonds_label": "Anleihen erlaubt",
    "profile.excluded_classes_label": "Ausgeschlossene Klassen",
    "profile.excluded_sectors_label": "Ausgeschlossene Sektoren",
    "profile.save_button": "Lokales Profil speichern",
    "profile.saved_toast": "Profil nur auf diesem Gerät gespeichert.",
    "profile.invalid": "Profil nicht gespeichert: {errore}",
    "profile.not_set": "Nicht festgelegt",
    "profile.years": "{n} Jahre",
    "profile.yes": "Ja",
    "profile.no": "Nein",
    "profile.objective_growth": "Wachstum",
    "profile.objective_income": "Einkommen",
    "profile.objective_preservation": "Erhalt",
    "profile.preference_simplicity": "Einfachheit",
    "profile.preference_balanced": "Ausgewogen",
    "profile.preference_diversification": "Diversifizierung",
    "profile.class_equity": "Aktien",
    "profile.class_bond": "Anleihen",
    "profile.class_cash": "Liquidität",
    "profile.class_commodities": "Rohstoffe",
    "profile.class_real_estate": "Immobilien",
    "profile.sector_technology": "Technologie",
    "profile.sector_finance": "Finanzen",
    "profile.sector_health": "Gesundheit",
    "profile.sector_energy": "Energie",
    "profile.sector_industry": "Industrie",
    "profile.sector_consumer": "Konsumgüter",
    "profile.sector_utilities": "Versorger",
    "profile.sector_real_estate": "Immobilien",
    "profile.sector_materials": "Materialien",
    "profile.sector_communication": "Kommunikation",
    "tab.diagnosi": "🧭 Diagnose",
    "diagnostic.header": "**Lokale deterministische Diagnose**",
    "diagnostic.no_profile": "Kein persönliches Profil: fehlende Felder sind {campi}.",
    "diagnostic.warning": "Warnung im Verhältnis zum Profil",
    "diagnostic.info": "Information",
    "diagnostic.portfolio": "Portfolio",
    "diagnostic.no_evidence": "Keine numerischen Belege",
    "diagnostic.severity_column": "Typ",
    "diagnostic.finding_column": "Befund",
    "diagnostic.asset_column": "Instrument",
    "diagnostic.evidence_column": "Beleg",
    "diagnostic.payload_header": "**Vorschau der anonymen Nutzlast**",
    "diagnostic.payload_caption": (
        "Dies ist die vollständige Form für eine mögliche spätere Weitergabe; "
        "hier wird nichts gesendet."
    ),
    "diagnostic.generic": "Berichtsfakt",
    "diagnostic.profile_missing": "Profil nicht ausgefüllt: keine persönliche Schwelle angewendet.",
    "diagnostic.weight_observation": "Beobachteter Portfolioanteil.",
    "diagnostic.ter_missing": "TER für dieses Instrument nicht verfügbar.",
    "diagnostic.ter_observation": "TER und Quelle für dieses Instrument verfügbar.",
    "diagnostic.drawdown_observation": "Beobachteter historischer maximaler Drawdown.",
    "diagnostic.holdings_missing": "Underlying-Positionen nicht verfügbar.",
    "diagnostic.position_limit_exceeded": "Der Anteil überschreitet das angegebene Limit.",
    "diagnostic.drawdown_exceeds_tolerance": (
        "Der historische Drawdown überschreitet den tolerierten Verlust."
    ),
    "diagnostic.history_shorter_than_horizon": (
        "Der beobachtete Zeitraum ist kürzer als der Horizont."
    ),
    "diagnostic.excluded_exposure": "Exposure zu einer ausgeschlossenen Klasse oder einem Sektor.",
    "diagnostic.bonds_not_allowed": "Das Profil erlaubt keine Anleihen.",
    "diagnostic.correlation_observation": "Historische Korrelationen sind verfügbar.",
    "diagnostic.rolling_observation": "Historische rollierende Renditen sind verfügbar.",
    "diagnostic.benchmark_observation": "Ein historischer Benchmarkvergleich ist verfügbar.",
    "diagnostic.inflation_observation": "Historische Inflationsdaten sind verfügbar.",
    "diagnostic.overlap_observation": (
        "Eine historische Holdings-Überschneidungsanalyse ist verfügbar."
    ),

    # --- Tab Fondsvergleich -----------------------------------------------------------------
    "confronto.caption": (
        "Verlauf von {capitale}, vollständig in jeden Fonds investiert, "
        "für einen Vergleich bei gleichem Kapital."
    ),
    "confronto.caption_pac": (
        "Verlauf von {capitale}, vollständig in jeden einzelnen Fonds "
        "investiert, mit demselben Einzahlungsplan wie das Portfolio: der "
        "Vergleich bleibt bei gleichem Kapital und gleichen Raten."
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
    "confronto.col_valore_finale_pac": "Endwert (aus {capitale} + Einzahlungen)",
    "confronto.stesso_capitale_caption_pac": (
        "Jede Zeile erhält dasselbe Anfangskapital (**{capitale}**) und "
        "denselben Einzahlungsplan. *Endwert* ist der tatsächliche Stand am "
        "Ende, Einzahlungen inklusive, und *XIRR* ist die Rendite deines "
        "Geldes, die berücksichtigt, wann jede Rate eingezahlt wurde. Alle "
        "übrigen Kennzahlen werden **ohne die Einzahlungen** berechnet: eine "
        "Einzahlung ist kein Marktgewinn."
    ),
    "confronto.footnote": (
        "Die Spalte *Rekonstruiert* markiert Zeilen, deren Kennzahlen "
        "einen von einem Proxy geschätzten Zeitraum enthalten."
    ),
    "confronto.riga_portafoglio": "🎯 PORTFOLIO",
    "si": "ja",
    "no": "nein",
    "nd": "k. A.",
    "benchmark.expander": "🎯 Benchmark und Vergleichsanalysen",
    "benchmark.label": "Referenz",
    "benchmark.option_none": "Keine",
    "benchmark.option_VT": "Globale Aktien (VT, Gesamtrendite)",
    "benchmark.option_VFINX": "S&P 500 (VFINX, Gesamtrendite)",
    "benchmark.option_custom": "Instrument suchen",
    "benchmark.search_label": "Benchmark suchen",
    "benchmark.search_placeholder": "Symbol, Name oder ISIN",
    "benchmark.selected": "Benchmark ausgewählt: **{symbol}**",
    "benchmark.remove_button": "Benchmark entfernen",
    "benchmark.failed": "Benchmark nicht verfügbar: {errore}",
    "benchmark.source": "Benchmarkquelle: {source} · Notierung: {symbol}",
    "benchmark.attempts": "Auflösungsversuche: {elenco}",
    "benchmark.legend": "Benchmark {symbol}",
    "benchmark.metrics_header": "Vergleich im gemeinsamen Zeitraum",
    "benchmark.metric": "Reihe",
    "benchmark.portfolio_label": "Ihr Portfolio",
    "benchmark.growth": "Gesamtrendite",
    "benchmark.cagr": "CAGR",
    "benchmark.volatility": "Volatilität",
    "benchmark.max_drawdown": "Max. Drawdown",
    "benchmark.active_return": "Aktive Rendite",
    "benchmark.tracking_error": "Tracking Error",
    "benchmark.information_ratio": "Information Ratio",
    "benchmark.common_period": "Gemeinsamer Zeitraum: {start} → {end} · {n} Monatsbeobachtungen",
    "benchmark.common_period_short": "der gemeinsame Zeitraum hat weniger als zwei Beobachtungen",
    "benchmark.metric_reason": "Hinweis: {motivo}.",
    "benchmark.reason_common_empty": "der gemeinsame Zeitraum ist leer",
    "benchmark.reason_insufficient": "die monatliche Stichprobe ist zu klein",
    "benchmark.reason_tracking_error_zero": "der Tracking Error ist null",
    "benchmark.reason_generic": "die Kennzahl kann nicht berechnet werden",
    "benchmark.correlation_header": "Korrelationen der Monatsrenditen",
    "benchmark.correlation_portfolio_header": "Korrelationen zwischen Portfolio und Instrumenten",
    "benchmark.rolling_header": "Annualisierte rollierende Renditen",
    "benchmark.rolling_period": "Fenster",
    "benchmark.rolling_worst": "Schlechteste",
    "benchmark.rolling_median": "Median",
    "benchmark.rolling_best": "Beste",
    "benchmark.rolling_positive": "Positive Fenster",
    "benchmark.rolling_observations": "Beobachtungen",
    "benchmark.years": "{n} Jahre",
    "inflation.expander": "📉 Reale Rendite und Inflation",
    "inflation.enable_checkbox": "Werte inflationsbereinigt anzeigen",
    "inflation.enable_help": "Verwendet den offiziellen monatlichen Eurostat-HVPI.",
    "inflation.area_label": "Kaufkraftgebiet",
    "inflation.area_it": "Italien",
    "inflation.area_ea": "Euro-Raum",
    "inflation.retry_button": "Eurostat erneut versuchen",
    "inflation.real_curve": "Portfolio in realer Kaufkraft",
    "inflation.metrics_header": "Nominaler und realer Vergleich",
    "inflation.metric_kind": "Werte",
    "inflation.metric_total_return": "Gesamtrendite",
    "inflation.metric_cagr": "CAGR",
    "inflation.metric_final": "Endwert",
    "inflation.nominal": "Nominal",
    "inflation.real": "Real",
    "inflation.coverage_caption": "Quelle: {source} · Gebiet: {area} · Abdeckung: {first} → {last}",
    "inflation.pac_caption": (
        "PAC eingezahlt: {nominal} nominal · {real} in anfänglicher Kaufkraft."
    ),
    "inflation.failed": "Reale Analyse nicht verfügbar: {errore}",
    "inflation.coverage_missing": "Der HICP-Index deckt den Portfoliozeitraum nicht ab.",
    "inflation.stale_caption": (
        "Eurostat antwortet nicht: möglicherweise veraltete Cache-Daten werden angezeigt."
    ),

    # --- Tab Drawdown -----------------------------------------------------------------------
    "drawdown.legend_portafoglio": "Portfolio",
    "drawdown.yaxis": "Drawdown (%)",
    "drawdown.pac_caption": (
        "Bei aktivem Sparplan werden Drawdown und Jahresrenditen ohne die "
        "Einzahlungen berechnet: sonst erschiene jede Rate als Marktgewinn und "
        "die Rückgänge wirkten milder, als sie waren."
    ),
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
    "previdenza.pac_caption": (
        "**Bei aktivem Sparplan** gilt in diesem Reiter: die Kurven der "
        "Anlagelinien im Portfolio-Diagramm erhalten denselben Einzahlungsplan; "
        "die Rendite deines Portfolios ist die ohne Einzahlungen, denn so "
        "berechnet COVIP die eigenen; Kostenerosion und projizierter Endwert "
        "rechnen mit deiner Rate über zehn Jahre, **konstant** gehalten — die "
        "jährliche Erhöhung geht in diese Projektion nicht ein."
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
    "previdenza.rendimento_header": (
        "**Durchschnittliche jährliche Rendite, auf denselben COVIP-Fenstern**"
    ),
    "previdenza.col_orizzonte": "{etichetta} · {periodo}",
    "previdenza.legenda_caption": (
        "Jede Spalte ist ein eigenes abgeschlossenes Fenster, kein kumulativer "
        "Zeitraum: die Daten stehen in der Kopfzeile. Ein Zehnjahreswert unter "
        "dem Fünfjahreswert heißt, dass die erste Hälfte des Jahrzehnts weniger "
        "gebracht hat, nicht dass der Fonds zuletzt schlechter geworden ist. "
        "**ISC 10a** ist der synthetische Kostenindikator, das Gegenstück zur "
        "TER in der Altersvorsorge: wie stark die Kosten im Schnitt jedes Jahr "
        "über zehn Jahre wiegen."
    ),
    "previdenza.portafoglio_periodo_proprio": (
        "Dein Backtest deckt **{inizio} → {fine}** ({anni} Jahre) ab und hat "
        "**{rendimento}** pro Jahr gebracht: eine Zahl, die mit den Spalten "
        "oben nicht vergleichbar ist. Die COVIP-Fenster sind **ganze "
        "Kalenderjahre**, vom 1. Januar bis zum 31. Dezember: ein Zeitraum, der "
        "mitten im Jahr beginnt oder endet, deckt sie nicht ab, auch wenn die "
        "Kalenderjahre gleich aussehen."
    ),
    "previdenza.allinea_button": "📐 Zeitraum auf {inizio} → {fine} setzen",
    "previdenza.allinea_caption": (
        "Ändert die Backtest-Daten so, dass sie die COVIP-Fenster abdecken. Der "
        "Backtest beginnt ohnehin am ersten Datum, an dem **alle** ausgewählten "
        "Fonds Daten haben: die längeren Fenster bleiben **n/d**, wenn ein "
        "Fonds jünger ist."
    ),
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
    "previdenza.anno_suffix": "{a} Jahr",
    "previdenza.anni_suffix": "{a} Jahre",
    "previdenza.il_tuo_portafoglio": "Ihr Portfolio",
    "previdenza.yaxis_rendimento": "Durchschnittliche jährliche Rendite (%)",
    "previdenza.costi_header": "**Wie stark die Kosten wiegen**",
    "previdenza.col_comparto": "Teilfonds",
    "previdenza.col_isc_annuo": "Jährliche ISC",
    "previdenza.col_rendimento_10a": "Rendite 10J",
    "previdenza.col_eroso": "Aufgezehrt bei {capitale} über 10 Jahre",
    "previdenza.col_eroso_pac": "Aufgezehrt bei {capitale} in 10 Jahren eingezahlt",
    "previdenza.col_quota_rendimento": "Anteil der Rendite",
    "previdenza.col_montante_pac_10a": "Projiziertes Kapital (Sparplan, 10J)",
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

    "directa.expander": "Directa-Portfolio importieren",
    "directa.caption": "CSV/XLSX laden, Spalten zuordnen und die Vorschau vor dem Import prüfen.",
    "directa.upload_label": "Aus Directa exportierte Datei",
    "directa.sheet_label": "Blatt",
    "directa.header_row_label": "Kopfzeile (0 = erste Zeile)",
    "directa.header_row_help": (
        "Wenn beschreibende Zeilen vor der Tabelle stehen, hier die Kopfzeile auswählen."
    ),
    "directa.file_error": "Directa-Datei konnte nicht gelesen werden: {errore}",
    "directa.movements_file": (
        "Dies ist ein Bewegungs-Export und kein Positions-Export: Er enthält "
        "Käufe und Gebühren, aber keinen aktuellen Marktwert. Verwenden Sie "
        "für den Portfolioimport den Positions-/Portfolio-Export von Directa."
    ),
    "directa.no_column": "(keine)",
    "directa.value_column": "Spalte aktueller Wert",
    "directa.isin_column": "ISIN-Spalte",
    "directa.ticker_column": "Ticker-Spalte",
    "directa.name_column": "Namensspalte",
    "directa.currency_column": "Währungsspalte (optional)",
    "directa.quantity_column": "Mengenspalte (optional)",
    "directa.average_column": "Spalte Einstandspreis (optional)",
    "directa.preview_identifier": "Kennung",
    "directa.preview_name": "Name",
    "directa.preview_value": "Aktueller Wert",
    "directa.issue_row": "Zeile",
    "directa.issue_column": "Spalte",
    "directa.issue_message": "Problem",
    "directa.issue_invalid_isin": "Ungültige ISIN.",
    "directa.issue_missing_identifier": "ISIN oder Ticker fehlt.",
    "directa.issue_summary_row": "Zusammenfassungszeile ohne Instrument: beim Import ausschließen.",
    "directa.issue_invalid_value": "Der aktuelle Wert muss positiv sein.",
    "directa.issue_invalid_quantity": "Die Menge muss positiv sein.",
    "directa.issue_invalid_average": "Der durchschnittliche Einstandspreis muss positiv sein.",
    "directa.value_currency": "Währung der Werte",
    "directa.mapping_error": "Unvollständige Zuordnung: {errore}",
    "directa.issues": "{n} Zeilen können nicht importiert werden",
    "directa.instrument_label": "Notierung für {nome}",
    "directa.exclude_unresolved": "Nicht importierbare Zeilen ausdrücklich ausschließen",
    "directa.unresolved": "Ohne Notierung oder nicht unterstützt: {elenco}",
    "directa.import_button": "Aufgelöste Positionen importieren",
    "directa.import_success": "{n} Directa-Positionen importiert",
    "costs.pic_expander": "PIC-Ein- und Ausstiegskosten",
    "costs.pic_caption": "Separate Schätzung: Backtest und Kennzahlen bleiben unverändert.",
    "costs.pic_enable": "PIC-Kostenschätzung berechnen",
    "costs.mode_label": "Kostenart",
    "costs.mode_none": "Keine Kosten",
    "costs.mode_fixed": "Fester Betrag je Auftrag",
    "costs.mode_percentage": "Prozentsatz je Auftrag",
    "costs.fixed_label": "Fester Betrag",
    "costs.rate_label": "Prozentsatz %",
    "costs.minimum_label": "Minimum",
    "costs.maximum_label": "Maximum (0 = ohne Limit)",
    "costs.maximum_help": "Null bedeutet, dass kein Höchstbetrag gilt.",
    "costs.buy_title": "Einstieg",
    "costs.sell_title": "Ausstieg",
    "costs.pic_error": "PIC-Kosten konnten nicht berechnet werden: {errore}",
    "costs.pic_result_expander": "Geschätzter Einfluss der PIC-Gebühren",
    "costs.pic_result_caption": (
        "Einstiegskosten werden im Budget reserviert; Ausstiegskosten werden "
        "je Fonds berechnet."
    ),
    "costs.pic_budget": "Budget",
    "costs.pic_buy_total": "Einstieg gesamt",
    "costs.pic_sell_total": "Ausstieg gesamt",
    "costs.pic_net_final": "Netto-Endbetrag",
    "costs.pic_line_investable": "Tatsächlich investiertes Kapital",
    "costs.pic_line_before_sell": "Betrag vor Ausstieg",
    "costs.pic_line_without": "Betrag ohne Kosten",
    "costs.pic_line_difference": "Gesamtdifferenz",
    "costs.pic_column_item": "Position",
    "costs.pic_column_value": "Wert",
    "costs.pic_column_side": "Vorgang",
    "costs.pic_column_symbol": "Symbol",
    "costs.pic_column_notional": "Auftragswert",
    "costs.pic_column_fee": "Gebühr",
    "ter_warning.retry_button": "TER-Abruf wiederholen",
    "ter_warning.attempts": "{symbol}: {esiti}",
    "ter_warning.sources": "TER-Quelle: {elenco}",
    "search.info_button": "Details",
    "editor.col_scheda": "Details",
    "editor.scheda_help": "Beschreibende Daten, Quellen und Konflikte des Instruments anzeigen.",
    "instrument.title": "Instrumenteninformationen",
    "instrument.loading": "Instrumentendaten werden abgerufen…",
    "instrument.not_available": "Nicht verfügbar",
    "instrument.date_not_available": "Datum nicht verfügbar",
    "instrument.date_placeholder": "JJJJ-MM-TT",
    "instrument.fact_provenance": "Quelle: {source} · beobachtet: {observed} · Qualität: {quality}",
    "instrument.fact_conflict_entry": "{source}: {value} · beobachtet: {observed}",
    "instrument.quality_reported": "von der Quelle angegeben",
    "instrument.quality_document": "im Dokument verifiziert",
    "instrument.quality_manual": "manuell eingegeben",
    "instrument.quality_derived": "abgeleitet",
    "instrument.no_conflicts": "Keine Konflikte zwischen den abgerufenen Fakten.",
    "instrument.fact_generic": "Fakt",
    "instrument.fact_name": "Name",
    "instrument.fact_ter": "TER",
    "instrument.fact_issuer": "Emittent",
    "instrument.fact_category": "Kategorie",
    "instrument.fact_index": "Nachgebildeter Index",
    "instrument.fact_domicile": "Domizil",
    "instrument.fact_fund_currency": "Fondswährung",
    "instrument.fact_inception": "Auflegungsdatum",
    "instrument.fact_aum": "Vermögen",
    "instrument.fact_kid_url": "KID-Link",
    "instrument.fact_kid_date": "KID-Datum",
    "instrument.fact_sri": "Synthetisches Risiko (1–7)",
    "instrument.fact_history_start": "Beginn der beobachteten Abdeckung",
    "instrument.fact_history_end": "Ende der beobachteten Abdeckung",
    "instrument.identity_section": "Identität und Börsennotierung",
    "instrument.identity_field": "Feld",
    "instrument.identity_value": "Wert",
    "instrument.identity_symbol": "Aktives Symbol",
    "instrument.identity_isin": "ISIN",
    "instrument.identity_exchange": "Markt",
    "instrument.identity_currency": "Notierungswährung",
    "instrument.costs_section": "Kosten und KID",
    "instrument.characteristics_section": "Merkmale",
    "instrument.allocation_section": "Aufteilung und Beteiligungen",
    "instrument.holdings_missing": "Die wichtigsten Beteiligungen sind nicht verfügbar.",
    "instrument.holding_symbol": "Symbol",
    "instrument.holding_name": "Name",
    "instrument.holding_weight": "Anteil",
    "instrument.history_section": "Historische Abdeckung",
    "instrument.related_section": "Verbundene Notierungen",
    "instrument.related_missing": "Keine weitere Notierung mit derselben ISIN verfügbar.",
    "instrument.related_symbol": "Symbol",
    "instrument.related_exchange": "Markt",
    "instrument.related_currency": "Währung",
    "instrument.related_source": "Quelle",
    "instrument.sources_section": "Quellen und Konflikte",
    "instrument.attempt": "{source}: {outcome}",
    "instrument.kid_section": "Im KID verifizierte Daten",
    "instrument.kid_ter_enabled": "TER aus dem KID setzen",
    "instrument.kid_url_label": "KID-URL",
    "instrument.kid_date_label": "Dokumentdatum (JJJJ-MM-TT)",
    "instrument.sri_label": "Synthetischer Risikoindikator (1–7)",
    "instrument.kid_save": "KID-Daten speichern",
    "instrument.kid_url_invalid": "Die URL muss mit http:// oder https:// beginnen.",
    "instrument.kid_date_invalid": "Das KID-Datum muss das Format JJJJ-MM-TT haben.",
    "instrument.kid_date_future": "Das KID-Datum darf nicht in der Zukunft liegen.",
    "instrument.kid_saved": "KID-Daten gespeichert.",
    "instrument.kid_clear": "KID-Daten entfernen",
    "instrument.retry_button": "Abruf wiederholen",
    "instrument.add_button": "Zum Portfolio hinzufügen",
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
    "balance": "Endstand",
    "invested": "Eingezahlt",
    "gain": "Gewinn",
    "xirr": "XIRR",
}

ESITI: dict[str, str] = {
    "ok": "ok",
    "no_data": "keine Daten",
    "not_configured": "nicht konfiguriert",
    "isin_required": "ISIN erforderlich",
    "found": "gefunden",
    "no_ter": "TER nicht vorhanden",
    "blocked": "vom Tarif blockiert",
    "symbol_unresolved": "Symbol nicht aufgelöst",
    "temporary_error": "vorübergehender Fehler",
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
    "manual": "Manuell eingegeben",
    "kid": "KID",
    "missing": "Nicht verfügbar",
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
