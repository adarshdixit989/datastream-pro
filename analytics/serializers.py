from rest_framework import serializers
from .models import Anomaly, Forecast

class AnomalySerializer(serializers.ModelSerializer):
    event_value = serializers.FloatField(source="event.value", read_only=True)
    class Meta:
        model = Anomaly
        fields = ["id", "event", "event_type", "event_value", "score", "reason", "detected_at"]

class ForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        fields = ["id", "event_type", "predicted_value", "horizon_minutes", "based_on_samples", "created_at"]
