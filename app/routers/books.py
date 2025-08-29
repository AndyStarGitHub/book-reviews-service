from fastapi import APIRouter, HTTPException
import os
from uuid import uuid4

from fastapi.params import Query
from loguru import logger

from ..es_client import get_es
from ..schemas import BookCreate, BookRead, BooksPage, ReviewAddFromBook, ReviewRead, ReviewsPage, BookReadLong
from ..utils import gen_id, now_iso

router = APIRouter(prefix="/books", tags=["books"])

BOOKS_INDEX = os.getenv("BOOKS_INDEX", "books")
REVIEWS_INDEX = os.getenv("REVIEWS_INDEX", "books")


@router.post("/", response_model=dict)
def add_book(payload: BookCreate):
    es = get_es()
    book_id = gen_id()
    doc = {
        "id": book_id,
        **payload.model_dump(),
        "created_at": now_iso(),
    }
    es.index(index=BOOKS_INDEX, id=book_id, document=doc, refresh=True)
    return {"id": book_id}

@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: str):
    es = get_es()
    book = es.get(index=BOOKS_INDEX, id=book_id, ignore=[404])
    if not book or not book.get("found"):
        raise HTTPException(status_code=404, detail="Book not found")
    source = book["_source"]
    return BookRead(**source)

@router.get("/", response_model=BooksPage)
def list_books(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort: str = Query("-created_at", description="Поле сортування: 'created_at' або '-created_at'")
):
    es = get_es()
    from_ = (page - 1) * size

    sort_clause = [{"created_at": {"order": "desc"}}] if sort.startswith("-") else [{"created_at": {"order": "asc"}}]

    res = es.search(
        index=BOOKS_INDEX,
        from_=from_,
        size=size,
        query={"match_all": {}},
        sort=sort_clause,
    )
    hits = res.get("hits", {})
    total = hits.get("total", {}).get("value", 0)
    items = [BookRead(**h["_source"]) for h in hits.get("hits", [])]

    return BooksPage(total=total, page=page, size=size, items=items)

@router.post("/{book_id}/reviews/", response_model=dict)
def add_review(book_id: str, payload: ReviewAddFromBook):
    es = get_es()
    logger.info(f"66 book_id: {book_id}")
    try:
        book = es.get(index=BOOKS_INDEX, id=book_id)
        if not book.get("found"):
            raise HTTPException(status_code=404, detail="The book not found")
    except Exception:
        raise HTTPException(status_code=404, detail="This book not found")

    review_id = str(uuid4())
    doc = {
        "id": review_id,
        "book_id": book_id,
        "rating": payload.rating,
        "text": payload.text,
        "created_at": now_iso(),
    }
    es.index(index=REVIEWS_INDEX, id=review_id, document=doc, refresh="wait_for")
    return {"id": review_id}

@router.get("/{book_id}/reviews/{review_id}", response_model=ReviewRead)
def get_review(book_id: str, review_id: str):
    es = get_es()
    review = es.get(index=REVIEWS_INDEX, id=review_id, ignore=[404])
    if not review or not review.get("found"):
        raise HTTPException(status_code=404, detail="Review not found")
    src = review["_source"]
    if src["book_id"] != book_id:
        raise HTTPException(status_code=400, detail="Review does not belong to this book")
    return ReviewRead(**src)

@router.get("/{book_id}/reviews/", response_model=ReviewsPage)
def list_reviews(
    book_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    es = get_es()
    from_ = (page - 1) * size
    res = es.search(
        index=REVIEWS_INDEX,
        from_=from_,
        size=size,
        query={"term": {"book_id": book_id}},
        sort=[{"created_at": {"order": "desc"}}],
    )
    hits = res.get("hits", {})
    total = hits.get("total", {}).get("value", 0)
    items = [ReviewRead(**h["_source"]) for h in hits.get("hits", [])]

    return ReviewsPage(total=total, page=page, size=size, items=items)

@router.get("/plus-reviews/{book_id}", response_model=BookReadLong)
def get_book_plus_reviews(book_id: str):
    logger.info(f"110 book_id: {book_id}")
    es = get_es()

    book = es.get(index=BOOKS_INDEX, id=book_id, ignore=[404])
    logger.info(f"115 book: {book}")
    if not book or not book.get("found"):
        raise HTTPException(status_code=404, detail="Book not found")
    src = book["_source"]
    logger.info(f"119 src: {src}")

    agg = es.search(
        index=REVIEWS_INDEX,
        size=0,
        query={"term": {"book_id": book_id}},
        aggs={"avg_rating": {"avg": {"field": "rating"}}},
    )
    avg = agg.get("aggregations", {}).get("avg_rating", {}).get("value")
    logger.info(f"128 avg: {avg}")

    rev = es.search(
        index=REVIEWS_INDEX,
        size=100,  # no pagination so far
        query={"term": {"book_id": book_id}},
        sort=[{"created_at": {"order": "desc"}}],
    )
    reviews = [ReviewRead(**h["_source"]) for h in rev.get("hits", {}).get("hits", [])]
    logger.info(f"137 reviews: {reviews}")

    return BookReadLong(**src, avg_rating=avg, reviews=reviews)
