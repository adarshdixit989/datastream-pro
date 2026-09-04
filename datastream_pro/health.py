from django.conf import settings
from django.http import JsonResponse
from django.db import connection
import redis
from kafka import KafkaProducer

def health_check(request):
    checks={"postgresql":False,"redis":False,"kafka":False}
    try:
        with connection.cursor() as c: c.execute("SELECT 1")
        checks["postgresql"]=True
    except Exception: pass
    try:
        checks["redis"]=bool(redis.Redis(host=settings.REDIS_HOST,port=settings.REDIS_PORT).ping())
    except Exception: pass
    try:
        p=KafkaProducer(bootstrap_servers=settings.KAFKA_BROKER,request_timeout_ms=1500); p.close(); checks["kafka"]=True
    except Exception: pass
    ok=all(checks.values())
    return JsonResponse({"status":"ok" if ok else "degraded","service":"datastream-pro","checks":checks},status=200 if ok else 503)
