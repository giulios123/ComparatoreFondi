# 007 · Attività

Riferimento: [`spec.md`](spec.md) · [`plan.md`](plan.md)

## Implementazione

- [ ] Fissare in un ambiente isolato versioni SDK/runtime e prerequisiti.
- [ ] Scrivere la sonda con payload sintetico, schema e tool disabilitati.
- [ ] Redigere ogni log eliminando prompt, output e credenziali sensibili.
- [ ] Provare autenticazione valida, assente, rete assente e limite raggiunto.
- [ ] Costruire il probe PyInstaller minimo per macOS e Windows.
- [ ] Misurare binari esterni, dimensione e comportamento di aggiornamento.
- [ ] Eseguire l'audit licenze prima di mantenere dipendenze nel progetto.
- [ ] Documentare l'esito e prendere la decisione go/no-go.

## Test

- [ ] Verificare che nessun tool sia registrato o invocabile.
- [ ] Verificare che l'output della sonda non contenga prefissi di token.
- [ ] Verificare parsing della risposta strutturata e risposta malformata.
- [ ] Verificare avvio del bundle probe sulle due piattaforme.

## Verifica dei criteri di accettazione

- [ ] 1 · richiesta Python 3.13 autenticata completata.
- [ ] 2 · prerequisiti e credenziali documentati in sicurezza.
- [ ] 3 · risposta strutturata senza strumenti.
- [ ] 4 · quattro classi di errore distinguibili.
- [ ] 5 · esito bundle macOS e Windows.
- [ ] 6 · dipendenze, licenze, dimensione e aggiornamenti annotati.
- [ ] 7 · decisione finale esplicita.
- [ ] 8 · applicazione corrente invariata e verde.

## Chiusura

- [ ] Suite unittest, ruff e `git diff --check` passano
- [ ] `docs/spikes/copilot-sdk-desktop.md` contiene evidenze riproducibili
- [ ] Aggiornato `docs/memory-bank/02-decisioni.md`
- [ ] Aggiornato lo stato in cima a `spec.md`
