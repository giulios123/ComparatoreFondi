# 001 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

L'etichetta più lunga è di **tre caratteri in tutte e quattro le lingue**
(`10a`, `20a`, `Max`, `10J`, `20J`). Garantire tre caratteri di larghezza
equivale quindi a garantire che nessuna vada a capo: il criterio 1 e il
criterio 2 si soddisfano con la stessa misura.

Streamlit non espone alcuna opzione per dire "questa etichetta non si spezza",
quindi serve CSS. Perché non diventi un precedente che si allarga da solo, va
agganciato a un elemento preciso: un `st.container(key="preset_periodo")` fa
emettere a Streamlit la classe `st-key-preset_periodo`, che è il modo
documentato di selezionare un contenitore specifico.

Tre regole, dentro quella classe:

```css
.st-key-preset_periodo [data-testid="stHorizontalBlock"] { gap: 0.4rem; }
.st-key-preset_periodo .stButton p      { white-space: nowrap; }
.st-key-preset_periodo .stButton button { min-width: 3ch;
                                          padding-left: .25rem;
                                          padding-right: .25rem; }
```

`min-width` in `ch` e non in pixel perché l'unità segue il font effettivo: la
garanzia dei tre caratteri regge anche se il tema cambia corpo o famiglia. Il
`gap` più stretto e il padding ridotto sono spazio restituito ai pulsanti:
rimandano il punto in cui il `min-width` deve sfondare la colonna per tenere
fede alla garanzia, ed è ciò che soddisfa il criterio 3.

Il layout su due file da tre e da due **resta**: è la prima difesa, il CSS è la
seconda.

## File toccati

| File | Cosa cambia |
|---|---|
| `app.py` (dopo `set_page_config`) | Blocco `<style>`, con il commento che spiega perché esiste |
| `app.py` (barra laterale, preset) | I due `st.columns(3)` finiscono dentro `st.container(key="preset_periodo")`; commento riscritto |
| `tests/test_app_sintassi.py` | Due guardie nuove (criterio 5) |
| `docs/memory-bank/02-decisioni.md` | Decisione 18: è la prima volta che l'app usa CSS custom |

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Accorciare le etichette (`10` senza suffisso) | Perde l'informazione dell'unità, e in tedesco `10J` resta comunque di tre caratteri: non risolve |
| Una tendina al posto dei pulsanti | Aggiunge un clic all'azione più frequente della barra laterale, per risolvere un problema di larghezza |
| `white-space: nowrap` su tutti i `.stButton` | Selettore globale: cambierebbe l'aspetto di pulsanti che oggi vanno a capo legittimamente (criterio 4) |
| Larghezza minima della barra laterale | Non è configurabile in Streamlit, e comunque toglierebbe all'utente una scelta che è sua |

## Rischi

- **Dipendenza dal DOM di Streamlit.** `st-key-…` è documentato; `.stButton` e
  `[data-testid="stHorizontalBlock"]` no. Un aggiornamento maggiore di Streamlit
  può cambiarli senza preavviso. Mitigazione: il blocco è uno solo e ben
  commentato, e la verifica a occhio sulla barra stretta va rifatta dopo un
  aggiornamento maggiore. La guardia nei test protegge il legame fra contenitore
  e regola, **non** il fatto che Streamlit continui a emettere quelle classi.
- **Una traduzione futura più lunga di tre caratteri** tornerebbe a spezzarsi.
  Mitigazione: una guardia che controlla la lunghezza delle etichette in tutti e
  quattro i cataloghi.

## Verifica

1. `uv run python -m unittest discover -s tests -p "test_*.py"`.
2. Avviare l'app, portare la barra laterale al minimo, confrontare con la stessa
   schermata a fix disattivato.
3. Ripetere in tedesco, che ha le etichette più larghe.
4. Controllare che i pulsanti fuori dalla barra laterale non siano cambiati.
