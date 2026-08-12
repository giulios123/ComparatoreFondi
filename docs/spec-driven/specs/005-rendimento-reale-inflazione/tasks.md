# 005 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [x] Implementare fonte e risultato HICP in `comparatore/inflation.py`.
- [x] Aggiungere cache, diagnostica e riprova senza bloccare il backtest.
- [x] Implementare deflazione di NAV, saldo e versato.
- [x] Aggiungere opt-in e area geografica alle preferenze locali.
- [x] Mostrare confronto nominale/reale e copertura temporale.
- [x] Aggiungere tutte le stringhe ai quattro cataloghi.

## Test

- [x] Parsing di fixture Eurostat e cambio di base dell'indice.
- [x] Inflazione nulla, positiva e storico parziale.
- [x] PAC: saldo, versato e NAV reale.
- [x] Errori di rete/parsing e cache locale.
- [x] Persistenza preferenze e guardie di `app.py` se necessarie.

## Verifica dei criteri di accettazione

- [x] 1 · funzione opt-in, nominale invariato.
- [x] 2 · scelta area con Italia e area euro.
- [x] 3 · fonte e ultimo mese visibili, nessuna previsione.
- [x] 4 · curve e metriche reali affiancate.
- [x] 5 · PAC deflazionato senza falsare i rendimenti.
- [x] 6 · copertura parziale dichiarata, nessun retro-riempimento.
- [x] 7 · errore Eurostat non bloccante e riprovabile.
- [x] 8 · cache e preferenza locali.
- [x] 9 · fixture offline e quattro lingue.

## Chiusura

- [x] Suite unittest, ruff e `git diff --check` passano
- [x] Verifica Streamlit nominale/reale con e senza PAC
- [x] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [x] Aggiunta una decisione a `docs/memory-bank/02-decisioni.md`
- [x] Aggiornato lo stato in cima a `spec.md`
