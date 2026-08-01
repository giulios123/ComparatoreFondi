# Stato attuale

*Aggiornato: agosto 2026*

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

## Aperto, e noto

| Cosa | Dettaglio |
|---|---|
| **App non firmate** | Gatekeeper e SmartScreen avvisano. Decisione 17: costa 99 $/anno + 70-250 $/anno, rimandata |
| **macOS solo arm64** | La build CI gira su `macos-latest`; per Intel/universal va adattato il workflow |

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

1. Completare gli screenshot del README con la scheda dei fondi pensione.
2. Valutare la firma del codice se l'app esce dalla cerchia di utenti fidati.
3. Se il progetto dovesse mai distribuirsi anche via PyPI, rivedere la
   decisione 20 (aggiungere un `[build-system]`, che oggi manca di proposito).
