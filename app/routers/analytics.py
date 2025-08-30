from fastapi import APIRouter
import os
from ..es_client import get_es
from ..schemas import TopRatedBook, TopRatedResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

REVIEWS_INDEX = os.getenv("REVIEWS_INDEX", "reviews")
BOOKS_INDEX = os.getenv("BOOKS_INDEX", "books")


@router.get("/top-rated", response_model=TopRatedResponse)
def top_rated_books():
    es = get_es()

    res = es.search(
        index=REVIEWS_INDEX,
        size=0,
        aggs={
            "by_book": {
                "terms": {
                    "field": "book_id",
                    "size": 5,
                    "order": {"avg_rating": "desc"},
                },
                "aggs": {"avg_rating": {"avg": {"field": "rating"}}},
            }
        },
    )

    buckets = res["aggregations"]["by_book"]["buckets"]
    top_ids = [bucket["key"] for bucket in buckets]

    if not top_ids:
        return TopRatedResponse(top=[])

    mget = es.mget(index=BOOKS_INDEX, ids=top_ids)
    meta = {doc["_id"]: doc["_source"] for doc in mget["docs"] if doc.get("found")}

    top = []
    for bucket in buckets:
        book_id = bucket["key"]
        avg = bucket["avg_rating"]["value"]
        src = meta.get(book_id)
        top.append(
            TopRatedBook(
                book_id=book_id,
                avg_rating=avg if avg is not None else 0.0,
                title=src["title"] if src else None,
                author=src["author"] if src else None,
            )
        )

    return TopRatedResponse(top=top)
