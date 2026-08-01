# Decisioni

Registro delle scelte che **vincolano il lavoro futuro**. Una voce per
decisione, non per commit. Le voci non si cancellano: una decisione superata si
marca come tale e rimanda a quella che l'ha sostituita.

Le decisioni da 1 a 17 sono state ricostruite a posteriori (agosto 2026) dai
messaggi di commit e dai commenti nel codice, che restano la fonte: dove il
codice spiega già una ragione, qui c'è il rimando, non una copia.

---

### 1 · Streamlit + `uv`, eseguito da sorgente

**Contesto.** Un'app per utenti non tecnici, scritta da una persona sola.
**Scelta.** Streamlit per l'interfaccia, `uv` come gestore di progetto e
Python 3.13. Nessun `[build-system]` in `pyproject.toml`: il progetto **non** si
installa come wheel, si esegue da sorgente.
**Conseguenze.** Niente `console_scripts`, niente `pip install comparatore-fondi`.
Chi vuole un eseguibile passa dal bundle PyInstaller (decisione 13). Scoperta
solo in seguito: senza `[build-system]` il pacchetto non ha mai un `.dist-info`,
quindi `importlib.metadata.version()` non lo trova **mai** — ne' da sorgente ne'
nel bundle. Ha tenuto rotto per due release il pannello versione in `app.py`,
finche' la decisione 20 non gli ha dato un'altra fonte.
**Traccia.** `pyproject.toml`, `.python-version`.

### 2 · `comparatore/` non importa mai Streamlit

**Contesto.** Un'app Streamlit tende a diventare un file solo in cui logica e
interfaccia si impastano, e da lì non si torna indietro.
**Scelta.** Tutta la logica in `comparatore/`, che non importa Streamlit; tutta
l'interfaccia in `app.py`.
**Conseguenze.** La libreria è usabile da uno script e testabile senza server —
il README lo documenta con un esempio. Il prezzo è che `app.py` non è
importabile e va coperto in un altro modo (decisione 16).
**Traccia.** README § Struttura del progetto; `comparatore/__init__.py`.

### 3 · Fonti multiple in ordine, con justETF in opt-in

**Contesto.** Nessuna fonte gratuita copre tutti i casi: Yahoo ha la ricerca ma
buchi sugli ETF europei, justETF ha gli ETF europei ma vuole l'ISIN e non ha
ricerca, il CSV copre tutto ma va caricato a mano.
**Scelta.** Un registry che le prova in ordine (CSV → Yahoo → EODHD → Twelve
Data) e si ferma alla prima che risponde, registrando **ogni tentativo e il suo
esito**. justETF usa un endpoint interno non documentato: entra nell'ordine
automatico **solo con opt-in esplicito** dell'utente.
**Conseguenze.** Una serie mancante produce una spiegazione a video, non un
grafico vuoto. L'opt-in justETF va ricordato fra un avvio e l'altro
(decisione 6).
**Traccia.** `comparatore/sources/registry.py` (intestazione); PR #7.

### 4 · Cache su disco accumulativa, separata da chiavi e preferenze

**Contesto.** `st.cache_data` vive nel processo: muore a ogni riavvio e non
protegge dal rate-limiting di Yahoo. Con vent'anni di default e più fondi in
portafoglio, ogni riavvio ripagherebbe l'intero download.
**Scelta.** Cache su disco in parquet, **accumulativa**: ogni file contiene
tutto lo storico mai scaricato per quella tripla (fonte, simbolo, valuta), non
la finestra richiesta. Accanto, un sidecar JSON con l'intervallo *richiesto* —
senza, un fondo nato nel 2012 e interrogato dal 1990 risulterebbe
perennemente "non coperto" e verrebbe riscaricato ogni volta.
**Conseguenze.** Chiedere periodi lunghi diventa progressivamente più economico.
"Svuota cache" non tocca chiavi né preferenze, che vivono fuori da `.cache/`.
**Traccia.** `comparatore/cache.py` (intestazione).

