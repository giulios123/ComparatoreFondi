# 008 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [ ] Implementare `InvestorProfile` e persistenza separata con permessi 600.
- [ ] Collegare il percorso dati utente nel bundle desktop.
- [ ] Definire `PortfolioFinding` ed evidenze strutturate.
- [ ] Implementare le prime regole deterministiche senza soglie inventate.
- [ ] Costruire il rapporto anonimo tramite allowlist.
- [ ] Mantenere la mappa asset reale/token soltanto in memoria.
- [ ] Integrare editor profilo, diagnosi e anteprima payload.
- [ ] Aggiungere i testi ai quattro cataloghi.

## Test

- [ ] Profilo valido, parziale, assente, corrotto e cancellato.
- [ ] Regole con benchmark/dati presenti e mancanti.
- [ ] Determinismo e ordine stabile dei rilievi.
- [ ] Assenza di nomi, simboli, ISIN, importi, path e credenziali nel payload.
- [ ] Bundle: profilo fuori dalla directory dell'app.

## Verifica dei criteri di accettazione

- [ ] 1 · profilo minimo completo e facoltativo.
- [ ] 2 · storage locale separato e cancellabile.
- [ ] 3 · nessuna soglia personale inventata.
- [ ] 4 · rilievi deterministici con evidenze.
- [ ] 5 · dati mancanti non trasformati in giudizi.
- [ ] 6 · payload anonimo completo e privo di identificatori.
- [ ] 7 · anteprima e test dei campi vietati.
- [ ] 8 · sole azioni di simulazione, nessuna previsione/ordine.
- [ ] 9 · test puri e quattro lingue.

## Chiusura

- [ ] Suite unittest, ruff e `git diff --check` passano
- [ ] Verifica permessi del file profilo su macOS/Windows per quanto applicabile
- [ ] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [ ] Aggiunta una decisione a `docs/memory-bank/02-decisioni.md`
- [ ] Aggiornato lo stato in cima a `spec.md`
