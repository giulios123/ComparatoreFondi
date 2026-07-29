# 📈 Comparatore Fondi

Backtester per fondi comuni ed ETF: cerca gli strumenti, definisci i pesi del
portafoglio, scegli il periodo e vedi quanto sarebbe diventato il tuo capitale —
con l'impatto dei costi (TER) evidenziato. Include anche il confronto con i
fondi pensione italiani (negoziali, aperti, PIP).

---

## Guida rapida

### 1. Installazione (una volta sola)

Serve Python 3.13+ e [`uv`](https://docs.astral.sh/uv/) come gestore del
progetto. Se `uv` non è già installato:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Poi, dalla cartella del progetto, installa le dipendenze:

```bash
uv sync
```

Questo crea l'ambiente virtuale in `.venv/` e installa tutto quello che serve
(Streamlit, pandas, yfinance, openpyxl, ecc.) leggendo `pyproject.toml`.

### 2. Avvio

```bash
uv run streamlit run app.py
```

Si apre automaticamente il browser su <http://localhost:8501>. Per fermarla,
`Ctrl+C` nel terminale.

### 3. Aggiungere un fondo

1. Apri il pannello **🔎 Cerca fondi ed ETF** in cima alla pagina.
2. Digita un nome (`Vanguard S&P 500`), un ticker (`VUSA.AS`) o un **ISIN**
   (`IE00B3XXRP09`) — l'ISIN è il modo più affidabile, soprattutto per i fondi
   europei.
3. Nei risultati, premi **Aggiungi** sulla riga giusta.
4. Ripeti per ogni fondo del portafoglio.

Il fondo compare nella tabella **Composizione del portafoglio**, dove puoi
modificare:

- **Peso %** — quota del capitale assegnata (il pulsante **⚖️ Pesi uguali** li
  ridistribuisce in automatico);
- **TER %** — precompilato quando la fonte lo espone, ma verifica sempre sul
  KID del fondo e correggilo se serve;
- **Costi extra %** — per costi non già inclusi nel NAV (custodia, consulenza);
- **ISIN** — compilalo se manca: permette di usare justETF dopo l'opt-in nelle
  fonti dati o selezionandolo esplicitamente sul singolo fondo;
- **Fonte** — normalmente su "Automatica"; forzala solo se vuoi diagnosticare
  da dove arrivano i dati di un fondo specifico;
- **Proxy storico** — vedi [Storico esteso](#storico-esteso).

### 4. Rimuovere un fondo

Ogni riga della tabella ha un'icona 🗑️ a sinistra: clicca e conferma per
toglierla. **🗑️ Svuota**, sotto la tabella, azzera tutto il portafoglio.

### 5. Impostare periodo, valuta e capitale

Tutto nella barra laterale a sinistra:

- **Periodo**: pulsanti rapidi `1a · 5a · 10a · 20a · Max`, oppure le due date
  a mano.
- **Valore iniziale del portafoglio** e **Valuta di riferimento**.
- **Ribilanciamento**: nessuno (buy & hold), mensile, trimestrale, annuale —
  vedi il tooltip ⓘ accanto al menu per la spiegazione completa. In breve:
  senza ribilanciamento i pesi impostati sono solo il punto di partenza e
  derivano nel tempo con i rendimenti relativi dei fondi (chi cresce di più
  finisce per pesare di più); con un ribilanciamento periodico, i pesi
  tornano a quelli impostati a ogni inizio periodo. Il backtest non applica
  commissioni di negoziazione né tassazione sulle plusvalenze, quindi
  ribilanciare spesso qui risulta più conveniente di quanto sarebbe nella
  realtà. Nella scheda 📊 Portafoglio, sotto **Composizione nel tempo**, una
  riga di testo mostra l'effetto concreto: quanto sono derivati i pesi (buy &
  hold) oppure quanti ribilanciamenti sono scattati nel periodo.

Il grafico e le metriche si aggiornano da soli. Se i pesi non sommano a 100%
l'app li normalizza e te lo segnala.

### 6. Leggere i risultati

Cinque schede sotto il grafico principale:

| Scheda | Cosa mostra |
|---|---|
| 📊 Portafoglio | curva del capitale, netta e lorda (senza TER), composizione nel tempo |
| ⚖️ Bilanciamento | ripartizione per classe di attivo, area, settore e valuta |
| 🆚 Confronto fondi | ogni fondo preso da solo, a parità di capitale investito |
| 📉 Drawdown | perdita dal massimo storico, e rendimenti per anno solare |
| 📋 Dati | tabella numerica scaricabile in CSV |

Ogni metrica in alto (Valore finale, CAGR, Volatilità, Max drawdown, Sharpe)
ha un tooltip ⓘ con la spiegazione; l'expander **❓ Come si leggono queste
metriche**, subito sotto, elenca anche Sortino e Calmar. Nella scheda 🆚
Confronto fondi, la tabella confronta ogni fondo preso da solo con il
portafoglio: una didascalia sopra ricorda che tutte le righe partono dallo
stesso capitale, quindi i valori finali sono confrontabili direttamente riga
per riga.

Il riquadro **💸 Impatto del TER** quantifica in euro quanto i costi correnti
sono costati rispetto al fondo ipotetico senza commissioni.

---

## Fonti dati e come configurarle

Nessuna fonte, da sola, copre tutti i casi. In modalità automatica l'app le
prova in ordine e si ferma alla prima che risponde, dicendo sempre quale ha
usato.

| Ordine | Fonte | Copre | Attivazione |
|---|---|---|---|
| 1 | **CSV caricato** | qualsiasi cosa, incluso ciò che nessuno espone | caricamento locale |
| 2 | **Yahoo Finance** | fonte generalista, unica con ricerca testuale | automatica |
| 3 | **EODHD** | fondi comuni ed ETF europei, TER affidabile | chiave personale |
| 4 | **Twelve Data** | 50+ mercati | chiave personale |

**justETF non fa parte dell'ordine automatico predefinito**: usa un endpoint
interno e non documentato. È disponibile solo attivando il relativo opt-in
nella barra laterale oppure scegliendo esplicitamente `justETF` come fonte del
singolo fondo. Prima del consenso, l'interfaccia indica esattamente cosa viene
inviato: ISIN, intervallo, valuta, indirizzo IP e normali metadati HTTP; non
vengono trasmessi capitale, pesi, CSV o chiavi API. Il consenso automatico vale
per la sessione corrente ed è revocabile in qualsiasi momento. Yahoo funziona
senza configurazione; EODHD e Twelve Data si attivano quando configuri una
chiave personale.

Quando una serie non arriva, l'app mostra cosa ha tentato e come è andata,
invece di lasciare un grafico vuoto senza spiegazione.

### Licenza del codice e termini dei dati

La licenza Apache-2.0 di questo repository copre il **codice del progetto**, non
concede diritti aggiuntivi sui dati ottenuti dai servizi esterni. Ogni utente è
responsabile di usare la propria chiave e un piano compatibile con il proprio
caso d'uso:

- [yfinance](https://ranaroussi.github.io/yfinance/) è Apache-2.0, ma ricorda
  che i dati Yahoo Finance sono destinati all'uso personale; valgono anche i
  [termini Yahoo API](https://legal.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.html);
- justETF non espone un'API pubblica per questa funzione: l'integrazione è
  sperimentale, opt-in e soggetta alle
  [condizioni justETF](https://www.justetf.com/it/about/legal-terms.html) e ai
  diritti dei fornitori dei dati;
- i piani ordinari EODHD sono per uso personale e vietano redistribuzione o
  display a terzi senza approvazione: consulta i
  [termini EODHD](https://eodhd.com/financial-apis/terms-conditions);
- il free tier Twelve Data non consente uso commerciale e redistribuzione o
  display esterno richiedono diritti specifici: consulta i
  [termini Twelve Data](https://twelvedata.com/terms);
- gli identificatori OpenFIGI sono dedicati al pubblico dominio secondo i
  [termini OpenFIGI](https://www.openfigi.com/docs/terms-of-service);
- i dataset COVIP sono CC BY 4.0 e i cambi BCE richiedono attribuzione della
  fonte; i dettagli delle elaborazioni sono indicati nelle sezioni dedicate.

Pubblicare, ospitare o monetizzare un'istanza multiutente può quindi richiedere
piani commerciali o autorizzazioni separate, anche se il codice resta open
source.

### Come configurare una chiave API (EODHD / Twelve Data)

Servono solo se vuoi coprire fondi che Yahoo e justETF non hanno — tipicamente
**fondi collocati dalle reti italiane** (Mediolanum, Fineco, banche). Yahoo ne
copre solo una parte, con storico fermo al 2018.

1. Registrati e ottieni una chiave gratuita da:
   - [eodhd.com](https://eodhd.com) per EODHD;
   - [twelvedata.com](https://twelvedata.com) per Twelve Data.
2. Nella barra laterale, sotto **Fonti dati**, apri **🔑 Chiavi API (EODHD,
   Twelve Data)**, incolla la chiave e premi **Salva**. Non serve riavviare:
   il pallino accanto alla fonte passa da ⚪ a 🟢 subito. Basta compilare le
   chiavi che hai — se ne manca una, quella fonte resta semplicemente spenta.

   La chiave viene scritta in `.streamlit/api_keys.json`, con permessi
   riservati al tuo utente (`chmod 600`), e resta lì fra un avvio e l'altro
   dell'app — **Svuota cache** non la tocca. È pensato per un uso in locale,
   a utente singolo: se l'app viene deployata ed è raggiungibile da più
   persone, quel file sarebbe condiviso da tutti i visitatori, quindi in
   quel caso conviene la via alternativa qui sotto. Il file è già in
   `.gitignore`: non finisce mai nel repository. Il pulsante **Dimentica le
  chiavi salvate**, nello stesso pannello, rimuove le credenziali e cancella
  immediatamente anche le cache EODHD e Twelve Data, senza toccare le altre
  fonti.

In alternativa (o se preferisci non salvare nulla su disco), le chiavi si
possono impostare anche fuori dall'interfaccia — e in tal caso hanno la
**precedenza più bassa**, cioè valgono solo finché non ne inserisci una
dall'interfaccia:

- **`.streamlit/secrets.toml`** nella cartella del progetto (la cartella
  `.streamlit/` va creata se non esiste già):

  ```toml
  EODHD_API_KEY = "la-tua-chiave-eodhd"
  TWELVEDATA_API_KEY = "la-tua-chiave-twelvedata"
  ```

  Anche questo file è già in `.gitignore`.

- **Variabili d'ambiente**, prima di avviare:

  ```bash
  export EODHD_API_KEY="la-tua-chiave-eodhd"
  export TWELVEDATA_API_KEY="la-tua-chiave-twelvedata"
  uv run streamlit run app.py
  ```

Ordine di precedenza: interfaccia → `secrets.toml` → variabile d'ambiente.
Le serie e i metadati EODHD/Twelve Data vengono eliminati automaticamente dopo
al massimo 30 giorni. La retention può solo essere ridotta, impostando
`COMPARATORE_RESTRICTED_CACHE_DAYS` a un valore fra 1 e 30. Alla cessazione di
un abbonamento resta responsabilità dell'utente rispettare gli eventuali
obblighi di cancellazione previsti dal provider.

### Come caricare una serie da CSV

Per i fondi comuni non quotati che nessuna fonte gratuita copre (tipico caso:
un fondo interno di una banca, senza ISIN pubblico su Yahoo/justETF).

1. Nella barra laterale, apri **📄 Carica una serie da CSV**.
2. Indica il **simbolo o ISIN** a cui associarla (deve corrispondere a quello
   che userai per aggiungere il fondo dalla ricerca, o puoi crearlo tu come
   codice interno).
3. Scegli la **valuta** della serie.
4. Carica il file CSV: due colonne, data e valore della quota. Non serve
   preoccuparsi del formato esatto — separatore (`;` o `,`), decimale
   (virgola o punto) e formato data vengono riconosciuti da soli, compresi i
   formati italiani (`GG/MM/AAAA`, virgola decimale). Esempio valido:

   ```csv
   Data;NAV
   02/01/2020;12,3456
   03/01/2020;12,4010
   06/01/2020;12,3900
   ```

Una volta caricata, la serie ha priorità massima: se aggiungi un fondo con
quello stesso simbolo o ISIN, l'app userà i tuoi dati invece di cercarli
altrove.

---

## Fondi pensione (negoziali, aperti e PIP)

La scheda **🏦 Fondi pensione**, in fondo alle schede dei risultati, confronta
il tuo portafoglio con la previdenza complementare italiana: 471 comparti fra
33 fondi negoziali, 38 aperti e 71 PIP, dati [COVIP](https://www.covip.it/open-data)
([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)), con rendimenti e
**Indicatore Sintetico dei Costi (ISC)**. Il progetto modifica la
rappresentazione originale: normalizza nomi e categorie, unisce albo,
rendimenti e ISC e calcola confronti, impatto dei costi e curve sintetiche.

### Come usarla

1. Costruisci prima il tuo portafoglio come al solito (fondi, pesi, periodo).
2. Apri la scheda **🏦 Fondi pensione**.
3. Filtra per tipo (negoziale / aperto / PIP), categoria (azionario,
   bilanciato, obbligazionario, garantito) o cerca per nome — es.
   `mediolanum`, `cometa`, `previgest`.
4. Seleziona uno o più comparti nel menu **Comparti da confrontare**.

Compaiono una tabella con i rendimenti a 1/3/5/10/20 anni affiancati a quelli
del tuo portafoglio, un grafico a barre, e una tabella separata sull'impatto
dell'ISC.

### Cosa può fare e cosa no

COVIP pubblica **rendimenti medi annui su orizzonti fissi**, non le serie
storiche giorno per giorno. Per questo, per i fondi pensione **non sono
calcolabili** curva del capitale, drawdown, volatilità, Sharpe o Calmar: non è
una scelta dell'app, è che il dato non esiste pubblicamente. Chi lo vuole può
scaricare il valore quota dal sito del proprio fondo e caricarlo con
l'uploader CSV descritto sopra.

Il confronto usa **le stesse finestre pubblicate da COVIP** (es. `2016-2025`,
non "ultimi dieci anni da oggi"): se il tuo portafoglio non copre l'intera
finestra, quella cella mostra `n/d` invece di un numero calcolato su un
periodo più corto e non realmente confrontabile.

Puoi anche sovrapporre al grafico principale una **curva sintetica** per ogni
comparto scelto (interruttore in fondo alla scheda, spento di default): è una
crescita costante ricavata dal rendimento medio, utile per un colpo d'occhio,
ma non un andamento reale — il percorso vero ha oscillato, e per questo non
entra nel calcolo delle metriche di rischio.

**Il confronto non considera la fiscalità**: deducibilità dei versamenti,
tassazione agevolata dei rendimenti e dell'imposta finale sono vantaggi reali
dei fondi pensione che qui non vengono modellati, quindi i numeri mostrati li
sottostimano rispetto alla realtà.

---

## Bilanciamento del portafoglio

La scheda **⚖️ Bilanciamento** risponde a "come è ripartito quello che ho", non
a "quanto avrei guadagnato": quattro ciambelle con la ripartizione per **classe
di attivo**, **area geografica**, **settore** e **valuta di quotazione**,
calcolate sui pesi impostati nella tabella di composizione.

### Da dove viene la classificazione

Nessuna fonte di prezzo dice che cosa sia uno strumento, quindi il dato viene
ricostruito da due sorgenti, in quest'ordine:

| Sorgente | Quando interviene | Che qualità ha |
|---|---|---|
| **EODHD** | se hai configurato la chiave | percentuali vere e granulari: un ETF mondiale risulta ripartito su più aree e più settori |
| **nome del fondo** | sempre, per le dimensioni che EODHD non copre | un'etichetta sola per dimensione, dedotta da parole chiave ("Eurozone Government Bond" → obbligazionario, Europa) |

Le due si sommano invece di escludersi: EODHD non restituisce i settori di un
obbligazionario, e su quelle dimensioni la deduzione dal nome resta meglio di un
buco. La provenienza è dichiarata sopra i grafici.

### Correggere a mano

La tabella **Classificazione** sotto i grafici ha una tendina per dimensione.
Il valore `(automatica)` conserva la classificazione dedotta, che può ripartirsi
su più voci; scegliendo una voce esplicita le si attribuisce l'intero strumento.
L'expander **🔍 Dettaglio per strumento** mostra la ripartizione effettiva riga
per riga, comprese quelle su più voci.

### Limiti

- La classificazione automatica è **indicativa**: va verificata sul KID. Senza
  chiave EODHD si basa solo sul nome, che spesso non basta — uno strumento non
  riconosciuto finisce in "Non classificato", visibile in grigio nel grafico
  invece di sparire da un totale che non chiuderebbe.
- La **valuta** è quella di quotazione, non l'esposizione valutaria: un ETF sul
  mercato mondiale quotato in euro resta esposto al dollaro.
- Il perimetro sono i fondi e gli ETF della tabella di composizione. I comparti
  COVIP della scheda 🏦 restano un confronto e non entrano nella ripartizione.
- I pesi usati sono quelli **impostati**, normalizzati a 100% come nel backtest,
  non quelli derivati a fine periodo.

---

## Come vengono trattati i costi

**I NAV pubblicati sono già al netto del TER.** La commissione di gestione
viene addebitata giorno per giorno dentro il NAV: se un fondo dichiara +10% di
rendimento, quel +10% è già al netto delle spese correnti. Sottrarre di nuovo
il TER dalla performance storica significa contarlo due volte.

L'app quindi lavora con due curve:

| Curva | Significato |
|---|---|
| **Netta** | La serie così com'è pubblicata: quello che l'investitore ha realmente ottenuto. |
| **Lorda** | Il TER ri-aggiunto sopra, cioè il fondo ipotetico senza commissioni. |

**La distanza fra le due curve è esattamente il costo del TER**, ed è quello
che il riquadro "Impatto del TER" quantifica in euro e in percentuale.

C'è poi la colonna **Costi extra %** per i costi che il NAV *non* contiene
già — commissioni di custodia, consulenza, oppure il TER di una classe
diversa da quella quotata. Questi vengono sottratti dalla performance.

La formula applicata è la capitalizzazione della commissione nel tempo:

```
fattore(t) = (1 - tasso_annuo) ^ (giorni_trascorsi / 365.25)
```

Il TER precompilato arriva dalla fonte quando disponibile, ma **la copertura
sui fondi europei è scarsa e i valori sono arrotondati** (Yahoo riporta `0.00`
per un TER reale dello 0,07%). Verifica sempre il TER sul KID e correggilo a
mano: il campo è editabile.

---

## Cambi valutari

I cambi sono quelli **ufficiali BCE**, disponibili dal **4 gennaio 1999** e
ottenuti tramite l'API open source
[Frankfurter](https://frankfurter.dev/), con ripiego su Yahoo per le valute
fuori dal paniere BCE. Le serie vengono riallineate ai giorni del portafoglio e
riportate in avanti nei giorni senza nuova rilevazione; la BCE resta la fonte
dei tassi e richiede che venga citata quando i dati sono riprodotti.

Prima della prima data disponibile non si inventa nulla: il periodo viene
accorciato e l'app lo segnala esplicitamente, invece di usare un cambio
retro-riempito su anni in cui non è mai stato quotato.

---

## Storico esteso

Gli ETF UCITS sono giovani: VWCE quota dal 2019, VUSA dal 2012. Attivando
*Storico esteso*, nella barra laterale, il periodo precedente viene
ricostruito con uno strumento più anziano (il **proxy**), agganciato con
continuità al primo dato reale del fondo.

I proxy predefiniti sono vecchie classi di fondi, non indici, perché con i
dividendi reinvestiti sono serie **total return** — un indice di solo prezzo
sottostimerebbe il rendimento ricostruito di circa 2 punti l'anno. L'app
propone il proxy in base al nome del fondo (colonna **Proxy storico** nella
tabella), e lo lascia sempre correggere o disattivare per singolo fondo.

**Il tratto ricostruito è una stima, non un dato reale**: compare tratteggiato
nei grafici, la tabella delle metriche lo segnala nella colonna *Ricostruito*,
e l'estensione è spenta di default.

Due limiti da conoscere:

- I proxy sono quotati in dollari, quindi con valuta di riferimento diversa da
  USD la ricostruzione **non può scendere sotto il 1999** (prima data dei
  cambi BCE), per quanto profondo sia il proxy. In USD si arriva al 1980.
- Un proxy che ha smesso di quotare prima della nascita del fondo viene
  rifiutato: l'ancoraggio userebbe un valore vecchio di mesi.

---

## Cache su disco

Le serie scaricate finiscono in `.cache/` in formato parquet. Per Yahoo,
justETF, cambi e CSV la cache è **accumulativa**: ogni file contiene tutto lo
storico mai scaricato per quella combinazione di fonte, simbolo e valuta, non
la singola finestra richiesta. EODHD e Twelve Data seguono invece una policy
ristretta: serie e metadati vengono eliminati dopo al massimo 30 giorni e un
dato scaduto non viene usato neppure come ripiego offline.

Si svuota con il pulsante **Svuota cache** nella barra laterale. La posizione
è sovrascrivibile con la variabile d'ambiente `COMPARATORE_CACHE_DIR`. Le
chiavi API salvate dall'interfaccia vivono altrove
(`.streamlit/api_keys.json`, vedi sopra) e non vengono toccate da questo
pulsante.

---

## Pacchetto standalone (macOS / Windows)

Oltre all'uso da sorgente con `uv run streamlit run app.py`, il progetto puo'
essere impacchettato in un eseguibile che non richiede Python installato,
tramite [PyInstaller](https://pyinstaller.org/). I file coinvolti sono in
`desktop/`:

- [`desktop/launcher.py`](desktop/launcher.py) — entry point del bundle: avvia il
  server Streamlit e apre il browser, come farebbe `streamlit run app.py`.
  Reindirizza anche cache e chiavi API dentro la cartella dati dell'utente
  (`~/Library/Application Support/ComparatoreFondi` su macOS, `%APPDATA%` su
  Windows), perche' dentro un bundle installato la cartella del codice e' di
  sola lettura.
- [`desktop/comparatore.spec`](desktop/comparatore.spec) — configurazione del
  build. Un solo file serve entrambe le piattaforme; rigenera e include
  `LICENSE` e `THIRD_PARTY_NOTICES.txt` per le dipendenze effettive della
  piattaforma.

### Build locale

```bash
uv sync --group dev
uv run pyinstaller desktop/comparatore.spec --noconfirm --clean
```

Risultato in `dist/`: `ComparatoreFondi.app` su macOS, la cartella
`ComparatoreFondi/` (con `ComparatoreFondi.exe`) su Windows. La build CI su
`macos-latest` produce un `.app` **arm64 (Apple Silicon)**; per Intel/universal
serve adattare il workflow.

Se l'app non parte da Finder/Esplora risorse, il log dell'ultimo avvio e' in
`comparatore.log` nella stessa cartella dati utente citata sopra.

### Build automatica (CI)

Il workflow [`.github/workflows/desktop-build.yml`](.github/workflows/desktop-build.yml)
builda entrambe le piattaforme su GitHub Actions:

- **manuale** — tab *Actions* del repo -> *Build desktop (macOS + Windows)* ->
  *Run workflow*; gli archivi si scaricano come artefatti della run;
- **su tag** — `git tag v0.3.0 && git push origin v0.3.0` builda entrambe le
  piattaforme e pubblica una GitHub Release con i due `.zip` allegati.

Il workflow `License audit` esegue inoltre la scansione a ogni push su `main` e
su ogni pull request, su Linux, macOS e Windows. Ogni licenza non inclusa
nell'allowlist verificata viene bloccata e richiede revisione; PyInstaller è
ammesso per la specifica Bootloader Exception, che non impone GPL al programma
impacchettato.

### Firma del codice (non ancora fatta)

Le app prodotte oggi **non sono firmate**: su macOS Gatekeeper mostra
"sviluppatore non identificato" (si apre comunque con click destro -> Apri),
su Windows SmartScreen mostra un avviso simile ("Ulteriori informazioni" ->
"Esegui comunque"). Per uso personale o con pochi utenti fidati e' un
fastidio, non un blocco reale.

Per togliere questi avvisi servono due iscrizioni distinte e a pagamento,
indipendenti fra loro:

- **macOS**: [Apple Developer Program](https://developer.apple.com/programs/),
  **99 $/anno**. Serve sia per firmare che per *notarizzare* (Apple scansiona
  il binario e rilascia un ticket che Gatekeeper controlla); senza
  notarizzazione l'avviso resta anche con un certificato valido.
- **Windows**: un certificato di *code signing* (OV o EV) da una CA
  riconosciuta (DigiCert, SSL.com, ecc.), tipicamente **70-250 $/anno**. Con
  un certificato OV normale, SmartScreen continua comunque a mostrare
  l'avviso finche' l'eseguibile non accumula una "reputazione" (download e
  utilizzo nel tempo); un certificato **EV** aggira questo periodo di
  attesa ma costa di piu'.

Nessuno dei due e' legato all'altro: puoi firmare solo macOS, solo Windows,
o nessuno dei due, senza cambiare nulla nel workflow di build oltre ad
aggiungere le credenziali come segreti del repository quando/se deciderai di
procedere.

---

## Struttura del progetto

```
app.py                    interfaccia Streamlit
.streamlit/
  config.toml              barra Streamlit senza Deploy/Rerun (committato)
  secrets.toml             chiavi API, alternativa al pannello (gitignored)
  api_keys.json            chiavi API salvate dal pannello (gitignored)
comparatore/
  sources/
    base.py               interfaccia comune alle fonti
    yahoo.py              ricerca, metadati, prezzi
    justetf.py            ETF europei per ISIN
    eodhd.py               EOD Historical Data (a chiave)
    twelvedata.py          Twelve Data (a chiave)
    csv_source.py          serie caricate dall'utente
    openfigi.py            risoluzione ISIN -> ticker
    registry.py            priorità, ripiego, diagnostica
  fx.py                    cambi BCE con ripiego Yahoo
  allocazione.py           classe di attivo, area e settore per il bilanciamento
  cache.py                 cache parquet accumulativa
  keys.py                  chiavi API salvate dall'interfaccia
  proxies.py               estensione dello storico
  covip.py                 fondi pensione: catalogo, rendimenti, ISC
  horizons.py              rendimenti sulle finestre COVIP
  engine.py                logica commissioni, simulazione, ribilanciamento
  metrics.py               metriche di performance
  data.py                  facciata sui nomi storici
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

---

## Note e limiti

- Prezzi **total return**: i dividendi sono reinvestiti, quindi fondi ad
  accumulazione e a distribuzione sono confrontabili.
- Il backtest parte dalla prima data in cui **tutti** i fondi hanno dati; se
  un fondo è più giovane del periodo richiesto l'app lo segnala. Lo storico
  esteso attenua il problema ma non lo elimina.
- I NAV mancanti vengono riportati in avanti (`ffill`), come è corretto per i
  fondi che non quotano tutti i giorni.
- **Non** sono considerati: costi di ingresso/uscita, spread denaro-lettera,
  fiscalità, versamenti periodici (PAC).
- Un fondo la cui valuta non è risolvibile viene **escluso** anziché mescolato
  a valute diverse.

Le performance passate non sono indicative di quelle future. Questo strumento
è di analisi, non una consulenza finanziaria.

---

## Licenza

Copyright 2026 Giulio Sciarappa.

Il codice di Comparatore Fondi è distribuito sotto
[Apache License 2.0](LICENSE). Le licenze, gli avvisi e i collegamenti al codice
sorgente delle dipendenze distribuite nel bundle sono raccolti in
[THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt). I dati recuperati dai
provider restano soggetti ai rispettivi termini e non sono relicenziati da
Apache-2.0.
