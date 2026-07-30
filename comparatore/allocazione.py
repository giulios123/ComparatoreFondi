"""Classificazione degli strumenti per classe di attivo, area e settore.

Il problema
-----------
Nessuna delle fonti di prezzo dice che cos'e' uno strumento. `Instrument` porta
il simbolo, il nome, la valuta e il TER: `quote_type` distingue un ETF da un
fondo comune, non un azionario da un obbligazionario. Per rispondere alla
domanda "come e' ripartito il mio portafoglio" serve un dato che l'applicazione
non ha, e che va quindi ricostruito.

Due sorgenti, in ordine di qualita':

  EODHD    espone `Asset_Allocation`, `World_Regions` e `Sector_Weights` dentro
           la risposta `/fundamentals` che la fonte gia' scarica per il TER.
           Sono percentuali vere, granulari, e coprono bene gli ETF.
  il nome  quando la chiave EODHD non c'e' o lo strumento non e' coperto, il
           nome del fondo e' l'unico indizio disponibile. "Xtrackers II Eurozone
           Government Bond" dice tutto quello che serve, "LU0292107645" niente.

L'utente puo' sempre correggere: la classificazione automatica e' un punto di
partenza, non un verdetto.

Distribuzioni, non etichette
----------------------------
Ogni dimensione e' un dizionario `{bucket: quota}` che somma a 1, non
un'etichetta sola. Un MSCI World non e' "100% Nord America" e un LifeStrategy
60/40 non e' "100% Bilanciato": schiacciare quei fondi su una casella sola
cancellerebbe proprio l'informazione che si sta cercando. Una scelta manuale e'
il caso degenere `{scelta: 1.0}`, quindi il codice che somma le quote e' uno
solo per entrambe le origini.

Il vocabolario dei bucket e' in italiano perche' sono etichette di
visualizzazione, non identificatori interni: finiscono tali e quali nelle
legende dei grafici e nelle tendine, come le chiavi italiane restituite da
`metrics.summarize()`.
"""

from __future__ import annotations

import re

# Le tre dimensioni classificate. L'ordine e' quello in cui compaiono
# nell'interfaccia.
DIMENSIONI = ("classe", "area", "settore")

# Bucket di ripiego: si usa quando nessun indizio convince. Non e' un errore,
# e' un'informazione ("questo strumento non lo so classificare") che nel grafico
# resta visibile invece di sparire in un totale che non chiude.
NON_CLASSIFICATO = "Non classificato"

# Sentinella della tendina, come `AUTO` per la colonna Fonte e `NO_PROXY` per
# la colonna Proxy storico: dice "lascia decidere alla classificazione
# automatica" e conserva la distribuzione dedotta, che puo' avere piu' bucket.
AUTOMATICA = "(automatica)"

CLASSI = [
    "Azionario",
    "Obbligazionario",
    "Liquidità",
    "Materie prime",
    "Immobiliare",
    NON_CLASSIFICATO,
]

AREE = [
    "Globale",
    "Nord America",
    "Europa",
    "Italia",
    "Giappone",
    "Asia-Pacifico",
    "Mercati emergenti",
    NON_CLASSIFICATO,
]

SETTORI = [
    "Diversificato",
    "Tecnologia",
    "Finanza",
    "Sanità",
    "Energia",
    "Industria",
    "Beni di consumo",
    "Utility",
    "Immobiliare",
    "Materiali",
    "Comunicazioni",
    NON_CLASSIFICATO,
]

BUCKET: dict[str, list[str]] = {
    "classe": CLASSI,
    "area": AREE,
    "settore": SETTORI,
}

# Opzioni delle tendine: la sentinella prima di tutto il resto.
OPZIONI: dict[str, list[str]] = {
    dimensione: [AUTOMATICA, *bucket] for dimensione, bucket in BUCKET.items()
}


# --------------------------------------------------------------------------
# Riconoscimento dal nome
# --------------------------------------------------------------------------

# Stesso idioma di `proxies._PATTERNS`: liste ordinate, prima i casi specifici,
# prima corrispondenza vince. Tabella separata da quella dei proxy perche' le
# due rispondono a domande diverse - li' "quale indice ricostruisce lo storico
# di questo fondo", qui "che cosa e' questo strumento" - e tenerle insieme
# significherebbe che rendere piu' prudente il backfill degrada la
# classificazione, e viceversa.

