# 002 · Integrità del backtest

*Stato: fatta — 3 agosto 2026*

## Problema

L'[audit tecnico del 1 agosto 2026](../../../audit-codebase-2026-08-01.md) ha
confermato tre modi in cui il backtest può mostrare un risultato apparentemente
valido ma riferito a un portafoglio diverso da quello che l'utente ha davvero
impostato:

1. Un fondo la cui fonte dati non risponde (rete assente, chiave mancante,
   simbolo sbagliato) viene escluso dal calcolo senza fermare il backtest: i
   pesi dei fondi rimasti vengono rinormalizzati in silenzio e il capitale
   finisce tutto su un sottoinsieme del portafoglio, con solo un avviso non
   bloccante a segnalarlo.
2. Una quota storica non finita o non positiva (zero, negativa, infinita — un
   errore di fonte o di CSV caricato a mano) non viene respinta: diventa un
   rendimento giornaliero di fatto nullo e la curva prosegue come se nulla
   fosse successo.
3. Due strumenti diversi con lo stesso nome visuale rompono il backtest quando
   il PAC è attivo, perché il motore usa il nome come chiave interna delle
   colonne: la selezione di una colonna diventa ambigua e il calcolo solleva
   un errore di broadcasting invece di un messaggio comprensibile.

Non è stato tentato nessun fix prima d'ora: l'audit è la prima volta che questi
tre casi sono stati riprodotti e documentati.

## Chi lo incontra

Chiunque usi il backtest con più di un fondo: chi ha una fonte dati
temporaneamente irraggiungibile, chi carica un CSV con una riga sporca, chi
confronta due share class o due fondi di case diverse con lo stesso nome
commerciale. Non richiede un errore raro — basta una connessione instabile o un
file esportato male.

## Criteri di accettazione

1. Se uno o più fondi del portafoglio non hanno prezzi risolti nel periodo
   richiesto (fonte irraggiungibile, cambio valuta non risolvibile), il
   backtest non parte: la pagina mostra quali fondi mancano e quale
   allocazione percentuale verrebbe realmente simulata sui fondi rimasti.
2. Dalla stessa schermata esiste un'unica azione esplicita che rimuove i fondi
   senza dati e fa ripartire il backtest sui rimanenti; dopo l'azione i pesi
   mostrati nell'editor di composizione sommano di nuovo a 100%.
3. Una serie di prezzi con almeno un valore zero, negativo o non finito (NaN,
   infinito) produce un errore che nomina il simbolo coinvolto, non un
   grafico silenziosamente sbagliato.
4. Due fondi con lo stesso nome visuale, con il PAC attivo, producono un
   backtest completo, senza eccezioni; nella legenda e nelle tabelle i due
   compaiono con etichette distinguibili (nome ed eventualmente il simbolo).
5. Un portafoglio con dati completi e nomi tutti distinti produce, dopo la
   modifica, gli stessi numeri di prima (nessuna regressione sul percorso già
   coperto dai test esistenti).

## Non-obiettivi

- Validazione semantica dei file importati (JSON di portafoglio, CSV) oltre a
  ciò che serve a intercettare i casi 1-3: resta il finding P2 "Import di
  portafoglio senza validazione semantica" dell'audit, non affrontato qui.
- Pin SHA delle GitHub Action e permessi minimi dei workflow: P2 separato.
- Copertura test delle integrazioni esterne (Yahoo/EODHD/Twelve/COVIP/FX) e
  hardening P3 (scritture atomiche, log, HTML nella ricerca): fuori ambito.
- Un modo per procedere comunque con un sottoinsieme dei fondi senza prima
  rimuoverli esplicitamente dall'editor: il blocco è voluto, non un dettaglio
  implementativo negoziabile.

## Vincoli

- `comparatore/` non deve importare Streamlit (vincolo di `AGENTS.md`): la
  validazione vive nel motore, l'azione di rimozione e il rendering
  dell'errore restano in `app.py`.
- Ogni stringa a video passa da `t()`, con le quattro traduzioni allineate
  (`tests/test_i18n.py`).
- L'invariante "i pesi sommano sempre a 100" di `comparatore/pesi.py` non si
  tocca: la rimozione dei fondi assenti la riusa (`pesi.rinormalizza`), non la
  reimplementa.
- Un cambiamento strutturale di `app.py` è accompagnato dalla sua guardia in
  `tests/test_app_sintassi.py`.

## Domande aperte

Nessuna: le tre alternative sul comportamento in caso di dati mancanti sono
state discusse con l'utente, che ha scelto "blocca con azione esplicita di
rimozione" fra le opzioni presentate.
