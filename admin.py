from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "source", "value", "created_at", "published_to_kafka")
    list_filter = ("event_type", "source", "published_to_kafka")
    search_fields = ("event_type", "source")