### 5 · Chiavi API in un file a parte, mascherate a video

**Contesto.** Le chiavi EODHD e Twelve Data si inseriscono dall'interfaccia.
**Scelta.** File dedicato (`.streamlit/api_keys.json`, permessi `600`), in
`.gitignore`, mostrato a video sempre mascherato.
**Conseguenze.** Una chiave non finisce mai in un commit né in uno screenshot.
Cancellare una chiave cancella anche la cache che ne dipende.
**Traccia.** `comparatore/keys.py`; commit `09814df`.

### 6 · Le preferenze si ricordano, e degradano in silenzio

**Contesto.** Lingua e opt-in justETF vanno ricordati fra un avvio e l'altro.
**Scelta.** Un file di preferenze separato dalla cache. Un file assente o
corrotto equivale a "nessuna preferenza salvata", **non** a un errore che
blocca l'avvio; anche un disco pieno o di sola lettura non deve impedire l'uso
dell'app.
**Conseguenze.** La persistenza è un miglioramento, mai un punto di rottura.
**Traccia.** `comparatore/prefs.py` (intestazione); commit `2284b0a`, `09814df`.

### 7 · Quattro lingue, e i selettori non accettano testo libero

**Contesto.** L'app si rivolge anche a chi non legge l'italiano; la lingua si
sceglie in cima alla barra laterale e va rilevata dal browser al primo avvio.
**Scelta.** Quattro cataloghi (`it`, `en`, `fr`, `de`) con `it.py` come
riferimento e un test che fallisce se uno resta indietro. Tutti i selettori
usano `filter_mode=None`: un utente non deve poter scrivere un valore che non
esiste fra le opzioni.
**Conseguenze.** Ogni stringa nuova è quattro modifiche, non una. In cambio,
nessuna stringa può comparire non tradotta.
**Traccia.** `comparatore/i18n.py`, `tests/test_i18n.py`; commit `21191d9`.

### 8 · Per i fondi pensione non si calcola ciò che non è calcolabile

**Contesto.** COVIP pubblica **medie annue su orizzonti fissi** (1, 3, 5, 10,
20 anni), non serie storiche. Da cinque numeri annualizzati l'andamento anno per
anno non è recuperabile: è informazione irreversibilmente aggregata.
**Scelta.** Per questi strumenti l'app **non** calcola curva del capitale,
drawdown, volatilità, Sharpe, Sortino, Calmar né rendimenti per anno solare. La
`serie_sintetica()` è una retta a rendimento costante e serve **solo** a rendere
confrontabile il punto d'arrivo: non va data in pasto al motore di backtest,
dove produrrebbe volatilità nulla e uno Sharpe privo di senso, facendo apparire
un comparto azionario come privo di rischio.
**Conseguenze.** Il confronto abilitato è per orizzonti, ed è rigoroso proprio
perché non finge di avere dati che non esistono. Chi vuole quelle misure carica
il valore quota del proprio fondo via CSV.
**Traccia.** `comparatore/covip.py` (intestazione e `serie_sintetica()`).

### 9 · Le finestre COVIP sono anni solari interi, e si dichiara

**Contesto.** Le colonne dicevano solo "1 anni", "10 anni", con il periodo nel
tooltip: non si capiva né cosa fossero né perché un decennio potesse rendere
meno di un quinquennio (sono finestre chiuse diverse, non periodi cumulativi).
E un backtest agosto 2021 → luglio 2025 non copre la finestra "5 anni =
2021-2025", pur avendo gli stessi anni di calendario.
**Scelta.** Il periodo entra nell'intestazione ("10 anni · 2016-2025"), il
singolare si legge "1 anno", e un pulsante allinea il periodo del backtest alle
finestre COVIP. Quando il portafoglio non copre nessuna finestra, l'app mostra
comunque il suo rendimento sul proprio periodo, **dichiarato non confrontabile**.
**Conseguenze.** Un `n/d` non resta mai senza spiegazione.
**Traccia.** Commit `9d06934`, `7d205fc`; `allinea_periodo_covip()` in `app.py`.

