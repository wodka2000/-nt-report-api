"""
Bot Telegram — Report LinkedIn
Raccoglie messaggi inoltrati, analizza PDF con Claude, genera post LinkedIn.
"""

import os
import json
import logging
import base64
import time
from datetime import datetime
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, PicklePersistence, filters, ContextTypes
)

# ── Configurazione ─────────────────────────────────────────────────────────────
TELEGRAM_TOKEN       = os.environ.get("TELEGRAM_TOKEN", "")
ANTHROPIC_API_KEY    = os.environ.get("ANTHROPIC_API_KEY", "")
OWNER_TELEGRAM_ID    = int(os.environ.get("OWNER_TELEGRAM_ID", "0"))
PAGE_SIZE = 7


def is_owner(update_or_id) -> bool:
    """Controlla se l'utente è il proprietario del bot."""
    uid = update_or_id if isinstance(update_or_id, int) else update_or_id.effective_user.id
    return uid == OWNER_TELEGRAM_ID


# ── Internazionalizzazione ──────────────────────────────────────────────────────

_STRINGS: dict[str, dict[str, str]] = {
    "lang_choice": {
        "it": "🌐 In che lingua vuoi ricevere i post e i messaggi del bot?",
        "en": "🌐 Which language would you like to use for posts and bot messages?",
    },
    "lang_set_it": {
        "it": "🇮🇹 Lingua impostata: Italiano.",
        "en": "🇮🇹 Language set to Italian.",
    },
    "lang_set_en": {
        "it": "🇬🇧 Lingua impostata: Inglese.",
        "en": "🇬🇧 Language set to English.",
    },
    "approved": {
        "it": "✅ Il tuo accesso è stato approvato!\n\nUsa /monitor per iniziare a scansionare le fonti normative.",
        "en": "✅ Your access has been approved!\n\nUse /monitor to start scanning regulatory sources.",
    },
    "rejected": {
        "it": "❌ La tua richiesta di accesso non è stata approvata.",
        "en": "❌ Your access request has not been approved.",
    },
    "monitor_menu": {
        "it": "🔍 Quale fonte vuoi scansionare?",
        "en": "🔍 Which source would you like to scan?",
    },
    "scan_start": {
        "it": "🔍 Scansione: <b>{label}</b>…",
        "en": "🔍 Scanning: <b>{label}</b>…",
    },
    "no_new_docs": {
        "it": "ℹ️ *{name}*: nessun documento nuovo oggi.",
        "en": "ℹ️ *{name}*: no new documents today.",
    },
    "sources_unreachable": {
        "it": "⚠️ Fonti non raggiungibili oggi: {sources}",
        "en": "⚠️ Sources unreachable today: {sources}",
    },
    "use_post": {
        "it": "📤 Pubblica",
        "en": "📤 Publish",
    },
    "ignore": {
        "it": "❌ Scarta",
        "en": "❌ Discard",
    },
    "post_full": {
        "it": "📝 *Post completo — copia e incolla su LinkedIn:*",
        "en": "📝 *Full post — copy and paste to LinkedIn:*",
    },
    "source_label": {
        "it": "🔗 Fonte:",
        "en": "🔗 Source:",
    },
    "saved": {
        "it": "💾 Salvato in `reports/{date}.md`",
        "en": "💾 Saved to `reports/{date}.md`",
    },
    "site_updated": {
        "it": "🌐 Sito aggiornato.",
        "en": "🌐 Site updated.",
    },
    "draft_unavailable": {
        "it": "⚠️ Bozza non più disponibile.",
        "en": "⚠️ Draft no longer available.",
    },
    "pausa": {
        "it": "🔕 Notifiche giornaliere disattivate. Usa /riprendi per riattivarle.\nPuoi sempre usare /monitor manualmente.",
        "en": "🔕 Daily notifications disabled. Use /riprendi to re-enable them.\nYou can always use /monitor manually.",
    },
    "riprendi": {
        "it": "🔔 Notifiche giornaliere riattivate.",
        "en": "🔔 Daily notifications re-enabled.",
    },
    "footer": {
        "it": "🤖 Post co-generato con Claude | Approfondisci su nt-report.com",
        "en": "🤖 Post co-created with Claude | Learn more at nt-report.com",
    },
    "translate": {
        "it": "🔄 Traduci",
        "en": "🔄 Translate",
    },
    "html_seeded": {
        "it": "ℹ️ *{name}*: prima scansione completata — monitorerai i nuovi contenuti da ora.",
        "en": "ℹ️ *{name}*: first scan completed — you'll be notified of new content from now on.",
    },
}


def _t(key: str, lang: str) -> str:
    """Restituisce la stringa nella lingua richiesta (fallback: italiano)."""
    return _STRINGS.get(key, {}).get(lang) or _STRINGS.get(key, {}).get("it", key)

TOPICS = {
    "energia":     "⚡ Energia",
    "gioco":       "🎰 Gioco",
    "tecnologia":  "💻 Tecnologia",
    "concessioni": "🏖️ Concessioni",
    "altro":       "📌 Altro",
}

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR      = Path(__file__).parent
PDF_BYTES_DIR = BASE_DIR / "data" / "pdf_bytes"
LOGS_DIR      = BASE_DIR / "logs"


# ── Claude API ─────────────────────────────────────────────────────────────────

