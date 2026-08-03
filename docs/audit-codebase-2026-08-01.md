# Audit tecnico e di sicurezza

**Data:** 1 agosto 2026  
**Revisione:** `c4c72d4`  
**Ambito:** libreria `comparatore/`, UI Streamlit, fonti dati, persistenza
locale, bundle desktop e CI. Non sono stati modificati comportamenti
applicativi durante l'audit.

## Sintesi

Il progetto ha fondamenta sane: il confine fra libreria e UI e' rispettato, la
suite e il lint passano, le dipendenze non hanno CVE note e il bundle macOS si
costruisce da una copia pulita. Le criticita' principali non sono una
compromissione remota: sono quattro problemi di integrita' del calcolo e di
robustezza che possono produrre un backtest errato oppure interrompere una
sessione locale con input plausibili.

| Priorita' | Esito | Area |
|---|---|---|
| P1 | Confermato | Un fondo senza prezzi viene escluso e i pesi residui vengono rinormalizzati in silenzio |
| P1 | Confermato | Nomi visuali duplicati rompono il backtest quando il PAC e' attivo |
| P1 | Confermato | Prezzi nulli o non finiti producono curve non affidabili senza un errore |
| P2 | Confermato | L'import JSON accetta campi non numerici e puo' provocare un traceback nell'UI |
| P2 | Confermato | Le GitHub Action sono referenziate con tag mutabili, non con SHA |
| P2 | Gap di qualita' | Fonti remote, FX e COVIP hanno copertura automatica bassa |

## Metodo e riscontri

- `uv lock --check`: superato, 72 pacchetti risolti.
- `uv run python -m unittest discover -s tests -p "test_*.py"`: **146 test
  superati**.
- `uv run ruff check .`: superato.
- `uv run python scripts/generate_third_party_notices.py --check`: superato,
  62 pacchetti verificati.
- `pip-audit --strict`: nessuna vulnerabilita' nota nelle dipendenze installate.
- Bandit: nessuna vulnerabilita' eseguibile ad alta confidenza. Il solo finding
  alto e' SHA-1 nella chiave di filename cache: e' un hash non crittografico per
  disambiguare nomi e non protegge dati, quindi e' un falso positivo di
  sicurezza.
- Scansione segreti sui file tracciati: nessuna credenziale; i due alert nel
  README sono riferimenti documentali. Il file locale ignorato
  `.streamlit/secrets.toml` non e' stato incluso nel risultato.
- Smoke test: Streamlit avviato su `127.0.0.1`, endpoint `/_stcore/health`
  risponde `ok`.
- Bundle: PyInstaller ha completato la build macOS arm64 in una copia generata
  con `git archive`. Resta ad-hoc e non notarizzato, limite gia' documentato.
- Coverage: **65%** complessivo. I moduli puri sono solidi (`engine` 88%,
  `portfolio_io` 98%, `pesi` 98%); i percorsi esterni sono scoperti (`yahoo`
  15%, `twelvedata` 22%, `eodhd` 23%, `fx` 23%, `covip` 24%).

## Finding confermati

### P1 - Dati mancanti cambiano l'allocazione effettiva

L'UI mostra i simboli irrisolti ma crea gli `Holding` solo per i simboli ancora
presenti nelle colonne prezzi. Il motore poi normalizza comunque i pesi dei
fondi rimasti. Con due fondi al 50%, se uno fallisce il download, il capitale
viene investito al 100% nell'altro, pur lasciando l'utente con un avviso non
bloccante.

Questo e' particolarmente delicato in un comparatore finanziario: un problema
temporaneo di una fonte diventa un risultato apparentemente valido ma relativo
a un portafoglio diverso. Occorre fermare il backtest per default, offrendo al
massimo un'azione esplicita che rimuova i fondi mancanti e mostri i pesi nuovi.

### P1 - Etichette duplicate causano errore con PAC

`run_backtest()` rinomina le colonne con l'etichetta visuale prima di costruire
`per_fund_nav`. Due strumenti distinti con lo stesso `label` rendono le colonne
duplicate; con PAC la selezione di una colonna diventa un DataFrame e
`nav_curve()` riceve forme incompatibili. La riproduzione con due simboli e
label identica solleva `ValueError: operands could not be broadcast together`.

La chiave interna deve restare il simbolo univoco fino alla fine del calcolo.
Per la UI si possono usare nomi univoci derivati, per esempio `Nome (SYMBOL)`,
o una struttura di metadati separata.

### P1 - Quote non valide vengono trasformate in rendimenti fittizi

In `simulate()` i rapporti di prezzo passano per `np.nan_to_num(..., nan=1,
posinf=1, neginf=1)`. Questo nasconde dati corrotti invece di respingerli. Le
prove locali mostrano che:

