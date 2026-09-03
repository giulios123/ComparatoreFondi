# 015 · Attivita'

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [x] Parser puro del rendiconto CSV a sezioni.
- [x] Join con la sezione Financial Instrument Information e diagnosi Summary/Lot.
- [x] Conversione multi-valuta con cambio ricavato, BCE/Yahoo e override manuale.
- [x] Expander Streamlit sotto Directa con risoluzione scalabile.
- [x] Traduzioni IT/EN/FR/DE e guardie sorgente.

## Test

- [x] Fixture sintetica italiana/inglese e test del parser.
- [x] Test FX, riconciliazione, fallback e dati non supportati.
- [x] Suite completa, Ruff, diff check e smoke test offline.

## Chiusura

- [x] Aggiornare `02-decisioni.md` e `03-stato-attuale.md`.
- [x] Portare lo stato della spec a `fatta` solo dopo la verifica completa.
