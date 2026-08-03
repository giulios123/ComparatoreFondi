# 003 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

Ogni voce è spuntabile guardando qualcosa. Se non lo è, non è un'attività.

## Implementazione

- [ ] `comparatore/portfolio_io.py`: costanti `_PESO_MAX = 100.0`,
      `_TER_MAX = 10.0`, `_DIMENSIONE_MASSIMA_BYTES`, `_FONDI_MASSIMI`, con
      commento che rimanda ai bound dell'editor in `app.py`
- [ ] `comparatore/portfolio_io.py`: `load()` respinge un file oltre
      `_DIMENSIONE_MASSIMA_BYTES` prima del parsing JSON
- [ ] `comparatore/portfolio_io.py`: `load()` respinge più di `_FONDI_MASSIMI`
      fondi
- [ ] `comparatore/portfolio_io.py`: per ogni fondo, `weight` deve essere
      numerico, finito, in `[0, _PESO_MAX]`
- [ ] `comparatore/portfolio_io.py`: per ogni fondo, `ter` ed `extra` (se
      presenti) devono essere numerici, finiti, in `[0, _TER_MAX]`
- [ ] `comparatore/portfolio_io.py`: `symbol` non vuoto (dopo `strip()`) e non
      ripetuto fra i fondi del file
- [ ] `comparatore/sources/csv_source.py`: costante dimensione massima in
      byte; `parse_csv` la controlla prima di decodificare
- [ ] `comparatore/sources/csv_source.py`: dopo il filtro `notna()`, verifica
      `> 0` e `isfinite` sulle quote; `CsvParseError` con la data della prima
      riga non valida
- [ ] `app.py`: `pesi.rinormalizza(...)` spostato dentro il blocco
      `try`/`except portfolio_io.PortfolioError`
- [ ] `app.py`: `except CsvParseError` mostra
      `t("csv.parse_error", errore=str(exc))`
- [ ] `comparatore/locales/it.py`: nuova chiave `csv.parse_error`
- [ ] `comparatore/locales/en.py`, `fr.py`, `de.py`: stessa chiave tradotta

## Test

- [ ] `tests/test_portfolio_io.py`: `weight` stringa non numerica
- [ ] `tests/test_portfolio_io.py`: `weight` `NaN`/`inf`
- [ ] `tests/test_portfolio_io.py`: `weight` negativo e `weight` > 100
- [ ] `tests/test_portfolio_io.py`: `ter`/`extra` negativi e oltre `_TER_MAX`
- [ ] `tests/test_portfolio_io.py`: `symbol` vuoto o solo spazi
- [ ] `tests/test_portfolio_io.py`: due fondi con lo stesso `symbol`
- [ ] `tests/test_portfolio_io.py`: file oltre la soglia di dimensione
- [ ] `tests/test_portfolio_io.py`: più fondi della soglia massima
- [ ] `tests/test_csv_source.py` *(nuovo)*: quota zero → `CsvParseError` con
      la data
- [ ] `tests/test_csv_source.py`: quota negativa → idem
- [ ] `tests/test_csv_source.py`: quota infinita → idem
- [ ] `tests/test_csv_source.py`: file oltre la soglia di dimensione
- [ ] `tests/test_csv_source.py`: un CSV valido continua a passare invariato
      (non regressione, criterio 7)
- [ ] `tests/test_app_sintassi.py`: guardia che `rinormalizza(` compare dopo
      `try:` e prima del corrispondente `except portfolio_io.PortfolioError`
- [ ] `tests/test_i18n.py` resta verde con la chiave nuova in tutte e quattro
      le lingue

## Verifica dei criteri di accettazione

- [ ] 1 · `weight` non numerico/non finito/fuori range → errore tradotto, non
      un traceback
- [ ] 2 · `ter`/`extra` non numerico/non finito/fuori range → stesso
      trattamento
- [ ] 3 · `symbol` vuoto o duplicato → respinto, indicando quale
- [ ] 4 · JSON oltre soglia dimensione/numero fondi → respinto prima del
      parsing completo
- [ ] 5 · CSV con quota non valida → respinto al caricamento, data nel
      messaggio
- [ ] 6 · CSV oltre soglia dimensione → respinto prima del parsing
- [ ] 7 · JSON e CSV già validi oggi → nessuna regressione

## Chiusura

- [ ] `uv run python -m unittest discover -s tests -p "test_*.py"` passa
- [ ] `uv run ruff check .` pulito
- [ ] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [ ] Aggiunta una voce a `docs/memory-bank/02-decisioni.md` *(solo se è stata
      presa una decisione vincolante)*
- [ ] Aggiornato lo stato in cima a `spec.md`
