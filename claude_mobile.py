"""
claude_mobile.py — Bot Telegram per controllare Claude Code da mobile.

Ogni messaggio ricevuto viene passato a Claude Code via `claude --print --continue`.
Claude può leggere e modificare i file del progetto, eseguire comandi, committare.

Avvio:
    CLAUDE_BOT_TOKEN=<token> python claude_mobile.py

Primo utilizzo: manda /start al bot per registrare il tuo chat ID.
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
PROJECT_DIR = Path(__file__).parent


# ── Comandi ────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.bot_data["owner_chat_id"] = chat_id
    await update.message.reply_text(
        f"✅ Chat ID registrato: <code>{chat_id}</code>\n\n"
        "Scrivimi qualsiasi messaggio e lo passerò a Claude Code.\n"
        "Claude può leggere e modificare i file del progetto.",
        parse_mode="HTML",
    )


async def cmd_nuova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inizia una nuova conversazione (non usa --continue)."""
    context.bot_data["prima_sessione"] = True
    await update.message.reply_text("🔄 Prossimo messaggio inizierà una nuova conversazione.")


# ── Messaggio in arrivo ────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    owner_id = context.bot_data.get("owner_chat_id")

    if owner_id and chat_id != owner_id:
        return  # ignora chiunque non sia il proprietario

    testo = update.message.text or update.message.caption or ""
    if not testo:
        return

    thinking = await update.message.reply_text("⏳ Claude sta elaborando…")

    prima_sessione = context.bot_data.pop("prima_sessione", False)

    try:
        cmd = ["claude", "--print", "-p", testo]
        if not prima_sessione:
            cmd.insert(1, "--continue")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                cmd,
                cwd=str(PROJECT_DIR),
                capture_output=True,
                text=True,
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

    await thinking.delete()

    # Telegram: max 4096 caratteri per messaggio
    chunk_size = 4000
    parti = [risposta[i:i + chunk_size] for i in range(0, len(risposta), chunk_size)]
    for parte in parti:
        await update.message.reply_text(parte)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
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
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
