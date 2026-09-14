"""
rassegna.py — Mini rassegna stampa quotidiana, in PDF, per stampa fisica.

Pipeline separata dal monitoraggio normativo (monitor.py): qui le fonti generaliste e gli
approfondimenti personali NON passano per lo scoring di rilevanza legale di Haiku né
generano bozze LinkedIn — sono solo selezionati/riassunti e impaginati in un PDF.

Struttura del giornale (richiesta da Niccolò il 2026-09-14):
  1. Prima pagina — sintesi dei titoli principali di tutte le sezioni
  2. Professionale — energia, giochi, concessioni, tecnologia (~2 pagine)
  3. Interessi — geopolitica/guerra, difesa IT/UE, politica estera, cavidotti sottomarini,
     estrazione dai fondali marini, spazio, scienza (fisica/biologia/materiali) (~3 pagine,
     solo se c'è qualcosa di rilevante)
  4. Attualità — cronaca, politica/economia generale, sport (~1 pagina)
  5. Varie — cruciverba, un piatto/vino/ristorante, una mostra, un'attività coi bambini,
     un libro, un disco (~1 pagina)

Il job in bot.py chiama genera_rassegna_pdf() ogni mattina, poi carica il risultato su
Drive (monitor.py, _upload_rassegna_to_drive) sovrascrivendo un file placeholder già
esistente — mai creando un file nuovo, per non incappare di nuovo in storageQuotaExceeded.
"""

import asyncio
import logging
import random
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
RASSEGNA_DIR = BASE_DIR / "rassegna"

# ── Fonti ────────────────────────────────────────────────────────────────────────
# NB: il feed storico corriere.it/rss/homepage.xml serve contenuto fermo al 2024 (sezione
# abbandonata) — si usano le sezioni principali verificate attive (verificato 2026-09-14,
# tutte con pubDate di oggi).
_ATTUALITA_FEEDS = [
    ("Corriere — Politica", "https://www.corriere.it/dynamic-feed/rss/section/Politica.xml"),
    ("Corriere — Economia", "https://www.corriere.it/dynamic-feed/rss/section/Economia.xml"),
    ("Corriere — Cronache", "https://www.corriere.it/dynamic-feed/rss/section/Cronache.xml"),
    ("Il Foglio", "https://naxos.ilfoglio.it/api/v5/rss/stories/latest"),
    ("Dagospia", "https://raw.githubusercontent.com/this1-it/dagospia/main/rss.xml"),
]

_TECNOLOGIA_FEEDS = [
    ("Agenda Digitale", "https://www.agendadigitale.eu/feed/"),
    ("Key4biz", "https://www.key4biz.it/feed/"),
]

_INTERESSI_FEEDS = [
    ("Analisi Difesa", "https://www.analisidifesa.it/feed"),
    ("Foreign Policy", "https://foreignpolicy.com/feed/"),
    ("ANSA — Mondo", "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml"),
    ("gCaptain", "https://www.gcaptain.com/feed/"),
    ("SpaceNews", "https://spacenews.com/feed/"),
    ("ESA", "https://www.esa.int/rssfeed/Our_Activities"),
    ("Phys.org — Fisica", "https://phys.org/rss-feed/physics-news/"),
    ("Phys.org — Biologia", "https://phys.org/rss-feed/biology-news/"),
    ("Phys.org — Materiali", "https://phys.org/rss-feed/chemistry-news/materials-science/"),
]

_INTERESSI_TEMI = """
- scenari internazionali di guerra e conflitti in corso
- settore difesa italiano ed europeo (industria, procurement, dottrina)
- politica estera e relazioni internazionali
- cavidotti sottomarini (posa, sabotaggi, infrastrutture critiche)
- attività estrattiva dai fondali marini (mining sottomarino, risorse minerarie)
- autorizzazioni spaziali e spazio in generale (lanci, satelliti, normativa spaziale)
- scienza: fisica, biologia, scienza dei materiali (scoperte rilevanti, non divulgazione generica)
""".strip()

_GIUSTIZIA_AMMINISTRATIVA_URL = "https://www.giustizia-amministrativa.it/web/guest/echi-d-europa-ufficio-studi"
_OROSCOPO_RSS = "https://www.ilsussidiario.net/feed/"

_SETTORI_LABEL = {"energia": "Energia", "concessioni": "Concessioni demaniali", "giochi": "Giochi"}

_JUNK_TITLE_PATTERNS = re.compile(r"apre una nuova finestra|^(Facebook|X|Twitter|LinkedIn|Instagram|YouTube)\s*:?\s*$", re.IGNORECASE)
_JUNK_TITLE_EXACT = {
    "comunicati stampa", "servizi digitali", "agenda trasparente", "antifrode e laboratori",
    "amministrazione trasparente", "note legali", "privacy policy", "mappa del sito",
    "ministero dell'economia e delle finanze", "ministero dell'economia e delle finanze mef",
    "contatti e assistenza", "relazioni con gli operatori",
}


def _is_junk_title(title: str) -> bool:
    """Filtra i link di navigazione/menu/social (alcune pagine PA statiche restituiscono
    voci di menu come se fossero notizie) — non fanno danno nel monitoraggio principale
    (Haiku li scarta per rilevanza), ma qui vengono mostrati direttamente senza scoring."""
    if not title:
        return True
    if _JUNK_TITLE_PATTERNS.search(title):
        return True
    if title.strip().lower() in _JUNK_TITLE_EXACT:
        return True
    if len(title.strip()) < 20:
        return True
    return False


def _clean_title(title: str) -> str:
    """Alcune pagine HTML concatenano etichetta+data+titolo senza spazi nel testo del link
    (es. 'Comunicato stampa11/09/2026Testo...') perché BeautifulSoup unisce nodi di testo
    adiacenti — qui si inseriscono spazi/trattino attorno alle date per leggibilità."""
    if not title:
        return title
    title = re.sub(r"(?<=[a-zà-ù])(\d{1,2}/\d{1,2}/\d{4})", r" \1", title)
    title = re.sub(r"(\d{1,2}/\d{1,2}/\d{4})(?=[A-ZÀ-Ù])", r"\1 — ", title)
    return title.strip()


