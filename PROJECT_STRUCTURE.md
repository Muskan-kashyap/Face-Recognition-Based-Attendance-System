# Project Structure

This repository now follows a production-grade microservice architecture for the Face Recognition Attendance Management Platform.

## Top-level services

- `frontend/` - React + TypeScript + Vite SPA with TailwindCSS, React Router, React Query, and Zustand.
- `backend/` - Existing FastAPI backend module and shared monolith utilities used by internal APIs.
- `gateway/` - FastAPI API gateway that routes requests to microservices and enforces CORS/security rules.
- `auth-service/` - Identity, JWT, refresh tokens, RBAC, multi-tenant organization service.
- `ai-service/` - Face registration, recognition, liveness detection, emotion analysis, and pgvector embedding service.
- `attendance-service/` - Attendance engine, check-in/out, shift validation, duplicate prevention, and manual attendance overrides.
- `blockchain-service/` - Blockchain anchoring service, Web3 verification, smart contract integration, and tamper-resistant audit storage.
- `analytics-service/` - Polars-based analytics engine, reporting, historical trends, and workload insights.
- `infrastructure/` - Docker Compose and Kubernetes manifests for local development and production deployment.
- `docs/` - Architecture, deployment, security, and testing documentation.

## Deployment orchestration

- Local orchestration: `infrastructure/docker-compose.yml`
- Kubernetes manifests: `infrastructure/k8s/`
- Infrastructure services include PostgreSQL with `pgvector`, Redis, RabbitMQ, and service containers.

## Purpose of the restructure

The new directory layout separates each domain service into its own root-level package for easier production deployment, independent CI/CD pipelines, and clearer operational responsibilities. This structure supports a SaaS-ready platform with strict service boundaries, secure tenancy, and scale-out readiness.
