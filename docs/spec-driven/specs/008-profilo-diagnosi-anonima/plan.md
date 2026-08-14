# 008 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Tenere separati tre contratti puri:

1. `InvestorProfile`, con validazione e persistenza locale;
2. `PortfolioFinding`, prodotto da regole deterministiche;
3. `AnonymousReport`, serializzazione allowlist destinata alla sola anteprima
   o alla futura spec 009.

`InvestorProfile` sara' versionato e composto soltanto da campi facoltativi:
orizzonte 1-100 anni, obiettivo, perdita tollerata, prelievi, limite per
posizione, preferenza di semplicita'/bilanciamento/diversificazione,
obbligazioni ammesse ed esclusioni guidate per classe e settore. Le esclusioni
saranno codici stabili, mai note libere.

La serializzazione anonima non parte dal dizionario completo del portafoglio
per poi togliere campi: costruisce un nuovo oggetto da una allowlist di campi
ammessi. La mappa fra `asset_N` e simboli reali vive soltanto in memoria nella
sessione e non entra nel payload.

Le regole iniziali coprono soltanto fatti supportati dai moduli esistenti:
dati/TER mancanti, concentrazioni oltre limiti dichiarati, drawdown storico
oltre tolleranza, categorie escluse, obbligazioni non ammesse, storico corto
rispetto all'orizzonte e fatti informativi su correlazioni, overlap, rolling,
benchmark e inflazione. Ogni soglia non personale e' descrittiva e non
etichettata come adeguatezza.

Il risultato e' ordinato stabilmente e contiene solo azioni dichiarative,
verificabili nell'app: controllo di un dato mancante, confronto con un peso
limite o scenario simmetrico per una coppia. Non muta lo stato.

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/profile.py` | Modello versionato, validazione e persistenza locale con permessi ristretti |
| `comparatore/diagnostics.py` | Rilievi, regole, evidenze e azioni di simulazione |
| `comparatore/privacy.py` | Allowlist anonima, token `asset_N` e controlli dei campi vietati |
| `desktop/launcher.py` | Percorso dati del profilo nel bundle, come chiavi e preferenze |
| `app.py` | Editor profilo, rapporto deterministico e anteprima payload |
| `comparatore/locales/{it,en,fr,de}.py` | Campi, spiegazioni e rilievi |
| `tests/test_profile.py` | Validazione, permessi, file assente/corrotto |
| `tests/test_diagnostics.py` | Regole e stabilita' del risultato |
| `tests/test_privacy.py` | Allowlist e tentativi di contaminazione con identificatori |

Riuso esplicito: modello degradabile di `prefs.py`/`keys.py`, risultati di
`metrics.py`, `comparative.py`, `inflation.py`, `overlap.py` e provenienze gia'
presenti nel portafoglio.

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Salvare il profilo nel JSON del portafoglio | Lo rende facile da condividere per errore insieme a dati che devono restare personali |
| Inviare il JSON completo e chiedere al modello di ignorare i campi sensibili | Il confine privacy dipenderebbe dal prompt invece che dal codice |
| Usare soglie universali per perdita e concentrazione | Trasforma preferenze personali in verita' generali non dichiarate |
| Far generare all'AI i rilievi di base | Rende variabile la diagnosi e impedisce test con formule chiuse |
| Conservare una mappa persistente asset-token | Permetterebbe di correlare analisi diverse senza necessita' |

## Rischi

- Testi liberi nelle esclusioni possono contenere nomi: inviare soltanto codici
  o categorie selezionate, non note libere.
- Una nuova chiave del portafoglio potrebbe sfuggire a una blacklist: l'allowlist
  evita il problema per costruzione.
- Un rilievo severo puo' sembrare una raccomandazione normativa: testi e
  struttura devono parlare di coerenza con il profilo dichiarato, non di
  adeguatezza certificata.
- La cancellazione del profilo deve essere indipendente da cache e portafogli.

## Verifica

1. Profili validi, incompleti, corrotti e cancellati.
2. Regole con soglie personali e senza soglia.
3. Payload contaminato intenzionalmente con nomi, ticker, ISIN, importi e path:
   nessun valore vietato compare nell'output.
4. Stabilita' del rapporto a parita' di input.
5. App senza profilo: backtest invariato e rilievi puramente descrittivi.
6. Unittest, ruff, `git diff --check` e verifica visuale nelle quattro lingue.
