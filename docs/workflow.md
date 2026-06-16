# Workflow Specifications

## End-to-End Attendance Workflow

### 1. Happy Path (On Time)
1. Employee stands in front of the kiosk.
2. Kiosk captures frame and POSTs to `/api/v1/attendance/check-in`.
3. System verifies liveness.
4. AI service extracts embeddings.
5. System finds the employee in `pgvector` index.
6. System checks the Employee's `Shift` and computes that they are within the `buffer_mins`.
7. `AttendanceLog` is created with status `"On Time"`.
8. Background Web3 task successfully anchors to Ethereum.

### 2. Exception Flow: Spoof Attack Detected
1. Employee holds up a photograph of their manager to the kiosk.
2. Kiosk captures frame and POSTs to `/api/v1/attendance/check-in`.
3. System executes Laplacian Liveness check.
4. Blur/Variance metric indicates the image is a flat, 2D photograph.
5. System aborts pipeline and returns `400 Bad Request: Spoofing Detected`.
6. Incident is flagged in the database for HR review.

### 3. Failure Handling: Database Unreachable
If PostgreSQL goes offline, the `backend` instantly catches the SQLAlchemy `OperationalError`. 
* **Mitigation Strategy**: Edge kiosks must implement a local offline queue (SQLite/IndexedDB). They cache the base64 image locally and replay the payloads when the backend returns a `200 OK` health check.

### 4. Failure Handling: Redis Unreachable
Redis is strictly used for JWT blacklisting and Rate Limiting.
* **Mitigation Strategy**: The `is_token_blacklisted` dependency catches the `ConnectionError` and **Fails Open**. This means tokens are assumed valid (if their JWT signature is correct). This prevents the entire physical office from being locked out during a Redis crash.
