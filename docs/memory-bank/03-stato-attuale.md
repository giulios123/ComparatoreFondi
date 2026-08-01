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

## Aperto, e noto

| Cosa | Dettaglio |
|---|---|
| **App non firmate** | Gatekeeper e SmartScreen avvisano. Decisione 17: costa 99 $/anno + 70-250 $/anno, rimandata |
| **macOS solo arm64** | La build CI gira su `macos-latest`; per Intel/universal va adattato il workflow |
| **Pillow non dichiarata** | `scripts/generate_icons.py` importa `PIL`, che non è in `pyproject.toml` (né runtime né dev). Lo script è macOS-only e usa e getta, quindi finora non è emerso |
| **`--locked` disallineato** | `desktop-build.yml` usa `uv sync --group dev --locked` nel job macOS ma `uv sync --group dev` in quello Windows: le due build possono partire da lockfile diversi |
| **Versione duplicata** | `pyproject.toml` e `desktop/comparatore.spec` vanno aggiornati insieme a mano |
| **Nessun linter** | Non c'è ruff, black o mypy configurato: lo stile è tenuto a mano |

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
2. Sciogliere i due disallineamenti della CI (Pillow, `--locked` su Windows).
3. Unificare la versione in un punto solo.
4. Valutare la firma del codice se l'app esce dalla cerchia di utenti fidati.
