"""
import_reports.py — Importa posts e documenti in web.db.

Fonti:
  1. reports/*.md  → tabella posts
  2. data/persistence.pkl → tabella documents (analisi PDF già fatte dal bot)

Uso: python -m web.scripts.import_reports
"""
import sys
import json
import logging
import pickle
import sqlite3
import re
from pathlib import Path
from datetime import datetime

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

from web.core.engine import BASE_DIR, _normalize_norma, _NORMA_ALIASES, TOPICS
from web.core.db import DB_PATH, _SCHEMA

# ── Costanti ────────────────────────────────────────────────────────────────────

REPORTS_DIR   = _ROOT / "reports"          # nel repo, non sul disco dati
PICKLE_PATH   = BASE_DIR / "data" / "persistence.pkl"
PDF_BYTES_DIR = BASE_DIR / "data" / "pdf_bytes"

# Mappa emoji→chiave topic presente negli header dei report
_TOPIC_EMOJI = {v: k for k, v in TOPICS.items()}

# Tutte le forme di norma note (per estrarre normas dal testo del post)
_ALL_NORMA_FORMS: list[tuple[str, str]] = []
for canonical, aliases in _NORMA_ALIASES:
    _ALL_NORMA_FORMS.append((canonical, canonical.lower()))
    for alias in aliases:
        _ALL_NORMA_FORMS.append((canonical, alias.lower()))


def _extract_normas_from_text(text: str) -> list[str]:
    """Cerca nel testo del post le norme note e restituisce le forme canoniche."""
    lower = text.lower()
    found = set()
    for canonical, pattern in _ALL_NORMA_FORMS:
        # Usa word boundary per evitare falsi positivi (es. "mica" in "economica")
        if re.search(r'(?<![a-z])' + re.escape(pattern) + r'(?![a-z])', lower):
            found.add(canonical)
    return sorted(found)


def _parse_topic_from_header(temi_line: str) -> str:
    """
    Estrae il primo topic da una riga come '**Temi:** ⚡ Energia, 💻 Tecnologia'.
    Restituisce la chiave interna (es. 'energia') o 'altro'.
    """
    for emoji_label, key in _TOPIC_EMOJI.items():
        if emoji_label in temi_line:
            return key
    return "altro"


