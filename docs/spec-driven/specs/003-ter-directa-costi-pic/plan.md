# 003 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Separare la risoluzione dei metadati dal semplice ritorno dell'`Instrument`,
cosi' la UI puo' distinguere un dato mancante da un errore. Aggiungere retry
esplicito e mapping Yahoo/EODHD senza rompere `Registry.metadata()`.

Tenere l'import Directa in un modulo puro che produce righe normalizzate e
diagnostica; la UI offre anteprima, mappatura e risoluzione delle quotazioni.

Tenere la stima PIC in un modulo puro: il calcolo risolve il capitale investibile
nel budget, poi usa le sleeve finali gia' prodotte dal backtest per la parte di
scarico. L'interfaccia mostra il prospetto senza cambiare il motore.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/sources/base.py`, `registry.py`, `yahoo.py`, `eodhd.py` | Risultati metadati, tentativi, mapping e provenienza TER |
| `comparatore/directa_io.py`, `comparatore/pic_costs.py` | Parser Directa e stima commissioni testabili |
| `comparatore/portfolio_io.py`, `app.py`, `comparatore/locales/*.py` | Persistenza, anteprima/import, retry TER, editor costi e testi |
| `tests/` | Contratti puri e guardie sorgente |

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| API Directa | Richiedono abilitazione e autorizzazione alla redistribuzione |
| Scraping justETF | Fonte opt-in e endpoint TER non documentato; fuori scope |
| Formato Directa fisso | Non esiste un campione pubblico stabile; la mappatura tollera varianti |
| Commissioni dentro `engine.run_backtest` | Cambierebbero metrica e curva, contro il requisito del prospetto separato |

## Rischi

- Le risposte Yahoo possono essere vuote o rate-limited: gli esiti strutturati e
  il retry devono impedire cache negative lunghe.
- Un controvalore Directa puo' usare separatori locali: il parser deve rifiutare
  ambiguita' invece di inventare un valore.
- Commissioni minime elevate possono consumare il budget: il calcolo deve
  restituire un errore localizzato, non un capitale investibile negativo.

## Verifica

1. Eseguire unittest, ruff e controlli AST di `app.py`.
2. Testare CSV/XLSX con intestazioni, separatori, duplicati e righe invalide.
3. Testare fixed/percentuale/min/max e confronto del prospetto con e senza PAC.
4. Avviare Streamlit via CSV offline e verificare import, TER retry e prospetto.
