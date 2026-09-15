---
name: rassegna
description: This skill should be used when Niccolò asks to "fammi il giornale di domani", "genera la rassegna", "fammi vedere la rassegna stampa", "voglio una prova della rassegna", or otherwise wants a preview/test edition of the rassegna.py daily newspaper PDF generated and sent to him. Applies to the NT Report bot project (J:\2026\NT\Report).
version: 1.0.0
---

# Rassegna stampa — generazione locale di prova

Genera un'edizione di prova del PDF "rassegna stampa" (`rassegna.py`) su questa macchina
Windows e la consegna a Niccolò via chat. Questo è il percorso di **test locale**, distinto
dal job di produzione (`run_rassegna_job` in `rassegna.py`, eseguito ogni pomeriggio alle
16:30 Rome sul server Oracle Cloud con WeasyPrint + upload Drive [oggi + archivio
settimanale] + invio Telegram automatico). La stampa fisica avviene alle 17:00 tramite
`print_agent.py` locale (Task Scheduler Windows, task "NTReportPrint") e il driver Windows
della Sharp BP-70M65 (non più raw socket — vedi "Stampa fisica" più sotto).

## Perché un percorso separato

WeasyPrint (usato in produzione per HTML→PDF) richiede librerie di sistema GTK/Pango/Cairo
non disponibili su Windows (`OSError: cannot load library 'libgobject-2.0-0'`). In locale si
usa Microsoft Edge in modalità headless come sostituto, solo per generare un'anteprima
visiva — la logica di generazione contenuti (`genera_rassegna_html()`) è invece identica a
quella di produzione, quindi l'anteprima è fedele nei contenuti.

## Procedura

1. Scrivi (o riusa se già presente) uno script temporaneo nella root del repo,
   `_tmp_test_rassegna.py`:

   ```python
   import re
   import os
   import asyncio

   bat = open("avvia.bat", encoding="utf-8").read()
   for m in re.finditer(r"set (\w+)=(.+)", bat):
       os.environ[m.group(1).strip()] = m.group(2).strip()

   import rassegna

   html = asyncio.run(rassegna.genera_rassegna_html())
   open("preview_rassegna.html", "w", encoding="utf-8").write(html)
   print("OK, html length:", len(html))
   ```

   Questo carica le variabili d'ambiente (API key, credenziali) da `avvia.bat` — lo stesso
   file usato da `avvia.bat` per avviare il bot — senza mai stamparle a schermo.

2. Eseguilo con l'interprete corretto (NON l'alias `python3` di Windows Store, che è uno
   stub sandboxato che non riesce ad accedere ai file del repo):

   ```bash
   cd "J:/2026/NT/Report"
   py -3.12 _tmp_test_rassegna.py
   ```

   Richiede 1-3 minuti (fetch di tutte le fonti + chiamate Claude per scoring/riassunti).
   Errori 403/SSL isolati su singole fonti RSS (es. rinnovabili.it, gioconews.it) sono normali
   e non bloccanti — il resto della pipeline prosegue.

3. Converti l'HTML in PDF con Edge headless:

   ```bash
   "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="J:\2026\NT\Report\rassegna_domani.pdf" "J:\2026\NT\Report\preview_rassegna.html"
   ```

4. Verifica il numero di pagine (atteso: 6-8; se molto diverso, indagare prima di inviare):

   ```bash
   py -3.12 -c "from pypdf import PdfReader; print('pagine:', len(PdfReader('rassegna_domani.pdf').pages))"
   ```

5. (Best effort, non bloccante) prova l'upload su Drive con lo stesso script di caricamento
   env vars, per verificare se Niccolò ha già caricato il placeholder `rassegna-oggi.pdf`:

   ```bash
   py -3.12 -c "
   import re, os
   bat = open('avvia.bat', encoding='utf-8').read()
   for m in re.finditer(r'set (\w+)=(.+)', bat):
       os.environ[m.group(1).strip()] = m.group(2).strip()
   from monitor import _upload_rassegna_to_drive
   print('upload ok:', _upload_rassegna_to_drive('rassegna_domani.pdf'))
   "
   ```

   Se stampa `Rassegna Drive: nessun file 'rassegna-oggi.pdf' nella cartella ...` il
   placeholder non è ancora stato caricato — segnalarlo a Niccolò nel messaggio di consegna
   (senza ripetere il promemoria se lui l'ha già visto più volte in sessioni precedenti;
   una riga basta).

6. Consegna il PDF con `SendUserFile`, con una caption che riassume brevemente cosa contiene
   e segnala eventuali anomalie osservate nei log (fonti fallite, sezioni vuote, ecc.).

