# Glossary

| Term | Definition |
|------|-----------|
| **Alembic** | A Python-based database migration tool for SQLAlchemy. Tracks schema changes over time as versioned Python scripts. |
| **AnchorRecord** | The core function in `AttendanceAudit.sol` that writes a SHA-256 hash to the Ethereum ledger. |
| **AttendanceLog** | The database record created each time an employee clocks in or out. Core business entity. |
| **bcrypt** | A password hashing function used to securely store user passwords. Computationally expensive by design to resist brute-force attacks. |
| **Buddy Punching** | The fraudulent practice of one employee clocking in on behalf of a colleague who hasn't arrived yet. |
| **BlockchainAuditLog** | A database table that stores the Ethereum transaction hash linking an `AttendanceLog` record to the immutable blockchain ledger. |
| **DeepFace** | A Python library that wraps multiple state-of-the-art face recognition models (ArcFace, FaceNet, VGG-Face). Used to extract face embeddings. |
| **Embedding** | A 128-dimensional array of floating-point numbers that represents the mathematical features of a human face. Mathematically irreversible — the original face cannot be reconstructed from it. |
| **FAR (False Acceptance Rate)** | The rate at which the biometric system incorrectly accepts an unauthorized person as a registered user. Must be minimized. |
| **Gas Fees** | The cost (in ETH) to execute a transaction on the Ethereum blockchain. Proportional to computational complexity. |
| **Grace Period** | A configurable number of minutes after a shift's start time during which an employee is still classified as "On Time". |
| **HNSW** | Hierarchical Navigable Small World. A graph-based approximate nearest-neighbor search algorithm used by `pgvector` for fast face matching. |
| **JWT (JSON Web Token)** | A compact, signed token used to securely transmit authentication claims between the client and server without maintaining server-side session state. |
| **L2 Distance** | Euclidean distance. Used by `pgvector` to compare two face embeddings. A smaller L2 distance = more similar faces. A threshold of `0.6` is used for matching. |
| **Liveness Detection** | The process of verifying that the face presented to the camera is a live human being, not a photograph, video, or 3D mask. |
| **Multi-Tenancy** | An architecture where a single deployed system serves multiple independent organizations (tenants) with complete data isolation. |
| **pgvector** | A PostgreSQL extension that adds a native `VECTOR` data type and distance functions, enabling fast similarity searches directly in the database. |
| **RBAC (Role-Based Access Control)** | An access control model where permissions are granted to roles (SuperAdmin, Admin, etc.) and users inherit permissions by being assigned a role. |
| **Simulation Mode** | A fallback state where the Blockchain service generates a local `sim_tx_{uuid}` hash instead of broadcasting a real transaction, resulting in zero gas cost. |
| **Smart Contract** | Self-executing code deployed on the Ethereum blockchain. The `AttendanceAudit.sol` contract is the immutable record keeper for this system. |
| **SuperAdmin** | The highest privilege role in the system. Can manage system-wide settings (like the Web3 toggle), create organizations, and override any data. |
| **SystemSetting** | A database table that stores key-value configuration pairs (e.g., `blockchain_enabled=true`), allowing dynamic runtime control without server restarts. |
| **ZKP (Zero-Knowledge Proof)** | A cryptographic method by which one party can prove to another party that they know a value, without conveying any information apart from the fact that they know the value. |
