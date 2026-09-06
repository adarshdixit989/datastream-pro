from django.apps import AppConfig

class AnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "analytics"

    def ready(self):
        from django.conf import settings
        if settings.DATABASES["default"]["ENGINE"] != "django.db.backends.sqlite3":
            return
        try:
            from django.db import connection
            from .models import Anomaly, Forecast
            tables = set(connection.introspection.table_names())
            with connection.schema_editor() as schema_editor:
                if Anomaly._meta.db_table not in tables:
                    schema_editor.create_model(Anomaly)
                if Forecast._meta.db_table not in tables:
                    schema_editor.create_model(Forecast)
        except Exception:
            pass
