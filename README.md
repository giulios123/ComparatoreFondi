# 📈 Comparatore Fondi

Backtester per fondi comuni ed ETF: cerca gli strumenti, definisci i pesi del
portafoglio, scegli il periodo e vedi quanto sarebbe diventato il tuo capitale —
con l'impatto dei costi (TER) evidenziato.

## Avvio

```bash
uv run streamlit run app.py
```

Si apre su <http://localhost:8501>.

## Cosa fa

- **Ricerca** per nome, ticker o **ISIN** (es. `IE00B3XXRP09`).
- **Backtest** da data X a data Y con pesi percentuali e capitale iniziale,
  con pulsanti rapidi di periodo (1a / 5a / 10a / 20a / Max).
- **Ribilanciamento** opzionale: nessuno (buy & hold), mensile, trimestrale, annuale.
- **Confronto**: curva del portafoglio + curva di ogni fondo preso singolarmente
  a parità di capitale.
- **Più fonti dati** con ripiego automatico, e possibilità di forzare la fonte
  per singolo fondo.
- **Conversione valutaria** ai cambi ufficiali BCE.
- **Storico esteso**: ricostruzione del periodo precedente alla nascita del fondo.
- **Rimozione di un fondo** dalla tabella, con l'icona del cestino sulla riga.
- **Metriche**: rendimento totale, CAGR, volatilità, Sharpe, Sortino, max
  drawdown, Calmar, miglior/peggior anno, rendimenti per anno solare.
- **Export CSV** di tutte le serie.

## Fonti dati

Nessuna fonte, da sola, copre tutti i casi. L'app le prova in ordine e si ferma
alla prima che risponde, dicendo sempre quale ha usato.

| Ordine | Fonte | Copre | Chiave |
|---|---|---|---|
| 1 | **CSV caricato** | qualsiasi cosa, incluso ciò che nessuno espone | — |
| 2 | **justETF** | ETF europei, per ISIN | — |
| 3 | **Yahoo Finance** | fonte generalista, unica con ricerca testuale | — |
| 4 | **EODHD** | fondi comuni ed ETF europei, TER affidabile | sì |
| 5 | **Twelve Data** | 50+ mercati | sì |

Quando una serie non arriva, l'app mostra cosa ha tentato e come è andata, invece
di lasciare un grafico vuoto senza spiegazione.

**justETF** è la fonte che chiude il buco più fastidioso: interrogata per ISIN
restituisce la serie total-return già convertita nella valuta richiesta, dalla
quotazione dell'ETF. Esempio concreto: l'iShares Core S&P 500 (`IE00B5BMR087`)
su Yahoo con il ticker di Milano non esiste, mentre justETF ne dà lo storico dal
2010. È però un'**API interna non documentata**: può cambiare senza preavviso,
per questo non è mai l'unica fonte di un fondo.

**Morningstar** e **Stooq** sono stati valutati e scartati: il primo ora richiede
un browser Chrome pilotato via Selenium, il secondo è dietro un controllo
anti-bot in JavaScript. Nessuno dei due è utilizzabile da un'app Streamlit.

### Chiavi API

Facoltative. Senza chiave le due fonti commerciali si dichiarano non configurate
e vengono saltate. Da variabile d'ambiente:

```bash
export EODHD_API_KEY="..."
export TWELVEDATA_API_KEY="..."
```

oppure in `.streamlit/secrets.toml` (già in `.gitignore`):

```toml
EODHD_API_KEY = "..."
TWELVEDATA_API_KEY = "..."
```

### Caricare una serie da CSV

Per i fondi comuni non quotati, che nessuna fonte gratuita copre. Due colonne,
data e valore della quota; separatore, decimale e formato data vengono
riconosciuti da soli, compresi i formati italiani (`;` e virgola decimale,
`GG/MM/AAAA`).

## Come vengono trattati i costi

Questo è il punto delicato, e vale la pena leggerlo.

**I NAV pubblicati sono già al netto del TER.** La commissione di gestione viene
addebitata giorno per giorno dentro il NAV: se un fondo dichiara +10% di
rendimento, quel +10% è già al netto delle spese correnti. Sottrarre di nuovo il
TER dalla performance storica significa contarlo due volte.

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

Il TER precompilato arriva dalla fonte quando disponibile, ma **la copertura sui
fondi europei è scarsa e i valori sono arrotondati** (Yahoo riporta `0.00` per un
TER reale dello 0,07%). Verifica sempre il TER sul KID e correggilo a mano: il
campo è editabile.

## Cambi valutari

I cambi sono quelli **ufficiali BCE**, disponibili dal **4 gennaio 1999**, con
ripiego su Yahoo per le valute fuori dal paniere BCE.

