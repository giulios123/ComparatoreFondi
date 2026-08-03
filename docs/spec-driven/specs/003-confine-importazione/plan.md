# 003 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

La validazione entra nei due punti che già esistono per questo scopo —
`portfolio_io.load()` e `sources/csv_source.parse_csv()` — invece di crescere
in `app.py`: sono già i moduli responsabili del confine, sono già testabili da
script, e `app.py` non è comunque importabile per i test (vincolo noto,
`AGENTS.md`).

Per il JSON, tipo/finitezza/range di `weight`, `ter`, `extra` e la ricerca di
simboli vuoti o duplicati si aggiungono dentro il ciclo che già itera sui
fondi in `load()`, subito dopo il controllo dei campi minimi esistente. Per il
CSV, un controllo esplicito di positività e finitezza si aggiunge subito dopo
il filtro `notna()` già presente, prima della deduplicazione dell'indice:
`CsvParseError` viene sollevata con la prima data non valida invece di
lasciarla passare in una serie apparentemente pulita.

Il `TypeError` a video si chiude spostando la chiamata a
`pesi.rinormalizza()` **dentro** il blocco `try` che già cattura
`PortfolioError` in `app.py`. Dopo la validazione più stringente non dovrebbe
più sollevare nulla di imprevisto, ma è comunque la correzione giusta: nel
punto in cui si gestiscono gli errori di un file esterno, ogni eccezione
imprevista deve restare gestita, non propagarsi.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/portfolio_io.py` | Nuove costanti `_PESO_MAX = 100.0`, `_TER_MAX = 10.0` (stessi bound di `app.py:955-967`); validazione di tipo/finitezza/range per `weight`/`ter`/`extra`, simboli vuoti/duplicati, tetto dimensione file e numero fondi — tutto dentro `load()` |
| `comparatore/sources/csv_source.py` | Dopo il filtro `notna()` esistente, controllo esplicito `> 0` e `isfinite`; solleva `CsvParseError` con la data della prima riga non valida; tetto sui byte in ingresso prima del parsing |
| `app.py` | `pesi.rinormalizza(...)` spostato dentro il `try` esistente; il ramo `except CsvParseError` mostra `t("csv.parse_error", errore=str(exc))` invece di `st.error(str(exc))` nudo |
| `comparatore/locales/{it,en,fr,de}.py` | Nuova chiave `csv.parse_error`, stessa forma di `portfolio_io.import_error` già esistente (`"File non valido: {errore}"` e le sue traduzioni) |
| `tests/test_portfolio_io.py` | Casi nuovi: `weight` stringa, `NaN`, `inf`, fuori `[0,100]`; `ter`/`extra` fuori `[0,10]`; `symbol` vuoto; `symbol` duplicato; file oltre soglia byte; più fondi della soglia |
| `tests/test_csv_source.py` *(nuovo file — oggi non esiste)* | Quota zero/negativa/infinita con la data nel messaggio; file oltre soglia byte. Non un refactor generale dei test di `parse_csv`: solo ciò che questa spec cambia |
| `tests/test_app_sintassi.py` | Guardia che `rinormalizza(...)` compare all'interno del blocco `try`/`except portfolio_io.PortfolioError`, non dopo |

Riuso esplicito: `portfolio_io.import_error` (chiave di traduzione già
esistente, `"File non valido: {errore}"`) per tutti i nuovi messaggi JSON,
nessuna chiave nuova necessaria lì; i bound `[0, 100]` e `[0, 10]` letti da
`app.py:955-967` invece di inventati; `PortfolioError` e `CsvParseError`
esistenti, nessun nuovo tipo di eccezione.

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Ricalcare `BacktestInputError` (spec 002: `kind` + `symbols` strutturati) anche qui | Il meccanismo già esistente — un messaggio libero interpolato in un'unica frase tradotta (`t("portfolio_io.import_error", errore=...)`) — copre già il requisito senza una chiave per ogni tipo di errore. Introdurre una seconda struttura per lo stesso confine avrebbe significato due modi diversi di fare la stessa cosa nello stesso file, senza un beneficio proporzionale: qui non serve tradurre template diversi per `kind` diversi, basta un messaggio descrittivo. |
| Validare dentro `app.py`, dove l'errore viene mostrato | Sposterebbe logica di dati fuori dalla libreria, rendendola non testabile da script e non riusabile — esattamente ciò che il confine libreria/UI di `AGENTS.md` vuole evitare. |
| Sostituire le quote non valide con l'ultimo valore buono (`ffill`) invece di respingerle | Stessa alternativa già scartata dalla decisione 21 per il motore: nasconde l'errore invece di segnalarlo. Applicare qui lo stesso principio mantiene i due confini (motore e import) coerenti fra loro. |
| Affidarsi solo al `maxUploadSize` di Streamlit (default 200 MB) invece di un tetto applicativo | Protegge il processo, non l'utente: un portafoglio reale pesa poche decine di KB, quindi un tetto molto più stretto intercetta l'anomalia (file corrotto, generato male) senza mai infastidire l'uso reale, e lo fa con un messaggio comprensibile invece che con un rifiuto silenzioso di Streamlit. |

## Rischi

- **Le soglie di `ter`/`extra`/`weight` duplicano bound già scritti
  nell'editor** (`app.py:955-967`) senza un collegamento automatico: se
  cambiano lì, non cambiano qui da soli. Non eliminabile con l'attuale
  confine architetturale (`app.py` non è importabile, quindi non può essere la
  fonte di una costante condivisa con `comparatore/`); si mitiga con un
  commento incrociato nei due punti, così chi cambia l'uno trova un
  riferimento all'altro.
- **CSV più severo può respingere file che oggi passano silenziosamente.** È
  il comportamento voluto — coerente con la decisione 21 — ma va controllato
  che nessun CSV reale già in uso (per esempio quelli usati per gli screenshot
  del README) contenga uno zero o un negativo che oggi viene tollerato.
- **Spostare `rinormalizza()` dentro il `try` allarga cosa viene mostrato come
  "file non valido".** Dopo la validazione più stringente l'unica eccezione
  plausibile in quel punto resta legata ai dati del file, quindi il messaggio
  generico resta corretto; va comunque verificato che nessuna eccezione
  "vera" (bug, non dato malformato) finisca silenziosamente presentata come
  errore utente.

## Verifica

1. `uv run python -m unittest discover -s tests -p "test_*.py"` — tutti i test
   esistenti restano verdi, i nuovi passano.
2. `uv run ruff check .` pulito.
3. `uv run streamlit run app.py`, via CSV offline (nessuna rete verso le
   fonti):
   - import di un JSON con `"weight": "abc"` → errore tradotto, nessun
     traceback in console (criterio 1);
   - import di un JSON con due fondi dallo stesso `symbol` → errore che
     indica quale (criterio 3);
   - caricamento di un CSV con una riga a quota zero → errore con la data,
     nessuna serie aggiunta (criterio 5);
   - caricamento di un JSON e di un CSV già usati prima di questo cambiamento
     → stesso comportamento di prima (criterio 7, confrontato a mano).
