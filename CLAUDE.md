# CLAUDE.md

Le istruzioni di progetto vivono in un file solo, condiviso con gli altri
strumenti. Leggilo per primo:

@AGENTS.md

Qui sotto solo ciò che riguarda specificamente Claude Code.

## A inizio sessione

Leggi `docs/memory-bank/03-stato-attuale.md`: dice a che punto è il progetto,
cosa è appena entrato e cosa è noto ma non ancora risolto. Gli altri file del
memory bank si consultano quando servono, non a tappeto.

## Durante il lavoro

- **Feature o cambio di comportamento visibile** ⇒ apri prima una spec sotto
  `docs/spec-driven/specs/`, seguendo `docs/spec-driven/README.md`. Il codice
  viene dopo il piano, non prima.
- **Correzioni piccole e refactor a parità di comportamento** ⇒ direttamente,
  senza spec.
- Un cambiamento strutturale ad `app.py` va accompagnato dalla sua guardia in
  `tests/test_app_sintassi.py`: è l'unico file che protegge l'interfaccia.
- Per provare l'app davvero (non solo i test) senza rete verso le fonti dati:
  carica una serie da CSV e importa un portafoglio JSON. Entrambe le strade
  sono offline e portano fino al backtest completo.

## A fine lavoro

Aggiorna `docs/memory-bank/03-stato-attuale.md`, e aggiungi una voce a
`docs/memory-bank/02-decisioni.md` **solo** se hai preso una decisione che
vincola il lavoro futuro — non per ogni commit.
