# 011 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

Ogni voce è spuntabile guardando qualcosa. Se non lo è, non è un'attività.

## Decisioni preliminari

- [ ] Decidere l'ordine iniziale per una nuova installazione.
- [ ] Decidere i criteri di spareggio dopo la preferenza di mercato.
- [ ] Decidere ampiezza e presentazione del catalogo iniziale.
- [ ] Rimuovere le domande aperte e approvare la spec.

## Implementazione

- [ ] Centralizzare mercati, alias e funzione di ordinamento in
      `comparatore/markets.py`.
- [ ] Normalizzare i mercati restituiti da OpenFIGI, EODHD e Yahoo.
- [ ] Raggruppare le quotazioni per identità senza fondere strumenti omonimi.
- [ ] Applicare la preferenza solo a ricerca generica e proposta per ISIN.
- [ ] Persistire l'elenco ordinato in `prefs.py` con compatibilità precedente.
- [ ] Aggiungere selezione ricercabile, riordino e gruppi di risultati alla UI.
- [ ] Aggiungere le chiavi ai quattro cataloghi.

## Test

- [ ] Coprire alias equivalenti, mercati ignoti e ordine deterministico.
- [ ] Coprire ricerca generica, per ISIN e per simbolo esatto.
- [ ] Coprire persistenza e migrazione delle preferenze.
- [ ] Coprire la conservazione del simbolo nei JSON esistenti.
- [ ] Aggiungere le guardie sorgente necessarie per `app.py`.

## Verifica dei criteri di accettazione

- [ ] 1 · L'elenco dei mercati è ricercabile, ordinabile e modificabile.
- [ ] 2 · Le quotazioni sono raggruppate e tutte restano consultabili.
- [ ] 3 · Simbolo, mercato e valuta sono distinti dall'esposizione geografica.
- [ ] 4 · La preferenza non cambia simboli esatti, importati o salvati.
- [ ] 5 · Il ripiego è stabile e conserva i mercati ignoti.
- [ ] 6 · Cambiare ordine riusa la cache grezza senza rete.
- [ ] 7 · Preferenze e portafoglio restano separati e retrocompatibili.
- [ ] 8 · Alias delle fonti sono centralizzati e non duplicano gruppi.
- [ ] 9 · Non esistono dipendenze da Directa o dati commerciali di liquidità.
- [ ] 10 · Quattro lingue e test coprono il comportamento.

## Chiusura

- [ ] `uv run python -m unittest discover -s tests -p "test_*.py"` passa
- [ ] `uv run ruff check .` passa
- [ ] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [ ] Aggiunta una voce a `docs/memory-bank/02-decisioni.md` *(solo se è stata
      presa una decisione vincolante)*
- [ ] Aggiornato lo stato in cima a `spec.md`
