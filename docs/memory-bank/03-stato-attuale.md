# Stato attuale

*Aggiornato: 3 agosto 2026*

## Dove siamo

**v0.2**, pubblicata il 31 luglio 2026 con i due archivi macOS e Windows
allegati alla release. L'app è funzionalmente completa per il suo scopo: cerca
strumenti su più fonti, simula il portafoglio, evidenzia il costo del TER e
confronta con i fondi pensione COVIP.

## Entrato di recente

- **PAC** (versamenti periodici) come funzione avanzata opt-in, con metriche
  normalizzate, curva PIC di confronto e XIRR.
- **Gestione dei pesi**: rimozione fondi visibile, auto-bilanciamento
  proporzionale, colonna importo accanto alla percentuale.
- **Finestre COVIP leggibili**: il periodo nell'intestazione delle colonne, il
  pulsante che allinea il backtest alle finestre, e un numero al posto della
  riga di `n/d` quando il portafoglio non le copre.
- **Documentazione per agenti** (`AGENTS.md`, `CLAUDE.md`), questo memory bank e
  il processo spec-driven in `docs/spec-driven/`.
- **Fix dei preset di periodo** che andavano a capo a barra laterale stretta —
  prima spec eseguita con il nuovo processo
  ([`001`](../spec-driven/specs/001-preset-periodo-nowrap/spec.md)).
- **I quattro disallineamenti annotati qui sotto sono stati sciolti**: Pillow
  dichiarata, `--locked` ovunque, versione unificata, ruff in CI (decisioni 19
  e 20). Indagandoli, la versione si è rivelata non solo duplicata ma **rotta**:
  il pannello "Informazioni e licenze" mostrava sempre `-` perché il pacchetto
  non viene mai installato come distribuzione. Ora mostra `0.2.0`.
- **I tre P1 dell'[audit tecnico](../audit-codebase-2026-08-01.md) sono
  risolti** — spec
  [`002-integrita-backtest`](../spec-driven/specs/002-integrita-backtest/spec.md).
  Un fondo senza prezzi ora blocca il backtest con un'azione esplicita di
  rimozione invece di rinormalizzare i pesi in silenzio; il motore rifiuta
  quote zero, negative o non finite invece di trasformarle in rendimento nullo
  (`comparatore.engine.valida_prezzi`, `valida_holdings`); il simbolo resta la
  chiave interna delle colonne per tutto il calcolo, quindi due fondi con lo
  stesso nome non rompono più il PAC (`BacktestResult.labels` per la vista).
  Decisione 21.
- **Validazione ordine indice** — fix di una lacuna nella spec 002: l'audit
  richiede esplicitamente di "validare **indici monotoni**", che la spec non
  affrontò. Aggiunto `prices.sort_index()` all'inizio di `simulate()` per
  robustezza verso CSV caricati con date disordinate, e guardia in
  `valida_prezzi()` che solleva se l'indice non è ordinato (per catturare
  anomalie). Test aggiunti in `ValidaPrezziTests`.
