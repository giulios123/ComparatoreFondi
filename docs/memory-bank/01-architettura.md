# Architettura

## La separazione che regge tutto

```
comparatore/     libreria pura        — non importa mai Streamlit
app.py           interfaccia          — Streamlit lo esegue come script
desktop/         confezionamento      — entry point del solo bundle PyInstaller
```

Non è una convenzione estetica. La libreria resta usabile da uno script normale
(il README lo documenta con un esempio) e — soprattutto — resta testabile senza
un server. Il prezzo lo paga `app.py`, che non essendo importabile va coperto da
guardie sul sorgente (vedi § Test).

## Flusso di una richiesta

```
      ricerca / ISIN
            │
            ▼
   sources/registry.py ─── prova le fonti in ordine e registra ogni tentativo
            │                 1. CSV caricato  (indicazione esplicita: vince su tutto)
            │                 2. Yahoo         (generalista, sempre disponibile)
            │                 3. EODHD         (solo con chiave)
            │                 4. Twelve Data   (solo con chiave)
            │                 ·  justETF       (solo con opt-in dell'utente)
            ▼
        cache.py ─────────── parquet accumulativo per (fonte, simbolo, valuta)
            │                + sidecar JSON con l'intervallo *richiesto*
            ▼
          fx.py ──────────── cambi BCE via Frankfurter, con ripiego su Yahoo
            │
            ▼
        engine.py ────────── tre serie esplicite: net / gross / extra
            │                (il NAV pubblicato è già al netto del TER:
            │                 sottrarlo di nuovo sarebbe doppio conteggio)
            ▼
       metrics.py ────────── CAGR, volatilità, Sharpe, Sortino, Calmar, drawdown
```

Il registry non si limita a restituire una serie: tiene traccia di **cosa ha
tentato e com'è andata** (`Attempt`), perché una serie mancante deve produrre
una spiegazione a video, non un grafico vuoto.

La cache è **accumulativa**: ogni file contiene tutto lo storico mai scaricato
per quella tripla, non la singola finestra richiesta. Chiedere periodi lunghi
diventa progressivamente più economico — che è il caso d'uso tipico dell'app.

## I moduli

| Modulo | Ruolo |
|---|---|
| `sources/` | Una classe per fonte (`yahoo`, `eodhd`, `twelvedata`, `justetf`, `csv_source`, `openfigi`) più il `registry` che le ordina |
| `engine.py` | Simulazione del portafoglio, ribilanciamento, costi, PAC |
| `metrics.py` | Metriche di rischio e rendimento |
| `cache.py` | Cache su disco in parquet, con TTL e sidecar |
| `fx.py` | Conversione valutaria |
| `covip.py` | Catalogo, rendimenti e ISC dei fondi pensione italiani |
| `horizons.py` | Rendimenti del portafoglio sulle finestre COVIP, per renderlo confrontabile |
| `allocazione.py` | Classificazione per asset class, area, settore; stima del paese dalle prime posizioni |
| `pesi.py` | Ridistribuzione proporzionale dei pesi, invariante "somma 100%" |
| `proxies.py` | Storico esteso tramite strumenti proxy |
| `portfolio_io.py` | Export/import del portafoglio in JSON versionato |
| `keys.py` / `prefs.py` | Chiavi API e preferenze utente, ciascuna nel proprio file |
| `i18n.py` + `locales/` | Traduzioni; `it.py` è il catalogo di riferimento |
| `licenses.py` | Legge `LICENSE` e `THIRD_PARTY_NOTICES.txt` per mostrarli nell'app |

## Interfaccia

`app.py` è un unico file. Struttura: configurazione e stato di sessione →
barra laterale (parametri, PAC, chiavi, CSV, portafoglio, licenze) → ricerca →
composizione del portafoglio → backtest → sei schede di risultati (Portafoglio,
Bilanciamento, Confronto fondi, Drawdown, Dati, Fondi pensione).

Un solo blocco di CSS custom, in cima al file, agganciato alla classe
`st-key-preset_periodo` di un `st.container(key=…)` — vedi decisione 18.

## Confezionamento

`desktop/comparatore.spec` produce un bundle PyInstaller *onedir*. Due
particolarità:

- L'`Analysis` elenca **due** script (`launcher.py` e `app.py`). Il secondo
  serve solo a far seguire all'analisi statica i suoi import: Streamlit legge
  `app.py` come testo a runtime, quindi sarebbe altrimenti invisibile.
- Lo spec **rigenera** `THIRD_PARTY_NOTICES.txt` e `THIRD_PARTY_LICENSES.json`
  a ogni build, per la piattaforma su cui gira.

`launcher.py` sposta cache, chiavi e preferenze nella cartella dati utente del
sistema operativo: dentro un bundle installato la cartella del codice è di sola
lettura. Usa la porta **8765**, non la 8501 dell'uso da sorgente.

## CI

| Workflow | Quando | Cosa fa |
|---|---|---|
| `tests.yml` | push su `main`, ogni PR | `unittest` su Ubuntu |
| `license-audit.yml` | push su `main`, ogni PR, manuale | Audit licenze su Linux + macOS + Windows |
| `desktop-build.yml` | tag `v*.*.*`, manuale | Bundle macOS (arm64) e Windows, allegati a una release |

## Test

`unittest` della standard library, un file per modulo, più
`tests/test_app_sintassi.py` che ispeziona il **sorgente** di `app.py` — perché
non essendo importabile è l'unico modo di proteggerlo. Oggi verifica che
compili, che l'export del portafoglio preceda il backtest, che preferenze e
chiavi restino collegate, e che il fix dei preset di periodo non sparisca.
