# 001 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [x] Blocco `<style>` dopo `st.set_page_config()` in `app.py`, con il commento
      che spiega perché il CSS esiste e perché `3ch` e non pixel
- [x] I due `st.columns(3)` dei preset dentro `st.container(key="preset_periodo")`
- [x] Riscritto il commento della sezione preset: descriveva solo la prima
      difesa (il layout 3+2), che da sola non basta

## Test

- [x] `test_preset_periodo_non_vanno_a_capo` — contenitore con `key` e regole
      CSS presenti insieme: separati non servono a niente
- [x] `test_etichette_preset_stanno_in_tre_caratteri` — nessuna etichetta di
      preset supera i 3 caratteri, in nessuno dei quattro cataloghi

## Verifica dei criteri di accettazione

- [x] **1 · Nessuna etichetta su più di una riga, a barra al minimo.**
      Misurato nel DOM a 176 px: `1a`, `5a`, `10a`, `20a`, `Max` → 1 riga
      ciascuna. Confronto con il fix disattivato: `10a` → 2 righe, `20a` → 2,
      `Max` → 2.
- [x] **2 · Vale in tedesco.** Stessa misura con l'interfaccia in Deutsch:
      `1J`, `5J`, `10J`, `20J`, `Max` → 1 riga ciascuna.
- [x] **3 · Le etichette restano dentro il pulsante.** Il primo tentativo con
      il solo `min-width` le faceva tracimare oltre il bordo a 176 px; ridotti
      `gap` e padding, rientrano. Verificato a occhio in italiano e tedesco.
- [x] **4 · Nessun altro pulsante cambia aspetto.** Il CSS è agganciato a
      `.st-key-preset_periodo`, che esiste solo attorno ai preset; controllato a
      video che "⚖️ Pesi uguali" e "🗑️ Svuota" siano invariati.
- [x] **5 · Una regressione viene intercettata dai test.** Le due guardie sopra.

## Chiusura

- [x] `uv run python -m unittest discover -s tests -p "test_*.py"` passa (144 test)
- [x] Aggiornato `docs/memory-bank/03-stato-attuale.md`
- [x] Aggiunta la decisione 18 a `docs/memory-bank/02-decisioni.md` — il CSS
      custom è un precedente e andava messo per iscritto
- [x] Aggiornato lo stato in cima a `spec.md`
