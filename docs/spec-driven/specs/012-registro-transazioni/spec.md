# 012 · Registro di transazioni, dividendi e risultati reali

*Stato: bozza — 12 agosto 2026*

## Problema

Il portafoglio attuale descrive soprattutto una composizione e può importare da
Directa una fotografia delle posizioni. Non conserva però la storia di acquisti,
vendite, dividendi, commissioni e movimenti di cassa. Di conseguenza non può
ricostruire capitale investito, flussi reali, risultato realizzato e non
realizzato o rendimento personale del portafoglio.

Il backtest resta una simulazione ipotetica: usarlo come se fosse il resoconto
delle operazioni effettive darebbe numeri fuorvianti, soprattutto con versamenti,
prelievi e valute differenti.

## Chi lo incontra

Chi usa il comparatore anche per seguire nel tempo il proprio portafoglio e
vuole importare estratti di uno o più intermediari senza legare l'app a Directa.

## Criteri di accettazione

1. L'utente può importare CSV o XLSX tramite una mappatura guidata e riusabile,
   senza che il formato generico dipenda da intestazioni o regole di Directa.
2. Il registro normalizza almeno acquisto, vendita, dividendo, commissione,
   versamento e prelievo; righe non riconosciute restano visibili e non vengono
   reinterpretate in silenzio.
3. Prima di confermare un import, l'utente vede anteprima, mapping, valuta,
   segno dei flussi, duplicati, righe escluse e problemi. Nessun dato esistente
   viene sovrascritto implicitamente.
4. Reimportare lo stesso file o la stessa operazione non crea duplicati; ogni
   esclusione automatica è spiegata e può essere verificata.
5. Il registro conserva almeno data e ora quando disponibili, tipo, strumento,
   quantità, prezzo, importo, valuta, commissioni, imposte riportate dal file,
   conto, fonte e identificativo originario. Le credenziali non ne fanno parte.
6. Dalle operazioni confermate si possono ricostruire posizioni, quantità,
   costo contabile, cassa, dividendi e commissioni; eventuali dati mancanti o
   saldi non riconciliati sono evidenziati.
7. L'app distingue risultato realizzato, risultato non realizzato e flussi di
   reddito. Il metodo di calcolo del costo è dichiarato e applicato in modo
   deterministico.
8. Il rendimento reale del portafoglio tiene separati almeno rendimento pesato
   per il denaro e rendimento pesato per il tempo, quando i dati sono
   sufficienti, senza confonderli con il backtest ipotetico.
9. Per operazioni in più valute, importi e risultati riportano valuta originaria,
   cambio usato, fonte e data; un cambio mancante rende incompleto il calcolo
   interessato senza inventare un tasso.
10. Il registro è locale, esportabile e reimportabile. Il portafoglio modello
    esistente non viene sostituito o ribilanciato senza una conferma separata.
11. Plusvalenze e minusvalenze mostrate nella prima versione sono risultati
    contabili, non una dichiarazione dell'imposta dovuta; ritenute e imposte
    presenti nell'estratto restano flussi espliciti.
12. Tutti i testi sono disponibili nelle quattro lingue e importazione,
    deduplicazione e calcoli sono coperti da test con fixture anonime.

## Non-obiettivi

- Collegarsi alle API dei broker o inviare ordini.
- Preparare una dichiarazione fiscale o certificare l'imposta dovuta.
- Replicare l'interfaccia o il tracciato di un solo intermediario.
- Gestire nella prima iterazione ogni possibile operazione societaria, derivato
  o strumento illiquido.
- Prevedere prezzi, dividendi o rendimenti futuri.
- Trasformare automaticamente la cronologia reale in un portafoglio modello.

## Vincoli

- Il registro e i file importati restano locali; non vengono inclusi nel
  payload anonimo dell'AI se non come metriche aggregate esplicitamente ammesse.
- La mappatura è guidata e validata: corrispondenze rigide alle colonne Directa
  non diventano il modello interno.
- I calcoli contabili sono separati da `engine.py`, che continua a rappresentare
  simulazioni PIC/PAC e backtest.
- `comparatore/` non importa Streamlit; tutti i testi a video passano da `t()`
  e sono presenti nei quattro cataloghi.
- Il file JSON di portafoglio esistente resta importabile; un eventuale formato
  del registro ha versione e migrazioni proprie.
- Frankfurter o un'altra fonte di cambio già accettata conserva provenienza e
  data e non sostituisce un tasso esplicito dell'operazione senza consenso.

## Domande aperte

- Quale metodo usare come riferimento per il costo contabile: costo medio
  ponderato, FIFO o scelta configurabile?
- La prima iterazione deve riconciliare un saldo di cassa completo oppure usare
  versamenti e prelievi soltanto per i rendimenti pesati per il denaro?
- Servono fin dall'inizio più conti e intermediari separati, oppure basta
  conservare il campo conto in vista di un uso futuro?
- Quali estratti anonimi, oltre a un esempio Directa, sono disponibili per
  progettare e collaudare la mappatura guidata?
- Come rappresentare nella prima iterazione ritenute, trasferimenti titoli,
  frazionamenti, fusioni e altre operazioni societarie?
