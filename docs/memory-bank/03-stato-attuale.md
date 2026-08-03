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
  anomalie). Test aggiunti in `ValidaPrezziTests` (164 test totali, tutti verdi).

## Aperto, e noto

| Cosa | Dettaglio |
|---|---|
| **App non firmate** | Gatekeeper e SmartScreen avvisano. Decisione 17: costa 99 $/anno + 70-250 $/anno, rimandata |
| **macOS solo arm64** | La build CI gira su `macos-latest`; per Intel/universal va adattato il workflow |
| **Import e CI** | L'[audit tecnico](../audit-codebase-2026-08-01.md) ha confermato validazione semantica insufficiente nell'import JSON (P2, non ancora affrontato) e action GitHub fissate a tag mutabili invece che a SHA (P2, non ancora affrontato). |

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
