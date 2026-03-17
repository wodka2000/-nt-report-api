# Brief per Claude Code — Bot Telegram Report LinkedIn

## Contesto
Sei in una cartella di progetto già esistente. Il bot è funzionante ma ha
accumulato troppi bug nel tempo. Il compito è riscriverlo da zero, mantenendo
tutti i file .md così come sono.

## Struttura cartella attuale
```
J:\2026\NT\Report\
├── avvia.bat          ← avvia il bot su Windows (imposta env vars e lancia bot.py)
├── bot.py             ← DA RISCRIVERE da zero
├── requirements.txt   ← dipendenze Python (non modificare)
├── BRIEF.md           ← questo file
├── PROMPT.md          ← istruzioni editoriali per Claude API (NON modificare)
├── TONO.md            ← riferimento stilistico (NON modificare)
├── PROFILO.md         ← analisi profilo LinkedIn autore (NON modificare)
├── ISTRUZIONI.md      ← contesto generale progetto (NON modificare)
└── reports\           ← cartella dove salvare i post generati (YYYY-MM-DD.md)
```

## avvia.bat (non modificare)
```bat
@echo off
set TELEGRAM_TOKEN=...
set ANTHROPIC_API_KEY=...
py -3.12 bot.py
pause
```

## Cosa fa il bot

### Ricezione messaggi
Il bot opera in una chat privata (solo l'utente e il bot).
L'utente inoltra messaggi da altre chat Telegram durante la settimana.
Tipi di messaggi gestiti:
- **PDF allegato**: analisi completa con Claude
- **Link a PDF** (URL che contiene "/pdf" o finisce in ".pdf"): scarica e analizza
- **Link normale**: fetch della pagina, estrai testo
- **Testo semplice**: salva come contenuto

### Al ricevimento di ogni messaggio inoltrato
1. Se PDF o link a PDF → analisi con Claude (vedi sotto) → mostra riepilogo
2. Chiede di classificare per tema con bottoni:
   ⚡ Energia | 🎰 Gioco | 💻 Tecnologia | 📋 Concessioni | 📌 Altro

### Analisi PDF con Claude
Usa claude-sonnet-4-6, max_tokens=2000.
Estrae in JSON:
- titolo (max 10 parole)
- autore (esatto come nel documento)
- data (se presente)
- sintesi (200 parole dense: fatti, dati, framework con nomi precisi)
- struttura: lista di {titolo, riassunto} per ogni sezione principale
- fonti: lista di norme/standard citati esplicitamente (ISO, Reg. UE, ecc.)

Il riepilogo mostrato all'utente include struttura e fonti.
Limite Telegram: troncare il messaggio a 3800 caratteri.

### Comando /report (o testo "report")
1. Mostra checklist con tutti i messaggi salvati (checkbox, paginata)
2. Tutti selezionati di default
3. Bottone "Genera report" → flusso conversazionale:

   **Step 1 — Focus**
   Bottoni dinamici dalle sezioni del documento estratte dall'analisi.
   Opzione "Tutto il documento". Testo libero se l'utente scrive.

   **Step 2 — Angolo normativo**
   Bottoni dinamici dalle fonti normative estratte dall'analisi.
   Opzione "Nessun angolo specifico". Testo libero se l'utente scrive.

4. Genera post con Claude (vedi sotto)
5. Salva in reports/YYYY-MM-DD.md
6. Chiede: vuoi fare un post su un'altra sezione? (bottoni con sezioni restanti)
   Oppure "Fine, svuota memoria"

### Generazione post LinkedIn con Claude
Usa claude-sonnet-4-6, max_tokens=1500.
Il content_block passato a Claude deve contenere la SINTESI del documento,
MAI l'URL grezzo (Claude tenterebbe di navigarlo).
Legge PROMPT.md a runtime come istruzioni editoriali.
Passa al prompt:
- Il contenuto (sintesi, non URL)
- Focus editoriale scelto dall'utente
- Angolo normativo scelto
- Se è post 1 (includi contestualizzazione fonte) o post 2+ (non ripetere fonte)

## Note tecniche critiche

### Telegram API
- Messaggi inoltrati: usare `getattr(msg, 'forward_origin', None)` per rilevare i forward
  (API v20+, non più forward_date/forward_from)
- Limite messaggi: 4096 caratteri per edit_text
- Limite callback_data: 64 byte — tenere i dati brevi

### Windows / Python 3.12
- Nessun problema di event loop con python-telegram-bot 21.x su Python 3.12

### Memoria persistente
- Usare PicklePersistence (filepath = cartella_progetto/data/persistence.pkl)
- La memoria deve sopravvivere ai riavvii del bot
- bot_data: cache messaggi e analisi PDF
- user_data: stato del flusso conversazionale corrente

### Rate limit Claude API
- Limite: 30.000 input token/minuto su Sonnet
- Retry automatico su RateLimitError: aspetta 60s, riprova fino a 3 volte
- PDF lunghi (60+ pagine) consumano molti token — il retry è essenziale

### Error handling
- Aggiungere error handler che logga le eccezioni con exc_info=True
- In caso di errore analisi PDF: mostrare comunque i bottoni del tema
- In caso di errore generazione: mostrare messaggio di errore leggibile

## Dipendenze (requirements.txt già presente, non modificare)
python-telegram-bot==21.6
anthropic>=0.30.0
httpx>=0.27.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
