# 012 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

Ogni voce è spuntabile guardando qualcosa. Se non lo è, non è un'attività.

## Decisioni preliminari

- [ ] Decidere e documentare il metodo del costo contabile.
- [ ] Decidere il perimetro della cassa e dei flussi esterni.
- [ ] Decidere il supporto iniziale per più conti e intermediari.
- [ ] Raccogliere almeno due estratti anonimi con formati differenti.
- [ ] Decidere il trattamento iniziale di imposte riportate, trasferimenti e
      operazioni societarie.
- [ ] Rimuovere le domande aperte e approvare la spec.

## Implementazione

- [ ] Definire modello, versione, tipi e validazione del registro.
- [ ] Implementare importazione CSV/XLSX con mapping, anteprima e conferma.
- [ ] Implementare identificativi e collisioni per un'importazione idempotente.
- [ ] Aggiungere il preset Directa come semplice configurazione del mapping.
- [ ] Implementare posizioni, cassa, costo, redditi e risultati contabili.
- [ ] Implementare TWRR e XIRR solo quando i flussi disponibili li rendono validi.
- [ ] Collegare cambi storici con fonte e data e rappresentare dati incompleti.
- [ ] Aggiungere registro e performance reale come sezioni distinte dal backtest.
- [ ] Aggiungere tutte le nuove chiavi ai quattro cataloghi.

## Test

- [ ] Rendere anonime e minimali tutte le fixture di movimenti.
- [ ] Coprire tipi, segni, validazione, versionamento e ricostruzione posizioni.
- [ ] Coprire mapping guidato, righe escluse, duplicati e collisioni.
- [ ] Coprire costo, vendite parziali, dividendi, commissioni, TWRR e XIRR.
- [ ] Coprire più valute, cambio esplicito e cambio storico mancante.
- [ ] Aggiungere una guardia sorgente per la separazione dal backtest.

## Verifica dei criteri di accettazione

- [ ] 1 · Almeno due CSV/XLSX differenti sono importabili con mapping guidato.
- [ ] 2 · I sei tipi minimi sono normalizzati e gli sconosciuti restano visibili.
- [ ] 3 · Anteprima e problemi precedono ogni scrittura nel registro.
- [ ] 4 · Reimport e collisioni non producono duplicati silenziosi.
- [ ] 5 · Tutti i campi minimi sono conservati senza credenziali.
- [ ] 6 · Posizioni, cassa, costo, dividendi e commissioni sono riconciliabili.
- [ ] 7 · Risultati realizzati e non realizzati usano il metodo dichiarato.
- [ ] 8 · TWRR, XIRR e backtest sono distinti e calcolati solo se validi.
- [ ] 9 · Valute e cambi espongono valore, fonte, data e incompletezza.
- [ ] 10 · Registro locale e portafoglio modello restano separati.
- [ ] 11 · I risultati sono dichiarati contabili, non imposte dovute.
- [ ] 12 · Quattro lingue e test automatici sono completi.

## Chiusura

- [ ] `uv run python -m unittest discover -s tests -p "test_*.py"` passa
- [ ] `uv run ruff check .` passa
- [ ] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [ ] Aggiunta una voce a `docs/memory-bank/02-decisioni.md` *(solo se è stata
      presa una decisione vincolante)*
- [ ] Aggiornato lo stato in cima a `spec.md`
