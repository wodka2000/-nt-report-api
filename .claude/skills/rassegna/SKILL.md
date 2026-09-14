---
name: rassegna
description: This skill should be used when Niccolò asks to "fammi il giornale di domani", "genera la rassegna", "fammi vedere la rassegna stampa", "voglio una prova della rassegna", or otherwise wants a preview/test edition of the rassegna.py daily newspaper PDF generated and sent to him. Applies to the NT Report bot project (J:\2026\NT\Report).
version: 1.0.0
---

# Rassegna stampa — generazione locale di prova

Genera un'edizione di prova del PDF "rassegna stampa" (`rassegna.py`) su questa macchina
Windows e la consegna a Niccolò via chat. Questo è il percorso di **test locale**, distinto
dal job di produzione (`run_rassegna_job` in `rassegna.py`, eseguito ogni mattina alle 6:00
sul server Oracle Cloud con WeasyPrint + upload Drive + invio Telegram automatico).

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
