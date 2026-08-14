# 010 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

Ogni voce è spuntabile guardando qualcosa. Se non lo è, non è un'attività.

## Implementazione

- [x] Definire fatti, provenienza, data, stato e conflitto in
      `comparatore/instrument_facts.py`.
- [x] Implementare la fusione campo per campo con protezione di valori manuali
      e KID e consenso justETF invariato.
- [x] Collegare i fatti persistibili a `Instrument` senza cambiare l'identità
      della quotazione.
- [x] Estendere in modo opzionale il contratto provider e mappare i campi
      disponibili da Yahoo e justETF.
- [x] Rendere retrocompatibili import ed export del portafoglio.
- [x] Aggiungere la scheda a ricerca e portafoglio con sezioni incomplete,
      conflitti e nuovo tentativo.
- [x] Aggiungere tutte le nuove chiavi ai quattro cataloghi.

## Test

- [x] Coprire normalizzazione, provenienza, priorità, conflitti e dati mancanti.
- [x] Coprire round-trip dei nuovi fatti e import di JSON senza la nuova sezione.
- [x] Coprire con guardia sorgente l'accessibilità della scheda dai due flussi.
- [x] Verificare la parità delle traduzioni.

## Verifica dei criteri di accettazione

- [x] 1 · La scheda si apre sia dalla ricerca sia da uno strumento in portafoglio.
- [x] 2 · Identità economica e quotazione sono distinte e il simbolo non cambia.
- [x] 3 · I metadati minimi esistenti compaiono in un'unica vista.
- [x] 4 · I campi aggiuntivi disponibili sono mostrati e quelli assenti non sono inferiti.
- [x] 5 · Valore, fonte, data e conflitti sono visibili per i dati variabili.
- [x] 6 · Manuale e KID restano protetti e justETF resta opt-in.
- [x] 7 · Le quotazioni collegate sono visibili senza sostituzione automatica.
- [x] 8 · Un provider in errore non blocca ricerca o backtest e può essere ritentato.
- [x] 9 · Il JSON resta retrocompatibile e non esporta stati transitori.
- [x] 10 · Le fonti rispettano costo, consenso e trasparenza stabiliti.
- [x] 11 · Quattro lingue e test automatici sono completi.

## Chiusura

- [x] `uv run python -m unittest discover -s tests -p "test_*.py"` passa (237 test)
- [x] `uv run ruff check .` passa
- [x] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [ ] Aggiunta una voce a `docs/memory-bank/02-decisioni.md` *(solo se è stata
      presa una decisione vincolante)*
- [x] Aggiornato lo stato in cima a `spec.md`
