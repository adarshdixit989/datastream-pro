from django.db import models

class Anomaly(models.Model):
    """A flagged anomalous event, produced by the streaming consumer's ML model."""
    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="anomalies")
    event_type = models.CharField(max_length=100, db_index=True)
    score = models.FloatField(help_text="Isolation Forest anomaly score (lower = more anomalous).")
    reason = models.CharField(max_length=255, blank=True, default="")
    detected_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-detected_at"]
    def __str__(self):
        return f"Anomaly<{self.event_type}> score={self.score:.3f}"

class Forecast(models.Model):
    """A per-event-type volume/value forecast produced on a rolling window."""
    event_type = models.CharField(max_length=100, db_index=True)
    predicted_value = models.FloatField()
    horizon_minutes = models.IntegerField(default=5)
    based_on_samples = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"Forecast<{self.event_type}> next={self.predicted_value:.2f}"
