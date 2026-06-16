# Future Enhancements

## Immediate Improvements (0-3 months)

### 1. Connect Web3 Toggle to Frontend Dashboard
* **Status**: Backend API complete; frontend UI not yet connected.
* **Effort**: Low (1-2 days)
* **Impact**: SuperAdmins can toggle gas fees without using a REST client.

### 2. Squash Alembic Migrations
* **Status**: Migration history contains manually patched files with commented-out type casts.
* **Effort**: Low (half day)
* **Action**: Once the production schema is stable, run `alembic merge heads` to produce a clean single baseline migration.

### 3. Strengthen `face_embeddings` Index
* **Status**: Currently using default index type.
* **Action**: Create an explicit HNSW index: `CREATE INDEX USING hnsw (embedding vector_l2_ops);`
* **Impact**: 5-10x faster vector search at scale.

---

## Near-Term Enhancements (3-6 months)

### 4. Layer 2 Ethereum Integration
* Instead of anchoring to Mainnet (expensive), route to **Polygon** or **Arbitrum**.
* Gas costs reduce from ~$1.50/tx to ~$0.001/tx.
* Implementation requires changing only the `BLOCKCHAIN_URL` env variable and redeploying the contract.

### 5. Real-Time WebSocket Dashboard
* Push check-in events to a live admin dashboard using FastAPI WebSockets.
* HR can watch employees clock in on a live map of the office floor plan.

### 6. PDF & Excel Payroll Export
* Integrate `openpyxl` / `reportlab` to auto-generate monthly attendance reports per employee.

---

## Long-Term Innovations (6-12 months)

### 7. Multi-Factor Authentication (MFA)
* Combine facial recognition with a TOTP code (Google Authenticator) for ultra-high-security environments.

### 8. Distributed Microservices (GKE)
* Fully decompose the monolith into the originally envisioned microservice architecture.
* Each service (`auth-service`, `ai-service`, `attendance-service`) gets its own PostgreSQL schema for true data isolation.

### 9. GDPR / PDPA Compliance Module
* **Right to Erasure**: Implement an endpoint to safely delete all `face_embeddings` for a given user without breaking attendance history.
* **Data Portability**: Allow employees to download their full attendance history as a JSON file.

---

## Research Opportunities

### 10. Zero-Proof Knowledge Enrollment
* Investigate using **Zero-Knowledge Proofs (ZKPs)** to allow the system to verify "this face matches the enrolled record" without ever transmitting or exposing the embedding vector — even internally. This is the ultimate privacy-preserving biometric architecture.
