import redis
from django.conf import settings

_client = None

def get_redis():
    global _client
    if not settings.REDIS_HOST:
        return None
    if _client is None:
        _client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    return _client

def _db_stats(event_type: str) -> dict:
    from events.models import Event
    from django.utils import timezone
    from datetime import timedelta
    qs = Event.objects.filter(event_type=event_type)
    count = qs.count()
    total = float(sum((e.value for e in qs), 0.0))
    cutoff = timezone.now() - timedelta(minutes=5)
    recent = qs.filter(created_at__gte=cutoff).count()
    return {
        "event_type": event_type,
        "count": count,
        "sum": total,
        "avg": total / count if count else 0.0,
        "events_last_5m": recent,
        "events_per_min": recent / 5 if recent else 0,
    }

def bump_counters(event_type: str, value: float):
    r = get_redis()
    if r is None:
        return
    try:
        pipe = r.pipeline()
        pipe.incr(f"stats:{event_type}:count")
        pipe.incrbyfloat(f"stats:{event_type}:sum", value)
        from django.utils import timezone
        minute_bucket = timezone.now().strftime("%Y-%m-%d %H:%M")
        key = f"stats:{event_type}:minute:{minute_bucket}"
        pipe.incr(key)
        pipe.expire(key, 3600)
        pipe.execute()
    except redis.RedisError:
        return

def get_stats(event_type: str) -> dict:
    r = get_redis()
    if r is None:
        return _db_stats(event_type)
    try:
        count = int(r.get(f"stats:{event_type}:count") or 0)
        total = float(r.get(f"stats:{event_type}:sum") or 0.0)
        avg = total / count if count else 0.0
        from datetime import datetime, timedelta
        now = datetime.now()
        rate = sum(int(r.get(f"stats:{event_type}:minute:{(now - timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M')}") or 0) for i in range(5))
        return {"event_type": event_type, "count": count, "sum": total, "avg": avg, "events_last_5m": rate, "events_per_min": rate / 5 if rate else 0}
    except redis.RedisError:
        return _db_stats(event_type)

def get_all_known_event_types() -> set:
    r = get_redis()
    if r is None:
        from events.models import Event
        return set(Event.objects.values_list("event_type", flat=True).distinct())
    try:
        return {k.split(":")[1] for k in r.keys("stats:*:count")}
    except redis.RedisError:
        from events.models import Event
        return set(Event.objects.values_list("event_type", flat=True).distinct())
