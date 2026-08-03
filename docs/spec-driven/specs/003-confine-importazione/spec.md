# 003 · Confine di importazione

*Stato: bozza — 3 agosto 2026*

## Problema

L'[audit tecnico del 1 agosto 2026](../../../audit-codebase-2026-08-01.md) ha
confermato un finding P2 mai affrontato, ed esplicitamente escluso dai
non-obiettivi della spec [`002`](../002-integrita-backtest/spec.md): l'import di
un portafoglio e il caricamento di un CSV accettano dati che non hanno senso
economico, e li fanno arrivare fino a un punto del codice che non sa gestirli.

Due casi verificati:

1. `portfolio_io.load()` controlla che le chiavi `symbol`, `name`, `weight`
   **esistano** in ogni fondo, non che i valori abbiano senso. Un JSON con
   `"weight": "not-a-number"` supera l'import senza errori. Il valore arriva
   fino a `pesi.rinormalizza()`, chiamata **fuori** dal blocco che cattura
   `PortfolioError`: il risultato è un `TypeError` non gestito mostrato
   nell'interfaccia, non un messaggio comprensibile.
2. `parse_csv()` scarta le righe con data o valore mancante, ma non quelle con
   una quota zero, negativa o infinita — `notna()` è vero anche per `inf`. Il
   file viene accettato, annunciato come un successo con tanto di conteggio
   delle osservazioni, e la quota non valida arriva fino al motore, dove la
   barriera introdotta dalla spec 002 (`engine.valida_prezzi`) la respinge sì,
   ma molto più tardi: quando l'utente ha già lasciato la sezione di
   caricamento, con un errore che nomina il simbolo e non la riga.

Nessun tentativo precedente: la spec 002 ha volutamente lasciato invariato
questo confine per restare nell'ambito dei tre P1 dell'audit.

## Chi lo incontra

Chiunque importi un portafoglio salvato in precedenza e modificato a mano, o
generato da uno strumento esterno; chiunque carichi un CSV con anche una sola
riga sporca (un export bancario con una quota a zero durante una sospensione,
un errore di battitura). Non serve un file malevolo: basta un file imperfetto,
lo scenario più comune per chi importa dati non prodotti dall'app stessa.

## Criteri di accettazione

1. Un JSON con un `weight` non numerico, non finito, o fuori dall'intervallo
   `[0, 100]` produce un errore tradotto e leggibile, non un traceback.
2. Un JSON con un `ter` o un `extra` non numerico, non finito, o fuori
   dall'intervallo `[0, 10]` viene respinto allo stesso modo.
3. Un JSON con un `symbol` vuoto (stringa vuota o solo spazi) o ripetuto fra
   due fondi dello stesso file viene respinto, indicando quale simbolo.
4. Un file JSON oltre una soglia di dimensione, o con più fondi di una soglia
   massima, viene respinto prima di essere interamente elaborato.
5. Un CSV con almeno una quota zero, negativa o infinita viene respinto **al
   momento del caricamento**, con un messaggio che indica la data della riga
   incriminata — non più tardi, al momento del backtest.
6. Un file CSV oltre una soglia di dimensione viene respinto prima di essere
   interamente elaborato.
7. Un JSON e un CSV oggi validi (già coperti dai test esistenti) continuano a
   essere accettati esattamente come prima: nessuna regressione sul percorso
   già funzionante.

## Non-obiettivi

- Validare il *contenuto* di `alloc`, `alloc_manuale` o `holdings` (la
  composizione geografica/settoriale dichiarata nel file): restano campi
  liberi come oggi, non alimentano calcoli numerici del backtest.
- Limiti anti-abuso di rete (rate limiting sull'upload, quote per IP): sono
  parte della modalità ospitata, spec
  [`004-istanza-multiutente`](../004-istanza-multiutente/spec.md).
- Validare i `parametri` del backtest (date, valuta base, ribilanciamento):
  non erano nel finding originale dell'audit.
- Cambiare il formato o la struttura del file JSON o del CSV: solo la loro
  validazione al confine, non lo schema.

## Vincoli

- `comparatore/` non deve importare Streamlit: la validazione vive in
  `portfolio_io.py` e `sources/csv_source.py`, non in `app.py`.
- Ogni messaggio mostrato a video passa da `t()`: si riusa la chiave
  `portfolio_io.import_error` già esistente per il JSON, se ne aggiunge una
  simmetrica per il CSV.
- Le soglie di `weight` e `ter`/`extra` non sono inventate: riprendono
  esattamente i limiti già imposti dall'editor di composizione
  (`st.column_config.NumberColumn` in `app.py`) — un valore che l'editor non
  permetterebbe mai di digitare non deve poter entrare dall'import.
- La semantica di `pesi.rinormalizza()` e la barriera del motore
  (`engine.valida_holdings`, spec 002) non cambiano: restano le due linee di
  difesa indipendenti già in campo, questa spec ne aggiunge una a monte.
- Un cambiamento strutturale di `app.py` è accompagnato dalla sua guardia in
  `tests/test_app_sintassi.py`.

## Domande aperte

Nessuna. Le soglie numeriche di `weight`/`ter`/`extra` derivano da bound già
esistenti nell'editor, non da una scelta nuova. Le due soglie di dimensione
file (JSON e CSV) sono valori pragmatici, motivati nel piano rispetto alla
dimensione reale di un portafoglio o di una serie storica.
