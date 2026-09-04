from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "event_type",
            "source",
            "value",
            "payload",
            "created_at",
            "published_to_kafka",
        ]
        read_only_fields = ["id", "created_at", "published_to_kafka"]