_CLASSI_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Monetari prima degli obbligazionari: "Treasury Bill" contiene "treasury".
    (re.compile(r"monetar|money\s*market|overnight|liquidit|t[-\s]?bill|"
                r"treasury\s*bill|cash", re.I), "Liquidità"),
    (re.compile(r"\bgold\b|\boro\b|silver|argento|commodit|materie\s*prime|"
                r"metal|petrol", re.I), "Materie prime"),
    (re.compile(r"\breit\b|real\s*estate|immobiliar|property", re.I), "Immobiliare"),
    (re.compile(r"\bbond|obbligaz|treasury|govie|\bgilt|fixed\s*income|"
                r"aggregate|\bbtp\b|\bbund\b|corporate\s*debt|high\s*yield",
                re.I), "Obbligazionario"),
    (re.compile(r"azionar|\bequity|\bstock|\bshare|msci|s&p|ftse|stoxx|nasdaq|"
                r"russell|topix|nikkei|\bdax\b|\bcac\b|\bmib\b|\bworld\b|"
                r"mondial|global|acwi", re.I), "Azionario"),
]

_AREE_PATTERNS: list[tuple[re.Pattern, str]] = [
    # "World ex-USA" va letto come globale, non come Nord America: senza questa
    # riga il pattern degli Stati Uniti piu' avanti lo catturerebbe.
    (re.compile(r"ex[-\s]?us(a)?\b|ex[-\s]?north\s*america|world\s*ex|"
                r"ex[-\s]?stati\s*uniti", re.I), "Globale"),
    (re.compile(r"\bitalia|\bitaly\b|\bmib\b|\bbtp\b", re.I), "Italia"),
    (re.compile(r"\bjapan|giappone|topix|nikkei", re.I), "Giappone"),
    (re.compile(r"emerging|emergent|\bem\b|\bcina\b|\bchina\b|\bindia\b|"
                r"\bbrasil|\bbrazil", re.I), "Mercati emergenti"),
    (re.compile(r"\busa\b|\bu\.?s\.?a\b|united\s*states|stati\s*uniti|"
                r"north\s*america|nord\s*america|s&p\s*500|sp\s*500|nasdaq|"
                r"russell|\bdow\b", re.I), "Nord America"),
    (re.compile(r"europ|euro\s*stoxx|eurozone|\bemu\b|\bdax\b|\bcac\b|"
                r"\bsmi\b|\bftse\s*100", re.I), "Europa"),
    (re.compile(r"pacific|asia|australia|australasia|corea|korea|taiwan",
                re.I), "Asia-Pacifico"),
    (re.compile(r"all[-\s]?world|acwi|all\s*country|msci\s*world|"
                r"developed\s*world|\bworld\b|mondial|global", re.I), "Globale"),
]

_SETTORI_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"technolog|tecnolog|semiconduct|software|\bit\s*sector|"
                r"information\s*tech|robotic|intelligenza\s*artificial|\bai\b",
                re.I), "Tecnologia"),
    (re.compile(r"financ|finanz|\bbank|insuranc|assicurat", re.I), "Finanza"),
    (re.compile(r"health|sanit|pharma|farmac|biotech|medical|medicin",
                re.I), "Sanità"),
    (re.compile(r"energy|energia|\boil\b|petrol|\bgas\b|clean\s*energ|"
                r"rinnovabil|renewable", re.I), "Energia"),
    (re.compile(r"industrial|industria|aerospace|aerospazial|defen[cs]e|difesa|"
                r"transport", re.I), "Industria"),
    (re.compile(r"consumer|consumi|beni\s*di\s*consumo|retail|\bfood\b|"
                r"beverage|luxur|lusso", re.I), "Beni di consumo"),
    (re.compile(r"utilit", re.I), "Utility"),
    (re.compile(r"\breit\b|real\s*estate|immobiliar|property", re.I), "Immobiliare"),
    (re.compile(r"material|materiali|mining|minerari|\bmetal|chemic|chimic",
                re.I), "Materiali"),
    (re.compile(r"communication|comunicazion|telecom|\bmedia\b", re.I),
     "Comunicazioni"),
]


