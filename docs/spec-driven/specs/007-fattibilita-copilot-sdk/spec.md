# 007 · Fattibilità del Copilot SDK nel desktop locale

*Stato: approvata — 12 agosto 2026*

## Problema

L'utente possiede gia' una sottoscrizione GitHub Copilot e vuole usarla per
interpretare il portafoglio senza acquistare una seconda API. GitHub documenta
un SDK Python che puo' autenticarsi con l'utente GitHub, ma l'app viene
distribuita anche come bundle PyInstaller macOS e Windows: non e' ancora
dimostrato che SDK, runtime Copilot, login interattivo e binari necessari
funzionino nel modello `onedir` del progetto.

Integrare direttamente la dipendenza in `app.py` prima di questa verifica
rischierebbe di rendere il bundle piu' grande o non avviabile e di confondere
un limite dell'abbonamento con un bug del comparatore.

## Chi lo incontra

Chi usa l'app locale e vuole sfruttare il proprio account Copilot senza
inserire chiavi di OpenAI o Anthropic, sia da sorgente sia dagli archivi desktop
macOS e Windows.

## Criteri di accettazione

1. Una prova isolata documenta se Python 3.13 puo' avviare il Copilot SDK,
   autenticare un utente GitHub con sottoscrizione attiva e ricevere una
   risposta, senza usare dati reali del portafoglio.
2. La prova stabilisce quali prerequisiti sono necessari: CLI inclusa,
   eseguibile esterno, GitHub CLI, device flow, variabili d'ambiente o token.
   Nessuna credenziale completa viene stampata o salvata nel repository.
3. Viene verificata una risposta strutturata con strumenti disabilitati: il
   modello non puo' leggere file, eseguire comandi, navigare il web o chiamare
   funzioni del comparatore.
4. Viene misurato cosa accade in almeno quattro casi: utente non autenticato,
   sottoscrizione non disponibile, rete assente e limite/rate limit raggiunto.
   Ogni caso deve essere distinguibile da una risposta malformata del modello.
5. Viene verificata la fattibilita' del bundle `onedir` su macOS e Windows, o
   viene identificato con precisione il prerequisito esterno che impedisce un
   bundle autosufficiente.
6. Dipendenze, licenze, dimensione del bundle e modalita' di aggiornamento del
   runtime vengono annotate prima di decidere se aggiungerle a `pyproject.toml`.
7. L'esito produce una decisione esplicita: integrare il Copilot SDK, integrare
   con un prerequisito documentato, oppure fermarsi. Un esito negativo non
   viene mascherato implementando automaticamente un provider diverso.
8. Il repository applicativo resta invariato salvo strumenti/documentazione
   dedicati alla prova; test e bundle correnti continuano a funzionare.

## Non-obiettivi

- Interfaccia finale di analisi AI.
- Invio del portafoglio, anche anonimizzato.
- Scelta del prompt definitivo o valutazione della qualita' finanziaria delle
  risposte.
- Supporto OpenAI, Anthropic o GitHub Models tramite PAT come fallback.
- Automazione di ordini o accesso a file, shell, browser e account del broker.

## Vincoli

- L'autenticazione preferita e' l'utente GitHub gia' connesso e la sua
  sottoscrizione Copilot; non si introduce una nuova chiave API nell'app.
- Il test usa un payload sintetico privo di nomi, ISIN, ticker e importi.
- Qualunque token temporaneo e' trattato come segreto, non compare in output e
  non entra in commit.
- Il progetto resta locale; non si crea un OAuth server o un servizio remoto.
- La dipendenza non entra nel gruppo runtime finche' il punto 7 non ha un esito
  favorevole.

## Domande aperte

Nessuna per la prova. Compatibilita' PyInstaller e disponibilita' effettiva
del runtime Python sono precisamente cio' che questa spec deve risolvere.
