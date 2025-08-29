import os

from pprint import pprint
from dotenv import load_dotenv

from elasticsearch import Elasticsearch


load_dotenv()

BOOKS_INDEX = os.getenv("BOOKS_INDEX", "books")
REVIEWS_INDEX = os.getenv("REVIEWS_INDEX", "reviews")

BOOKS_MAPPINGS = {
    "properties": {
        "id": {"type": "keyword"},
        "title": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
        "author": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
        "year": {"type": "integer"},
        "genres": {"type": "keyword"},
        "created_at": {"type": "date"},
    }
}

REVIEWS_MAPPINGS = {
    "properties": {
        "id": {"type": "keyword"},
        "book_id": {"type": "keyword"},
        "rating": {"type": "integer"},
        "text": {"type": "text"},
        "created_at": {"type": "date"},
    }
}

SETTINGS = {
    "index": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    }
}

def ensure_indices(es: Elasticsearch) -> None:
    # books
    if not es.indices.exists(index=BOOKS_INDEX):
        es.indices.create(
            index=BOOKS_INDEX,
            settings=SETTINGS,
            mappings=BOOKS_MAPPINGS,
        )
    # reviews
    if not es.indices.exists(index=REVIEWS_INDEX):
        es.indices.create(
            index=REVIEWS_INDEX,
            settings=SETTINGS,
            mappings=REVIEWS_MAPPINGS,
        )
