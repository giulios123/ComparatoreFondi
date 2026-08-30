# 014 · Attivita'

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [x] Aggiungere heatmap e rolling puri, inclusi periodi parziali e coperture.
- [x] Correggere Sortino, aggiungere Ulcer Index e correggere rolling mensile.
- [x] Aggiungere simulatore batch, campionamento vincolato e affinamento.
- [x] Integrare scheda Analisi, grafici, download e applicazione confermata.
- [x] Aggiungere tutte le chiavi IT/EN/FR/DE.

## Test

- [x] Test numerici con fixture manuali per calendario e metriche.
- [x] Test di vincoli, riproducibilita', PAC, ribilanciamento e fingerprint.
- [x] Test export/import, applicazione e guardie di `app.py`.

## Verifica dei criteri di accettazione

- [x] 1–4 · Scheda, heatmap e rolling verificati offline.
- [x] 5–6 · Frontiera, risultati e applicazione verificati offline.
- [x] 7–8 · Metriche, localizzazioni e suite completa verificati.

## Chiusura

- [x] `uv run python -m unittest discover -s tests -p "test_*.py"` passa
- [x] `uv run ruff check .` passa
- [x] Aggiornato `README.md` e `docs/memory-bank/03-stato-attuale.md`
- [x] Aggiunta decisione in `docs/memory-bank/02-decisioni.md`
- [x] Aggiornato lo stato in cima a `spec.md`
