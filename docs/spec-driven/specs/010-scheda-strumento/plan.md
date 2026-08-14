# 010 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Introdurre un modello normalizzato per i fatti descrittivi, separato sia
dall'identità della quotazione sia dallo stato della UI. Ogni fatto conserva
valore, fonte, data e qualità. Il registro fonde le risposte dei provider campo
per campo applicando una gerarchia esplicita, senza perdere i conflitti e senza
sovrascrivere valori manuali o da KID.

La UI presenta la scheda come vista riusabile dalla ricerca e dal portafoglio.
Le sezioni non disponibili restano leggibili e un errore di acquisizione non
interrompe il flusso principale.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/instrument_facts.py` | Nuovi modelli per fatti, provenienza, data, stato e conflitti; fusione per campo. |
| `comparatore/sources/base.py` | Collega allo strumento i fatti normalizzati persistibili ed estende in modo compatibile il contratto opzionale dei provider. |
| `comparatore/sources/registry.py` | Raccoglie i fatti dai provider e applica le priorità esistenti. |
| `comparatore/sources/yahoo.py` | Mappa soltanto i campi realmente disponibili e ne registra la provenienza. |
| `comparatore/sources/justetf.py` | Espone i metadati ammessi mantenendo consenso esplicito e priorità del TER. |
| `comparatore/portfolio_io.py` | Importa ed esporta i soli fatti persistibili, mantenendo compatibili i JSON precedenti. |
| `app.py` | Aggiunge la scheda riusabile, gli stati incompleti e l'azione di nuovo tentativo. |
| `comparatore/locales/it.py` | Testi italiani della scheda e delle fonti. |
| `comparatore/locales/en.py` | Traduzioni inglesi. |
| `comparatore/locales/fr.py` | Traduzioni francesi. |
| `comparatore/locales/de.py` | Traduzioni tedesche. |
| `tests/test_instrument_facts.py` | Copre normalizzazione, priorità, conflitti e campi mancanti. |
| `tests/test_portfolio_io.py` | Copre round-trip e retrocompatibilità del JSON. |
| `tests/test_app_sintassi.py` | Aggiunge una guardia sorgente per l'accesso alla scheda dai due flussi. |
| `tests/test_i18n.py` | Continua a garantire la parità dei quattro cataloghi. |

Si riusano i metadati e la provenienza TER già presenti; non si introduce una
seconda pipeline parallela per gli stessi dati.

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Aggiungere tutti i campi direttamente a `Instrument` senza metadati | Perderebbe fonte, data, stato e conflitti e renderebbe ambigua la precedenza. |
| Mostrare il primo valore non vuoto restituito dai provider | L'ordine di rete deciderebbe il risultato e potrebbe sovrascrivere KID o dati manuali. |
| Rendere obbligatoria una fonte commerciale | Non rispetta il limite di costo e renderebbe fragile l'uso locale. |
| Nascondere le sezioni incomplete | Farebbe apparire completo un dato che non lo è. |

## Rischi

- Provider diversi possono usare unità o semantiche differenti: fixture con
  conflitti verificano la normalizzazione e impediscono fusioni implicite.
- Salvare troppi dati nel portafoglio può produrre snapshot obsoleti: si
  persiste solo il valore utile con fonte e data, mai la cache o gli errori.
- La scheda può diventare troppo densa: sezioni progressive e campi non
  disponibili compatti ne preservano la leggibilità.
- Un provider può cambiare il proprio schema: il parsing resta isolato e il
  fallimento è rappresentato come stato non bloccante.

## Verifica

1. Eseguire `uv run python -m unittest tests.test_instrument_facts tests.test_portfolio_io`.
2. Eseguire `uv run python -m unittest discover -s tests -p "test_*.py"`.
3. Eseguire `uv run ruff check .`.
4. Provare una scheda completa, una con campi mancanti e una con conflitto fra
   fonte automatica e KID/manuale.
5. Importare un JSON precedente, riesportarlo e verificare che simbolo e mercato
   selezionati non cambino.
6. Simulare il fallimento di un provider e verificare che ricerca e backtest
   restino utilizzabili.

## Evidenza di chiusura

- Controllo end-to-end nell'app: la ricerca mostra il pulsante `Scheda` e apre
  il dialogo largo con sezioni, fonti, campi mancanti, azione di aggiunta e
  retry; il dialogo usa le stesse funzioni del portafoglio.
- Suite completa: 237 test `unittest`, Ruff, `git diff --check` e smoke
  Streamlit su sessione pulita superati.
- La verifica dei casi completi/conflittuali e delle quattro lingue resta
  coperta dalle fixture provider e dalla parità dei cataloghi; non si sono
  aggiunte chiamate provider oltre a quelle gia' presenti.
