# Software Requirements Specification (SRS)
## AI-Powered Face Recognition Attendance Management Platform

### 1. Introduction
This Software Requirements Specification (SRS) defines the functional, performance, security, and interface requirements for the modular Face Recognition Attendance Platform.

### 2. Functional Requirements

#### 2.1 Multi-Tenant Identity & Access Management (IAM)
- **FR-1.1:** The system must support isolated tenant organizations, storing all user accounts, shifts, and logs under a unique UUID `org_id`.
- **FR-1.2:** Implement Role-Based Access Control (RBAC) with specific permission matrices for System Admins, Tenant Admins, Managers, Employees, and Edge Devices.
- **FR-1.3:** Provide JWT-based authentication with Access Tokens (expires in 60 mins) and Refresh Tokens (expires in 7 days) stored securely in HTTP-only cookies.

#### 2.2 Biometric Processing & Face Recognition
- **FR-2.1:** The biometric system must accept facial images via webcam or uploaded frames, detecting exactly one face per image.
- **FR-2.2:** The system must extract a 128-dimensional embedding vector representing the face.
- **FR-2.3:** Biometric matches must be performed against active records in the database (`is_active = 1` and `is_deleted = 0`) using Cosine similarity.
- **FR-2.4:** The system must implement Schnorr signature zero-knowledge proofs to store public commitments of biometric templates, ensuring raw biometric templates cannot be reverse-engineered into images.

#### 2.3 Liveness Detection & Anti-Spoofing
- **FR-3.1:** Prior to embedding extraction, the image must undergo texture and depth analysis.
- **FR-3.2:** Laplacian variance calculations must classify images with a variance below $100$ as flat media (spoof attempts) and reject them.
- **FR-3.3:** MediaPipe facial landmark coordinates must analyze structural landmarks to ensure the face is a 3D volume.

#### 2.4 Offline Kiosk Synchronization
- **FR-4.1:** Edge devices must run a local SQLite database and queue check-ins offline.
- **FR-4.2:** On network reconnection, the offline queue must send batches to the Gateway.
- **FR-4.3:** The backend must parse the batch payload, inserting logs with their original `captured_at` timestamps into the primary database.

#### 2.5 Blockchain Anchoring & Audit Trail
- **FR-5.1:** All check-ins, registration updates, and manual overrides must trigger a background process that hashes the database record and anchors it to the smart contract.
- **FR-5.2:** Provide a verification endpoint that fetches the contract hash for a specific `ref_id` and verifies it against the current database row hash.
- **FR-5.3:** Database tables must utilize soft deletes via an `is_deleted` flag. Hard deletes are strictly forbidden to ensure audit integrity.

#### 2.6 Analytical Pipeline
- **FR-6.1:** Aggregations of emotions and schedules must be computed daily via Polars.
- **FR-6.2:** Calculate burnout risk indicators by flagging department stress indexes when stress emotions (e.g., angry, sad, fear) exceed 40% of records in a 30-day window.

---

### 3. Non-Functional Requirements

#### 3.1 Performance
- **NFR-1.1 (Latency):** Biometric matching and check-in confirmation must execute in under 500ms under a load of 1,000 concurrent requests.
- **NFR-1.2 (Search Speed):** Use an HNSW index (Hierarchical Navigable Small World) on the `vector(128)` embedding column to maintain sub-10ms search times across 100,000 enrolled users.

#### 3.2 Security & Compliance
- **NFR-2.1 (GDPR Biometric Compliance):** Raw face images must never be stored on disks or database columns.
- **NFR-2.2 (Data-in-Transit):** All APIs must enforce TLS 1.3. Communication between microservices must run over secure internal virtual networks.
- **NFR-2.3 (Rate Limiting):** API gateways must restrict requests to 100 requests/minute per API key to mitigate Denial of Service (DoS) attacks.

#### 3.3 Reliability & Availability
- **NFR-3.1 (Uptime):** System availability must meet 99.9% uptime SLA.
- **NFR-3.2 (Offline Tolerance):** Edge devices must tolerate internet outages of up to 30 days, caching up to 50,000 attendance records locally.

---

### 4. System Boundaries & Interface Specifications
```
+-------------------------------------------------------------+
|                      React Web App                          |
+------------------------------+------------------------------+
                               | HTTPS / WSS
                               v
+-------------------------------------------------------------+
|                    FastAPI API Gateway                      |
+-------+-------------------+--------------------+------------+
        |                   |                    |
        v                   v                    v
+---------------+   +---------------+   +---------------------+
| Auth/IAM Svc  |   | Biometrics Svc|   | Analytics & BI Svc  |
| (PostgreSQL)  |   | (pgvector DB) |   | (Polars, Replica DB)|
+---------------+   +-------+-------+   +---------------------+
                            |
                            v
                    +---------------+
                    | Blockchain Svc| ----> [Solidity Smart Contract]
                    | (RabbitMQ)    |
                    +---------------+
```
- **Database Interfaces:** Services communicate exclusively with their own database instances or isolated schemas. Direct cross-service database access is prohibited.
- **Communication Protocol:** Synchronous inter-service calls use gRPC, and asynchronous event distribution (e.g. blockchain indexing, log synchronization) uses RabbitMQ.
