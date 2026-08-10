# 003 · TER affidabili, import Directa e costi PIC

*Stato: fatta — 10 agosto 2026*

## Problema

Il TER viene letto durante l'aggiunta del fondo, ma le fonti hanno copertura
irregolare, gli errori temporanei vengono confusi con un TER assente e il
risultato negativo resta in cache. Se l'utente configura una chiave o corregge
l'ISIN dopo l'aggiunta, il fondo gia' presente non viene riprovato.

Directa mostra posizioni con ISIN e controvalore, ma l'app non sa importarli da
un file e non esiste un formato pubblico stabile da assumere senza un campione.

Il PIC non espone il costo di carico e scarico: l'utente puo' quindi confrontare
montanti che ignorano commissioni fisse o percentuali con minimo e massimo.

## Chi lo incontra

Chi aggiunge ETF o fondi con una fonte TER intermittente, chi ricostruisce il
portafoglio corrente da Directa e chi valuta un PIC con un piano commissionale.

## Criteri di accettazione

1. Un tentativo TER distingue a video almeno: trovato, TER assente, fonte non
   configurata, fundamentals EODHD bloccato, simbolo non risolto ed errore
   temporaneo; il fondo conserva fonte e provenienza del valore mostrato.
2. Un comando di riprova rilancia i TER mancanti senza sovrascrivere un valore
   inserito manualmente; configurare una chiave, modificare l'ISIN o importare
   da Directa rilancia automaticamente i soli valori mancanti.
3. Un file CSV o XLSX puo' essere caricato, mappato in anteprima e importato
   dopo aver risolto o escluso esplicitamente ogni riga; capitale e pesi usano
   i controvalori attuali e nessuna riga viene scartata senza motivo visibile.
4. Il prospetto PIC accetta regole indipendenti di acquisto e vendita (nessuna,
   fissa, percentuale con minimo/massimo), riserva il carico dentro il budget,
   calcola lo scarico per posizione e mostra montante netto e costi separati.
5. Con PAC attivo il prospetto commissioni resta nascosto e il backtest,
   curve e metriche esistenti restano invariati.
6. I portafogli esportati prima della modifica continuano a caricarsi; le
   nuove opzioni e la provenienza TER vengono esportate senza chiavi segrete.
7. I test standard e `ruff check .` restano puliti e la libreria non importa
   Streamlit.

## Non-obiettivi

- Nuovi provider TER, scraping justETF o integrazione con le API Directa.
- Ricostruzione delle operazioni storiche, fiscalita' o liquidita' Directa.
- Applicazione delle commissioni alle rate PAC o modifica delle metriche del
  motore di backtest.

## Vincoli

- `comparatore/` resta indipendente da Streamlit; ogni testo a video passa da
  `t()` e viene aggiunto ai quattro cataloghi.
- L'import Directa usa una mappatura guidata finche' non esiste un campione
  reale, quindi il parser non assume intestazioni proprietarie.
- Il portafoglio importato sostituisce quello corrente e usa la valuta indicata
  dall'utente per i controvalori.
- Il valore manuale del TER e' autorevole anche quando e' zero.

## Domande aperte

- Nessuna.
