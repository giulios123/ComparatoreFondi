# 008 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [x] Implementare `InvestorProfile` versionato e persistenza separata con permessi 600.
- [x] Collegare il percorso dati utente nel bundle desktop.
- [x] Definire `PortfolioFinding` ed evidenze strutturate.
- [x] Implementare regole deterministiche: conflitti personali e fatti informativi senza soglie inventate.
- [x] Costruire il rapporto anonimo tramite allowlist, token temporanei e ordine stabile.
- [x] Mantenere la mappa asset reale/token soltanto in memoria.
- [x] Integrare editor profilo, diagnosi, anteprima payload e nessuna chiamata esterna.
- [x] Aggiungere i testi ai quattro cataloghi.

## Test

- [x] Profilo valido, parziale, assente, corrotto e cancellato.
- [x] Regole con benchmark, inflazione, overlap e dati presenti o mancanti.
- [x] Determinismo e ordine stabile dei rilievi.
- [x] Assenza di nomi, simboli, ISIN, importi, path e credenziali nel payload.
- [x] Bundle: profilo fuori dalla directory dell'app e non nell'export JSON.

## Verifica dei criteri di accettazione

- [x] 1 · profilo minimo completo e facoltativo.
- [x] 2 · storage locale separato e cancellabile.
- [x] 3 · nessuna soglia personale inventata.
- [x] 4 · rilievi deterministici con evidenze.
- [x] 5 · dati mancanti non trasformati in giudizi.
- [x] 6 · payload anonimo completo e privo di identificatori.
- [x] 7 · anteprima e test dei campi vietati.
- [x] 8 · sole azioni di simulazione, nessuna previsione/ordine.
- [x] 9 · test puri e quattro lingue.

## Chiusura

- [x] Suite unittest, ruff e `git diff --check` passano
- [x] Verifica permessi del file profilo su macOS/Windows per quanto applicabile
- [x] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [x] Aggiunta una decisione a `docs/memory-bank/02-decisioni.md`
- [x] Aggiornato lo stato in cima a `spec.md`
