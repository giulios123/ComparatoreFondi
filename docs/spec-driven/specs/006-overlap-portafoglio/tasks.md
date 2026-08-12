# 006 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [ ] Definire holdings normalizzate e risultati in `comparatore/overlap.py`.
- [ ] Implementare matching deterministico e gestione delle ambiguita'.
- [ ] Calcolare copertura, matrice pairwise ed esposizione aggregata.
- [ ] Propagare fonte/data delle holdings senza rompere i vecchi metadati.
- [ ] Integrare viste e avvisi nella scheda Bilanciamento.
- [ ] Esportare un riepilogo anonimo consumabile dalla spec 008.
- [ ] Aggiornare i quattro cataloghi.

## Test

- [ ] Copertura completa, parziale e assente.
- [ ] Overlap noto senza rinormalizzazione.
- [ ] Identificatori, simboli, nomi e collisioni ambigue.
- [ ] Aggregazione ponderata del portafoglio.
- [ ] Compatibilita' JSON e regressione dei grafici esistenti.

## Verifica dei criteri di accettazione

- [ ] 1 · copertura e fonte per fondo.
- [ ] 2 · overlap come limite inferiore non rinormalizzato.
- [ ] 3 · matrice con `n/d` per casi non affidabili.
- [ ] 4 · esposizione aggregata e quota sconosciuta.
- [ ] 5 · matching stabile e ambiguita' non fuse.
- [ ] 6 · fondi senza holdings visibili e non bloccanti.
- [ ] 7 · correzioni manuali e bilanciamento invariati.
- [ ] 8 · risultato anonimo strutturato.
- [ ] 9 · test e quattro lingue.

## Chiusura

- [ ] Suite unittest, ruff e `git diff --check` passano
- [ ] Verifica visuale con holdings complete, parziali e assenti
- [ ] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [ ] Aggiunta una decisione a `docs/memory-bank/02-decisioni.md`
- [ ] Aggiornato lo stato in cima a `spec.md`
