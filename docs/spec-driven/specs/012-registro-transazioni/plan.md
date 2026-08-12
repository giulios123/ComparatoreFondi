# 012 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

L'implementazione parte solo dopo aver deciso metodo di costo, perimetro della
cassa, conti e operazioni speciali e dopo aver raccolto almeno due tracciati
anonimi differenti. Il modello interno è un registro versionato e indipendente
dai file sorgente. L'importatore riconosce candidati, propone un mapping e crea
un'anteprima; soltanto la conferma aggiunge operazioni normalizzate.

I calcoli di posizioni, risultati e performance sono funzioni pure separate dal
backtester. Il registro conserva valori originari e cambi osservati, mentre le
viste derivate possono essere ricalcolate. Identificativi originari e impronte
stabili rendono l'import idempotente senza nascondere collisioni dubbie.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/transactions.py` | Modello versionato di operazione, tipi, validazione e registro locale. |
| `comparatore/transaction_io.py` | Lettura CSV/XLSX, mapping guidato, anteprima, errori e deduplicazione. |
| `comparatore/performance.py` | Posizioni, costo, risultati realizzati/non realizzati, redditi, TWRR e XIRR. |
| `comparatore/fx.py` | Risolve i cambi storici conservando valore, fonte e data senza sostituzioni implicite. |
| `comparatore/portfolio_io.py` | Mantiene separati portafoglio modello e riferimento opzionale al registro. |
| `comparatore/directa_io.py` | Offre un preset di mapping per i movimenti Directa senza diventare il formato interno. |
| `app.py` | Aggiunge importazione guidata, anteprima, registro, riconciliazione e viste di performance reale. |
| `comparatore/locales/it.py` | Testi italiani del registro e delle avvertenze contabili. |
| `comparatore/locales/en.py` | Traduzioni inglesi. |
| `comparatore/locales/fr.py` | Traduzioni francesi. |
| `comparatore/locales/de.py` | Traduzioni tedesche. |
| `tests/fixtures/transactions/` | Tracciati minimi anonimi per intermediari e casi limite. |
| `tests/test_transactions.py` | Copre modello, validazione, versione e ricostruzione delle posizioni. |
| `tests/test_transaction_io.py` | Copre mapping, anteprima, errori e idempotenza. |
| `tests/test_performance.py` | Copre costo, flussi, risultati, TWRR, XIRR e valute. |
| `tests/test_app_sintassi.py` | Protegge la separazione visibile fra dati reali e backtest. |
| `tests/test_i18n.py` | Continua a garantire la parità dei cataloghi. |

Si riusano il lettore tabellare e la logica di mapping resiliente già introdotti
per Directa, `xirr()` dove semanticamente corretto e il client dei cambi. Non si
riusano le strutture del backtest come se fossero un libro contabile.

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Calcolare tutto dalla fotografia corrente delle posizioni | Non ricostruisce flussi, dividendi, commissioni o risultati realizzati. |
| Usare il CSV Directa come schema interno | Impedisce l'uso di altri intermediari e rende fragili le migrazioni. |
| Correggere automaticamente righe incoerenti | Può cambiare segno o natura economica di un'operazione senza consenso. |
| Memorizzare solo le viste aggregate | Impedisce audit, correzione e ricalcolo con regole migliorate. |
| Presentare una stima fiscale completa | Le regole dipendono da regime, residenza, strumento e storia e richiedono una spec dedicata. |

## Rischi

- I tracciati reali sono molto variabili: due o più fixture anonime e un mapping
  confermabile riducono assunzioni specifiche di un broker.
- La deduplicazione può unire operazioni legittimamente uguali: identificativi
  originari hanno precedenza e le collisioni senza ID richiedono conferma.
- Costo e plusvalenze cambiano con il metodo contabile: la spec resta bozza finché
  il metodo non è deciso e i test fissano esempi numerici verificabili.
- Movimenti mancanti falsano cassa e rendimento: saldi non riconciliati e periodi
  incompleti sono evidenziati, non colmati.
- Cambi storici mancanti possono produrre totali parziali: il calcolo espone il
  perimetro escluso e non usa il cambio corrente come ripiego silenzioso.
- La UI può confondere simulazione e storia reale: le viste sono separate e una
  guardia sorgente protegge etichette e ordine.

## Verifica

1. Chiudere le domande aperte, acquisire le fixture anonime e approvare la spec.
2. Verificare a mano esempi contabili minimi per acquisto, vendita parziale,
   dividendo, commissione e cambio valuta prima di codificarli nei test.
3. Eseguire `uv run python -m unittest tests.test_transactions tests.test_transaction_io tests.test_performance`.
4. Eseguire `uv run python -m unittest discover -s tests -p "test_*.py"`.
5. Eseguire `uv run ruff check .`.
6. Importare due volte ciascuna fixture e verificare conteggi, collisioni e
   spiegazioni delle righe escluse.
7. Confrontare posizioni, costo, risultati e flussi con i valori attesi delle
   fixture, includendo almeno una valuta estera e un cambio mancante.
8. Verificare visivamente che performance reale e backtest siano sezioni
   distinte e che il portafoglio modello non cambi senza conferma.
