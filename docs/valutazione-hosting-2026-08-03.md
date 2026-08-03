# Valutazione: hosting su un sito web

**Data:** 3 agosto 2026
**Revisione:** `033c24d`
**Ambito:** impatto tecnico e legale di rendere l'app raggiungibile da più
visitatori tramite un sito web, invece che eseguita in locale da un utente
solo. Non sono stati modificati comportamenti applicativi durante l'analisi.

## Sintesi

L'app è stata progettata, fin dalla [decisione 1](memory-bank/02-decisioni.md),
per un utente solo su una macchina sola: il launcher desktop si lega a
`localhost`, e tre store — chiavi API, preferenze, cache — sono file **di
processo**, non per visitatore. Ospitarla su un sito web non è una questione di
infrastruttura soltanto: buona parte dello stato che oggi è innocuo perché c'è
un solo utente diventa, con più visitatori, o un difetto di correttezza (un
visitatore vede o cancella la chiave di un altro) o un problema di licenza (dati
presi con la chiave di A serviti a B).

Lo scenario valutato, su richiesta, è **istanza pubblica con chiavi
dell'utente** ("BYO-key"): ogni visitatore inserisce le proprie chiavi EODHD e
Twelve Data. È lo scenario pubblico più difendibile sul piano dei termini
d'uso, ma **non è sufficiente da solo**: risolve le fonti a chiave, non tocca
quelle senza chiave (Yahoo, justETF, OpenFIGI) che sono interrogate dal server
a nome di visitatori anonimi — e Yahoo è la fonte predefinita.

| Area | Stato oggi | Bloccante per l'hosting? |
|---|---|---|
| Chiavi API | File di processo condiviso, riscrivibile da chiunque dalla UI | Sì |
| Preferenze (lingua, opt-in justETF) | File di processo condiviso | Sì |
| Cache disco | Nessun tetto, nessuna partizione per chiave/licenza | Sì (per le fonti a chiave) |
| Validazione input (import JSON/CSV) | P2 aperto dall'audit, nessun cambiamento | Sì |
| Fonti senza chiave (Yahoo, justETF, OpenFIGI) | Sempre attive, nessuna chiave dell'utente le protegge | Decisione da prendere, non solo tecnica |
| Esercizio (rate limiting, timeout, upload) | Assente ovunque | Necessario, non bloccante da solo |
| Config server / artefatti di deploy | Inesistenti | Necessario |

Il resto del documento motiva questa tabella riga per riga, con riferimenti
verificabili nel codice.

## Perché "BYO-key" non chiude da solo il problema

Le fonti si dividono in due gruppi, e la distinzione è quella che conta:

- **A chiave:** EODHD, Twelve Data. Con BYO-key, i dati arrivano con la chiave
  del visitatore: la responsabilità del piano e dei suoi limiti resta sua.
- **Senza chiave:** Yahoo (fonte predefinita, via `yfinance`), justETF
  (opt-in, endpoint interno non documentato), OpenFIGI (tier anonimo). Queste
  fonti **non hanno alcuna nozione di "utente"**: ogni richiesta parte dal
  server, con l'IP e le credenziali implicite del server, indipendentemente da
  chi la trigghera nel browser.

