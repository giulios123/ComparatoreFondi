# 011 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Prima dell'implementazione vanno chiuse le tre domande della spec. Poi si
introduce un catalogo centrale di mercati e alias, indipendente dalla UI, e una
funzione pura che raggruppa le quotazioni per identità e applica un ordinamento
deterministico. Le fonti continuano a restituire i dati grezzi; il registro
normalizza i codici e ordina solo quando prepara i risultati per l'utente.

La preferenza viene salvata nel file locale già usato per le impostazioni. Un
simbolo esatto e una posizione persistita saltano la selezione automatica e
mantengono sempre la propria quotazione.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/markets.py` | Catalogo di mercati, alias e ordinamento puro delle quotazioni. |
| `comparatore/sources/base.py` | Rende coerente il campo mercato nell'identità di una quotazione. |
| `comparatore/sources/openfigi.py` | Usa il catalogo centrale invece di una graduatoria locale duplicata. |
| `comparatore/sources/eodhd.py` | Normalizza suffissi e mercati tramite il catalogo centrale. |
| `comparatore/sources/yahoo.py` | Mappa i codici di mercato disponibili senza dedurre quelli assenti. |
| `comparatore/sources/registry.py` | Raggruppa per identità, applica la preferenza e preserva la ricerca esatta. |
| `comparatore/prefs.py` | Salva e valida l'elenco ordinato con migrazione silenziosa delle preferenze precedenti. |
| `comparatore/portfolio_io.py` | Verifica che import ed export mantengano la quotazione esatta. |
| `app.py` | Aggiunge il selettore ricercabile, il riordino e i gruppi espandibili dei risultati. |
| `comparatore/locales/it.py` | Testi italiani per preferenze, mercati e spiegazioni. |
| `comparatore/locales/en.py` | Traduzioni inglesi. |
| `comparatore/locales/fr.py` | Traduzioni francesi. |
| `comparatore/locales/de.py` | Traduzioni tedesche. |
| `tests/test_markets.py` | Copre alias, gruppi, preferenze e ordinamento deterministico. |
| `tests/test_registry.py` | Copre ricerca generica, ISIN e simbolo esatto. |
| `tests/test_prefs.py` | Copre persistenza e compatibilità delle preferenze. |
| `tests/test_portfolio_io.py` | Copre la conservazione della quotazione importata. |
| `tests/test_app_sintassi.py` | Aggiunge le guardie sorgente per preferenza e risultati raggruppati. |

Si riusano `prefs.py`, il registro delle fonti e l'identità già contenuta nei
risultati; il catalogo elimina le graduatorie di mercati duplicate invece di
aggiungerne una terza.

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Salvare una sola borsa preferita | Non rappresenta una priorità di ripiego e costringe a cambiare spesso impostazione. |
| Filtrare via i mercati non preferiti | Nasconde alternative utili e fa sembrare assente uno strumento disponibile. |
| Riscrivere all'apertura i simboli del portafoglio | Cambia silenziosamente identità, storia e fonte dati di una posizione. |
| Ordinare direttamente dentro ogni provider | Produce regole divergenti e lega la cache a una preferenza locale. |
| Dare precedenza a Milano perché è usato da Directa | Renderebbe una funzione generale dipendente da un intermediario. |

## Rischi

- I codici di mercato non sono uniformi fra fonti: fixture per alias equivalenti
  intercettano duplicati e normalizzazioni errate.
- Due strumenti possono condividere un nome ma non l'identità: il raggruppamento
  usa ISIN quando disponibile e non fonde per il solo nome.
- Un cambio di preferenza può sembrare un cambio di strumento: la UI mantiene
  visibili simbolo, valuta e mercato e non modifica selezioni già confermate.
- Le preferenze precedenti non contengono il nuovo campo: il caricamento usa un
  valore iniziale deciso prima dell'implementazione e degrada senza errore.

## Verifica

1. Chiudere le domande aperte e aggiornare lo stato della spec ad approvata.
2. Eseguire `uv run python -m unittest tests.test_markets tests.test_registry tests.test_prefs tests.test_portfolio_io`.
3. Eseguire `uv run python -m unittest discover -s tests -p "test_*.py"`.
4. Eseguire `uv run ruff check .`.
5. Provare una ricerca per ISIN con quotazioni Milano, Xetra e mercato ignoto,
   cambiare ordine e verificare che non parta una nuova richiesta di rete.
6. Importare un portafoglio con simbolo esatto non preferito e verificare che
   ricerca, salvataggio e backtest continuino a usare quel simbolo.
7. Ispezionare manualmente i gruppi in tutte le lingue, distinguendo mercato,
   valuta ed esposizione geografica.
