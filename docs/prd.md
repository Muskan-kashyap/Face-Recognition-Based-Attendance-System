# Product Requirements Document (PRD)
## AI-Powered Face Recognition Attendance Management Platform

### 1. Executive Summary & Vision
The AI-Powered Face Recognition Attendance Management Platform is a production-grade, multi-tenant SaaS application designed to provide organizations with a secure, spoof-proof, automated, and tamper-resistant system for employee attendance. By leveraging advanced biometric recognition, facial emotion analytics, liveness detection, and blockchain anchoring, the platform eliminates buddy punching, verifies the authenticity of attendance records, detects workforce burnout risk, and operates seamlessly even in network-constrained environments.

---

### 2. Core Personas & Roles
The system enforces strict Role-Based Access Control (RBAC) across multi-tenant boundaries:
- **System Administrator (SaaS Provider):** Manages organizations (tenants), system billing, global configurations, and monitors global API gateways.
- **Tenant Administrator (HR Director / Org Admin):** Manages organization departments, shifts, user onboarding, role assignments, API keys for edge devices, and handles attendance overrides.
- **Manager / Supervisor:** Views department-level dashboards, reviews team attendance logs, runs reports, and flags anomalies.
- **Employee:** Registers biometric credentials via one-time tokens, clock-ins/outs via web/mobile/edge portal, views personal attendance logs, requests corrections, and files support tickets or reimbursement claims.
- **Device (Edge Client):** Non-human API agent acting as a wall-mounted tablet or kiosk submitting attendance logs in bulk or real-time.

---

### 3. Feature Breakdown & Requirements

#### 3.1 Multi-Tenant SaaS Infrastructure
- **Isolation:** Absolute separation of tenant data (users, logs, departments) via unique organization identifiers (`org_id`).
- **Tenant Onboarding:** Automatic generation of tenant organization records, onboarding tokens, and default roles.
- **API Key Management:** Tenants can generate secure, scoped API keys for edge devices with rate limits.

#### 3.2 Biometric Face Registration & Verification
- **Onboarding Workflow:** Employees receive a secure, one-time enrollment token via email to register their faces.
- **Biometric Processing:** Extracts a 128-dimensional face embedding using InsightFace/ArcFace and stores it in PostgreSQL via `pgvector`.
- **Zero-Knowledge Commitment:** Stores Schnorr public commitments to secure biometric signatures without saving raw face photos.

#### 3.3 Real-Time Attendance & Liveness Detection
- **Sub-500ms Latency:** Recognition pipeline must verify embeddings against the organization's database partition in less than 500ms.
- **Anti-Spoof Liveness Protection:** MediaPipe landmarks and motion analysis (e.g., blink, texture analysis, and Laplacian depth variance) prevent spoofing using screens, photos, or 3D masks.
- **Facial Emotion Analytics:** Analyzes expression (e.g., happy, sad, angry, stressed) at clock-in using DeepFace.

#### 3.4 Blockchain-Backed Integrity Verification
- **Hash Anchoring:** Every check-in/out record is hashed and anchored to a Solidity smart contract deployed on Polygon/Ganache.
- **Verification Portal:** Administrators can check if a database log has been modified by comparing it against the blockchain state.

#### 3.5 Offline Synchronization Queue
- **Edge Kiosk Mode:** Wall-mounted kiosks queue recognition logs locally when offline.
- **Sync Reconciliation:** Automatically pushes queued payloads to the API Gateway when network reconnects, maintaining correct check-in timestamps.

#### 3.6 Manual Override Workflow
- **Correction Requests:** When recognition fails or devices malfunction, admins can override attendance logs.
- **Double-Signoff:** Requires admin reasoning and employee approval for the correction to seal.

#### 3.7 Predictive Workforce Analytics
- **Burnout Heatmap:** Aggregates emotion scores and late arrivals by department using Polars to highlight burnout risks.
- **AI Nudges:** Automatically alerts managers when a department's burnout index exceeds a critical threshold (>40).

---

### 4. User Stories & Acceptance Criteria

| ID | User Story | Acceptance Criteria |
|---|---|---|
| **US-01** | As an Employee, I want to register my biometric face credentials securely via a one-time onboarding link, so my biometrics are registered without storing my raw images. | 1. Link expires after 24 hours.<br>2. Image processed in memory to generate a 128-d embedding.<br>3. Generates Schnorr public commitment (`zkp_public_commitment`).<br>4. Raw image discarded immediately. |
| **US-02** | As an Employee, I want to clock in at the wall-mounted kiosk, so that my attendance is logged instantly. | 1. Clock-in takes < 500ms from face detection.<br>2. Liveness detection filters photos/screens.<br>3. Emits emotion tag (e.g., 'happy', 'stressed').<br>4. Generates database entry and queues blockchain anchoring transaction. |
| **US-03** | As a Tenant Admin, I want to approve a manual override for an employee who forgot to clock in, so that payroll is calculated correctly. | 1. Admin enters reason category and override status.<br>2. Employee receives a verification notification.<br>3. Status updates to `manual_override` once employee signs off. |
| **US-04** | As a Manager, I want to view a department burnout heatmap, so that I can detect stress events and implement wellness measures. | 1. Aggregates data over a rolling 30 days using Polars.<br>2. Computes wellness score and flags stress index if stress emotions exceed 40% of logs.<br>3. Renders a color-coded department heatmap. |
