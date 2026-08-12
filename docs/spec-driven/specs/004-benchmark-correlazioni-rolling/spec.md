# 004 · Benchmark, correlazioni e rendimenti rolling

*Stato: approvata — 12 agosto 2026*

## Problema

Il backtest descrive il portafoglio e confronta i fondi che lo compongono, ma
non risponde a tre domande distinte:

1. se il risultato sia stato migliore o peggiore di un riferimento scelto
   dall'utente;
2. quanto gli strumenti si siano mossi insieme, al di la' delle etichette di
   classe, area e settore;
3. quanto il rendimento dipenda dalla data iniziale scelta.

Il CAGR sull'intero periodo e' un solo punto di osservazione. Due portafogli con
lo stesso CAGR possono avere avuto finestre pluriennali molto diverse, e fondi
con nomi diversi possono essere quasi perfettamente correlati.

## Chi lo incontra

Chi valuta se la complessita' del proprio portafoglio abbia aggiunto qualcosa
rispetto a un riferimento semplice, chi vuole riconoscere diversificazione
solo apparente e chi non vuole giudicare una strategia da una singola coppia di
date favorevole o sfavorevole.

## Criteri di accettazione

1. Il benchmark e' facoltativo e si puo' scegliere in tre modi: nessuno, uno
   dei due riferimenti rapidi "Azionario mondiale" e "S&P 500", oppure una
   ricerca libera tramite le stesse fonti usate per gli altri strumenti.
2. Il benchmark resta esterno al portafoglio: non entra nei pesi, non modifica
   la composizione e non cambia curve o metriche gia' esistenti. Con PAC attivo
   riceve lo stesso capitale e lo stesso calendario di versamenti, mentre le
   metriche di rendimento restano depurate dai flussi.
3. Il portafoglio mantiene l'intero periodo disponibile. Grafici e metriche
   comparative dichiarano invece il periodo comune effettivamente coperto da
   portafoglio e benchmark; nessuna serie viene estesa o retro-riempita per
   rendere il confronto artificialmente piu' lungo.
4. Se il benchmark non e' risolvibile, il backtest del portafoglio continua e
   la pagina spiega quale fonte e' fallita; l'assenza di un riferimento
   opzionale non viene trattata come l'assenza di un fondo investito.
5. Il confronto mostra almeno crescita, CAGR, volatilita', max drawdown,
   rendimento attivo, tracking error e information ratio sul periodo comune;
   una metrica non calcolabile resta `n/d` con una spiegazione.
6. Una matrice mostra le correlazioni dei rendimenti mensili total-return,
   nella valuta di riferimento, fra gli strumenti del portafoglio e, se
   presente, il benchmark. Il periodo comune e il numero di osservazioni sono
   visibili; con dati insufficienti non viene mostrato un numero ingannevole.
7. Per portafoglio e benchmark sono disponibili rendimenti rolling a 1, 3, 5
   e 10 anni quando lo storico basta, con serie temporale, peggiore, mediana,
   migliore e percentuale di finestre positive.
8. La scelta del benchmark sopravvive a export/import del portafoglio; i JSON
   precedenti continuano a caricarsi assumendo "nessun benchmark".
9. Tutti i testi sono disponibili nelle quattro lingue e le nuove analisi
   sono coperte da test riproducibili senza rete.

## Non-obiettivi

- Previsioni, Monte Carlo, frontiera efficiente o ottimizzazione dei pesi.
- Scelta automatica di un benchmark "giusto" in base al portafoglio.
- Uso delle curve sintetiche COVIP come benchmark di rischio.
- Modifica dei proxy storici dei fondi o uso automatico di un proxy per
  allungare il benchmark.
- Preferenza delle piazze di quotazione: e' la spec 011.
- Spiegazione tramite AI: e' la spec 009.

## Vincoli

- Le serie devono essere total-return. Un indice di solo prezzo non puo'
  essere presentato come equivalente a un riferimento con dividendi
  reinvestiti.
- Il benchmark libero conserva simbolo, ISIN, fonte e diagnostica della
  quotazione realmente scelta.
- `comparatore/` resta indipendente da Streamlit; `app.py` non si importa nei
  test e riceve le consuete guardie sul sorgente quando cambia struttura.
- Il pulsante di export continua a precedere il backtest.
- Nessun benchmark viene contato nel TER medio, nei costi o nel bilanciamento
  del portafoglio.

## Domande aperte

Nessuna. I due preset rapidi sono riferimenti investibili total-return gia'
presenti nel catalogo dei proxy: azionario mondiale (`VT`) e S&P 500
(`VFINX`). L'interfaccia deve dichiarare il simbolo reale e non chiamarli con
il nome di un indice diverso.
