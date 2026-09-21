from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import aiosqlite

from web.core.db import get_db, list_rassegne, get_rassegna
from web.core.constants import RASSEGNE_DIR

router = APIRouter()


@router.get("/rassegne")
async def api_list_rassegne(db: aiosqlite.Connection = Depends(get_db)):
    """Elenco pubblico delle rassegne disponibili (versione senza la pagina con la
    ToDo list privata — quella resta solo nella copia stampata/su Drive)."""
    return await list_rassegne(db)


@router.get("/rassegne/{data}/pdf")
async def api_get_rassegna_pdf(data: str, db: aiosqlite.Connection = Depends(get_db)):
    row = await get_rassegna(db, data)
    if not row:
        raise HTTPException(404, "Rassegna non trovata")
    path = RASSEGNE_DIR / row["pdf_path"]
    if not path.exists():
        raise HTTPException(404, "File PDF non trovato sul disco")
    return FileResponse(str(path), media_type="application/pdf", filename=f"rassegna-{data}.pdf")
