# Infrastructure

This directory contains the local and cloud deployment artifacts for the platform.

## Files

- `docker-compose.yml` - Local development and staging orchestrator that brings up PostgreSQL with pgvector, Redis, RabbitMQ, gateway, auth-service, ai-service, attendance-service, blockchain-service, and analytics-service.
- `k8s/` - Kubernetes manifests for production-ready deployment, including ConfigMaps, Secrets, and Ingress definitions.

## Local setup

From the repository root:

```bash
cd infrastructure
docker compose up --build -d
```

Service endpoints:

- Gateway: `http://localhost:8000`
- Auth service: `http://localhost:8001`
- AI service: `http://localhost:8002`
- Attendance service: `http://localhost:8003`
- Blockchain service: `http://localhost:8004`
- Analytics service: `http://localhost:8005`

## Kubernetes

Build container images and deploy using your chosen registry. The `k8s/` folder contains:

- `configmaps.yaml` - environment variables and shared configuration.
- `secrets.yaml` - encrypted secret references for DB credentials and JWT signing keys.
- `ingress.yaml` - external routing into the cluster.

Deploy with:

```bash
kubectl apply -f infrastructure/k8s/
```

For production, ensure the cluster is configured with persistent volumes for PostgreSQL and a secrets manager for TLS and JWT secrets.
