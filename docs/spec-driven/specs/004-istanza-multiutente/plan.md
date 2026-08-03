# 004 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Una sola variabile d'ambiente, `COMPARATORE_HOSTED`, letta da una nuova
funzione `comparatore.hosted.is_hosted()` — non un ramo di codice separato o
un fork, ma la stessa convenzione già in uso per `COMPARATORE_CACHE_DIR` e le
altre tre variabili esistenti. È centralizzata in un modulo a sé (e non
riletta con `os.environ.get(...)` in ogni punto, come fanno invece
`keys.py`/`prefs.py`/`cache.py` per le proprie variabili) per un motivo
preciso: qui la correttezza dipende dal fatto che **tutti** i punti che la
leggono concordino sulla stessa interpretazione. Le altre variabili sono lette
da un solo modulo ciascuna, quindi un disallineamento lì avrebbe un impatto
limitato; `COMPARATORE_HOSTED` viene letta da almeno quattro punti diversi
(chiavi, preferenze, cache, `app.py`), e un disallineamento anche in uno solo
riaprirebbe esattamente il problema che la spec chiude.

Il resto dell'approccio, per ciascun criterio:

- **Chiavi e preferenze (criteri 1-3).** `keys.py` e `prefs.py` già degradano
  in silenzio quando il file è assente o illeggibile ("nessuna chiave/
  preferenza salvata" non è un errore, è un caso normale). La modalità
  ospitata estende esattamente questo comportamento esistente: `load()`
  restituisce sempre `{}`, `save()` e `clear()` non toccano il disco. Nessuna
  modifica ad `app.py` per questa parte: continua a chiamare le stesse
  funzioni di sempre, è la libreria a decidere se persistere. L'unica
  eccezione è `api_key()` in `app.py`, che deve smettere di ricadere su
  `st.secrets`/`os.environ` in modalità ospitata — non può stare in
  `keys.py` perché `st.secrets` è specifico di Streamlit.
- **justETF (criterio 4).** Il checkbox e il suo `st.expander` non vengono
  renderizzati in modalità ospitata. Difesa in profondità: `build_registry()`
  forza comunque `enable_justetf=False` quando ospitato, indipendentemente
  da cosa contenga `st.session_state` — stesso principio già scelto nella
  decisione 21 per la validazione del motore (l'ultima barriera non si fida
  di chi sta a monte).
- **Cache partizionata (criterio 5).** Una funzione `cache.scope_key(key, secret)`
  che, se `secret` è non vuoto, ne deriva un suffisso breve con lo stesso
  meccanismo già usato da `cache.py` per i nomi di file (SHA-1 troncato: non
  è un nuovo primitivo crittografico, è lo stesso già in campo). `EodhdSource`
  e `TwelveDataSource` la applicano a ogni chiave che costruiscono — inclusa
  `eodhd-fundamentals-blocked` — quando `hosted.is_hosted()`. In modalità non
  ospitata `scope_key` è un no-op: le chiavi restano identiche a oggi, zero
  invalidazione della cache esistente.
- **Tetto cache (criterio 6).** Nuova `cache.enforce_size_cap(max_mb)`: se
  `stats()` supera la soglia, elimina i file più vecchi per `mtime` finché non
  rientra. Richiamata da `build_registry()` insieme a `purge_expired()`, ma
  solo quando ospitato — non cambia il comportamento locale, dove il problema
  non si è mai presentato.
- **Pulsante svuota cache (criterio 7).** Nascosto in modalità ospitata,
  insieme alla chiamata a `disk_cache.clear_prefixes()` dentro "Dimentica le
  chiavi" (con la cache ora partizionata per chiave, un `clear_prefixes()`
  globale da un singolo visitatore cancellerebbe comunque le partizioni degli
  altri).
- **Upload (criterio 8).** `[server] maxUploadSize = 20` in
  `.streamlit/config.toml`, statico e non condizionato al flag: Streamlit
  legge questo file prima che il codice Python esegua, quindi non c'è un modo
  pulito per farlo dipendere da `COMPARATORE_HOSTED` senza un secondo file di
  config. 20 MB resta comunque ampiamente sopra le soglie applicative
  introdotte dalla spec 003 (1 MB JSON, 5 MB CSV) e ben sotto il default di
  200 MB: un cambiamento che non serve solo all'hosting, utile a prescindere.
