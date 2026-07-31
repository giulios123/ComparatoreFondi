"""Traduzioni dell'interfaccia: rilevamento della lingua e funzione `traduci()`.

Rinominare cio' che e' effimero, congelare cio' che e' persistito. Le chiavi
di `comparatore.metrics.summarize()` sono effimere - dict -> colonne del
DataFrame -> `column_config`, mai su disco - e sono ID inglesi stabili scelti
a quello scopo (`final_value`, `cagr`, ...). I bucket di
`comparatore.allocazione`, i nomi delle fonti e i valori dell'enum
`Rebalance` sono invece persistiti - dentro `st.session_state.selected` e nel
file esportato da `comparatore.portfolio_io` - e restano stringhe italiane o
codici stabili non toccati da qui: si traducono solo a video tramite le
funzioni `etichetta_*` sotto, che pescano dalle mappe di visualizzazione dei
moduli in `comparatore.locales`. Un DataFrame o un file esportato restano
quindi identici a prescindere dalla lingua dell'interfaccia.
"""

from __future__ import annotations

import locale as _locale
import os
import re
import subprocess
import sys

from comparatore.locales import de, en, fr, it

LINGUE = {"it": "Italiano", "en": "English", "fr": "Français", "de": "Deutsch"}
DEFAULT = "it"

_CATALOGHI = {"it": it, "en": en, "fr": fr, "de": de}

# Separatore delle migliaia per `fmt_money()`: con `format="%.0f"` (nessun
# decimale) e' l'unico aspetto della formattazione numerica che cambia.
SEPARATORE_MIGLIAIA = {"it": ".", "en": ",", "fr": " ", "de": "."}

# Formato di `st.date_input` e dei pattern `strftime`/hovertemplate Plotly.
FORMATO_DATA = {"it": "DD/MM/YYYY", "en": "MM/DD/YYYY", "fr": "DD/MM/YYYY", "de": "DD.MM.YYYY"}
FORMATO_DATA_STRFTIME = {"it": "%d/%m/%Y", "en": "%m/%d/%Y", "fr": "%d/%m/%Y", "de": "%d.%m.%Y"}
# Mese e anno per le etichette degli assi temporali: numerico e non `%b`, che
# Plotly scriverebbe comunque in inglese senza caricarne il locale.
FORMATO_MESE_ANNO = {"it": "%m/%Y", "en": "%m/%Y", "fr": "%m/%Y", "de": "%m.%Y"}


def _catalogo(lingua: str):
    return _CATALOGHI.get(lingua, _CATALOGHI[DEFAULT])


def _lingue_da_accept_language(header: str) -> list[str]:
    """Codici lingua in ordine di preferenza da un'intestazione Accept-Language."""
    voci: list[tuple[float, str]] = []
    for parte in (header or "").split(","):
        parte = parte.strip()
        if not parte:
            continue
        pezzi = parte.split(";")
        codice = pezzi[0].strip().split("-")[0].lower()
        qualita = 1.0
        for p in pezzi[1:]:
            p = p.strip()
            if p.startswith("q="):
                try:
                    qualita = float(p[2:])
                except ValueError:
                    qualita = 0.0
        if codice:
            voci.append((qualita, codice))
    voci.sort(key=lambda x: -x[0])
    out: list[str] = []
    for _, codice in voci:
        if codice not in out:
            out.append(codice)
    return out


def locale_di_sistema() -> str:
    """Locale del sistema operativo, per il rilevamento nel bundle desktop.

    Su macOS `locale.getlocale()` non porta nessuna informazione utile -
    restituisce `('C', 'UTF-8')` a prescindere dalla lingua impostata nelle
    Preferenze di Sistema, e `getdefaultlocale()` e' deprecata. La lingua
    vive solo in `AppleLanguages`: si legge con `defaults read -g
    AppleLanguages`, un best-effort che degrada in silenzio se il comando
    non c'e' o impiega troppo.
    """
    try:
        codice, _ = _locale.getlocale()
    except Exception:
        codice = None
    if codice and codice != "C":
        return codice
    if sys.platform == "darwin":
        try:
            risultato = subprocess.run(
                ["defaults", "read", "-g", "AppleLanguages"],
                capture_output=True, text=True, timeout=2,
            )
            trovato = re.search(r'"?([a-zA-Z]{2})[-_]?', risultato.stdout)
            if trovato:
                return trovato.group(1)
        except Exception:
            pass
    return os.environ.get("LANG", "") or ""


def rileva(browser_locale: str = "", accept_language: str = "", locale_sistema: str = "") -> str:
    """Lingua da usare la prima volta: locale del browser (`st.context.locale`,
    cioe' `navigator.language` - copre sia l'uso web sia il bundle desktop,
    che apre comunque il browser di sistema) -> intestazione
    Accept-Language (cintura, per i runtime dove il primo segnale manca) ->
    locale di sistema -> italiano.
    """
    codice_browser = (browser_locale or "").strip().lower().split("-")[0]
    if codice_browser in LINGUE:
        return codice_browser
    for candidato in _lingue_da_accept_language(accept_language):
        if candidato in LINGUE:
            return candidato
    codice = (locale_sistema or "").strip().lower()
    for candidato in re.split(r"[_.\-]", codice):
        if candidato in LINGUE:
            return candidato
    return DEFAULT


def traduci(lingua: str, chiave: str, **kwargs) -> str:
    """Stringa tradotta per `chiave`; ripiega sull'italiano e poi sulla
    chiave stessa, cosi' una voce mancante non blocca mai l'interfaccia.
    """
    testo = _catalogo(lingua).MESSAGGI.get(chiave)
    if testo is None:
        testo = _CATALOGHI[DEFAULT].MESSAGGI.get(chiave, chiave)
    if kwargs:
        try:
            return testo.format(**kwargs)
        except (KeyError, IndexError):
            return testo
    return testo


def etichetta_termine(lingua: str, termine: str) -> str:
    """Traduzione di un termine di dominio: bucket di allocazione (classe,
    area, settore, paese), sentinelle come "(automatica)" o "Non
    classificato". Il termine stesso resta la chiave interna - vedi il
    modulo docstring.
    """
    return _catalogo(lingua).TERMINI.get(termine, termine)


def etichetta_metrica(lingua: str, nome: str) -> str:
    return _catalogo(lingua).METRICHE.get(nome, nome)


def etichetta_fonte(lingua: str, nome: str) -> str:
    return _catalogo(lingua).FONTI.get(nome, nome)


def etichetta_esito(lingua: str, codice: str) -> str:
    return _catalogo(lingua).ESITI.get(codice, codice)


def etichetta_ribilanciamento(lingua: str, valore) -> str:
    chiave = valore.value if hasattr(valore, "value") else str(valore)
    return _catalogo(lingua).RIBILANCIAMENTO.get(chiave, chiave)


def formato_data(lingua: str) -> str:
    return FORMATO_DATA.get(lingua, FORMATO_DATA[DEFAULT])


def formato_data_strftime(lingua: str) -> str:
    return FORMATO_DATA_STRFTIME.get(lingua, FORMATO_DATA_STRFTIME[DEFAULT])


def formato_mese_anno(lingua: str) -> str:
    return FORMATO_MESE_ANNO.get(lingua, FORMATO_MESE_ANNO[DEFAULT])


def separatore_migliaia(lingua: str) -> str:
    return SEPARATORE_MIGLIAIA.get(lingua, SEPARATORE_MIGLIAIA[DEFAULT])
