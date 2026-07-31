"""Pesi percentuali del portafoglio: l'invariante e' che sommano sempre a 100.

Il problema
-----------
Prima di questo modulo i pesi erano semplici float liberi: si poteva digitare
60 e 60 su due fondi, ottenendo un totale di 120% che il motore di backtest
normalizzava silenziosamente a 60/40 (vedi `engine.simulate`). L'utente
credeva di aver impostato un'allocazione diversa da quella davvero usata.

Qui i pesi vengono sempre fatti passare per una di queste funzioni, che
garantiscono la somma esatta a 100.00 per costruzione: non serve piu'
validare "il totale e' 100?" a valle, perche' non puo' essere altrimenti.

Nessun import di Streamlit: la logica e' testabile da sola, l'applicazione
allo stato di sessione resta in `app.py` (stesso principio di
`portfolio_io.py`).
"""

from __future__ import annotations


def arrotonda_a_100(pesi: list[float], decimali: int = 2) -> list[float]:
    """Arrotonda ogni peso, scaricando il residuo sul peso maggiore.

    `round(100 / 3, 2) * 3 == 99.99`: arrotondare ogni valore indipendentemente
    non garantisce che la somma torni esatta. Il residuo (in genere un
    centesimo) e' invisibile su un numero a due decimali, quindi va assegnato
    al fondo piu' grande piuttosto che distribuito.
    """
    if not pesi:
        return []
    arrotondati = [round(p, decimali) for p in pesi]
    residuo = round(100.0 - sum(arrotondati), decimali)
    if residuo:
        indice_max = max(range(len(arrotondati)), key=lambda i: arrotondati[i])
        arrotondati[indice_max] = round(arrotondati[indice_max] + residuo, decimali)
    return arrotondati


def uguali(n: int) -> list[float]:
    """Ripartizione paritaria fra `n` fondi, somma esatta a 100."""
    if n <= 0:
        return []
    return arrotonda_a_100([100.0 / n] * n)


def ridistribuisci(pesi: list[float], fissi: dict[int, float]) -> list[float]:
    """Impone i pesi in `fissi` (indice -> valore) e ridistribuisce il residuo
    sugli altri indici in proporzione ai loro pesi attuali fra loro.

    Se la somma dei valori fissi supera 100, vengono riscalati proporzionalmente
    fra loro cosi' da occupare l'intero 100% (gli indici liberi restano a zero).
    Se gli indici liberi sono attualmente tutti a zero, il residuo viene diviso
    in parti uguali fra loro invece che azzerato.
    """
    n = len(pesi)
    if n == 0:
        return []
    if n == 1:
        return [100.0]

    valori_fissi = {i: max(0.0, v) for i, v in fissi.items() if 0 <= i < n}
    somma_fissi = sum(valori_fissi.values())
    if somma_fissi > 100:
        fattore = 100.0 / somma_fissi
        valori_fissi = {i: v * fattore for i, v in valori_fissi.items()}
        somma_fissi = 100.0

    liberi = [i for i in range(n) if i not in valori_fissi]
    residuo = 100.0 - somma_fissi

    risultato = [0.0] * n
    for i, v in valori_fissi.items():
        risultato[i] = v

    if liberi:
        somma_liberi = sum(pesi[i] for i in liberi)
        if somma_liberi > 0:
            for i in liberi:
                risultato[i] = residuo * pesi[i] / somma_liberi
        else:
            quota = residuo / len(liberi)
            for i in liberi:
                risultato[i] = quota

    return arrotonda_a_100(risultato)


def rinormalizza(pesi: list[float]) -> list[float]:
    """Riscala i pesi mantenendo i rapporti fra loro, somma esatta a 100.

    Usata dopo la rimozione di un fondo (i rimasti mantengono le proporzioni
    reciproche) e dopo l'import di un portafoglio salvato in precedenza.
    """
    n = len(pesi)
    if n == 0:
        return []
    somma = sum(pesi)
    if somma <= 0:
        return uguali(n)
    return arrotonda_a_100([p * 100.0 / somma for p in pesi])


def da_importi(importi: list[float]) -> tuple[float, list[float]]:
    """Dagli importi in valuta base al totale e ai pesi corrispondenti."""
    totale = sum(importi)
    if totale <= 0:
        return 0.0, uguali(len(importi))
    return totale, arrotonda_a_100([imp * 100.0 / totale for imp in importi])


def importi(pesi: list[float], capitale: float) -> list[float]:
    """Dai pesi (percentuali, somma 100) al relativo importo in valuta base."""
    return [p / 100.0 * capitale for p in pesi]
