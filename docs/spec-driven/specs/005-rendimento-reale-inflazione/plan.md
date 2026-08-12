# 005 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Creare una fonte Eurostat isolata in un modulo puro. Scarica l'HICP mensile
"all items" come indice, conserva osservazioni e metadati nella cache e
restituisce un risultato strutturato con area, date e diagnostica.

Il calcolo normalizza l'indice a 1 sulla prima data comune e divide ogni curva
nominale per il fattore dei prezzi. Il valore reale e' quindi espresso nel
potere d'acquisto dell'inizio del periodo reale. Le osservazioni mensili sono
portate in avanti fra una pubblicazione e la successiva, ma non prima del primo
dato e non oltre il mese coperto dall'ultima osservazione ufficiale.

Per il PAC si deflazionano separatamente saldo e versato cumulato. Le metriche
di rendimento si calcolano sul NAV reale, non sul saldo che incorpora nuovi
versamenti.

Riferimenti ufficiali:

- https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-introduction
- https://ec.europa.eu/eurostat/web/hicp/information-data

## File toccati

| File | Cosa cambia |
|---|---|
| `comparatore/inflation.py` | Client Eurostat, parsing HICP, diagnostica e deflazione delle curve |
| `comparatore/cache.py` | Solo se serve un helper generico per serie mensili con metadati |
| `comparatore/prefs.py` | Area HICP preferita e opt-in, con degrado silenzioso |
| `app.py` | Controlli, confronto nominale/reale, date fonte e retry |
| `comparatore/locales/{it,en,fr,de}.py` | Testi e nomi delle aree supportate |
| `tests/test_inflation.py` | Fixture Eurostat, cambi di base, copertura e formule |
| `tests/test_prefs.py` | Persistenza e compatibilita' delle preferenze |

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Sottrarre il tasso medio annuo dal CAGR | Non rispetta la capitalizzazione ne' le variazioni mensili e gestisce male il PAC |
| Usare l'inflazione USA perche' ha serie lunghe facili da trovare | Non descrive il potere d'acquisto di un utente europeo |
| Deducere il paese dalla valuta base | EUR non distingue Italia, Germania, Francia o area euro |
| Inserire manualmente un unico tasso futuro | Trasforma un'analisi storica in previsione, contro il vincolo esplicito |
| Retro-riempire l'indice prima della prima osservazione | Attribuisce a un periodo dati che non esistono |

## Rischi

- Eurostat puo' cambiare struttura o base dell'indice: fixture e normalizzazione
  relativa devono separare il livello assoluto dal fattore di crescita.
- Il mese corrente e' normalmente incompleto: mostrare l'ultimo mese evita che
  un valore portato avanti sembri aggiornato a oggi.
- Deflazionare il saldo PAC senza deflazionare il versato produrrebbe un
  confronto incoerente: entrambi vanno espressi alla stessa data base.
- Un errore Eurostat non deve finire nella guardia dei fondi assenti, che resta
  riservata alle holding investite.

## Verifica

1. Fixture con HICP costante: curva reale identica alla nominale.
2. Fixture con inflazione nota: valore e CAGR reali confrontati con formula
   chiusa.
3. PAC sintetico: saldo e versato reali coerenti, metriche sul NAV.
4. Storici sfalsati e ultimo mese mancante: nessun backfill e date visibili.
5. Errore HTTP/parsing: backtest nominale invariato.
6. Unittest, ruff, `git diff --check` e smoke offline dell'interfaccia.
