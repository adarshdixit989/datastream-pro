"""
Thin wrapper around kafka-python's KafkaProducer.

The producer is created lazily and cached at module level so we don't
reconnect to the broker on every request. If Kafka is unreachable (e.g.
running the API without the full docker-compose stack), publishing fails
soft: the event is still persisted to Postgres and the API call succeeds,
so local development / demos don't hard-depend on a live broker.
"""
import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

_producer = None


def get_producer():
    global _producer
    if _producer is None:
        from kafka import KafkaProducer

        _producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            retries=3,
            linger_ms=20,
        )
    return _producer


def publish_event(event) -> bool:
    """
    Publish a single events.models.Event instance to the configured Kafka
    topic. Returns True on success, False if publishing failed (logged,
    never raised, so the ingestion API stays available even if Kafka is
    briefly unavailable).
    """
    message = {
        "id": event.id,
        "event_type": event.event_type,
        "source": event.source,
        "value": event.value,
        "payload": event.payload,
        "created_at": event.created_at.isoformat(),
    }
    try:
        producer = get_producer()
        producer.send(settings.KAFKA_TOPIC, key=event.event_type, value=message)
        producer.flush(timeout=5)
        return True
    except Exception as exc:  # noqa: BLE001 - broad on purpose, this must never crash ingestion
        logger.warning("Failed to publish event %s to Kafka: %s", event.id, exc)
        return False
