# Memory bank

La memoria di progetto: **perché** le cose sono come sono.

Il codice di questo repository spiega già molto di sé — i commenti raccontano
le ragioni, non le righe. Ma quelle ragioni sono sparse fra un commento in
`covip.py`, un messaggio di commit di tre mesi fa e una riga del README. Il
memory bank le raccoglie in un posto solo, così chi arriva (o chi torna dopo
un mese) non deve ricostruirle leggendo `git log`.

## I file

| File | Cosa contiene | Quanto cambia |
|---|---|---|
| [`00-panoramica.md`](00-panoramica.md) | Cosa fa il progetto, per chi, cosa **non** fa, glossario | Raramente |
| [`01-architettura.md`](01-architettura.md) | Come è fatto: moduli, flusso dei dati, CI, bundle | Quando cambia la struttura |
| [`02-decisioni.md`](02-decisioni.md) | Registro delle decisioni prese, con il loro perché | Solo per decisioni vincolanti |
| [`03-stato-attuale.md`](03-stato-attuale.md) | Dove siamo adesso, cosa è aperto, prossimi passi | Spesso — è il file da leggere per primo |

## Come si aggiorna

- **`03-stato-attuale.md`**: a fine di ogni lavoro che cambia qualcosa di
  visibile. Sostituisci, non accumulare: è una fotografia del presente, non un
  diario.
- **`02-decisioni.md`**: solo quando una scelta **vincola il lavoro futuro** —
  "d'ora in poi si fa così, e ecco perché l'alternativa è stata scartata". Non
  una voce per commit. Le voci non si cancellano: una decisione superata si
  marca come tale, con il rimando a quella che l'ha sostituita.
- **`00-` e `01-`**: quando la realtà che descrivono cambia, non prima.

Se una decisione è già spiegata da un commento nel codice, il memory bank la
**cita** invece di riscriverla: la duplicazione invecchia male, il rimando no.