def _primo(patterns: list[tuple[re.Pattern, str]], testo: str) -> str:
    for pattern, bucket in patterns:
        if pattern.search(testo):
            return bucket
    return ""


def classifica_da_nome(
    nome: str, symbol: str = "", quote_type: str = ""
) -> dict[str, dict[str, float]]:
    """Classificazione dedotta dal nome dello strumento.

    Volutamente prudente: nel dubbio restituisce `NON_CLASSIFICATO`, che
    nell'interfaccia si vede e si corregge, invece di un'etichetta plausibile ma
    sbagliata che nessuno andrebbe a controllare.

    Le tre dimensioni si valutano con tabelle separate perche' un nome porta
    spesso informazioni su una sola: "Eurozone Government Bond" dice la classe
    *e* l'area, "Consumer Staples" solo il settore. Una tabella unica con una
    tripla per riga costringerebbe a moltiplicare le combinazioni.
    """
    testo = f"{nome} {symbol}".strip()

    classe = _primo(_CLASSI_PATTERNS, testo) if testo else ""
    area = _primo(_AREE_PATTERNS, testo) if testo else ""
    settore = _primo(_SETTORI_PATTERNS, testo) if testo else ""

    # Un titolo singolo e' azionario per definizione, anche quando il nome non
    # contiene nessuna delle parole chiave (nessun pattern trova "Apple Inc.").
    if not classe and "EQUITY" in (quote_type or "").upper():
        classe = "Azionario"

    if not settore:
        # Il settore ha senso solo per l'azionario: chiedersi in che settore
        # investa un obbligazionario governativo non porta da nessuna parte.
        settore = "Diversificato" if classe == "Azionario" else NON_CLASSIFICATO

    return {
        "classe": {classe or NON_CLASSIFICATO: 1.0},
        "area": {area or NON_CLASSIFICATO: 1.0},
        "settore": {settore: 1.0},
    }


# --------------------------------------------------------------------------
# Traduzione dei blocchi EODHD
# --------------------------------------------------------------------------

_EODHD_CLASSI = {
    "stock us": "Azionario",
    "stock non-us": "Azionario",
    "stock non us": "Azionario",
    "stocks": "Azionario",
    "equity": "Azionario",
    "bond": "Obbligazionario",
    "bonds": "Obbligazionario",
    "fixed income": "Obbligazionario",
    "cash": "Liquidità",
    "realestate": "Immobiliare",
    "real estate": "Immobiliare",
    "commodity": "Materie prime",
    "commodities": "Materie prime",
}

_EODHD_AREE = {
    "north america": "Nord America",
    "united states": "Nord America",
    "canada": "Nord America",
    "united kingdom": "Europa",
    "europe developed": "Europa",
    "europe": "Europa",
    "eurozone": "Europa",
    "europe emerging": "Mercati emergenti",
    "asia emerging": "Mercati emergenti",
    "latin america": "Mercati emergenti",
    "africa/middle east": "Mercati emergenti",
    "africa middle east": "Mercati emergenti",
    "japan": "Giappone",
    "australasia": "Asia-Pacifico",
    "asia developed": "Asia-Pacifico",
}

_EODHD_SETTORI = {
    "basic materials": "Materiali",
    "materials": "Materiali",
    "consumer cyclicals": "Beni di consumo",
    "consumer cyclical": "Beni di consumo",
    "consumer defensive": "Beni di consumo",
    "consumer defensives": "Beni di consumo",
    "financial services": "Finanza",
    "financials": "Finanza",
    "realestate": "Immobiliare",
    "real estate": "Immobiliare",
    "communication services": "Comunicazioni",
    "energy": "Energia",
    "industrials": "Industria",
    "technology": "Tecnologia",
    "healthcare": "Sanità",
    "health care": "Sanità",
    "utilities": "Utility",
}

# Campi da cui leggere la quota, in ordine di preferenza. `Relative_to_Category`
# e' volutamente escluso: e' uno scarto rispetto alla media di categoria, non un
# peso, e sommarlo produrrebbe percentuali senza senso.
_CAMPI_QUOTA = ("Net_Assets_%", "Equity_%", "Long_%", "Weight_%")


