# 009 · Copilot spiega il portafoglio e propone simulazioni

*Stato: approvata, subordinata alle spec 007 e 008 — 12 agosto 2026*

## Problema

Metriche, correlazioni, rolling return, inflazione e overlap possono essere
corretti ma difficili da collegare fra loro. Il rapporto deterministico della
spec 008 stabilisce i fatti, ma non adatta tono, ordine e spiegazione alla
domanda dell'utente e non trasforma facilmente un rilievo in una sequenza di
simulazioni comprensibili.

L'utente vuole anche indicazioni esplicite quando i dati le sostengono, senza
previsioni e senza inviare identita' o patrimonio. Un modello lasciato libero
di analizzare il portafoglio grezzo potrebbe inventare strumenti, confondere
passato e futuro o produrre consigli non collegati ai numeri mostrati.

## Chi lo incontra

Chi usa localmente Comparatore Fondi, possiede una sottoscrizione GitHub
Copilot e vuole una spiegazione in linguaggio naturale con priorita' e prossimi
confronti da provare, mantenendo identificatori e importi sul proprio computer.

## Criteri di accettazione

1. La funzione e' facoltativa e si attiva soltanto con un'azione esplicita;
   nessun dato viene inviato durante il normale backtest o in background.
2. Prima dell'invio l'utente vede integralmente provider, modello e payload
   anonimo prodotto dalla spec 008 e puo' annullare.
3. Copilot riceve soltanto il rapporto anonimo e istruzioni statiche: niente
   nomi, ticker, ISIN, importi, file, chiavi o accesso agli oggetti Streamlit.
4. La sessione non espone tool, web, shell, filesystem, broker o funzioni di
   esecuzione. E' una singola analisi senza memoria remota richiesta
   dall'applicazione.
5. La risposta segue uno schema strutturato con sintesi, rilievi prioritari,
   evidenze richiamate per codice, indicazioni, simulazioni suggerite, limiti e
   avvertenza sul carattere storico dell'analisi.
6. Ogni indicazione deve richiamare almeno un'evidenza presente nel payload.
   Se il modello cita un codice inesistente, inventa un asset o viola lo schema,
   quella parte non viene mostrata come valida e l'utente vede la ragione.
7. Le indicazioni possono essere esplicite su struttura e scenari (per esempio
   ridurre una concentrazione oltre il limite dichiarato o confrontare la
   rimozione di `asset_2`), ma non prevedono rendimenti, non promettono esiti e
   non eseguono cambiamenti. L'utente applica eventualmente uno scenario in
   una copia confermata del portafoglio.
8. La risposta usa la lingua corrente dell'interfaccia; la mappa fra
   `asset_N` e nomi reali viene applicata soltanto localmente dopo la
   validazione.
9. Login assente, rete assente, quota esaurita, timeout e risposta invalida
   producono messaggi distinti. Il rapporto deterministico resta disponibile
   e il backtest non viene modificato.
10. Il comportamento del client e della validazione e' coperto con mock; casi
    campione verificano che l'output non introduca previsioni o identificatori.

## Non-obiettivi

- Cercare autonomamente nuovi strumenti, notizie o quotazioni sul web.
- Consigliare un ticker non gia' rappresentato fra candidati anonimi forniti
  dall'app.
- Conversazione persistente, memoria fra sessioni o sincronizzazione cloud.
- Esecuzione automatica delle simulazioni o modifica del portafoglio corrente
  senza conferma.
- Consulenza certificata, ordini, timing di mercato o previsioni.
- Provider diversi da quello approvato dalla spec 007.

## Vincoli

- La spec si implementa soltanto dopo un esito favorevole della spec 007 e usa
  esclusivamente il contratto privacy della spec 008.
- I calcoli restano nel codice locale; il modello ordina e spiega risultati,
  non ricalcola le serie.
- Nessun segreto GitHub viene gestito dal file delle API EODHD/Twelve Data.
- Una risposta AI non entra nelle metriche, nei JSON di portafoglio o nella
  cache prezzi.
- Nessuna previsione, anche se richiesta in linguaggio libero.

## Domande aperte

Nessuna di prodotto. Il modello disponibile e la modalita' concreta di avvio
sono quelli verificati e approvati dalla spec 007, non valori fissati ora.
