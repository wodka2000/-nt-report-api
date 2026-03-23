"""
monitor.py — Agente di monitoraggio normativo.

Ogni giorno alle 08:00 UTC:
  1. Scarica RSS/pagine web dalle fonti configurate
  2. Valuta rilevanza con Claude Haiku (0-10)
  3. Se score >= 5: scarica contenuto completo, genera bozza post con Sonnet
  4. Notifica via Telegram con bottoni [Usa questo post] [Ignora]

Integrato nel bot via JobQueue — non va eseguito direttamente.
"""

import json
import re
import asyncio
import logging
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

import httpx
import feedparser
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

# ── Configurazione fonti ────────────────────────────────────────────────────────

_SOURCES_FILE = Path(__file__).parent / "sources.md"


def _load_sources() -> list[dict]:
    """Legge le fonti attive da sources.md (righe senza 'aggiungere dopo')."""
    sources = []
    text = _SOURCES_FILE.read_text(encoding="utf-8")
    for line in text.splitlines():
        # Riga di tabella con almeno 4 colonne: | Nome | URL | Tipo | Settori | Note |
        if not line.startswith("|") or line.startswith("| Nome") or set(line.strip("|").replace("-", "").replace("|", "").replace(" ", "")) == set():
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 4:
            continue
        name, url, tipo, _, note = (cols + [""] * 5)[:5]
        if not url.startswith("http"):
            continue
        if "aggiungere dopo" in note:
            continue
        source: dict = {"name": name, "url": url, "type": tipo}
        m = re.search(r"link_filter:(\S+)", note)
        if m:
            source["link_filter"] = [m.group(1)]
        g = re.search(r"group:(\S+)", note)
        if g:
            source["group"] = g.group(1)
        if "fetch_summary" in note:
            source["fetch_summary"] = True
        t = re.search(r"timeout:(\d+)", note)
        if t:
            source["timeout"] = int(t.group(1))
        sources.append(source)
    return sources


SOURCES = _load_sources()

_SETTORI_DESC = """
- energia: regolazione energetica, elettricità, gas, rinnovabili, ARERA, mercati energetici, tariffe
- gioco: gioco pubblico, concessioni giochi, ADM, slot machine, scommesse, lotterie, gioco online
- tecnologia: AI Act, GDPR, DSA, DMA, NIS2, Data Act, cybersecurity, intelligenza artificiale, dati personali, piattaforme digitali
- concessioni: concessioni pubbliche, demanio, appalti, gare pubbliche, autorizzazioni, licenze
""".strip()

_RELEVANCE_PROMPT = """\
Sei un assistente legale specializzato in diritto dell'energia, gioco pubblico, \
tecnologia (AI Act, GDPR, DSA) e concessioni pubbliche italiane ed europee.

Valuta la rilevanza del seguente documento per uno studio legale italiano attivo in questi settori:
{settori}

Documento:
Titolo: {titolo}
Sommario: {sommario}
{esempi}
Rispondi SOLO con un oggetto JSON valido, senza testo aggiuntivo:
{{"score": <intero 0-10>, "settore": "<energia|gioco|tecnologia|concessioni|altro>", "motivo": "<max 20 parole in italiano>"}}
"""

_POST_PROMPT = """\
Generate a professional LinkedIn post in {lingua} about the following regulatory document.

Source: {fonte}
Title: {titolo}
Document date: {data}

Document content:
{contenuto}

Rules:
- Start with the document date (e.g. "On 18 March 2025, ARERA...")
- Professional tone, never sensationalist
- Only facts and regulatory references from the document
- No speculation or subjective opinion
- Maximum 1300 characters (text + hashtags)
- IMPORTANT: always end with a complete sentence, never mid-sentence
- End with 3-5 relevant hashtags
"""


# ── Database locale per tracciare i documenti già visti ────────────────────────

def _db_path() -> Path:
    from bot import BASE_DIR
    return BASE_DIR / "data" / "monitor.db"


