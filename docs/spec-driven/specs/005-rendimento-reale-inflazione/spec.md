# 005 · Rendimento reale al netto dell'inflazione

*Stato: approvata — 12 agosto 2026*

## Problema

L'app mostra valori e rendimenti nominali. Su periodi lunghi un montante puo'
crescere molto e perdere comunque una parte rilevante del proprio potere
d'acquisto; oggi l'utente deve ricostruire questa differenza altrove e non puo'
confrontarla con la stessa curva, lo stesso PAC e lo stesso periodo del
backtest.

## Chi lo incontra

Chi valuta obiettivi di lungo periodo, confronta un PAC con un PIC o legge un
CAGR nominale durante anni di inflazione elevata. E' particolarmente rilevante
quando capitale e obiettivi sono espressi in euro, ma il principio vale per
ogni utente europeo.

## Criteri di accettazione

1. L'analisi dell'inflazione e' facoltativa, spenta di default e non cambia i
   risultati nominali esistenti.
2. L'utente sceglie il riferimento geografico; Italia e area euro sono sempre
   disponibili e l'Italia e' il valore iniziale per una nuova installazione.
3. La pagina mostra fonte, area, ultimo mese disponibile e intervallo coperto
   dall'indice dei prezzi. Nessun valore futuro viene stimato.
4. Sono visibili almeno curva reale, valore finale reale, rendimento totale
   reale e CAGR reale, affiancati ai corrispondenti valori nominali.
5. Con PAC attivo sia saldo sia versato vengono espressi nel potere d'acquisto
   della data iniziale; i flussi non vengono scambiati per rendimento.
6. Se l'indice dei prezzi inizia dopo il portafoglio, il tratto reale parte
   dalla prima data coperta e lo dichiara; non viene retro-riempito. Un ritardo
   normale di pubblicazione a fine serie e' visibile tramite la data
   dell'ultimo dato utilizzato.
7. Se Eurostat non risponde, il backtest nominale continua e l'analisi reale
   mostra un errore non bloccante con una possibilita' di riprova.
8. I dati sono conservati nella cache locale, la preferenza geografica
   sopravvive ai riavvii e nessun dato personale viene inviato a Eurostat.
9. Calcoli, parsing e fallback sono coperti offline da fixture; tutti i testi
   sono tradotti nelle quattro lingue.

## Non-obiettivi

- Previsione dell'inflazione o proiezione del potere d'acquisto futuro.
- Un paniere personale basato sulle spese dell'utente.
- Fiscalita', costo della vita per citta' o cambio del paese durante il
  backtest.
- Inflazione implicita di mercato o scenari macroeconomici.
- Uso dell'inflazione per ottimizzare o raccomandare strumenti.

## Vincoli

- La fonte e' l'indice armonizzato dei prezzi al consumo (HICP) pubblicato da
  Eurostat tramite API gratuita; eventuali cambi di base dell'indice non
  devono produrre salti nel fattore relativo.
- Il dato mensile viene applicato alle date di mercato senza inventare valori
  prima della prima osservazione o oltre l'ultimo periodo pubblicato.
- La curva nominale resta la fonte di verita' del backtest; quella reale e'
  una vista derivata.
- `comparatore/` non importa Streamlit e ogni errore di rete degrada in una
  diagnostica, non in un traceback.

## Domande aperte

Nessuna. L'area geografica descrive il potere d'acquisto dell'utente e non si
deduce dalla valuta del portafoglio; per questo resta una scelta esplicita.
