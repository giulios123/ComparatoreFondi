# 002 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [x] `comparatore/engine.py`: `BacktestInputError(ValueError)` con `kind`,
      `symbols`, messaggio italiano
- [x] `comparatore/engine.py`: `valida_prezzi(prices, *, consenti_nan=False)`
- [x] `comparatore/engine.py`: `valida_holdings(holdings, colonne)`
- [x] `comparatore/engine.py`: `etichette_uniche(holdings)` — `Nome` se
      univoco, `Nome (SIMBOLO)` se duplicato
- [x] `comparatore/engine.py`: `simulate` valida i prezzi in modo stretto,
      rimosso `np.nan_to_num`
- [x] `comparatore/engine.py`: `run_backtest` valida holdings e prezzi
      (`consenti_nan=True`), non rinomina più le colonne, popola
      `BacktestResult.labels`
- [x] `app.py`: guardia bloccante prima della costruzione degli `Holding`
      (elenco simboli assenti, allocazione ricalcolata con
      `pesi.rinormalizza`, bottone, `st.stop()`)
- [x] `app.py`: `rimuovi_fondi_assenti(simboli)` accanto a `rimuovi_fondo()`
- [x] `app.py`: tolto il filtro `if f["symbol"] in prices.columns` dalla
      costruzione di `holdings`
- [x] `app.py`: ogni lettura di colonna/etichetta per nome passa da
      `res.labels` (contributions, allocazione finale, grafico di confronto,
      tabella metriche, drawdown, rendimenti annui, export CSV)
- [x] `app.py`: `except BacktestInputError` prima di `except ValueError`,
      traduce `exc.kind`
- [x] `comparatore/locales/it.py`: chiavi nuove (riferimento)
- [x] `comparatore/locales/en.py`, `fr.py`, `de.py`: stesse chiavi tradotte

## Test

- [x] `tests/test_engine.py`: prezzo zero, negativo, `inf`, `NaN` residuo
- [x] `tests/test_engine.py`: date duplicate nell'indice prezzi
- [x] `tests/test_engine.py`: simbolo duplicato fra gli holdings
- [x] `tests/test_engine.py`: holding senza colonna prezzi corrispondente
- [x] `tests/test_engine.py`: peso `NaN`/negativo, somma pesi zero
- [x] `tests/test_engine.py`: due holding con `label` identica e PAC attivo →
      nessuna eccezione, `per_fund` a due colonne (simboli), `labels` disambigua
- [x] `tests/test_app_sintassi.py`: la guardia dei fondi assenti precede
      `run_backtest`
- [x] `tests/test_app_sintassi.py`: `app.py` usa `res.labels` e non contiene
      più `label_splice` derivato dall'etichetta

## Verifica dei criteri di accettazione

- [x] 1 · fondo senza prezzi → backtest bloccato, elenco e allocazione reale
      mostrati. **Verificato a livello di libreria**, non nell'interfaccia
      dal vivo: Claude in Chrome non era connesso in questa sessione, quindi
      non è stato possibile guidare un browser sull'app in esecuzione. È
      stato eseguito uno script che riproduce esattamente il percorso di
      `app.py` (`Registry.resolve_many` → stessa espressione della guardia →
      `pesi.rinormalizza`) con un CSV reale e un simbolo inesistente: la
      guardia isola correttamente il simbolo assente e calcola l'allocazione
      di destinazione (100% sul fondo rimasto). Il rendering a video
      (`st.error`, `st.caption`, il bottone) non è stato osservato
      direttamente.
- [x] 2 · bottone di rimozione riporta i pesi a 100 e fa ripartire il calcolo.
      **Stessa riserva del punto 1**: `rimuovi_fondi_assenti()` riusa
      `pesi.rinormalizza()`, già coperto da `tests/test_pesi.py`; il click
      effettivo del bottone in un browser non è stato osservato.
- [x] 3 · quota non valida (zero/negativa/non finita) → errore con il simbolo,
      nessun grafico. Verificato sia a livello di libreria (script con un
      CSV reale contenente uno zero, `BacktestInputError` con
      `kind="quote_non_valide"` e il simbolo giusto) sia con test dedicati.
- [x] 4 · label duplicate + PAC → backtest completo, legenda distinguibile.
      Verificato a livello di libreria con due CSV reali e nomi identici,
      PAC attivo: nessuna eccezione, `res.labels` disambigua correttamente
      (`Stesso Nome Fondo (AAA)` / `(BBB)`).
- [x] 5 · portafoglio già valido → stessi numeri di prima. Verificato
      indirettamente: l'intera suite di test esistente (146 test, invariati)
      resta verde senza modifiche, compresi i test che confrontano `simulate`
      e `run_backtest` con formule chiuse.

## Chiusura

- [x] `uv run python -m unittest discover -s tests -p "test_*.py"` passa
      (162 test: 146 preesistenti + 16 nuovi)
- [x] `uv run ruff check .` pulito
- [x] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [x] Aggiunta la decisione 21 a `docs/memory-bank/02-decisioni.md`
- [x] Aggiornato lo stato in cima a `spec.md`
