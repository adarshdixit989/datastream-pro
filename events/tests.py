from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Event


class EventAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("events.views.publish_event", return_value=True)
    def test_create_event(self, mock_publish):
        response = self.client.post(
            "/api/events/",
            {"event_type": "purchase", "source": "test", "value": 42.5, "payload": {}},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()
        self.assertEqual(event.event_type, "purchase")
        self.assertTrue(event.published_to_kafka)
        mock_publish.assert_called_once()

    @patch("events.views.publish_event", return_value=True)
    def test_list_events_filters_by_type(self, mock_publish):
        Event.objects.create(event_type="purchase", source="t", value=1)
        Event.objects.create(event_type="page_view", source="t", value=1)

        response = self.client.get("/api/events/", {"event_type": "purchase"})
        self.assertEqual(response.status_code, 200)
        results = response.data["results"] if "results" in response.data else response.data
        self.assertTrue(all(item["event_type"] == "purchase" for item in results))

    @patch("events.views.publish_event", return_value=True)
    def test_bulk_ingest(self, mock_publish):
        payload = [
            {"event_type": "signup", "source": "t", "value": 1},
            {"event_type": "signup", "source": "t", "value": 1},
        ]
        response = self.client.post("/api/events/bulk/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["ingested"], 2)
        self.assertEqual(Event.objects.count(), 2)