### 10 · I pesi sommano sempre a 100, e si perdono solo apposta

**Contesto.** Aggiungere un fondo azzerava l'allocazione impostata a mano.
**Scelta.** I pesi si ridistribuiscono **in proporzione**, mantenendo i rapporti
reciproci fra i fondi già presenti; l'invariante "somma 100%" vale sempre, non
solo dopo la prima modifica. L'unico modo di perdere volutamente
un'allocazione è il pulsante **⚖️ Pesi uguali**.
**Conseguenze.** Nessuna azione dell'utente distrugge lavoro senza che l'abbia
chiesto.
**Traccia.** `comparatore/pesi.py`; commit `393e296`.

### 11 · Il PAC è opt-in, e il confronto COVIP usa il NAV

**Contesto.** I versamenti periodici cambiano il significato di quasi tutte le
metriche: il capitale non è più fisso, il CAGR non basta più (serve l'XIRR), e
il valore grezzo del portafoglio cresce anche solo perché ci si versa dentro.
**Scelta.** Il PAC è una funzione avanzata, dietro un expander collassato —
chi non lo apre non lo incontra. Se arriva già attivo (da un portafoglio
importato) l'expander **si apre da solo**, così non resta un PAC acceso ma
invisibile che produce numeri inspiegabili. Il confronto con i rendimenti COVIP
usa il **NAV** e non il valore grezzo: altrimenti ogni versamento verrebbe letto
come un guadagno di mercato, gonfiando la riga "il tuo portafoglio" proprio
accanto a rendimenti ufficiali pubblicati.
**Conseguenze.** Un ramo in più in molte metriche, in cambio di un confronto che
resta onesto.
**Traccia.** Commit `edffbf9`, `cced333`; `app.py` (riga "il tuo portafoglio").

### 12 · L'export del portafoglio precede il backtest

**Contesto.** Se il pulsante di download vive dopo il backtest, un errore nel
backtest porta via anche la possibilità di salvare il proprio lavoro.
**Scelta.** Il pulsante si prenota con `st.empty()` **prima**, e si riempie
dopo.
**Conseguenze.** È un vincolo sull'*ordine delle righe* di `app.py`, che nessun
type checker può proteggere: da qui la guardia AST nei test.
**Traccia.** Commit `e067f78`; `tests/test_app_sintassi.py`.

### 13 · Bundle PyInstaller *onedir*, con i dati utente fuori dal bundle

**Contesto.** Chi non ha Python deve poter usare l'app.
**Scelta.** Un solo file `.spec` per macOS e Windows, modalità *onedir*.
L'`Analysis` elenca due script: `launcher.py` (l'eseguibile vero) e `app.py`,
che serve solo a far seguire all'analisi statica i suoi import — Streamlit lo
legge come testo a runtime e sarebbe altrimenti invisibile. Cache, chiavi e
preferenze vengono spostate nella cartella dati utente del sistema operativo,
perché dentro un bundle installato la cartella del codice è di sola lettura.
Porta **8765**, non la 8501 dell'uso da sorgente.
**Conseguenze.** Due configurazioni di avvio da tenere a mente quando si
documenta o si diagnostica.
**Traccia.** Commit `ed185b7`; `desktop/comparatore.spec`, `desktop/launcher.py`.

### 14 · Le licenze si verificano in CI, su tutte e tre le piattaforme

**Contesto.** Il bundle ridistribuisce decine di dipendenze, e le dipendenze
effettive cambiano da piattaforma a piattaforma.
**Scelta.** `THIRD_PARTY_NOTICES.txt` e `THIRD_PARTY_LICENSES.json` sono
**generati**, mai scritti a mano, e rigenerati a ogni build. Un audit gira su
Linux, macOS e Windows a ogni push e PR: ogni licenza fuori dall'allowlist
blocca. PyInstaller è ammesso per la sua Bootloader Exception, che non impone
la GPL al programma impacchettato.
**Conseguenze.** Aggiungere una dipendenza può far fallire la CI per motivi di
licenza, ed è voluto.
**Traccia.** Commit `8459ea8`; `.github/workflows/license-audit.yml`.

