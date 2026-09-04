from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import AnomalyViewSet, ForecastViewSet, StatsView

router = DefaultRouter()
router.register(r"anomalies", AnomalyViewSet, basename="anomaly")
router.register(r"forecast", ForecastViewSet, basename="forecast")
urlpatterns = [path("stats/", StatsView.as_view(), name="stats")] + router.urls
