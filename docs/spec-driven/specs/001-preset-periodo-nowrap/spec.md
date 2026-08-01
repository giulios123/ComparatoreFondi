# 001 · I preset di periodo non devono andare a capo

*Stato: fatta — agosto 2026*

## Problema

Nella barra laterale, sotto "Periodo", cinque pulsanti impostano il periodo del
backtest con un clic: `1a`, `5a`, `10a`, `20a`, `Max`. La barra laterale di
Streamlit si trascina per cambiarne la larghezza, e stringendola i pulsanti
diventano più stretti della propria etichetta: `10a` si spezza in `10` sopra e
`a` sotto, `Max` in `Ma` e `x`. Il pulsante raddoppia in altezza e l'etichetta
smette di essere leggibile a colpo d'occhio.

Un tentativo c'era già stato: i cinque pulsanti erano stati spostati da una fila
sola a due file da tre e da due, così ciascuno partisse con quasi il doppio
dello spazio. Ha alzato la soglia, non l'ha eliminata — sotto una certa
larghezza il problema si ripresenta identico.

## Chi lo incontra

Chi lavora su schermi stretti o affianca l'app ad altro, e restringe la barra
laterale per guadagnare spazio al grafico. I preset di periodo sono fra i
comandi più usati della barra: è la strada rapida per "guardiamo gli ultimi
dieci anni".

## Criteri di accettazione

1. Con la barra laterale portata alla sua larghezza minima, **nessuna delle
   cinque etichette** (`1a`, `5a`, `10a`, `20a`, `Max`) occupa più di una riga.
2. Vale in **tutte e quattro le lingue**, incluso il tedesco, dove le etichette
   sono `1J`, `5J`, `10J`, `20J`, `Max`.
3. Le etichette restano dentro il proprio pulsante: non tracimano oltre il bordo
   visibile.
4. Nessun altro pulsante dell'applicazione cambia aspetto.
5. Una regressione futura viene intercettata dai test, non dall'utente.

## Non-obiettivi

- **Non** si tocca il comportamento dei pulsanti: fanno esattamente quello che
  facevano.
- **Non** si affronta il resto della barra laterale, dove le etichette lunghe
  vanno a capo (e va bene così: "Valore iniziale del portafoglio" su due righe
  si legge, `10a` spezzato no).
- **Non** si introduce un tema o un foglio di stile generale.

## Vincoli

- La libreria `comparatore/` non c'entra: è un problema di sola interfaccia
  (decisione 2 del memory bank).
- `app.py` non è importabile: qualunque guardia va scritta come ispezione del
  sorgente in `tests/test_app_sintassi.py` (decisione 16).
- Ogni etichetta a video passa da `t()` e vive in quattro cataloghi
  (decisione 7): una soluzione che dipende dal testo italiano non è una
  soluzione.

## Domande aperte

Nessuna. *(Richiesta iniziale: «basterebbe lasciare almeno 3 caratteri di spazio
prima di andare a capo» — è il criterio 1, tradotto in una misura.)*
