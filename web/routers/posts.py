from fastapi import APIRouter, Depends, Query
from web.core.db import get_db, list_posts, get_post, count_posts
from web.core.constants import TOPICS, _NORMA_ALIASES
import aiosqlite

router = APIRouter()


@router.get("/topics")
async def get_topics():
    return TOPICS


@router.get("/normas")
async def get_normas():
    return [{"canonical": c, "aliases": a} for c, a in _NORMA_ALIASES]


@router.get("/posts")
async def api_list_posts(
    topic:     str | None = Query(None),
    norma:     str | None = Query(None),
    date_from: str | None = Query(None),
    date_to:   str | None = Query(None),
    page:      int        = Query(1, ge=1),
    page_size: int        = Query(20, ge=1, le=100),
    db: aiosqlite.Connection = Depends(get_db),
):
    posts = await list_posts(db, topic=topic, norma=norma,
                             date_from=date_from, date_to=date_to,
                             page=page, page_size=page_size)
    total = await count_posts(db, topic=topic, norma=norma)
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
