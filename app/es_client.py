import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "http://localhost:9200")

_es: Elasticsearch | None = None


def get_es() -> Elasticsearch:
    global _es
    if _es is None:
        _es = Elasticsearch(ELASTIC_HOST)
    return _es
