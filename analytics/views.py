from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Anomaly, Forecast
from .serializers import AnomalySerializer, ForecastSerializer
from .redis_client import get_stats, get_all_known_event_types

class AnomalyViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Anomaly.objects.select_related("event").all()
    serializer_class = AnomalySerializer
    def get_queryset(self):
        qs = super().get_queryset()
        event_type = self.request.query_params.get("event_type")
        if event_type:
            qs = qs.filter(event_type=event_type)
        return qs

class ForecastViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Forecast.objects.all()
    serializer_class = ForecastSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        event_type = self.request.query_params.get("event_type")
        if event_type:
            qs = qs.filter(event_type=event_type)[:1]
        return qs[:20]

class StatsView(APIView):
    def get(self, request):
        event_type = request.query_params.get("event_type")
        if event_type:
            return Response(get_stats(event_type))
        types = sorted(get_all_known_event_types())
        return Response({"event_types": [get_stats(t) for t in types]})