- **Non-regressione (criterio 9).** Ogni ramo nuovo è condizionato da
  `hosted.is_hosted()`; a variabile assente il comportamento è bit-per-bit
  quello di oggi — è la ragione per cui i test esistenti non richiedono
  modifiche, solo aggiunte.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/hosted.py` *(nuovo)* | `is_hosted() -> bool`, legge `COMPARATORE_HOSTED` (vuoto/`"0"`/assente = `False`) |
| `comparatore/keys.py` | `load()`/`save()`/`clear()` diventano no-op quando `hosted.is_hosted()` |
| `comparatore/prefs.py` | Stesso trattamento di `keys.py` |
| `comparatore/cache.py` | Nuova `scope_key(key, secret)`; nuova `enforce_size_cap(max_mb)` |
| `comparatore/sources/eodhd.py` | Ogni chiave passata a `cache.read_meta`/`write_meta`/`get_or_fetch` passa da `scope_key(..., self.api_key)` quando ospitato |
| `comparatore/sources/twelvedata.py` | Stesso trattamento di `eodhd.py` |
| `app.py` | `api_key()` non ricade su `st.secrets`/`os.environ` quando ospitato; blocco justETF (checkbox + expander) e pulsante "Svuota cache" avvolti in `if not hosted.is_hosted():`; `build_registry()` forza `enable_justetf=False` e chiama `enforce_size_cap` quando ospitato; "Dimentica le chiavi" salta `clear_prefixes`/`st.cache_data.clear()` quando ospitato |
| `.streamlit/config.toml` | Aggiunta sezione `[server]` con `maxUploadSize = 20` |
| `comparatore/locales/{it,en,fr,de}.py` | Verifica che nessuna stringa nuova sia necessaria (i blocchi nascosti non introducono nuovi messaggi); se serve un avviso "non disponibile in questa modalità", chiave nuova nei quattro cataloghi |
| `tests/test_hosted_mode.py` *(nuovo)* | `is_hosted()`, no-op di chiavi/preferenze, `scope_key`, `enforce_size_cap`, con la stessa redirezione via variabile d'ambiente già usata in `test_cache.py`/`test_prefs.py` |
| `tests/test_app_sintassi.py` | Guardia che il blocco justETF e il pulsante "Svuota cache" sono dentro un `if` che referenzia `hosted.is_hosted()` |

Riuso esplicito: il meccanismo di degrado silenzioso già scritto in
`keys.py`/`prefs.py` (nessuna nuova gestione d'errore, solo un nuovo motivo
per restituire `{}`); lo schema SHA-1 troncato già usato da `cache.py` per i
nomi di file; il pattern "redirezione via variabile d'ambiente in `setUp`/
`tearDown`" già in `test_cache.py:14-17` e `test_prefs.py:11-22`; il principio
di validazione-come-ultima-barriera della decisione 21 per il guard su
`enable_justetf` in `build_registry()`.

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Un secondo file `app_hosted.py` o un flag passato a ogni funzione invece di una variabile d'ambiente letta internamente | Duplicherebbe l'interfaccia pubblica della libreria e romperebbe la promessa di `AGENTS.md` che `comparatore/` resta usabile da script: chi la usa da script otterrebbe comunque il comportamento giusto leggendo la stessa variabile, senza dover sapere che esiste una "modalità" separata da passare esplicitamente ovunque. |
| Leggere `COMPARATORE_HOSTED` con `os.environ.get(...)` direttamente in ognuno dei quattro punti, come fanno le altre variabili `COMPARATORE_*` | Coerente con lo stile esistente, ma qui la posta in gioco è diversa: un disallineamento fra `keys.py` e `cache.py` su cosa conta come "vero" (es. `"1"` accettato in un punto e non nell'altro) riaprirebbe silenziosamente il leak che la spec chiude. Un punto solo, con un test dedicato, è la scelta più sicura per l'unica variabile fra le cinque il cui malfunzionamento è un problema di sicurezza, non solo di configurazione. |
| Disattivare anche Yahoo e OpenFIGI in modalità ospitata, non solo justETF | È la raccomandazione della valutazione hosting, ma è dichiarata lì come decisione legale aperta, non presa. Deciderla dentro questo piano tecnico avrebbe forzato una scelta di prodotto che non è stata chiesta; resta un non-obiettivo esplicito, non un'omissione. |
| Partizionare la cache per sessione (`st.session_state` id) invece che per chiave API | La chiave è ciò che conta legalmente (i dati sono legati al piano di chi li ha scaricati, non alla sessione browser che li ha richiesti); partizionare per sessione avrebbe moltiplicato inutilmente le voci di cache per lo stesso visitatore che ricarica la pagina, senza risolvere il problema di licenza che è il motivo del criterio 5. |
| Un tetto di cache globale, attivo anche in modalità non ospitata | Cambierebbe un comportamento mai stato in discussione per l'uso locale, dove il problema non si è mai presentato (un solo utente, cache che cresce lentamente); tenerlo dietro al flag evita una regressione non richiesta. |

## Rischi

- **`scope_key` applicata solo ai punti di chiamata individuati.** Se
  `eodhd.py`/`twelvedata.py` acquisissero in futuro una nuova chiamata a
  `cache.read_meta`/`write_meta`/`get_or_fetch` senza passare da `scope_key`,
  quella voce tornerebbe condivisa silenziosamente. Non esiste un modo
  puramente meccanico di garantirlo (la cache non sa distinguere da sola
  "chiave giusta" da "chiave sbagliata"); mitigato solo dal fatto che i due
  moduli hanno pochissimi punti di chiamata, tutti elencati in questo piano.
- **`enforce_size_cap` elimina file per `mtime`, non per rilevanza.** Una
  voce riscritta di recente ma raramente utile sopravvive più a lungo di una
  usata spesso ma scritta prima; è una LRU approssimata, non esatta. Accettato
  perché il criterio 6 chiede un tetto, non una strategia di eviction
  ottimale — e aggiungere un contatore di accessi vero sarebbe la prima cosa
  spropositata per il problema che c'è.
- **`.streamlit/config.toml` cambia per tutti, non solo per l'hosting.** Un
  uso locale che oggi carica file sopra i 20 MB (poco plausibile per CSV/JSON
  di un portafoglio, ma possibile) smetterebbe di funzionare senza alzare il
  limite via `--server.maxUploadSize` o l'equivalente variabile d'ambiente
  Streamlit. Rischio giudicato basso e accettabile: nessun file di test o
  screenshot del progetto si avvicina a quella soglia.
- **I test di `app.py` restano strutturali, non comportamentali** (stessa
  riserva già scritta nella spec 002): la guardia AST verifica che il blocco
  giusto sia condizionato al flag giusto, non che renderizzi davvero in modo
  diverso in un browser. La verifica end-to-end resta manuale, con
  `COMPARATORE_HOSTED=1` esportata prima di avviare Streamlit.

## Verifica

1. `uv run python -m unittest discover -s tests -p "test_*.py"` — tutti i test
   esistenti restano verdi (nessuna variabile d'ambiente impostata di
   default), i nuovi passano.
2. `uv run ruff check .` pulito.
3. Senza `COMPARATORE_HOSTED`: `uv run streamlit run app.py` via CSV offline,
   comportamento identico a oggi (criterio 9) — chiave salvata visibile al
   riavvio, lingua ricordata, justETF disponibile.
4. Con `COMPARATORE_HOSTED=1` esportata prima del comando: due profili
   browser diversi (o una finestra normale e una in incognito) non condividono
   la chiave inserita nell'uno o nell'altro (criterio 1); nessun file compare
   in `.streamlit/` durante l'uso (criterio 2, controllato con `ls` durante la
   sessione); il blocco justETF non è visibile (criterio 4); il pulsante
   "Svuota cache" non è visibile (criterio 7).
5. Verifica di libreria per il criterio 5 (partizionamento): due chiamate a
   `EodhdSource(api_key="A")`/`EodhdSource(api_key="B")` con
   `COMPARATORE_HOSTED=1` producono percorsi di file diversi in `.cache/` per
   lo stesso simbolo — controllabile con uno script, senza rete, ispezionando
   `cache.scope_key` direttamente.
