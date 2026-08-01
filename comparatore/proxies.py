"""Estensione dello storico di un fondo con uno strumento piu' anziano.

Il problema
-----------
Gli ETF UCITS sono giovani: VWCE quota dal 2019, VUSA dal 2012. Nessuna fonte
puo' inventare dati che non esistono. L'unico modo per vedere come si sarebbe
comportato un portafoglio nel 2000 o nel 1987 e' ricostruire il periodo
precedente con uno strumento che a quell'epoca c'era gia', e **dichiararlo**.

Total return, non prezzo
------------------------
La scelta del proxy e' meno ovvia di quanto sembri. Misurato su finestra comune:

    VFINX (fondo)  CAGR 11,44%     <- dividendi reinvestiti
    ^GSPC (indice) CAGR  9,56%     <- solo prezzo
    divario                1,89 punti l'anno

Su quarant'anni quel divario e' un fattore due sul montante finale. Lo stesso
vale per l'indice MSCI World `^990100-USD-STRD`, che nonostante il nome resta
indietro di 2,01 punti l'anno rispetto a un fondo mondiale total return.

Per questo i proxy predefiniti sono vecchie classi di fondi, che con
`auto_adjust` sono serie total return, e non indici di prezzo. Gli indici a
storico piu' lungo restano selezionabili a mano, segnalati per quello che sono.

Trattamento delle commissioni
-----------------------------
Il TER del fondo si aggiunge al tratto ricostruito **solo** quando il proxy e'
un indice total return, che per costruzione non ha costi. Un proxy che e' un
fondo ha gia' il proprio TER dentro il NAV, e sottrarlo di nuovo ripeterebbe
l'errore di doppio conteggio. Su un indice di solo prezzo non si applica nulla:
i dividendi mancanti pesano gia' piu' del TER.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass

import pandas as pd

# Distanza massima fra il primo dato reale del fondo e l'ultima quotazione utile
# del proxy. Oltre questa soglia l'ancoraggio non e' affidabile.
MAX_ANCHOR_GAP_DAYS = 45


@dataclass(frozen=True)
class ProxyDef:
    symbol: str
    label: str
    kind: str  # "fondo" | "indice"
    total_return: bool
    currency: str  # forzata: alcuni indici non dichiarano la valuta
    since: str  # prima data disponibile, informativa
    note: str = ""

    @property
    def applies_ter(self) -> bool:
        """Se il TER del fondo va addebitato al tratto ricostruito."""
        return self.kind == "indice" and self.total_return

    @property
    def caveat(self) -> str:
        if not self.total_return:
            return (
                "indice di solo prezzo: il tratto ricostruito esclude i dividendi "
                "e sottostima il rendimento"
            )
        return ""


# Proxy predefiniti: total return, storico lungo, verificati.
CATALOG: dict[str, ProxyDef] = {
    "VFINX": ProxyDef("VFINX", "S&P 500 (Vanguard 500, TR)", "fondo", True, "USD", "1980-01-02"),
    "VTSMX": ProxyDef("VTSMX", "USA total market (TR)", "fondo", True, "USD", "1992-04-27"),
    # Vanguard Total World. VTWSX, la classe a fondo comune, avrebbe la stessa
    # storia ma si ferma al 2019: da evitare come proxy, perche' per un ETF nato
    # dopo quella data l'ancoraggio userebbe un valore vecchio di anni.
    "VT": ProxyDef("VT", "Azionario mondiale (TR)", "fondo", True, "USD", "2008-06-26"),
    "VGTSX": ProxyDef("VGTSX", "Internazionale ex USA (TR)", "fondo", True, "USD", "1996-04-29"),
    "VEURX": ProxyDef("VEURX", "Europa (TR)", "fondo", True, "USD", "1990-06-18"),
    "VEIEX": ProxyDef("VEIEX", "Mercati emergenti (TR)", "fondo", True, "USD", "1994-05-04"),
    "VBMFX": ProxyDef(
        "VBMFX", "Obbligazionario aggregato USA (TR)", "fondo", True, "USD", "1986-12-11"),
    "QQQ": ProxyDef("QQQ", "Nasdaq 100 (TR)", "fondo", True, "USD", "1999-03-10"),
    "^SP500TR": ProxyDef("^SP500TR", "S&P 500 Total Return", "indice", True, "USD", "1988-01-04"),
    # Indici di solo prezzo: piu' storico, ma sottostimano. Solo su scelta esplicita.
    "^GSPC": ProxyDef(
        "^GSPC", "S&P 500 (solo prezzo)", "indice", False, "USD", "1927-12-30",
        note="massima profondita' disponibile",
    ),
    "^990100-USD-STRD": ProxyDef(
        "^990100-USD-STRD", "MSCI World (solo prezzo)", "indice", False, "USD",
        "1972-01-03", note="massima profondita' disponibile",
    ),
    "^NDX": ProxyDef(
        "^NDX", "Nasdaq 100 (solo prezzo)", "indice", False, "USD", "1985-10-01"
    ),
}

# Riconoscimento dal nome del fondo. L'ordine conta: prima i casi specifici.
_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"nasdaq|ndx\b", re.I), "QQQ"),
    (re.compile(r"emerging|emergent|\bem\b", re.I), "VEIEX"),
    (re.compile(r"euro\s*stoxx|\beurope|europa", re.I), "VEURX"),
    (re.compile(r"aggregate|\bbond|obbligaz|treasury|govie", re.I), "VBMFX"),
    (re.compile(r"s&p\s*500|sp\s*500|s&p500", re.I), "VFINX"),
    (re.compile(r"total\s*(stock)?\s*market|crsp\s*us", re.I), "VTSMX"),
    (re.compile(r"all[-\s]?world|acwi|all\s*country|msci\s*world|developed\s*world|global",
                re.I), "VT"),
    (re.compile(r"\bworld\b|mondiale|globale", re.I), "VT"),
    (re.compile(r"ex[-\s]?us|international|internazionale", re.I), "VGTSX"),
    (re.compile(r"\busa\b|united\s*states|\bus\b|statiuniti|stati\s*uniti", re.I), "VFINX"),
]


def suggest_proxy(fund_name: str, symbol: str = "") -> ProxyDef | None:
    """Proxy proposto in base al nome del fondo, o None se nessuno convince.

    Volutamente prudente: meglio non proporre nulla che accoppiare un settoriale
    o un fondo con copertura valutaria a un indice che non lo rappresenta.
    """
    haystack = f"{fund_name} {symbol}".strip()
    if not haystack:
        return None
    for pattern, key in _PATTERNS:
        if pattern.search(haystack):
            return CATALOG[key]
    return None


def alternatives_for(proxy: ProxyDef | None) -> list[ProxyDef]:
    """Proxy con piu' storico dello stesso mercato, da offrire come scelta."""
    if proxy is None:
        return []
    family = {
        "VFINX": ["^SP500TR", "^GSPC"],
        "VT": ["^990100-USD-STRD"],
        "QQQ": ["^NDX"],
    }.get(proxy.symbol, [])
    return [CATALOG[s] for s in family]


