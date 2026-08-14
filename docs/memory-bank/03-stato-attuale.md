# Stato attuale

*Aggiornato: 14 agosto 2026*

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
  anomalie). Test aggiunti in `ValidaPrezziTests` (164 test totali, tutti verdi).
- **TER, import Directa e costi PIC** — spec
  [`003-ter-directa-costi-pic`](../spec-driven/specs/003-ter-directa-costi-pic/spec.md):
  il recupero dei metadati conserva tentativi e provenienza, ha retry esplicito
  e corregge il mapping Yahoo → EODHD; con opt-in justETF può usare anche il
  TER dalla pagina profilo dell'ETF come fonte preferita con opt-in, senza
  sovrascrivere un TER manuale; CSV/XLSX Directa si importano con
  mappatura guidata. Il parser riconosce anche intestazioni dopo righe
  descrittive, preseleziona gli alias con accenti e distingue gli export
  "Movimenti" dagli export di posizioni: lo storico non viene interpretato
  come controvalore attuale. Le posizioni Directa riconoscono anche i totali di
  coda come righe da escludere esplicitamente. Per gli ETF, con justETF abilitato,
  vengono conservate politica di distribuzione e metodo di replica, visibili
  nell'editor; i vecchi JSON ricevono n/d. Il PIC espone un prospetto separato
  per carico e scarico senza alterare il backtest. I test sono 188; il mapping
  delle piazze MI distingue una quotazione EODHD identica e gli importi delle
  commissioni mostrano i centesimi.
- **Benchmark, correlazioni e rolling** — spec
  [`004-benchmark-correlazioni-rolling`](../spec-driven/specs/004-benchmark-correlazioni-rolling/spec.md):
  il benchmark e' opzionale, resta fuori dagli holdings e viene risolto con una
  diagnostica propria; il confronto usa il periodo comune senza estendere lo
  storico. Sono disponibili metriche attive, correlazioni mensili e rolling a
  1/3/5/10 anni, con compatibilita' dei JSON precedenti.
- **Rendimento reale HICP** — spec
  [`005-rendimento-reale-inflazione`](../spec-driven/specs/005-rendimento-reale-inflazione/spec.md):
  Eurostat fornisce l'indice mensile per Italia o area euro; la cache conserva
  metadati e degrada ai dati vecchi coperti se la rete fallisce. La curva reale
  e' derivata e il PAC deflaziona saldo e flussi rata per rata senza alterare il
  backtest nominale. I test sono 209.
- **Sovrapposizione delle partecipazioni** — spec
  [`006-overlap-portafoglio`](../spec-driven/specs/006-overlap-portafoglio/spec.md):
  le holdings vengono normalizzate con identita' deterministiche, la copertura
  resta esplicita e l'overlap e' sempre un limite inferiore senza
  rinormalizzazione. La scheda Bilanciamento mostra matrice, coppie,
  concentrazione aggregata e quota sconosciuta; i JSON precedenti ricevono i
  nuovi metadati con backfill. I test sono 215.
- **Profilo locale e diagnosi anonima** — spec
  [`008-profilo-diagnosi-anonima`](../spec-driven/specs/008-profilo-diagnosi-anonima/spec.md):
  il profilo facoltativo vive separato dal portafoglio, le regole producono
  rilievi deterministici solo rispetto alle preferenze dichiarate e il payload
  di anteprima nasce da una allowlist con token temporanei. La tab Diagnosi non
  effettua chiamate esterne; i test complessivi sono 224.
- **Scheda informativa dello strumento** — spec
  [`010-scheda-strumento`](../spec-driven/specs/010-scheda-strumento/spec.md):
  i fatti normalizzati conservano valore, fonte, date, qualità, alternative
  discordanti e quotazioni collegate senza cambiare la quotazione attiva. La
  scheda unica è raggiungibile da ricerca e portafoglio, include retry dei soli
  fatti automatici e un editor KID con override protetto; l'export persiste solo
  dati utili e rimuove `ter_attempts`. Yahoo, EODHD e justETF riusano le
  richieste già previste, con justETF ancora opt-in. La copertura storica deriva
  dalle serie già risolte dal flusso del portafoglio. I test complessivi sono
  237 e Ruff è pulito.

## Aperto, e noto

| Cosa | Dettaglio |
|---|---|
| **App non firmate** | Gatekeeper e SmartScreen avvisano. Decisione 17: costa 99 $/anno + 70-250 $/anno, rimandata |
| **macOS solo arm64** | La build CI gira su `macos-latest`; per Intel/universal va adattato il workflow |
| **Import JSON e CI** | L'[audit tecnico](../audit-codebase-2026-08-01.md) ha confermato validazione semantica insufficiente nell'import JSON (P2, non ancora affrontato) e action GitHub fissate a tag mutabili invece che a SHA (P2, non ancora affrontato). L'import Directa ha invece validazione propria e mappatura guidata. |

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

1. Eseguire la roadmap P2 dell'[audit tecnico](../audit-codebase-2026-08-01.md):
   validazione semantica dell'import JSON e pin SHA delle GitHub Action.
2. Completare gli screenshot del README con la scheda dei fondi pensione.
3. Valutare la firma del codice se l'app esce dalla cerchia di utenti fidati.
4. Se il progetto dovesse mai distribuirsi anche via PyPI, rivedere la
   decisione 20 (aggiungere un `[build-system]`, che oggi manca di proposito).