7. **Pulisci sempre i file temporanei** al termine, riusciti o no:

   ```bash
   rm -f _tmp_test_rassegna.py preview_rassegna.html rassegna_domani.pdf
   ```

   Questi file non vanno mai commitati (sono già coperti da `.gitignore` per `rassegna/`,
   ma questi specifici stanno nella root — non aggiungerli a git).

## Da non fare

- Non eseguire `genera_rassegna_pdf()` direttamente in locale (usa WeasyPrint, fallisce su
  Windows) — passare sempre da `genera_rassegna_html()` + Edge headless per i test locali.
- Non usare `python3`/`py3` come interprete (stub Windows Store rotto) — sempre `py -3.12` o
  `/c/Python314/python`.
- Non modificare la soglia di pertinenza (`_RASSEGNA_SCORE_MIN` in `rassegna.py`, attualmente
  8/10) senza che Niccolò lo chieda esplicitamente — è stata calibrata a sua richiesta il
  2026-09-14 per essere più esigente della soglia 5/10 usata da `monitor.py` per le bozze
  LinkedIn.
- Non abbassare `max_per_settore`/`max_per_fonte` (6 e 5) senza controllare prima
  un'anteprima — se una pagina resta comunque vuota il problema è a monte (poche notizie
  pertinenti quel giorno), non il cap. Storia: alzati a 8/6 il 2026-09-15 per "riempire le
  pagine", poi ridotti a 6/5 lo stesso giorno perché avevano allungato troppo (10 pagine
  invece di 6-8) — usare l'anteprima per ritarare, non aumentare/diminuire alla cieca.
- La sezione professionale usa `cols-3` (non `cols-2`) apposta per ridurre il rischio di
  pagine quasi vuote quando una sotto-sezione (tipicamente Tecnologia, che ha solo 2 fonti
  dedicate) è corta — mitiga ma non elimina il rischio, controllare visivamente.
- Non riportare mai in produzione la mappatura dei codici icona `icon-awi-white-NN` di
  meteoam.it come sereno/nuvoloso/nebbia/neve: verificato il 2026-09-15 che non esiste una
  legenda pubblica recuperabile (controllati CSS e bundle JS del sito). `_fetch_meteo_playwright`
  deriva la condizione SOLO da segnali verificati (probabilità di pioggia, temperatura) — se
  si trova un modo per verificare la legenda reale, si può estendere a nuvoloso/nebbia/neve,
  ma non prima.

## Sezione Varie — meteo, link reali, cruciverba giuridico (dal 2026-09-15)

- **Meteo**: `_fetch_meteo_playwright()` renderizza meteoam.it con un browser headless
  (Playwright/Chromium, installato sia in locale sia sul server in `venv` come utente
  `ntbot` — vedi sotto) ed estrae dati REALI dal DOM: alba/tramonto/umidità dal pannello
  principale (selettori `.meteogram-info-list-parameter-*`), temperatura/vento/probabilità
  di pioggia orari da `.weather-info-container` (che copre abbondantemente anche il giorno
  dopo — non serve interagire con lo swiper). La direzione del vento è nel nome della classe
  CSS dell'icona (es. `d-e-se` = Est-Sudest), non serve indovinarla. Se il rendering
  fallisce (sito cambia layout, timeout) ripiega su `_claude_web_search_json` (meno
  affidabile, usato solo come fallback). Cerca sempre Roma, più l'eventuale città di viaggio
  individuata nella ToDo list SOLO se lo spostamento è programmato per domani esattamente
  (non per una data futura più lontana — vedi `_rileva_citta_viaggio`).
  - **Setup necessario**: `playwright install chromium` va eseguito come l'utente che
    esegue il bot (`ntbot` sul server, tramite `sudo -u ntbot venv/bin/playwright install
    chromium` — MAI con `sudo` semplice, altrimenti scarica nella cache di root e il
    servizio non lo trova a runtime). La prima volta serve anche `--with-deps` (una tantum,
    con sudo semplice va bene per le librerie di sistema) per le dipendenze apt.
- **Link reali in Varie** (mostra, con i bambini, libro, disco, a tavola): via
  `_claude_web_search_json`, non generati "a memoria" — riduce ma NON azzera il rischio che
  un link non sia perfettamente accurato. Segnalare sempre a Niccolò, quando si consegna
  un'anteprima, di dare un'occhiata ai link prima che vengano stampati automaticamente.
  "A tavola" è sempre l'ultimo blocco della pagina (richiesta esplicita di Niccolò). Mostra/
  bambini/ristorante preferiscono Roma o Lazio salvo eccezioni molto importanti.
