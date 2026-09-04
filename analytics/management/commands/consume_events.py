"""
Long-running worker: consumes events from Kafka, updates Redis real-time
counters, runs ML anomaly detection + forecasting per event, and persists
anomalies/forecasts to Postgres.

Run with:
    python manage.py consume_events

This is the process that would run in the `consumer` container in
docker-compose (see docker-compose.yml).
"""
import json
import logging
import time

from django.core.management.base import BaseCommand
from django.conf import settings

from events.models import Event
from analytics.models import Anomaly, Forecast
from analytics.redis_client import bump_counters
from analytics.ml.anomaly_detector import detector
from analytics.ml.forecaster import forecaster

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Consume streaming events from Kafka and run real-time analytics (anomaly detection + forecasting)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--forecast-every",
            type=int,
            default=25,
            help="Persist a Forecast row every N processed events per event_type.",
        )

    def handle(self, *args, **options):
        forecast_every = options["forecast_every"]
        events_since_forecast: dict[str, int] = {}

        self.stdout.write(self.style.SUCCESS(f"Connecting to Kafka broker at {settings.KAFKA_BROKER} ..."))

        consumer = self._connect_with_retry()

        self.stdout.write(self.style.SUCCESS(f"Subscribed to topic '{settings.KAFKA_TOPIC}'. Waiting for events..."))

        for message in consumer:
            try:
                self._process_message(message.value, events_since_forecast, forecast_every)
            except Exception as exc:  # noqa: BLE001 - never let one bad message kill the worker
                logger.exception("Failed to process message: %s", exc)

    def _connect_with_retry(self, max_retries=10, delay_seconds=5):
        from kafka import KafkaConsumer
        from kafka.errors import NoBrokersAvailable

        for attempt in range(1, max_retries + 1):
            try:
                return KafkaConsumer(
                    settings.KAFKA_TOPIC,
                    bootstrap_servers=settings.KAFKA_BROKER,
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                    auto_offset_reset="latest",
                    enable_auto_commit=True,
                    group_id="datastream-pro-consumer",
                )
            except NoBrokersAvailable:
                self.stdout.write(
                    self.style.WARNING(
                        f"Kafka not reachable yet (attempt {attempt}/{max_retries}). Retrying in {delay_seconds}s..."
                    )
                )
                time.sleep(delay_seconds)
        raise RuntimeError("Could not connect to Kafka after retries.")

    def _process_message(self, data: dict, events_since_forecast: dict, forecast_every: int):
        event_type = data["event_type"]
        value = float(data["value"])
        event_id = data.get("id")

        # 1. Real-time counters
        bump_counters(event_type, value)

        # 2. Anomaly detection
        is_anomaly, score = detector.score(event_type, value)
        if is_anomaly and event_id:
            try:
                event_obj = Event.objects.get(id=event_id)
                Anomaly.objects.create(
                    event=event_obj,
                    event_type=event_type,
                    score=score,
                    reason=f"value={value} flagged by IsolationForest (score={score:.4f})",
                )
                self.stdout.write(self.style.ERROR(f"[ANOMALY] {event_type} value={value} score={score:.4f}"))
            except Event.DoesNotExist:
                logger.warning("Event id %s not found when persisting anomaly", event_id)

        # 3. Forecasting (persisted periodically, not on every single event)
        prediction = forecaster.add_and_forecast(event_type, value)
        events_since_forecast[event_type] = events_since_forecast.get(event_type, 0) + 1
        if prediction is not None and events_since_forecast[event_type] >= forecast_every:
            Forecast.objects.create(
                event_type=event_type,
                predicted_value=prediction,
                based_on_samples=forecaster.sample_count(event_type),
            )
            events_since_forecast[event_type] = 0
            self.stdout.write(self.style.SUCCESS(f"[FORECAST] {event_type} next~={prediction:.2f}"))
