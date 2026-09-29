"""
varie.py — Spunti della rubrica "Varie" della rassegna (webapp varie.html).
Lettura pubblica; spunta/stelle/commento richiedono header X-Varie-Pin = VARIE_PIN.
"""
import os
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
import aiosqlite

from web.core.db import get_db, list_varie

router = APIRouter()

_VARIE_PIN = os.environ.get("VARIE_PIN", "")


def _check_pin(x_varie_pin: str = Header("")):
    if not _VARIE_PIN:
        raise HTTPException(503, "VARIE_PIN non configurato sul server")
    if x_varie_pin != _VARIE_PIN:
        raise HTTPException(401, "PIN non valido")


class VoceUpdate(BaseModel):
    fatto:    bool | None = None
    stelle:   int | None = Field(None, ge=0, le=3)
    commento: str | None = Field(None, max_length=5000)


@router.get("/varie")
async def api_list_varie(db: aiosqlite.Connection = Depends(get_db)):
    return await list_varie(db)


@router.get("/varie/pin", dependencies=[Depends(_check_pin)])
async def api_check_pin():
    """Usato dalla pagina per verificare il PIN prima di memorizzarlo."""
    return {"status": "ok"}


@router.patch("/varie/{voce_id}", dependencies=[Depends(_check_pin)])
async def api_update_voce(
    voce_id: int,
    payload: VoceUpdate,
    db: aiosqlite.Connection = Depends(get_db),
):
    fields, params = [], []
    if payload.fatto is not None:
        fields.append("fatto = ?")
        params.append(int(payload.fatto))
    if payload.stelle is not None:
        fields.append("stelle = ?")
        params.append(payload.stelle)
    if payload.commento is not None:
        fields.append("commento = ?")
        params.append(payload.commento)
    if not fields:
        raise HTTPException(400, "Nessun campo da aggiornare")
    params.append(voce_id)
    cur = await db.execute(f"UPDATE varie SET {', '.join(fields)} WHERE id = ?", params)
    if cur.rowcount == 0:
        raise HTTPException(404, "Voce non trovata")
    await db.commit()
    return {"status": "ok", "id": voce_id}