# --------------------------------------------------------------------------
# Innesto
# --------------------------------------------------------------------------


@dataclass
class Extension:
    series: pd.Series  # serie completa: ricostruita + reale
    splice_date: pd.Timestamp  # primo giorno di dati reali
    reconstructed_days: int
    proxy: ProxyDef


def extend_with_proxy(
    fund: pd.Series,
    proxy_series: pd.Series,
    proxy: ProxyDef,
    ter: float = 0.0,
) -> Extension | None:
    """Prolunga `fund` all'indietro con `proxy_series`.

    Entrambe le serie devono gia' essere nella stessa valuta. L'ancoraggio e'
    sul primo giorno di dati reali, cosi' la giunzione e' continua e il tratto
    ricostruito conserva i rendimenti del proxy invece dei suoi livelli.
    """
    if fund is None or fund.empty or proxy_series is None or proxy_series.empty:
        return None

    fund = fund.dropna().sort_index()
    proxy_series = proxy_series.dropna().sort_index()
    start = fund.index[0]

    before = proxy_series.loc[proxy_series.index < start]
    if before.empty:
        # Il proxy non e' piu' anziano del fondo: non c'e' niente da ricostruire.
        return None

    # Valore del proxy nel punto di giunzione: l'ultimo disponibile a quella
    # data o prima, perche' i calendari di borsa non coincidono.
    at_splice = proxy_series.loc[proxy_series.index <= start]
    if at_splice.empty or at_splice.iloc[-1] == 0:
        return None

    anchor_date = at_splice.index[-1]
    # Un proxy che ha smesso di quotare prima della nascita del fondo
    # ancorerebbe su un valore vecchio di mesi o anni, e l'intero tratto
    # ricostruito ne uscirebbe traslato di un fattore arbitrario. Meglio non
    # ricostruire affatto che ricostruire male.
    if (start - anchor_date).days > MAX_ANCHOR_GAP_DAYS:
        return None

    anchor_value = float(at_splice.iloc[-1])
    first_value = float(fund.iloc[0])

    # F(t) = F(T) * I(t)/I(T) * (1 - ter)^(-(T-t)/anno)
    #
    # Il fattore del TER e' a esponente negativo perche' si guarda indietro: un
    # fondo che replica l'indice perde il TER ogni anno, quindi tanto piu' si
    # risale nel tempo tanto piu' alto doveva essere il suo NAV rispetto a una
    # semplice riscalatura dell'indice. Per t -> T l'esponente tende a zero e il
    # raccordo con il primo dato reale e' continuo per costruzione.
    #
    # Non si riusa `apply_annual_fee` di engine.py: quella ancora il fattore al
    # primo giorno della serie, qui il riferimento e' la giunzione.
    reconstructed = before / anchor_value * first_value
    if proxy.applies_ter and ter:
        years_back = (anchor_date - before.index).days.to_numpy() / 365.25
        reconstructed = reconstructed * (1.0 - ter) ** (-years_back)

    extended = pd.concat([reconstructed, fund])
    extended = extended[~extended.index.duplicated(keep="last")].sort_index()

    return Extension(
        series=extended,
        splice_date=start,
        reconstructed_days=len(reconstructed),
        proxy=proxy,
    )


def fetch_proxy_series(
    proxy: ProxyDef, start: dt.date, end: dt.date, base_ccy: str
) -> tuple[pd.Series | None, dt.date | None]:
    """Scarica il proxy e lo converte in `base_ccy`.

    Restituisce anche la data da cui la conversione e' possibile: i proxy sono
    tutti in dollari e i cambi ufficiali BCE partono dal 1999, quindi con una
    valuta base diversa da USD la ricostruzione non puo' scendere sotto quella
    soglia per quanto profondo sia il proxy.
    """
    from .fx import convert_currency
    from .sources.yahoo import YahooSource

    series = YahooSource().prices(proxy.symbol, start, end, base_ccy)
    if series is None or series.empty:
        return None, None

    # Alcuni indici non dichiarano la valuta e verrebbero scartati: si forza
    # quella nota dal catalogo.
    currency = series.currency or proxy.currency

    frame = series.prices.to_frame(name=proxy.symbol)
    res = convert_currency(frame, {proxy.symbol: currency}, base_ccy, start, end)
    if proxy.symbol not in res.prices.columns:
        return None, None

    converted = res.prices[proxy.symbol].dropna()
    if converted.empty:
        return None, None
    return converted, res.truncated.get(proxy.symbol)