### 15 · La barra degli strumenti di Streamlit è in modalità `viewer`

**Contesto.** Deploy, Rerun e Clear cache sono comandi di Streamlit, non
dell'app: a chi usa il comparatore non servono e possono confondere.
**Scelta.** `toolbarMode = "viewer"` nel config committato. La cache si svuota
dal pulsante nella barra laterale, che è dell'app.
**Traccia.** `.streamlit/config.toml`.

### 16 · `app.py` si protegge con guardie sul sorgente

**Contesto.** Conseguenza diretta della decisione 2: nessun modulo importa
`app.py`, quindi un errore di sintassi può restare invisibile fino al primo
avvio manuale — è successo (commit `caa1c91`).
**Scelta.** `tests/test_app_sintassi.py` lo compila con `ast.parse()` e verifica
via AST o via testo gli invarianti che nessun type checker può proteggere.
**Conseguenze.** Chi cambia `app.py` in modo strutturale aggiunge lì la propria
guardia. È l'unico posto dove una regressione dell'interfaccia può essere
intercettata prima dell'utente.
**Traccia.** `tests/test_app_sintassi.py`.

### 17 · Le release sono due `.zip` non firmati, su tag a tre componenti

**Contesto.** Firmare costa: Apple Developer Program 99 $/anno, certificato di
code signing Windows 70-250 $/anno — e con un certificato OV normale SmartScreen
continua comunque ad avvisare finché l'eseguibile non accumula reputazione.
**Scelta.** Si pubblica non firmato, documentando a video e nel README come
aprire l'app nonostante Gatekeeper e SmartScreen. Il workflow si attiva sui tag
`v*.*.*`.
**Conseguenze.** Il tag deve avere **tre** componenti: `v0.3.0` sì, `v0.2` no —
quella release ha richiesto una run manuale del workflow. La build macOS è
**arm64 (Apple Silicon)**: per Intel/universal va adattato il workflow.
**Traccia.** `.github/workflows/desktop-build.yml`; README § Firma del codice.

### 18 · CSS custom solo se scoped, e solo se non c'è alternativa

*Agosto 2026 — spec [`001-preset-periodo-nowrap`](../spec-driven/specs/001-preset-periodo-nowrap/spec.md)*

