import redis
from django.conf import settings

_client = None


def get_redis():
    global _client
    if _client is None:
        _client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )
    return _client


def bump_counters(event_type: str, value: float):
    """
    Update real-time Redis counters for a single incoming event:
    - total event count per type
    - rolling sum (for average) per type
    - per-minute bucket count (for a live sparkline / rate)
    """
    r = get_redis()
    pipe = r.pipeline()
    pipe.incr(f"stats:{event_type}:count")
    pipe.incrbyfloat(f"stats:{event_type}:sum", value)

    from django.utils import timezone

    minute_bucket = timezone.now().strftime("%Y-%m-%d %H:%M")
    key = f"stats:{event_type}:minute:{minute_bucket}"
    pipe.incr(key)
    pipe.expire(key, 3600)  # keep an hour of minute buckets
    pipe.execute()


def get_stats(event_type: str) -> dict:
    r = get_redis()
    count = int(r.get(f"stats:{event_type}:count") or 0)
    total = float(r.get(f"stats:{event_type}:sum") or 0.0)
    avg = total / count if count else 0.0
    from datetime import datetime, timedelta
    now = datetime.now()
    rate = 0
    for i in range(5):
        bucket = (now - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M")
        rate += int(r.get(f"stats:{event_type}:minute:{bucket}") or 0)
    return {"event_type": event_type, "count": count, "sum": total, "avg": avg, "events_last_5m": rate, "events_per_min": rate / 5 if rate else 0}


def get_all_known_event_types() -> set:
    r = get_redis()
    keys = r.keys("stats:*:count")
    return {k.split(":")[1] for k in keys}
