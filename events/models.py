from django.db import models


class Event(models.Model):
    """
    A raw streaming event ingested through the API and published to Kafka.
    Persisted here for durability / replay in addition to being streamed.
    """

    event_type = models.CharField(max_length=100, db_index=True)
    source = models.CharField(max_length=100, default="unknown")
    value = models.FloatField(help_text="Primary numeric metric for this event (e.g. amount, latency, count).")
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    published_to_kafka = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} @ {self.created_at.isoformat()} = {self.value}"
