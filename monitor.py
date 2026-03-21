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
Genera un post LinkedIn professionale in italiano sul seguente documento normativo.

Fonte: {fonte}
Titolo: {titolo}
Data documento: {data}

Contenuto del documento:
{contenuto}

Regole:
- Inizia sempre con la data del documento (es. "Il 18 marzo 2025, ARERA ha...")
- Tono professionale, mai sensazionalistico
- Solo fatti e riferimenti normativi presenti nel documento
- Nessuna speculazione o opinione soggettiva
- Massimo 1300 caratteri (testo + hashtag)
- IMPORTANTE: concludi SEMPRE con una frase completa di senso compiuto, mai a metà frase
- Termina con 3-5 hashtag pertinenti
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


def _save_rating(url: str, rating: int, chat_id: str = "owner") -> None:
    con = sqlite3.connect(_db_path())
    con.execute("UPDATE seen_docs SET rating=? WHERE url=? AND chat_id=?", (rating, url, chat_id))
    con.commit()
    con.close()


def _get_rated_examples(chat_id: str = "owner", limit: int = 5) -> tuple[list[str], list[str]]:
    """Restituisce titoli di documenti con rating alto (4-5) e basso (1-2) per questo utente."""
    con = sqlite3.connect(_db_path())
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


def _is_seen(url: str, chat_id: str = "owner") -> bool:
    con = sqlite3.connect(_db_path())
    row = con.execute("SELECT 1 FROM seen_docs WHERE url=? AND chat_id=?", (url, chat_id)).fetchone()
    con.close()
    return row is not None


def _mark_seen(url: str, title: str, source: str, score: float, chat_id: str = "owner") -> None:
    con = sqlite3.connect(_db_path())
    con.execute(
        "INSERT OR IGNORE INTO seen_docs (url, chat_id, title, source, score) VALUES (?,?,?,?,?)",
        (url, chat_id, title, source, score),
    )
    con.commit()
    con.close()


# ── Fetch fonti ─────────────────────────────────────────────────────────────────

async def _fetch_rss(url: str) -> list[dict] | None:
    """Scarica un feed RSS. Restituisce None se la fonte non è raggiungibile."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        feed = feedparser.parse(resp.content)
        items = []
        for entry in feed.entries[:30]:
            if not entry.get("link"):
                continue
            # Estrai contenuto completo se disponibile (content:encoded)
            content = ""
            if hasattr(entry, "content") and entry.content:
                raw = entry.content[0].get("value", "")
                content = BeautifulSoup(raw, "html.parser").get_text(separator="\n", strip=True)
            items.append({
                "url":     entry.get("link", ""),
                "title":   entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "content": content,
            })
        return items
    except Exception as e:
        logger.error(f"Errore fetch RSS {url}: {e}")
        return None


async def _fetch_html_links(url: str, link_filter: list[str] | None = None) -> list[dict] | None:
    """Scrapa una pagina HTML cercando link a comunicati/provvedimenti."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
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


