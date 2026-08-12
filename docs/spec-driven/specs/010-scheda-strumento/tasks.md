# 010 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

Ogni voce è spuntabile guardando qualcosa. Se non lo è, non è un'attività.

## Implementazione

- [ ] Definire fatti, provenienza, data, stato e conflitto in
      `comparatore/instrument_facts.py`.
- [ ] Implementare la fusione campo per campo con protezione di valori manuali
      e KID e consenso justETF invariato.
- [ ] Collegare i fatti persistibili a `Instrument` senza cambiare l'identità
      della quotazione.
- [ ] Estendere in modo opzionale il contratto provider e mappare i campi
      disponibili da Yahoo e justETF.
- [ ] Rendere retrocompatibili import ed export del portafoglio.
- [ ] Aggiungere la scheda a ricerca e portafoglio con sezioni incomplete,
      conflitti e nuovo tentativo.
- [ ] Aggiungere tutte le nuove chiavi ai quattro cataloghi.

## Test

- [ ] Coprire normalizzazione, provenienza, priorità, conflitti e dati mancanti.
- [ ] Coprire round-trip dei nuovi fatti e import di JSON senza la nuova sezione.
- [ ] Coprire con guardia sorgente l'accessibilità della scheda dai due flussi.
- [ ] Verificare la parità delle traduzioni.

## Verifica dei criteri di accettazione

- [ ] 1 · La scheda si apre sia dalla ricerca sia da uno strumento in portafoglio.
- [ ] 2 · Identità economica e quotazione sono distinte e il simbolo non cambia.
- [ ] 3 · I metadati minimi esistenti compaiono in un'unica vista.
- [ ] 4 · I campi aggiuntivi disponibili sono mostrati e quelli assenti non sono inferiti.
- [ ] 5 · Valore, fonte, data e conflitti sono visibili per i dati variabili.
- [ ] 6 · Manuale e KID restano protetti e justETF resta opt-in.
- [ ] 7 · Le quotazioni collegate sono visibili senza sostituzione automatica.
- [ ] 8 · Un provider in errore non blocca ricerca o backtest e può essere ritentato.
- [ ] 9 · Il JSON resta retrocompatibile e non esporta stati transitori.
- [ ] 10 · Le fonti rispettano costo, consenso e trasparenza stabiliti.
- [ ] 11 · Quattro lingue e test automatici sono completi.

## Chiusura

- [ ] `uv run python -m unittest discover -s tests -p "test_*.py"` passa
- [ ] `uv run ruff check .` passa
- [ ] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [ ] Aggiunta una voce a `docs/memory-bank/02-decisioni.md` *(solo se è stata
      presa una decisione vincolante)*
- [ ] Aggiornato lo stato in cima a `spec.md`
