# Sviluppo spec-driven

Fino alla v0.2 le funzionalità sono nate direttamente come codice. Funziona
finché il contesto sta in testa a una persona sola; smette di funzionare quando
il lavoro si distribuisce fra sessioni diverse, o fra una persona e un agente.

Il flusso qui descritto separa **cosa serve** da **come lo si fa**, e mette per
iscritto il primo prima di aver deciso il secondo.

## Il flusso

```
   spec.md  ──▶  plan.md  ──▶  tasks.md  ──▶  codice  ──▶  verifica
   cosa e            come,          checklist                 contro i
   perché            e cosa si      eseguibile                criteri della
                     scarta                                   spec
```

**1 · `spec.md` — cosa serve, e perché.**
Il problema, chi lo incontra, e **criteri di accettazione osservabili**: cose
che si possono guardare e dire sì o no, senza aprire il codice. Include i
non-obiettivi, che sono metà del valore di una spec.
Regola dura: **nessuna soluzione tecnica**. Se scrivendo la spec ti viene in
mente come si fa, appuntalo nel piano, non qui.

**2 · `plan.md` — come.**
L'approccio scelto, i file che verranno toccati, le **alternative scartate con
il motivo** (è la parte che serve fra sei mesi), i rischi e come si verifica.

**3 · `tasks.md` — la checklist.**
Passi eseguibili, ciascuno verificabile. Se un passo non si può spuntare
guardando qualcosa, non è un passo: è un'intenzione.

**4 · Codice, poi verifica.**
Si implementa seguendo `tasks.md`, e alla fine si ripercorrono i criteri di
accettazione della spec **uno per uno**. Un criterio non verificabile in
quell'ambiente si dichiara tale — non si dà per buono.

**5 · Memory bank.**
A lavoro finito si aggiorna `docs/memory-bank/03-stato-attuale.md`. Se lungo la
strada è stata presa una decisione che vincola il futuro, si aggiunge una voce a
`02-decisioni.md` — con il rimando alla spec.

## Quando serve una spec

**Sì:**
- una funzionalità nuova;
- un cambio di comportamento visibile all'utente (anche piccolo: il fix dei
  pulsanti che andavano a capo è la spec `001`);
- una scelta che vincola il futuro, anche se il codice è poco.

**No:**
- refusi, rinomine, riordini;
- refactor a parità di comportamento;
- aggiornamenti di dipendenze;
- correzione di un bug che tradisce un comportamento già specificato altrove —
  lì la spec c'è già, è il comportamento atteso.

Nel dubbio: se qualcuno fra sei mesi potrebbe chiedersi *"perché è fatto
così?"*, serve una spec.

## Convenzioni

```
docs/spec-driven/
├── README.md                     questo file
├── templates/                    spec.md · plan.md · tasks.md
└── specs/
    └── NNN-slug-breve/           numerazione progressiva, mai riusata
        ├── spec.md
        ├── plan.md
        └── tasks.md
```

- **Una cartella per spec, una spec per branch.** Il numero della spec entra nel
  nome del branch (`feat/001-preset-periodo-nowrap`) e nel corpo del messaggio
  di commit, così dal `git log` si risale sempre al perché.
- **Le spec non si cancellano.** Una spec abbandonata resta, con scritto in cima
  che è stata abbandonata e perché: è informazione, non spazzatura.
- **Le spec si scrivono in italiano**, come il resto della documentazione e dei
  commenti.

## Esempio da leggere

[`specs/001-preset-periodo-nowrap/`](specs/001-preset-periodo-nowrap/spec.md) —
la prima spec, scritta ed eseguita con questo processo. È piccola apposta: serve
a mostrare la forma, non a impressionare.