def _numero(valore) -> float:
    """Quota percentuale da un valore EODHD, 0 quando non si riesce a leggerla.

    Il formato dei blocchi non e' documentato e cambia da un endpoint all'altro:
    a volte il valore e' un dizionario con la percentuale dentro, a volte una
    stringa con il simbolo di percentuale, a volte un numero. Si accettano tutte
    e tre le forme invece di sollevare, perche' una risposta inattesa deve
    costare al massimo una classificazione mancante, non un'eccezione a schermo.
    """
    if isinstance(valore, dict):
        for campo in _CAMPI_QUOTA:
            if campo in valore:
                return _numero(valore[campo])
        return 0.0
    if isinstance(valore, str):
        pulito = valore.strip().replace("%", "").replace(",", ".")
        try:
            return float(pulito)
        except ValueError:
            return 0.0
    if isinstance(valore, (int, float)) and not isinstance(valore, bool):
        return float(valore)
    return 0.0


def _normalizza(quote: dict[str, float]) -> dict[str, float]:
    """Riporta le quote a somma 1, scartando quelle nulle o negative."""
    positive = {b: v for b, v in quote.items() if v > 0}
    totale = sum(positive.values())
    if totale <= 0:
        return {}
    return {b: v / totale for b, v in positive.items()}


def _traduci(blocco, mappa: dict[str, str]) -> dict[str, float]:
    """Da un blocco EODHD o Yahoo alla distribuzione sui bucket italiani.

    Yahoo (`funds_data`) usa chiavi `snake_case` ("consumer_cyclical"), EODHD
    parole separate da spazio ("consumer cyclical"): normalizzando
    l'underscore in spazio le due fonti condividono la stessa mappa dei
    settori invece di doverne mantenere due. Nessuna chiave EODHD contiene un
    underscore, quindi la normalizzazione non cambia nulla per quella fonte.
    """
    if not isinstance(blocco, dict):
        return {}
    quote: dict[str, float] = {}
    for chiave, valore in blocco.items():
        chiave_norm = str(chiave).strip().lower().replace("_", " ")
        bucket = mappa.get(chiave_norm, NON_CLASSIFICATO)
        quota = _numero(valore)
        if quota > 0:
            quote[bucket] = quote.get(bucket, 0.0) + quota
    return _normalizza(quote)


def classifica_da_eodhd(etf_data) -> dict[str, dict[str, float]]:
    """Classificazione dai blocchi `ETF_Data` di EODHD.

    Restituisce solo le dimensioni effettivamente presenti: un ETF
    obbligazionario non ha `Sector_Weights`, e inventargli un settore sarebbe
    peggio che lasciarlo vuoto e far intervenire il ripiego sul nome.
    """
    if not isinstance(etf_data, dict):
        return {}
    trovate = {
        "classe": _traduci(etf_data.get("Asset_Allocation"), _EODHD_CLASSI),
        "area": _traduci(etf_data.get("World_Regions"), _EODHD_AREE),
        "settore": _traduci(etf_data.get("Sector_Weights"), _EODHD_SETTORI),
    }
    return {d: q for d, q in trovate.items() if q}


# Chiavi di `funds_data.asset_classes` di yfinance, gia' minuscole.
# "otherposition" e' deliberatamente assente: non e' ne' azionario ne'
# obbligazionario ne' liquidita', ed e' proprio il bucket che finisce al 100%
# sui fondi che yfinance non sa scomporre (oro fisico, monetari) - vedi la
# guardia in `classifica_da_yahoo`.
_YAHOO_CLASSI = {
    "stockposition": "Azionario",
    "preferredposition": "Azionario",
    "bondposition": "Obbligazionario",
    "convertibleposition": "Obbligazionario",
    "cashposition": "Liquidità",
}


