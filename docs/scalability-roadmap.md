# Scalability Roadmap

## Current Architecture Limits
The current Hybrid Docker Compose architecture on a single AWS EC2 instance has the following practical limits:

| Metric | Current Limit | Notes |
|--------|--------------|-------|
| Concurrent check-ins | ~50-100/min | Limited by single-node synchronous processing |
| Face embeddings in DB | ~500K | HNSW index degrades above this on a `db.t4g.small` |
| API throughput | ~200 req/sec | FastAPI + single uvicorn worker |
| AI processing | ~10 faces/sec | NVIDIA T4 GPU on `g4dn.xlarge` |

---

## Scaling Strategies

### Phase 1: Vertical Scaling (0-6 months)
The fastest path to scaling. Upgrade the single EC2 instance:
- `g4dn.xlarge` → `g4dn.2xlarge` (doubles GPU memory; handles ~20 faces/sec)
- `db.t4g.small` → `db.r6g.large` (5x more DB RAM for pgvector HNSW hot data)

**Impact**: Supports up to ~300 concurrent morning check-ins. Minimal operational change.

### Phase 2: Horizontal API Scaling (6-12 months)
Move from single-EC2 Docker Compose to an **AWS ECS (Fargate)** cluster:
- Run multiple instances of the `backend` container behind an **Application Load Balancer (ALB)**.
- `ai-service` runs on a separate ECS service with GPU capacity providers.
- Shared state (DB + Redis) remains managed services and is not duplicated.

**Impact**: Linear scalability. 3 backend containers → 3x throughput.

### Phase 3: Kubernetes on GKE (12-24 months)
For enterprise-grade, multi-campus deployments (10,000+ employees):
- Migrate to **Google Kubernetes Engine (GKE)** with Horizontal Pod Autoscalers (HPA).
- AI service scales from 2 → 10 GPU pods during the 9:00 AM peak window automatically.
- PostgreSQL migrates to **Google Cloud AlloyDB** for integrated `pgvector` support.

### Phase 4: Edge Computing (Future)
To eliminate latency from remote office locations:
- Deploy **Raspberry Pi kiosks** that run a lightweight TensorFlow Lite face model locally.
- Cache embeddings on the edge device (AES-256 encrypted).
- Kiosks sync offline queues to the cloud when connectivity is restored, eliminating dependency on the WAN during peak hours.
