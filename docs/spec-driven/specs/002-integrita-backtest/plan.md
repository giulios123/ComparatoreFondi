# 002 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Il motore diventa l'ultima barriera: `run_backtest` e `simulate` rifiutano
esplicitamente prezzi non finiti/non positivi, holding duplicati o non coperti
da colonne prezzi, pesi non validi — invece di lasciarli passare per
`np.nan_to_num` o per una rinormalizzazione implicita. Il simbolo resta la
chiave interna delle colonne per tutto il calcolo (mai più il nome visuale);
l'etichetta univoca da mostrare a video arriva come mappa separata nel
risultato.

In `app.py`, prima di costruire gli `Holding` si controlla che ogni fondo
selezionato abbia una colonna prezzi risolta. Se manca qualcosa: errore
bloccante con l'elenco e l'allocazione che si otterrebbe rimuovendoli, un
bottone che li rimuove davvero (riusando lo schema di `rimuovi_fondo`), `stop`.
Nessun filtro silenzioso: da qui in avanti "i fondi selezionati" e "i fondi
simulati" sono sempre lo stesso insieme.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/engine.py` | Nuova `BacktestInputError(ValueError)`; nuove `valida_prezzi()`, `valida_holdings()`, `etichette_uniche()`; `simulate` e `run_backtest` le chiamano; rimosso `np.nan_to_num` in `simulate`; `run_backtest` non rinomina più le colonne con l'etichetta, popola `BacktestResult.labels` invece di rinominare `per_fund`/`per_fund_gross`/`per_fund_nav`/`contributions` |
| `app.py` | Guardia bloccante prima della costruzione degli `Holding` (usa `pesi.rinormalizza`, già esistente); nuova `rimuovi_fondi_assenti()` accanto a `rimuovi_fondo()`; tolto il filtro `if f["symbol"] in prices.columns`; ogni lettura di colonna/etichetta per nome passa da `res.labels`; nuovo `except BacktestInputError` che traduce `exc.kind` |
| `comparatore/locales/{it,en,fr,de}.py` | Chiavi nuove: `engine.error_*` (una per `kind`), `integrita.error_fondi_assenti`, `integrita.allocazione_reale`, `integrita.button_rimuovi` |
| `tests/test_engine.py` | Casi per ogni validazione, più il caso "label duplicata + PAC" che riproduce il finding e deve passare |
| `tests/test_app_sintassi.py` | Guardia che la nuova strozzatura precede `run_backtest`; guardia che `app.py` usa `res.labels` e non contiene più `label_splice` derivato dall'etichetta |
| `docs/memory-bank/03-stato-attuale.md`, `02-decisioni.md` | Chiusura del lavoro, decisione 21 |

Riuso esplicito: `pesi.rinormalizza()` (già scritto per il caso "rimozione
fondo", stesso identico bisogno qui), `rimuovi_fondo()` come modello per
`rimuovi_fondi_assenti()`, `assicura_alloc()` per non duplicare la costruzione
dei fondi.

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Avviso non bloccante con pesi effettivi mostrati esplicitamente | Non risolve il finding: un risultato su un portafoglio diverso resta raggiungibile senza conferma esplicita — è esattamente il comportamento che l'audit segnala come pericoloso. |
| Bloccare senza pulsante, lasciando che l'utente rimuova i fondi a mano dall'editor esistente | Più semplice ma più attrito: l'utente deve già sapere quali simboli sono falliti e tornare su un'altra sezione dell'interfaccia per farlo. |
| Sostituire i prezzi non validi con l'ultimo valore buono (`ffill` più aggressivo) invece di rifiutarli | Nasconde il problema anziché segnalarlo: una quota a zero per un giorno intero è quasi sempre un errore di fonte, non un dato vero da colmare silenziosamente. |
| Tenere l'etichetta come chiave delle colonne e deduplicare solo quando serve (rilevamento a runtime nel punto del rename) | Il bug richiederebbe la stessa logica di disambiguazione in più punti sparsi di `app.py`; centralizzarla in `run_backtest` (che già conosce simbolo ed etichetta insieme) è più semplice e copre anche `contributions`. |
| Una `spec` per punto (fondi mancanti, quote non valide, label duplicate) | I tre cambiano lo stesso percorso (`run_backtest` → editor di composizione) e si verificano con lo stesso backtest di prova; separarli avrebbe solo moltiplicato le cartelle senza isolare davvero il lavoro. |

## Rischi

- **Rottura dei test esistenti che assumono `label == symbol`.** Con la chiave
  che resta il simbolo, quei test dovrebbero restare verdi senza modifiche
  (è la non-regressione prevista); si esegue la suite per confermarlo prima di
  aggiungere i test nuovi.
- **Punti di lettura di `res.per_fund`/`res.contributions` in `app.py` non
  individuati.** Mitigato enumerando ogni occorrenza prima di modificare (già
  fatto in fase di esplorazione: righe 1261-1266, 1512-1536, 1751-1798,
  1868-1911) e dalla guardia AST che verifica l'assenza di `label_splice`.
- **Messaggi d'errore che restano in italiano fisso invece di passare da
  `t()`.** Il messaggio dentro `BacktestInputError` è per l'uso da script; a
  video passa sempre dalla traduzione in `app.py`, non dal messaggio
  dell'eccezione — va controllato a mano che nessun punto mostri
  `str(exc)` direttamente per il nuovo tipo di errore.

## Verifica

1. `uv run python -m unittest discover -s tests -p "test_*.py"` — tutti i test
   esistenti restano verdi, i nuovi passano.
2. `uv run ruff check .` pulito.
3. `uv run streamlit run app.py`, via CSV offline (nessuna rete verso le
   fonti):
   - un fondo con simbolo non risolvibile → backtest bloccato, elenco e
     allocazione mostrati, il bottone rimuove e fa ripartire il calcolo con i
     pesi tornati a 100 (criteri 1-2);
   - un CSV con una riga a prezzo zero o negativo → errore che nomina il
     simbolo, nessun grafico (criterio 3);
   - due CSV con lo stesso nome fondo, PAC acceso → backtest completo,
     legenda con etichette distinte (criterio 4);
   - un portafoglio a due fondi con dati completi e nomi distinti → stessi
     numeri di prima del cambiamento (criterio 5, confrontato a mano prima e
     dopo).