Non è un dettaglio estetico. La versione precedente usava le coppie Yahoo e
riempiva i buchi all'indietro con `bfill()`, ma Yahoo pubblica `EURUSD=X` solo
dal dicembre 2003: un fondo americano analizzato dal 1990 veniva convertito per
tredici anni con il cambio del 2003, **senza alcun avviso**. Ora, prima della
prima data disponibile, non si inventa nulla: il periodo viene accorciato e la
cosa viene detta esplicitamente.

## Storico esteso

Gli ETF UCITS sono giovani: VWCE quota dal 2019, VUSA dal 2012. Attivando
*Storico esteso* il periodo precedente viene ricostruito con uno strumento più
anziano, agganciato con continuità al primo dato reale.

I proxy predefiniti sono vecchie classi di fondi, non indici, perché con i
dividendi reinvestiti sono serie **total return**. La differenza è tutt'altro che
teorica — misurata sulla stessa finestra 1980-2026:

```
VFINX (fondo)   CAGR 11,44%    <- dividendi reinvestiti
^GSPC (indice)  CAGR  9,56%    <- solo prezzo
                     1,89 punti l'anno di differenza
```

Su quarant'anni quel divario vale circa un fattore due sul montante finale. Lo
stesso vale per l'indice MSCI World, che nonostante il nome resta indietro di
2,01 punti l'anno rispetto a un fondo mondiale total return. Gli indici a storico
più lungo restano selezionabili, ma segnalati per quello che sono.

L'app propone il proxy in base al nome del fondo e lo lascia **sempre
correggere** dalla colonna *Proxy storico*; se il nome non è riconosciuto non
propone nulla, perché accoppiare un settoriale all'indice sbagliato è peggio che
non ricostruire.

**Il tratto ricostruito è una stima, non un dato reale**: compare tratteggiato
nei grafici, la tabella delle metriche lo segnala nella colonna *Ricostruito*, e
l'estensione è spenta di default.

Due limiti da conoscere:

- I proxy sono quotati in dollari, quindi con valuta di riferimento diversa da
  USD la ricostruzione **non può scendere sotto il 1999** (prima data dei cambi
  BCE), per quanto profondo sia il proxy. In USD si arriva al 1980.
- Un proxy che ha smesso di quotare prima della nascita del fondo viene
  rifiutato: l'ancoraggio userebbe un valore vecchio di mesi e traslerebbe
  l'intera ricostruzione.

## Cache su disco

Le serie scaricate finiscono in `.cache/` in formato parquet. La cache è
**accumulativa**: ogni file contiene tutto lo storico mai scaricato per quella
combinazione di fonte, simbolo e valuta, non la singola finestra richiesta.
Chiedere periodi lunghi diventa quindi progressivamente più economico, e i dati
restano disponibili anche se una fonte cade o applica un limite di frequenza.

Si svuota dalla barra laterale. La posizione è sovrascrivibile con
`COMPARATORE_CACHE_DIR`.

## Struttura

```
app.py                    interfaccia Streamlit
comparatore/
  sources/
    base.py               interfaccia comune alle fonti
    yahoo.py              ricerca, metadati, prezzi
    justetf.py            ETF europei per ISIN
    eodhd.py              EOD Historical Data (a chiave)
    twelvedata.py         Twelve Data (a chiave)
    csv_source.py         serie caricate dall'utente
    openfigi.py           risoluzione ISIN -> ticker
    registry.py           priorità, ripiego, diagnostica
  fx.py                   cambi BCE con ripiego Yahoo
  cache.py                cache parquet accumulativa
  proxies.py              estensione dello storico
  engine.py               logica commissioni, simulazione, ribilanciamento
  metrics.py              metriche di performance
  data.py                 facciata sui nomi storici
```

I moduli in `comparatore/` non importano Streamlit e sono usabili da script:

```python
import datetime as dt
from comparatore.sources import Registry

reg = Registry()
res = reg.resolve("IE00B3XXRP09", dt.date(2010, 1, 1), dt.date.today(),
                  "EUR", isin="IE00B3XXRP09")
print(res.series.source, len(res.series.prices))
```

## Note e limiti

- Prezzi **total return**: i dividendi sono reinvestiti, quindi fondi ad
  accumulazione e a distribuzione sono confrontabili.
- Il backtest parte dalla prima data in cui **tutti** i fondi hanno dati; se un
  fondo è più giovane del periodo richiesto l'app lo segnala. Lo storico esteso
  attenua il problema ma non lo elimina.
- I NAV mancanti vengono riportati in avanti (`ffill`), come è corretto per i
  fondi che non quotano tutti i giorni.
- **Non** sono considerati: costi di ingresso/uscita, spread denaro-lettera,
  fiscalità, versamenti periodici (PAC).
- Un fondo la cui valuta non è risolvibile viene **escluso** anziché mescolato
  a valute diverse.

Le performance passate non sono indicative di quelle future. Questo strumento è
di analisi, non una consulenza finanziaria.