def _init_db() -> None:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS drafts (
            draft_id  TEXT PRIMARY KEY,
            data      TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS seen_docs (
            url      TEXT,
            chat_id  TEXT NOT NULL DEFAULT 'owner',
            title    TEXT,
            source   TEXT,
            score    REAL,
            rating   INTEGER DEFAULT NULL,
            seen_at  TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (url, chat_id)
        )
    """)
    # Migrazioni per DB esistenti
    try:
        con.execute("ALTER TABLE seen_docs ADD COLUMN rating INTEGER DEFAULT NULL")
    except sqlite3.OperationalError:
        pass
    try:
        con.execute("ALTER TABLE seen_docs ADD COLUMN chat_id TEXT NOT NULL DEFAULT 'owner'")
        # Rimuove il vecchio vincolo PRIMARY KEY su url e ricrea la tabella con la chiave composita
        con.executescript("""
            CREATE TABLE IF NOT EXISTS seen_docs_new (
                url      TEXT,
                chat_id  TEXT NOT NULL DEFAULT 'owner',
                title    TEXT,
                source   TEXT,
                score    REAL,
                rating   INTEGER DEFAULT NULL,
                seen_at  TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (url, chat_id)
            );
            INSERT OR IGNORE INTO seen_docs_new SELECT url, 'owner', title, source, score, rating, seen_at FROM seen_docs;
            DROP TABLE seen_docs;
            ALTER TABLE seen_docs_new RENAME TO seen_docs;
        """)
    except sqlite3.OperationalError:
        pass
    con.commit()
    con.close()


def _db_connect():
    con = sqlite3.connect(_db_path(), timeout=15)
    con.execute("PRAGMA journal_mode=WAL")
    return con


def _save_draft(draft_id: str, draft: dict) -> None:
    con = _db_connect()
    con.execute(
        "INSERT OR REPLACE INTO drafts (draft_id, data) VALUES (?, ?)",
        (draft_id, json.dumps(draft, ensure_ascii=False)),
    )
    con.commit()
    con.close()


def _load_draft(draft_id: str) -> dict | None:
    try:
        _init_db()
        con = _db_connect()
        row = con.execute("SELECT data FROM drafts WHERE draft_id=?", (draft_id,)).fetchone()
        con.close()
        if row:
            return json.loads(row[0])
    except Exception:
        pass
    return None


def _save_rating(url: str, rating: int, chat_id: str = "owner") -> None:
    con = _db_connect()
    con.execute("UPDATE seen_docs SET rating=? WHERE url=? AND chat_id=?", (rating, url, chat_id))
    con.commit()
    con.close()


def _get_rated_examples(chat_id: str = "owner", limit: int = 5) -> tuple[list[str], list[str]]:
    """Restituisce titoli di documenti con rating alto (4-5) e basso (1-2) per questo utente."""
    con = _db_connect()
    high = [r[0] for r in con.execute(
        "SELECT title FROM seen_docs WHERE chat_id=? AND rating >= 4 ORDER BY seen_at DESC LIMIT ?",
        (chat_id, limit)
    ).fetchall()]
    low = [r[0] for r in con.execute(
        "SELECT title FROM seen_docs WHERE chat_id=? AND rating <= 2 AND rating IS NOT NULL ORDER BY seen_at DESC LIMIT ?",
        (chat_id, limit)
    ).fetchall()]
    con.close()
    return high, low


def _has_seen_source(chat_id: str, source: str) -> bool:
    """Controlla se l'utente ha già visto almeno un item da questa fonte."""
    con = _db_connect()
    row = con.execute(
        "SELECT 1 FROM seen_docs WHERE chat_id=? AND source=? LIMIT 1", (chat_id, source)
    ).fetchone()
    con.close()
    return row is not None


def _seed_seen_from_owner(chat_id: str, approved_at: str) -> int:
    """Copia nella seen_docs dell'utente gli item già visti dall'owner prima di approved_at."""
    from bot import OWNER_TELEGRAM_ID
    owner_id = str(OWNER_TELEGRAM_ID)
    con = _db_connect()
    rows = con.execute(
        "SELECT url, title, source, score, seen_at FROM seen_docs "
        "WHERE chat_id=? AND seen_at < ?", (owner_id, approved_at)
    ).fetchall()
    count = 0
    for url, title, source, score, seen_at in rows:
        con.execute(
            "INSERT OR IGNORE INTO seen_docs (url, chat_id, title, source, score, seen_at) "
            "VALUES (?,?,?,?,?,?)", (url, chat_id, title, source, score, seen_at)
        )
        count += 1
    con.commit()
    con.close()
    return count


def _is_seen(url: str, chat_id: str = "owner") -> bool:
    con = _db_connect()
    row = con.execute("SELECT 1 FROM seen_docs WHERE url=? AND chat_id=?", (url, chat_id)).fetchone()
    con.close()
    return row is not None


def _mark_seen(url: str, title: str, source: str, score: float, chat_id: str = "owner") -> None:
    con = _db_connect()
    con.execute(
        "INSERT OR IGNORE INTO seen_docs (url, chat_id, title, source, score) VALUES (?,?,?,?,?)",
        (url, chat_id, title, source, score),
    )
    con.commit()
    con.close()


# ── Fetch fonti ─────────────────────────────────────────────────────────────────

_RSS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


def _parse_rss_entries(feed) -> list[dict]:
    items = []
    for entry in feed.entries[:30]:
        if not entry.get("link"):
            continue
        content = ""
        if hasattr(entry, "content") and entry.content:
            raw = entry.content[0].get("value", "")
            content = BeautifulSoup(raw, "html.parser").get_text(separator="\n", strip=True)
        summary = entry.get("summary", "") or content[:600]
        items.append({
            "url":       entry.get("link", ""),
            "title":     entry.get("title", ""),
            "summary":   summary,
            "content":   content,
            "published": entry.get("published_parsed"),
        })
    return items


async def _fetch_rss(url: str, timeout: int = 20) -> list[dict] | None:
    """Scarica un feed RSS. Restituisce None se la fonte non è raggiungibile."""
    # Tentativo 1: httpx
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(url, headers=_RSS_HEADERS)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        if feed.entries:
            return _parse_rss_entries(feed)
        # feed vuoto con httpx → prova feedparser diretto
    except Exception as e:
        logger.warning(f"RSS httpx fallito per {url}: {e} — provo feedparser diretto")

    # Tentativo 2: feedparser diretto (urllib, diverso stack HTTP)
    try:
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(
            None,
            lambda: feedparser.parse(url, request_headers=_RSS_HEADERS),
        )
        if feed.get("bozo") and not feed.entries:
            logger.error(f"Errore fetch RSS {url}: {feed.get('bozo_exception')}")
            return None
        return _parse_rss_entries(feed)
    except Exception as e:
        logger.error(f"Errore fetch RSS {url}: {e}")
        return None


async def _fetch_html_links(url: str, link_filter: list[str] | None = None, timeout: int = 15) -> list[dict] | None:
    """Scrapa una pagina HTML cercando link a comunicati/provvedimenti."""
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        base = urlparse(url)
        seen_urls: set[str] = set()
        items = []
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if not text or len(text) < 15:
                continue
            if href.startswith("/"):
                href = f"{base.scheme}://{base.netloc}{href}"
            elif not href.startswith("http"):
                continue
            # Applica filtro per keyword nel link o nel testo
            if link_filter:
                href_lower = href.lower()
                text_lower = text.lower()
                if not any(kw in href_lower or kw in text_lower for kw in link_filter):
                    continue
            if href in seen_urls:
                continue
            seen_urls.add(href)
            items.append({"url": href, "title": text, "summary": ""})
            if len(items) >= 40:
                break
        return items
    except Exception as e:
        logger.error(f"Errore fetch HTML {url}: {e}")
        return None


async def _fetch_content(url: str) -> tuple[str, str]:
    """Scarica il testo principale e la data di pubblicazione di una pagina.
    Restituisce (contenuto, data_trovata)."""
    import re
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        testo = soup.get_text(separator="\n", strip=True)
        # Cerca data nel testo (formati comuni italiani)
        data = ""
        match = re.search(
            r'\b(\d{1,2}[\s/\-]\w+[\s/\-]\d{4}|\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})\b',
            testo[:2000]
        )
        if match:
            data = match.group()
        return testo[:8000], data
    except Exception as e:
        logger.error(f"Errore fetch contenuto {url}: {e}")
        return "", ""


# ── Valutazione e generazione ───────────────────────────────────────────────────

def _assess_relevance(titolo: str, sommario: str, chat_id: str = "owner") -> dict:
    """Usa Haiku per valutare la rilevanza (score 0-10)."""
    import re
    from bot import call_claude
    high, low = _get_rated_examples(chat_id)
    esempi = ""
    if high or low:
        esempi = "\nPreferenze dell'utente (basate sui rating):"
        if high:
            esempi += f"\n- Molto rilevanti (4-5 ⭐): {'; '.join(high[:3])}"
        if low:
            esempi += f"\n- Poco rilevanti (1-2 ⭐): {'; '.join(low[:3])}"
    prompt = _RELEVANCE_PROMPT.format(
        settori=_SETTORI_DESC,
        titolo=titolo,
        sommario=(sommario or "(nessun sommario)")[:600],
        esempi=esempi,
    )
    try:
        msg = call_claude(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()
        # Estrai il blocco JSON anche se ci sono testi attorno
        match = re.search(r'\{[^{}]+\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except Exception as e:
        logger.warning(f"Errore valutazione rilevanza: {e}")
        return {"score": 0, "settore": "altro", "motivo": "errore parsing"}


def _generate_post(fonte: str, titolo: str, contenuto: str, data: str = "", lang: str = "it") -> str:
    """Usa Sonnet per generare la bozza del post LinkedIn."""
    from bot import call_claude
    lingua = "Italian" if lang == "it" else "English"
    prompt = _POST_PROMPT.format(
        fonte=fonte,
        titolo=titolo,
        data=data or "not available",
        contenuto=contenuto[:6000],
        lingua=lingua,
    )
    msg = call_claude(
        model="claude-sonnet-4-6",
        max_tokens=900,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


# ── Job principale ──────────────────────────────────────────────────────────────

async def show_monitor_menu(context, chat_id: int = None, username: str = "owner") -> None:
    """Manda il messaggio con la tastiera inline per scegliere la fonte da scansionare.
    Usato sia dal job giornaliero che dal comando /monitor.
    """
    if chat_id is None:
        chat_id = context.bot_data.get("owner_chat_id")
    if not chat_id:
        logger.warning("Monitor: chat_id non trovato — manda /start al bot per registrarti")
        return
    # Salva username associato a questo chat per i callback
    context.bot_data[f"monitor_username_{chat_id}"] = username

    sources = _load_sources()
    seen_groups = set()
    buttons = []
    for i, s in enumerate(sources):
        group = s.get("group")
        if group:
            if group not in seen_groups:
                seen_groups.add(group)
                buttons.append([InlineKeyboardButton(group, callback_data=f"mon_fonte:group:{group}")])
        else:
            buttons.append([InlineKeyboardButton(s["name"], callback_data=f"mon_fonte:{i}")])
    buttons.append([InlineKeyboardButton("📋 Tutte le fonti", callback_data="mon_fonte:all")])

    from bot import _t
    from users import get_lang
    lang = get_lang(chat_id) if chat_id else "it"
    await context.bot.send_message(
        chat_id=chat_id,
        text=_t("monitor_menu", lang),
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def _run_scan(context, sources: list[dict], chat_id: int = None, username: str = "owner") -> None:
    """Esegue la scansione sulle fonti indicate e notifica i risultati."""
    from bot import TOPICS

    if chat_id is None:
        chat_id = context.bot_data.get("owner_chat_id")
    if not chat_id:
        logger.warning("Monitor: chat_id non trovato — manda /start al bot per registrarti")
        return

    _init_db()
    loop = asyncio.get_event_loop()
    from users import get_lang, get_approved_at
    from bot import OWNER_TELEGRAM_ID, is_owner
    lang = get_lang(chat_id) if chat_id else "it"
    is_owner_user = (chat_id == OWNER_TELEGRAM_ID)
    approved_at = get_approved_at(chat_id) if (chat_id and not is_owner_user) else None

    # Converti approved_at in struct_time per confronto con published_parsed RSS
    import time as _time
    approved_at_struct = None
    if approved_at:
        try:
            approved_at_struct = _time.strptime(approved_at[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    # Contatore bozze salvate in bot_data per i callback
    # Le bozze sono scoped per chat_id per evitare cross-contamination tra utenti
    drafts: dict = context.bot_data.setdefault("monitor_drafts", {})
    draft_counter: int = context.bot_data.get(f"monitor_draft_counter_{chat_id}", 0)

    errori: list[tuple[str, str]] = []
    trovati: int = 0

    for source in sources:
        name = source["name"]
        url  = source["url"]

        try:
            items = (
                await _fetch_rss(url, timeout=source.get("timeout", 20))
                if source["type"] == "rss"
                else await _fetch_html_links(url, link_filter=source.get("link_filter"),
                                             timeout=source.get("timeout", 15))
            )
            fetch_err = ""
        except Exception as exc:
            items = None
            fetch_err = str(exc)[:120]

        if items is None:
            errori.append((name, fetch_err or "nessuna risposta/timeout"))
            logger.warning(f"Monitor: fonte non raggiungibile — {name} ({fetch_err})")
            continue

        logger.info(f"Monitor: {name} — {len(items)} elementi da controllare")

        # Non-owner + HTML: primo accesso → seed da owner e skip
        if not is_owner_user and source["type"] == "html" and not _has_seen_source(str(chat_id), name):
            for item in items:
                if item["url"]:
                    _mark_seen(item["url"], item["title"], name, 0.0, str(chat_id))
            from bot import _t
            await context.bot.send_message(
                chat_id=chat_id,
                text=_t("html_seeded", lang).format(name=name),
                parse_mode="Markdown",
            )
            continue

        nuovi = 0
        riepilogo_fonte = []

        for item in items:
            item_url = item["url"]
            if not item_url:
                continue
            if _is_seen(item_url, str(chat_id)):
                continue

            # Non-owner + RSS: salta item pubblicati prima di approved_at
            if not is_owner_user and source["type"] == "rss" and approved_at_struct:
                pub = item.get("published")
                if pub and pub < approved_at_struct:
                    _mark_seen(item_url, item["title"], name, 0.0, str(chat_id))
                    continue

            nuovi += 1

            # Se la fonte richiede fetch_summary, scarica la pagina per avere un sommario
            if source.get("fetch_summary") and not item.get("summary"):
                page_text, _ = await _fetch_content(item_url)
                item["summary"] = page_text[:1500]

            # Valutazione rapida con Haiku (in thread per non bloccare l'event loop)
            relevance = await loop.run_in_executor(
                None, _assess_relevance, item["title"], item["summary"], str(chat_id)
            )
            score   = float(relevance.get("score", 0))
            settore = relevance.get("settore", "altro")
            motivo  = relevance.get("motivo", "")

            _mark_seen(item_url, item["title"], name, score, str(chat_id))
            riepilogo_fonte.append((score, settore, item["title"][:80], motivo))

            if score < 5:
                continue

            trovati += 1
            logger.info(f"Monitor: documento rilevante [{score}/10] — {item['title'][:60]}")

            # Per RSS: usa content:encoded o summary (evita fetch pagina → Cloudflare)
            # Per HTML: fetch contenuto completo della pagina
            if source["type"] == "rss":
                rss_content = item.get("content", "") or item.get("summary", "")
                contenuto, data = rss_content[:8000], ""
            else:
                contenuto, data = await _fetch_content(item_url)
            bozza = await loop.run_in_executor(
                None, _generate_post, name, item["title"], contenuto, data, lang
            )
            from bot import _t
            bozza = (
                f"📌 {name}\n\n{bozza}\n\n"
                f"🔗 {item_url}\n\n"
                f"---\n"
                f"{_t('footer', 'it')}\n"
                f"{_t('footer', 'en')}"
            )

            # Salva bozza in bot_data per il callback
            # draft_id = "{chat_id}_{counter}" per evitare sovrapposizioni tra utenti
            draft_counter += 1
            draft_id = f"{chat_id}_{draft_counter}"
            draft_data = {
                "titolo":      item["title"],
                "bozza":       bozza,
                "url":         item_url,
                "settore":     settore,
                "source_name": name,
                "username":    username,
                "chat_id":     str(chat_id),
                "lang":        lang,
                "contenuto":   contenuto[:6000],
            }
            drafts[draft_id] = draft_data
            _save_draft(draft_id, draft_data)
            context.bot_data[f"monitor_draft_counter_{chat_id}"] = draft_counter

            # Messaggio Telegram con bozza
            topic_label = TOPICS.get(settore, "📌 Altro")
            if len(bozza) <= 600:
                anteprima = bozza
            else:
                # Taglia sempre all'ultimo punto entro 600 caratteri
                taglio = bozza[:600].rfind(".")
                if taglio == -1:
                    taglio = 599  # nessun punto trovato: taglio duro
                anteprima = bozza[:taglio + 1] + "…"
            testo = (
                f"📋 *Nuovo documento — {name}*\n"
                f"Score: {score:.0f}/10 · {topic_label}\n"
                f"*{item['title'][:100]}*\n"
                f"_{motivo[:150]}_\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{anteprima}"
            )
            # Telegram limite 4096 caratteri
            if len(testo) > 4000:
                testo = testo[:4000] + "…"

            from bot import OWNER_TELEGRAM_ID, _t
            rows = []
            if chat_id == OWNER_TELEGRAM_ID:
                rows.append([
                    InlineKeyboardButton("⭐",     callback_data=f"mon_rating:{draft_id}:1"),
                    InlineKeyboardButton("⭐⭐",   callback_data=f"mon_rating:{draft_id}:2"),
                    InlineKeyboardButton("⭐⭐⭐", callback_data=f"mon_rating:{draft_id}:3"),
                    InlineKeyboardButton("⭐⭐⭐⭐",   callback_data=f"mon_rating:{draft_id}:4"),
                    InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data=f"mon_rating:{draft_id}:5"),
                ])
            action_row = [
                InlineKeyboardButton(_t("use_post", lang), callback_data=f"mon_usa:{draft_id}"),
                InlineKeyboardButton(_t("ignore",   lang), callback_data=f"mon_ignora:{draft_id}"),
            ]
            if chat_id == OWNER_TELEGRAM_ID:
                action_row.append(InlineKeyboardButton(_t("translate", lang), callback_data=f"mon_traduci:{draft_id}"))
            rows.append(action_row)
            keyboard = InlineKeyboardMarkup(rows)

            await context.bot.send_message(
                chat_id=chat_id,
                text=testo,
                parse_mode="Markdown",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )

            await asyncio.sleep(3)

        # Riepilogo per fonte
        if riepilogo_fonte:
            righe = [f"📊 *{name}* — {nuovi} nuovi documenti valutati:\n"]
            for score, settore, titolo, motivo in sorted(riepilogo_fonte, reverse=True):
                emoji = "🟢" if score >= 5 else "⚪"
                righe.append(f"{emoji} [{score:.0f}/10] {titolo}\n   _{motivo}_")
            await context.bot.send_message(
                chat_id=chat_id,
                text="\n".join(righe),
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        else:
            from bot import _t
            n_items = len(items) if items else 0
            await context.bot.send_message(
                chat_id=chat_id,
                text=_t("no_new_docs", lang).format(name=name) + f"\n_(feed: {n_items} item, tutti già visti)_",
                parse_mode="Markdown",
            )

    # Riepilogo finale
    if errori:
        from bot import _t
        righe = [_t("sources_unreachable", lang).format(sources="")]
        for nome, motivo in errori:
            righe.append(f"• *{nome}*: `{motivo}`")
        await context.bot.send_message(
            chat_id=chat_id,
            text="\n".join(righe),
            parse_mode="Markdown",
        )

    logger.info(f"Monitor: completato. Rilevanti: {trovati}, errori fonti: {len(errori)}")


async def _show_recent_seen(context, chat_id: int, source_names: list[str]) -> None:
    """Mostra i documenti già visti negli ultimi 7 giorni per le fonti indicate."""
    con = _db_connect()
    placeholders = ",".join("?" * len(source_names))
    rows = con.execute(
        f"SELECT title, url, score, seen_at FROM seen_docs "
        f"WHERE chat_id IN (?, 'owner') AND source IN ({placeholders}) "
        f"AND seen_at >= datetime('now', '-30 days') "
        f"ORDER BY seen_at DESC LIMIT 30",
        (str(chat_id), *source_names),
    ).fetchall()
    con.close()

    # Debug temporaneo: mostra sempre quante righe trova e con quali chat_id
    con2 = _db_connect()
    all_sources = con2.execute(
        f"SELECT DISTINCT chat_id, source, COUNT(*) FROM seen_docs "
        f"WHERE source IN ({placeholders}) GROUP BY chat_id, source",
        source_names,
    ).fetchall()
    con2.close()
    debug = "\n".join(f"  `{cid}` | {src} | {n}" for cid, src, n in all_sources)
    await context.bot.send_message(chat_id=chat_id,
        text=f"🔍 Debug seen_docs:\n{debug or '(vuoto)'}", parse_mode="Markdown")

    if not rows:
        return

    righe = ["📅 *Ultimi 30 giorni — già visti:*\n"]
    for title, url, score, seen_at in rows:
        data = seen_at[:10] if seen_at else "?"
        emoji = "🟢" if (score or 0) >= 5 else "⚪"
        righe.append(f"{emoji} [{score:.0f}/10] {data} — [{title[:70]}]({url})")

    testo = "\n".join(righe)
    if len(testo) > 4000:
        testo = testo[:4000] + "…"
    await context.bot.send_message(
        chat_id=chat_id,
        text=testo,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


# ── Callback handlers (da registrare in bot.py) ─────────────────────────────────

async def handle_mon_fonte_cb(update, context) -> None:
    """Utente ha scelto la fonte dal menu — avvia la scansione."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    token = query.data.split(":", 1)[1]  # "all", "group:ADM", oppure indice numerico
    sources = _load_sources()

    if token == "all":
        selected = sources
        label = "tutte le fonti"
    elif token.startswith("group:"):
        group_name = token.split(":", 1)[1]
        selected = [s for s in sources if s.get("group") == group_name]
        label = group_name
    else:
        idx = int(token)
        selected = [sources[idx]] if idx < len(sources) else []
        label = selected[0]["name"] if selected else "fonte sconosciuta"

    if not selected:
        await query.message.reply_text("⚠️ Fonte non trovata.")
        return

    chat_id  = query.message.chat.id
    username = context.bot_data.get(f"monitor_username_{chat_id}", "owner")
    from bot import _t
    from users import get_lang
    lang = get_lang(chat_id)
    await query.message.reply_text(_t("scan_start", lang).format(label=label), parse_mode="HTML")
    await _run_scan(context, selected, chat_id=chat_id, username=username)

    # Per selezioni specifiche (non "tutte le fonti"), mostra anche i visti nell'ultima settimana
    if token != "all":
        source_names = [s["name"] for s in selected]
        await _show_recent_seen(context, chat_id, source_names)


async def _save_post_to_report(context, draft: dict, reply_target, notify_errors: bool = False) -> None:
    """Salva la bozza monitor nel file report del giorno e pusha su GitHub."""
    import subprocess
    from datetime import datetime
    from bot import BASE_DIR, TOPICS

    settore     = draft.get("settore", "altro")
    topic_lbl   = TOPICS.get(settore, "📌 Altro")
    source_name = draft.get("source_name", "")
    username    = draft.get("username", "owner")
    date_str    = datetime.now().strftime("%Y-%m-%d")
    time_str    = datetime.now().strftime("%H:%M")

    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / f"{date_str}.md"

    # Calcola il numero del prossimo post
    post_num = 1
    if report_path.exists():
        text = report_path.read_text(encoding="utf-8")
        import re
        post_num = len(re.findall(r"^## Post \d+", text, re.MULTILINE)) + 1

    mode = "a" if report_path.exists() else "w"
    with open(report_path, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write(f"# Report LinkedIn — {date_str}\n**Temi:** {topic_lbl}\n\n")
        f.write(f"## Post {post_num} — {time_str}\n\n")
        f.write(f"**Focus:** {draft['titolo'][:120]}  \n")
        f.write(f"**Temi:** {topic_lbl}  \n")
        f.write(f"**Angolo normativo:** {source_name}  \n")
        f.write(f"**Autore:** @{username}  \n")
        f.write(f"\n{draft['bozza']}\n\n---\n\n")

    from bot import _t
    from users import get_lang
    lang = get_lang(int(draft.get("chat_id", 0))) if draft.get("chat_id") else "it"
    await reply_target.reply_text(_t("saved", lang).format(date=date_str), parse_mode="Markdown")

    # Git push + refresh sito
    loop = asyncio.get_event_loop()
    def _git_push():
        # Pull prima di pushare per evitare conflitti
        subprocess.run(["git", "-C", str(BASE_DIR), "pull", "--rebase"],
                       capture_output=True, text=True)
        r1 = subprocess.run(["git", "-C", str(BASE_DIR), "add", f"reports/{date_str}.md"],
                            capture_output=True, text=True)
        r2 = subprocess.run(["git", "-C", str(BASE_DIR), "commit", "-m",
                              f"report: monitor post {date_str} ({source_name})"],
                            capture_output=True, text=True)
        r3 = subprocess.run(["git", "-C", str(BASE_DIR), "push"],
                            capture_output=True, text=True)
        if r3.returncode != 0:
            output = "\n".join(filter(None, [r1.stderr, r2.stderr, r3.stdout, r3.stderr]))
            raise RuntimeError(output or "push fallito")
    try:
        await loop.run_in_executor(None, _git_push)
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post("https://nt-report-api.onrender.com/api/refresh")
        await reply_target.reply_text(_t("site_updated", lang))
    except Exception as e:
        logger.warning(f"Monitor git push fallito: {e}")
        if notify_errors:
            await reply_target.reply_text(f"⚠️ Push fallito: {str(e)[:400]}")


async def handle_mon_rating_cb(update, context) -> None:
    """Utente ha assegnato un rating ⭐ — salva e rimuove i bottoni."""
    query = update.callback_query
    parts = query.data.split(":")  # mon_rating:{draft_id}:{stars}
    draft_id = parts[1]
    stars = int(parts[2])

    drafts = context.bot_data.get("monitor_drafts", {})
    draft  = drafts.get(draft_id)
    if draft:
        chat_id = str(query.message.chat.id)
        _save_rating(draft["url"], stars, chat_id)

    await query.answer(f"{'⭐' * stars} salvato")
    await query.edit_message_reply_markup(reply_markup=None)


async def handle_mon_usa_cb(update, context) -> None:
    """Utente ha cliccato 'Usa questo post' — salva rating 5 e mostra il testo completo."""
    query = update.callback_query
    await query.answer()

    try:
        draft_id = query.data.split(":", 1)[1]
        drafts   = context.bot_data.get("monitor_drafts", {})
        draft    = drafts.get(draft_id) or _load_draft(draft_id)

        from bot import _t
        from users import get_lang
        lang = get_lang(query.message.chat.id)

        if not draft:
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(_t("draft_unavailable", lang))
            return

        _save_rating(draft["url"], 5, str(query.message.chat.id))
        await query.edit_message_reply_markup(reply_markup=None)

        reply_text = (
            f"{_t('post_full', lang)}\n\n{draft['bozza']}\n\n"
            f"{_t('source_label', lang)} {draft['url']}"
        )
        try:
            await query.message.reply_text(reply_text, parse_mode="Markdown",
                                           disable_web_page_preview=True)
        except Exception:
            await query.message.reply_text(reply_text, disable_web_page_preview=True)

        # Salva nel report del giorno e pusha sul sito
        from bot import is_owner
        await _save_post_to_report(context, draft, query.message,
                                   notify_errors=is_owner(update))

    except Exception as exc:
        logger.exception("Errore in handle_mon_usa_cb")
        try:
            await query.message.reply_text(f"⚠️ Errore: {type(exc).__name__}: {str(exc)[:300]}")
        except Exception:
            pass


async def handle_mon_ignora_cb(update, context) -> None:
    """Utente ha cliccato 'Ignora' — salva rating 1 e rimuove i bottoni."""
    query = update.callback_query
    parts = query.data.split(":", 1)
    if len(parts) > 1:
        drafts = context.bot_data.get("monitor_drafts", {})
        draft  = drafts.get(parts[1]) or _load_draft(parts[1])
        if draft:
            _save_rating(draft["url"], 1, str(query.message.chat.id))
    await query.answer("Documento ignorato.")
    await query.edit_message_reply_markup(reply_markup=None)


async def handle_mon_traduci_cb(update, context) -> None:
    """Owner clicca 'Traduci' — rigenera la bozza nell'altra lingua."""
    query = update.callback_query
    await query.answer()

    draft_id = query.data.split(":", 1)[1]
    drafts   = context.bot_data.get("monitor_drafts", {})
    draft    = drafts.get(draft_id) or _load_draft(draft_id)

    if not draft:
        await query.message.reply_text("⚠️ Bozza non più disponibile.")
        return

    from bot import _t, OWNER_TELEGRAM_ID
    from users import get_lang, set_lang
    chat_id = query.message.chat.id
    current_lang = draft.get("lang", get_lang(chat_id))
    new_lang = "en" if current_lang == "it" else "it"

    await query.message.reply_text(f"⏳ Traduzione in corso…")

    loop = asyncio.get_event_loop()
    contenuto = draft.get("contenuto", "")
    new_bozza = await loop.run_in_executor(
        None, _generate_post, draft["source_name"], draft["titolo"], contenuto, "", new_lang
    )
    new_bozza = (
        f"📌 {draft['source_name']}\n\n{new_bozza}\n\n"
        f"🔗 {draft['url']}\n\n"
        f"---\n"
        f"{_t('footer', 'it')}\n"
        f"{_t('footer', 'en')}"
    )

    # Aggiorna il draft con la nuova lingua e bozza e persisti su DB
    draft["bozza"] = new_bozza
    draft["lang"]  = new_lang
    _save_draft(draft_id, draft)

    # Rimuovi i bottoni dal messaggio originale
    await query.edit_message_reply_markup(reply_markup=None)

    # Ri-aggiungi i bottoni sul messaggio tradotto
    action_row = [
        InlineKeyboardButton(_t("use_post", new_lang), callback_data=f"mon_usa:{draft_id}"),
        InlineKeyboardButton(_t("ignore",   new_lang), callback_data=f"mon_ignora:{draft_id}"),
    ]
    if chat_id == OWNER_TELEGRAM_ID:
        action_row.append(InlineKeyboardButton(_t("translate", new_lang), callback_data=f"mon_traduci:{draft_id}"))
    keyboard = InlineKeyboardMarkup([action_row])

    try:
        await query.message.reply_text(
            f"{_t('post_full', new_lang)}\n\n{new_bozza}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=keyboard,
        )
    except Exception:
        await query.message.reply_text(
            f"{_t('post_full', new_lang)}\n\n{new_bozza}",
            disable_web_page_preview=True,
            reply_markup=keyboard,
        )
