"""
print_agent.py — Agente locale di stampa per la rassegna stampa quotidiana.

Gira SOLO su questo PC Windows (stessa LAN della stampante), NON sul server Oracle Cloud.
Va schedulato con Task Scheduler di Windows, una volta al giorno (consigliato: 17:00,
stampa serale).

Cosa fa:
  1. Si autentica su Google Drive con lo stesso Service Account già usato dal bot
     (secrets/google-drive-sa.json).
  2. Scarica il file placeholder "rassegna-oggi.pdf" dalla cartella Drive condivisa,
     riprovando ogni 2 minuti finché non è stato aggiornato OGGI (il job del bot lo
     aggiorna ogni pomeriggio alle 16:30) o finché non scade il tempo massimo di attesa.
  3. Lo stampa con `os.startfile(path, "print")` — lo stesso verbo di Explorer "tasto
     destro > Stampa" (per Acrobat: `Acrobat.exe /p /h "file"`), che usa il printer
     predefinito con le impostazioni driver già configurate (fronte-retro + pinzatura).
     Verificato funzionante il 2026-09-15: a differenza di `/t` e del verbo "PrintTo"
     (entrambi si bloccano indefinitamente senza mai mettere in coda il job — vedi la
     skill rassegna per i dettagli), il verbo "print" mette in coda il job in ~2 secondi
     e la stampa fisica esce corretta.
  4. Se qualcosa fallisce (nessun aggiornamento entro il timeout, nessun job mai comparso
     in coda di stampa), manda un messaggio Telegram di avviso a Niccolò.

## Setup one-time
  - Config: secrets/print_agent_config.json (gitignorato, stesso pattern di
    secrets/google-drive-sa.json) con questo contenuto:
        {"telegram_token": "<token del bot>", "owner_chat_id": <chat id di Niccolò>}
  - Task Scheduler → crea attività:
      Trigger:  giornaliero, ore 17:00
      Azione:   "py" con argomenti "-3.12 J:\\2026\\NT\\Report\\print_agent.py"
                (directory di lavoro: J:\\2026\\NT\\Report)
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# Task Scheduler esegue questo script con la codepage console di sistema (cp1252 su
# questo PC), che non sa rappresentare le emoji usate nei messaggi di alert — senza
# questo reconfigure, un print(msg) con "⚠️" crasha PRIMA di mandare l'alert Telegram
# (bug reale, visto il 2026-09-16: l'eccezione da segnalare non veniva mai segnalata).
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).parent
_DRIVE_SA_FILE = BASE_DIR / "secrets" / "google-drive-sa.json"
_CONFIG_FILE = BASE_DIR / "secrets" / "print_agent_config.json"
_DRIVE_FOLDER_ID = "1KoZUSKO75QJsWJJqYJ_emT3qjEL07iM5"
_DRIVE_RASSEGNA_NAME = "rassegna-oggi.pdf"
_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]

PRINTER_NAME = "SHARP BP-70M65 PCL6"
_LOCAL_PDF_PATH = BASE_DIR / "rassegna-stampa-oggi.pdf"

POLL_INTERVAL_SECONDS = 120
STOP_POLLING_AFTER = "17:30"
_PRINT_QUEUE_TIMEOUT_SECONDS = 20


def _load_config() -> dict:
    if not _CONFIG_FILE.exists():
        print(f"Config mancante: {_CONFIG_FILE} — vedi istruzioni di setup nel docstring del file.")
        sys.exit(1)
    return json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))


def _get_drive_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_file(str(_DRIVE_SA_FILE), scopes=_DRIVE_SCOPES)
    return build("drive", "v3", credentials=creds)


def _find_today_file(drive) -> tuple[str, str] | None:
    """Ritorna (file_id, modifiedTime) se rassegna-oggi.pdf esiste ed è stato aggiornato oggi."""
    res = drive.files().list(
        q=f"'{_DRIVE_FOLDER_ID}' in parents and name='{_DRIVE_RASSEGNA_NAME}' and trashed=false",
        fields="files(id, modifiedTime)",
    ).execute()
    files = res.get("files", [])
    if not files:
        return None
    file_id = files[0]["id"]
    modified_time = files[0]["modifiedTime"]  # es. "2026-09-15T05:03:12.000Z" (UTC)
    modified_date = modified_time[:10]
    today = datetime.now().strftime("%Y-%m-%d")
    if modified_date != today:
        return None
    return file_id, modified_time


def _download(drive, file_id: str) -> bytes:
    from googleapiclient.http import MediaIoBaseDownload
    import io
    buf = io.BytesIO()
    request = drive.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()


def _ensure_default_printer() -> bool:
    """Il verbo shell 'print' usato sotto stampa sempre sulla stampante PREDEFINITA di
    Windows, non su PRINTER_NAME esplicitamente — se qualcos'altro (Windows Update,
    un'altra app, un cambio manuale) sposta il default su "Microsoft Print to PDF" o
    "OneNote", la stampa fisica non parte più: appare una finestra di salvataggio (o
    non succede nulla) e nessun errore Python viene sollevato (bug reale, trovato il
    2026-09-23 — la stampa manuale delle 16:xx è finita silenziosamente su "Microsoft
    Print to PDF"). Impostare sempre esplicitamente PRINTER_NAME come default prima di
    stampare, invece di fidarsi dello stato del sistema. Ritorna False se PRINTER_NAME
    non esiste tra le stampanti installate (setup rotto, da segnalare)."""
    ps_script = f"""
$p = Get-CimInstance Win32_Printer -Filter "Name='{PRINTER_NAME}'" -ErrorAction SilentlyContinue
if (-not $p) {{ Write-Output "PRINTER_NOT_FOUND"; exit }}
if (-not $p.Default) {{ Invoke-CimMethod -InputObject $p -MethodName SetDefaultPrinter | Out-Null }}
Write-Output "OK"
"""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True, text=True, timeout=20,
    )
    return result.stdout.strip() == "OK"


def _print_via_shell(pdf_bytes: bytes) -> bool:
    """Salva il PDF in locale e lo stampa con il verbo shell 'print' (equivalente a
    tasto destro > Stampa in Explorer). Ritorna True se un job è comparso in coda entro
    il timeout (segno che la stampa è partita), False altrimenti."""
    _LOCAL_PDF_PATH.write_bytes(pdf_bytes)
    if not _ensure_default_printer():
        return False
    os.startfile(str(_LOCAL_PDF_PATH), "print")

    # IMPORTANTE (bug trovato il 2026-09-15): un job compare in coda già mentre è ancora
    # "Spooling" — se si chiude Acrobat in quel momento (com'era prima), l'invio dei dati
    # viene troncato e il job resta bloccato per sempre in Spooling senza mai stampare
    # fisicamente, pur essendo "visto in coda". Bisogna aspettare che il job ESCA dallo
    # stato Spooling (o dalla coda) prima di chiudere Acrobat.
    ps_script = f"""
$deadline = (Get-Date).AddSeconds({_PRINT_QUEUE_TIMEOUT_SECONDS})
$seen = $false
while ((Get-Date) -lt $deadline) {{
    $jobs = Get-PrintJob -PrinterName '{PRINTER_NAME}' -ErrorAction SilentlyContinue
    if ($jobs) {{
        $seen = $true
        if (($jobs | Where-Object {{ $_.JobStatus -match 'Spooling' }}).Count -eq 0) {{
            Write-Output "JOB_DONE_SPOOLING"; exit
        }}
    }} elseif ($seen) {{
        Write-Output "JOB_LEFT_QUEUE"; exit
    }}
    Start-Sleep -Milliseconds 300
}}
if ($seen) {{ Write-Output "JOB_SEEN_BUT_STILL_SPOOLING" }} else {{ Write-Output "NO_JOB" }}
"""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True, text=True, timeout=_PRINT_QUEUE_TIMEOUT_SECONDS + 15,
    )
    esito = result.stdout.strip()
    job_seen = esito in ("JOB_DONE_SPOOLING", "JOB_LEFT_QUEUE")

    # L'app di visualizzazione resta aperta con /h ma non si chiude da sola: la chiudiamo
    # solo ORA che il job ha finito di essere spoolato (mai mentre è ancora Spooling).
    subprocess.run(["taskkill", "/IM", "Acrobat.exe", "/F"], capture_output=True)
    return job_seen


def _send_telegram_alert(config: dict, text: str) -> None:
    token = config.get("telegram_token")
    chat_id = config.get("owner_chat_id")
    if not token or not chat_id:
        print(f"[niente config Telegram, alert solo su console] {text}")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"Anche l'alert Telegram è fallito: {e}")


def main() -> None:
    config = _load_config()
    drive = _get_drive_service()

    stop_at = datetime.strptime(STOP_POLLING_AFTER, "%H:%M").replace(
        year=datetime.now().year, month=datetime.now().month, day=datetime.now().day
    )

    found = None
    while datetime.now() < stop_at:
        found = _find_today_file(drive)
        if found:
            break
        print(f"Rassegna di oggi non ancora pronta su Drive, riprovo tra {POLL_INTERVAL_SECONDS}s...")
        time.sleep(POLL_INTERVAL_SECONDS)

    if not found:
        msg = f"⚠️ Print agent: la rassegna di oggi non è comparsa su Drive entro le {STOP_POLLING_AFTER} — stampa NON avviata."
        print(msg)
        _send_telegram_alert(config, msg)
        sys.exit(1)

    file_id, _ = found
    try:
        pdf_bytes = _download(drive, file_id)
        ok = _print_via_shell(pdf_bytes)
        if ok:
            print("Rassegna inviata alla stampante con successo (job visto in coda).")
        else:
            msg = "⚠️ Print agent: nessun job comparso in coda di stampa entro il timeout — stampa probabilmente NON partita."
            print(msg)
            _send_telegram_alert(config, msg)
            sys.exit(1)
    except Exception as e:
        msg = f"⚠️ Print agent: errore durante download/stampa: {e}"
        print(msg)
        _send_telegram_alert(config, msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
