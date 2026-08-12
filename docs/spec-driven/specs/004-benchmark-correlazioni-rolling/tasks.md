# 004 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [ ] Aggiungere contratti e calcoli puri in `comparatore/comparative.py`.
- [ ] Esporre i due preset rapidi senza attivare l'innesto storico dei proxy.
- [ ] Integrare ricerca, selezione, rimozione e diagnostica del benchmark.
- [ ] Simulare il benchmark con lo stesso capitale/PAC senza inserirlo negli holdings.
- [ ] Aggiungere confronto, correlazioni e rolling alla UI.
- [ ] Persistire la scelta nel JSON con backfill "nessun benchmark".
- [ ] Aggiungere le chiavi ai quattro cataloghi.

## Test

- [ ] Testare periodo comune, dati insufficienti e benchmark irrisolvibile.
- [ ] Testare metriche attive e correlazioni con formule chiuse.
- [ ] Testare rolling 1/3/5/10, finestre positive e valori riassuntivi.
- [ ] Testare PAC e assenza di regressioni sulle metriche del portafoglio.
- [ ] Testare round-trip JSON e guardie strutturali di `app.py`.

## Verifica dei criteri di accettazione

- [ ] 1 · benchmark assente, due preset e ricerca libera.
- [ ] 2 · benchmark esterno a pesi, costi e composizione.
- [ ] 3 · periodo completo del portafoglio e periodo comune dichiarato.
- [ ] 4 · benchmark fallito non blocca il backtest.
- [ ] 5 · metriche comparative complete o `n/d` spiegato.
- [ ] 6 · correlazioni mensili con periodo e campione visibili.
- [ ] 7 · rolling 1/3/5/10 con riepilogo.
- [ ] 8 · compatibilita' e persistenza JSON.
- [ ] 9 · quattro lingue e test offline.

## Chiusura

- [ ] `uv run python -m unittest discover -s tests -p "test_*.py"` passa
- [ ] `uv run ruff check .` passa
- [ ] `git diff --check` passa
- [ ] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [ ] Aggiunta una decisione a `docs/memory-bank/02-decisioni.md`
- [ ] Aggiornato lo stato in cima a `spec.md`