def call_claude(**kwargs) -> anthropic.types.Message:
    """Chiama Claude con retry automatico su RateLimitError e OverloadedError (max 3 tentativi)."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    for attempt in range(4):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError:
            if attempt == 3:
                raise
            wait = 60 * (attempt + 1)
            logger.warning(f"Rate limit, attendo {wait}s (tentativo {attempt + 1}/3)")
            time.sleep(wait)
        except anthropic.APIStatusError as e:
            if e.status_code == 529 and attempt < 3:
                wait = 30 * (attempt + 1)
                logger.warning(f"API overloaded (529), attendo {wait}s (tentativo {attempt + 1}/3)")
                time.sleep(wait)
            else:
                raise


# ── Cache bytes PDF su disco ───────────────────────────────────────────────────

def save_pdf_bytes(msg_id: int, data: bytes) -> None:
    PDF_BYTES_DIR.mkdir(parents=True, exist_ok=True)
    (PDF_BYTES_DIR / f"{msg_id}.pdf").write_bytes(data)


def load_pdf_bytes(msg_id: int) -> bytes | None:
    path = PDF_BYTES_DIR / f"{msg_id}.pdf"
    return path.read_bytes() if path.exists() else None


def delete_pdf_bytes(msg_id: int) -> None:
    path = PDF_BYTES_DIR / f"{msg_id}.pdf"
    if path.exists():
        path.unlink()
    for chunk in PDF_BYTES_DIR.glob(f"{msg_id}_c*.pdf"):
        chunk.unlink()


# ── Utility: fetch URL ─────────────────────────────────────────────────────────

async def fetch_url_text(url: str) -> tuple[str, str]:
    """Scarica una pagina web e restituisce (titolo, testo)."""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title else url
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        return title, " ".join(paragraphs)[:3000]
    except Exception as e:
        logger.warning(f"fetch_url_text fallito per {url}: {e}")
        return url, ""


def is_pdf_url(url: str) -> bool:
    u = url.lower()
    return u.endswith(".pdf") or u.endswith("/pdf") or "/pdf" in u


# ── Analisi PDF ────────────────────────────────────────────────────────────────

CHUNK_PAGES    = 10   # pagine per chunk
CHUNK_THRESHOLD = 10  # sopra questa soglia si attiva il chunking

# ── Normalizzazione fonti normative ────────────────────────────────────────────

_NORMA_ALIASES: list[tuple[str, list[str]]] = [
    # GDPR
    ("Reg. UE 2016/679", ["gdpr", "general data protection", "regolamento generale protezione", "2016/679"]),
    # AI Act
    ("Reg. UE 2024/1689", ["ai act", "artificial intelligence act", "regolamento ia", "2024/1689"]),
    # DSA
    ("Reg. UE 2022/2065", ["dsa", "digital services act", "2022/2065"]),
    # DMA
    ("Reg. UE 2022/1925", ["dma", "digital markets act", "2022/1925"]),
    # NIS2
    ("Dir. UE 2022/2555", ["nis2", "nis 2", "2022/2555"]),
    # Data Act
    ("Reg. UE 2023/2854", ["data act", "2023/2854"]),
    # Data Governance Act
    ("Reg. UE 2022/868", ["data governance act", "dga", "2022/868"]),
    # ePrivacy
    ("Dir. 2002/58/CE", ["eprivacy", "e-privacy", "2002/58"]),
    # MiCA
    ("Reg. UE 2023/1114", ["mica", "markets in crypto", "2023/1114"]),
    # DORA
    ("Reg. UE 2022/2554", ["dora", "digital operational resilience", "2022/2554"]),
]

def _normalize_norma(norma: str) -> str:
    """
    Riconduce varianti di nome (acronimo, nome esteso, numero) alla forma canonica.
    Esempio: "GDPR" → "Reg. UE 2016/679"
    Se non trova corrispondenza, restituisce la stringa originale.
    """
    lower = norma.lower().strip()
    for canonical, aliases in _NORMA_ALIASES:
        if lower == canonical.lower():
            return canonical
        for alias in aliases:
            if alias in lower or lower in alias:
                return canonical
    return norma


_ANALYSIS_PROMPT = (
    'Analizza il documento e restituisci SOLO questo JSON, senza altro testo:\n'
    '{\n'
    '  "titolo": "titolo sintetico (max 10 parole)",\n'
    '  "autore": "autore o istituzione esatti come nel documento",\n'
    '  "data": "data pubblicazione se presente, altrimenti null",\n'
    '  "sintesi": "riassunto denso 200 parole: fatti, dati, framework con nomi precisi",\n'
    '  "struttura": [\n'
    '    {"titolo": "titolo preciso sezione o gruppo tematico", "riassunto": "1-2 frasi su cosa contiene"},\n'
    '    ...\n'
    '  ],\n'
    '  "fonti": ["Reg. UE 2024/1689", "ISO 37000", "..."]\n'
    '}\n\n'
    'Regole:\n'
    '- struttura: massimo 10-12 voci. Raggruppa considerando e articoli correlati '
    'in macro-temi (es. "Art. 4-5 + Cons. 3-6: AI literacy e nuovi divieti"). '
    'Non creare mai una voce separata per ogni singolo articolo o considerando. '
    'Per documenti con molti articoli, aggrega per tema (es. PMI, enforcement, sandbox, '
    'divieti, governance, disposizioni transitorie). '
    'Titolo sintetico con riferimenti chiave, riassunto di 1-2 frasi.\n'
    '- fonti: SOLO norme, regolamenti, standard, linee guida citati esplicitamente '
    '(ISO, UNI, Reg. UE, Direttive, Decreti, RFC ecc.). '
    'Se non ci sono, elenca framework metodologici formali. '
    'Non inventare nulla che non sia nel documento.'
)


def _count_pdf_pages(file_bytes: bytes) -> int | None:
    """Restituisce il numero di pagine del PDF. Richiede pypdf; None se non disponibile."""
    try:
        import io
        from pypdf import PdfReader
        return len(PdfReader(io.BytesIO(file_bytes)).pages)
    except Exception:
        return None


def _split_pdf(file_bytes: bytes, pages_per_chunk: int) -> list[tuple[int, int, bytes]]:
    """
    Suddivide il PDF in chunk da N pagine.
    Restituisce lista di (pagina_inizio_1based, pagina_fine_1based, bytes_chunk).
    """
    import io
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(io.BytesIO(file_bytes))
    total  = len(reader.pages)
    chunks = []
    for start in range(0, total, pages_per_chunk):
        end    = min(start + pages_per_chunk, total)
        writer = PdfWriter()
        for i in range(start, end):
            writer.add_page(reader.pages[i])
        buf = io.BytesIO()
        writer.write(buf)
        chunks.append((start + 1, end, buf.getvalue()))
    return chunks


async def _call_analysis(file_bytes: bytes) -> dict:
    """Singola chiamata Claude per analizzare un PDF (o un chunk)."""
    pdf_b64 = base64.standard_b64encode(file_bytes).decode("utf-8")
    msg = call_claude(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        messages=[{"role": "user", "content": [
            {"type": "document",
             "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
            {"type": "text", "text": _ANALYSIS_PROMPT},
        ]}],
    )
    if msg.stop_reason == "max_tokens":
        logger.warning("_call_analysis: risposta troncata (max_tokens raggiunto)")
    raw = msg.content[0].text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except Exception:
        logger.error(f"_call_analysis: JSON non valido, raw[:200]={raw[:200]!r}")
        return {"titolo": "Documento PDF", "autore": "", "data": None,
                "sintesi": raw[:400], "struttura": [], "fonti": []}


async def analyze_pdf(file_bytes: bytes, msg_id: int = None) -> dict:
    """
    Analisi completa con Claude.
    Se pypdf è disponibile e il documento supera CHUNK_THRESHOLD pagine,
    suddivide in chunk da CHUNK_PAGES pagine e analizza ciascuno separatamente.
    Ogni sezione della struttura include '_chunk_file' per indicare da quale
    chunk proviene (usato da extract_section per massima precisione).
    """
    size_kb = len(file_bytes) // 1024
    total_pages = _count_pdf_pages(file_bytes)
    logger.info(f"analyze_pdf: {size_kb} KB"
                + (f", {total_pages} pagine" if total_pages else ", pagine non rilevabili"))

    # ── Analisi singola (documento breve o pypdf non disponibile) ──────────────
    if not total_pages or total_pages <= CHUNK_THRESHOLD:
        data = await _call_analysis(file_bytes)
        # fonti_index: ogni norma (normalizzata) → [None] = PDF intero
        data["fonti_index"] = {_normalize_norma(f): [None] for f in data.get("fonti", [])}
        logger.info(f"analyze_pdf (singola): {len(data.get('struttura', []))} sezioni, "
                    f"{len(data.get('fonti', []))} fonti")
        return data

    # ── Analisi per chunk (documento lungo) ────────────────────────────────────
    logger.info(f"analyze_pdf: documento lungo ({total_pages} p.) → "
                f"split in chunk da {CHUNK_PAGES} pagine")

    try:
        chunks = _split_pdf(file_bytes, CHUNK_PAGES)
    except Exception as e:
        logger.error(f"_split_pdf fallito: {e} — fallback ad analisi singola")
        return await _call_analysis(file_bytes)

    result   = {"titolo": "Documento PDF", "autore": "", "data": None,
                "sintesi": "", "struttura": [], "fonti": [], "fonti_index": {}}
    seen_s   = set()
    seen_f   = set()
    sintesi_parts = []

    for idx, (p_start, p_end, chunk_bytes) in enumerate(chunks):
        logger.info(f"  chunk {idx + 1}/{len(chunks)}: pagine {p_start}-{p_end}")

        # Salva il chunk su disco (per extract_section e fonti_index)
        chunk_file: str | None = None
        if msg_id is not None:
            chunk_path = PDF_BYTES_DIR / f"{msg_id}_c{idx}.pdf"
            chunk_path.write_bytes(chunk_bytes)
            chunk_file = str(chunk_path)

        chunk_data = await _call_analysis(chunk_bytes)

        # Primo chunk → titolo, autore, data
        if idx == 0:
            result["titolo"] = chunk_data.get("titolo", "Documento PDF")
            result["autore"] = chunk_data.get("autore", "")
            result["data"]   = chunk_data.get("data")

        # Sintesi parziale con indicazione pagine
        s = chunk_data.get("sintesi", "")
        if s:
            sintesi_parts.append(f"[p.{p_start}-{p_end}] {s}")

        # Struttura: merge deduplicato, con riferimento al chunk file
        for sec in chunk_data.get("struttura", []):
            key = sec.get("titolo", "") if isinstance(sec, dict) else str(sec)
            if key not in seen_s:
                seen_s.add(key)
                entry = (sec.copy() if isinstance(sec, dict)
                         else {"titolo": sec, "riassunto": ""})
                entry["_chunk_file"] = chunk_file
                result["struttura"].append(entry)

        # Fonti: merge deduplicato + fonti_index {norma_canonica → [chunk_files]}
        for f in chunk_data.get("fonti", []):
            canonical = _normalize_norma(f)
            if f not in seen_f:
                seen_f.add(f)
                result["fonti"].append(f)
            result["fonti_index"].setdefault(canonical, [])
            if chunk_file and chunk_file not in result["fonti_index"][canonical]:
                result["fonti_index"][canonical].append(chunk_file)

    if len(sintesi_parts) > 1:
        result["sintesi"] = await _call_synthesis(sintesi_parts)
        logger.info("analyze_pdf: sintesi gerarchica completata")
    else:
        result["sintesi"] = sintesi_parts[0] if sintesi_parts else ""
    logger.info(f"analyze_pdf (chunked): {len(result['struttura'])} sezioni totali, "
                f"{len(result['fonti'])} fonti, "
                f"{len(result['fonti_index'])} voci fonti_index")
    return result


async def _call_synthesis(sintesi_parts: list[str]) -> str:
    """Ri-sintetizza le sintesi parziali di più chunk in un unico riassunto coerente (~200 parole)."""
    combined = "\n\n".join(sintesi_parts)
    # Se il combined è già breve, non serve una chiamata extra
    if len(combined) <= 800:
        return combined
    msg = call_claude(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": (
            "Di seguito le sintesi di sezioni successive di un unico documento. "
            "Producile in un unico riassunto coerente di circa 200 parole, "
            "con fatti, dati e riferimenti normativi precisi. "
            "Rispondi SOLO con il testo del riassunto, nient'altro:\n\n" + combined
        )}],
    )
    return msg.content[0].text.strip()


async def extract_section(msg_id: int, section_title: str,
                           section_context: str = "",
                           chunk_file: str | None = None) -> str | None:
    """
    Estrae 400-500 parole dense sulla sezione scelta.
    Se chunk_file è indicato (documento chunked), usa quel chunk anziché il PDF intero
    → Claude vede solo le pagine rilevanti, risultato più preciso.
    Restituisce None se i bytes non sono disponibili su disco.
    """
    if chunk_file:
        path = Path(chunk_file)
        file_bytes = path.read_bytes() if path.exists() else None
    else:
        file_bytes = load_pdf_bytes(msg_id)

    if not file_bytes:
        logger.warning(f"extract_section: bytes non trovati "
                       f"(msg_id={msg_id}, chunk_file={chunk_file})")
        return None

    pdf_b64 = base64.standard_b64encode(file_bytes).decode("utf-8")
    context_hint = f" ({section_context})" if section_context else ""
    prompt = (
        f'Estrai il contenuto della sezione "{section_title}"{context_hint} da questo documento.\n\n'
        "Restituisci un testo di 400-500 parole con i fatti, dati, numeri, nomi precisi "
        "e riferimenti normativi che compaiono ESPLICITAMENTE in quella sezione.\n\n"
        "REGOLE ASSOLUTE:\n"
        "- Includi SOLO ciò che è scritto in quella sezione specifica\n"
        "- NON includere fatti di contesto generale che ricorrono come giustificazione "
        "in più sezioni del documento (cifre aggregate di policy, obiettivi di lungo periodo, "
        "motivazioni generali della riforma): se un dato appare anche nell'introduzione "
        "e in altre sezioni come cornice, escludilo\n"
        "- NON aggiungere contesto generale sul documento o sul tema\n"
        "- Se un'informazione non è specifica di questa sezione, non citarla\n"
        "- Nessun commento, nessuna meta-osservazione"
    )
    msg = call_claude(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{"role": "user", "content": [
            {"type": "document",
             "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
            {"type": "text", "text": prompt},
        ]}],
    )
    return msg.content[0].text.strip()


async def extract_by_norma(msg_id: int, norma: str, analysis: dict) -> str | None:
    """
    Estrae da ogni chunk indicizzato per 'norma' tutti i passi in cui essa compare,
    con citazioni testuali e riferimento alla sezione/articolo di provenienza.
    Sintetizza se i passi provengono da più chunk.
    """
    fonti_index = analysis.get("fonti_index", {})
    canonical   = _normalize_norma(norma)
    chunk_files = fonti_index.get(canonical) or fonti_index.get(norma)

    # Fallback: norma non in index → scansiona il PDF intero
    if not chunk_files:
        chunk_files = [None]

    _EXTRACT_PROMPT = (
        f"Estrai TUTTI i passi in cui compare un riferimento a «{norma}».\n"
        "Per ciascun passo:\n"
        "- riporta la citazione testuale tra virgolette\n"
        "- indica l'articolo o la sezione di provenienza\n"
        "Se non c'è nessun riferimento a questa norma, rispondi esattamente: NESSUN RIFERIMENTO."
    )

    passages = []
    for cf in chunk_files:
        if cf:
            path = Path(cf)
            file_bytes = path.read_bytes() if path.exists() else None
        else:
            file_bytes = load_pdf_bytes(msg_id)

        if not file_bytes:
            continue

        pdf_b64 = base64.standard_b64encode(file_bytes).decode("utf-8")
        resp = call_claude(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            messages=[{"role": "user", "content": [
                {"type": "document",
                 "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
                {"type": "text", "text": _EXTRACT_PROMPT},
            ]}],
        )
        text = resp.content[0].text.strip()
        if text.upper() != "NESSUN RIFERIMENTO":
            passages.append(text)

    if not passages:
        return None

    if len(passages) == 1:
        return passages[0]

    # Più chunk: sintetizza mantenendo le citazioni
    combined = "\n\n---\n\n".join(passages)
    resp = call_claude(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        messages=[{"role": "user", "content": (
            f"Di seguito tutti i passi del documento che citano «{norma}», "
            "estratti da sezioni diverse.\n"
            "Organizzali in una sintesi coerente per tema, "
            "mantenendo le citazioni testuali tra virgolette e i riferimenti agli articoli/sezioni:\n\n"
            + combined
        )}],
    )
    return resp.content[0].text.strip()


def format_pdf_structure_msg(analysis: dict) -> str:
    """Messaggio 1: header + sintesi + struttura compatta numerata (solo titoli)."""
    titolo    = analysis.get("titolo", "Documento PDF")
    autore    = analysis.get("autore", "")
    data_p    = analysis.get("data", "")
    sintesi   = analysis.get("sintesi", "")
    struttura = analysis.get("struttura", [])

    header = f"*{titolo}*"
    if autore: header += f" — {autore}"
    if data_p: header += f" ({data_p})"

    sintesi_short = sintesi[:300] + ("…" if len(sintesi) > 300 else "")

    struttura_lines = []
    for i, s in enumerate(struttura, 1):
        label = s.get("titolo", "") if isinstance(s, dict) else str(s)
        struttura_lines.append(f"  {i}. {label[:70]}")
    struttura_txt = "\n".join(struttura_lines) if struttura_lines else "  (non rilevata)"

    hint = "\n\n_Usa 📖 per il dettaglio di una sezione_" if struttura else ""
    text = (
        f"✅ {header}\n\n"
        f"_{sintesi_short}_\n\n"
        f"📋 *Struttura:*\n{struttura_txt}{hint}"
    )
    if len(text) > 4000:
        text = text[:3990] + "…"
    return text


def sec_menu_keyboard(msg_id: int, struttura: list, page: int = 0) -> InlineKeyboardMarkup:
    """Tastiera paginata per scegliere una sezione da approfondire."""
    PAGE = 8
    total = len(struttura)
    start = page * PAGE
    end   = min(start + PAGE, total)
    rows  = []
    for i in range(start, end):
        s     = struttura[i]
        label = s.get("titolo", f"Sezione {i+1}") if isinstance(s, dict) else str(s)
        rows.append([InlineKeyboardButton(
            f"{i+1}. {label[:50]}", callback_data=f"sec_show:{msg_id}:{i}"
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"sec_menu:{msg_id}:{page-1}"))
    if end < total:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"sec_menu:{msg_id}:{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("✖️ Chiudi", callback_data=f"sec_menu:{msg_id}:close")])
    return InlineKeyboardMarkup(rows)


def detail_keyboard(msg_id: int) -> InlineKeyboardMarkup:
    """Bottone sul messaggio struttura per aprire il menu sezioni."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("📖 Approfondisci una sezione", callback_data=f"sec_menu:{msg_id}:0")
    ]])


