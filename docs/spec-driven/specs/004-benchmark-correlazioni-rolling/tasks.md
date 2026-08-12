# 004 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [x] Aggiungere contratti e calcoli puri in `comparatore/comparative.py`.
- [x] Esporre i due preset rapidi senza attivare l'innesto storico dei proxy.
- [x] Integrare ricerca, selezione, rimozione e diagnostica del benchmark.
- [x] Simulare il benchmark con lo stesso capitale/PAC senza inserirlo negli holdings.
- [x] Aggiungere confronto, correlazioni e rolling alla UI.
- [x] Persistire la scelta nel JSON con backfill "nessun benchmark".
- [x] Aggiungere le chiavi ai quattro cataloghi.

## Test

- [x] Testare periodo comune, dati insufficienti e benchmark irrisolvibile.
- [x] Testare metriche attive e correlazioni con formule chiuse.
- [x] Testare rolling 1/3/5/10, finestre positive e valori riassuntivi.
- [x] Testare PAC e assenza di regressioni sulle metriche del portafoglio.
- [x] Testare round-trip JSON e guardie strutturali di `app.py`.

## Verifica dei criteri di accettazione

- [x] 1 · benchmark assente, due preset e ricerca libera.
- [x] 2 · benchmark esterno a pesi, costi e composizione.
- [x] 3 · periodo completo del portafoglio e periodo comune dichiarato.
- [x] 4 · benchmark fallito non blocca il backtest.
- [x] 5 · metriche comparative complete o `n/d` spiegato.
- [x] 6 · correlazioni mensili con periodo e campione visibili.
- [x] 7 · rolling 1/3/5/10 con riepilogo.
- [x] 8 · compatibilita' e persistenza JSON.
- [x] 9 · quattro lingue e test offline.

## Chiusura

- [x] `uv run python -m unittest discover -s tests -p "test_*.py"` passa
- [x] `uv run ruff check .` passa
- [x] `git diff --check` passa
- [x] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [x] Aggiunta una decisione a `docs/memory-bank/02-decisioni.md`
- [x] Aggiornato lo stato in cima a `spec.md`