def _parse_reports() -> list[dict]:
    """
    Parsa tutti i file reports/*.md e restituisce una lista di post dict.
    Ignora esempio.md.
    """
    posts = []
    for md_file in sorted(REPORTS_DIR.glob("*.md")):
        if md_file.stem == "esempio":
            continue

        # Data dal nome file (YYYY-MM-DD.md)
        try:
            post_date = datetime.strptime(md_file.stem, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            post_date = md_file.stem

        text = md_file.read_text(encoding="utf-8")

        # Topic dall'header del file (fallback per post senza **Temi:** nel corpo)
        file_topic = "altro"
        for line in text.splitlines()[:8]:
            if "**Temi:**" in line or "Temi:" in line:
                file_topic = _parse_topic_from_header(line)
                break

        # Suddivide in sezioni ## Post N — HH:MM
        sections = re.split(r"\n##\s+Post\s+(\d+)\s+[—–-]+\s+(\d{2}:\d{2})", text)

        # sections[0] = tutto prima del primo ## Post → può contenere un post libero
        # sections[1::3] = numeri post, sections[2::3] = orari, sections[3::3] = corpi

        def _make_post(body: str, num: int, time_str: str,
                       focus: str = "", angolo: str = "", topic: str = "altro") -> dict | None:
            body = body.strip()
            if not body or len(body) < 50:
                return None
            # Estrai topic dalla riga **Temi:** nel corpo; fallback al topic del file
            post_topic = topic
            for line in body.splitlines()[:8]:
                if "**Temi:**" in line or "Temi:" in line:
                    post_topic = _parse_topic_from_header(line)
                    break
            # Rimuove righe di metadata dal corpo
            lines = [l for l in body.splitlines()
                     if not re.match(r"\*\*(Focus|Temi|Angolo normativo|Fase \d).*\*\*", l)
                     and l.strip() != "---"]
            body = "\n".join(lines).strip()
            if not body:
                return None
            normas = _extract_normas_from_text(body)
            return {
                "doc_id":      None,
                "post_date":   post_date,
                "post_time":   time_str,
                "post_num":    num,
                "focus":       focus,
                "angolo":      angolo,
                "topic":       post_topic,
                "normas":      json.dumps(normas),
                "body":        body,
                "source_file": md_file.name,
            }

        # Post precedenti al primo ## header (formato vecchio)
        preamble = sections[0]
        # Rimuove header report e cerca blocchi di testo separati da ---
        preamble = re.sub(r"^#.*\n|^\*\*.*\*\*.*\n", "", preamble, flags=re.MULTILINE)
        for i, block in enumerate(preamble.split("---")):
            p = _make_post(block, i + 1, "00:00", topic=file_topic)
            if p:
                posts.append(p)

        # Post strutturati ## Post N
        triples = list(zip(sections[1::3], sections[2::3], sections[3::3]))
        for num_str, time_str, body in triples:
            # Estrai Focus e Angolo dal body
            focus, angolo = "", ""
            for line in body.splitlines()[:6]:
                m = re.search(r"\*\*Focus:\*\*\s*(.+)", line)
                if m:
                    focus = m.group(1).strip()
                m = re.search(r"\*\*Angolo normativo:\*\*\s*(.+)", line)
                if m:
                    angolo = m.group(1).strip()
            p = _make_post(body, int(num_str), time_str, focus, angolo, topic=file_topic)
            if p:
                posts.append(p)

    return posts


class _TolerantUnpickler(pickle.Unpickler):
    """Ignora persistent_id e oggetti sconosciuti invece di sollevare eccezioni."""
    def persistent_load(self, pid):
        return None

    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except Exception:
            # Classe non disponibile (oggetti Telegram, ecc.) → restituisce un placeholder
            return type(name, (), {"__reduce__": lambda s: (dict, ())})


def _parse_pickle() -> list[dict]:
    """
    Legge data/persistence.pkl e restituisce una lista di document dict
    estratti dalle chiavi 'pdf:{msg_id}'.
    """
    if not PICKLE_PATH.exists():
        print("  persistence.pkl non trovato — skip import documenti")
        return []

    with open(PICKLE_PATH, "rb") as f:
        data = _TolerantUnpickler(f).load()

    # PicklePersistence salva in {'bot_data': {...}, 'user_data': {...}, ...}
    bot_data = data.get("bot_data", data) if isinstance(data, dict) else {}

    documents = []
    for key, value in bot_data.items():
        if not (isinstance(key, str) and key.startswith("pdf:") and isinstance(value, dict)):
            continue
        msg_id = key.split(":", 1)[1]
        analysis = value

        # Path del PDF su disco
        pdf_file = PDF_BYTES_DIR / f"{msg_id}.pdf"
        pdf_path = str(pdf_file.relative_to(BASE_DIR)) if pdf_file.exists() else None

        documents.append({
            "id":          f"tg_{msg_id}",
            "titolo":      analysis.get("titolo", ""),
            "autore":      analysis.get("autore", ""),
            "data_pub":    analysis.get("data") or "",
            "sintesi":     analysis.get("sintesi", ""),
            "struttura":   json.dumps(analysis.get("struttura", [])),
            "fonti":       json.dumps(analysis.get("fonti", [])),
            "fonti_index": json.dumps(analysis.get("fonti_index", {})),
            "topic":       "altro",
            "pdf_path":    pdf_path,
        })

    return documents


logger = logging.getLogger(__name__)


def run() -> None:
    logger.info(f"DB: {DB_PATH}")
    logger.info(f"REPORTS_DIR: {REPORTS_DIR} (exists: {REPORTS_DIR.exists()})")
    md_files = list(REPORTS_DIR.glob("*.md")) if REPORTS_DIR.exists() else []
    logger.info(f"File .md trovati: {[f.name for f in md_files]}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(DB_PATH)
    con.executescript(_SCHEMA)
    con.commit()

    # ── Import documenti ────────────────────────────────────────────────────────
    documents = _parse_pickle()
    doc_count = 0
    for doc in documents:
        con.execute("""
            INSERT INTO documents (id, titolo, autore, data_pub, sintesi,
                                   struttura, fonti, fonti_index, topic, pdf_path)
            VALUES (:id, :titolo, :autore, :data_pub, :sintesi,
                    :struttura, :fonti, :fonti_index, :topic, :pdf_path)
            ON CONFLICT(id) DO UPDATE SET
                titolo=excluded.titolo, autore=excluded.autore,
                sintesi=excluded.sintesi, struttura=excluded.struttura,
                fonti=excluded.fonti, fonti_index=excluded.fonti_index,
                pdf_path=excluded.pdf_path
        """, doc)
        doc_count += 1
    con.commit()
    logger.info(f"Documenti importati: {doc_count}")

    # ── Import posts ────────────────────────────────────────────────────────────
    posts = _parse_reports()
    post_count = 0
    existing_keys = set(
        (r[0], r[1], r[2]) for r in
        con.execute("SELECT post_date, source_file, post_num FROM posts").fetchall()
    )
    topic_update_count = 0
    for post in posts:
        key = (post["post_date"], post["source_file"], post["post_num"])
        if key in existing_keys:
            # Aggiorna topic se era "altro" e ora abbiamo uno specifico
            if post["topic"] != "altro":
                con.execute("""
                    UPDATE posts SET topic=:topic
                    WHERE post_date=:post_date AND source_file=:source_file
                      AND post_num=:post_num AND topic='altro'
                """, post)
                topic_update_count += con.execute("SELECT changes()").fetchone()[0]
            continue
        con.execute("""
            INSERT INTO posts (doc_id, post_date, post_time, post_num,
                               focus, angolo, topic, normas, body, source_file)
            VALUES (:doc_id, :post_date, :post_time, :post_num,
                    :focus, :angolo, :topic, :normas, :body, :source_file)
        """, post)
        post_count += 1
    con.commit()
    logger.info(f"Post importati: {post_count}, topic aggiornati: {topic_update_count}")

    con.close()
    logger.info("Import completato.")


if __name__ == "__main__":
    run()