def azioni_keyboard(msg_id: int) -> InlineKeyboardMarkup:
    """Tastiera con le 4 azioni principali su un PDF, sempre disponibile."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 Approfondisci sezione", callback_data=f"sec_menu:{msg_id}:0"),
            InlineKeyboardButton("💬 Domande",               callback_data=f"chat_start:{msg_id}"),
        ],
        [
            InlineKeyboardButton("📝 Post documento intero", callback_data=f"pdf_post_all:{msg_id}"),
            InlineKeyboardButton("📝 Post su sezione",       callback_data=f"pdf_post_sec:{msg_id}:0"),
        ],
    ])


AZIONI_LEGEND = (
    "📖 *Approfondisci sezione* — estrae il testo completo di una parte del documento\n"
    "💬 *Domande* — fai domande libere al documento (modalità chat)\n"
    "📝 *Post documento intero* — genera un post LinkedIn sull'intero testo\n"
    "📝 *Post su sezione* — post focalizzato su una parte, con scelta dell'angolo normativo"
)


def _setup_gen_for_pdf(msg_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Popola user_data per la generazione di un post su un singolo PDF."""
    analysis = context.bot_data.get(f"pdf:{msg_id}", {})
    item = {
        "msg_id":      msg_id,
        "text":        analysis.get("sintesi", ""),
        "url":         None,
        "title":       analysis.get("titolo", "Documento PDF"),
        "date":        analysis.get("data", "") or "",
        "source_chat": analysis.get("autore", ""),
        "topic":       context.bot_data.get("msg_topics", {}).get(msg_id, "altro"),
    }
    struttura = analysis.get("struttura", [])
    enriched  = []
    for s in struttura:
        entry = s.copy() if isinstance(s, dict) else {"titolo": s, "riassunto": ""}
        entry.setdefault("_msg_id", msg_id)
        enriched.append(entry)
    context.user_data["ck_items"]        = [item]
    context.user_data["ck_selected"]     = {msg_id}
    context.user_data["gen_struttura"]   = enriched
    context.user_data["gen_fonti"]       = analysis.get("fonti", [])
    context.user_data["gen_post_numero"] = context.user_data.get("gen_post_numero", 1)


def format_pdf_fonti_msg(analysis: dict) -> str:
    """Messaggio 2: fonti normative + domanda tema."""
    fonti     = analysis.get("fonti", [])
    n_sezioni = len(analysis.get("struttura", []))
    n_fonti   = len(fonti)

    fonti_lines = [f"  • {f}" for f in fonti]
    fonti_txt = "\n".join(fonti_lines) if fonti_lines else "  (nessuna fonte normativa esplicita)"

    info = f"_{n_sezioni} sezioni · {n_fonti} fonti_\n\n" if (n_sezioni or n_fonti) else ""
    text = f"{info}⚖️ *Fonti normative:*\n{fonti_txt}\n\nDi che tema si tratta?"
    if len(text) > 4000:
        text = text[:3980] + "…\n\nDi che tema si tratta?"
    return text


# ── Generazione post LinkedIn ──────────────────────────────────────────────────

async def generate_linkedin_post(
    items: list[dict],
    focus: str = "tutto il documento",
    angolo: str = "",
    post_numero: int = 1,
    content_override: str = None,
) -> str:
    """
    Genera il post LinkedIn.

    Se content_override è fornito (testo di una sezione specifica estratta dal PDF),
    viene usato direttamente come contenuto al posto di items.
    Altrimenti si usa la sintesi di ciascun item (senza troncature).
    """
    if not items and not content_override:
        return "Nessuna notizia selezionata."

    prompt_file   = BASE_DIR / "PROMPT.md"
    vincoli_file  = BASE_DIR / "VINCOLI.md"
    istruzioni = prompt_file.read_text(encoding="utf-8")  if prompt_file.exists()  else ""
    vincoli    = vincoli_file.read_text(encoding="utf-8") if vincoli_file.exists() else ""

    if content_override:
        content_block = content_override
        if angolo and content_override.startswith(f"Riferimenti a «{angolo}»"):
            intro = (
                f"Hai davanti tutti i passi in cui i documenti selezionati citano «{angolo}». "
                "Genera il post usando ESCLUSIVAMENTE queste citazioni e i fatti in esse contenuti. "
                "Non aggiungere elementi da altre parti dei documenti:\n\n"
            )
            angolo = ""  # già nel contenuto, non serve ripeterlo nel prompt
        else:
            intro = (
                "Hai davanti il contenuto di una sezione specifica di un documento. "
                "Genera il post usando ESCLUSIVAMENTE i fatti presenti in questo testo. "
                "NON aggiungere elementi da altre parti del documento, "
                "anche se li conosci dal contesto:\n\n"
            )
    else:
        intro = (
            "Hai raccolto questi contenuti da includere nel post. "
            "Devi usarli TUTTI, nessuno escluso:\n\n"
        )
        # Raggruppa per tema — NON include URL grezzi
        by_topic: dict[str, list] = {}
        for item in items:
            by_topic.setdefault(item.get("topic", "altro"), []).append(item)

        sections = []
        for topic_key, entries in by_topic.items():
            label = TOPICS.get(topic_key, topic_key.capitalize())
            bullets = []
            for item in entries:
                body = item.get("text") or item.get("title") or ""
                if body:
                    bullets.append(f"- {body}")
            if bullets:
                sections.append(f"**{label}**\n" + "\n".join(bullets))
        content_block = "\n\n".join(sections)

    focus_str = (
        f"Concentra il post su questa parte del documento: {focus}"
        if focus and focus != "tutto il documento"
        else "Tratta il documento nel suo insieme."
    )
    angolo_str = f"Privilegia l'angolo normativo di: {angolo}" if angolo else ""
    post_str = (
        "Questo è il POST 1: includi una riga di contestualizzazione della fonte "
        "(autore, istituzione, anno) subito dopo l'attacco."
        if post_numero == 1
        else f"Questo è il POST {post_numero} di una serie: "
             "NON ripetere autore, istituzione o anno — il lettore li conosce già."
    )

    prompt = (
        "Sei un avvocato specializzato in diritto dell'energia, gioco d'azzardo, "
        "tecnologia e concessioni.\n"
        + intro
        + f"{content_block}\n\n"
        "---\n\n"
        f"Focus editoriale: {focus_str}\n"
        + (f"Angolo normativo: {angolo_str}\n" if angolo_str else "")
        + f"{post_str}\n\n"
        + (vincoli + "\n\n" if vincoli else "")
        + "Segui scrupolosamente le istruzioni che seguono:\n\n"
        + istruzioni.replace("{FIRMA}", "prima_persona")
    )

    msg = call_claude(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── Helpers dati ───────────────────────────────────────────────────────────────

def make_item(msg_id: int, text: str, url: str = None,
              title: str = None, date=None,
              source_chat: str = None, topic: str = "altro") -> dict:
    return {
        "msg_id":      msg_id,
        "text":        text,
        "url":         url,
        "title":       title or text[:60],
        "date":        date.strftime("%d/%m/%Y") if date else "",
        "source_chat": source_chat or "",
        "topic":       topic,
    }


def get_forward_source(msg) -> str:
    forward_origin = getattr(msg, "forward_origin", None)
    if forward_origin:
        if hasattr(forward_origin, "chat"):
            return getattr(forward_origin.chat, "title", "") or ""
        if hasattr(forward_origin, "sender_user"):
            return getattr(forward_origin.sender_user, "full_name", "") or ""
    if getattr(msg, "forward_from_chat", None):
        return msg.forward_from_chat.title or ""
    if getattr(msg, "forward_from", None):
        return msg.forward_from.full_name or ""
    return ""


def is_forward(msg) -> bool:
    return bool(
        getattr(msg, "forward_origin",    None) or
        getattr(msg, "forward_date",      None) or
        getattr(msg, "forward_from",      None) or
        getattr(msg, "forward_from_chat", None)
    )


def collect_items(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> list[dict]:
    """Restituisce tutti gli item inoltrati in questa chat, dal più recente."""
    cache:      dict = context.bot_data.get("msg_cache", {})
    topics_map: dict = context.bot_data.get("msg_topics", {})

    items = []
    for msg_id, msg in sorted(cache.items(), reverse=True):
        if getattr(msg, "chat_id", None) != chat_id:
            continue

        text  = msg.text or msg.caption or ""
        url   = None
        title = None

        entities = msg.entities or msg.caption_entities or []
        for ent in entities:
            if ent.type == "url":
                url = text[ent.offset: ent.offset + ent.length]
                break

        # PDF analizzato → usa i dati estratti
        pdf_data = context.bot_data.get(f"pdf:{msg_id}")
        if pdf_data:
            title = pdf_data.get("titolo", "Documento PDF")
            text  = pdf_data.get("sintesi", "")
        # URL normale → usa il testo fetchato se disponibile
        elif url:
            url_data = context.bot_data.get(f"url_text:{msg_id}")
            if url_data:
                title = url_data.get("titolo", url)
                text  = url_data.get("testo", "")
            else:
                title = url
        elif text:
            title = text[:80]

        if not (title or text):
            continue

        topic = topics_map.get(msg_id, "altro")
        date  = getattr(msg, "forward_date", None) or msg.date
        items.append(make_item(
            msg_id=msg_id, text=text, url=url, title=title,
            date=date, source_chat=get_forward_source(msg), topic=topic,
        ))
    return items


def collect_analysis(items: list[dict], context) -> tuple[list[dict], list[str]]:
    """
    Raccoglie struttura e fonti da tutti i PDF analizzati degli item selezionati.
    Ogni entry di struttura include _msg_id per sapere da quale PDF proviene.
    """
    struttura: list[dict] = []
    fonti: list[str] = []
    seen_s, seen_f = set(), set()
    for item in items:
        analysis = context.bot_data.get(f"pdf:{item['msg_id']}", {})
        for s in analysis.get("struttura", []):
            key = s.get("titolo", "") if isinstance(s, dict) else str(s)
            if key not in seen_s:
                seen_s.add(key)
                entry = (s.copy() if isinstance(s, dict) else {"titolo": s, "riassunto": ""})
                entry["_msg_id"]     = item["msg_id"]
                entry["_chunk_file"] = entry.get("_chunk_file")  # None per doc non-chunked
                struttura.append(entry)
        for f in analysis.get("fonti", []):
            if f not in seen_f:
                seen_f.add(f)
                fonti.append(f)
    return struttura, fonti


def struttura_label(s) -> str:
    """Estrae il titolo testuale da un elemento struttura (dict o stringa)."""
    return s.get("titolo", "") if isinstance(s, dict) else str(s)


def cluster_struttura(struttura_list: list[dict], analyses: dict) -> list[dict]:
    """
    Raggruppa le sezioni di più documenti in macro-temi trasversali.
    analyses: {msg_id: analysis_dict}
    Restituisce lista di cluster: [{label, entries: [struttura_entry, ...]}]
    Chiamata Haiku text-only (~500 token input, ~200 output).
    """
    if not struttura_list:
        return []

    # Costruisce l'elenco con riferimento al documento di provenienza
    lines = []
    for i, s in enumerate(struttura_list):
        titolo    = struttura_label(s)
        riassunto = s.get("riassunto", "") if isinstance(s, dict) else ""
        msg_id    = s.get("_msg_id")
        doc_title = analyses.get(msg_id, {}).get("titolo", "Documento") if msg_id else "Documento"
        lines.append(f"{i}. [{doc_title}] {titolo}: {riassunto}")

    entries_text = "\n".join(lines)
    try:
        resp = call_claude(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": (
                "Di seguito le sezioni di più documenti. "
                "Raggruppa quelle che trattano argomenti simili in macro-temi trasversali. "
                "Massimo 8 cluster. Restituisci SOLO questo JSON, senza altro testo:\n"
                '[{"label": "Nome cluster", "indices": [0, 3, 5]}, ...]\n\n'
                f"Sezioni:\n{entries_text}"
            )}],
        )
        raw = resp.content[0].text.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        cluster_data = json.loads(raw)
    except Exception as e:
        logger.error(f"cluster_struttura fallito: {e} — fallback a lista piatta")
        return [{"label": struttura_label(s), "entries": [s]} for s in struttura_list]

    clusters = []
    for c in cluster_data:
        label   = c.get("label", "Argomento")
        indices = [i for i in c.get("indices", []) if i < len(struttura_list)]
        entries = [struttura_list[i] for i in indices]
        if entries:
            clusters.append({"label": label, "entries": entries})

    # Eventuali sezioni non assegnate a nessun cluster
    assigned = {i for c in cluster_data for i in c.get("indices", [])}
    orphans  = [struttura_list[i] for i in range(len(struttura_list)) if i not in assigned]
    if orphans:
        clusters.append({"label": "Altro", "entries": orphans})

    return clusters