def classifica_da_yahoo(
    asset_classes: dict | None, sector_weightings: dict | None
) -> dict[str, dict[str, float]]:
    """Classificazione dal modulo `funds_data` di yfinance (senza chiave).

    Stessa idea di `classifica_da_eodhd`: solo le dimensioni presenti, mai
    inventate. Una guardia in piu' su `classe`, non necessaria per EODHD: qui
    "otherPosition" (oro fisico, monetari - vedi `_YAHOO_CLASSI`) puo' arrivare
    al 100%, e restituirlo come classe prevalente sovrascriverebbe una classe
    corretta gia' dedotta dal nome, perche' `unisci` fa vincere la fonte non
    vuota sul ripiego.
    """
    classe = _traduci(asset_classes, _YAHOO_CLASSI)
    settore = _traduci(sector_weightings, _EODHD_SETTORI)
    trovate: dict[str, dict[str, float]] = {}
    if classe and etichetta_prevalente(classe) != NON_CLASSIFICATO:
        trovate["classe"] = classe
    if settore:
        trovate["settore"] = settore
    return trovate


# --------------------------------------------------------------------------
# Stima geografica dalle prime posizioni
# --------------------------------------------------------------------------
#
# Fuori da `DIMENSIONI` di proposito: non e' correggibile a mano (il
# vocabolario sarebbe una trentina di paesi, non le poche voci di una
# tendina) e ha sempre un bucket residuo (RESTO_FONDO), che non avrebbe senso
# in una tendina "scegli il paese esatto". Vive di fianco alle altre tre
# dimensioni nella scheda Bilanciamento, non dentro `risolvi`/`OPZIONI`.

DIMENSIONE_PAESE = "paese"

PAESI = [
    "Stati Uniti", "Taiwan", "Cina", "Giappone", "Corea del Sud", "India",
    "Regno Unito", "Francia", "Germania", "Svizzera", "Italia", "Spagna",
    "Paesi Bassi", "Canada", "Australia", "Hong Kong", "Brasile", "Messico",
    "Danimarca", "Svezia", "Norvegia",
]

# Quota delle prime posizioni non coperta dalla stima: le prime 10 di un
# fondo ampio (VWCE, EIMI...) coprono un quinto o un quarto del patrimonio, il
# resto resta sconosciuto e va dichiarato come tale, non rinormalizzato sulle
# sole 10 - altrimenti le percentuali sarebbero calcolate su un fondo piu'
# piccolo di quello vero. Stesso principio di NON_CLASSIFICATO in `aggrega`.
RESTO_FONDO = "Resto del fondo"

# Suffisso di borsa Yahoo -> paese. Copre le piazze osservate nelle prime
# posizioni degli ETF globali e dei mercati emergenti piu' comuni; un
# suffisso assente da questa mappa finisce in NON_CLASSIFICATO, mai indovinato.
_SUFFISSO_PAESE = {
    "TW": "Taiwan",
    "HK": "Hong Kong",
    "KS": "Corea del Sud",
    "NS": "India",
    "BO": "India",
    "L": "Regno Unito",
    "SW": "Svizzera",
    "AX": "Australia",
    "AS": "Paesi Bassi",
    "DE": "Germania",
    "MC": "Spagna",
    "PA": "Francia",
    "MI": "Italia",
    "T": "Giappone",
    "TO": "Canada",
    "SS": "Cina",
    "SZ": "Cina",
    "CO": "Danimarca",
    "ST": "Svezia",
    "OL": "Norvegia",
    "SA": "Brasile",
    "MX": "Messico",
}


def paesi_da_posizioni(holdings: list[dict] | None) -> dict[str, float]:
    """Stima geografica dai simboli delle prime posizioni di un fondo.

    E' una stima, non una ripartizione: copre solo le prime posizioni
    restituite da `funds_data` (un quinto o un quarto del patrimonio sui fondi
    ampi), il resto finisce dichiaratamente in `RESTO_FONDO` invece di essere
    spalmato sulle altre voci o ignorato.

    Un simbolo senza suffisso di borsa (`NVDA`, `AAPL`) e' Stati Uniti solo se
    e' fatto di sole lettere: i codici numerici delle piazze asiatiche
    (`005935` per una classe di Samsung, `00939` per una banca cinese, come
    li restituisce Yahoo) non hanno suffisso ma non sono americani, e devono
    finire in `NON_CLASSIFICATO` invece che erroneamente negli Stati Uniti.
    """
    if not holdings:
        return {}

    quote: dict[str, float] = {}
    coperto = 0.0
    for h in holdings:
        try:
            quota = float((h or {}).get("quota") or 0.0)
        except (TypeError, ValueError):
            continue
        if quota <= 0:
            continue
        coperto += quota
        symbol = str((h or {}).get("symbol") or "")
        if "." in symbol:
            suffisso = symbol.rsplit(".", 1)[1].upper()
            paese = _SUFFISSO_PAESE.get(suffisso, NON_CLASSIFICATO)
        elif symbol.isalpha():
            paese = "Stati Uniti"
        else:
            paese = NON_CLASSIFICATO
        quote[paese] = quote.get(paese, 0.0) + quota

    if not quote:
        return {}
    resto = max(0.0, 1.0 - coperto)
    if resto > 0:
        quote[RESTO_FONDO] = quote.get(RESTO_FONDO, 0.0) + resto
    return _normalizza(quote)


