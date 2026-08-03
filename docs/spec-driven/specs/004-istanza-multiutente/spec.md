# 004 · Istanza multiutente

*Stato: bozza — 3 agosto 2026*

## Problema

La [valutazione hosting del 3 agosto 2026](../../../valutazione-hosting-2026-08-03.md)
ha confermato che l'app, così com'è, presuppone un utente solo su una
macchina sola: tre store — chiavi API, preferenze, cache — sono file di
**processo**, non per visitatore, e l'unico stato realmente per-sessione è
`st.session_state`. Con più visitatori concorrenti (lo scenario valutato:
istanza pubblica dove ogni visitatore inserisce le proprie chiavi EODHD e
Twelve Data) questo produce, verificato nel codice:

1. Un visitatore B che si collega dopo A eredita la chiave di A
   (`st.session_state.api_keys` è inizializzato da un file unico), ne vede le
   ultime quattro cifre, ne consuma la quota, e può cancellarla per tutti.
2. La lingua e l'opt-in justETF sono preferenze **globali**: chi le cambia le
   cambia per ogni visitatore successivo. Per justETF questo è aggravato dal
   fatto che è un consenso esplicito — il README lo descrive come "ricordato
   su questo computer", un'assunzione che smette di valere su un server.
3. La cache dei dati EODHD/Twelve Data non distingue quale chiave ha
   prodotto quale dato: nei piani di questi due provider, dati scaricati con
   la chiave di A non devono essere serviti a B — è il "display a terzi" che
   quei piani vietano esplicitamente. Un flag di cache (`eodhd-fundamentals-blocked`)
   è condiviso: un 403 sul piano free di un visitatore disabilita i
   fondamentali per tutti per un giorno.
4. Nessun tetto sulla dimensione della cache, nessun limite di caricamento
   più stretto del default Streamlit di 200 MB.

Nessun tentativo precedente: l'app non è mai stata pensata per più utenti
concorrenti, quindi questo comportamento non è una regressione, è
un'assunzione di progetto (decisione 1) che uno scenario nuovo rende
insufficiente.

## Chi lo incontra

Chiunque ospiti l'app su un sito raggiungibile da più visitatori nello stesso
momento — lo scenario che questa spec abilita, non uno che esiste già.
Nessun utente locale (desktop, uso da sorgente) è toccato: per un processo con
un solo visitatore reale, il comportamento di oggi resta quello di sempre.

## Criteri di accettazione

Con la modalità ospitata attiva (variabile d'ambiente):

1. Due sessioni browser distinte non vedono, in nessuna forma (nemmeno
   mascherata), le chiavi API inserite l'una dall'altra.
2. Nessun file viene scritto in `.streamlit/` durante l'uso dell'app (chiavi
   e preferenze restano solo in `st.session_state`).
3. La lingua scelta in una sessione non influenza la lingua iniziale di
   un'altra sessione aperta successivamente; il rilevamento automatico
   (locale del browser → intestazione `Accept-Language` → italiano) torna a
   funzionare per ogni nuova sessione, invece di restare scavalcato da una
   preferenza salvata in precedenza da qualcun altro.
4. Il checkbox di attivazione justETF non è disponibile: nessuna richiesta
   verso il suo endpoint può partire dal server per conto di un visitatore
   anonimo.
5. Due sessioni che usano chiavi EODHD o Twelve Data diverse non condividono
   le voci di cache costruite con quelle chiavi, incluso il flag
   `eodhd-fundamentals-blocked`.
6. La cartella cache non supera una soglia di dimensione configurabile: una
   volta raggiunta, le voci più vecchie vengono eliminate prima di scriverne
   di nuove.
7. Il pulsante che svuota l'intera cache non è disponibile (in modalità
   ospitata nessuna azione di un singolo visitatore cancella dati di altri).
8. Il limite di caricamento file è più stretto del default Streamlit di 200 MB.
9. Con la modalità ospitata **non** attiva, ogni comportamento resta
   identico a oggi: stesso file di chiavi condiviso, stesse preferenze
   globali, stessa cache non partizionata — nessuna regressione per l'uso
   locale/desktop.

## Non-obiettivi

- Rate limiting, timeout più stretti, retry/backoff sulle chiamate esterne:
  la valutazione hosting li elenca come necessari all'esercizio del
  servizio, ma restano fuori da questa spec — sono infrastruttura di
  esercizio, non correttezza multiutente.
- Config `[server]` di Streamlit (CORS, XSRF, indirizzo), immagine
  container, reverse proxy, TLS: sono artefatti di deploy, non
  comportamento dell'applicazione. La valutazione hosting li elenca; questa
  spec non li produce.
- Disattivare Yahoo od OpenFIGI (le altre due fonti senza chiave utente):
  la valutazione hosting raccomanda di valutarlo, ma è una decisione
  esplicitamente lasciata aperta lì, non presa qui. Questa spec disattiva
  solo justETF, che ha già un meccanismo di opt-in esplicito da cui
  agganciarsi.
- Autenticazione dei visitatori, quote per IP, protezione anti-bot: fuori
  ambito, non richiesti dallo scenario valutato (istanza pubblica aperta).
- Scritture atomiche di cache/chiavi/preferenze: è il finding P3
  dell'audit, indipendente dalla modalità ospitata, pianificato a parte.

## Vincoli

- `comparatore/` non deve importare Streamlit: la modalità ospitata è
  letta dalla libreria tramite variabile d'ambiente, con la stessa
  convenzione già in uso per `COMPARATORE_CACHE_DIR`, `COMPARATORE_KEYS_FILE`,
  `COMPARATORE_PREFS_FILE`, `COMPARATORE_RESTRICTED_CACHE_DAYS`.
- Nessuna chiave API, nemmeno mascherata o come hash, deve finire in un
  percorso di file o in un log.
- Ogni stringa mostrata a video passa da `t()`, con le quattro traduzioni
  allineate.
- Un cambiamento strutturale di `app.py` è accompagnato dalla sua guardia in
  `tests/test_app_sintassi.py`.
- Il comportamento per l'uso locale/desktop (modalità ospitata assente) non
  cambia: questa spec aggiunge un ramo di comportamento, non ne sostituisce
  uno esistente.

## Domande aperte

Nessuna bloccante per l'implementazione. Resta esplicitamente aperta, e
tracciata nella valutazione hosting piuttosto che qui, la decisione se
disattivare anche Yahoo e OpenFIGI in modalità ospitata: questa spec non la
presuppone né la preclude.
