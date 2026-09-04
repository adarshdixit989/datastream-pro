# DataStream Pro — Enterprise Real-Time Analytics Platform

Enterprise-style real-time analytics platform built with Python, Django REST Framework, Apache Kafka, Redis, PostgreSQL, React, TypeScript, Scikit-learn and Docker.

## Features
- Kafka event streaming and ingestion
- Redis real-time counters and rate metrics
- PostgreSQL durable event storage
- Isolation Forest anomaly detection
- Rolling Linear Regression forecasting
- React + TypeScript analytics dashboard
- Docker Compose local development stack
- GitHub Actions CI/CD
- AWS deployment blueprint for EC2/ECS, RDS, ElastiCache, S3, ECR and Lambda

## Run locally
1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. API: `http://localhost:8000`
4. Dashboard: `http://localhost:5173`

Performance and reliability figures should be reported only after running the included benchmark/load-test workflow.
