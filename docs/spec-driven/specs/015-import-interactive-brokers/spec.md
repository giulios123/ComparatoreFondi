# 015 · Import portafoglio Interactive Brokers

*Stato: fatta — 3 settembre 2026*

## Problema

L'import Directa legge una singola tabella CSV/XLSX con mappatura guidata. Un
rendiconto Activity Statement di Interactive Brokers e' invece un CSV a sezioni:
posizioni aperte, anagrafica strumenti, liquidita', operazioni e totali hanno
intestazioni e larghezze diverse nello stesso file. Passarlo al lettore Directa
farebbe fallire il parsing o potrebbe confondere dati contabili con valori di
mercato.

Il campione disponibile contiene posizioni azionarie long in piu' valute,
righe Summary e Lot e l'anagrafica degli strumenti in una sezione separata.

## Chi lo incontra

Chi vuole ricostruire nel comparatore la composizione corrente del proprio
conto Interactive Brokers, senza importare la cronologia delle operazioni.

## Criteri di accettazione

1. Un expander dedicato a Interactive Brokers compare immediatamente sotto
   l'import Directa e accetta il rendiconto Activity Statement in CSV.
2. Il parser riconosce la struttura a sezioni e le intestazioni italiane e
   inglesi senza assumere una tabella rettangolare unica.
3. Vengono considerate solo le righe `Summary` della sezione delle posizioni
   aperte. Righe `Lot`, totali e sezioni contabili non diventano posizioni e
   la UI ne spiega l'esclusione.
4. Le posizioni vengono collegate all'anagrafica per tipo di attivo e simbolo;
   ISIN, descrizione, mercato e tipo sono conservati quando disponibili. Una
   posizione senza anagrafica resta visibile con il ticker e una diagnosi.
5. Valuta base e data finale vengono lette dal rendiconto o dal nome del file.
   I controvalori esteri vengono convertiti prima di capitale e pesi: prima si
   usa un cambio ricavabile e riconciliabile con il totale IBKR quando e'
   univoco, poi il cambio BCE/Yahoo alla data finale, con correzione manuale.
6. Un cambio mancante blocca l'import; una differenza dal totale IBKR resta
   visibile e richiede conferma esplicita. La liquidita' e' esclusa e i soli
   titoli vengono rinormalizzati al 100%.
7. Le risoluzioni univoche usano anche azioni e altri strumenti non-fondo;
   i selettori manuali compaiono solo per risultati ambigui o non risolti.
   L'utente deve escludere esplicitamente ogni riga non importabile.
8. Short, derivati, quantita' o valori non positivi e dati non riconciliabili
   non vengono reinterpretati in silenzio.
9. Il portafoglio importato sostituisce quello corrente come Directa, senza
   persistere conto, nome, operazioni, credenziali o file sorgente.
10. Tutti i testi sono presenti nei quattro cataloghi; parser e conversioni
    sono testati senza Streamlit e il comportamento Directa resta invariato.

## Non-obiettivi

- Flex Query, XML, API IBKR o altri tracciati non presenti nel campione.
- Registro di acquisti, vendite, dividendi, commissioni e fiscalita' (spec 012).
- Importazione o simulazione della liquidita', delle posizioni short e dei
  derivati.
- Modifica del formato JSON del portafoglio o del motore di backtest.

## Vincoli

- `comparatore/` non importa Streamlit; ogni testo a video passa da `t()`.
- Il CSV reale resta fuori dal repository; le fixture sono sintetiche e
  anonime.
- Le API dei broker non vengono chiamate: per i prezzi e le quotazioni si
  riusano le fonti gia' presenti nell'app.

## Domande aperte

Nessuna: per la prima versione sono stati scelti rendiconto CSV, soli titoli,
cassa esclusa e politica di cambio rendiconto-poi-BCE con override manuale.

## Riferimenti

- [Open Positions Flex Query](https://www.ibkrguides.com/reportingreference/reportguide/open%20positionsfq.htm)
- [Open Positions dei rendiconti standard](https://www.ibkrguides.com/reportingreference/reportguide/openpositions_realizedsummary.htm)