Il README lo dice già in termini legali, in [§ "Licenza del codice e termini
dei dati"](../README.md): i dati di Yahoo Finance sono per uso personale, e i
piani EODHD/Twelve Data ordinari vietano redistribuzione o display a terzi
senza approvazione. In un'istanza multiutente, chi fa quella richiesta al
provider è l'operatore del sito, non il singolo visitatore — indipendentemente
da chi vede il risultato nel browser. BYO-key sposta la responsabilità sulle
fonti a chiave; le fonti senza chiave restano responsabilità di chi ospita,
qualunque sia lo scenario.

**Conclusione:** un'istanza pubblica BYO-key è, più precisamente, un'istanza
dove *le fonti a chiave sono dell'utente e quelle senza chiave sono
responsabilità di chi la ospita*. L'opzione più semplice da difendere è
**spegnere Yahoo, justETF e OpenFIGI in modalità ospitata**, lasciando solo le
fonti a chiave e il caricamento CSV/import JSON (già offline per definizione).
Ogni alternativa — tenerle accese, magari con un avviso — è un rischio assunto
consapevolmente, non un problema che l'ingegneria da sola risolve.

## Stato globale: il nodo tecnico centrale

Tutto ciò che persiste sopravvive al processo, non alla sessione; l'unico
stato realmente per-visitatore è `st.session_state`. Tre store attraversano
quel confine.

### Chiavi API

`st.session_state.api_keys` viene inizializzato da `api_keys_store.load()` a
ogni nuova sessione ([app.py:59](../app.py:59)) — cioè da un **file unico**
([keys.py:24-29](../comparatore/keys.py:24)). Il form nella barra laterale
scrive nello stesso file ([app.py:648](../app.py:648)): un visitatore B che si
collega dopo A eredita la chiave di A, ne vede le ultime quattro cifre tramite
`masked()` ([app.py:657](../app.py:657), [keys.py:32-39](../comparatore/keys.py:32)),
ne consuma la quota, e può cancellarla per tutti con "Dimentica"
([app.py:661-666](../app.py:661), che chiama anche `disk_cache.clear_prefixes`
e `st.cache_data.clear()` — una cancellazione cache globale innescata da un
solo visitatore).

Anche azzerando quel file, `api_key()` ricade su `st.secrets` poi
`os.environ` ([app.py:235-251](../app.py:235)). Se chi ospita imposta
`EODHD_API_KEY` nell'ambiente del server — è la via che il README consiglia
per i deploy — ogni visitatore **senza** chiave propria la userebbe in
silenzio. Questo non è più BYO-key: è la chiave dell'operatore prestata a
sconosciuti. La modalità ospitata deve disabilitare esplicitamente questo
fallback, non solo smettere di scrivere il file.

### Preferenze

Stessa forma: `prefs.save()` scrive lingua e opt-in justETF in un file unico
([prefs.py:51-69](../comparatore/prefs.py:51)), letto a ogni rerun di ogni
sessione ([app.py:38](../app.py:38)). Due conseguenze concrete:

- **L'opt-in justETF diventa globale.** Un visitatore anonimo che lo attiva lo
  attiva per tutti ([app.py:622-628](../app.py:622)). Il modello di consenso
  descritto nel README — "ricordato su questo computer", con l'IP dichiarato
  esplicitamente all'utente prima del consenso — presuppone un computer per
  utente. Su un server, l'IP che justETF riceve è quello del server, non del
  visitatore che ha dato il consenso: il consenso stesso perde di significato.
- **La lingua si blocca sulla prima scelta salvata.** La catena di
  rilevamento per-visitatore — `st.context.locale` → `Accept-Language` →
  locale di sistema ([i18n.rileva](../comparatore/i18n.py)) — è già corretta e
  già per-sessione, ma [app.py:131-134](../app.py:131) la scavalca appena
  `saved_prefs["lingua"]` esiste. Non è un problema nuovo da progettare: è una
  riga che va condizionata alla modalità ospitata perché la logica sotto torni
  a essere raggiunta.

### Cache disco

Nessun tetto di dimensione o di conteggio file, nessuna LRU
([cache.py](../comparatore/cache.py) — `stats()` alle righe
[287-292](../comparatore/cache.py:287) riporta soltanto, non applica limiti).
Il TTL di 24 ore ([cache.py:34](../comparatore/cache.py:34)) è freschezza, non
eliminazione: una voce scaduta viene riletta e sovrascritta. L'unica
cancellazione vera è `purge_expired`, e riguarda solo EODHD/Twelve Data, con
un tetto di 30 giorni ([cache.py:40-46](../comparatore/cache.py:40),
richiamata a ogni rerun in [app.py:260-261](../app.py:260)). Yahoo, FX,
justETF, OpenFIGI e COVIP non vengono mai eliminati: ogni simbolo digitato da
un visitatore qualunque diventa un file permanente sul disco del server.

Due conseguenze specifiche dell'hosting, non solo di spazio disco:

- **Licenza.** In BYO-key, i dati EODHD/Twelve Data scaricati con la chiave di
  A non devono finire serviti a B dalla cache condivisa — è esattamente il
  "display a terzi" che i piani vietano. La cache va partizionata per chiave
  (o disabilitata) per queste due fonti.
- **Accoppiamento fra visitatori.** `eodhd-fundamentals-blocked` è un flag di
  cache condiviso: un 403 sul piano free di un visitatore disabilita i
  fondamentali per **tutti** per un giorno
  ([eodhd.py:71-80](../comparatore/sources/eodhd.py:71)).

Il pulsante "Svuota cache" è `shutil.rmtree` dell'intera cartella, offerto
senza controllo a chiunque ([app.py:718-722](../app.py:718),
[cache.py:278-284](../comparatore/cache.py:278)): un solo visitatore può
azzerare la cache di tutti e provocare una tempesta di refetch simultanei.

## Esercizio e robustezza

- **Nessun rate limiting, retry o backoff da nessuna parte** — confermato per
  assenza (`requests.Session`, `HTTPAdapter`, `Retry`, `backoff` non compaiono
  in `comparatore/`). Frankfurter e COVIP hanno un timeout di **60 secondi**
  ([fx.py:38](../comparatore/fx.py:38),
  [covip.py:47](../comparatore/covip.py:47)); il codice stesso documenta una
  risposta a freddo misurata di 27 secondi. Streamlit dà a ogni sessione il
  proprio thread: N visitatori concorrenti significano N richieste esterne
  concorrenti, senza alcun tetto.
- **Upload al default Streamlit di 200 MB**, interamente in RAM
  ([.streamlit/config.toml](../.streamlit/config.toml) imposta solo
  `toolbarMode`). `parse_csv` non ha limiti di righe o byte e tenta fino a
  quattro passate `pd.read_csv` sul testo intero
  ([csv_source.py:103-137](../comparatore/sources/csv_source.py:103)).
- **Input non validato semanticamente** — è il P2 già aperto dall'audit
  (import JSON e CSV), ed è la superficie principale in un'istanza pubblica:
  vedi la spec [`003-confine-importazione`](spec-driven/specs/003-confine-importazione/spec.md).
- **`unsafe_allow_html=True`** su `quote_type` ed `exchange`, presi grezzi dal
  JSON dei provider ([app.py:882-887](../app.py:882)). Non è XSS dimostrato
  (l'audit lo classifica come osservato, non come vulnerabilità), ma in
  un'istanza pubblica una risposta ostile da un provider raggiungerebbe ogni
  visitatore, non solo l'utente locale che l'ha cercata.
- **`i18n.locale_di_sistema()` lancia un subprocess** (`defaults read` su
  macOS) che legge il locale **del server** per scegliere la lingua **del
  visitatore** ([i18n.py:91-94](../comparatore/i18n.py:91)). Diventa
  irrilevante appena la lingua torna per-sessione (vedi sopra), ma va notato
  perché oggi è silenziosamente sbagliato in ogni deploy multiutente.
- **Nessun artefatto di deploy.** Verificata l'assenza di `Dockerfile`,
  `Procfile`, `requirements*.txt`, `fly.toml`, `render.yaml`, `vercel.json`,
  `app.yaml`. `.streamlit/config.toml` non ha sezione `[server]`: indirizzo,
  CORS, XSRF, `maxUploadSize` sono tutti ai valori predefiniti. Il
  `desktop/launcher.py` **non è candidabile** come entry point: si lega a
  `localhost` per costruzione ([launcher.py:71-87](../desktop/launcher.py:71))
  ed esiste solo per il bundle PyInstaller.
- **Scritture non atomiche** (già P3 nell'audit, aggravato dalla concorrenza):
  `keys.save()` scrive il file **e poi** applica `chmod 600`
  ([keys.py:61-72](../comparatore/keys.py:61)) — una finestra, per quanto
  breve, in cui una chiave in chiaro è leggibile a umask predefinito;
  `prefs.py` non applica `chmod` affatto; la cache scrive parquet e sidecar
  JSON in due passi non atomici
  ([cache.py:101-120](../comparatore/cache.py:101)).

**Un rischio che l'hosting introduce e non esiste oggi:** il modulo
`logging` non compare in nessun punto del codice — comodo per la privacy
locale, insufficiente per l'esercizio di un servizio pubblico. Ma EODHD e
Twelve Data ricevono la chiave come query parameter: aggiungere log di
accesso o di eccezioni HTTP, che l'hosting richiederebbe, rischia di
registrare **le chiavi dei visitatori** se non progettato per escludere le
query string fin dall'inizio.

## Requisiti, se si procede

**Bloccanti** (senza questi, l'istanza pubblica ha un difetto di correttezza
o di licenza, non solo di robustezza):

1. Chiavi API esclusivamente in sessione, **e** nessun fallback a
   `st.secrets`/variabili d'ambiente in modalità ospitata.
2. Preferenze per-sessione; opt-in justETF non attivabile globalmente.
3. Cache delle fonti a chiave partizionata per chiave (o disattivata) in
   modalità ospitata.
4. Validazione semantica dell'import (spec `003`, sotto).

**Di esercizio** (necessari perché il servizio regga il traffico pubblico,
non per correttezza):

5. Tetto di dimensione/conteggio sulla cache disco.
6. Rate limiting e timeout più stretti sulle chiamate esterne.
7. `maxUploadSize` ridotto e tetti espliciti nei parser CSV/JSON.
8. Config `[server]` Streamlit, immagine container, reverse proxy con TLS e
   XSRF attivo — nessuno di questi esiste oggi.

**Hardening** (miglioramenti già noti dall'audit come P3, non specifici
dell'hosting ma con impatto maggiore se pubblico): scritture atomiche, rimozione
di `unsafe_allow_html` dalla ricerca, logging che esclude le query string.

**Decisione legale, non tecnica:** cosa fare di Yahoo, justETF e OpenFIGI in
modalità ospitata. Questo documento raccomanda di spegnerle; è una scelta del
progetto, non un fatto che l'analisi possa decidere da sola.

## Forma architetturale raccomandata

Una **modalità ospitata**, attivata da una variabile d'ambiente
(`COMPARATORE_HOSTED` o simile), non un ramo di codice separato o un fork.
Motivazione: `comparatore/` non può importare Streamlit
([decisione 2](memory-bank/02-decisioni.md)), e la libreria **legge già**
l'ambiente per `COMPARATORE_CACHE_DIR`, `COMPARATORE_KEYS_FILE`,
`COMPARATORE_PREFS_FILE` e `COMPARATORE_RESTRICTED_CACHE_DAYS`
([keys.py:26](../comparatore/keys.py:26),
[prefs.py:21](../comparatore/prefs.py:21),
[cache.py:50](../comparatore/cache.py:50)). Estendere questa convenzione
esistente, invece di introdurne una nuova, è la via che tocca meno codice e
resta coerente con come il progetto già si configura per il bundle desktop
(`desktop/launcher.py:56-58`).

L'attuazione tecnica dei quattro requisiti bloccanti è la spec
[`004-istanza-multiutente`](spec-driven/specs/004-istanza-multiutente/spec.md).

## Scenari scartati in questa valutazione

Su richiesta, l'analisi si è concentrata sullo scenario BYO-key. Per
completezza, gli altri tre scenari discussi e non approfonditi:

- **Istanza privata per l'operatore** (dietro autenticazione, pochi utenti
  fidati): il modello di stato globale attuale resterebbe accettabile perché
  l'utente è sostanzialmente uno; richiederebbe solo autenticazione a monte
  (reverse proxy) e HTTPS. Nessun cambiamento allo stato applicativo.
- **Istanza pubblica con le chiavi dell'operatore**: da valutare soprattutto
  per il rischio legale (i piani EODHD personale e Twelve Data free vietano
  esplicitamente questo uso) e di costo/quota consumata da visitatori
  anonimi. Non richiede il lavoro di questo documento, ma è la scelta meno
  difendibile sul piano dei termini d'uso.
- **Demo pubblica solo offline** (CSV + import JSON + COVIP, che è CC BY 4.0,
  fonti a chiave disattivate): aggira quasi tutti i vincoli di licenza sui
  dati, ma richiede comunque i requisiti 4 e 5-8 sopra.

## Cosa non copre questa valutazione

Non è stata scelta un'infrastruttura di hosting specifica (PaaS, container,
VPS), né prodotto alcun artefatto di deploy: è materiale successivo a una
decisione di procedere. Non è stata stimata la capacità (quanti visitatori
concorrenti il modello a un thread per sessione di Streamlit regge in
pratica): richiede un carico di prova che questo documento non include. Non è
stata presa la decisione se ospitare l'app: questo documento la rende
informata, non la sostituisce.
