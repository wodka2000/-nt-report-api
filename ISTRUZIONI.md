# Progetto: Report LinkedIn — Studio Legale

## Contesto
Questo progetto gestisce la raccolta settimanale di notizie e la generazione di post LinkedIn
per uno studio legale specializzato in quattro aree tematiche.

## Aree tematiche presidiate
- **Energia** — diritto dell'energia, rinnovabili, mercati energetici, regolazione ARERA
- **Gioco** — gioco d'azzardo, concessioni ADM/AAMS, normativa di settore
- **Tecnologia** — AI Act, protezione dati, cybersecurity, regolazione digitale
- **Concessioni** — concessioni pubbliche, gare, demanio, balneari

## Flusso di lavoro
1. Durante la settimana i contenuti vengono raccolti tramite bot Telegram (`bot.py`)
2. Il bot chiede di classificare ogni elemento per tema
3. Alla fine della settimana si genera il report con `/report` nel canale Telegram
4. Il post generato viene salvato in `reports/YYYY-MM-DD.md`
5. Prima della pubblicazione si modifica a mano se necessario

## Struttura cartella
```
studio_legale_linkedin/
├── ISTRUZIONI.md       ← questo file
├── PROFILO.md          ← profilo LinkedIn e posizionamento (da completare)
├── TONO.md             ← regole di stile e tono per i post
├── bot.py              ← codice del bot Telegram
├── requirements.txt    ← dipendenze Python
└── reports/            ← post generati, uno per data
    └── YYYY-MM-DD.md
```

## Come usare con Claude Code
Apri Claude Code dalla cartella `studio_legale_linkedin/` e puoi chiedere:
- "Genera il report di questa settimana con questi elementi: [lista]"
- "Modifica il tono del report del 2024-03-15"
- "Aggiorna le istruzioni di tono con questa preferenza: [...]"
- "Mostrami i report degli ultimi 30 giorni"
