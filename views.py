from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer
from .kafka_producer import publish_event


class EventViewSet(viewsets.ModelViewSet):
    """
    Ingestion API for streaming events.

    POST /api/events/          -> persist + publish to Kafka
    GET  /api/events/          -> list recent events (paginated)
    GET  /api/events/{id}/     -> retrieve one event
    POST /api/events/bulk/     -> ingest a batch of events in one call
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_fields = ["event_type", "source"]

    def get_queryset(self):
        qs = super().get_queryset()
        event_type = self.request.query_params.get("event_type")
        if event_type:
            qs = qs.filter(event_type=event_type)
        return qs

    def perform_create(self, serializer):
        event = serializer.save()
        published = publish_event(event)
        if published:
            event.published_to_kafka = True
            event.save(update_fields=["published_to_kafka"])

    @action(detail=False, methods=["post"])
    def bulk(self, request):
        items = request.data if isinstance(request.data, list) else request.data.get("events", [])
        serializer = self.get_serializer(data=items, many=True)
        serializer.is_valid(raise_exception=True)
        events = serializer.save()
        for event in events:
            if publish_event(event):
                event.published_to_kafka = True
                event.save(update_fields=["published_to_kafka"])
        return Response(
            {"ingested": len(events)},
            status=status.HTTP_201_CREATED,
        )
