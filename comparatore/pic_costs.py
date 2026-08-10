"""Stima delle commissioni di carico e scarico per un PIC.

Il motore di backtest resta volutamente estraneo alle commissioni di ordine:
una commissione iniziale non e' un costo annuo e inserirla nelle serie
storiche cambierebbe il significato delle metriche esistenti. Questo modulo
calcola quindi un prospetto separato, mantenendo i pesi obiettivo e usando i
montanti finali gia' prodotti dal motore.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum


class TransactionFeeMode(str, Enum):
    NONE = "none"
    FIXED = "fixed"
    PERCENTAGE = "percentage"


class PicCostError(ValueError):
    """Regola o budget incompatibile con un prospetto PIC."""


@dataclass(frozen=True)
class TransactionFeeRule:
    """Una regola applicata a ogni ordine del portafoglio.

    `amount` e' nella valuta del portafoglio per la modalita' fissa; `rate` e'
    una frazione (0.01 = 1%) per la modalita' percentuale. Minimo e massimo
    valgono solo per la percentuale e sono opzionali.
    """

    mode: TransactionFeeMode = TransactionFeeMode.NONE
    amount: float = 0.0
    rate: float = 0.0
    minimum: float = 0.0
    maximum: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.mode, TransactionFeeMode):
            try:
                object.__setattr__(self, "mode", TransactionFeeMode(self.mode))
            except ValueError as exc:
                raise PicCostError("Tipo di commissione non riconosciuto.") from exc

    def validate(self) -> None:
        values = (self.amount, self.rate, self.minimum)
        if any(not math.isfinite(float(value)) or float(value) < 0 for value in values):
            raise PicCostError("I costi devono essere numeri finiti e non negativi.")
        if self.maximum is not None and (
            not math.isfinite(float(self.maximum)) or float(self.maximum) < 0
        ):
            raise PicCostError("Il costo massimo deve essere finito e non negativo.")
        if self.maximum is not None and self.maximum < self.minimum:
            raise PicCostError("Il costo massimo non puo' essere inferiore al minimo.")
        if self.mode is TransactionFeeMode.PERCENTAGE and self.rate > 1:
            raise PicCostError("La percentuale della commissione non puo' superare il 100%.")

    def fee(self, notional: float, *, decimals: int = 2) -> float:
        """Restituisce la commissione per un ordine di `notional`.

        La regola restituisce l'addebito contrattuale anche quando supera il
        controvalore: e' l'estimatore a bloccare un carico impossibile, invece
        di nascondere un minimo sproporzionato dietro un troncamento.
        """
        self.validate()
        value = float(notional)
        if not math.isfinite(value) or value < 0:
            raise PicCostError("Il controvalore dell'ordine deve essere finito e non negativo.")
        if self.mode is TransactionFeeMode.NONE:
            raw = 0.0
        elif self.mode is TransactionFeeMode.FIXED:
            raw = self.amount
        else:
            raw = max(value * self.rate, self.minimum)
            if self.maximum is not None:
                raw = min(raw, self.maximum)
        return round(raw, decimals)


@dataclass(frozen=True)
class PicCostLine:
    symbol: str
    notional: float
    fee: float


@dataclass(frozen=True)
class PicCostEstimate:
    """Prospetto completo, separato dal risultato del backtest."""

    budget: float
    buy_cost: float
    investable: float
    final_without_costs: float
    final_before_sell: float
    sell_cost: float
    final_net: float
    total_cost: float
    difference: float
    buy_lines: tuple[PicCostLine, ...] = field(default_factory=tuple)
    sell_lines: tuple[PicCostLine, ...] = field(default_factory=tuple)


def _decimals(currency: str) -> int:
    return 0 if currency.upper() == "JPY" else 2


def _solve_investable(
    budget: float, weights: dict[str, float], rule: TransactionFeeRule, decimals: int
) -> tuple[float, tuple[PicCostLine, ...]]:
    """Trova il capitale investibile per cui investito + carico = budget."""
    rule.validate()
    if budget <= 0 or not math.isfinite(budget):
        raise PicCostError("Il budget PIC deve essere finito e maggiore di zero.")
    if any(
        not math.isfinite(float(weight)) or float(weight) < 0
        for weight in weights.values()
    ):
        raise PicCostError("I pesi devono essere finiti e non negativi.")
    active = [(str(symbol), float(weight)) for symbol, weight in weights.items() if weight > 0]
    if not active or sum(weight for _, weight in active) <= 0:
        raise PicCostError("Serve almeno un peso positivo per stimare i costi PIC.")
    total_weight = sum(weight for _, weight in active)
    active = [(symbol, weight / total_weight) for symbol, weight in active]

    def lines(invested: float) -> tuple[PicCostLine, ...]:
        return tuple(
            PicCostLine(symbol, invested * weight, rule.fee(invested * weight, decimals=decimals))
            for symbol, weight in active
        )

    # La funzione e' monotona. La ricerca binaria resta corretta anche con
    # minimi e arrotondamento alle cifre monetarie.
    low, high = 0.0, budget
    for _ in range(100):
        middle = (low + high) / 2
        candidate = lines(middle)
        if middle + sum(line.fee for line in candidate) <= budget:
            low = middle
        else:
            high = middle

    invested = round(low, decimals)
    buy_lines = lines(invested)
    buy_cost = round(sum(line.fee for line in buy_lines), decimals)
    # Corregge l'ultimo centesimo dovuto all'arrotondamento della ricerca.
    while invested + buy_cost > budget + 10 ** (-(decimals + 1)):
        invested = round(invested - 10 ** -decimals, decimals)
        if invested < 0:
            raise PicCostError("Le commissioni di carico esauriscono il budget PIC.")
        buy_lines = lines(invested)
        buy_cost = round(sum(line.fee for line in buy_lines), decimals)

    if any(line.fee > line.notional for line in buy_lines):
        raise PicCostError("Una commissione di carico supera il controvalore dell'ordine.")
    if invested <= 0 or invested + buy_cost > budget + 10 ** (-(decimals + 1)):
        raise PicCostError("Le commissioni di carico esauriscono il budget PIC.")
    return invested, buy_lines


def estimate_pic_costs(
    budget: float,
    weights: dict[str, float],
    final_values: dict[str, float],
    buy_rule: TransactionFeeRule | None = None,
    sell_rule: TransactionFeeRule | None = None,
    *,
    currency: str = "EUR",
) -> PicCostEstimate:
    """Stima carico/scarico a partire dai montanti finali senza commissioni."""
    buy_rule = buy_rule or TransactionFeeRule()
    sell_rule = sell_rule or TransactionFeeRule()
    sell_rule.validate()
    decimals = _decimals(currency)
    investable, buy_lines = _solve_investable(budget, weights, buy_rule, decimals)
    buy_cost = round(sum(line.fee for line in buy_lines), decimals)

    for value in final_values.values():
        if not math.isfinite(float(value)) or float(value) < 0:
            raise PicCostError("I montanti finali devono essere finiti e non negativi.")
    final_without_costs = round(
        sum(float(final_values.get(symbol, 0.0)) for symbol in weights), decimals
    )
    scale = investable / budget
    final_lines = []
    for symbol, weight in weights.items():
        if weight <= 0:
            continue
        notional = max(0.0, float(final_values.get(symbol, 0.0)) * scale)
        fee = sell_rule.fee(notional, decimals=decimals)
        final_lines.append(PicCostLine(symbol, notional, fee))
    sell_lines = tuple(final_lines)
    sell_cost = round(sum(line.fee for line in sell_lines), decimals)
    final_before_sell = round(sum(line.notional for line in sell_lines), decimals)
    final_net = round(final_before_sell - sell_cost, decimals)
    total_cost = round(buy_cost + sell_cost, decimals)
    difference = round(final_without_costs - final_net, decimals)
    return PicCostEstimate(
        budget=round(float(budget), decimals),
        buy_cost=buy_cost,
        investable=round(investable, decimals),
        final_without_costs=final_without_costs,
        final_before_sell=final_before_sell,
        sell_cost=sell_cost,
        final_net=final_net,
        total_cost=total_cost,
        difference=difference,
        buy_lines=buy_lines,
        sell_lines=sell_lines,
    )


__all__ = [
    "PicCostError",
    "PicCostEstimate",
    "PicCostLine",
    "TransactionFeeMode",
    "TransactionFeeRule",
    "estimate_pic_costs",
]