# --------------------------------------------------------------------------
# Composizione e aggregazione
# --------------------------------------------------------------------------


def unisci(
    principale: dict[str, dict[str, float]],
    ripiego: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    """Completa `principale` con `ripiego` sulle dimensioni che gli mancano."""
    out = dict(ripiego)
    for dimensione, quote in (principale or {}).items():
        if quote:
            out[dimensione] = quote
    return out


def risolvi(auto: dict[str, float] | None, manuale: str = "") -> dict[str, float]:
    """Distribuzione effettiva di una dimensione.

    Una scelta manuale vince e collassa tutto su un bucket solo: e' esattamente
    quello che l'utente ha chiesto scegliendola. `AUTOMATICA` e la stringa vuota
    lasciano la distribuzione dedotta, che puo' avere piu' bucket.
    """
    if manuale and manuale != AUTOMATICA:
        return {manuale: 1.0}
    return dict(auto) if auto else {NON_CLASSIFICATO: 1.0}


def aggrega(
    pesi: dict[str, float],
    distribuzioni: dict[str, dict[str, float]],
) -> dict[str, float]:
    """Ripartizione del portafoglio su una dimensione.

    `pesi` associa a ogni strumento la sua quota di portafoglio, `distribuzioni`
    la sua ripartizione sui bucket. I pesi vengono normalizzati a 1 come fa
    `engine.simulate()`, cosi' il totale chiude al 100% anche quando nella
    tabella sommano a 97 o a 103. Uno strumento senza distribuzione finisce
    tutto in `NON_CLASSIFICATO` invece di sparire, altrimenti le percentuali
    mostrate sarebbero calcolate su un portafoglio piu' piccolo di quello vero.

    Il risultato e' ordinato per quota decrescente: e' l'ordine in cui va letto.
    """
    positivi = {k: p for k, p in pesi.items() if p > 0}
    totale = sum(positivi.values())
    if totale <= 0:
        return {}

    out: dict[str, float] = {}
    for chiave, peso in positivi.items():
        quota_strumento = peso / totale
        dist = _normalizza(distribuzioni.get(chiave) or {})
        if not dist:
            dist = {NON_CLASSIFICATO: 1.0}
        for bucket, quota in dist.items():
            out[bucket] = out.get(bucket, 0.0) + quota_strumento * quota

    return dict(sorted(out.items(), key=lambda kv: kv[1], reverse=True))


def etichetta_prevalente(dist: dict[str, float] | None) -> str:
    """Il bucket con la quota maggiore, per chi ha spazio per una parola sola."""
    if not dist:
        return NON_CLASSIFICATO
    return max(dist.items(), key=lambda kv: kv[1])[0]


def descrivi(dist: dict[str, float] | None, max_voci: int = 3) -> str:
    """Distribuzione in forma leggibile: "Nord America 62% · Europa 18% · +3".

    Con un bucket solo restituisce l'etichetta nuda, senza il "100%" che non
    aggiunge nulla.
    """
    if not dist:
        return NON_CLASSIFICATO
    voci = sorted(dist.items(), key=lambda kv: kv[1], reverse=True)
    if len(voci) == 1:
        return voci[0][0]
    testo = " · ".join(f"{b} {q * 100:.0f}%" for b, q in voci[:max_voci])
    resto = len(voci) - max_voci
    return f"{testo} · +{resto}" if resto > 0 else testo
