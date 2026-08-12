# 006 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Creare un modulo puro che normalizza le holdings gia' presenti negli
`Instrument`, conserva identita', quota e fonte e produce tre risultati:
copertura per fondo, overlap a coppie e esposizione aggregata del portafoglio.

Per due fondi, l'overlap osservato e' la somma di `min(quota_a, quota_b)` per
ogni partecipazione riconosciuta in entrambi. Le quote originali non vengono
riscalate. Per il portafoglio, ogni posizione contribuisce con
`peso_fondo * quota_posizione`; la differenza rispetto al 100% e' la parte non
coperta dai dati disponibili.

Il matching prova nell'ordine identificatore stabile, simbolo normalizzato e
nome normalizzato univoco. Un nome che collassa piu' simboli resta ambiguo e
viene segnalato invece di fondere righe.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/overlap.py` | Modelli normalizzati, copertura, matching, overlap e aggregazione |
| `comparatore/sources/base.py` | Identificatore opzionale e data delle holdings, senza rendere obbligatori i nuovi campi |
| `comparatore/sources/yahoo.py` | Popolamento dei campi disponibili e provenienza |
| `comparatore/portfolio_io.py` | Backfill e persistenza compatibile dei nuovi metadati opzionali |
| `app.py` | Matrice, dettaglio coppie, concentrazione aggregata e avvisi di copertura |
| `comparatore/locales/{it,en,fr,de}.py` | Etichette e spiegazioni del limite inferiore |
| `tests/test_overlap.py` | Matching, formule, copertura e ambiguita' |
| `tests/test_portfolio_io.py` | Compatibilita' dei JSON precedenti |

Riuso esplicito: holdings gia' raccolte da Yahoo, pesi normalizzati del
portafoglio e convenzioni `NON_CLASSIFICATO`/provenienza di `allocazione.py`.

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Rinormalizzare le top 10 al 100% | Fa sembrare che una porzione del fondo sia l'intero fondo e gonfia l'overlap |
| Usare soltanto il nome della societa' | Suffissi, classi azionarie e omonimie producono fusioni errate |
| Mostrare zero quando mancano holdings | Confonde "nessun dato" con "nessuna sovrapposizione" |
| Chiedere all'AI di riconciliare i nomi | Il risultato diventerebbe variabile e non verificabile |
| Integrare subito file holdings di ogni emittente | Formati e termini diversi allargherebbero la prima versione prima di validarne l'utilita' |

## Rischi

- I simboli delle holdings possono cambiare tra borse: il fallback non deve
  fingere un identificatore globale.
- Dati datati possono descrivere portafogli non piu' correnti: la data va
  mostrata quando disponibile.
- Una matrice fitta diventa illeggibile: dettaglio e ordinamento devono
  privilegiare le coppie con maggiore overlap e copertura.
- La somma nota del portafoglio non deve essere presentata come concentrazione
  totale: il residuo sconosciuto e' parte del risultato.

## Verifica

1. Fondi sintetici con holdings complete e overlap noto.
2. Holdings parziali: overlap non rinormalizzato e quota sconosciuta corretta.
3. Simboli uguali, nomi varianti e collisioni ambigue.
4. Fondo privo di holdings: `n/d`, backtest invariato.
5. Round-trip JSON precedente e nuovo.
6. Unittest, ruff, `git diff --check` e smoke della matrice in quattro lingue.
