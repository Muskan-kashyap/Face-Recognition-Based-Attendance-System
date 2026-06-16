# Non-Functional Requirements

## 1. Performance
* **Latency**: The `POST /api/v1/attendance/check-in` endpoint must return a response in under 2.5 seconds (P95).
* **Vector Search**: PostgreSQL `pgvector` HNSW index must search 100,000 embeddings in < 50ms.

## 2. Scalability
* **Statelessness**: The FastAPI application must remain stateless, relying entirely on Redis for session state and rate-limiting to allow horizontal auto-scaling via Kubernetes or AWS Auto Scaling Groups.

## 3. Reliability
* **Fail-Open Mechanics**: If Redis crashes, the token blacklist must "fail open" (allowing check-ins to continue) while logging the error, ensuring the physical entry gates never back up.
* **Database Resiliency**: The system must connect to a managed HA Database (e.g., AWS RDS Multi-AZ) to prevent data loss.

## 4. Security
* **Zero-Knowledge Biometrics**: The system shall NEVER persist raw facial images (.jpg, .png) to disk or database. Only the mathematically irreversible 128-d vector floats are saved.
* **RBAC**: A strict Role-Based Access Control matrix must be enforced via JWT payload inspection.

## 5. Maintainability
* **Proxy Architecture**: The heavy AI/ML dependencies (Torch, DeepFace) must remain strictly segregated in the `ai-service` container to ensure the core `backend` container remains lightweight and easy to deploy.
