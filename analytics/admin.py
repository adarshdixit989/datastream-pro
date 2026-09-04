from django.contrib import admin
from .models import Anomaly, Forecast

@admin.register(Anomaly)
class AnomalyAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "score", "detected_at")
    list_filter = ("event_type",)

@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "predicted_value", "based_on_samples", "created_at")
    list_filter = ("event_type",)
