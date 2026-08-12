# 009 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Costruire un adattatore Copilot dietro un protocollo minimo e puro dal punto di
vista dell'app: `analyze(AnonymousReport) -> AiAnalysis`. L'adattatore e'
l'unico modulo che importa l'SDK e resta opzionale, cosi' il resto della
libreria e i test funzionano anche quando la dipendenza non e' disponibile.

Il prompt definisce ruolo, divieto di previsione, schema e codici di evidenza;
non contiene logica finanziaria che dovrebbe vivere in `diagnostics.py`. La
risposta viene validata localmente. Soltanto dopo la validazione si sostituiscono
i token `asset_N` con etichette reali per la vista.

Le simulazioni sono oggetti dichiarativi (azione, asset token, nuovo peso o
rimozione) e non callback eseguibili. Un comando separato crea una copia dello
stato, mostra le differenze e chiede conferma prima di applicarla; la prima
versione puo' limitarsi a precompilare lo scenario senza lanciarlo.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/ai/base.py` | Protocollo, schema `AiAnalysis`, errori e validazione riferimenti |
| `comparatore/ai/copilot.py` | Adattatore opzionale approvato dalla spec 007, nessun tool |
| `comparatore/ai/prompt.py` | Istruzioni versionate e indipendenti dalla lingua dei dati |
| `comparatore/scenarios.py` | Oggetti dichiarativi e applicazione confermata a una copia |
| `app.py` | Stato login, anteprima, invio esplicito, risposta e scenari |
| `comparatore/locales/{it,en,fr,de}.py` | UI, errori e avvertenze; non il testo generato |
| `desktop/comparatore.spec` | Runtime/dati Copilot soltanto come stabilito dalla spec 007 |
| `tests/test_ai.py` | Mock client, schema, riferimenti, errori e privacy |
| `tests/test_scenarios.py` | Nessuna modifica prima della conferma e invariante pesi |
| `tests/test_app_sintassi.py` | Nessuna chiamata automatica prima dell'azione utente |

Riuso esplicito: `AnonymousReport` e mappa in memoria della spec 008,
`pesi.ridistribuisci()` per scenari confermati, gestione localizzata degli
errori e storage GitHub deciso nella spec 007.

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Inviare direttamente il JSON del portafoglio | Contiene identificatori, importi e campi non necessari |
| Chat libera con cronologia | Aumenta dati inviati, stato e possibilita' di deviare dal rapporto verificato |
| Lasciare che il modello restituisca solo Markdown | Non permette di verificare evidenze, asset citati e azioni |
| Concedere tool per modificare il portafoglio | Trasforma una spiegazione in un agente operativo senza necessita' |
| Eseguire automaticamente lo scenario suggerito | Una risposta variabile non deve mutare lo stato senza decisione umana |
| Test end-to-end reali in CI | Consumano quota e dipendono da rete/account; il contratto si testa con mock |

## Rischi

- Il modello puo' seguire lo schema ma usare linguaggio predittivo: validazione
  strutturale, istruzioni e casi di eval intercettano almeno le forme note;
  l'avvertenza resta sempre visibile.
- Il remapping locale puo' sostituire token dentro parole simili: usare campi
  strutturati, non sostituzione libera sull'intero testo.
- Un suggerimento puo' essere valido ma basato su copertura parziale: limiti ed
  evidenze devono viaggiare insieme fino alla vista.
- Rate limit o login scaduto non devono cancellare il rapporto deterministico.

## Verifica

1. Mock con risposta valida, codice evidenza inesistente, asset inventato,
   schema rotto e testo predittivo.
2. Ispezione del payload: nessun identificatore vietato e nessun tool.
3. Errori distinti per login, rete, quota, timeout e parsing.
4. Scenario suggerito: nessuna mutazione prima della conferma, pesi a 100 dopo.
5. Test manuale autenticato soltanto dopo i mock, con un portafoglio fittizio.
6. Suite, ruff, `git diff --check`, audit licenze e smoke dei bundle.