def build_cluster_content(cluster: dict, analyses: dict) -> str:
    """
    Costruisce il blocco di contenuto per la generazione del post da un cluster.
    Aggrega le sintesi parziali (riassunti sezione) di tutte le entries,
    raggruppate per documento di provenienza.
    """
    by_doc: dict[int, list] = {}
    for entry in cluster.get("entries", []):
        mid = entry.get("_msg_id")
        by_doc.setdefault(mid, []).append(entry)

    parts = []
    for mid, entries in by_doc.items():
        analysis  = analyses.get(mid, {})
        doc_title = analysis.get("titolo", "Documento")
        autore    = analysis.get("autore", "")
        data      = analysis.get("data", "")
        header    = doc_title
        if autore: header += f" — {autore}"
        if data:   header += f" ({data})"
        parts.append(f"**{header}**")
        for e in entries:
            titolo    = struttura_label(e)
            riassunto = e.get("riassunto", "") if isinstance(e, dict) else ""
            parts.append(f"- {titolo}: {riassunto}")
        parts.append("")

    return "\n".join(parts)


# ── UI checklist ───────────────────────────────────────────────────────────────

def checklist_keyboard(items: list[dict], selected: set, page: int) -> InlineKeyboardMarkup:
    start = page * PAGE_SIZE
    page_items = items[start: start + PAGE_SIZE]
    total_pages = max(1, (len(items) + PAGE_SIZE - 1) // PAGE_SIZE)

    rows = []
    for item in page_items:
        mid   = item["msg_id"]
        check = "✅" if mid in selected else "☐"
        icon  = TOPICS.get(item.get("topic", "altro"), "📌")[:2]
        label = item["title"][:44]
        date  = item["date"]
        rows.append([InlineKeyboardButton(
            f"{check} {icon} {label} ({date})",
            callback_data=f"ck_toggle:{mid}:{page}"
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ Prec.", callback_data=f"ck_page:{page - 1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Succ. ▶️", callback_data=f"ck_page:{page + 1}"))
    if nav:
        rows.append(nav)

    rows.append([
        InlineKeyboardButton("✅ Tutti",   callback_data="ck_all:1"),
        InlineKeyboardButton("☐ Nessuno", callback_data="ck_all:0"),
    ])
    n = len(selected)
    rows.append([InlineKeyboardButton(
        f"🗞️ Genera report ({n} elementi)" if n else "🗞️ Genera report",
        callback_data="ck_generate"
    )])
    return InlineKeyboardMarkup(rows)


def checklist_text(items: list[dict], selected: set, page: int) -> str:
    total_pages = max(1, (len(items) + PAGE_SIZE - 1) // PAGE_SIZE)
    return (
        f"🗞️ *Genera report LinkedIn*\n"
        f"*{len(selected)}/{len(items)}* elementi selezionati — "
        f"pagina {page + 1}/{total_pages}\n\n"
        "_Tocca per includere/escludere dal post_"
    )


def topic_keyboard(msg_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(lbl, callback_data=f"settema:{msg_id}:{k}")]
        for k, lbl in TOPICS.items()
    ]
    rows.append([InlineKeyboardButton("💬 Domande sul documento", callback_data=f"chat_start:{msg_id}")])
    return InlineKeyboardMarkup(rows)


# ── Handlers ───────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from users import is_approved, add_pending, get_status

    user    = update.effective_user
    user_id = user.id
    username  = user.username or ""
    full_name = user.full_name or ""

    # Il proprietario si registra sempre
    if is_owner(update):
        context.bot_data["owner_chat_id"] = update.effective_chat.id
        await update.message.reply_text(
            "👋 *Benvenuto!*\n\n"
            "Questo è il tuo canale per i report LinkedIn.\n\n"
            "*Come funziona:*\n"
            "1. Scorri le tue chat Telegram\n"
            "2. Inoltra qui messaggi, link o PDF\n"
            "3. Classifica per tema con i bottoni\n"
            "4. Scrivi /report quando sei pronto\n\n"
            "*Comandi:*\n"
            "/report — mostra gli elementi inoltrati e genera il post\n"
            "/monitor — scansiona le fonti normative\n"
            "/chat — apri una sessione di domande su un PDF\n"
            "/fine — chiudi la sessione di chat\n"
            "/pulisci — svuota la memoria\n"
            "/utenti — gestisci gli utenti approvati",
            parse_mode="Markdown",
        )
        return

    status = get_status(user_id)

    if status == "approved":
        await update.message.reply_text(
            "👋 Bentornato!\n\n"
            "Usa /monitor per scansionare le fonti normative.",
        )
        return

    if status == "pending":
        await update.message.reply_text(
            "⏳ La tua richiesta di accesso è in attesa di approvazione."
        )
        return

    if status == "rejected":
        await update.message.reply_text(
            "❌ La tua richiesta di accesso non è stata approvata."
        )
        return

    # Nuovo utente — invia richiesta al proprietario
    is_new = add_pending(user_id, username, full_name)
    if is_new:
        owner_chat_id = context.bot_data.get("owner_chat_id")
        if owner_chat_id:
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Approva", callback_data=f"user_approve:{user_id}"),
                InlineKeyboardButton("❌ Rifiuta", callback_data=f"user_reject:{user_id}"),
            ]])
            await context.bot.send_message(
                chat_id=owner_chat_id,
                text=(
                    f"👤 *Nuova richiesta di accesso*\n"
                    f"Nome: {full_name}\n"
                    f"Username: @{username}\n"
                    f"ID: `{user_id}`"
                ),
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
    await update.message.reply_text(
        "👋 Ciao! Hai richiesto accesso a questo bot.\n"
        "Riceverai una notifica quando la richiesta sarà approvata."
    )


async def handle_user_approve_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Proprietario approva una richiesta di accesso."""
    query = update.callback_query
    await query.answer()
    if not is_owner(update):
        return
    from users import approve_user, get_username
    user_id = int(query.data.split(":")[1])
    approve_user(user_id)
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(f"✅ Utente {user_id} approvato.")
    try:
        lang_keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🇮🇹 Italiano", callback_data=f"lang:{user_id}:it"),
            InlineKeyboardButton("🇬🇧 English",  callback_data=f"lang:{user_id}:en"),
        ]])
        await context.bot.send_message(
            chat_id=user_id,
            text=_t("approved", "it") + "\n\n" + _t("lang_choice", "it"),
            reply_markup=lang_keyboard,
        )
    except Exception:
        pass


async def handle_user_reject_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Proprietario rifiuta una richiesta di accesso."""
    query = update.callback_query
    await query.answer()
    if not is_owner(update):
        return
    from users import reject_user
    user_id = int(query.data.split(":")[1])
    reject_user(user_id)
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(f"❌ Utente {user_id} rifiutato.")
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=_t("rejected", "it"),
        )
    except Exception:
        pass


async def handle_lang_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Utente sceglie la lingua — salva la preferenza."""
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")  # lang:{user_id}:{lang}
    lang = parts[2] if len(parts) >= 3 else "it"
    from users import set_lang, get_lang
    set_lang(update.effective_user.id, lang)
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(_t(f"lang_set_{lang}", lang))


async def cmd_lingua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Permette all'utente di cambiare la lingua."""
    from users import is_approved, get_lang
    user_id = update.effective_user.id
    if not (is_owner(update) or is_approved(user_id)):
        return
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🇮🇹 Italiano", callback_data=f"lang:{user_id}:it"),
        InlineKeyboardButton("🇬🇧 English",  callback_data=f"lang:{user_id}:en"),
    ]])
    await update.message.reply_text(_t("lang_choice", lang), reply_markup=keyboard)


async def cmd_utenti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista utenti (solo proprietario)."""
    if not is_owner(update):
        return
    from users import list_users
    utenti = list_users()
    if not utenti:
        await update.message.reply_text("Nessun utente registrato.")
        return
    righe = []
    for u in utenti:
        emoji = {"approved": "✅", "pending": "⏳", "rejected": "❌"}.get(u["status"], "❓")
        righe.append(f"{emoji} @{u['username']} ({u['full_name']}) — `{u['id']}`")
    await update.message.reply_text("\n".join(righe), parse_mode="Markdown")


async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("Questo comando è riservato all'amministratore.")
        return
    chat_id = update.effective_chat.id
    items = collect_items(context, chat_id)
    if not items:
        await update.message.reply_text(
            "📭 Non ho trovato messaggi inoltrati.\n\n"
            "Inoltra qui link o PDF, poi scrivi /report."
        )
        return
    selected = {item["msg_id"] for item in items}
    context.user_data["ck_items"]    = items
    context.user_data["ck_selected"] = selected
    context.user_data["ck_page"]     = 0
    await update.message.reply_text(
        checklist_text(items, selected, 0),
        reply_markup=checklist_keyboard(items, selected, 0),
        parse_mode="Markdown",
    )


async def cmd_pulisci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("Questo comando è riservato all'amministratore.")
        return
    chat_id    = update.effective_chat.id
    cache:      dict = context.bot_data.get("msg_cache", {})
    topics_map: dict = context.bot_data.get("msg_topics", {})
    to_remove = [mid for mid, m in cache.items() if getattr(m, "chat_id", None) == chat_id]
    for mid in to_remove:
        cache.pop(mid, None)
        topics_map.pop(mid, None)
        context.bot_data.pop(f"pdf:{mid}", None)
        context.bot_data.pop(f"url_text:{mid}", None)
        delete_pdf_bytes(mid)
    await update.message.reply_text(
        f"🗑️ Rimossi {len(to_remove)} messaggi dalla memoria.\n"
        "Puoi ricominciare ad inoltrare nuovi contenuti."
    )


async def clear_memory(chat_id: int, context: ContextTypes.DEFAULT_TYPE, reply_msg=None):
    """Svuota la cache di questa chat e resetta lo stato conversazionale."""
    cache:      dict = context.bot_data.get("msg_cache", {})
    topics_map: dict = context.bot_data.get("msg_topics", {})
    to_remove = [mid for mid, m in cache.items() if getattr(m, "chat_id", None) == chat_id]
    for mid in to_remove:
        cache.pop(mid, None)
        topics_map.pop(mid, None)
        context.bot_data.pop(f"pdf:{mid}", None)
        context.bot_data.pop(f"url_text:{mid}", None)
        delete_pdf_bytes(mid)
    for k in ("ck_items", "ck_selected", "ck_page", "gen_struttura", "gen_fonti",
              "gen_focus", "gen_angolo", "gen_post_numero", "gen_sezioni_restanti",
              "gen_chat_id", "awaiting_focus", "awaiting_angolo"):
        context.user_data.pop(k, None)
    if reply_msg:
        await reply_msg.reply_text(
            f"🗑️ Memoria svuotata ({len(to_remove)} messaggi rimossi).\n"
            "Puoi iniziare ad inoltrare contenuti per il prossimo report."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Smista tutti i messaggi non-command:
    - Se il bot attende focus o angolo in testo libero → gestisce il flusso
    - Se l'utente scrive "report" → avvia /report
    - Altrimenti → gestisce come potenziale messaggio inoltrato
    """
    msg = update.message
    if not msg:
        return

    # Solo il proprietario può inviare messaggi/PDF/link al bot
    if not is_owner(update):
        return

    text = (msg.text or "").strip()

    # Modalità chat: intercetta tutto il testo non-forward
    if context.user_data.get("chat_mode") and text and not is_forward(msg):
        if text.lower() == "fine":
            await _end_chat_session(msg, context)
        else:
            await handle_chat_input(msg, context)
        return

    # Flusso conversazionale: focus in testo libero
    if context.user_data.get("awaiting_focus") and text and not is_forward(msg):
        context.user_data.pop("awaiting_focus")
        context.user_data["gen_focus"] = text
        await ask_angolo_reply(msg, context)
        return

    # Flusso conversazionale: angolo in testo libero
    if context.user_data.get("awaiting_angolo") and text and not is_forward(msg):
        context.user_data.pop("awaiting_angolo")
        context.user_data["gen_angolo"] = text
        await do_generate(msg, context)
        return

    # Shortcut testuale "report"
    if text.lower() in ("report", "/report") and not is_forward(msg):
        await cmd_report(update, context)
        return

    # Tutto il resto: gestisci come messaggio inoltrato
    await handle_forwarded(msg, context)


