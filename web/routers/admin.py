"""
admin.py — Endpoint protetti per modifica/archiviazione/cancellazione post.
Richiedono header: X-Admin-Token: {ADMIN_TOKEN}
"""
import os
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
import aiosqlite

from web.core.db import get_db

router = APIRouter(prefix="/api/admin")

_ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")


def _check_auth(x_admin_token: str = Header(...)):
    if not _ADMIN_TOKEN:
        raise HTTPException(503, "ADMIN_TOKEN non configurato sul server")
    if x_admin_token != _ADMIN_TOKEN:
        raise HTTPException(401, "Token non valido")


class PostUpdate(BaseModel):
    topic: str | None = None
    body:  str | None = None


@router.patch("/posts/{post_id}", dependencies=[Depends(_check_auth)])
async def admin_update_post(
    post_id: int,
    payload: PostUpdate,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Modifica topic e/o body di un post."""
    fields, params = [], []
    if payload.topic is not None:
        fields.append("topic = ?")
        params.append(payload.topic)
    if payload.body is not None:
        fields.append("body = ?")
        params.append(payload.body)
    if not fields:
        raise HTTPException(400, "Nessun campo da aggiornare")
    params.append(post_id)
    await db.execute(f"UPDATE posts SET {', '.join(fields)} WHERE id = ?", params)
    await db.commit()
    return {"status": "ok", "id": post_id}


@router.post("/posts/{post_id}/archive", dependencies=[Depends(_check_auth)])
async def admin_archive_post(
    post_id: int,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Sposta un post in archivio (status = 'archived')."""
    await db.execute("UPDATE posts SET status = 'archived' WHERE id = ?", (post_id,))
    await db.commit()
    return {"status": "ok", "id": post_id}


@router.post("/posts/{post_id}/restore", dependencies=[Depends(_check_auth)])
async def admin_restore_post(
    post_id: int,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Riporta un post ad active."""
    await db.execute("UPDATE posts SET status = 'active' WHERE id = ?", (post_id,))
    await db.commit()
    return {"status": "ok", "id": post_id}


@router.delete("/posts/{post_id}", dependencies=[Depends(_check_auth)])
async def admin_delete_post(
    post_id: int,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Soft delete: nasconde il post ovunque (status = 'deleted')."""
    await db.execute("UPDATE posts SET status = 'deleted' WHERE id = ?", (post_id,))
    await db.commit()
    return {"status": "ok", "id": post_id}


@router.get("/posts", dependencies=[Depends(_check_auth)])
async def admin_list_all_posts(
    db: aiosqlite.Connection = Depends(get_db),
):
    """Lista tutti i post (active + archived + deleted) per il pannello admin."""
    async with db.execute(
        "SELECT id, post_date, post_time, focus, topic, status, source_file "
        "FROM posts ORDER BY post_date DESC, post_time DESC"
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]
