# Features

## 1. Zero-Knowledge Biometric Identification
* **Purpose**: Identify employees walking into an office without requiring passwords or badges, without storing their actual face.
* **Technical Implementation**: Takes a base64 frame, passes it to the `ai-service`, runs `DeepFace` to extract a 128-dimensional embedding, and uses PostgreSQL `pgvector` (`L2 distance < 0.6`) to match the user.
* **Business Value**: Eliminates buddy punching and physical hardware bottlenecks.

## 2. Web3 Attendance Anchoring
* **Purpose**: Guarantee that an attendance record was not maliciously altered after the fact by a rogue DBA or manager.
* **Technical Implementation**: A background FastApi task hashes the attendance payload (User ID, Timestamp, Action) via SHA-256 and signs a transaction to an Ethereum smart contract using `web3.py`.
* **Limitations**: Highly dependent on Gas fees. Can be toggled off via the `SystemSettings` table.

## 3. Dynamic Shift Calculation
* **Purpose**: Automatically compute if an employee is Late or On-Time.
* **Technical Implementation**: The `AttendanceController` calculates the delta between the physical timestamp and the User's `Shift` start time, accounting for specific `buffer_mins` (clocking in early) and `grace_period_mins` (clocking in late).
* **Business Value**: Eliminates 80% of HR's manual payroll reconciliation.

## 4. Emotional Wellness Analytics
* **Purpose**: Passively track macro-level burnout in a department.
* **Technical Implementation**: The `ai-service` runs a lightweight emotion classification model on the check-in frame (Happy, Sad, Angry, Neutral). This is aggregated into a `/api/v1/attendance/wellness-heatmap` for managers.
* **Limitations**: Accuracy varies by lighting conditions; cannot be used for punitive measures.
