from fastapi import APIRouter, HTTPException
import os

from fastapi.params import Query
from loguru import logger

from ..es_client import get_es
from ..schemas import ReviewCreate, ReviewRead, ReviewsPage
from ..utils import gen_id, now_iso

router = APIRouter(prefix="/reviews", tags=["reviews"])

BOOKS_INDEX = os.getenv("BOOKS_INDEX", "books")
REVIEWS_INDEX = os.getenv("REVIEWS_INDEX", "reviews")


@router.post("/", response_model=dict)
def add_review(payload: ReviewCreate):
    es = get_es()

    try:
        book = es.get(index=BOOKS_INDEX, id=payload.book_id)
        if not book.get("found"):
            raise HTTPException(status_code=404, detail="Book not found")
    except Exception:
        raise HTTPException(status_code=404, detail="Book not found")

    review_id = gen_id()
    doc = {
        "id": review_id,
        **payload.model_dump(),
        "created_at": now_iso(),
    }
    es.index(index=REVIEWS_INDEX, id=review_id, document=doc, refresh=True)
    return {"id": review_id}


@router.get("/{review_id}", response_model=ReviewRead)
def get_review(review_id: str):
    logger.info(f"32 review_id: {review_id}")
    es = get_es()
    logger.info(f"35 es: {es}")
    review = es.get(index=REVIEWS_INDEX, id=review_id, ignore=[404])
    if not review or not review.get("found"):
        raise HTTPException(status_code=404, detail="Review not found")
    source = review["_source"]
    return ReviewRead(**source)


@router.get("/", response_model=ReviewsPage)
def list_reviews(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort: str = Query(
        "-created_at", description="Поле сортування: 'created_at' або '-created_at'"
    ),
):
    es = get_es()
    from_ = (page - 1) * size

    sort_clause = (
        [{"created_at": {"order": "desc"}}]
        if sort.startswith("-")
        else [{"created_at": {"order": "asc"}}]
    )

    res = es.search(
        index=REVIEWS_INDEX,
        from_=from_,
        size=size,
        query={"match_all": {}},
        sort=sort_clause,
    )
    hits = res.get("hits", {})
    total = hits.get("total", {}).get("value", 0)
    items = [ReviewRead(**h["_source"]) for h in hits.get("hits", [])]

    return ReviewsPage(total=total, page=page, size=size, items=items)