- **Viaggio**: se la ToDo list indica uno spostamento per domani, `_fetch_varie_viaggio`
  aggiunge cosa fare/vedere/mangiare nella città di destinazione (stesso principio, link
  reali). Condivide la rilevazione città con `_fetch_meteo` (`_rileva_citta_viaggio`,
  chiamata una sola volta in `genera_rassegna_html`, non duplicarla).
- **Cruciverba**: tema sempre giuridico (`_CRUCIVERBA_TEMI`, rotazione tra sotto-aree del
  diritto), parole 6-10 lettere, definizioni tecniche — deliberatamente difficile. Le
  soluzioni di oggi NON vengono stampate lo stesso giorno: si salvano in una tabella SQLite
  dedicata (`cruciverba_soluzioni`, creata da `rassegna.py` stesso, non in `monitor.py`) e
  compaiono nell'edizione del giorno successivo, come nei cruciverba dei giornali veri. Se si
  rigenera la rassegna dello stesso giorno più volte per test, questo sovrascrive la riga di
  oggi (comportamento voluto, `INSERT OR REPLACE`).
- **Fallback "mai vuoto" nel professionale**: `_select_with_fallback` ripesca item vecchi
  SOLO se hanno un `published` verificato (RSS). Le pagine ADM sono HTML senza data reale:
  prima del 2026-09-15 il fallback le riproponeva come notizie del giorno anche se vecchie
  di mesi/anni (bug reale, segnalato da Niccolò). Non rimuovere questo controllo per "non
  lasciare mai vuota" una sezione — è un compromesso deliberato, meglio vuota che falsa.

## Archivio settimanale su Drive (dal 2026-09-15)

Oltre al file rotante `rassegna-oggi.pdf` (usato dal print agent), ogni generazione carica
anche un secondo file rotante a 7 slot per giorno della settimana:
`rassegna-lunedi.pdf` ... `rassegna-domenica.pdf` (funzione
`_upload_rassegna_settimana_to_drive` in `monitor.py`, stessa cartella Drive). Stesso vincolo
delle altre funzioni Drive: il Service Account non può creare file nuovi
(`storageQuotaExceeded`, riverificato anche con `files().copy()` — fallisce allo stesso
modo), quindi **Niccolò deve caricare a mano, una volta sola, 7 file placeholder con questi
nomi esatti** nella cartella condivisa. Finché non lo fa, l'upload settimanale fallisce in
silenzio (loggato come warning, non blocca il resto del job) — verificare con
`_find_drive_file_id` prima di assumere che sia già a posto.

## Stampa fisica — driver Windows, non raw socket (dal 2026-09-15)

La stampa via socket raw (porta 9100, JetDirect) NON applica fronte-retro/pinzatura ed è
risultata inaffidabile (byte accettati dalla stampante ma stampa non sempre partita — la
Sharp probabilmente non ha "PDF Direct Print" abilitato). Il metodo corretto passa dal
driver Windows già installato ("SHARP BP-70M65 PCL6", porta TCP/IP 10.0.0.65):

- Fronte-retro (bordo lungo) e pinzatura (1 punto, angolo) sono impostati come default del
  driver via PowerShell `Set-PrintConfiguration -PrinterName "SHARP BP-70M65 PCL6"
  -DuplexingMode TwoSidedLongEdge -PrintTicketXml <ticket con Feature
  psk:JobStapleAllDocuments, Option psk:StapleTopLeft>` — verificato che il driver espone
  la pinzatura tramite Print Schema (non tutti i driver lo fanno).
- L'invio effettivo del job NON è ancora risolto in modo affidabile: `Acrobat.exe /t` è
  stato provato ma non ha funzionato in un caso con un'istanza di Acrobat già aperta con un
  altro documento (probabile conflitto DDE) — non riutilizzare questo metodo senza
  verificarlo di nuovo. La stampa manuale (Niccolò apre il PDF e lo stampa lui) funziona
  correttamente con queste impostazioni. Se serve automatizzare di nuovo l'invio (per
  `print_agent.py`), NON passare da Acrobat: valutare alternative che non aprano/riusino
  un'istanza già in esecuzione.
- `print_agent.py` in repo usa ancora il vecchio metodo raw socket — da aggiornare per
  usare il driver quando si troverà un metodo di invio affidabile, altrimenti la stampa
  automatica delle 17:00 rischia di non funzionare (nessuna conferma di stampa fisica
  riuscita in automatico, solo test manuali finora).
