# 003 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [x] Aggiungere i contratti di diagnostica metadati e la provenienza TER.
- [x] Correggere mapping Yahoo/EODHD e retry/cache dei metadati.
- [x] Implementare parser e modelli normalizzati Directa.
- [x] Riconoscere intestazioni dopo righe descrittive e distinguere export
  Movimenti dagli export di posizioni senza reinterpretare gli importi.
- [x] Persistire e mostrare politica di distribuzione e metodo di replica,
  con fallback n/d quando la fonte non li espone.
- [x] Dare precedenza al TER justETF opt-in sul valore Yahoo automatico,
  lasciando protetto l'override manuale.
- [x] Integrare anteprima, mappatura, risoluzione e import nell'app.
- [x] Usare justETF come fonte TER preferita solo con opt-in esplicito.
- [x] Implementare regole e stima costi PIC.
- [x] Integrare editor, persistenza e prospetto localizzato.
- [x] Aggiornare i quattro cataloghi e backfill JSON.

## Test

- [x] Test TER, mapping, retry e override manuale.
- [x] Test precedenza justETF quando Yahoo restituisce un TER diverso.
- [x] Test Directa CSV/XLSX e diagnostica righe.
- [x] Test campione Movimenti Directa: intestazione automatica, alias e blocco
  dell'import senza controvalore attuale.
- [x] Test campione Posizioni Directa, metadati ETF e compatibilita' JSON.
- [x] Test commissioni, budget, arrotondamento e montante netto.
- [x] Test compatibilita' portfolio e guardie AST.
- [x] Regressioni su piazza MI e visualizzazione delle commissioni alla precisione monetaria.

## Verifica dei criteri di accettazione

- [x] 1 · Diagnostica TER visibile e fonte conservata.
- [x] 2 · Retry senza sovrascrivere manuale.
- [x] 3 · Import mappato senza scarti silenziosi.
- [x] 4 · Prospetto PIC completo.
- [x] 5 · PAC e backtest invariati.
- [x] 6 · JSON precedente compatibile.
- [x] 7 · Suite e lint verdi.
- [x] 8 · Caratteristiche ETF e compatibilita' dei portafogli precedenti.

## Chiusura

- [x] `uv run python -m unittest discover -s tests -p "test_*.py"` passa
- [x] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [x] Aggiornato lo stato in cima a `spec.md`
