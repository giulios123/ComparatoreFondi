# 📈 Comparatore Fondi

Backtester per fondi comuni ed ETF su dati Yahoo Finance: cerca gli strumenti,
definisci i pesi del portafoglio, scegli il periodo e vedi quanto sarebbe
diventato il tuo capitale — con l'impatto dei costi (TER) evidenziato.

## Avvio

```bash
uv run streamlit run app.py
```

Si apre su <http://localhost:8501>.

## Cosa fa

- **Ricerca** su Yahoo Finance per nome, ticker o **ISIN** (es. `IE00B3XXRP09`).
- **Backtest** da data X a data Y con pesi percentuali e capitale iniziale.
- **Ribilanciamento** opzionale: nessuno (buy & hold), mensile, trimestrale, annuale.
- **Confronto**: curva del portafoglio + curva di ogni fondo preso singolarmente
  a parità di capitale.
- **Conversione valutaria** ai cambi giornalieri, così puoi mischiare fondi in
  EUR, USD, GBP… senza falsare il risultato.
- **Metriche**: rendimento totale, CAGR, volatilità, Sharpe, Sortino, max
  drawdown, Calmar, miglior/peggior anno, rendimenti per anno solare.
- **Export CSV** di tutte le serie.

## Come vengono trattati i costi

Questo è il punto delicato, e vale la pena leggerlo.

**I NAV pubblicati da Yahoo sono già al netto del TER.** La commissione di
gestione viene addebitata giorno per giorno dentro il NAV: se un fondo dichiara
+10% di rendimento, quel +10% è già al netto delle spese correnti. Sottrarre di
nuovo il TER dalla performance storica significa contarlo due volte.

L'app quindi lavora con due curve:

| Curva | Significato |
|---|---|
| **Netta** | La serie così com'è pubblicata: quello che l'investitore ha realmente ottenuto. |
| **Lorda** | Il TER ri-aggiunto sopra, cioè il fondo ipotetico senza commissioni. |

**La distanza fra le due curve è esattamente il costo del TER**, ed è quello che
il riquadro "Impatto del TER" quantifica in euro e in percentuale.

C'è poi la colonna **Costi extra %** per i costi che il NAV *non* contiene già —
commissioni di custodia, consulenza, oppure il TER di una classe diversa da
quella quotata. Questi vengono sottratti dalla performance.

La formula applicata è la capitalizzazione della commissione nel tempo:

```
fattore(t) = (1 - tasso_annuo) ^ (giorni_trascorsi / 365.25)
```

Il TER precompilato arriva da Yahoo quando disponibile, ma **la copertura sui
fondi europei è scarsa e i valori sono arrotondati** (VUSA riporta `0.00` invece
di `0.07`). Verifica sempre il TER sul KID del fondo e correggilo a mano: il
campo è editabile.

## Struttura

```
app.py                  interfaccia Streamlit
comparatore/
  data.py               ricerca Yahoo, prezzi, valute, TER
  engine.py             logica commissioni, simulazione, ribilanciamento
  metrics.py            metriche di performance
```

I moduli in `comparatore/` non importano Streamlit e sono usabili da script.

## Note e limiti

- Prezzi **total return** (`auto_adjust=True`): i dividendi sono reinvestiti,
  quindi fondi ad accumulazione e a distribuzione sono confrontabili.
- Il backtest parte dalla prima data in cui **tutti** i fondi hanno dati; se un
  fondo è più giovane del periodo richiesto l'app lo segnala.
- I NAV mancanti vengono riportati in avanti (`ffill`), come è corretto per i
  fondi che non quotano tutti i giorni.
- **Non** sono considerati: costi di ingresso/uscita, spread denaro-lettera,
  fiscalità, versamenti periodici (PAC).
- Un fondo la cui valuta non è risolvibile viene **escluso** anziché mescolato
  a valute diverse.

Le performance passate non sono indicative di quelle future. Questo strumento è
di analisi, non una consulenza finanziaria.
