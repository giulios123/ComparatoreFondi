# 014 · Heatmap, rolling e frontiera storica

*Stato: fatta — 29 agosto 2026*

## Problema

Il confronto attuale mostra metriche aggregate, correlazioni e un riepilogo
rolling mensile, ma non rende leggibili la stagionalita' dei rendimenti, la
distribuzione delle finestre storiche e l'effetto della combinazione dei pesi.

## Chi lo incontra

Chi vuole capire quando un portafoglio ha guadagnato, quanto sia dipeso dalla
data di ingresso e quali combinazioni dei fondi gia' scelti abbiano avuto il
miglior compromesso storico.

## Criteri di accettazione

1. Una scheda Analisi contiene Heatmap, Rolling e Frontiera senza alterare le
   schede esistenti.
2. La heatmap e' selezionabile per portafoglio, benchmark o strumento, usa uno
   storico indipendente e distingue valori mancanti, parziali e YTD.
3. Il rolling offre Continuous, Annual e Distribution, gli orizzonti 1/3/5/10/
   15/20 anni e CAGR, volatilita', Sharpe, Sortino, Calmar e Ulcer Index.
4. Le finestre richiedono lo storico precedente necessario, non vengono
   accorciate e dichiarano copertura e periodo comune quando si confrontano
   piu' serie.
5. La frontiera simula i fondi del portafoglio sulle date del backtest, con
   PAC, ribilanciamento e vincoli min/max per fondo; mostra mix, punti non
   dominati ed estremi per rendimento, rischio e drawdown.
6. Una ricerca riproducibile usa campionamento piu' affinamento, non promette
   un ottimo futuro e permette anteprima, export e applicazione confermata dei
   pesi senza aggiungere il benchmark alle holdings.
7. Sortino e Ulcer Index hanno definizioni verificate e test numerici; il
   rolling mensile conserva l'API esistente correggendo la dimensione delle
   finestre.
8. Tutti i testi passano dai quattro cataloghi, il codice numerico resta
   indipendente da Streamlit e la suite offline continua a passare.

## Non-obiettivi

- Previsioni, rendimenti attesi o validazione fuori campione.
- Short selling, leva, fiscalita' o nuove fonti dati.
- Ottimizzazione delle curve sintetiche COVIP.
- Modifica automatica di portafoglio senza una conferma dell'utente.

## Vincoli

- Prezzi nominali netti e dati total-return secondo le fonti gia' usate.
- Benchmark sempre esterno a holdings, TER, costi e ribilanciamento principale.
- Nessun import di Streamlit in `comparatore/`; UI e stringhe restano in `app.py`
  e nei cataloghi esistenti.
- MAX mantiene il limite storico applicativo del 1970; dati insufficienti o
  denominatori nulli restano `n/d`.

## Domande aperte

Nessuna: collocazione, copertura, PAC, vincoli, ricerca e azione sui pesi sono
stati concordati nel piano di implementazione.
