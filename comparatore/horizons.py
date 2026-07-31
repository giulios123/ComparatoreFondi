"""Rendimenti del portafoglio sulle stesse finestre usate da COVIP.

Perche' un modulo a parte
-------------------------
I rendimenti COVIP non sono "ultimi dieci anni a partire da oggi": sono finestre
chiuse e datate, `2016-2025`, ferme al 31 dicembre dell'ultimo anno pubblicato.
Confrontarle con il decennio 2016-2026 del portafoglio sarebbe un confronto
falsato, e non di poco: e' proprio la coda recente quella che sposta di piu' i
numeri, e la si conterebbe da una parte sola.

Qui il rendimento del portafoglio si calcola sulle finestre lette dal file
COVIP, e quando il portafoglio non le copre per intero il risultato e' `None` -
cioe' "non disponibile" - invece di un numero calcolato su un periodo piu' corto
che sembrerebbe confrontabile senza esserlo.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd

# I calendari di borsa non contengono il 1° gennaio ne' il 31 dicembre, e i
# fondi non quotano tutti i giorni: si concede qualche giorno agli estremi prima
# di dichiarare che la finestra non e' coperta.
TOLLERANZA_GIORNI = 15


def copre_finestra(
    series: pd.Series,
    inizio: dt.date,
    fine: dt.date,
    tolleranza: int = TOLLERANZA_GIORNI,
) -> bool:
    """Vero se la serie copre davvero l'intera finestra."""
    if series is None or series.empty:
        return False
    valid = series.dropna()
    if valid.empty:
        return False
    margine = pd.Timedelta(days=tolleranza)
    return (
        valid.index[0] <= pd.Timestamp(inizio) + margine
        and valid.index[-1] >= pd.Timestamp(fine) - margine
    )


def rendimento_su_finestra(
    series: pd.Series,
    inizio: dt.date,
    fine: dt.date,
    tolleranza: int = TOLLERANZA_GIORNI,
) -> float | None:
    """Rendimento medio annuo composto sulla finestra, o None se non coperta.

    Il valore e' una frazione (0.0447 per 4,47%), coerente con il resto del
    pacchetto; i dati COVIP sono in punti percentuali e vanno divisi per cento.
    """
    if not copre_finestra(series, inizio, fine, tolleranza):
        return None

    finestra = series.dropna().loc[pd.Timestamp(inizio) : pd.Timestamp(fine)]
    if len(finestra) < 2:
        return None

    primo, ultimo = float(finestra.iloc[0]), float(finestra.iloc[-1])
    if primo <= 0:
        return None

    anni = (finestra.index[-1] - finestra.index[0]).days / 365.25
    if anni <= 0:
        return None
    return (ultimo / primo) ** (1.0 / anni) - 1.0


def rendimenti_per_orizzonte(
    series: pd.Series,
    finestre: dict[int, tuple[dt.date, dt.date]],
    tolleranza: int = TOLLERANZA_GIORNI,
) -> dict[int, float | None]:
    """Rendimento annuo del portafoglio per ciascun orizzonte COVIP."""
    return {
        anni: rendimento_su_finestra(series, inizio, fine, tolleranza)
        for anni, (inizio, fine) in finestre.items()
    }


def capitale_finale(
    rendimento_annuo: float | None,
    anni: int,
    capitale: float,
    versamento_periodico: float = 0.0,
    rate_annue: int = 12,
) -> float | None:
    """Montante dopo `anni` a un tasso annuo composto.

    Con `versamento_periodico` > 0 diventa la formula dell'annualita': oltre
    al capitale iniziale che cresce come sempre, ad ogni fine periodo si
    aggiunge una rata che da quel momento cresce anch'essa al tasso annuo -
    la stessa convenzione (rata versata a fine periodo, non a inizio) usata
    dal motore di backtest per il PAC in `comparatore.engine.simulate`.
    `rate_annue` e' il numero di rate in un anno (12 mensile, 4 trimestrale,
    1 annuale).
    """
    if rendimento_annuo is None:
        return None
    montante = capitale * (1.0 + rendimento_annuo) ** anni
    if versamento_periodico:
        n = anni * rate_annue
        tasso_periodo = (1.0 + rendimento_annuo) ** (1.0 / rate_annue) - 1.0
        if tasso_periodo == 0:
            montante += versamento_periodico * n
        else:
            montante += versamento_periodico * ((1.0 + tasso_periodo) ** n - 1.0) / tasso_periodo
    return montante


def costo_cumulato(
    isc_annuo: float | None,
    anni: int,
    capitale: float,
    versamento_periodico: float = 0.0,
    rate_annue: int = 12,
) -> float | None:
    """Quanto pesa un ISC costante su `anni`, a parita' di rendimento lordo.

    Confronta il montante senza costi con quello eroso dall'ISC: e' la stessa
    logica con cui l'applicazione mostra l'impatto del TER sui fondi comuni.

    Con `versamento_periodico` > 0 vale per un piano di accumulo, dove la
    scorciatoia - sommare tutto il versato e trattarlo come se fosse sul conto
    dal primo giorno - sovrastima il costo di parecchio: la rata versata al
    nono anno subisce un anno di costi, non dieci. Qui si confronta il piano
    non eroso (tasso zero: capitale piu' le rate) con lo stesso piano cresciuto
    a `-isc`, cioe' eroso per il solo tempo in cui ogni rata e' investita.
    """
    if isc_annuo is None:
        return None
    lordo = capitale_finale(0.0, anni, capitale, versamento_periodico, rate_annue)
    netto = capitale_finale(-isc_annuo, anni, capitale, versamento_periodico, rate_annue)
    return lordo - netto
