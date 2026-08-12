# 005 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [ ] Implementare fonte e risultato HICP in `comparatore/inflation.py`.
- [ ] Aggiungere cache, diagnostica e riprova senza bloccare il backtest.
- [ ] Implementare deflazione di NAV, saldo e versato.
- [ ] Aggiungere opt-in e area geografica alle preferenze locali.
- [ ] Mostrare confronto nominale/reale e copertura temporale.
- [ ] Aggiungere tutte le stringhe ai quattro cataloghi.

## Test

- [ ] Parsing di fixture Eurostat e cambio di base dell'indice.
- [ ] Inflazione nulla, positiva e storico parziale.
- [ ] PAC: saldo, versato e NAV reale.
- [ ] Errori di rete/parsing e cache locale.
- [ ] Persistenza preferenze e guardie di `app.py` se necessarie.

## Verifica dei criteri di accettazione

- [ ] 1 · funzione opt-in, nominale invariato.
- [ ] 2 · scelta area con Italia e area euro.
- [ ] 3 · fonte e ultimo mese visibili, nessuna previsione.
- [ ] 4 · curve e metriche reali affiancate.
- [ ] 5 · PAC deflazionato senza falsare i rendimenti.
- [ ] 6 · copertura parziale dichiarata, nessun retro-riempimento.
- [ ] 7 · errore Eurostat non bloccante e riprovabile.
- [ ] 8 · cache e preferenza locali.
- [ ] 9 · fixture offline e quattro lingue.

## Chiusura

- [ ] Suite unittest, ruff e `git diff --check` passano
- [ ] Verifica Streamlit nominale/reale con e senza PAC
- [ ] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [ ] Aggiunta una decisione a `docs/memory-bank/02-decisioni.md`
- [ ] Aggiornato lo stato in cima a `spec.md`
