# AGENTS.md

Istruzioni per chiunque — persona o agente — lavori su questo repository.
È la fonte unica: `CLAUDE.md` la referenzia invece di duplicarla.

## Cos'è

Backtester per fondi ed ETF con l'impatto del TER in evidenza, più il confronto
con i fondi pensione italiani (dati COVIP). Applicazione **Streamlit** in
Python 3.13, gestita con **`uv`**, in italiano/inglese/francese/tedesco.

Tre confini, e sono la cosa più importante da sapere prima di scrivere codice:

| Cosa | Dove | Regola |
|---|---|---|
| Libreria | `comparatore/` | **Non importa mai Streamlit.** Deve restare usabile da uno script normale |
| Interfaccia | `app.py` (unico file, ~2200 righe) | Streamlit lo **esegue come script**, non lo importa mai |
| Bundle desktop | `desktop/launcher.py` | Entry point del solo eseguibile PyInstaller, non dell'uso da sorgente |

## Comandi

```bash
uv sync                            # dipendenze di runtime
uv sync --group dev                # + PyInstaller e pip-licenses

uv run streamlit run app.py        # avvia l'app su http://localhost:8501
uv run python -m unittest discover -s tests -p "test_*.py"   # test

uv run pyinstaller desktop/comparatore.spec --noconfirm --clean   # bundle
uv run python scripts/generate_third_party_notices.py --check     # audit licenze
```

I test sono **`unittest` della standard library, non pytest**: pytest non è fra
le dipendenze e `uv run pytest` non funziona.

## Regole non negoziabili

- **Niente stringhe a video fuori da `t()`.** Ogni testo passa da
  `t("chiave")`, e una chiave nuova va aggiunta a **tutti e quattro** i
  cataloghi in `comparatore/locales/` (`it.py`, `en.py`, `fr.py`, `de.py`).
  `it.py` è il riferimento; `tests/test_i18n.py` fallisce se uno resta indietro.
- **`comparatore/` non importa `streamlit`.** Chi lo fa rompe l'uso da script
  documentato nel README (§ Struttura del progetto) e rende la libreria non
  testabile senza un server.
- **Mai committare chiavi API.** `.streamlit/api_keys.json`, `prefs.json` e
  `secrets.toml` sono in `.gitignore` e devono restarci.
- **`THIRD_PARTY_NOTICES.txt` e `THIRD_PARTY_LICENSES.json` sono generati**, non
  si modificano a mano: `desktop/comparatore.spec` li rigenera a ogni build e la
  CI verifica l'allowlist su Linux, macOS e Windows.
- **La versione è duplicata**: `pyproject.toml` (`version`) e
  `desktop/comparatore.spec` (`CFBundleShortVersionString`). Vanno cambiate
  insieme.
- **Il tag di release ha tre componenti.** Il workflow si attiva su `v*.*.*`:
  `v0.3.0` sì, `v0.2` no (quella release ha richiesto una run manuale).
- **CSS custom solo se non c'è alternativa**, e sempre agganciato a una classe
  `st-key-…` di un `st.container(key=…)`, mai a un selettore globale. Oggi ce
  n'è **uno solo**, in cima ad `app.py`, per i pulsanti dei periodi rapidi.

## Stile

Commenti e docstring **in italiano**, e spiegano il *perché*, non il *cosa*: è
la cifra di questo codice e va mantenuta. Due esempi da leggere prima di
scrivere il proprio: l'intestazione di `comparatore/covip.py` (perché certe
metriche non sono calcolabili per i fondi pensione) e `allinea_periodo_covip()`
in `app.py` (perché esiste quel pulsante).

Nei commenti e nelle docstring si usa in prevalenza l'apostrofo ASCII (`piu'`,
`perche'`, `cosi'`); le stringhe dei cataloghi di traduzione usano invece gli
accenti veri (`più`, `perché`), perché finiscono a video.

## Test

`app.py` non è importabile, quindi non è testabile in modo diretto: è coperto
da guardie che ne ispezionano il **sorgente** in `tests/test_app_sintassi.py`
(che compili, che l'export preceda il backtest, che il fix dei preset non
sparisca). Chi cambia `app.py` in modo strutturale aggiunge lì la propria
guardia — è l'unico posto dove una regressione può essere intercettata.

Il resto della libreria si testa normalmente, un file per modulo.

## Prima di scrivere codice

- `docs/memory-bank/` — il **perché** delle scelte fatte finora. Da leggere
  prima di rimettere in discussione un vincolo: quasi sempre la risposta c'è già.
  Il file che cambia più spesso, e da cui partire, è `03-stato-attuale.md`.
- `docs/spec-driven/` — il processo. **Feature nuova o cambio di comportamento
  visibile ⇒ prima una spec**, poi il piano, poi il codice. Refusi, refactor a
  parità di comportamento e aggiornamenti di dipendenze non ne hanno bisogno.

## Dati esterni

L'app legge da Yahoo Finance, EODHD, Twelve Data, justETF, OpenFIGI, COVIP e
Frankfurter (cambi BCE). In un ambiente senza rete verso questi domini restano
utilizzabili il caricamento di serie da CSV e l'import di un portafoglio JSON:
è la via per provare l'interfaccia end-to-end offline.

Il codice è Apache-2.0, **i dati no**: justETF è opt-in esplicito dell'utente
proprio per questo. Vedi README § "Licenza del codice e termini dei dati".
