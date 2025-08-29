from pathlib import Path

from fastapi import FastAPI
from loguru import logger

from .es_client import get_es
from app.index_migrations import ensure_indices
from .routers import books, reviews, search, analytics

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logger.add(LOG_DIR / "main.log")

app = FastAPI(title="Book Reviews Service")

@app.on_event("startup")
def on_startup():
    es = get_es()

    try:
        ensure_indices(es)
    except Exception as e:
        print(f"[WARN] ensure_indices failed: {e}")

app.include_router(books.router)
app.include_router(reviews.router)
app.include_router(search.router)
app.include_router(analytics.router)

@app.get("/")
async def root():
    return {"message": "Book Reviews Service Root"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}