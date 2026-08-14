# 010 · Scheda informativa dello strumento

*Stato: implementata — 14 agosto 2026*

## Problema

Oggi l'app mostra alcune informazioni descrittive di fondi ed ETF soltanto nei
punti in cui servono al confronto: TER, composizione, metodo di distribuzione e
pochi altri attributi. L'utente non ha una scheda unica in cui capire che cosa
ha selezionato, quale quotazione sta usando, quanto sono completi i dati e da
quale fonte proviene ogni informazione.

L'assenza di provenienza e data di osservazione rende inoltre difficile
distinguere un dato mancante da un dato vecchio o da un conflitto fra fonti.

## Chi lo incontra

Chi cerca un nuovo strumento, verifica una posizione importata o confronta due
quotazioni dello stesso fondo prima di avviare il backtest.

## Criteri di accettazione

1. Da un risultato di ricerca e da uno strumento già in portafoglio si può
   aprire una scheda dedicata, per fondi, ETF e altri tipi supportati.
2. La scheda distingue l'identità economica dalla quotazione: mostra almeno
   nome, simbolo, ISIN quando disponibile, tipo, mercato e valuta di
   quotazione senza sostituire automaticamente il simbolo scelto.
3. La scheda riunisce almeno TER e relativa origine, politica di distribuzione,
   replica, allocazione, principali partecipazioni e copertura storica quando
   questi dati sono disponibili.
4. Quando una fonte gratuita o già integrata li fornisce, la scheda può mostrare
   anche emittente, indice seguito, domicilio, valuta del fondo, data di avvio,
   patrimonio, collegamento al KID, data del documento e indicatore sintetico
   di rischio; un campo assente resta esplicitamente non disponibile e non
   viene inferito.
5. Ogni dato variabile espone fonte, data di osservazione o aggiornamento e
   stato di acquisizione; i conflitti fra fonti restano visibili.
6. Un valore manuale o ricavato da un KID non viene sovrascritto da una fonte
   automatica con priorità inferiore. La priorità justETF resta soggetta
   all'attivazione esplicita già esistente.
7. Se sono note più quotazioni dello stesso ISIN, la relazione è visibile nella
   scheda ma la quotazione attiva non cambia senza un'azione dell'utente.
8. Il fallimento di una fonte non blocca ricerca o backtest: la scheda indica
   quali sezioni sono incomplete e consente di ritentare l'acquisizione.
9. I dati normalizzati utili persistono nel JSON del portafoglio in modo
   retrocompatibile; stati transitori, errori e contenuti di cache non vengono
   esportati.
10. Nessuna fonte introdotta dalla prima versione richiede una spesa superiore
    a 10 euro al mese; ogni sorgente con condizioni d'uso particolari richiede
    lo stesso livello di consenso e trasparenza previsto per justETF.
11. Tutti i testi sono disponibili in italiano, inglese, francese e tedesco e
    i nuovi comportamenti sono coperti da test automatici.

## Non-obiettivi

- Costruire un database commerciale completo di fondi ed ETF.
- Attribuire rating proprietari, punteggi ESG o raccomandazioni di acquisto.
- Estrarre automaticamente qualsiasi PDF o KID nella prima iterazione.
- Scegliere il mercato preferito: è oggetto della spec 011.
- Generare l'analisi assistita dall'AI: è oggetto della spec 009.

## Vincoli

- `comparatore/` non importa Streamlit.
- I testi a video passano da `t()` e le nuove chiavi esistono in tutti e quattro
  i cataloghi.
- La gerarchia delle fonti già decisa resta valida: i valori manuali e da KID
  sono protetti e justETF è utilizzabile solo con consenso esplicito.
- La scheda non deve confondere mercato di quotazione, valuta di quotazione,
  domicilio ed esposizione geografica.
- I dati ricevuti da terzi conservano fonte, data e limiti d'uso; il codice
  Apache-2.0 non attribuisce automaticamente la stessa licenza ai dati.
- Il formato JSON esistente resta importabile.

## Domande aperte

- Nessuna.
