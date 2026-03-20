"""
users.py — Gestione whitelist utenti del bot.
"""
import sqlite3
from pathlib import Path

_DB = Path(__file__).parent / "data" / "users.db"


def _init():
    _DB.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(_DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id  INTEGER PRIMARY KEY,
            username     TEXT,
            full_name    TEXT,
            status       TEXT DEFAULT 'pending',
            requested_at TEXT DEFAULT (datetime('now')),
            approved_at  TEXT
        )
    """)
    con.commit()
    con.close()


def is_approved(telegram_id: int) -> bool:
    _init()
    con = sqlite3.connect(_DB)
    row = con.execute(
        "SELECT status FROM users WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()
    con.close()
    return row is not None and row[0] == "approved"


def get_username(telegram_id: int) -> str:
    _init()
    con = sqlite3.connect(_DB)
    row = con.execute(
        "SELECT username FROM users WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()
    con.close()
    return (row[0] or f"user_{telegram_id}") if row else f"user_{telegram_id}"


def get_status(telegram_id: int) -> str | None:
    """Ritorna lo status dell'utente o None se non esiste."""
    _init()
    con = sqlite3.connect(_DB)
    row = con.execute(
        "SELECT status FROM users WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()
    con.close()
    return row[0] if row else None


def add_pending(telegram_id: int, username: str, full_name: str) -> bool:
    """Aggiunge una richiesta. Ritorna True se nuova, False se già esistente."""
    _init()
    con = sqlite3.connect(_DB)
    existing = con.execute(
        "SELECT status FROM users WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()
    if existing:
        con.close()
        return False
    con.execute(
        "INSERT INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)",
        (telegram_id, username or "", full_name or ""),
    )
    con.commit()
    con.close()
    return True


def approve_user(telegram_id: int) -> None:
    con = sqlite3.connect(_DB)
    con.execute(
        "UPDATE users SET status='approved', approved_at=datetime('now') WHERE telegram_id=?",
        (telegram_id,),
    )
    con.commit()
    con.close()


def reject_user(telegram_id: int) -> None:
    con = sqlite3.connect(_DB)
    con.execute(
        "UPDATE users SET status='rejected' WHERE telegram_id=?", (telegram_id,)
    )
    con.commit()
    con.close()


def list_users() -> list[dict]:
    _init()
    con = sqlite3.connect(_DB)
    rows = con.execute(
        "SELECT telegram_id, username, full_name, status, requested_at "
        "FROM users ORDER BY requested_at DESC"
    ).fetchall()
    con.close()
    return [
        {"id": r[0], "username": r[1], "full_name": r[2],
         "status": r[3], "requested_at": r[4]}
        for r in rows
    ]
