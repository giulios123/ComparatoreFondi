# 006 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [x] Definire `HoldingPosition`, `FundHoldings`, `FundCoverage`, `PairOverlap`, `PortfolioExposure` e `OverlapReport` in `comparatore/overlap.py`.
- [x] Implementare validazione delle quote, matching deterministico e gestione delle ambiguita'.
- [x] Calcolare copertura, matrice pairwise ed esposizione aggregata senza rinormalizzare.
- [x] Propagare identificatore, tipo, fonte e data delle holdings senza rompere i vecchi metadati.
- [x] Integrare copertura, matrice, dettaglio coppie e concentrazioni nella scheda Bilanciamento.
- [x] Esporre un riepilogo strutturato e anonimo consumabile dalla spec 008.
- [x] Aggiornare i quattro cataloghi.

## Test

- [x] Copertura completa, parziale, assente e dati datati.
- [x] Overlap noto senza rinormalizzazione e `n/d` per dati insufficienti.
- [x] Identificatori, simboli, nomi, duplicati e collisioni ambigue.
- [x] Aggregazione ponderata del portafoglio.
- [x] Compatibilita' JSON e regressione dei grafici esistenti.

## Verifica dei criteri di accettazione

- [x] 1 · copertura, fonte e data per fondo.
- [x] 2 · overlap come limite inferiore non rinormalizzato, anche con copertura parziale.
- [x] 3 · matrice con `n/d` per casi non affidabili.
- [x] 4 · esposizione aggregata e quota sconosciuta.
- [x] 5 · matching stabile e ambiguita' non fuse.
- [x] 6 · fondi senza holdings visibili e non bloccanti.
- [x] 7 · correzioni manuali e bilanciamento invariati.
- [x] 8 · risultato anonimo strutturato.
- [x] 9 · test e quattro lingue.

## Chiusura

- [x] Suite unittest, ruff e `git diff --check` passano
- [ ] Verifica visuale con holdings complete, parziali e assenti
- [x] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [x] Aggiunta una decisione a `docs/memory-bank/02-decisioni.md`
- [x] Aggiornato lo stato in cima a `spec.md`
