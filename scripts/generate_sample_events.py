#!/usr/bin/env python
"""
Fires synthetic events at the ingestion API so you can watch the full
pipeline (API -> Kafka -> consumer -> Redis/Postgres -> ML) work end to
end without needing external/real traffic.

Usage:
    python scripts/generate_sample_events.py --count 500 --delay 0.05
"""
import argparse
import os
import random
import sys
import time

import requests

EVENT_TYPES = ["purchase", "page_view", "api_latency_ms", "signup", "login_failure"]


def random_value(event_type: str) -> float:
    base = {
        "purchase": (10, 200),
        "page_view": (1, 1),
        "api_latency_ms": (20, 300),
        "signup": (1, 1),
        "login_failure": (1, 1),
    }[event_type]

    value = random.uniform(*base)

    # Occasionally inject an outlier so the anomaly detector has something to catch.
    if random.random() < 0.03:
        value *= random.uniform(8, 20)

    return round(value, 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=200, help="Number of events to send")
    parser.add_argument("--delay", type=float, default=0.05, help="Seconds to sleep between events")
    parser.add_argument(
        "--base-url",
        default=os.getenv("API_BASE_URL", "http://localhost:8000"),
        help="Base URL of the running Django API",
    )
    args = parser.parse_args()

    url = f"{args.base_url}/api/events/"
    sent, failed = 0, 0

    for i in range(args.count):
        event_type = random.choice(EVENT_TYPES)
        payload = {
            "event_type": event_type,
            "source": "sample-generator",
            "value": random_value(event_type),
            "payload": {"seq": i},
        }
        try:
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 201:
                sent += 1
            else:
                failed += 1
                print(f"[{i}] unexpected status {resp.status_code}: {resp.text}", file=sys.stderr)
        except requests.RequestException as exc:
            failed += 1
            print(f"[{i}] request failed: {exc}", file=sys.stderr)

        if (i + 1) % 50 == 0:
            print(f"Sent {i + 1}/{args.count} events...")

        time.sleep(args.delay)

    print(f"Done. sent={sent} failed={failed}")


if __name__ == "__main__":
    main()
