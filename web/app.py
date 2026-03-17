"""
app.py — FastAPI entrypoint per NT Report Web.
Avvio: uvicorn web.app:app --reload --port 8080
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from web.core.db import init_db
from web.routers import posts

_STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Import automatico dei report se il DB è vuoto
    import aiosqlite
    from web.core.db import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM posts") as cur:
            count = (await cur.fetchone())[0]
    if count == 0:
        import logging
        logging.getLogger(__name__).info("DB vuoto — eseguo import_reports")
        from web.scripts.import_reports import run as import_run
        import asyncio
        await asyncio.get_event_loop().run_in_executor(None, import_run)
    yield


app = FastAPI(title="NT Report Web", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router, prefix="/api")

# Static files — deve stare dopo i router per non intercettare /api/*
if _STATIC.exists():
    app.mount("/", StaticFiles(directory=str(_STATIC), html=True), name="static")
