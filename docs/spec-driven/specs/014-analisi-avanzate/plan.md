# 014 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Creare un livello numerico puro per calendario, heatmap e finestre rolling e
un valutatore batch NumPy per la frontiera. L'interfaccia risolve le serie con
il registry esistente, aggiorna i controlli solo nella scheda Analisi e usa
gli stessi oggetti PAC/ribilanciamento del backtest.

La ricerca usa seed fisso, simplex vincolato e affinamento locale per coppie di
pesi. I risultati hanno un fingerprint degli input; un risultato vecchio non
puo' essere applicato dopo che sono cambiati dati o parametri.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/analytics.py` | Calendario heatmap, rolling multi-metrica e coperture |
| `comparatore/frontier.py` | Simulazione batch, campionamento, vincoli e Pareto |
| `comparatore/metrics.py` | Sortino corretto e Ulcer Index |
| `app.py` | Scheda, caricamento storico, grafici e applicazione confermata |
| `comparatore/locales/*.py` | Etichette, aiuti ed errori nelle quattro lingue |

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Importare un optimizer esterno | Aggiunge dipendenze e non risolve la natura non convessa di drawdown e Ulcer Index |
| Inserire heatmap e frontiera in Confronto | La nuova analisi ha periodo e costi computazionali distinti |
| Applicare automaticamente il migliore | Una ricerca storica non e' una raccomandazione futura |

## Rischi

- Storici corti o con buchi: test di copertura e messaggi `n/d`, mai backfill.
- PAC e ribilanciamenti: confronto batch con `engine.simulate` su fixture.
- Rerun Streamlit costosi: calcolo soltanto su comando e tab aperta, con cache
  invalidata dal fingerprint.
- Traduzioni mancanti e regressioni nello script piatto: guardie AST e test i18n.

## Verifica

Unittest numerici e di frontiera, controllo sintassi/Ruff, smoke Streamlit con
CSV offline e verifica browser di selezioni, tooltip, layout stretto,
conferma applicazione ed errori isolati per vista.