async def handle_forwarded(msg, context: ContextTypes.DEFAULT_TYPE):
    """Processa un messaggio inoltrato o inviato direttamente: PDF, link a PDF, link normale, testo."""
    forward = is_forward(msg)
    has_pdf = msg.document and (
        msg.document.mime_type == "application/pdf" or
        (msg.document.file_name or "").lower().endswith(".pdf")
    )
    text_raw = msg.text or msg.caption or ""
    has_url  = any(e.type == "url" for e in (msg.entities or msg.caption_entities or []))

    # Messaggio diretto senza PDF e senza URL: ignoralo (è testo conversazionale)
    if not forward and not has_pdf and not has_url:
        return

    logger.info(
        f"{'Forward' if forward else 'Direct'}: id={msg.message_id} "
        f"forward_origin={getattr(msg, 'forward_origin', None)} "
        f"text={repr(text_raw[:60])}"
    )

    # Salva in cache
    cache = context.bot_data.setdefault("msg_cache", {})
    cache[msg.message_id] = msg

    # ── PDF allegato ───────────────────────────────────────────────────────────
    if has_pdf:
        processing = await msg.reply_text(
            f"📄 *{msg.document.file_name}* — analisi in corso…",
            parse_mode="Markdown"
        )
        try:
            tg_file    = await context.bot.get_file(msg.document.file_id)
            file_bytes = bytes(await tg_file.download_as_bytearray())
            save_pdf_bytes(msg.message_id, file_bytes)
            analysis   = await analyze_pdf(file_bytes, msg_id=msg.message_id)
            context.bot_data[f"pdf:{msg.message_id}"] = analysis

            n_sezioni = len(analysis.get("struttura", []))
            n_fonti   = len(analysis.get("fonti", []))
            struct_msg = format_pdf_structure_msg(analysis)
            if n_sezioni == 0:
                struct_msg += "\n\n⚠️ _Struttura non estratta — il documento potrebbe essere troppo lungo o scansionato._"
            size_kb = len(file_bytes) // 1024
            logger.info(f"PDF {msg.document.file_name}: {size_kb} KB, "
                        f"{n_sezioni} sezioni, {n_fonti} fonti")
            await processing.edit_text(
                struct_msg,
                parse_mode="Markdown",
                reply_markup=detail_keyboard(msg.message_id) if n_sezioni > 0 else None,
            )
            await msg.reply_text(
                format_pdf_fonti_msg(analysis),
                parse_mode="Markdown",
                reply_markup=topic_keyboard(msg.message_id),
            )
            if n_sezioni > 0:
                await msg.reply_text(
                    AZIONI_LEGEND,
                    parse_mode="Markdown",
                    reply_markup=azioni_keyboard(msg.message_id),
                )
        except Exception as e:
            logger.error(f"Errore analisi PDF: {e}", exc_info=True)
            await processing.edit_text(
                f"⚠️ Analisi parziale: {str(e)[:100]}\n\nDi che tema si tratta?",
                reply_markup=topic_keyboard(msg.message_id),
            )
        return

    # Estrai URL dal messaggio
    text = msg.text or msg.caption or ""
    url  = None
    for ent in (msg.entities or msg.caption_entities or []):
        if ent.type == "url":
            url = text[ent.offset: ent.offset + ent.length]
            break

    # ── Link a PDF ─────────────────────────────────────────────────────────────
    if url and is_pdf_url(url):
        processing = await msg.reply_text("📄 Link a PDF rilevato — scarico e analizzo…")
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and b"%PDF" in resp.content[:8]:
                save_pdf_bytes(msg.message_id, resp.content)
                analysis = await analyze_pdf(resp.content, msg_id=msg.message_id)
                context.bot_data[f"pdf:{msg.message_id}"] = analysis
                n_sec = len(analysis.get("struttura", []))
                await processing.edit_text(
                    format_pdf_structure_msg(analysis),
                    parse_mode="Markdown",
                    reply_markup=detail_keyboard(msg.message_id) if n_sec > 0 else None,
                )
                await msg.reply_text(
                    format_pdf_fonti_msg(analysis),
                    parse_mode="Markdown",
                    reply_markup=topic_keyboard(msg.message_id),
                )
                if n_sec > 0:
                    await msg.reply_text(
                        AZIONI_LEGEND,
                        parse_mode="Markdown",
                        reply_markup=azioni_keyboard(msg.message_id),
                    )
            else:
                await processing.edit_text(
                    f"⚠️ Il link non restituisce un PDF valido (status {resp.status_code}).\n\n"
                    "Di che tema si tratta?",
                    reply_markup=topic_keyboard(msg.message_id),
                )
        except Exception as e:
            logger.error(f"Errore download PDF da link: {e}", exc_info=True)
            await processing.edit_text(
                f"⚠️ Impossibile scaricare il PDF: {str(e)[:100]}\n\nDi che tema si tratta?",
                reply_markup=topic_keyboard(msg.message_id),
            )
        return

    # ── Link normale ───────────────────────────────────────────────────────────
    if url:
        title, page_text = await fetch_url_text(url)
        if page_text:
            context.bot_data[f"url_text:{msg.message_id}"] = {"titolo": title, "testo": page_text}
        preview = title[:100]
        await msg.reply_text(
            f"📥 `{preview}`\n\nDi che tema si tratta?",
            reply_markup=topic_keyboard(msg.message_id),
            parse_mode="Markdown",
        )
        return

    # ── Testo semplice ─────────────────────────────────────────────────────────
    preview = text[:80]
    if not preview:
        return
    await msg.reply_text(
        f"📥 `{preview}`\n\nDi che tema si tratta?",
        reply_markup=topic_keyboard(msg.message_id),
        parse_mode="Markdown",
    )


async def handle_settema_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, mid_str, topic = query.data.split(":")
    mid = int(mid_str)
    context.bot_data.setdefault("msg_topics", {})[mid] = topic
    label = TOPICS.get(topic, topic)
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(f"✅ Classificato come *{label}*", parse_mode="Markdown")


async def handle_checklist_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query    = update.callback_query
    await query.answer()
    data     = query.data
    items    = context.user_data.get("ck_items", [])
    selected = context.user_data.get("ck_selected", set())
    page     = context.user_data.get("ck_page", 0)

    if data.startswith("ck_toggle:"):
        _, mid_str, pg_str = data.split(":")
        mid  = int(mid_str)
        page = int(pg_str)
        if mid in selected:
            selected.discard(mid)
        else:
            selected.add(mid)

    elif data.startswith("ck_page:"):
        page = int(data.split(":")[1])

    elif data.startswith("ck_all:"):
        selected = {i["msg_id"] for i in items} if data.endswith(":1") else set()

    elif data == "ck_generate":
        if not selected:
            await query.answer("⚠️ Seleziona almeno un elemento!", show_alert=True)
            return
        context.user_data["ck_selected"] = selected
        sel_items = [i for i in items if i["msg_id"] in selected]
        struttura_list, fonti_list = collect_analysis(sel_items, context)
        context.user_data["gen_struttura"]  = struttura_list
        context.user_data["gen_fonti"]      = fonti_list
        context.user_data["awaiting_focus"] = True

        # Più documenti con struttura → clustering trasversale
        pdf_items = [i for i in sel_items if context.bot_data.get(f"pdf:{i['msg_id']}")]
        use_clusters = len(pdf_items) > 1 and struttura_list

        if use_clusters:
            await query.edit_message_text("⏳ Identifico argomenti trasversali…")
            analyses = {i["msg_id"]: context.bot_data.get(f"pdf:{i['msg_id']}", {})
                        for i in pdf_items}
            clusters = cluster_struttura(struttura_list, analyses)
            context.user_data["gen_clusters"] = clusters
            context.user_data["gen_analyses"] = analyses
            rows = [[InlineKeyboardButton(c["label"][:60], callback_data=f"gen_cluster:{i}")]
                    for i, c in enumerate(clusters)]
            rows.append([InlineKeyboardButton("📊 Tutti i documenti", callback_data="gen_focus:tutti")])
            await query.edit_message_text(
                "🔍 *Argomenti trasversali identificati:*\n\n"
                "Scegli il tema su cui vuoi il post, oppure scrivi nel prossimo messaggio.",
                reply_markup=InlineKeyboardMarkup(rows),
                parse_mode="Markdown",
            )
        else:
            rows = [[InlineKeyboardButton(struttura_label(s)[:60], callback_data=f"gen_focus:{i}")]
                    for i, s in enumerate(struttura_list[:8])]
            rows.append([InlineKeyboardButton("📊 Tutto il documento", callback_data="gen_focus:tutti")])
            await query.edit_message_text(
                "🔍 *Su quale parte vuoi concentrare il post?*\n\n"
                "Scegli dalla struttura del documento, oppure scrivi nel prossimo messaggio.",
                reply_markup=InlineKeyboardMarkup(rows),
                parse_mode="Markdown",
            )
        return

    elif data.startswith("gen_cluster:"):
        context.user_data.pop("awaiting_focus", None)
        try:
            idx      = int(data.split(":", 1)[1])
            clusters = context.user_data.get("gen_clusters", [])
            cluster  = clusters[idx]
            analyses = context.user_data.get("gen_analyses", {})
            # Costruisce il contenuto aggregato dal cluster e lo passa come override
            context.user_data["gen_focus"]            = cluster["label"]
            context.user_data["gen_content_override"] = build_cluster_content(cluster, analyses)
        except (ValueError, IndexError):
            context.user_data["gen_focus"] = "tutto il documento"
        await ask_angolo_edit(query, context)
        return

    elif data.startswith("gen_focus:"):
        context.user_data.pop("awaiting_focus", None)
        val = data.split(":", 1)[1]
        struttura_list = context.user_data.get("gen_struttura", [])
        if val == "tutti":
            focus = "tutto il documento"
        else:
            try:
                focus = struttura_label(struttura_list[int(val)])
            except (ValueError, IndexError):
                focus = val
        context.user_data["gen_focus"] = focus
        context.user_data.pop("gen_content_override", None)
        await ask_angolo_edit(query, context)
        return

    elif data.startswith("gen_angolo:"):
        context.user_data.pop("awaiting_angolo", None)
        val = data.split(":", 1)[1]
        fonti_list = context.user_data.get("gen_fonti", [])
        if val == "nessuno":
            angolo = ""
        else:
            try:
                angolo = fonti_list[int(val)]
            except (ValueError, IndexError):
                angolo = val
        context.user_data["gen_angolo"] = angolo
        await do_generate(query, context)
        return

    context.user_data["ck_selected"] = selected
    context.user_data["ck_page"]     = page
    await query.edit_message_text(
        checklist_text(items, selected, page),
        reply_markup=checklist_keyboard(items, selected, page),
        parse_mode="Markdown",
    )


