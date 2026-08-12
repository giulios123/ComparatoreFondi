# 008 · Profilo locale e diagnosi anonima del portafoglio

*Stato: implementata — 12 agosto 2026*

## Problema

Le stesse metriche non hanno lo stesso significato per ogni persona. Una
perdita storica del 30%, una posizione al 45% o un orizzonte di cinque anni
possono essere accettabili per un utente e incompatibili con gli obiettivi di
un altro. Senza un contesto locale, indicazioni esplicite diventerebbero frasi
generiche o assumerebbero preferenze mai dichiarate.

Inoltre l'eventuale interprete Copilot non deve ricevere nomi, ISIN, ticker o
patrimonio. Serve quindi un rapporto deterministico che separi i fatti del
portafoglio dalla loro presentazione e sappia produrre una forma anonima
ispezionabile prima di qualunque invio.

## Chi lo incontra

Chi vuole capire quali aspetti del proprio portafoglio meritino attenzione e,
in seguito, ricevere spiegazioni coerenti con orizzonte e tolleranza alle
perdite senza trasferire dati identificativi a un modello esterno.

## Criteri di accettazione

1. Un profilo facoltativo e locale raccoglie almeno: orizzonte in anni,
   obiettivo (crescita/reddito/conservazione), perdita temporanea massima
   tollerata, presenza di prelievi, limite per singola posizione, preferenza
   fra semplicita' e diversificazione, disponibilita' a detenere obbligazioni
   ed eventuali esclusioni.
2. Il profilo e' salvato fuori da cache e portafogli, con permessi ristretti;
   non entra nell'export JSON e cancellarlo non modifica il portafoglio.
3. In assenza di profilo il rapporto descrive fatti e limiti dei dati, ma non
   presenta come personale una soglia predefinita. Le indicazioni dipendenti
   dalle preferenze spiegano quale campo manca.
4. Un motore deterministico produce rilievi strutturati con codice, gravita',
   evidenze numeriche, periodo/fonte, limiti e azioni di simulazione possibili.
   Lo stesso input produce sempre lo stesso rapporto.
5. Il rapporto usa, quando disponibili, costi e provenienza, benchmark,
   correlazioni, rolling return, inflazione e overlap; l'assenza di una spec
   precedente non viene trasformata in zero o in un giudizio positivo.
6. La forma anonima sostituisce ogni strumento con identificatori temporanei
   (`asset_1`, `asset_2`), elimina nomi, simboli, ISIN, importi assoluti,
   percorsi locali, nomi file e credenziali e conserva soltanto percentuali,
   metriche e durate necessarie.
7. Prima di ogni uso esterno l'utente puo' vedere integralmente il payload
   anonimo; esiste un test che fallisce se vi compaiono chiavi o valori
   identificativi vietati.
8. Il rapporto propone soltanto azioni verificabili nell'app, come confrontare
   uno scenario, ridurre/aumentare un peso ipotetico o controllare un dato
   mancante; non esegue ordini e non prevede rendimenti futuri.
9. Profilo, diagnosi, anonimizzazione e compatibilita' dei file locali sono
   testati senza Streamlit; la UI e' disponibile nelle quattro lingue.

## Non-obiettivi

- Chiamare Copilot o un altro provider: e' la spec 009.
- Valutazione MiFID formale o certificazione di adeguatezza.
- Raccolta di reddito, patrimonio complessivo, codice fiscale, eta' o conto
  titoli.
- Profilo condiviso fra dispositivi o sincronizzato in cloud.
- Ordini automatici, previsioni o scelta autonoma di nuovi strumenti.

## Vincoli

- Tutto il profilo resta locale e non e' necessario per usare il backtest.
- Le soglie personali prevalgono su euristiche generiche; una soglia non
  compilata non viene inventata.
- Ogni rilievo conserva l'evidenza che lo ha generato e l'eventuale copertura
  parziale dei dati.
- I valori manuali autorevoli, come TER e classificazioni corrette, non vengono
  reinterpretati come errori della fonte.
- `comparatore/` resta indipendente da Streamlit.

## Domande aperte

Nessuna. Il profilo e' volutamente minimo e puo' essere esteso soltanto quando
una nuova regola dimostra di aver bisogno di un dato aggiuntivo.
