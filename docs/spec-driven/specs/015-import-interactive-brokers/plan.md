# 015 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Creare un parser puro per il CSV a sezioni IBKR. Il parser individua le sezioni
tramite la firma delle intestazioni, normalizza le sole posizioni Summary,
collega l'anagrafica strumenti e restituisce diagnosi, valuta base, data finale,
totali e gli eventuali cambi ricavabili dai totali IBKR.

L'interfaccia riusa la risoluzione delle quotazioni e la costruzione dei fondi
gia' usate da Directa, ma con `funds_only=False`. Per i file grandi conserva gli
esiti in sessione e mostra una scelta manuale soltanto per le eccezioni. La
conversione dei controvalori avviene prima di `pesi.rinormalizza()`; il portafoglio
modello viene sostituito solo con il pulsante di conferma.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/ibkr_io.py` | Parser, modelli normalizzati, diagnosi, totali e cambi ricavabili. |
| `comparatore/fx.py` | Helper per il cambio disponibile alla data richiesta, con fonte. |
| `app.py` | Stato upload, expander IBKR, risoluzione, override FX, anteprima e import atomico. |
| `comparatore/locales/*.py` | Etichette, avvertenze e messaggi nelle quattro lingue. |
| `tests/fixtures/ibkr_statement.csv` | Fixture sintetica a sezioni, senza dati personali. |
| `tests/test_ibkr_io.py` | Parser, join, Summary/Lot, valute e diagnosi. |
| `tests/test_fx.py` | Cambio alla data e fallback gia' compatibili. |
| `tests/test_app_sintassi.py` | Guardie per ordine UI, risoluzione e sostituzione dello stato. |
| `docs/memory-bank/02-decisioni.md` | Decisione sull'import IBKR e sulla valuta. |
| `docs/memory-bank/03-stato-attuale.md` | Stato della feature e copertura dei test. |

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Passare il rendiconto a `directa_io.read_table()` | Le sezioni hanno righe con larghezze diverse. |
| Usare tutto il CSV come storico transazioni | La richiesta riguarda la fotografia corrente; il registro e' la spec 012. |
| Usare solo il cambio corrente | Disallinea la data del rendiconto e rende il peso non riconciliabile. |
| Importare la cassa come fondo | Il motore attuale non rappresenta una sleeve cash separata. |
| Mostrare una selezione per ogni posizione | Un rendiconto reale puo' avere centinaia di righe e diventa inutilizzabile. |

## Verifica

1. Fixture italiana e inglese con righe Summary, Lot, Total e anagrafica.
2. Test di parsing irregolare, join, valori negativi, short, duplicati e campi mancanti.
3. Test di cambio ricavabile con una valuta estera, fallback FX mockato,
   override manuale e riconciliazione non accettata.
4. Test di import con `funds_only=False`, esclusione esplicita e sostituzione
   atomica del portafoglio.
5. Eseguire unittest completo, Ruff, `git diff --check` e smoke Streamlit con
   fixture offline. Il campione reale viene verificato manualmente senza salvarlo.
