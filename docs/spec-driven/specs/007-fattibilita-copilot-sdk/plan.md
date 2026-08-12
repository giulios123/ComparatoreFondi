# 007 · Piano

Riferimento: [`spec.md`](spec.md)

## Approccio

Eseguire uno spike fuori dal percorso applicativo. Prima si prova l'SDK in un
ambiente isolato e con un payload fittizio; poi si costruisce un programma
PyInstaller minimo che avvia il client ma non contiene Streamlit. Solo se
questi passaggi riescono si valuta lo stesso avvio dentro il bundle reale.

Il client crea una sessione senza tool e richiede un oggetto JSON con schema
banale. Un wrapper registra soltanto stato, tempi, classe dell'errore e modello,
mai prompt completi, output sensibili o token. I casi senza login/rete/quota
vengono riprodotti separatamente.

La documentazione GitHub consultata in fase di specifica e' il punto di
partenza, non una prova di compatibilita' del nostro bundle:

- https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/authenticate
- https://docs.github.com/en/copilot/how-tos/copilot-sdk/setup

## File toccati

| File | Cosa cambia |
|---|---|
| `scripts/copilot_sdk_probe.py` | Sonda senza dati reali, nessun tool, output redatto |
| `docs/spikes/copilot-sdk-desktop.md` | Versioni, prerequisiti, prove, errori e decisione finale |
| `desktop/copilot-probe.spec` | Solo se necessario per isolare il test PyInstaller; non entra nel workflow release |
| `pyproject.toml`, `uv.lock` | Solo dopo esito favorevole, e inizialmente in un gruppo opzionale dedicato |
| `THIRD_PARTY_NOTICES.txt`, `THIRD_PARTY_LICENSES.json` | Rigenerati, mai modificati a mano, se la dipendenza viene mantenuta |
| `docs/memory-bank/02-decisioni.md` | Decisione go/no-go con il rimando alla prova |

## Alternative scartate

| Alternativa | Perché no |
|---|---|
| Integrare subito il client in `app.py` | Mescola fattibilita', UX, privacy e packaging; un fallimento non avrebbe una causa isolata |
| Usare direttamente un PAT GitHub Models | Non verifica se la sottoscrizione Copilot gia' pagata e' riutilizzabile |
| Provare soltanto da sorgente | Il prodotto viene distribuito come bundle e il rischio principale e' proprio il runtime esterno |
| Concedere tool al modello per vedere se "funziona meglio" | Non servono all'analisi richiesta e ampliano inutilmente il confine di sicurezza |
| Salvare login/token nel file delle chiavi attuale | Le credenziali GitHub hanno ciclo di vita e storage nel keychain gestiti dal relativo client |

## Rischi

- Una prova interattiva non e' riproducibile in CI: separare build senza login
  e verifica manuale autenticata, dichiarando quale criterio copre ciascuna.
- L'SDK puo' cambiare rapidamente: annotare versioni esatte e data della prova.
- Il runtime puo' essere disponibile su macOS ma non su Windows: nessun go
  generale finche' entrambe le piattaforme di release non hanno un percorso.
- Nuove dipendenze possono avere licenze o binari non ammessi: eseguire l'audit
  prima di mantenerle nel lock.

## Verifica

1. Eseguire la sonda da sorgente con login valido e payload sintetico.
2. Ripetere senza credenziali e senza rete; registrare classi di errore.
3. Costruire e avviare il probe PyInstaller su macOS e Windows.
4. Controllare processi/binari esterni richiesti e dimensione del bundle.
5. Eseguire audit licenze se la dipendenza viene aggiunta.
6. Scrivere il documento di esito con una decisione unica e verificabile.
7. Eseguire suite, ruff e `git diff --check` sul repository rimasto.
