# AWS deployment blueprint

This directory is intentionally provider-ready rather than pretending that cloud resources already exist. It provides a repeatable path for deploying DataStream Pro to AWS after adding your account-specific secrets and variables.

Recommended production layout:
- EC2/ECS: web + stream consumer containers
- ElastiCache Redis: real-time counters
- Amazon RDS PostgreSQL: durable data
- MSK (optional): managed Kafka instead of the bundled local Kafka/Zookeeper
- S3: event/model/archive storage
- Lambda + EventBridge: scheduled model/report jobs
- ECR: container images
- GitHub Actions: CI/CD

The local docker-compose stack remains the canonical development environment.