async def handle_continua_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce 'continua con altra sezione' o 'fine, svuota memoria'."""
    query = update.callback_query
    await query.answer()
    val     = query.data.split(":", 1)[1]
    chat_id = context.user_data.get("gen_chat_id", query.message.chat_id)

    if val == "fine":
        await query.edit_message_text("✅ Fatto.")
        await clear_memory(chat_id, context, reply_msg=query.message)
        return

    sezioni = context.user_data.get("gen_sezioni_restanti", [])
    try:
        focus = struttura_label(sezioni[int(val)])
    except (ValueError, IndexError):
        focus = val
    context.user_data["gen_focus"] = focus
    await ask_angolo_edit(query, context)


async def ask_angolo_reply(msg, context: ContextTypes.DEFAULT_TYPE):
    """Chiede l'angolo normativo con una reply al messaggio."""
    fonti_list = context.user_data.get("gen_fonti", [])
    context.user_data["awaiting_angolo"] = True
    rows = [[InlineKeyboardButton(f[:60], callback_data=f"gen_angolo:{i}")]
            for i, f in enumerate(fonti_list[:8])]
    rows.append([InlineKeyboardButton("📊 Nessun angolo specifico", callback_data="gen_angolo:nessuno")])
    await msg.reply_text(
        "⚖️ *C'è un angolo normativo da privilegiare?*\n\n"
        "Scegli tra le fonti trovate, oppure scrivi nel prossimo messaggio.",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown",
    )


async def ask_angolo_edit(query, context: ContextTypes.DEFAULT_TYPE):
    """Chiede l'angolo normativo modificando il messaggio della callback."""
    fonti_list = context.user_data.get("gen_fonti", [])
    context.user_data["awaiting_angolo"] = True
    rows = [[InlineKeyboardButton(f[:60], callback_data=f"gen_angolo:{i}")]
            for i, f in enumerate(fonti_list[:8])]
    rows.append([InlineKeyboardButton("📊 Nessun angolo specifico", callback_data="gen_angolo:nessuno")])
    focus = context.user_data.get("gen_focus", "")
    header = (
        f"⚖️ *Angolo normativo per «{focus[:50]}»?*\n\n"
        "Scegli tra le fonti trovate, oppure scrivi nel prossimo messaggio."
    )
    await query.edit_message_text(
        header, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown"
    )


async def do_generate(msg_or_query, context: ContextTypes.DEFAULT_TYPE):
    """
    Genera il post LinkedIn e lo salva in reports/YYYY-MM-DD.md.

    Se focus è una sezione specifica e il PDF è disponibile su disco,
    estrae prima il testo dettagliato di quella sezione (chunk approach).
    Se focus è 'tutto il documento', usa la sintesi già in cache.
    """
    items    = context.user_data.get("ck_items", [])
    selected = context.user_data.get("ck_selected", set())
    focus    = context.user_data.get("gen_focus", "tutto il documento")
    angolo   = context.user_data.get("gen_angolo", "")
    post_num = context.user_data.get("gen_post_numero", 1)

    sel_items = [i for i in items if i["msg_id"] in selected]
    is_query  = hasattr(msg_or_query, "edit_message_text")
    chat_id   = msg_or_query.message.chat_id if is_query else msg_or_query.chat_id

    if is_query:
        await msg_or_query.edit_message_text("⏳ Sto generando il post LinkedIn…")
    else:
        await msg_or_query.reply_text("⏳ Sto generando il post LinkedIn…")

    # ── Cluster override (multi-documento): usa il contenuto aggregato già costruito ──
    content_override = context.user_data.pop("gen_content_override", None)

    # ── Chunk approach: se focus è una sezione specifica (documento singolo) ────
    if not content_override and focus != "tutto il documento":
        struttura_list = context.user_data.get("gen_struttura", [])
        section = next((s for s in struttura_list if struttura_label(s) == focus), None)
        if section and section.get("_msg_id"):
            try:
                section_text = await extract_section(
                    section["_msg_id"], focus, section.get("riassunto", ""),
                    chunk_file=section.get("_chunk_file"),
                )
                if section_text:
                    content_override = section_text
                    logger.info(f"Chunk estratto per sezione '{focus}': {len(section_text)} caratteri")
                else:
                    logger.info(f"PDF bytes non disponibili per sezione '{focus}', uso sintesi")
            except Exception as e:
                logger.error(f"extract_section fallito: {e}", exc_info=True)
                # Fallback silenzioso: usa la sintesi

    # ── Angolo normativo: estrai i passi dove la norma compare nei documenti ─────
    norma_content = None
    if angolo and not content_override:
        await (msg_or_query.edit_message_text if is_query else msg_or_query.reply_text)(
            f"🔎 Cerco «{angolo}» nei documenti…"
        )
        norma_parts = []
        for item in sel_items:
            item_analysis = context.bot_data.get(f"pdf:{item['msg_id']}", {})
            if not item_analysis.get("fonti_index"):
                continue
            try:
                part = await extract_by_norma(item["msg_id"], angolo, item_analysis)
                if part:
                    doc_title = item_analysis.get("titolo", "Documento")
                    norma_parts.append(f"**{doc_title}**\n\n{part}")
            except Exception as e:
                logger.error(f"extract_by_norma fallito per {item['msg_id']}: {e}", exc_info=True)

        if norma_parts:
            norma_content = f"Riferimenti a «{angolo}» nei documenti selezionati:\n\n" + "\n\n---\n\n".join(norma_parts)
            logger.info(f"extract_by_norma: {len(norma_parts)} doc, {len(norma_content)} caratteri")
        else:
            logger.info(f"extract_by_norma: nessun riferimento trovato per '{angolo}'")

        await (msg_or_query.edit_message_text if is_query else msg_or_query.reply_text)(
            "⏳ Sto generando il post LinkedIn…"
        )

    try:
        post = await generate_linkedin_post(
            sel_items,
            focus=focus,
            angolo=angolo,
            post_numero=post_num,
            content_override=norma_content or content_override,
        )
    except Exception as e:
        logger.error(f"Errore generazione: {e}", exc_info=True)
        err_fn = msg_or_query.edit_message_text if is_query else msg_or_query.reply_text
        await err_fn(f"❌ Errore nella generazione: {str(e)[:200]}")
        return

    context.user_data["gen_post_numero"] = post_num + 1
    reply_target = msg_or_query.message if is_query else msg_or_query

    if is_query:
        await msg_or_query.edit_message_text("✅ Post generato!")

    date_str = datetime.now().strftime("%Y-%m-%d")
    await reply_target.reply_text(
        f"📝 *Post LinkedIn — {datetime.now().strftime('%d/%m/%Y')}*\n\n{post}",
        parse_mode="Markdown",
    )

    # Salva su file
    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / f"{date_str}.md"
    mode = "a" if report_path.exists() else "w"
    topic     = sel_items[0].get("topic", "altro") if sel_items else "altro"
    topic_lbl = TOPICS.get(topic, topic.capitalize())
    with open(report_path, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write(f"# Report LinkedIn — {date_str}\n\n")
        f.write(f"## Post {post_num} — {datetime.now().strftime('%H:%M')}\n\n")
        f.write(f"**Focus:** {focus}  \n")
        f.write(f"**Temi:** {topic_lbl}  \n")
        if angolo:
            f.write(f"**Angolo normativo:** {angolo}  \n")
        f.write(f"\n{post}\n\n---\n\n")
    await reply_target.reply_text(f"💾 Salvato in `reports/{date_str}.md`", parse_mode="Markdown")

    # Git commit + push automatico per aggiornare il sito
    import subprocess, asyncio
    loop = asyncio.get_event_loop()
    def _git_push():
        subprocess.run(["git", "-C", str(BASE_DIR), "stash"], capture_output=True, text=True)
        subprocess.run(["git", "-C", str(BASE_DIR), "pull", "--rebase"], capture_output=True, text=True)
        subprocess.run(["git", "-C", str(BASE_DIR), "stash", "pop"], capture_output=True, text=True)
        r1 = subprocess.run(["git", "-C", str(BASE_DIR), "add", f"reports/{date_str}.md"], capture_output=True, text=True)
        r2 = subprocess.run(["git", "-C", str(BASE_DIR), "commit", "-m", f"report: aggiungi post {date_str}"], capture_output=True, text=True)
        r3 = subprocess.run(["git", "-C", str(BASE_DIR), "push"], capture_output=True, text=True)
        output = "\n".join(filter(None, [r1.stderr, r2.stderr, r3.stdout, r3.stderr]))
        if r3.returncode != 0:
            raise RuntimeError(output or "push fallito senza output")
        return output
    try:
        await loop.run_in_executor(None, _git_push)
        # Chiama il refresh endpoint del sito per importare subito i nuovi post
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post("https://nt-report-api.onrender.com/api/refresh")
        await reply_target.reply_text("🌐 Sito aggiornato.", parse_mode="Markdown")
    except Exception as e:
        await reply_target.reply_text(f"⚠️ Push fallito:\n<code>{str(e)[:800]}</code>", parse_mode="HTML")
        logger.warning(f"git push report fallito: {e}")

    # Chiedi se continuare con un'altra sezione
    struttura_list   = context.user_data.get("gen_struttura", [])
    sezioni_restanti = [s for s in struttura_list if struttura_label(s) != focus]

    if sezioni_restanti:
        rows = [[InlineKeyboardButton(struttura_label(s)[:60], callback_data=f"gen_continua:{i}")]
                for i, s in enumerate(sezioni_restanti[:6])]
        rows.append([InlineKeyboardButton("✅ Fine, svuota memoria", callback_data="gen_continua:fine")])
        context.user_data["gen_sezioni_restanti"] = sezioni_restanti
        context.user_data["gen_chat_id"]          = chat_id
        await reply_target.reply_text(
            "📌 *Vuoi pubblicare un altro post sulla stessa selezione?*\n\n"
            "Scegli un'altra sezione del documento:",
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="Markdown",
        )
    else:
        await clear_memory(chat_id, context, reply_msg=reply_target)


# ── Chat sul documento ─────────────────────────────────────────────────────────

def _build_chat_context(analysis: dict) -> str:
    """
    Costruisce il contesto testuale del documento dall'analisi già estratta.
    Usa sintesi + struttura con riassunti, senza inviare i byte del PDF.
    """
    lines = []
    titolo = analysis.get("titolo", "Documento")
    autore = analysis.get("autore", "")
    data   = analysis.get("data", "")
    header = titolo
    if autore: header += f" — {autore}"
    if data:   header += f" ({data})"
    lines.append(f"# {header}\n")

    sintesi = analysis.get("sintesi", "")
    if sintesi:
        lines.append(f"## Sintesi\n{sintesi}\n")

    struttura = analysis.get("struttura", [])
    if struttura:
        lines.append("## Struttura del documento")
        for i, s in enumerate(struttura, 1):
            titolo_s  = s.get("titolo", f"Sezione {i}") if isinstance(s, dict) else str(s)
            riassunto = s.get("riassunto", "") if isinstance(s, dict) else ""
            lines.append(f"**{i}. {titolo_s}**")
            if riassunto:
                lines.append(riassunto)
        lines.append("")

    fonti = analysis.get("fonti", [])
    if fonti:
        lines.append("## Fonti normative citate")
        lines.append(", ".join(fonti))

    return "\n".join(lines)


def _build_chat_api_messages(msg_id: int, qa_history: list[dict], question: str,
                              analysis: dict | None = None) -> list:
    """
    Costruisce la lista messaggi per l'API Claude usando il contesto testuale
    estratto dall'analisi (sintesi + struttura), senza inviare i byte del PDF.
    qa_history contiene solo stringhe → pickle leggero, nessun byte in memoria.
    """
    ctx = _build_chat_context(analysis or {})
    system_ctx = f"Documento di riferimento:\n\n{ctx}"

    messages = []
    if qa_history:
        messages = list(qa_history)
    messages.append({"role": "user", "content": question})
    return messages, system_ctx


async def cmd_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Avvia la modalità chat su un documento PDF."""
    chat_id = update.effective_chat.id
    cache   = context.bot_data.get("msg_cache", {})

    # Trova i PDF analizzati disponibili per questa chat
    pdf_items = []
    for msg_id, msg in sorted(cache.items(), reverse=True):
        if getattr(msg, "chat_id", None) != chat_id:
            continue
        analysis = context.bot_data.get(f"pdf:{msg_id}")
        if analysis and analysis.get("sintesi"):
            pdf_items.append((msg_id, analysis.get("titolo", "Documento PDF")))

    if not pdf_items:
        await update.message.reply_text(
            "📭 Nessun documento disponibile per la chat.\n\n"
            "Inoltra un PDF, aspetta l'analisi, poi usa /chat."
        )
        return

    if len(pdf_items) == 1:
        msg_id, title = pdf_items[0]
        await _start_chat_session(msg_id, title, update.message, context)
        return

    rows = [[InlineKeyboardButton(title[:60], callback_data=f"chat_sel:{msg_id}")]
            for msg_id, title in pdf_items[:8]]
    await update.message.reply_text(
        "📄 *Su quale documento vuoi fare domande?*",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown",
    )


async def handle_chat_select_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg_id = int(query.data.split(":", 1)[1])
    analysis = context.bot_data.get(f"pdf:{msg_id}", {})
    title    = analysis.get("titolo", "Documento PDF")
    await query.edit_message_text(f"📄 Documento selezionato: *{title}*", parse_mode="Markdown")
    await _start_chat_session(msg_id, title, query.message, context)


async def handle_chat_start_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Avvia la chat su un PDF direttamente dal bottone nel messaggio di analisi."""
    query = update.callback_query
    await query.answer()
    msg_id   = int(query.data.split(":", 1)[1])
    analysis = context.bot_data.get(f"pdf:{msg_id}", {})
    title    = analysis.get("titolo", "Documento PDF")
    if not analysis.get("sintesi"):
        await query.answer("⚠️ Analisi non disponibile per questo documento.", show_alert=True)
        return
    await query.edit_message_reply_markup(reply_markup=None)
    await _start_chat_session(msg_id, title, query.message, context)


async def handle_sec_menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra/naviga la tastiera paginata delle sezioni da approfondire."""
    query = update.callback_query
    await query.answer()
    parts  = query.data.split(":")          # sec_menu:{msg_id}:{page|close}
    msg_id = int(parts[1])
    action = parts[2]

    if action == "close":
        await query.edit_message_reply_markup(reply_markup=detail_keyboard(msg_id))
        return

    page     = int(action)
    analysis = context.bot_data.get(f"pdf:{msg_id}", {})
    struttura = analysis.get("struttura", [])
    if not struttura:
        await query.answer("Struttura non disponibile.", show_alert=True)
        return
    await query.edit_message_reply_markup(
        reply_markup=sec_menu_keyboard(msg_id, struttura, page)
    )


async def handle_sec_show_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Estrae e invia il dettaglio di una sezione specifica."""
    query = update.callback_query
    await query.answer()
    parts    = query.data.split(":")        # sec_show:{msg_id}:{idx}
    msg_id   = int(parts[1])
    idx      = int(parts[2])

    analysis  = context.bot_data.get(f"pdf:{msg_id}", {})
    struttura = analysis.get("struttura", [])
    if idx >= len(struttura):
        await query.answer("Sezione non trovata.", show_alert=True)
        return

    sec = struttura[idx]
    sec_title   = sec.get("titolo", f"Sezione {idx+1}") if isinstance(sec, dict) else str(sec)
    chunk_file  = sec.get("_chunk_file") if isinstance(sec, dict) else None

    processing = await query.message.reply_text(f"⏳ Estraggo: _{sec_title[:60]}_…", parse_mode="Markdown")
    try:
        detail = await extract_section(msg_id, sec_title, chunk_file=chunk_file)
        if detail:
            text = f"*{sec_title}*\n\n{detail}"
        else:
            riassunto = sec.get("riassunto", "") if isinstance(sec, dict) else ""
            text = f"*{sec_title}*\n\n_{riassunto or 'Dettaglio non disponibile.'}_"
    except Exception as e:
        logger.error(f"sec_show_cb: {e}", exc_info=True)
        text = f"⚠️ Errore nell'estrazione: {str(e)[:100]}"

    if len(text) > 4000:
        text = text[:3990] + "…"
    back_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("◀️ Torna alle sezioni", callback_data=f"sec_menu:{msg_id}:0")
    ]])
    await processing.edit_text(text, parse_mode="Markdown", reply_markup=back_btn)


