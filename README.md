# DataStream Pro — Enterprise Real-Time Analytics Platform

DataStream Pro is a production-style reference platform for high-throughput event ingestion, streaming analytics, ML anomaly detection, forecasting, and operational monitoring.

## Stack

**Backend:** Python 3.11, Django 5, Django REST Framework, PostgreSQL 16, Redis 7, Apache Kafka 7.6, Scikit-learn  
**Platform:** Docker Compose, Gunicorn, GitHub Actions, AWS-ready deployment blueprint (EC2/ECS, S3, Lambda, ECR)  
**Frontend:** React + TypeScript, Vite, Recharts, Lucide

## Architecture

```text
Clients / Load Generator
          │
          ▼
   React Dashboard ◀──────────────┐
          │ REST                  │ live polling
          ▼                       │
   Django REST API                │
          │                       │
          ├──────► PostgreSQL     │
          │                       │
          ▼                       │
       Kafka ──► Analytics Consumer
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Redis             Scikit-learn
     live metrics      anomaly + forecast
          │                   │
          └─────────┬─────────┘
                    ▼
              Analytics API
```

## Included capabilities

- REST + bulk event ingestion with Kafka decoupling
- Dedicated streaming consumer
- Redis counters and recent-rate calculations
- PostgreSQL durable event/anomaly/forecast storage
- Isolation Forest anomaly detection
- Rolling linear-regression forecasting
- Enterprise dark operations dashboard
- Pipeline health endpoint covering PostgreSQL, Redis and Kafka
- Dockerized local stack with frontend, API, consumer and data services
- GitHub Actions CI and Docker build
- AWS deployment blueprint and thin Lambda entry point
- Throughput benchmark script for evidence-based performance claims

## Run the full stack

```bash
cp .env.example .env
docker compose up --build
```

Open the dashboard at **http://localhost:3000**. API remains available at **http://localhost:8000**.

First-time database setup is performed automatically by the `web` container. To create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

Generate traffic:

```bash
docker compose exec web python scripts/generate_sample_events.py --count 500
```

Useful endpoints:

- `/api/events/`
- `/api/events/bulk/`
- `/api/analytics/stats/`
- `/api/analytics/anomalies/`
- `/api/analytics/forecast/`
- `/healthz/`
- `/admin/`

## Performance evidence

The resume figures **1M+ events/day, 30% accuracy improvement, 99.9% uptime and 40% faster releases** should only be published as measured results. This repository includes `benchmarks/load_test.py` and `docs/CLAIMS.md` to make those claims reproducible and defensible instead of hard-coding unsupported numbers.

Example throughput test:

```bash
python benchmarks/load_test.py --count 10000 --batch 500
```

## AWS path

`deploy/aws/` documents the production topology. A typical deployment uses ECR for images, EC2/ECS for web and consumer services, RDS PostgreSQL, ElastiCache Redis, MSK for managed Kafka, S3 for archives/models, and Lambda + EventBridge for scheduled lightweight jobs. Account-specific infrastructure, secrets and domain/TLS settings should be supplied before deployment.

## GitHub

```bash
git init
git add .
git commit -m "Build DataStream Pro enterprise analytics platform"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO>
git push -u origin main
```
