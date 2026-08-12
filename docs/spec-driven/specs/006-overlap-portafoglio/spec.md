# 006 · Sovrapposizione delle partecipazioni

*Stato: implementata — 12 agosto 2026*

## Problema

La scheda Bilanciamento mostra classi, aree, settori e prime posizioni, ma non
somma la stessa societa' posseduta attraverso fondi diversi. Due ETF possono
sembrare diversificati per nome e replicare in larga parte le stesse aziende.

Le fonti gratuite espongono spesso soltanto le prime posizioni: ignorare il
limite farebbe apparire l'analisi completa, rinormalizzare la parte nota al
100% gonfierebbe le concentrazioni e trattare l'assenza come zero inventerebbe
una differenza.

## Chi lo incontra

Chi combina ETF globali, regionali, settoriali o fattoriali e vuole capire
quali esposizioni sottostanti sta duplicando, soprattutto quando il portafoglio
ha molti strumenti ma la diversificazione reale e' inferiore a quella
apparente.

## Criteri di accettazione

1. Per ogni fondo la pagina dichiara quanta parte delle partecipazioni e'
   conosciuta e da quale fonte proviene; la quota mancante resta esplicita.
2. Per ogni coppia con dati sufficienti viene mostrata la sovrapposizione
   minima osservabile delle partecipazioni note. Le quote non vengono
   rinormalizzate al 100% e il numero e' etichettato come limite inferiore,
   non come overlap completo.
3. Una matrice permette di individuare le coppie piu' sovrapposte; celle con
   identita' ambigue o copertura insufficiente mostrano `n/d` o un avviso,
   non zero.
4. Una vista aggregata somma l'esposizione del portafoglio alle stesse
   partecipazioni, moltiplicando il peso nel fondo per il peso del fondo nel
   portafoglio, e mostra anche la quota complessiva non coperta.
5. L'identita' di una partecipazione usa un identificatore stabile quando
   disponibile; simboli e nomi normalizzati sono ripieghi dichiarati. Due
   corrispondenze ambigue non vengono fuse automaticamente.
6. Fondi senza holdings o con dati vecchi non bloccano il backtest e non
   spariscono dall'analisi: sono elencati con la ragione dell'assenza.
7. Correzioni manuali di classe/area/settore non alterano le partecipazioni
   sottostanti e l'overlap non altera i grafici di bilanciamento esistenti.
8. I dati necessari al successivo rapporto anonimo sono disponibili come
   risultato strutturato senza nomi di fondo obbligatori.
9. Calcoli e matching sono coperti da test; tutti i testi passano dai quattro
   cataloghi.

## Non-obiettivi

- Promettere il look-through completo quando la fonte espone solo le prime
  posizioni.
- Acquistare o integrare un feed commerciale di holdings.
- Deducere paesi, settori o fattori mancanti dall'overlap.
- Raccomandare automaticamente quale fondo eliminare.
- Importare in questa prima versione file holdings degli emittenti: potra'
  essere un'estensione successiva dello stesso contratto dati.

## Vincoli

- Le quote delle posizioni restano frazioni del fondo e non vengono
  rinormalizzate per nascondere la parte sconosciuta.
- La provenienza Yahoo o di altre fonti resta separata dalla provenienza TER e
  allocazione.
- Il matching deve essere deterministico e testabile; nessun modello AI decide
  se due nomi descrivono la stessa societa'.
- `comparatore/` non importa Streamlit e l'assenza di metadati non blocca le
  serie prezzi.

## Domande aperte

Nessuna per la prima versione. Il caricamento manuale di holdings completi e'
rimandato finche' l'analisi sulle posizioni gia' disponibili non dimostra di
essere utile.