- `[100, NaN, 110]` elimina la riga `NaN` e restituisce una serie di due punti;
- `[100, 0, 110]` porta il valore da 1.000 a 0 e lo lascia a 0;
- `[100, inf, 110]` produce una curva `1.000, 1.000, 0`.

Il parser CSV e le fonti dovrebbero rifiutare quote non finite o non positive
con un messaggio per simbolo. Il motore, come ultima barriera, deve validare
indici monotoni, finitezza e prezzi strettamente positivi prima della
simulazione, evitando di convertire errori in rendimento zero.

### P2 - Import di portafoglio senza validazione semantica

`portfolio_io.load()` controlla schema e presenza delle chiavi, ma non tipo,
finitezza o intervallo di `weight`, `ter` ed `extra`. Un JSON con
`"weight": "not-a-number"` supera l'import; la rinormalizzazione nell'UI
solleva poi `TypeError` fuori dal gestore di `PortfolioError`.

La correzione deve stare nel confine di importazione: accettare soltanto valori
numerici finiti, vincolare i campi economici, normalizzare i tipi e rigettare
simboli vuoti o duplicati con `PortfolioError` localizzabile. Aggiungere limiti
di dimensione e numero di fondi protegge anche da file involontariamente enormi.

### P2 - Supply chain CI migliorabile

I workflow limitano correttamente `contents: read` per test e licenze, ma le
action sono fissate a tag (`@v4`, `@v5`, `@v2`) anziche' a SHA immutabili. Il
workflow desktop assegna inoltre `contents: write` a tutti i job, mentre serve
solo alla pubblicazione della release. Un tag di action compromesso o spostato
puo' quindi eseguire codice con permessi di scrittura sul repository durante
una release.

Fissare ogni action a un commit SHA annotato con il tag leggibile e spostare
`contents: write` nel solo job `release`; i job di build devono avere
`contents: read` o nessun permesso aggiuntivo.

## Sicurezza: punti osservati ma non classificati come vulnerabilita'

- L'app e' pensata per uso locale e il launcher desktop ascolta solo su
  `localhost`; e' una scelta corretta. Un deploy multiutente non e' sicuro con
  il file condiviso delle chiavi API, ed e' gia' avvertito nel README.
- `keys.save()` applica `chmod 600` dopo la scrittura e cache/preferenze/chiavi
  non usano sostituzione atomica. Su filesystem condivisi o in caso di crash
  resta una finestra piccola di permessi o di file parziale. E' hardening P3,
  non una vulnerabilita' dimostrata nel modello locale previsto.
- Tre chiamate `unsafe_allow_html=True` interpolano metadati di provider nella
  ricerca. Non e' stato dimostrato XSS: Streamlit applica le proprie difese al
  rendering. Eliminare l'HTML o fare escaping esplicito resta preferibile, dato
  che i valori sono esterni.
- EODHD e Twelve Data ricevono la chiave come query parameter, imposto dalle
  loro API. Non loggare URL completi o eccezioni HTTP contenenti query e
  continuare a proteggere cache e log locali.

## Roadmap prioritaria

1. **P1 - Integrita' del backtest:** rendere bloccanti i fondi o cambi FX
   mancanti; aggiungere un test di regressione UI-sorgente che vieti l'avvio
   con un sottoinsieme non confermato del portafoglio.
2. **P1 - Validazione del motore:** introdurre una funzione di validazione
   prezzi e pesi, chiamata da `run_backtest`, con test per zero, `NaN`, infinito,
   duplicati e campi assenti.
3. **P1 - Identita' dei fondi:** mantenere il simbolo come identificatore di
   colonne e applicare etichette univoche solo alla presentazione; coprire il
   PAC con nomi uguali.
4. **P2 - Confine import:** validare semanticamente JSON e CSV, compresi limiti
   ragionevoli di file/riga; fare in modo che ogni errore di import diventi un
   `PortfolioError` gestito.
5. **P2 - CI:** pin SHA delle action, permessi minimi per job e controllo
   automatico che impedisca tag mobili.
6. **P2 - Test delle integrazioni:** fixture registrate per Yahoo/EODHD/Twelve,
   COVIP e Frankfurter; test offline di errori, rate limit, cache corrotta e
   conversione FX.
7. **P3 - Affidabilita' locale:** scritture atomiche per cache, preferenze e
   chiavi; log a rotazione con permessi restrittivi; rimuovere HTML non
   necessario dalla ricerca.

## Cosa non emerge dall'audit

Non sono emerse CVE note, segreti tracciati, import di Streamlit nella libreria,
esecuzione shell da input utente, SQL injection o bind di rete pubblico nel
percorso desktop. Le formule COVIP e la semantica dei rendimenti delle fonti
richiedono ancora una revisione con dati e documentazione ufficiali accessibili:
non vengono dichiarate corrette o errate da questa analisi.