def _recent(items: list[dict], hours: int = 30) -> list[dict]:
    """Filtra gli item con `published` (time.struct_time) nelle ultime `hours` ore.
    Se un item non ha data, viene tenuto (meglio includere che perdere silenziosamente)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    out = []
    for it in items:
        pub = it.get("published")
        if not pub:
            out.append(it)
            continue
        try:
            pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)
        except Exception:
            out.append(it)
            continue
        if pub_dt >= cutoff:
            out.append(it)
    return out


async def _fetch_feed_list(feeds: list[tuple[str, str]], max_per_fonte: int, hours: int = 30,
                            filter_recent: bool = True) -> list[dict]:
    """Scarica una lista di feed RSS (nome, url), aggiunge il nome fonte a ogni item.
    Nessuno scoring di rilevanza — solo raccolta. Se `filter_recent` è False ritorna anche
    item più vecchi (serve al fallback "sezione mai vuota" di _fetch_settori_professionali)."""
    from monitor import _fetch_rss

    out = []
    for nome, url in feeds:
        try:
            items = await _fetch_rss(url)
        except Exception as e:
            logger.warning(f"Rassegna: fetch fallito per {nome}: {e}")
            items = None
        if not items:
            continue
        candidati = _recent(items, hours) if filter_recent else items
        for it in candidati[:max_per_fonte]:
            it["source_name"] = nome
            out.append(it)
    return out


async def _fetch_attualita(max_per_fonte: int = 4) -> list[dict]:
    return await _fetch_feed_list(_ATTUALITA_FEEDS, max_per_fonte)


_SETTORI_CHAT_ID = "rassegna_settori"  # namespace dedicato in seen_docs, separato da "owner"

# GU, AGCM e Corte Costituzionale sono condivise tra più ambiti (TOPICS_CONFIG le include
# in energia/concessioni/giochi contemporaneamente): pubblicano di tutto, non solo notizie
# in tema. Le fonti di settore vere e proprie (ARERA, PV Magazine, Mondo Balneare, ADM,
# Jamma.it...) sono già mono-tema per costruzione e non hanno bisogno di verifica.
_SHARED_GROUPS = {"GU", "AGCM"}
_SHARED_NAMES = {"Corte Costituzionale"}


def _is_shared_source(s: dict) -> bool:
    return s.get("group") in _SHARED_GROUPS or s["name"] in _SHARED_NAMES


async def _fetch_source_items(s: dict) -> list[dict]:
    from monitor import _fetch_rss, _fetch_html_links

    try:
        fetched = (
            await _fetch_rss(s["url"], timeout=s.get("timeout", 20))
            if s["type"] == "rss"
            else await _fetch_html_links(s["url"], link_filter=s.get("link_filter"),
                                          timeout=s.get("timeout", 15),
                                          no_verify=s.get("no_verify", False))
        )
    except Exception as e:
        logger.warning(f"Rassegna settori: fetch fallito per {s['name']}: {e}")
        return []
    if not fetched:
        return []
    for it in fetched:
        it["source_name"] = s["name"]
    return fetched


# Soglia di pertinenza per le fonti condivise (GU/AGCM/Corte Costituzionale) nella rassegna
# stampa: più alta della soglia 5/10 usata da monitor.py per le bozze LinkedIn. Lì lo scopo è
# "vale la pena valutarlo per un post", qui è "vale la pena stamparlo la mattina" — una barra
# più esigente, per tenere fuori adempimenti/proroghe/nomine di routine e lasciare solo
# notizie di sistema o aggiornamenti normativi importanti (richiesta di Niccolò, 2026-09-14).
_RASSEGNA_SCORE_MIN = 8


async def _score_and_bucket(items: list[dict], valid_settori: set[str]) -> dict[str, list[dict]]:
    """Le fonti condivise (GU, AGCM, Corte Costituzionale) pubblicano di tutto, non solo
    notizie in tema: ogni item viene classificato con lo stesso scoring Haiku
    (_assess_relevance) già usato dal monitoraggio principale, ma con soglia più alta
    (_RASSEGNA_SCORE_MIN) perché qui il bar è "notizia di sistema", non "spunto per un post"
    — e smistato nel settore assegnato dal modello, non in quello della fonte. Una sola
    valutazione per item, non una per ambito: le fonti condivise vengono fetchate/valutate
    una volta sola a monte."""
    if not items:
        return {}
    from monitor import _assess_relevance

    loop = asyncio.get_event_loop()

    async def _score(it: dict):
        try:
            res = await loop.run_in_executor(None, _assess_relevance, it.get("title", ""), it.get("summary", ""))
        except Exception as e:
            logger.warning(f"Rassegna: scoring pertinenza fallito per {it.get('url','')}: {e}")
            return None
        if res.get("settore") in valid_settori and res.get("score", 0) >= _RASSEGNA_SCORE_MIN:
            return res["settore"], it
        return None

    risultati = await asyncio.gather(*[_score(it) for it in items])
    out: dict[str, list[dict]] = {}
    for r in risultati:
        if r:
            settore, it = r
            out.setdefault(settore, []).append(it)
    return out


async def _fetch_settori_professionali(max_per_settore: int = 5) -> dict[str, list[dict]]:
    """Notizie del giorno per energia/giochi/concessioni dalle fonti già configurate in
    sources.md (stesso meccanismo del monitoraggio principale, TOPICS_CONFIG, incluse le
    riviste di settore già censite lì — PV Magazine, Quotidiano Energia, Staffetta Online,
    Rinnovabili.it, Jamma.it, GiocoNews, Press Giochi, Agimeg, Mondo Balneare), più
    tecnologia da due fonti dedicate non presenti in sources.md. Dedup separato dal
    monitoraggio principale (namespace 'rassegna_settori') per non interferire con le
    bozze LinkedIn, che restano basate sul proprio tracking 'owner'.

    Questa è la sezione professionale di Niccolò: non deve mai restare vuota di notizie
    PERTINENTI (meglio vuota che piena di rumore) — se dopo il filtro di pertinenza non
    resta nulla di recente, si ripiega su cascata (vedi _select_with_fallback) fino a
    mostrare almeno l'ultima notizia pertinente disponibile, anche se non recentissima."""
    from monitor import SOURCES, TOPICS_CONFIG, _get_topic_sources, _is_seen, _mark_seen

    def _select_with_fallback(items: list[dict]) -> list[dict]:
        candidati = [it for it in items if not _is_junk_title(it.get("title", ""))]
        if not candidati:
            return []
        recenti = _recent(candidati)
        freschi = [it for it in recenti if not _is_seen(it["url"], chat_id=_SETTORI_CHAT_ID)]
        for it in freschi:
            _mark_seen(it["url"], it["title"], it.get("source_name", ""), 0, chat_id=_SETTORI_CHAT_ID)
        # Fallback a cascata: prima le novità mai viste, poi quelle recenti già viste (nessun
        # aggiornamento ma non vecchie), infine qualunque item pertinente disponibile — mai
        # una lista vuota se esiste almeno un candidato pertinente, anche datato.
        return (freschi or recenti or candidati)[:max_per_settore]

    topic_keys = ("energia", "concessioni", "giochi")
    label_by_topic = {"energia": "Energia", "concessioni": "Concessioni demaniali", "giochi": "Giochi"}

    # Le fonti condivise tra più ambiti vengono raccolte una sola volta (non una per ambito)
    # per non moltiplicare fetch e chiamate di scoring.
    shared_sources: dict[str, dict] = {}
    trusted_by_topic: dict[str, list[dict]] = {k: [] for k in topic_keys}

    for topic_key in topic_keys:
        # Le pagine "Gioco Distanza" (Normativa e Comunicati) condividono lo stesso menu di
        # navigazione statico del sito ADM: senza un link_filter dedicato in sources.md,
        # _fetch_html_links restituisce le voci di menu invece di notizie datate.
        sources = [s for s in _get_topic_sources(topic_key, SOURCES) if "gioco distanza" not in s["name"].lower()]
        for s in sources:
            if _is_shared_source(s):
                shared_sources[s["name"]] = s
            else:
                trusted_by_topic[topic_key].extend(await _fetch_source_items(s))

    shared_items: list[dict] = []
    for s in shared_sources.values():
        shared_items.extend(await _fetch_source_items(s))

    target_settori = {TOPICS_CONFIG[k]["settori"][0] for k in topic_keys}
    verified_by_settore = await _score_and_bucket(shared_items, target_settori)

    result: dict[str, list[dict]] = {}
    for topic_key in topic_keys:
        target_settore = TOPICS_CONFIG[topic_key]["settori"][0]
        combinati = trusted_by_topic[topic_key] + verified_by_settore.get(target_settore, [])
        result[label_by_topic[topic_key]] = _select_with_fallback(combinati)

    tech_items = await _fetch_feed_list(_TECNOLOGIA_FEEDS, max_per_fonte=8, filter_recent=False)
    result["Tecnologia"] = _select_with_fallback(tech_items)

    return result


