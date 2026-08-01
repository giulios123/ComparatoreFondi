# Panoramica

## Cosa fa

Comparatore Fondi risponde a una domanda: **quanto sarebbe diventato il mio
capitale**, se lo avessi investito in questi strumenti, con questi pesi, in
questo periodo — e **quanto se ne sono presi i costi**.

Tre cose che l'app fa e che gli strumenti gratuiti tipicamente non fanno:

1. **Mette il TER in primo piano.** I NAV pubblicati sono già al netto delle
   commissioni; l'app ricostruisce anche la curva *lorda* e mostra la distanza
   fra le due. È un numero in euro, non una percentuale astratta.
2. **Confronta con i fondi pensione italiani.** Negoziali, aperti e PIP, con i
   dati ufficiali COVIP: non sono strumenti di mercato e non compaiono su
   nessuna API di quotazioni.
3. **Dichiara la provenienza di ogni dato.** Quale fonte ha risposto per quale
   strumento, e se un'allocazione è dedotta dal nome invece che letta.

## Per chi

Chi investe per sé e vuole capire cosa sta comprando — non un professionista
con un terminale. Da qui discendono l'interfaccia in quattro lingue, le
spiegazioni a video accanto a ogni metrica invece che in un manuale, e la
scelta di impacchettare l'app in un eseguibile per chi non ha Python.

## Cosa **non** fa

Sono non-obiettivi espliciti, non funzionalità mancanti:

- **Non dà consigli finanziari** e non suggerisce cosa comprare.
- **Non fa previsioni.** Tutto quello che mostra è passato. La "serie sintetica"
  usata per i fondi pensione è una retta a rendimento costante e serve solo a
  rendere confrontabile il *punto d'arrivo*: non è un andamento e non va data in
  pasto al motore di backtest (`comparatore/covip.py`, `serie_sintetica()`).
- **Non gestisce ordini, conti o posizioni reali.**
- **Non modella la fiscalità.** I rendimenti sono lordi d'imposta, e per i fondi
  pensione — che hanno un trattamento fiscale diverso — l'app lo dice a video.
- **Non promette dati completi.** Le fonti gratuite hanno buchi, e l'app
  preferisce dichiararli (`n/d`, provenienza, "ricostruito") piuttosto che
  riempirli.

## Glossario

| Termine | Significato |
|---|---|
| **TER** | *Total Expense Ratio*: costo annuo corrente di un fondo/ETF, già scontato dai NAV pubblicati |
| **ISC** | *Indicatore Sintetico dei Costi*: l'equivalente del TER per la previdenza complementare, pubblicato da COVIP |
| **COVIP** | L'autorità di vigilanza sui fondi pensione italiani; pubblica albo, rendimenti e ISC come open data (CC BY 4.0) |
| **NAV** | Valore della quota di un fondo |
| **PIC** | *Piano di Investimento di Capitale*: tutto il capitale versato all'inizio |
| **PAC** | *Piano di Accumulo di Capitale*: versamenti periodici nel tempo |
| **XIRR** | Tasso interno di rendimento con flussi a date irregolari — la metrica giusta per un PAC, dove il CAGR non basta |
| **CAGR** | Rendimento medio annuo composto |
| **Drawdown** | Perdita dal massimo precedente; il *max drawdown* è la peggiore subita nel periodo |
| **Proxy** | Strumento con storia più lunga usato per estendere all'indietro la serie di un fondo giovane |
| **Orizzonte COVIP** | Finestra di anni solari interi (1, 3, 5, 10, 20) su cui COVIP pubblica i rendimenti medi annui |