async def handle_pdf_post_all_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Post LinkedIn sull'intero documento."""
    query = update.callback_query
    await query.answer()
    msg_id = int(query.data.split(":")[1])
    _setup_gen_for_pdf(msg_id, context)
    context.user_data["gen_focus"] = "tutto il documento"
    await ask_angolo_edit(query, context)


async def handle_pdf_post_sec_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Selezione sezione per post LinkedIn focalizzato."""
    query = update.callback_query
    await query.answer()
    parts  = query.data.split(":")          # pdf_post_sec:{msg_id}:{page}
    msg_id = int(parts[1])
    page   = int(parts[2]) if len(parts) > 2 else 0

    analysis  = context.bot_data.get(f"pdf:{msg_id}", {})
    struttura = analysis.get("struttura", [])
    if not struttura:
        await query.answer("Struttura non disponibile.", show_alert=True)
        return

    PAGE  = 8
    total = len(struttura)
    start = page * PAGE
    end   = min(start + PAGE, total)
    rows  = []
    for i in range(start, end):
        s     = struttura[i]
        label = s.get("titolo", f"Sezione {i+1}") if isinstance(s, dict) else str(s)
        rows.append([InlineKeyboardButton(
            f"{i+1}. {label[:50]}", callback_data=f"pdf_focus:{msg_id}:{i}"
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"pdf_post_sec:{msg_id}:{page-1}"))
    if end < total:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"pdf_post_sec:{msg_id}:{page+1}"))
    if nav:
        rows.append(nav)
    await query.edit_message_text(
        "📝 *Su quale sezione vuoi il post?*",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown",
    )


async def handle_pdf_focus_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sezione selezionata → chiede l'angolo normativo."""
    query = update.callback_query
    await query.answer()
    parts  = query.data.split(":")          # pdf_focus:{msg_id}:{idx}
    msg_id = int(parts[1])
    idx    = int(parts[2])
    _setup_gen_for_pdf(msg_id, context)
    struttura = context.user_data["gen_struttura"]
    focus = struttura_label(struttura[idx]) if idx < len(struttura) else "tutto il documento"
    context.user_data["gen_focus"] = focus
    await ask_angolo_edit(query, context)


async def _start_chat_session(msg_id: int, title: str,
                               reply_msg, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chat_mode"]       = True
    context.user_data["chat_msg_id"]     = msg_id
    context.user_data["chat_title"]      = title
    context.user_data["chat_qa"]         = []   # {role, content} testo puro
    context.user_data["chat_log"]        = []   # (role, text, hhmm)
    context.user_data["chat_started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    await reply_msg.reply_text(
        f"💬 *Chat attiva — {title}*\n\n"
        "Fai pure le tue domande sul documento.\n"
        "Scrivi /fine o premi il bottone per chiudere la sessione.",
        parse_mode="Markdown",
    )


def _has_chunks(analysis: dict) -> bool:
    """True se il documento è stato analizzato per chunk (chunk files disponibili su disco)."""
    for s in analysis.get("struttura", []):
        cf = s.get("_chunk_file") if isinstance(s, dict) else None
        if cf and Path(cf).exists():
            return True
    return False


def _identify_relevant_chunk_file(question: str, struttura: list) -> str | None:
    """
    Usa Haiku (solo testo) per identificare quale chunk è più rilevante.
    Restituisce il path del chunk file, o None se non determinabile.
    Una singola chiamata leggera: input = titoli+riassunti, output = un numero.
    """
    entries = []
    chunk_map = {}  # idx → chunk_file
    for i, s in enumerate(struttura):
        titolo    = s.get("titolo", f"Sezione {i}") if isinstance(s, dict) else str(s)
        riassunto = s.get("riassunto", "") if isinstance(s, dict) else ""
        cf        = s.get("_chunk_file") if isinstance(s, dict) else None
        entries.append(f"{i}. {titolo}: {riassunto}")
        chunk_map[i] = cf

    if not entries:
        return None

    struttura_text = "\n".join(entries)
    try:
        resp = call_claude(
            model="claude-haiku-4-5-20251001",
            max_tokens=5,
            messages=[{"role": "user", "content": (
                f"Domanda: {question}\n\n"
                f"Sezioni del documento:\n{struttura_text}\n\n"
                "Rispondi SOLO con il numero (cifra) della sezione più rilevante."
            )}],
        )
        idx = int(resp.content[0].text.strip().split()[0])
        cf  = chunk_map.get(idx)
        if cf and Path(cf).exists():
            return cf
    except Exception:
        pass
    return None


async def handle_chat_input(msg, context: ContextTypes.DEFAULT_TYPE, question_override: str = None):
    """Processa una domanda in modalità chat — risposta rapida da sintesi/struttura."""
    question = question_override or (msg.text or "").strip()
    if not question:
        return

    msg_id   = context.user_data["chat_msg_id"]
    qa       = context.user_data.get("chat_qa", [])
    analysis = context.bot_data.get(f"pdf:{msg_id}", {})

    # Salva la domanda per l'eventuale approfondimento con citazioni
    context.user_data["chat_last_question"] = question

    processing = await msg.reply_text("⏳ …")
    try:
        messages, system_ctx = _build_chat_api_messages(msg_id, qa, question, analysis)
        response = call_claude(
            model="claude-haiku-4-5-20251001",
            max_tokens=3000,
            system=(
                "Sei un assistente che risponde a domande su questo documento. "
                "Risposte dirette e precise; cita il testo quando utile. "
                "Non fare speculazioni oltre il contenuto del documento.\n\n"
                + system_ctx
            ),
            messages=messages,
        )
        answer = response.content[0].text
        truncated = response.stop_reason == "max_tokens"
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        await processing.edit_text(f"❌ Errore: {str(e)[:200]}")
        return

    # Aggiorna la cronologia (solo testo, no bytes)
    qa.append({"role": "user",      "content": question})
    qa.append({"role": "assistant", "content": answer})
    context.user_data["chat_qa"] = qa

    # Aggiorna il log
    now = datetime.now().strftime("%H:%M")
    log = context.user_data.setdefault("chat_log", [])
    log.append(("utente",  question, now))
    log.append(("claude",  answer,   now))

    # Bottoni: Continua (se troncato) + Approfondisci (se chunks disponibili) + Fine
    has_detail = _has_chunks(analysis) or bool(load_pdf_bytes(msg_id))
    display    = answer + ("\n\n⚠️ _Risposta troncata._" if truncated else "")
    btns = []
    if truncated:
        btns.append(InlineKeyboardButton("▶️ Continua", callback_data="chat_continua"))
    if has_detail:
        btns.append(InlineKeyboardButton("🔍 Risposta con citazioni", callback_data="chat_approfondisci"))
    btns.append(InlineKeyboardButton("🔚 Fine sessione", callback_data="chat_fine"))
    keyboard = InlineKeyboardMarkup([btns])
    await processing.edit_text(display, reply_markup=keyboard)


async def handle_chat_fine_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await _end_chat_session(query.message, context)


async def handle_chat_continua_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chiede a Claude di continuare la risposta troncata."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await handle_chat_input(query.message, context,
                            question_override="Continua la risposta dal punto in cui ti sei interrotto.")


