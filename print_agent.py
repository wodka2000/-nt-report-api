"""
print_agent.py — Agente locale di stampa per la rassegna stampa quotidiana.

Gira SOLO su questo PC Windows (stessa LAN della stampante), NON sul server Oracle Cloud.
Va schedulato con Task Scheduler di Windows, una volta al giorno (consigliato: 08:30).

Cosa fa:
  1. Si autentica su Google Drive con lo stesso Service Account già usato dal bot
     (secrets/google-drive-sa.json).
  2. Scarica il file placeholder "rassegna-oggi.pdf" dalla cartella Drive condivisa,
     riprovando ogni 2 minuti finché non è stato aggiornato OGGI (il job del bot lo
     aggiorna ogni mattina alle 06:00) o finché non scade il tempo massimo di attesa.
  3. Lo stampa inviandolo via socket grezzo (JetDirect) alla Sharp BP-70M65 sulla porta 9100
     — verificato funzionante il 2026-09-14 con un PDF di prova.
  4. Se qualcosa fallisce (nessun aggiornamento entro il timeout, stampante irraggiungibile),
     manda un messaggio Telegram di avviso a Niccolò.

## Setup one-time
  - Config: secrets/print_agent_config.json (gitignorato, stesso pattern di
    secrets/google-drive-sa.json) con questo contenuto:
        {"telegram_token": "<token del bot>", "owner_chat_id": <chat id di Niccolò>}
  - Task Scheduler → crea attività:
      Trigger:  giornaliero, ore 08:30
      Azione:   "py" con argomenti "-3.12 J:\\2026\\NT\\Report\\print_agent.py"
                (directory di lavoro: J:\\2026\\NT\\Report)
"""

import json
import socket
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
_DRIVE_SA_FILE = BASE_DIR / "secrets" / "google-drive-sa.json"
_CONFIG_FILE = BASE_DIR / "secrets" / "print_agent_config.json"
_DRIVE_FOLDER_ID = "1KoZUSKO75QJsWJJqYJ_emT3qjEL07iM5"
_DRIVE_RASSEGNA_NAME = "rassegna-oggi.pdf"
_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]

PRINTER_HOST = "10.0.0.65"
PRINTER_PORT = 9100

POLL_INTERVAL_SECONDS = 120
STOP_POLLING_AFTER = "08:55"


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


def _print_raw(pdf_bytes: bytes) -> None:
    with socket.create_connection((PRINTER_HOST, PRINTER_PORT), timeout=30) as s:
        s.sendall(pdf_bytes)
        s.shutdown(socket.SHUT_WR)


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
        msg = "⚠️ Print agent: la rassegna di oggi non è comparsa su Drive entro le 08:55 — stampa NON avviata."
        print(msg)
        _send_telegram_alert(config, msg)
        sys.exit(1)

    file_id, _ = found
    try:
        pdf_bytes = _download(drive, file_id)
        _print_raw(pdf_bytes)
        print("Rassegna inviata alla stampante con successo.")
    except Exception as e:
        msg = f"⚠️ Print agent: errore durante download/stampa: {e}"
        print(msg)
        _send_telegram_alert(config, msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
