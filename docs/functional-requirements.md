# Functional Requirements

## FR-01: Biometric Enrollment
* **Identifier**: FR-01
* **Description**: The system must allow users to enroll their face by submitting an image.
* **Inputs**: Base64 encoded facial image, valid JWT token.
* **Outputs**: 128-dimensional embedding vector stored in DB.
* **Preconditions**: User must not already have an active `FaceEmbedding`.
* **Postconditions**: The `face_embeddings` table is populated.
* **Acceptance Criteria**: Submitting a clear image returns a 200 OK. Submitting an image with no face returns a 400 Bad Request.

## FR-02: Face Check-In
* **Identifier**: FR-02
* **Description**: The system must identify a user from a live photo and log their attendance.
* **Inputs**: Base64 encoded live photo.
* **Outputs**: Attendance log ID, Shift Status (Late, On Time).
* **Preconditions**: User must be enrolled (FR-01).
* **Postconditions**: `attendance_logs` table is updated.
* **Acceptance Criteria**: The system successfully matches the face using L2 distance < 0.6 and computes the shift status accurately based on `buffer_mins` and `grace_period_mins`.

## FR-03: Liveness Detection
* **Identifier**: FR-03
* **Description**: The system must reject printed photos or digital screens.
* **Inputs**: Base64 encoded live photo.
* **Outputs**: Boolean (True if live, False if spoof).
* **Preconditions**: None.
* **Postconditions**: If False, request is rejected before DeepFace embedding extraction.
* **Acceptance Criteria**: Holding up an iPad with a face on it returns 400 Bad Request.

## FR-04: Blockchain Anchoring
* **Identifier**: FR-04
* **Description**: The system must anchor daily attendance hashes to Ethereum.
* **Inputs**: Attendance Log ID, User ID, Timestamp.
* **Outputs**: Ethereum Transaction Hash.
* **Preconditions**: `BLOCKCHAIN_ENABLED` must be True in `SystemSettings`.
* **Postconditions**: `blockchain_audit_logs` table is updated with the TX Hash.
* **Acceptance Criteria**: An asynchronous task successfully signs and broadcasts a payload to the deployed `AttendanceAudit.sol` contract.
