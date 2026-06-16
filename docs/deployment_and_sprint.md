# Deployment & Sprint Specifications
## Sprint-wise Implementation Plan and Production Deployment Guide

### 1. Sprint-Wise Implementation Plan

#### Sprint 1: Identity Foundations & Multi-Tenant Databases
- **Objectives:** Establish base microservices, multi-tenant databases, security integrations, and RBAC authentication.
- **Tasks:**
  - Build Auth & Tenant Microservice.
  - Implement JWT authentication with Refresh Token rotation.
  - Deploy PostgreSQL database instances with Schema isolation.
  - Establish the Custom API Gateway routing table.

#### Sprint 2: Biometric Engine, pgvector, and Liveness Detection
- **Objectives:** Implement face recognition, liveness verification, and optimize database search speeds.
- **Tasks:**
  - Initialize the Biometrics Service using InsightFace/ArcFace.
  - Configure PostgreSQL database with the `pgvector` extension.
  - Construct the HNSW (Hierarchical Navigable Small World) index.
  - Implement liveness anti-spoofing via Laplacian variance and facial landmarks.

#### Sprint 3: Attendance Engine, Offline Sync & Events
- **Objectives:** Build real-time check-in logic, manual overrides, and offline kiosk queues.
- **Tasks:**
  - Deploy the Attendance Service.
  - Configure RabbitMQ event broker for handling inter-service communication.
  - Create manual override flows with supervisor and employee double-signoff.
  - Implement offline queue synchronization for kiosk devices.

#### Sprint 4: Blockchain Anchoring, Analytics & Deployment
- **Objectives:** Configure smart contracts, Polars analytics, CI/CD pipelines, and scale deployments.
- **Tasks:**
  - Write and deploy Solidity anchoring smart contracts to Ganache/Polygon.
  - Create the Analytics Service with Polars aggregations.
  - Write Dockerfiles and compile Kubernetes deployment manifests.
  - Deploy CI/CD workflows and monitor system logs.

---

### 2. Production Deployment Guide

#### 2.1 Cluster Preparation & Namespace
1. Connect to your active cloud environment (e.g. GKE, EKS) and verify connection:
   ```bash
   kubectl cluster-info
   ```
2. Create the platform namespace:
   ```bash
   kubectl create namespace face-attendance
   ```

#### 2.2 Database and Extension Migration
1. Provision database servers (e.g., AWS RDS or Cloud SQL).
2. Apply migrations to initialize target tables:
   ```bash
   cd auth-service
   alembic upgrade head
   ```
3. Enable vector index capabilities:
   ```sql
   -- Connect as database admin
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   CREATE EXTENSION IF NOT EXISTS pgcrypto;
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

#### 2.3 Smart Contract Anchoring Setup
1. Compile smart contracts using Truffle or Hardhat:
   ```bash
   npx hardhat compile
   ```
2. Deploy Solidity contract to Polygon:
   ```bash
   npx hardhat run scripts/deploy.js --network polygon
   ```
3. Copy the returned contract address and paste it into the Blockchain Service configuration map.

#### 2.4 Service Deployments via Kubernetes
1. Apply the ConfigMaps and Secrets files containing variables (DB URL, Redis keys, Secret Keys):
   ```bash
   kubectl apply -f k8s/configmap.yaml -n face-attendance
   kubectl apply -f k8s/secrets.yaml -n face-attendance
   ```
2. Deploy the core services:
   ```bash
   kubectl apply -f k8s/auth-deployment.yaml -n face-attendance
   kubectl apply -f k8s/biometrics-deployment.yaml -n face-attendance
   kubectl apply -f k8s/attendance-deployment.yaml -n face-attendance
   kubectl apply -f k8s/gateway-deployment.yaml -n face-attendance
   ```
3. Apply Horizontal Pod Autoscaling (HPA) policies to manage traffic spikes:
   ```bash
   kubectl apply -f k8s/hpa-biometrics.yaml -n face-attendance
   ```
4. Verify all components are running correctly:
   ```bash
   kubectl get pods -n face-attendance
   ```
