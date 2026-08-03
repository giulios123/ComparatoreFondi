# 004 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

Ogni voce è spuntabile guardando qualcosa. Se non lo è, non è un'attività.

## Implementazione

- [ ] `comparatore/hosted.py` *(nuovo)*: `is_hosted() -> bool` legge
      `COMPARATORE_HOSTED`, vuoto/assente/`"0"` = `False`
- [ ] `comparatore/keys.py`: `load()` restituisce `{}` quando `is_hosted()`
- [ ] `comparatore/keys.py`: `save()` e `clear()` non toccano il disco quando
      `is_hosted()`
- [ ] `comparatore/prefs.py`: stesso trattamento di `keys.py` per
      `load()`/`save()`
- [ ] `comparatore/cache.py`: `scope_key(key: str, secret: str) -> str`, no-op
      se `secret` vuoto, altrimenti suffisso SHA-1 troncato (stesso schema
      del filename esistente)
- [ ] `comparatore/cache.py`: `enforce_size_cap(max_mb: float) -> None`,
      elimina i file più vecchi per `mtime` finché `stats()` rientra nel tetto
- [ ] `comparatore/sources/eodhd.py`: ogni chiave di cache passa da
      `cache.scope_key(..., self.api_key)` quando `hosted.is_hosted()`
      (`eodhd/`, `eodhd-sym/`, `eodhd-ccy/`, `eodhd-fundamentals-blocked`)
- [ ] `comparatore/sources/twelvedata.py`: stesso trattamento
      (`twelvedata/`, `twelvedata-ccy/`)
- [ ] `app.py`: `api_key()` salta il fallback `st.secrets`/`os.environ`
      quando `hosted.is_hosted()`
- [ ] `app.py`: blocco checkbox + expander justETF avvolto in
      `if not hosted.is_hosted():`
- [ ] `app.py`: `build_registry()` forza `enable_justetf=False` quando
      ospitato, indipendentemente da `st.session_state`
- [ ] `app.py`: `build_registry()` chiama `disk_cache.enforce_size_cap(...)`
      quando ospitato, soglia da `COMPARATORE_CACHE_MAX_MB` (stesso schema di
      `restricted_retention_days()`)
- [ ] `app.py`: pulsante "Svuota cache" avvolto in
      `if not hosted.is_hosted():`
- [ ] `app.py`: "Dimentica le chiavi" salta `disk_cache.clear_prefixes(...)`
      e `st.cache_data.clear()` quando ospitato
- [ ] `.streamlit/config.toml`: sezione `[server]` con `maxUploadSize = 20`

## Test

- [ ] `tests/test_hosted_mode.py` *(nuovo)*: `is_hosted()` per variabile
      assente, `""`, `"0"`, `"1"`
- [ ] `tests/test_hosted_mode.py`: `keys.load()/save()/clear()` no-op sotto
      `COMPARATORE_HOSTED=1` (redirezione file via `COMPARATORE_KEYS_FILE` +
      `tempfile`, stesso pattern di `test_cache.py`)
- [ ] `tests/test_hosted_mode.py`: stesso trattamento per `prefs.py`
- [ ] `tests/test_hosted_mode.py`: `cache.scope_key` no-op a secret vuoto,
      output diverso per secret diversi, stabile per lo stesso secret
- [ ] `tests/test_hosted_mode.py`: `cache.enforce_size_cap` elimina i file più
      vecchi finché sotto soglia, su una cartella temporanea popolata ad hoc
- [ ] `tests/test_hosted_mode.py`: `EodhdSource`/`TwelveDataSource` con due
      `api_key` diverse producono chiavi di cache diverse quando ospitato,
      identiche quando non ospitato (non-regressione, criterio 9)
- [ ] `tests/test_app_sintassi.py`: guardia che il blocco justETF è dentro un
      `if` che referenzia `hosted.is_hosted()`
- [ ] `tests/test_app_sintassi.py`: guardia che il pulsante "Svuota cache" è
      dentro lo stesso tipo di `if`
- [ ] Suite esistente (`test_cache.py`, `test_keys.py`, `test_prefs.py`)
      resta verde senza modifiche, a conferma della non-regressione (criterio 9)

## Verifica dei criteri di accettazione

- [ ] 1 · due sessioni non vedono le chiavi l'una dell'altra
- [ ] 2 · nessuna scrittura in `.streamlit/` in modalità ospitata
- [ ] 3 · lingua non condivisa fra sessioni; rilevamento automatico attivo
- [ ] 4 · checkbox justETF non disponibile in modalità ospitata
- [ ] 5 · cache partizionata per chiave, incluso il flag fondamentali bloccati
- [ ] 6 · tetto di dimensione della cache rispettato
- [ ] 7 · pulsante "Svuota cache" non disponibile in modalità ospitata
- [ ] 8 · limite di caricamento più stretto del default
- [ ] 9 · nessuna regressione a `COMPARATORE_HOSTED` assente

## Chiusura

- [ ] `uv run python -m unittest discover -s tests -p "test_*.py"` passa
- [ ] `uv run ruff check .` pulito
- [ ] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [ ] Aggiunta una voce a `docs/memory-bank/02-decisioni.md` *(probabile: la
      scelta di `COMPARATORE_HOSTED` come unico interruttore vincola come si
      aggiunge ogni comportamento multiutente futuro)*
- [ ] Aggiornato lo stato in cima a `spec.md`
