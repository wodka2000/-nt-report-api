"""
engine.py — Import shim da bot.py.

Importa le funzioni pure (nessuna dipendenza Telegram) direttamente dal bot,
così qualsiasi aggiornamento al bot si riflette automaticamente qui.
Se bot.py non è disponibile (es. deploy su Render), usa i fallback da constants.py.
"""
import sys
from pathlib import Path

# Aggiunge la root del progetto al path
_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

# Costanti sempre disponibili (non dipendono da Telegram)
from web.core.constants import (  # noqa: E402
    TOPICS, _NORMA_ALIASES, _normalize_norma, BASE_DIR, PDF_BYTES_DIR,
)

# Funzioni AI — disponibili solo quando bot.py è installato (ambiente locale)
try:
    from bot import (  # noqa: E402
        analyze_pdf,
        generate_linkedin_post,
        extract_section,
        extract_by_norma,
        _build_chat_context,
        _build_chat_api_messages,
        call_claude,
        save_pdf_bytes,
        load_pdf_bytes,
        make_item,
    )
except ImportError:
    analyze_pdf = generate_linkedin_post = extract_section = None
    extract_by_norma = _build_chat_context = _build_chat_api_messages = None
    call_claude = save_pdf_bytes = load_pdf_bytes = make_item = None

__all__ = [
    "analyze_pdf",
    "generate_linkedin_post",
    "extract_section",
    "extract_by_norma",
    "_build_chat_context",
    "_build_chat_api_messages",
    "call_claude",
    "_normalize_norma",
    "_NORMA_ALIASES",
    "TOPICS",
    "PDF_BYTES_DIR",
    "BASE_DIR",
    "save_pdf_bytes",
    "load_pdf_bytes",
    "make_item",
]