**Contesto.** I pulsanti dei periodi rapidi si spezzavano ("10" sopra, "a"
sotto) quando la barra laterale veniva stretta. Il primo tentativo — passare da
cinque pulsanti in fila a due file da tre e da due — ha alzato la soglia ma non
l'ha eliminata, e nessuna opzione di Streamlit permette di dire "questa
etichetta non va a capo".
**Scelta.** Si ammette il CSS custom, con due vincoli: agganciato alla classe
`st-key-…` di un `st.container(key=…)` e **mai** a un selettore globale; e
motivato da un commento che spieghi perché non c'era altra strada. Oggi ce n'è
**un solo blocco**, in cima ad `app.py`.
**Conseguenze.** L'app dipende da un dettaglio del DOM di Streamlit (le classi
`st-key-…`, documentate, e `.stButton`, che non lo è): un aggiornamento maggiore
di Streamlit va verificato a occhio sulla barra stretta. La guardia in
`tests/test_app_sintassi.py` protegge il legame fra il contenitore e la regola,
non il fatto che Streamlit continui a emettere quelle classi.
**Alternative scartate.** Etichette più corte (perdono informazione e non
risolvono in tedesco); un solo selettore a tendina al posto dei pulsanti (un
clic in più per l'azione più frequente della barra laterale).

### 19 · Un linter in CI, in sola verifica

*Agosto 2026*

**Contesto.** Nessuno strumento controllava lo stile del codice. Misurato con
ruff sul codice esistente: pulitissimo, **due soli** rilievi con le regole
predefinite (due import morti in `covip.py`). Introdurne uno costava poco e da
quel momento in poi avrebbe protetto.
**Scelta.** `ruff check`, non `ruff format`: un formatter riscriverebbe ogni
file toccato, e combatterebbe con l'allineamento manuale dei cataloghi di
traduzione, dove ogni riga è una voce e la leggibilità della colonna conta più
di una lunghezza uniforme. Regole `E, W, F, I, UP`, riga a 100 caratteri (il
file più lungo del repository sfora 88 di 25 caratteri: 79 o 88 avrebbero
costretto a spezzare frasi che si leggono meglio intere). `UP042` (StrEnum) è
escluso: cambierebbe cosa restituisce `str()` su `Rebalance`/`FeeMode`/
`Frequency`, che finisce nel JSON dei portafogli esportati — un cambio di
formato dati, non di stile, e semmai passa da una spec sua. Job CI separato da
`unittest`, cosi' un fallimento di stile non nasconde l'esito dei test.
**Conseguenze.** 41 rilievi preesistenti corretti (11 in automatico — newline
finali, import morti, ordinamento; 30 a mano, tutte righe lunghe). Le
stringhe tradotte nei cataloghi sono state solo **spezzate su più righe** con
la sintassi di concatenazione già in uso altrove nello stesso file — mai
riformulate: è stato verificato confrontando il valore Python di ogni chiave,
non solo il diff testuale, che le quattro lingue restassero carattere per
carattere identiche.
**Alternative scartate.** `force-single-line` in `isort` per preservare lo
stile "un simbolo per riga" di un singolo blocco di import in `app.py`: avrebbe
riscritto la convenzione opposta, e dominante, usata in una decina di altri
file (`from x import a, b, c` su una riga). Non era una convenzione
documentata: si è lasciato che il blocco in `app.py` si allineasse al resto.
**Traccia.** `pyproject.toml` (`[tool.ruff]`), `.github/workflows/tests.yml`
(job `lint`).

### 20 · La versione vive in `comparatore/__init__.py`

*Agosto 2026*

**Contesto.** La versione sembrava "solo" duplicata fra `pyproject.toml` e
`desktop/comparatore.spec`. Indagando è emerso un terzo consumatore silenzioso:
`app.py` la leggeva con `importlib.metadata.version("comparatore-fondi")` nel
pannello "Informazioni e licenze". Per la decisione 1 il pacchetto non viene
**mai** installato come distribuzione, quindi quella chiamata falliva sempre e
il pannello mostrava "-" fin da quando esiste — un bug silenzioso, mai
segnalato perché non rompeva nulla di bloccante.
**Scelta.** `__version__` in `comparatore/__init__.py` come fonte unica: è il
file che finisce nel bundle e che si legge senza installare nulla. `app.py` lo
importa. `desktop/comparatore.spec` lo estrae con `ast.parse()` invece di
importare il pacchetto — che in fase di build tirerebbe dentro pandas e
streamlit solo per una stringa, oltre a introdurre un ordine di inizializzazione
non necessario. `pyproject.toml` resta un secondo letterale, perché senza
`[build-system]` deve restare statico, ma un test lo tiene allineato.
**Conseguenze.** Il pannello versione mostra di nuovo un numero, non un
segnaposto. Un bump di versione ora tocca due file invece di tre, e
`tests/test_versione.py` avverte se restano scoordinati.
**Alternative scartate.** Aggiungere un `[build-system]` per far funzionare
`importlib.metadata` sul serio: è la via canonica, ma contraddice la decisione
1 (eseguito da sorgente) e avrebbe richiesto `copy_metadata` nel bundle
PyInstaller per lo stesso motivo per cui oggi serve `collect_all` sui pacchetti
con dati non-Python. Rimandata, non scartata per sempre: se il progetto dovesse
mai distribuirsi anche via PyPI, e' la prima cosa da rivedere.
**Traccia.** `comparatore/__init__.py`, `desktop/comparatore.spec`,
`tests/test_versione.py`.
