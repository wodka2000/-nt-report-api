"""
claude_mobile.py — Bot Telegram per controllare Claude Code da mobile.

Ogni messaggio viene passato a `claude --print` con gli ultimi 3 scambi
come contesto (domanda + risposta troncata a 1000 caratteri).

Avvio:
    CLAUDE_BOT_TOKEN=<token> python claude_mobile.py

Primo utilizzo: manda /start al bot per registrare il tuo chat ID.
Comandi: /nuova — azzera la cronologia e inizia da zero.
"""

import asyncio
import logging
import os
import subprocess
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    PicklePersistence, filters, ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

CLAUDE_BOT_TOKEN = os.environ.get("CLAUDE_BOT_TOKEN", "")
PROJECT_DIR      = Path(__file__).parent

MAX_TURNS        = 3     # scambi da passare come contesto
MAX_REPLY_CHARS  = 1000  # caratteri di risposta da conservare in storico


def _build_prompt(history: list[dict], nuovo_messaggio: str) -> str:
    """Costruisce il prompt con lo storico + il nuovo messaggio."""
    parti = [
        "Sei Claude Code, stai lavorando al progetto NT Report.\n"
        "Puoi leggere e modificare i file nella directory corrente.\n"
        "Stai rispondendo a un messaggio arrivato via Telegram mobile.\n"
    ]
    if history:
        parti.append("--- Contesto conversazione precedente ---")
        for turn in history:
            parti.append(f"Utente: {turn['user']}")
            parti.append(f"Claude: {turn['claude']}")
        parti.append("--- Fine contesto ---\n")
    parti.append(f"Utente: {nuovo_messaggio}")
    return "\n".join(parti)


# ── Comandi ────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.bot_data["owner_chat_id"] = chat_id
    context.bot_data.setdefault("history", [])
    await update.message.reply_text(
        f"✅ Chat ID registrato: <code>{chat_id}</code>\n\n"
        "Scrivimi qualsiasi messaggio e lo passerò a Claude Code.\n"
        "Claude può leggere e modificare i file del progetto.\n\n"
        "/nuova — inizia una nuova conversazione",
        parse_mode="HTML",
    )


async def cmd_nuova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.bot_data["history"] = []
    await update.message.reply_text("🔄 Conversazione azzerata.")


# ── Messaggio in arrivo ────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id  = update.effective_chat.id
    owner_id = context.bot_data.get("owner_chat_id")

    if owner_id and chat_id != owner_id:
        return

    testo = update.message.text or update.message.caption or ""
    if not testo:
        return

    thinking = await update.message.reply_text("⏳ Claude sta elaborando…")

    history: list[dict] = context.bot_data.setdefault("history", [])
    prompt  = _build_prompt(history[-MAX_TURNS:], testo)

    try:
        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                ["claude", "--print", "-p", prompt],
                cwd=str(PROJECT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=300,
            ),
        )
        risposta = result.stdout.strip()
        if result.returncode != 0 and not risposta:
            risposta = f"⚠️ Errore:\n{result.stderr.strip()[:1000]}"

    except subprocess.TimeoutExpired:
        risposta = "⚠️ Timeout: Claude ha impiegato troppo. Riprova con una richiesta più semplice."
    except FileNotFoundError:
        risposta = "⚠️ Comando `claude` non trovato. Assicurati che Claude Code sia installato e nel PATH."

    # Salva turno nello storico (risposta troncata)
    history.append({
        "user":   testo,
        "claude": risposta[:MAX_REPLY_CHARS] + ("…" if len(risposta) > MAX_REPLY_CHARS else ""),
    })
    context.bot_data["history"] = history

    await thinking.delete()

    # Invia risposta (max 4000 caratteri per messaggio Telegram)
    for i in range(0, len(risposta), 4000):
        await update.message.reply_text(risposta[i:i + 4000])


# ── Main ───────────────────────────────────────────────────────────────────────

async def main():
    if not CLAUDE_BOT_TOKEN:
        raise ValueError("CLAUDE_BOT_TOKEN non impostato")

    data_dir = PROJECT_DIR / "data"
    data_dir.mkdir(exist_ok=True)
    persistence = PicklePersistence(filepath=data_dir / "claude_mobile_persistence.pkl")

    app = (
        Application.builder()
        .token(CLAUDE_BOT_TOKEN)
        .persistence(persistence)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("nuova", cmd_nuova))
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
        handle_message,
    ))

    logger.info("claude_mobile: avvio polling")
    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
        await app.updater.stop()
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
