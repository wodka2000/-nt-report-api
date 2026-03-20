"""
db.py — SQLite schema e helpers (aiosqlite).
Il DB vive in BASE_DIR/data/web.db e non viene mai toccato dal bot.
"""
import json
import aiosqlite
from pathlib import Path
from web.core.constants import BASE_DIR

DB_PATH = BASE_DIR / "data" / "web.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id          TEXT PRIMARY KEY,
    titolo      TEXT,
    autore      TEXT,
    data_pub    TEXT,
    sintesi     TEXT,
    struttura   TEXT,        -- JSON
    fonti       TEXT,        -- JSON array
    fonti_index TEXT,        -- JSON
    topic       TEXT,
    pdf_path    TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS posts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id      TEXT REFERENCES documents(id),
    post_date   TEXT,        -- YYYY-MM-DD
    post_time   TEXT,        -- HH:MM
    post_num    INTEGER,
    focus       TEXT,
    angolo      TEXT,
    topic       TEXT,
    normas      TEXT,        -- JSON array di norme canoniche
    body        TEXT,
    source_file TEXT,
    status      TEXT DEFAULT 'active',  -- active | archived | deleted
    author      TEXT DEFAULT 'owner'    -- username Telegram
);

CREATE TABLE IF NOT EXISTS payments (
    id          TEXT PRIMARY KEY,
    action      TEXT,
    doc_id      TEXT,
    amount_usdc TEXT,
    tx_hash     TEXT,
    confirmed   INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now')),
    expires_at  TEXT
);

CREATE INDEX IF NOT EXISTS idx_posts_topic  ON posts(topic);
CREATE INDEX IF NOT EXISTS idx_posts_date   ON posts(post_date);
CREATE INDEX IF NOT EXISTS idx_posts_angolo ON posts(angolo);
"""


async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.execute("PRAGMA journal_mode=WAL")  # letture concorrenti durante scritture
        # Migrazioni: aggiunge colonne se non esistono (DB già esistenti)
        if not await _column_exists(db, "posts", "status"):
            await db.execute("ALTER TABLE posts ADD COLUMN status TEXT DEFAULT 'active'")
        if not await _column_exists(db, "posts", "author"):
            await db.execute("ALTER TABLE posts ADD COLUMN author TEXT DEFAULT 'owner'")
        await db.commit()


async def _column_exists(db: aiosqlite.Connection, table: str, column: str) -> bool:
    async with db.execute(f"PRAGMA table_info({table})") as cur:
        rows = await cur.fetchall()
    return any(row[1] == column for row in rows)


async def get_db() -> aiosqlite.Connection:
    """Dependency FastAPI: restituisce una connessione con row_factory."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


# ── Helpers posts ───────────────────────────────────────────────────────────────

async def list_posts(
    db: aiosqlite.Connection,
    topic: str | None = None,
    norma: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    status: str = "active",
    author: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> list[dict]:
    clauses, params = ["p.status = ?"], [status]
    if topic:
        clauses.append("p.topic = ?")
        params.append(topic)
    if norma:
        clauses.append("p.normas LIKE ?")
        params.append(f"%{norma}%")
    if date_from:
        clauses.append("p.post_date >= ?")
        params.append(date_from)
    if date_to:
        clauses.append("p.post_date <= ?")
        params.append(date_to)
    if author:
        clauses.append("p.author = ?")
        params.append(author)

    where = "WHERE " + " AND ".join(clauses)
    offset = (page - 1) * page_size
    params += [page_size, offset]

    sql = f"""
        SELECT p.*, d.titolo AS doc_titolo, d.autore AS doc_autore
        FROM posts p
        LEFT JOIN documents d ON p.doc_id = d.id
        {where}
        ORDER BY p.post_date DESC, p.post_time DESC
        LIMIT ? OFFSET ?
    """
    async with db.execute(sql, params) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_post(db: aiosqlite.Connection, post_id: int) -> dict | None:
    async with db.execute(
        "SELECT p.*, d.titolo AS doc_titolo, d.autore AS doc_autore, "
        "d.sintesi AS doc_sintesi, d.fonti AS doc_fonti "
        "FROM posts p LEFT JOIN documents d ON p.doc_id = d.id "
        "WHERE p.id = ?", (post_id,)
    ) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def count_posts(
    db: aiosqlite.Connection,
    topic: str | None = None,
    norma: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    status: str = "active",
    author: str | None = None,
) -> int:
    clauses, params = ["status = ?"], [status]
    if topic:
        clauses.append("topic = ?")
        params.append(topic)
    if norma:
        clauses.append("normas LIKE ?")
        params.append(f"%{norma}%")
    if date_from:
        clauses.append("post_date >= ?")
        params.append(date_from)
    if date_to:
        clauses.append("post_date <= ?")
        params.append(date_to)
    if author:
        clauses.append("author = ?")
        params.append(author)
    where = "WHERE " + " AND ".join(clauses)
    async with db.execute(f"SELECT COUNT(*) FROM posts {where}", params) as cur:
        row = await cur.fetchone()
    return row[0] if row else 0


# ── Helpers documents ───────────────────────────────────────────────────────────

async def upsert_document(db: aiosqlite.Connection, doc: dict) -> None:
    await db.execute("""
        INSERT INTO documents (id, titolo, autore, data_pub, sintesi,
                               struttura, fonti, fonti_index, topic, pdf_path)
        VALUES (:id, :titolo, :autore, :data_pub, :sintesi,
                :struttura, :fonti, :fonti_index, :topic, :pdf_path)
        ON CONFLICT(id) DO UPDATE SET
            titolo=excluded.titolo, autore=excluded.autore,
            data_pub=excluded.data_pub, sintesi=excluded.sintesi,
            struttura=excluded.struttura, fonti=excluded.fonti,
            fonti_index=excluded.fonti_index, topic=excluded.topic,
            pdf_path=excluded.pdf_path
    """, doc)


async def get_document(db: aiosqlite.Connection, doc_id: str) -> dict | None:
    async with db.execute(
        "SELECT * FROM documents WHERE id = ?", (doc_id,)
    ) as cur:
        row = await cur.fetchone()
    if not row:
        return None
    d = dict(row)
    for field in ("struttura", "fonti", "fonti_index"):
        if d.get(field):
            try:
                d[field] = json.loads(d[field])
            except Exception:
                pass
    return d


async def list_authors(db: aiosqlite.Connection) -> list[str]:
    """Lista degli autori distinti con almeno un post attivo."""
    async with db.execute(
        "SELECT DISTINCT author FROM posts WHERE status = 'active' AND author IS NOT NULL ORDER BY author"
    ) as cur:
        rows = await cur.fetchall()
    return [r[0] for r in rows]


async def insert_post(db: aiosqlite.Connection, post: dict) -> int:
    async with db.execute("""
        INSERT INTO posts (doc_id, post_date, post_time, post_num,
                           focus, angolo, topic, normas, body, source_file)
        VALUES (:doc_id, :post_date, :post_time, :post_num,
                :focus, :angolo, :topic, :normas, :body, :source_file)
    """, post) as cur:
        return cur.lastrowid