async def handle_chat_approfondisci_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Risposta di secondo livello con citazioni testuali dirette.
    1. Identifica il chunk rilevante (chiamata Haiku text-only, ~5 token output).
    2. Rianalizza solo quel chunk con il PDF parziale → risposta con citazioni.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    msg_id   = context.user_data.get("chat_msg_id")
    question = context.user_data.get("chat_last_question", "")
    analysis = context.bot_data.get(f"pdf:{msg_id}", {})
    struttura = analysis.get("struttura", [])

    if not question:
        await query.message.reply_text("⚠️ Domanda non trovata in sessione.")
        return

    processing = await query.message.reply_text("🔍 Cerco la sezione rilevante…")

    # Fase 1: identifica chunk (text-only, economico)
    chunk_file = _identify_relevant_chunk_file(question, struttura)

    # Fallback: PDF intero (per documenti non chunked o chunk non trovato)
    if chunk_file:
        file_bytes = Path(chunk_file).read_bytes()
        source_label = "_Sezione estratta dal documento originale_"
    else:
        file_bytes = load_pdf_bytes(msg_id)
        source_label = "_Documento completo_"

    if not file_bytes:
        await processing.edit_text("⚠️ File PDF non disponibile su disco.")
        return

    await processing.edit_text("🔍 Analizzo il testo originale…")

    # Fase 2: risposta precisa con citazioni dal PDF parziale
    pdf_b64   = base64.standard_b64encode(file_bytes).decode("utf-8")
    doc_block = {"type": "document",
                 "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}}
    try:
        response = call_claude(
            model="claude-haiku-4-5-20251001",
            max_tokens=3000,
            system=(
                "Sei un assistente che risponde a domande su documenti legali e normativi. "
                "Risposte precise con citazioni testuali dirette tra virgolette. "
                "Indica sempre articolo o sezione da cui proviene ogni citazione."
            ),
            messages=[{"role": "user", "content": [
                doc_block,
                {"type": "text", "text": question},
            ]}],
        )
        answer    = response.content[0].text
        truncated = response.stop_reason == "max_tokens"
    except Exception as e:
        logger.error(f"chat_approfondisci error: {e}", exc_info=True)
        await processing.edit_text(f"❌ Errore: {str(e)[:200]}")
        return

    # Aggiorna cronologia e log
    qa  = context.user_data.get("chat_qa", [])
    now = datetime.now().strftime("%H:%M")
    qa.append({"role": "assistant", "content": f"[Con citazioni] {answer}"})
    context.user_data["chat_qa"] = qa
    context.user_data.setdefault("chat_log", []).append(("claude (citazioni)", answer, now))

    display = f"{source_label}\n\n{answer}"
    if truncated:
        display += "\n\n⚠️ _Risposta troncata._"
    btns = []
    if truncated:
        btns.append(InlineKeyboardButton("▶️ Continua", callback_data="chat_continua"))
    btns.append(InlineKeyboardButton("🔚 Fine sessione", callback_data="chat_fine"))
    await processing.edit_text(display, reply_markup=InlineKeyboardMarkup([btns]))


async def cmd_fine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("chat_mode"):
        await _end_chat_session(update.message, context)
    else:
        await update.message.reply_text("Nessuna sessione di chat attiva.")


async def _end_chat_session(reply_msg, context: ContextTypes.DEFAULT_TYPE):
    title      = context.user_data.get("chat_title", "Documento")
    started_at = context.user_data.get("chat_started_at", "")
    ended_at   = datetime.now().strftime("%H:%M")
    log        = context.user_data.get("chat_log", [])

    # Salva il log su file
    log_path = None
    if log:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        filename  = datetime.now().strftime("%Y-%m-%d_%H-%M") + "_chat.txt"
        log_path  = LOGS_DIR / filename
        lines = [
            f"# Chat — {title}",
            f"# Sessione: {started_at} — {ended_at}",
            "",
        ]
        for role, text, hhmm in log:
            label = "Utente" if role == "utente" else "Claude"
            lines.append(f"[{hhmm}] {label}:")
            lines.append(text)
            lines.append("")
        log_path.write_text("\n".join(lines), encoding="utf-8")

    # Pulisci lo stato
    for k in ("chat_mode", "chat_msg_id", "chat_title",
              "chat_qa", "chat_log", "chat_started_at"):
        context.user_data.pop(k, None)

    msg = "✅ Sessione chiusa."
    if log_path:
        msg += f"\n💾 Log salvato in `logs/{log_path.name}`"
    await reply_msg.reply_text(msg, parse_mode="Markdown")


# ── Monitor manuale ────────────────────────────────────────────────────────────

async def cmd_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra il menu inline per scegliere quale fonte monitorare."""
    from users import is_approved
    user_id = update.effective_user.id
    if not (is_owner(update) or is_approved(user_id)):
        await update.message.reply_text(
            "Non sei autorizzato. Usa /start per richiedere l'accesso."
        )
        return
    if is_owner(update):
        context.bot_data["owner_chat_id"] = update.effective_chat.id
    chat_id  = update.effective_chat.id
    user     = update.effective_user
    username = user.username or user.first_name or f"user_{user_id}"
    from monitor import show_monitor_menu
    await show_monitor_menu(context, chat_id=chat_id, username=username)


async def cmd_confronta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra il menu di selezione dei post pubblicati per generare un post comparativo."""
    from users import is_approved
    user_id = update.effective_user.id
    if not (is_owner(update) or is_approved(user_id)):
        await update.message.reply_text("Non sei autorizzato. Usa /start per richiedere l'accesso.")
        return
    chat_id = update.effective_chat.id
    from monitor import show_compare_menu
    await show_compare_menu(context, chat_id=chat_id)


async def cmd_pausa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Disattiva le notifiche giornaliere automatiche."""
    from users import is_approved, opt_out, get_lang
    user_id = update.effective_user.id
    if not (is_owner(update) or is_approved(user_id)):
        return
    opt_out(user_id)
    await update.message.reply_text(_t("pausa", get_lang(user_id)))


async def cmd_riprendi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Riattiva le notifiche giornaliere automatiche."""
    from users import is_approved, opt_in, get_lang
    user_id = update.effective_user.id
    if not (is_owner(update) or is_approved(user_id)):
        return
    opt_in(user_id)
    await update.message.reply_text(_t("riprendi", get_lang(user_id)))


async def cmd_aggiorna(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fa git pull e riavvia il servizio systemd."""
    import subprocess, asyncio
    msg = await update.message.reply_text("⏳ Aggiornamento in corso…")

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: subprocess.run(
            ["git", "-C", "/opt/ntreportbot", "pull"],
            capture_output=True, text=True, timeout=30,
        )
    )
    output = (result.stdout + result.stderr).strip() or "(nessun output)"
    await msg.edit_text(f"✅ git pull completato:\n<code>{output[:800]}</code>\n\nRiavvio tra 3 secondi…", parse_mode="HTML")

    await asyncio.sleep(3)
    import os, signal
    os.kill(os.getpid(), signal.SIGTERM)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN non impostato")
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY non impostato")

    data_dir = BASE_DIR / "data"
    data_dir.mkdir(exist_ok=True)
    persistence = PicklePersistence(filepath=data_dir / "persistence.pkl")

    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .persistence(persistence)
        .build()
    )

    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("help",     cmd_start))
    app.add_handler(CommandHandler("report",   cmd_report))
    app.add_handler(CommandHandler("pulisci",  cmd_pulisci))
    app.add_handler(CommandHandler("chat",     cmd_chat))
    app.add_handler(CommandHandler("fine",     cmd_fine))
    app.add_handler(CommandHandler("monitor",  cmd_monitor))
    app.add_handler(CommandHandler("confronta", cmd_confronta))
    app.add_handler(CommandHandler("pausa",    cmd_pausa))
    app.add_handler(CommandHandler("riprendi", cmd_riprendi))
    app.add_handler(CommandHandler("lingua",   cmd_lingua))
    app.add_handler(CallbackQueryHandler(handle_lang_cb, pattern=r"^lang:"))
    app.add_handler(CommandHandler("aggiorna", cmd_aggiorna))
    app.add_handler(CommandHandler("utenti",   cmd_utenti))
    app.add_handler(CallbackQueryHandler(handle_user_approve_cb, pattern=r"^user_approve:"))
    app.add_handler(CallbackQueryHandler(handle_user_reject_cb,  pattern=r"^user_reject:"))

    # Monitor callbacks
    from monitor import (show_monitor_menu, handle_mon_topic_cb, handle_mon_fonte_cb,
                         handle_mon_usa_cb, handle_mon_ignora_cb,
                         handle_mon_traduci_cb, handle_mon_cmp_cb)
    app.add_handler(CallbackQueryHandler(handle_mon_topic_cb,    pattern=r"^mon_topic:"))
    app.add_handler(CallbackQueryHandler(handle_mon_fonte_cb,    pattern=r"^mon_fonte:"))
    app.add_handler(CallbackQueryHandler(handle_mon_usa_cb,      pattern=r"^mon_usa:"))
    app.add_handler(CallbackQueryHandler(handle_mon_ignora_cb,   pattern=r"^mon_ignora:"))
    app.add_handler(CallbackQueryHandler(handle_mon_traduci_cb,  pattern=r"^mon_traduci:"))
    app.add_handler(CallbackQueryHandler(handle_mon_cmp_cb,      pattern=r"^mon_cmp:"))

    # Job giornaliero alle 07:00 UTC = 08:00 ora italiana (CET, UTC+1)
    # NB: in estate (CEST, UTC+2) corrisponderà alle 09:00 — aggiornare a hour=6 da fine marzo
    from datetime import time as dt_time

    async def _daily_monitor_job(context):
        from monitor import show_monitor_menu
        from users import list_users, get_username
        # Owner
        owner_chat_id = context.bot_data.get("owner_chat_id")
        if owner_chat_id:
            await show_monitor_menu(context, chat_id=owner_chat_id, username="owner")
        # Utenti approvati che non hanno disattivato le notifiche
        for u in list_users():
            if u["status"] == "approved" and not u["opted_out"]:
                await show_monitor_menu(context, chat_id=u["id"],
                                        username=u["username"] or f"user_{u['id']}")

    app.job_queue.run_daily(_daily_monitor_job, time=dt_time(hour=7, minute=0))

    app.add_handler(CallbackQueryHandler(handle_chat_select_cb,        pattern=r"^chat_sel:"))
    app.add_handler(CallbackQueryHandler(handle_chat_fine_cb,          pattern=r"^chat_fine$"))
    app.add_handler(CallbackQueryHandler(handle_chat_continua_cb,      pattern=r"^chat_continua$"))
    app.add_handler(CallbackQueryHandler(handle_chat_approfondisci_cb, pattern=r"^chat_approfondisci$"))
    app.add_handler(CallbackQueryHandler(handle_chat_start_cb,         pattern=r"^chat_start:"))
    app.add_handler(CallbackQueryHandler(handle_sec_menu_cb,     pattern=r"^sec_menu:"))
    app.add_handler(CallbackQueryHandler(handle_sec_show_cb,     pattern=r"^sec_show:"))
    app.add_handler(CallbackQueryHandler(handle_pdf_post_all_cb, pattern=r"^pdf_post_all:"))
    app.add_handler(CallbackQueryHandler(handle_pdf_post_sec_cb, pattern=r"^pdf_post_sec:"))
    app.add_handler(CallbackQueryHandler(handle_pdf_focus_cb,    pattern=r"^pdf_focus:"))
    app.add_handler(CallbackQueryHandler(handle_settema_cb,     pattern=r"^settema:"))
    app.add_handler(CallbackQueryHandler(handle_continua_cb,    pattern=r"^gen_continua:"))
    app.add_handler(CallbackQueryHandler(handle_checklist_cb,   pattern=r"^(ck_|gen_)"))

    app.add_handler(MessageHandler(
        (filters.TEXT | filters.Document.ALL | filters.PHOTO) & ~filters.COMMAND,
        handle_message,
    ))

    async def error_handler(update, context):
        logger.error(f"Eccezione non gestita: {context.error}", exc_info=context.error)

    app.add_error_handler(error_handler)

    # Registra i comandi nel menu Telegram (appare con /)
    from telegram import BotCommand
    async def post_init(application):
        await application.bot.set_my_commands([
            BotCommand("start",   "Benvenuto e istruzioni"),
            BotCommand("report",  "Genera post LinkedIn dai documenti"),
            BotCommand("monitor",  "Scansiona fonti normative ora"),
            BotCommand("confronta","Crea un post comparativo da post pubblicati"),
            BotCommand("pausa",    "Disattiva notifiche giornaliere automatiche"),
            BotCommand("riprendi", "Riattiva notifiche giornaliere automatiche"),
            BotCommand("lingua",   "Cambia lingua / Change language"),
            BotCommand("aggiorna", "Aggiorna bot dal server (git pull + restart)"),
            BotCommand("chat",    "Apri sessione domande su un PDF"),
            BotCommand("fine",    "Chiudi sessione chat"),
            BotCommand("pulisci", "Svuota la memoria"),
            BotCommand("help",    "Mostra i comandi disponibili"),
        ])
    app.post_init = post_init

    logger.info("Bot avviato.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
