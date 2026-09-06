from django.apps import AppConfig

class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "events"

    def ready(self):
        # The Render demo service intentionally supports a no-database mode.
        # Create only the application's required table when SQLite is active.
        from django.conf import settings
        if settings.DATABASES["default"]["ENGINE"] != "django.db.backends.sqlite3":
            return
        try:
            from django.db import connection
            from .models import Event
            if Event._meta.db_table not in connection.introspection.table_names():
                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(Event)
        except Exception:
            # A concurrent worker may have created it; the next request will work.
            pass
