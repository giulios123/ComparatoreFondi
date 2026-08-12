# 004 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Introdurre un modulo puro per le analisi comparative. Riceve curve o prezzi
gia' validati e convertiti nella valuta base, allinea esplicitamente il periodo
comune e calcola correlazioni, metriche attive e finestre rolling senza
conoscere Streamlit.

Il benchmark usa il normale `Registry` per ricerca, diagnostica e prezzi, ma
resta una risoluzione separata da `resolve_many()` del portafoglio. I preset
riusano simbolo e descrizione di `proxies.CATALOG`; non riusano invece la
logica di innesto storico, perche' un benchmark non va ricostruito in
silenzio. Per il PAC si esegue una simulazione a una sola holding con costi
aggiuntivi nulli e si confronta il NAV per le metriche.

Le correlazioni usano gli ultimi valori mensili e un unico intervallo comune a
tutte le colonne. Le finestre rolling lavorano sulla stessa frequenza mensile:
12, 36, 60 e 120 mesi, annualizzando il rapporto fra gli estremi. Non si usano
correlazioni pairwise su periodi diversi, che renderebbero le celle della
matrice non confrontabili.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/comparative.py` | Allineamento comune, rendimenti mensili, correlazioni, rolling, metriche attive e risultati strutturati |
| `comparatore/proxies.py` | Esposizione prudente dei due preset gia' verificati, senza cambiare la logica di estensione |
| `comparatore/portfolio_io.py` | Benchmark opzionale nei parametri, con compatibilita' dei JSON precedenti |
| `app.py` | Selettore, ricerca benchmark, risoluzione non bloccante, grafici e tabelle |
| `comparatore/locales/{it,en,fr,de}.py` | Etichette, spiegazioni e diagnostica |
| `tests/test_comparative.py` | Formule chiuse per allineamento, metriche e rolling |
| `tests/test_portfolio_io.py` | Round-trip e backfill del benchmark |
| `tests/test_app_sintassi.py` | Guardia che il benchmark non entra negli holdings del portafoglio e non precede l'export |

Riuso esplicito: `Registry.resolve()`, `run_backtest()`, `metrics.summarize()`,
`proxies.CATALOG`, `coverage_warnings()` e la diagnostica fonti gia' tradotta.

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Benchmark fisso S&P 500 | Non rappresenta ogni portafoglio e trasforma un riferimento facoltativo in una scelta editoriale implicita |
| Indici di solo prezzo per avere piu' storia | Perdono i dividendi e falsano il confronto pluriennale |
| Troncare l'intero backtest alla nascita del benchmark | Porta via dati utili al portafoglio per soddisfare una funzione opzionale |
| Correlazioni giornaliere | Sono piu' sensibili a calendari diversi, NAV non sincroni e rumore di mercato |
| Correlazioni pairwise con finestre diverse | Due celle non descriverebbero lo stesso periodo e sembrerebbero comunque direttamente confrontabili |
| Rolling su 252 giorni per anno | Un numero fisso di sedute non coincide con anni di calendario e gestisce male serie mensili o fondi con quotazioni discontinue |

## Rischi

- Un benchmark corto puo' lasciare poche osservazioni: soglie minime e periodo
  comune visibile evitano una precisione apparente.
- Tracking error e information ratio possono essere scambiati per previsioni:
  tooltip e testi devono dichiarare che descrivono soltanto il periodo storico.
- Il benchmark libero puo' coincidere con un fondo del portafoglio: e' lecito,
  ma resta una seconda vista della stessa serie e non una holding duplicata.
- Un nuovo percorso di risoluzione in `app.py` puo' spostare l'export sotto un
  errore: la guardia sorgente protegge l'ordine.

## Verifica

1. Test con serie sintetiche a rendimento costante per cui CAGR, tracking error
   e rolling hanno soluzione nota.
2. Test con storici sfalsati: il portafoglio conserva l'intera curva e il
   confronto usa solo l'intersezione.
3. Test con benchmark assente o fonte fallita: il backtest del portafoglio
   produce gli stessi risultati del percorso senza benchmark.
4. `uv run python -m unittest discover -s tests -p "test_*.py"`.
5. `uv run ruff check .` e `git diff --check`.
6. Smoke Streamlit offline con serie CSV per portafoglio e benchmark, PAC
   acceso e spento, export/import e tutte e quattro le lingue.
