# 009 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [ ] Verificare che le spec 007 e 008 siano fatte e favorevoli.
- [ ] Definire protocollo, schema, errori e validazione delle evidenze.
- [ ] Implementare l'adattatore Copilot senza tool e con import opzionale.
- [ ] Versionare il prompt e vietare previsione/asset esterni.
- [ ] Integrare anteprima e invio soltanto su azione esplicita.
- [ ] Validare la risposta prima del remapping locale degli asset.
- [ ] Implementare scenari dichiarativi e conferma separata.
- [ ] Gestire login, rete, quota, timeout e risposta invalida.
- [ ] Aggiornare cataloghi, bundle e licenze secondo la spec 007.

## Test

- [ ] Mock di risposta valida e di ogni errore previsto.
- [ ] Evidenze inesistenti, asset inventati e schema invalido.
- [ ] Nessun identificatore nel payload e nessun tool registrato.
- [ ] Nessuna chiamata al normale rerun/backtest.
- [ ] Scenari non mutanti prima della conferma e pesi validi dopo.
- [ ] Casi campione senza linguaggio predittivo.

## Verifica dei criteri di accettazione

- [ ] 1 · invio solo esplicito.
- [ ] 2 · anteprima completa di provider, modello e payload.
- [ ] 3 · solo dati anonimi.
- [ ] 4 · sessione senza strumenti e memoria richiesta.
- [ ] 5 · risposta strutturata completa.
- [ ] 6 · riferimenti invalidi respinti.
- [ ] 7 · indicazioni/scenari senza previsione o mutazione automatica.
- [ ] 8 · lingua corrente e remapping locale.
- [ ] 9 · errori distinti, rapporto locale sempre disponibile.
- [ ] 10 · mock ed eval di privacy/comportamento.

## Chiusura

- [ ] Suite unittest, ruff e `git diff --check` passano
- [ ] Audit licenze e build desktop passano su macOS/Windows
- [ ] Verifica manuale con payload fittizio e account Copilot
- [ ] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [ ] Aggiunta una decisione a `docs/memory-bank/02-decisioni.md`
- [ ] Aggiornato lo stato in cima a `spec.md`
