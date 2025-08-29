from datetime import datetime, timezone
from uuid import uuid4


def gen_id() -> str:
    return str(uuid4())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
