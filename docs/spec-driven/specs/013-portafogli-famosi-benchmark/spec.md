# 013 · Portafogli famosi come benchmark compositi

*Stato: approvata — 2026-08-26*

## Problema

Il benchmark oggi può essere un singolo strumento (`VT`, `VFINX` o una
quotazione cercata). Chi vuole confrontare il portafoglio con una strategia
conosciuta deve quindi ricostruirla manualmente tra le proprie holdings,
mescolando il riferimento con TER, costi e ribilanciamento dell'investitore.

## Chi lo incontra

Chi usa il backtester per confrontare una strategia multi-asset con 25
portafogli modello pubblici, anche senza avere a disposizione tutti i fondi
originali o usando un dispositivo senza hover.

## Criteri di accettazione

1. Il catalogo statico contiene esattamente 25 ID, con pesi canonici ed
   eseguibili al 100%, fonte HTTPS e classificazione `composite` o `managed`.
2. La sidebar conserva `VT`, `VFINX`, ricerca libera e nessun benchmark e offre
   una voce “Portafogli famosi” con ricerca, popover nativo e pulsanti con
   tooltip localizzato; la scheda del selezionato resta visibile anche senza
   hover.
3. Il JSON versione 1 conserva il nuovo riferimento
   `kind=portfolio`, `portfolio_id` e `catalog_version`, senza invalidare i
   file precedenti; un ID sconosciuto diventa nessun benchmark.
4. I componenti sono risolti singolarmente e convertiti nella valuta base; il
   periodo è l'intersezione dei dati reali. Un componente mancante rende
   indisponibile tutto il benchmark, senza rinormalizzare e senza fermare il
   backtest dell'utente.
5. I modelli compositi usano lo stesso capitale e PAC dell'utente e
   ribilanciamento annuale al primo giorno di mercato; ALLW, RPAR e TRTY sono
   singoli strumenti gestiti internamente. Grafici e metriche mostrano una
   sola curva composita.
6. Sono presenti test di catalogo, persistenza, periodo comune, PAC,
   conversione valutaria, ribilanciamento annuale, duplicati e fallimento
   atomico, oltre alle guardie sorgente dell'app.

## Non-obiettivi

- modificare holdings, pesi, TER, costi o ribilanciamento scelti dall'utente;
- promettere rendimento o adeguatezza finanziaria;
- aggiornare automaticamente composizioni o proxy del catalogo;
- aggiungere CSS o JavaScript per simulare il ritardo del tooltip.

## Vincoli

- `comparatore/` resta importabile senza Streamlit;
- ogni testo a video passa da `t()` e compare nei quattro cataloghi;
- i proxy conservano l'esposizione dichiarata e gli avvertimenti sulle
  approssimazioni e sulle eccezioni (ETC/ETF USA);
- niente extrapolazione, backfill da indici o rinormalizzazione parziale.

## Domande aperte

Nessuna: le fonti, le allocazioni e i proxy sono bloccati nel piano approvato.