_GA_CHAT_ID = "rassegna_ga"


async def _fetch_giustizia_amministrativa() -> list[dict]:
    """Bollettini periodici (es. 'Echi d'Europa') dalla pagina Ufficio Studi — HTML statico
    con link a PDF. La pagina elenca sempre TUTTI i bollettini pubblicati (aggiornata
    raramente): senza dedup comparirebbero identici ogni giorno. Si tiene traccia dei PDF
    già visti e si mostrano solo quelli nuovi rispetto all'ultima esecuzione."""
    from monitor import _fetch_html_links, _is_seen, _mark_seen

    try:
        items = await _fetch_html_links(_GIUSTIZIA_AMMINISTRATIVA_URL, link_filter=[".pdf"])
    except Exception as e:
        logger.warning(f"Rassegna: fetch Giustizia Amministrativa fallito: {e}")
        return []
    if not items:
        return []
    nuovi = [it for it in items if not _is_seen(it["url"], chat_id=_GA_CHAT_ID)]
    for it in nuovi:
        it["source_name"] = "Ufficio Studi — Giustizia Amministrativa"
        _mark_seen(it["url"], it["title"], "Giustizia Amministrativa", 0, chat_id=_GA_CHAT_ID)
    return nuovi[:5]


async def _fetch_interessi() -> list[dict]:
    """Raccoglie un pool ampio da fonti di geopolitica/difesa/spazio/scienza, poi chiede a
    Claude di selezionare solo ciò che è realmente pertinente ai temi di interesse
    (`_INTERESSI_TEMI`) — non è scoring binario come per il monitoraggio legale, è
    selezione editoriale: se non c'è nulla di interessante oggi, la lista può restare
    vuota e la sezione lo dice esplicitamente, senza riempitivo forzato."""
    from bot import call_claude

    candidati = await _fetch_feed_list(_INTERESSI_FEEDS, max_per_fonte=8, hours=36)
    if not candidati:
        return []

    elenco = "\n".join(
        f"{i}. [{it['source_name']}] {it['title']}" for i, it in enumerate(candidati)
    )
    prompt = f"""\
Sei il curatore della sezione "Interessi personali" di una rassegna stampa quotidiana per
un avvocato che segue, per interesse personale (non professionale), questi temi:
{_INTERESSI_TEMI}

Di seguito un elenco di titoli raccolti oggi da varie fonti. Scegli SOLO quelli
realmente pertinenti e di qualità (niente gossip, niente cronaca sportiva, niente
articoli genericamente scientifici da rotocalco) — massimo 16, anche meno se non c'è
abbastanza materiale valido. Per ciascuno indica il tema di riferimento tra:
guerra/geopolitica, difesa, politica estera, cavidotti sottomarini, estrazione fondali
marini, spazio, scienza.

Elenco:
{elenco}

Rispondi SOLO con un array JSON, senza testo aggiuntivo, con oggetti
{{"indice": <int>, "tema": "<uno dei temi sopra>"}}. Se nulla è pertinente, rispondi con [].
"""
    try:
        msg = call_claude(
            model="claude-haiku-4-5",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        import json
        selezione = json.loads(raw)
    except Exception as e:
        logger.warning(f"Rassegna interessi: selezione Claude fallita: {e}")
        return []

    out = []
    for sel in selezione:
        idx = sel.get("indice")
        if idx is None or not (0 <= idx < len(candidati)):
            continue
        it = dict(candidati[idx])
        it["tema"] = sel.get("tema", "")
        out.append(it)
    return out


async def _fetch_oroscopo() -> str | None:
    """Best-effort: cerca nel feed RSS di ilsussidiario.net un articolo con 'oroscopo' e
    'paolo fox' nel titolo, pubblicato di recente. Ritorna None se non trovato — la
    sezione viene semplicemente omessa, nessun errore bloccante."""
    from monitor import _fetch_rss

    try:
        items = await _fetch_rss(_OROSCOPO_RSS)
    except Exception as e:
        logger.warning(f"Rassegna: fetch oroscopo fallito: {e}")
        return None
    if not items:
        return None
    from bs4 import BeautifulSoup

    for it in _recent(items, hours=48):
        titolo = (it.get("title") or "").lower()
        if "oroscopo" in titolo and "fox" in titolo:
            raw = it.get("summary") or it.get("content") or ""
            if not raw:
                continue
            testo = BeautifulSoup(raw, "html.parser").get_text(separator=" ", strip=True)
            testo = re.sub(r"\s*The post.*?appeared first on.*$", "", testo, flags=re.IGNORECASE).strip()
            if testo:
                return testo[:2000]
    return None


_DRIVE_TODO_NAME = "ToDo"


def _fetch_todo_list() -> list[str]:
    """Legge la lista ToDo di Niccolò (Google Doc nella cartella Drive condivisa) e la
    restituisce come lista di voci, una per riga non vuota. Non solleva mai: ritorna []
    se il file manca o Drive non è raggiungibile, così la rassegna non si blocca."""
    from monitor import _get_google_creds, _find_drive_file_id, _DRIVE_SA_FILE

    if not _DRIVE_SA_FILE.exists():
        return []
    try:
        from googleapiclient.discovery import build
        creds = _get_google_creds()
        file_id = _find_drive_file_id(creds, _DRIVE_TODO_NAME)
        if not file_id:
            return []
        drive = build("drive", "v3", credentials=creds)
        content = drive.files().export(fileId=file_id, mimeType="text/plain").execute()
        testo = content.decode("utf-8-sig")
        return [riga.strip() for riga in testo.splitlines() if riga.strip()]
    except Exception as e:
        logger.warning(f"Rassegna: lettura ToDo da Drive fallita: {e}")
        return []


def _get_ft_stampa_queue() -> list[dict]:
    """Legge le segnalazioni manuali (FT/La Stampa) non ancora usate e le marca come usate."""
    from monitor import _db_connect, _init_db

    _init_db()
    con = _db_connect()
    rows = con.execute(
        "SELECT id, testo, url FROM rassegna_queue WHERE usato=0 ORDER BY aggiunto_il"
    ).fetchall()
    if rows:
        ids = [r[0] for r in rows]
        con.executemany("UPDATE rassegna_queue SET usato=1 WHERE id=?", [(i,) for i in ids])
        con.commit()
    con.close()
    return [{"testo": r[1], "url": r[2]} for r in rows]


# ── Riassunti (il giornale stampato deve essere autosufficiente, non solo link) ────

def _clean_summary_text(raw: str) -> str:
    """Ripulisce un summary RSS da tag HTML/entità/spazi ripetuti."""
    if not raw:
        return ""
    from bs4 import BeautifulSoup
    text = BeautifulSoup(raw, "html.parser").get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


async def _fetch_pdf_text(url: str) -> str:
    """Estrae il testo delle prime pagine di un PDF (avvisi ADM, bollettini Ufficio Studi
    sono spesso PDF, non HTML — senza questo, _fetch_content li tratterebbe come pagine
    HTML e produrrebbe solo rumore binario)."""
    import io
    import httpx
    from pypdf import PdfReader

    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        reader = PdfReader(io.BytesIO(resp.content))
        return "\n".join((page.extract_text() or "") for page in reader.pages[:5])[:4000]
    except Exception as e:
        logger.warning(f"Rassegna: estrazione PDF fallita per {url}: {e}")
        return ""


async def _ensure_material(it: dict) -> None:
    """Garantisce che l'item abbia abbastanza materiale testuale per un riassunto fedele:
    usa il summary RSS se sostanzioso, altrimenti scarica il testo della pagina (o del PDF).
    Se anche quello fallisce, il riassunto verrà generato dal solo titolo (nessun dato
    inventato, solo genericità dichiarata al modello in _summarize_items)."""
    from monitor import _fetch_content

    materiale = _clean_summary_text(it.get("summary") or it.get("content") or "")
    if len(materiale) < 60:
        url = it.get("url", "")
        try:
            testo = await _fetch_pdf_text(url) if ".pdf" in url.lower() else (await _fetch_content(url))[0]
            if len(testo) > len(materiale):
                materiale = testo
        except Exception as e:
            logger.warning(f"Rassegna: fetch contenuto fallito per {url}: {e}")
    it["materiale"] = materiale[:1500]


def _summarize_items(items: list[dict]) -> None:
    """Genera un riassunto fattuale di 2-3 frasi per ciascun item (chiave 'riassunto',
    mutato in place). Una sola chiamata Claude per l'intero batch. Il PDF va stampato e
    deve essere autosufficiente: niente voci con solo titolo e link."""
    if not items:
        return
    from bot import call_claude
    import json

    elenco = "\n\n".join(
        f"{i}. Titolo: {it.get('title','')}\n"
        f"Materiale: {it.get('materiale') or '(nessuno — riassumi in modo generico solo dal titolo)'}"
        for i, it in enumerate(items)
    )
    prompt = f"""\
Per ciascuna delle seguenti notizie scrivi un riassunto fattuale di 2-3 frasi (max 50
parole), in italiano, SOLO sulla base del materiale fornito. Non inventare MAI cifre,
nomi, date o dettagli non presenti nel materiale: se il materiale è insufficiente,
riassumi in modo più generico basandoti solo sul titolo, restando onesto sui limiti
dell'informazione disponibile invece di inventare.

{elenco}

Rispondi SOLO con un array JSON: [{{"indice": <int>, "riassunto": "..."}}, ...]
"""
    try:
        msg = call_claude(
            model="claude-haiku-4-5",
            max_tokens=400 + 120 * len(items),
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        risultati = json.loads(raw)
        for r in risultati:
            idx = r.get("indice")
            if idx is not None and 0 <= idx < len(items):
                items[idx]["riassunto"] = r.get("riassunto", "")
    except Exception as e:
        logger.warning(f"Rassegna: riassunto batch fallito: {e}")


async def _arricchisci_con_riassunti(*gruppi: list[dict]) -> None:
    """Scarica il materiale mancante (concorrente) e genera i riassunti per ogni gruppo di
    item passato (un gruppo = una sezione, per tenere le chiamate Claude ragionevoli)."""
    tutti = [it for gruppo in gruppi for it in gruppo]
    if not tutti:
        return
    await asyncio.gather(*[_ensure_material(it) for it in tutti])
    for gruppo in gruppi:
        _summarize_items(gruppo)


# ── Sezione "Varie" (contenuti generati, non notizie) ─────────────────────────────

def _genera_varie() -> dict[str, str]:
    """Un blocco di spunti non-notiziosi: piatto/vino/ristorante, mostra, attività con
    bambini, libro, disco. Sono spunti EVERGREEN (classici, non legati a un evento con
    data/luogo verificabile solo oggi) per evitare di presentare come fatto verificato
    qualcosa che un modello linguistico non può controllare in tempo reale (es. una mostra
    con date/sede specifiche che potrebbe non esistere)."""
    from bot import call_claude
    import json

    prompt = """\
Genera spunti per la rubrica "Varie" di una rassegna stampa personale per un avvocato
italiano appassionato di cultura generale. Servono 5 suggerimenti BREVI (max 2 frasi
ciascuno), in italiano, in tono colloquiale ma non sciatto:

1. piatto_vino: un abbinamento piatto+vino della tradizione italiana da provare (classico,
   non legato a un ristorante specifico che non puoi verificare esista ancora)
2. mostra: un suggerimento culturale SENZA inventare date/sedi di mostre temporanee
   specifiche che non puoi verificare — va bene un museo/collezione permanente italiana
   nota, o un genere di mostra da cercare nella propria città
3. attivita_bambini: un'idea di attività da fare con bambini, generica e replicabile
   (non legata a un evento specifico con data)
4. libro: un libro (classico o comunque consolidato, non un'uscita recentissima che non
   puoi verificare) pertinente a diritto, economia, storia o scienza
5. disco: un disco/album (qualsiasi genere) da riascoltare

Rispondi SOLO con un oggetto JSON valido:
{"piatto_vino": "...", "mostra": "...", "attivita_bambini": "...", "libro": "...", "disco": "..."}
"""
    try:
        msg = call_claude(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"Rassegna varie: generazione fallita: {e}")
        return {}


# ── Cruciverba ─────────────────────────────────────────────────────────────────────

_CRUCIVERBA_TEMI = [
    "diritto e istituzioni italiane", "energia e ambiente", "spazio e astronomia",
    "storia contemporanea", "geografia europea", "cultura generale",
]


def _genera_parole_cruciverba() -> list[tuple[str, str]]:
    """Chiede a Claude 7 parole italiane brevi (5-9 lettere, senza spazi né accenti) con
    definizione in stile cruciverba, su un tema a rotazione giornaliera."""
    from bot import call_claude
    import json

    tema = _CRUCIVERBA_TEMI[datetime.now().toordinal() % len(_CRUCIVERBA_TEMI)]
    prompt = f"""\
Genera 7 parole italiane per un mini cruciverba, tema: {tema}.
Regole per ogni parola: 5-9 lettere, UNA sola parola (no spazi, no trattini, no accenti,
tutto maiuscolo), niente nomi propri.
Per ognuna scrivi anche la definizione in stile cruciverba (breve, max 8 parole).

Rispondi SOLO con un array JSON: [{{"parola": "ESEMPIO", "definizione": "..."}}, ...]
"""
    try:
        msg = call_claude(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        data = json.loads(raw)
        out = []
        for d in data:
            parola = re.sub(r"[^A-Za-zÀ-ÿ]", "", d.get("parola", "")).upper()
            parola = (parola.replace("À", "A").replace("È", "E").replace("É", "E")
                      .replace("Ì", "I").replace("Ò", "O").replace("Ù", "U"))
            if 4 <= len(parola) <= 10:
                out.append((parola, d.get("definizione", "")))
        return out
    except Exception as e:
        logger.warning(f"Cruciverba: generazione parole fallita: {e}")
        return []


def _crossword_place(words_clues: list[tuple[str, str]]) -> dict:
    """Algoritmo greedy: piazza la prima parola in orizzontale, poi incastra ogni parola
    successiva in un punto di incrocio con una lettera comune a una parola già piazzata.
    Le parole che non trovano un incrocio vengono scartate (meglio un cruciverba piccolo
    ma coerente che forzare un piazzamento scollegato)."""
    words_clues = sorted(set(words_clues), key=lambda wc: -len(wc[0]))
    if not words_clues:
        return {"grid": {}, "placed": []}

    grid: dict[tuple[int, int], str] = {}
    placed: list[dict] = []

    def can_place(word, row, col, direction) -> bool:
        for i, ch in enumerate(word):
            r, c = (row + i, col) if direction == "D" else (row, col + i)
            if grid.get((r, c), ch) != ch:
                return False
        return True

    def do_place(word, row, col, direction) -> None:
        for i, ch in enumerate(word):
            r, c = (row + i, col) if direction == "D" else (row, col + i)
            grid[(r, c)] = ch

    first_word, first_clue = words_clues[0]
    do_place(first_word, 0, 0, "A")
    placed.append({"word": first_word, "clue": first_clue, "row": 0, "col": 0, "dir": "A"})

    for word, clue in words_clues[1:]:
        best = None
        for p in placed:
            for i, ch in enumerate(word):
                for j, pch in enumerate(p["word"]):
                    if ch != pch:
                        continue
                    new_dir = "D" if p["dir"] == "A" else "A"
                    cross_r = p["row"] + (j if p["dir"] == "D" else 0)
                    cross_c = p["col"] + (j if p["dir"] == "A" else 0)
                    row, col = (cross_r - i, cross_c) if new_dir == "D" else (cross_r, cross_c - i)
                    if can_place(word, row, col, new_dir):
                        best = (word, row, col, new_dir)
                        break
                if best:
                    break
            if best:
                break
        if best:
            w, row, col, direction = best
            do_place(w, row, col, direction)
            placed.append({"word": w, "clue": clue, "row": row, "col": col, "dir": direction})

    return {"grid": grid, "placed": placed}


def _crossword_render(result: dict) -> dict | None:
    grid, placed = result["grid"], result["placed"]
    if len(placed) < 2:
        return None

    rows = [r for r, _ in grid]
    cols = [c for _, c in grid]
    min_r, min_c = min(rows), min(cols)
    height, width = max(rows) - min_r + 1, max(cols) - min_c + 1

    norm = [{**p, "row": p["row"] - min_r, "col": p["col"] - min_c} for p in placed]
    starts: dict[tuple[int, int], int] = {}
    for p in sorted(norm, key=lambda p: (p["row"], p["col"])):
        key = (p["row"], p["col"])
        if key not in starts:
            starts[key] = len(starts) + 1

    filled = set()
    for p in norm:
        for i in range(len(p["word"])):
            r, c = (p["row"] + i, p["col"]) if p["dir"] == "D" else (p["row"], p["col"] + i)
            filled.add((r, c))

    rows_html = []
    for r in range(height):
        cells = []
        for c in range(width):
            if (r, c) in filled:
                n = starts.get((r, c), "")
                cells.append(f'<td class="cw-cell"><span class="cw-num">{n}</span></td>')
            else:
                cells.append('<td class="cw-blank"></td>')
        rows_html.append(f"<tr>{''.join(cells)}</tr>")
    grid_html = f'<table class="cw-grid">{"".join(rows_html)}</table>'

    across = sorted((starts[(p["row"], p["col"])], p["clue"]) for p in norm if p["dir"] == "A")
    down = sorted((starts[(p["row"], p["col"])], p["clue"]) for p in norm if p["dir"] == "D")
    answers = ", ".join(
        f'{starts[(p["row"], p["col"])]}. {p["word"]}'
        for p in sorted(norm, key=lambda p: (p["row"], p["col"]))
    )
    return {"grid_html": grid_html, "across": across, "down": down, "answers": answers}


def _genera_cruciverba() -> dict | None:
    parole = _genera_parole_cruciverba()
    if len(parole) < 3:
        return None
    piazzate = _crossword_place(parole)
    return _crossword_render(piazzate)


# ── Composizione HTML ──────────────────────────────────────────────────────────────

_CSS = """
  @page { size: A4; margin: 1.6cm; }
  body { font-family: Georgia, 'Times New Roman', serif; color: #111; font-size: 12px; }
  .page { page-break-after: always; }
  .page:last-child { page-break-after: auto; }
  h1.masthead { font-size: 40px; text-align: center; border-top: 4px solid #111;
                border-bottom: 4px solid #111; padding: 10px 0; margin-bottom: 2px;
                letter-spacing: 2px; font-variant: small-caps; }
  .data { text-align: center; font-style: italic; color: #555; margin-bottom: 16px;
          border-bottom: 1px solid #ccc; padding-bottom: 10px; }
  h2.sezione { font-size: 22px; margin: 0 0 10px 0; border-bottom: 3px solid #111;
               padding-bottom: 4px; font-variant: small-caps; }
  h3 { font-size: 13.5px; margin: 0 0 4px 0; text-transform: uppercase;
       letter-spacing: 0.4px; border-bottom: 1px solid #111; padding-bottom: 2px;
       break-after: avoid; break-inside: avoid; }
  a { color: #111; text-decoration: none; font-weight: bold; }
  .fonte { color: #777; font-size: 10px; font-style: italic; }

  /* Corpo delle sezioni a colonne, come le pagine interne di un giornale */
  .section-body { column-gap: 22px; column-rule: 1px solid #bbb; text-align: justify;
                   hyphens: auto; orphans: 3; widows: 3; }
  .section-body.cols-2 { columns: 2; }
  .section-body.cols-3 { columns: 3; }
  .section-body ul { list-style: none; margin: 0 0 14px 0; padding: 0; }
  .section-body li { margin: 0; padding: 7px 0; line-height: 1.35; border-top: 1px solid #ddd;
                      break-inside: avoid; }
  .section-body li:first-child { border-top: none; }
  .section-body li a { display: block; font-size: 11.5px; margin-bottom: 3px; }
  .section-body li .riassunto { display: block; font-size: 11px; font-weight: normal;
                                  color: #333; margin-bottom: 3px; }
  .section-body .fonte { display: block; margin-top: 2px; }

  /* Prima pagina: titolo di apertura a piena larghezza, poi colonne per il resto */
  .lead { border-bottom: 2px solid #111; padding-bottom: 14px; margin-bottom: 16px; }
  .lead .tag { font-size: 11px; text-transform: uppercase; color: #888; letter-spacing: 0.5px; }
  .lead .titolo { display: block; font-size: 26px; font-weight: bold; line-height: 1.2;
                  margin-top: 4px; font-family: Georgia, serif; }
  .front-cols { columns: 3; column-gap: 24px; column-rule: 1px solid #bbb; text-align: justify;
                hyphens: auto; }
  .headline { margin-bottom: 12px; break-inside: avoid; padding-bottom: 10px; border-bottom: 1px solid #ddd; }
  .headline .tag { font-size: 9px; text-transform: uppercase; color: #888; letter-spacing: 0.5px; }
  .headline .titolo { font-size: 13px; font-weight: bold; display: block; line-height: 1.25; }

  .todo { border: 1px solid #111; padding: 10px 14px; margin-bottom: 16px; }
  .todo h3 { border: none; margin-bottom: 6px; }
  .todo ul { list-style: none; margin: 0; padding: 0; columns: 2; column-gap: 20px; }
  .todo li { font-size: 12px; margin-bottom: 6px; break-inside: avoid; }
  .todo .checkbox { font-size: 13px; margin-right: 4px; }

  .varie-block { margin-bottom: 16px; }
  .varie-block .label { font-weight: bold; }
  table.cw-grid { border-collapse: collapse; margin: 10px 0; }
  table.cw-grid td { width: 26px; height: 26px; text-align: center; vertical-align: top;
                      position: relative; }
  td.cw-cell { border: 1px solid #111; }
  td.cw-blank { border: none; }
  .cw-num { font-size: 8px; position: absolute; top: 1px; left: 2px; }
  .cw-clues { columns: 2; column-gap: 24px; font-size: 12px; }
  .cw-answers { font-size: 9px; color: #999; margin-top: 14px; }
"""


def _render_headline_list(items: list[dict], tag: str, title_key: str = "title") -> str:
    out = []
    for it in items:
        out.append(
            f'<div class="headline"><span class="tag">{tag}</span>'
            f'<span class="titolo">{_clean_title(it.get(title_key, ""))}</span></div>'
        )
    return "".join(out)


def _build_todo_checklist(todo: list[str]) -> str:
    if not todo:
        return ""
    righe = "".join(f'<li><span class="checkbox">☐</span> {voce}</li>' for voce in todo)
    return f'<div class="todo"><h3>Da fare</h3><ul>{righe}</ul></div>'


def _build_front_page(settori: dict, interessi: list, attualita: list, todo: list[str]) -> str:
    top_settori = [it for items in settori.values() for it in items][:4]
    top_interessi = interessi[:5]
    top_attualita = attualita[:5]

    tutti = top_settori + top_interessi + top_attualita
    lead_html = ""
    if tutti:
        lead = tutti[0]
        tutti = tutti[1:]
        tag = "Professionale" if lead in top_settori else ("Interessi" if lead in top_interessi else "Attualità")
        lead_html = f"""
    <div class="lead"><span class="tag">{tag}</span>
      <span class="titolo">{_clean_title(lead.get("title", ""))}</span></div>"""
        top_settori = [it for it in top_settori if it is not lead]
        top_interessi = [it for it in top_interessi if it is not lead]
        top_attualita = [it for it in top_attualita if it is not lead]

    return f"""
<div class="page">
  <h1 class="masthead">NT REPORT</h1>
  <div class="data">{datetime.now().strftime("%A %d %B %Y")}</div>
  {lead_html}
  <div class="front-cols">
    {_render_headline_list(top_settori, "Professionale")}
    {_render_headline_list(top_interessi, "Interessi")}
    {_render_headline_list(top_attualita, "Attualità")}
  </div>
  {_build_todo_checklist(todo)}
</div>"""


def _render_item_li(it: dict) -> str:
    riassunto = it.get("riassunto", "")
    riassunto_html = f'<span class="riassunto">{riassunto}</span>' if riassunto else ""
    fonte = it.get("source_name", "")
    fonte_html = f'<span class="fonte">{fonte}</span>' if fonte else ""
    return (
        f'<li><a href="{it.get("url","")}">{_clean_title(it.get("title",""))}</a>'
        f'{riassunto_html}{fonte_html}</li>'
    )


def _build_settori_page(settori: dict, giustizia_amm: list) -> str:
    blocchi = []
    for label, items in settori.items():
        if not items:
            continue
        righe = "".join(_render_item_li(it) for it in items)
        blocchi.append(f"<h3>{label}</h3><ul>{righe}</ul>")
    corpo = "".join(blocchi) or "<p><em>Nessuna novità nelle fonti professionali oggi.</em></p>"

    if giustizia_amm:
        righe = "".join(_render_item_li(it) for it in giustizia_amm)
        corpo += f"<h3>Giustizia Amministrativa — Ufficio Studi</h3><ul>{righe}</ul>"

    return f"""
<div class="page">
  <h2 class="sezione">Professionale — Energia, Giochi, Concessioni, Tecnologia</h2>
  <div class="section-body cols-2">{corpo}</div>
</div>"""


def _build_interessi_page(interessi: list) -> str:
    if not interessi:
        corpo = "<p><em>Nessuna notizia particolarmente rilevante oggi su questi temi.</em></p>"
    else:
        by_tema: dict[str, list] = {}
        for it in interessi:
            by_tema.setdefault(it.get("tema") or "Altro", []).append(it)
        blocchi = []
        for tema, items in by_tema.items():
            righe = "".join(_render_item_li(it) for it in items)
            blocchi.append(f"<h3>{tema.capitalize()}</h3><ul>{righe}</ul>")
        corpo = "".join(blocchi)

    return f"""
<div class="page">
  <h2 class="sezione">Interessi — Geopolitica, Difesa, Spazio, Scienza</h2>
  <div class="section-body cols-2">{corpo}</div>
</div>"""


def _build_attualita_page(attualita: list, ft_stampa: list) -> str:
    righe = "".join(_render_item_li(it) for it in attualita)
    corpo = f"<ul>{righe}</ul>" if attualita else "<p><em>Nessuna notizia trovata oggi.</em></p>"

    if ft_stampa:
        righe_ft = "".join(
            f'<li>{it["testo"]}' + (f' — <a href="{it["url"]}">link</a>' if it.get("url") else "") + "</li>"
            for it in ft_stampa
        )
        corpo += f'<h3>Dal Financial Times e La Stampa (segnalati a mano)</h3><ul>{righe_ft}</ul>'

    return f"""
<div class="page">
  <h2 class="sezione">Attualità</h2>
  <div class="section-body cols-3">{corpo}</div>
</div>"""


def _build_varie_page(varie: dict, cruciverba: dict | None, oroscopo: str | None) -> str:
    blocchi = []
    labels = {
        "piatto_vino": "A tavola", "mostra": "Da vedere", "attivita_bambini": "Con i bambini",
        "libro": "Da leggere", "disco": "Da ascoltare",
    }
    for key, label in labels.items():
        if varie.get(key):
            blocchi.append(f'<div class="varie-block"><span class="label">{label}:</span> {varie[key]}</div>')
    varie_html = "".join(blocchi)

    cw_html = ""
    if cruciverba:
        clues_a = "".join(f"<li>{n}. {c}</li>" for n, c in cruciverba["across"])
        clues_d = "".join(f"<li>{n}. {c}</li>" for n, c in cruciverba["down"])
        cw_html = f"""
        <h3>Cruciverba</h3>
        {cruciverba["grid_html"]}
        <div class="cw-clues">
          <div><strong>Orizzontali</strong><ul>{clues_a}</ul></div>
          <div><strong>Verticali</strong><ul>{clues_d}</ul></div>
        </div>
        <div class="cw-answers">Soluzioni: {cruciverba["answers"]}</div>"""

    oro_html = f'<div class="varie-block"><span class="label">Oroscopo (Paolo Fox):</span> {oroscopo}</div>' if oroscopo else ""

    return f"""
<div class="page">
  <h2 class="sezione">Varie</h2>
  {varie_html}
  {oro_html}
  {cw_html}
</div>"""


def _build_html(settori, interessi, attualita, giustizia_amm, ft_stampa, varie, cruciverba, oroscopo, todo) -> str:
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<style>{_CSS}</style>
</head>
<body>
  {_build_front_page(settori, interessi, attualita, todo)}
  {_build_settori_page(settori, giustizia_amm)}
  {_build_interessi_page(interessi)}
  {_build_attualita_page(attualita, ft_stampa)}
  {_build_varie_page(varie, cruciverba, oroscopo)}
</body>
</html>"""


# ── Orchestrazione ───────────────────────────────────────────────────────────────

async def run_rassegna_job(context) -> None:
    """Job giornaliero: genera il PDF, lo carica su Drive (per il print agent locale) e lo
    invia come documento Telegram all'owner. Solo per l'owner, non blocca in caso di errori
    parziali (es. upload Drive fallito) — avvisa e prosegue dove possibile."""
    from monitor import _upload_rassegna_to_drive

    chat_id = context.bot_data.get("owner_chat_id")
    if not chat_id:
        logger.warning("Rassegna: owner_chat_id non trovato — manda /start al bot")
        return

    try:
        pdf_path = await genera_rassegna_pdf()
    except Exception as e:
        logger.error(f"Rassegna: generazione PDF fallita: {e}", exc_info=True)
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Rassegna: generazione PDF fallita: {str(e)[:300]}")
        return

    import asyncio
    loop = asyncio.get_event_loop()
    uploaded = await loop.run_in_executor(None, _upload_rassegna_to_drive, pdf_path)
    if uploaded:
        await context.bot.send_message(chat_id=chat_id, text="📂 Rassegna caricata su Drive per la stampa.")
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Upload su Drive saltato o fallito (vedi log) — la stampa automatica non partirà.",
        )

    with open(pdf_path, "rb") as f:
        await context.bot.send_document(chat_id=chat_id, document=f, filename=pdf_path.name)


async def genera_rassegna_html() -> str:
    """Esegue tutti i fetch/generazioni e ritorna l'HTML completo (usato sia dal path di
    produzione — che poi lo converte in PDF con WeasyPrint — sia da test locali)."""
    settori = await _fetch_settori_professionali()
    interessi = await _fetch_interessi()
    attualita = await _fetch_attualita()
    giustizia_amm = await _fetch_giustizia_amministrativa()
    oroscopo = await _fetch_oroscopo()
    ft_stampa = _get_ft_stampa_queue()
    varie = _genera_varie()
    cruciverba = _genera_cruciverba()
    todo = _fetch_todo_list()

    # Il PDF va stampato: ogni voce deve avere un riassunto leggibile, non solo un link.
    settori_items = [it for items in settori.values() for it in items]
    await _arricchisci_con_riassunti(settori_items, interessi, attualita, giustizia_amm)

    return _build_html(settori, interessi, attualita, giustizia_amm, ft_stampa, varie, cruciverba, oroscopo, todo)


async def genera_rassegna_pdf() -> Path:
    """Genera il PDF del giorno e lo salva in rassegna/YYYY-MM-DD.pdf. Non committato su
    git (artefatto binario giornaliero, escluso via .gitignore)."""
    from weasyprint import HTML

    html = await genera_rassegna_html()

    RASSEGNA_DIR.mkdir(exist_ok=True)
    out_path = RASSEGNA_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.pdf"
    HTML(string=html).write_pdf(str(out_path))
    return out_path
