# Objectives and Goals

## Business Objectives
1. **Eliminate Time Theft**: Completely eradicate buddy-punching and unauthorized check-ins.
2. **Ensure Auditability**: Guarantee that all attendance records are legally and cryptographically verifiable for compliance purposes.
3. **Streamline Payroll**: Automate the calculation of "Late," "On Time," and "Early" statuses based on dynamic shift rules to reduce HR overhead by 80%.

## Technical Objectives
1. **Microsecond Vector Search**: Utilize `pgvector` to perform HNSW (Hierarchical Navigable Small World) distance calculations in PostgreSQL to achieve <500ms face matching.
2. **Zero-Knowledge Architecture**: Never store raw biometric images; only store mathematical embeddings.
3. **Immutable Ledgers**: Implement an Ethereum Web3 integration that anchors daily attendance hashes asynchronously without blocking the core API.
4. **Failsafe Graceful Degradation**: Ensure that if secondary systems (Redis, Blockchain nodes) go offline, the core API continues to process attendance logs securely.

## Short-Term Goals (0-3 Months)
* Successfully deploy the hybrid proxy architecture to an AWS EC2 `g4dn.xlarge` instance.
* Enroll 100 pilot employees with 99% embedding accuracy.
* Achieve sub-2-second end-to-end check-in latency.

## Long-Term Goals (6-12 Months)
* Implement a distributed Microservice architecture on Google Kubernetes Engine (GKE) to support >10,000 concurrent employee clock-ins.
* Integrate Edge-Device caching (e.g., Raspberry Pi kiosks) that can perform offline check-ins and sync payloads securely when the network returns.

## Success Metrics & KPIs
* **Latency**: Median API response time for `/api/v1/attendance/check-in` under 2000ms.
* **Accuracy**: False Acceptance Rate (FAR) < 0.001%.
* **Uptime**: 99.9% backend availability.
* **Adoption**: 100% of target workforce enrolled via the one-time ZKP token link.