- **Valutazione hosting** — [documento del 3 agosto](../valutazione-hosting-2026-08-03.md)
  sull'impatto di ospitare l'app su un sito web (scenario valutato: istanza
  pubblica con chiavi dell'utente). Conclusione: BYO-key non basta da sola,
  perché copre solo le fonti a chiave (EODHD, Twelve Data) e non quelle senza
  (Yahoo, justETF, OpenFIGI), interrogate dal server a nome di visitatori
  anonimi. Ha aperto due spec, entrambe ancora in bozza, non implementate:
  [`003-confine-importazione`](../spec-driven/specs/003-confine-importazione/spec.md)
  (valida semanticamente import JSON e CSV — il P2 dell'audit, prerequisito
  anche per l'hosting) e
  [`004-istanza-multiutente`](../spec-driven/specs/004-istanza-multiutente/spec.md)
  (modalità ospitata dietro `COMPARATORE_HOSTED`: chiavi/preferenze
  per-sessione, cache partizionata per chiave, justETF disattivato).
- **GitHub Action pinnate a SHA, permessi per-job** — chiude il secondo P2
  dell'audit. Le 5 action distinte nei tre workflow ora referenziano un
  commit SHA (`# vX.Y.Z` in commento), non più un tag mobile;
  `desktop-build.yml` non ha più `contents: write` a livello di workflow, solo
  il job `release` lo dichiara. Decisione 22.
- **P3 chiusi**: `keys.save()`/`prefs.save()`/`cache.write()`/`write_meta()`
  passano tutti da un file temporaneo nella stessa cartella e `os.replace`
  (atomico) invece di scrivere e basta — per le chiavi, `chmod 600` avviene
  ora *prima* che il file compaia al percorso finale, chiudendo la finestra in
  cui erano leggibili a permessi di default. Le tre celle `unsafe_allow_html`
  nella ricerca (metadati grezzi dei provider) sono diventate `st.caption()`.
- **Copertura test delle fonti esterne**: prima non esisteva alcun mock nella
  suite. Aggiunto `tests/fixtures.py` (una `FakeResponse` minima per
  `unittest.mock.patch("requests.get"/"post", ...)`) più test per
  `yahoo.py`, `twelvedata.py`, `fx.py` (sia il percorso BCE via `requests` sia
  il ripiego Yahoo via `yfinance`), `openfigi.py`, `justetf.py`, il confine di
  rete di `covip.py`, e i percorsi HTTP di `eodhd.py` che mancavano. Il
  parsing dei fogli COVIP (`_parse_rendimenti`/`_parse_isc`) resta fuori:
  dipende da un layout di celle unite che servirebbe una fixture più grande
  per imitare fedelmente, non è dove l'audit segnalava copertura zero. 235
  test totali, tutti verdi.

## Aperto, e noto

| Cosa | Dettaglio |
|---|---|
| **App non firmate** | Gatekeeper e SmartScreen avvisano. Decisione 17: costa 99 $/anno + 70-250 $/anno, rimandata |
| **macOS solo arm64** | La build CI gira su `macos-latest`; per Intel/universal va adattato il workflow |
| **Import senza validazione semantica** | P2 dell'audit, non ancora implementato: spec [`003-confine-importazione`](../spec-driven/specs/003-confine-importazione/spec.md) scritta, in bozza |
| **Hosting su un sito web** | Valutato ma non deciso: vedi [valutazione hosting](../valutazione-hosting-2026-08-03.md) e spec [`004-istanza-multiutente`](../spec-driven/specs/004-istanza-multiutente/spec.md) (in bozza). Resta aperta anche la decisione se disattivare Yahoo/OpenFIGI in modalità ospitata, non solo justETF |

## Da sapere per lavorarci

- **Le fonti dati richiedono rete.** Yahoo, COVIP, Frankfurter e le altre sono
  spesso irraggiungibili da ambienti sandboxed. Per provare l'app end-to-end
  offline: carica una serie da CSV (barra laterale) e importa un portafoglio
  JSON. Si arriva fino al backtest completo, grafici inclusi — è così che sono
  stati fatti gli screenshot del README.
- **Gli screenshot della scheda "Fondi pensione" non esistono** proprio per
  questo: il catalogo COVIP non era raggiungibile e non è materiale che si possa
  inventare. Vanno catturati da un ambiente con rete verso `covip.it`.

## Prossimi passi possibili

Nessuno è deciso — sono le direzioni che il lavoro fatto finora lascia aperte:

1. Implementare le spec [`003-confine-importazione`](../spec-driven/specs/003-confine-importazione/spec.md)
   e [`004-istanza-multiutente`](../spec-driven/specs/004-istanza-multiutente/spec.md)
   (in quest'ordine: la seconda si appoggia alla prima per l'input ostile).
   Entrambe sono ferme allo stadio di spec+piano+attività, nessun codice
   scritto: la decisione se e quando implementarle non è stata presa qui.
2. Decidere se e come ospitare l'app su un sito web — la
   [valutazione](../valutazione-hosting-2026-08-03.md) mappa i requisiti, non
   sceglie lo scenario. Se si procede, resta anche da produrre gli artefatti
   di deploy veri e propri (config `[server]` di Streamlit, container, reverse
   proxy): dichiarati fuori ambito dalla valutazione stessa.
3. Completare gli screenshot del README con la scheda dei fondi pensione.
4. Valutare la firma del codice se l'app esce dalla cerchia di utenti fidati.
5. Se il progetto dovesse mai distribuirsi anche via PyPI, rivedere la
   decisione 20 (aggiungere un `[build-system]`, che oggi manca di proposito).
