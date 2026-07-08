# Deployment Guide

## Localhost
- Copy .env.example to .env.
- Run scripts/bootstrap.ps1.
- Start API with python run.py.

## Docker
- Build image: docker build -t bia-app .
- Start stack: docker compose up --build
- Validate health: GET /system/health

## Cloud Targets
## Render
- Use Docker deployment.
- Set environment variables from .env.
- Expose port 8000.

## Railway
- Deploy from Dockerfile.
- Add PostgreSQL, Redis, RabbitMQ plugins.

## AWS
- ECS Fargate for app + worker.
- RDS PostgreSQL for persistence.
- ElastiCache Redis + MQ service.

## Security Requirements
- Set APP_ENV=production.
- Set API_KEY and SECRET_KEY.
- Configure CORS ALLOWED_ORIGINS.
- Use HTTPS and reverse proxy.
