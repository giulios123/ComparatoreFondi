# 013 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Un catalogo puro e versionato descrive nome, fonte, allocazione canonica e
strumenti eseguibili. La persistenza salva solo l'ID stabile. L'interfaccia
seleziona il catalogo in un `st.popover`; il calcolo risolve ogni componente,
costruisce il calendario comune e usa il motore esistente con `YEARLY` per i
modelli fissi. La vista benchmark resta a valle del backtest principale.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/benchmark_portfolios.py` | Catalogo, proxy, metadati e validazione |
| `comparatore/portfolio_io.py` | Schema opzionale `kind=portfolio` |
| `comparatore/locales/*.py` | Etichette, descrizioni e diagnosi nelle quattro lingue |
| `app.py` | Popover, import/export e calcolo composito |
| `tests/test_benchmark_portfolios.py` | Test catalogo e simulazione offline |
| `tests/test_portfolio_io.py` | Round-trip e compatibilità JSON |
| `tests/test_app_sintassi.py` | Guardie popover, tooltip e separazione holdings |
| `README.md`, `docs/memory-bank/*` | Documentazione e decisione architetturale |

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Inserire i portafogli tra le holdings | Fonderebbe benchmark e portafoglio dell'utente |
| Un selectbox con 25 righe | Lista lunga e poco usabile su mobile |
| Proxy di asset class diverso | Altererebbe l'esposizione e nasconderebbe il rischio |
| CSS/JavaScript per il tooltip | Il ritardo nativo è sufficiente e più accessibile |

## Rischi

- un simbolo EUR può avere uno storico più corto o non risolversi: il
  fallimento deve essere atomico e diagnosticato per sleeve;
- strumenti gestiti USA e oro ETC hanno eccezioni operative: devono essere
  visibili nella scheda e nel tooltip;
- un catalogo con pesi errati può produrre numeri credibili: la validazione
  automatica blocca importi diversi da 100%.

## Verifica

1. `uv run python -m unittest discover -s tests -p "test_*.py"`.
2. `uv run ruff check .` e `git diff --check`.
3. Smoke `uv run streamlit run app.py` e QA manuale desktop/mobile con quattro
   lingue, PAC attivo, ricerca, import/export e componente mancante.
4. Verifica live non-CI delle quotazioni e degli ISIN; correggere solo con una
   quotazione EUR dello stesso ISIN.
