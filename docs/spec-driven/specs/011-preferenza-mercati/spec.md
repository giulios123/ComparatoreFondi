# 011 · Preferenza dei mercati di quotazione

*Stato: bozza — 12 agosto 2026*

## Problema

Lo stesso fondo o ETF può essere quotato a Milano, Xetra e su altri mercati con
simboli e valute differenti. Oggi l'ordine dei risultati dipende soprattutto
dalle graduatorie interne delle singole fonti: l'utente non può dichiarare i
mercati che preferisce e può quindi vedere per prima una quotazione diversa da
quella che usa abitualmente.

La preferenza non deve però trasformarsi in una sostituzione silenziosa: una
posizione già importata o scelta con un simbolo esatto deve continuare a
identificare quella quotazione.

## Chi lo incontra

Chi cerca per nome o ISIN uno strumento disponibile su più borse, in particolare
chi vuole privilegiare Milano, Xetra o un altro mercato senza rendere l'app
specifica per un singolo intermediario.

## Criteri di accettazione

1. Nelle preferenze locali l'utente può costruire un elenco ordinato di mercati
   preferiti scegliendoli da un catalogo ricercabile, modificarne l'ordine e
   rimuoverli.
2. I risultati riferiti allo stesso ISIN o alla stessa identità economica sono
   raggruppati; all'interno del gruppo compaiono prima le quotazioni dei mercati
   preferiti e restano consultabili tutte le alternative note.
3. Ogni risultato mostra chiaramente mercato, valuta e simbolo, senza presentare
   il mercato di quotazione come esposizione geografica del fondo.
4. La preferenza incide sulla graduatoria di una ricerca generica e sulla scelta
   proposta dopo una ricerca per ISIN, ma non sostituisce un simbolo esatto già
   selezionato, importato o salvato.
5. In assenza di una preferenza applicabile, l'ordine è stabile e spiegabile;
   le quotazioni prive di mercato noto restano disponibili in fondo al gruppo.
6. La cache delle risposte delle fonti conserva i risultati grezzi: cambiare la
   preferenza riordina immediatamente i risultati senza una nuova chiamata di
   rete e senza invalidare dati utili.
7. Il portafoglio JSON continua a salvare la quotazione esatta. La preferenza è
   una configurazione locale separata e non modifica i file importati.
8. L'elenco dei mercati e gli alias usati da OpenFIGI, Yahoo ed EODHD sono
   centralizzati e testati, così che codici equivalenti non producano gruppi
   duplicati.
9. La funzione non contiene regole specifiche per Directa e non richiede dati
   commerciali su liquidità o spread.
10. Tutti i testi sono disponibili nelle quattro lingue e ricerca, persistenza
    e retrocompatibilità sono coperte da test automatici.

## Non-obiettivi

- Scegliere il mercato con il volume o lo spread migliore senza dati affidabili.
- Calcolare commissioni di negoziazione specifiche di un intermediario.
- Inviare ordini, fare routing verso un broker o cambiare automaticamente una
  posizione esistente.
- Dedurre l'esposizione geografica dal luogo di quotazione.
- Nascondere le quotazioni che non appartengono ai mercati preferiti.

## Vincoli

- La preferenza resta locale e non contiene dati personali o credenziali.
- Le chiavi dei risultati e della cache non dipendono dall'ordine impostato
  dall'utente.
- Ricerca e backtest restano utilizzabili se il mercato è assente o non
  normalizzabile.
- `comparatore/` non importa Streamlit; ogni testo a video passa da `t()` ed è
  tradotto nei quattro cataloghi.
- I JSON di portafoglio già prodotti restano importabili e il loro simbolo non
  viene reinterpretato.

## Domande aperte

- Quale ordine iniziale mostrare a una nuova installazione: Milano per tutti,
  un ordine basato sulla lingua/area locale o nessuna preferenza?
- Dopo la preferenza di mercato, quale ordine usare fra valuta di quotazione,
  completezza dei dati e graduatoria originaria della fonte?
- Il catalogo iniziale deve mostrare tutti i mercati supportati dalle fonti o
  una lista breve di mercati europei con ricerca degli altri?
