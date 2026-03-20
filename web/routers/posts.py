from fastapi import APIRouter, Depends, Query, BackgroundTasks
from web.core.db import get_db, list_posts, get_post, count_posts, list_authors
from web.core.constants import TOPICS, _NORMA_ALIASES
import aiosqlite

router = APIRouter()


@router.post("/refresh")
async def api_refresh(background_tasks: BackgroundTasks):
    """Reimporta i report dal filesystem. Chiamato dal bot dopo ogni push."""
    import asyncio
    from web.scripts.import_reports import run as import_run
    async def _run_in_thread():
        await asyncio.get_event_loop().run_in_executor(None, import_run)
    background_tasks.add_task(_run_in_thread)
    return {"status": "import avviato"}


@router.get("/topics")
async def get_topics():
    return TOPICS


@router.get("/normas")
async def get_normas():
    return [{"canonical": c, "aliases": a} for c, a in _NORMA_ALIASES]


@router.get("/authors")
async def api_list_authors(db: aiosqlite.Connection = Depends(get_db)):
    """Lista degli autori con almeno un post attivo."""
    return await list_authors(db)


@router.get("/posts")
async def api_list_posts(
    topic:     str | None = Query(None),
    norma:     str | None = Query(None),
    date_from: str | None = Query(None),
    date_to:   str | None = Query(None),
    status:    str        = Query("active", pattern="^(active|archived)$"),
    author:    str | None = Query(None),
    page:      int        = Query(1, ge=1),
    page_size: int        = Query(20, ge=1, le=100),
    db: aiosqlite.Connection = Depends(get_db),
):
    posts = await list_posts(db, topic=topic, norma=norma,
                             date_from=date_from, date_to=date_to,
                             status=status, author=author, page=page, page_size=page_size)
    total = await count_posts(db, topic=topic, norma=norma, date_from=date_from, date_to=date_to,
                              status=status, author=author)
    return {
        "total":     total,
        "page":      page,
        "page_size": page_size,
        "pages":     max(1, -(-total // page_size)),
        "items":     posts,
    }


@router.get("/posts/{post_id}")
async def api_get_post(
    post_id: int,
    db: aiosqlite.Connection = Depends(get_db),
):
    post = await get_post(db, post_id)
    if not post:
        from fastapi import HTTPException
        raise HTTPException(404, "Post non trovato")
    return post
