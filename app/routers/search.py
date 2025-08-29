from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
import os

from loguru import logger

from ..es_client import get_es
from ..schemas import BookSearchItem, SearchPage

router = APIRouter(prefix="/search", tags=["search"])

BOOKS_INDEX = os.getenv("BOOKS_INDEX", "books")
REVIEWS_INDEX = os.getenv("REVIEWS_INDEX", "reviews")


@router.get("/", response_model=SearchPage)
def search_books(
    query_main: Optional[str] = Query(
        None, escription="Повнотекстовий запит по title/author/genres"
    ),
    genre: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(0, ge=0, le=5),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):

    es = get_es()
    from_ = (page - 1) * size

    must: List[Dict[str, Any]] = []
    filters: List[Dict[str, Any]] = []

    if query_main:
        must.append(
            {
                "multi_match": {
                    "query": query_main,
                    "fields": [
                        "title^3",
                        "author^2",
                        "genres",
                        "title.raw",
                        "author.raw",
                    ],
                }
            }
        )
    if genre:
        filters.append({"term": {"genres": genre}})
    if year:
        filters.append({"term": {"year": year}})

    query = (
        {"bool": {"must": must, "filter": filters}}
        if (must or filters)
        else {"match_all": {}}
    )

    sort_clause = None if query_main else [{"created_at": {"order": "desc"}}]
    logger.info(f"search 43 sort_clause: {sort_clause}")
    res = es.search(
        index=BOOKS_INDEX,
        from_=from_,
        size=size,
        query=query,
        sort=sort_clause,
    )
    hits = res.get("hits", {})
    total = hits.get("total", {}).get("value", 0)
    items = [h["_source"] for h in hits.get("hits", [])]
    logger.info(f"search 56 items: {items}")
    logger.info(f"search 57 min_rating: {min_rating}")
    if min_rating is None or not items:
        return SearchPage(
            total=total,
            page=page,
            size=size,
            items=[BookSearchItem(**it) for it in items],
        )

    ids = [it["id"] for it in items]
    logger.info(f"search 67 ids: {ids}")
    rev = es.search(
        index=REVIEWS_INDEX,
        size=0,
        query={"terms": {"book_id": ids}},
        aggs={
            "by_book": {
                "terms": {"field": "book_id", "size": len(ids)},
                "aggs": {"avg_rating": {"avg": {"field": "rating"}}},
            }
        },
    )
    logger.info(f"search 78 rev: {rev}")
    buckets = {
        b["key"]: b["avg_rating"]["value"]
        for b in rev["aggregations"]["by_book"]["buckets"]
    }
    logger.info(f"search 80 buckets: {buckets}")

    enriched = []
    for it in items:
        avg = buckets.get(it["id"])
        logger.info(f"search 85 avg: {avg}")
        it2 = {**it, "avg_rating": avg}
        if (avg or 0) >= min_rating:
            enriched.append(it2)

    logger.info(f"search 90 enriched: {enriched}")
    return SearchPage(
        total=total,
        page=page,
        size=size,
        items=[BookSearchItem(**it) for it in enriched],
    )