def _generate_post(fonte: str, titolo: str, contenuto: str, data: str = "") -> str:
    """Usa Sonnet per generare la bozza del post LinkedIn."""
    from bot import call_claude
    prompt = _POST_PROMPT.format(
        fonte=fonte,
        titolo=titolo,
        data=data or "non disponibile",
        contenuto=contenuto[:6000],
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

    await context.bot.send_message(
        chat_id=chat_id,
        text="🔍 Quale fonte vuoi scansionare?",
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

    # Contatore bozze salvate in bot_data per i callback
    # Le bozze sono scoped per chat_id per evitare cross-contamination tra utenti
    drafts: dict = context.bot_data.setdefault("monitor_drafts", {})
    draft_counter: int = context.bot_data.get(f"monitor_draft_counter_{chat_id}", 0)

    errori: list[str] = []
    trovati: int = 0

    for source in sources:
        name = source["name"]
        url  = source["url"]

        items = (
            await _fetch_rss(url)
            if source["type"] == "rss"
            else await _fetch_html_links(url, link_filter=source.get("link_filter"))
        )

        if items is None:
            errori.append(name)
            logger.warning(f"Monitor: fonte non raggiungibile — {name}")
            continue

        logger.info(f"Monitor: {name} — {len(items)} elementi da controllare")

        nuovi = 0
        riepilogo_fonte = []

        for item in items:
            item_url = item["url"]
            if not item_url:
                continue
            if _is_seen(item_url, str(chat_id)):
                continue

            nuovi += 1

            # Se la fonte richiede fetch_summary, scarica la pagina per avere un sommario
            if source.get("fetch_summary") and not item.get("summary"):
                page_text, _ = await _fetch_content(item_url)
                item["summary"] = page_text[:1500]

            # Valutazione rapida con Haiku
            relevance = _assess_relevance(item["title"], item["summary"], str(chat_id))
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
            bozza = _generate_post(name, item["title"], contenuto, data)
            bozza = (
                f"📌 {name}\n\n{bozza}\n\n"
                f"🔗 {item_url}\n\n"
                f"---\n"
                f"🤖 Post co-generato con Claude | Approfondisci su nt-report.com"
            )

            # Salva bozza in bot_data per il callback
            # draft_id = "{chat_id}_{counter}" per evitare sovrapposizioni tra utenti
            draft_counter += 1
            draft_id = f"{chat_id}_{draft_counter}"
            drafts[draft_id] = {
                "titolo":      item["title"],
                "bozza":       bozza,
                "url":         item_url,
                "settore":     settore,
                "source_name": name,
                "username":    username,
            }
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

            from bot import OWNER_TELEGRAM_ID
            rows = []
            if chat_id == OWNER_TELEGRAM_ID:
                rows.append([
                    InlineKeyboardButton("⭐",     callback_data=f"mon_rating:{draft_id}:1"),
                    InlineKeyboardButton("⭐⭐",   callback_data=f"mon_rating:{draft_id}:2"),
                    InlineKeyboardButton("⭐⭐⭐", callback_data=f"mon_rating:{draft_id}:3"),
                    InlineKeyboardButton("⭐⭐⭐⭐",   callback_data=f"mon_rating:{draft_id}:4"),
                    InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data=f"mon_rating:{draft_id}:5"),
                ])
            rows.append([
                InlineKeyboardButton("✅ Usa questo post", callback_data=f"mon_usa:{draft_id}"),
                InlineKeyboardButton("🗑 Ignora",          callback_data=f"mon_ignora:{draft_id}"),
            ])
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
        elif not errori:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"ℹ️ *{name}*: nessun documento nuovo oggi.",
                parse_mode="Markdown",
            )

    # Riepilogo finale
    if errori:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⚠️ Fonti non raggiungibili oggi: {', '.join(errori)}",
        )

    logger.info(f"Monitor: completato. Rilevanti: {trovati}, errori fonti: {len(errori)}")


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
    await query.message.reply_text(f"🔍 Scansione: <b>{label}</b>…", parse_mode="HTML")
    await _run_scan(context, selected, chat_id=chat_id, username=username)


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

    await reply_target.reply_text(f"💾 Salvato in `reports/{date_str}.md`", parse_mode="Markdown")

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
        await reply_target.reply_text("🌐 Sito aggiornato.")
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

    draft_id = query.data.split(":", 1)[1]
    drafts   = context.bot_data.get("monitor_drafts", {})
    draft    = drafts.get(draft_id)

    if not draft:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("⚠️ Bozza non più disponibile.")
        return

    _save_rating(draft["url"], 5, str(query.message.chat.id))
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        f"📝 *Post completo — copia e incolla su LinkedIn:*\n\n{draft['bozza']}\n\n"
        f"🔗 Fonte: {draft['url']}",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

    # Salva nel report del giorno e pusha sul sito
    from bot import is_owner
    await _save_post_to_report(context, draft, query.message,
                               notify_errors=is_owner(update))


async def handle_mon_ignora_cb(update, context) -> None:
    """Utente ha cliccato 'Ignora' — salva rating 1 e rimuove i bottoni."""
    query = update.callback_query
    parts = query.data.split(":", 1)
    if len(parts) > 1:
        drafts = context.bot_data.get("monitor_drafts", {})
        draft  = drafts.get(parts[1])
        if draft:
            _save_rating(draft["url"], 1, str(query.message.chat.id))
    await query.answer("Documento ignorato.")
    await query.edit_message_reply_markup(reply_markup=None)
