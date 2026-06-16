# Face Recognition-Based Attendance System
> **An Enterprise-Grade, Zero-Knowledge Biometric Time and Attendance Platform with Web3 Anchoring.**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)](https://www.postgresql.org/)
[![Ethereum Web3](https://img.shields.io/badge/Web3-Sepolia_Testnet-627EEA.svg)](https://ethereum.org/)

## Executive Summary
The Face Recognition-Based Attendance System is a modern, high-performance platform designed to eliminate buddy-punching, streamline payroll operations, and guarantee absolute auditability. By combining state-of-the-art DeepFace models, high-speed `pgvector` similarity searches, and immutable Ethereum blockchain anchoring, this system provides organizations with mathematically undeniable attendance records.

## Key Features
* **Zero-Knowledge Biometrics**: Raw face images are never stored. The system strictly stores 128-dimensional mathematical embeddings.
* **Liveness Detection**: Anti-spoofing pipeline rejects static photographs and digital masks.
* **Web3 Audit Trail**: Every check-in is hashed and anchored to an Ethereum smart contract.
* **Role-Based Access Control (RBAC)**: Multi-tenant architecture with distinct permissions for SuperAdmins, Admins, Managers, and Employees.
* **Emotion & Burnout Analytics**: Background analysis of employee sentiment to detect burnout risks and trigger managerial nudges.
* **Resilient Infrastructure**: Failsafe Redis implementation gracefully degrades token blacklisting without taking the system offline.

## Technology Stack
* **Backend**: FastAPI (Python 3.12)
* **AI/ML Engine**: DeepFace, PyTorch
* **Database**: PostgreSQL 15+ with `pgvector` extension
* **Caching/Rate-Limiting**: Redis (ElastiCache)
* **Blockchain**: Solidity (`AttendanceAudit.sol`), `web3.py`
* **Deployment**: Docker Compose, AWS EC2, GitHub Actions

## Architecture Snapshot
The platform employs a hybrid proxy architecture. A lightweight **FastAPI Monolith** handles all HTTP routing, JWT validation, rate limiting, and database interactions. Heavy biometric operations are offloaded via HTTP to an isolated **AI-Service** container, allowing the ML models to fully utilize attached GPUs (like the NVIDIA T4) without blocking concurrent API requests.

## Quick Start
1. Configure your `.env` variables (see `SETUP.md`).
2. Run the deployment sequence:
```bash
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

## Documentation Index
Comprehensive documentation can be found in the `docs/` directory:
1. [Project Overview](docs/project-overview.md)
2. [Architecture Blueprint](docs/architecture.md)
3. [Database Design](docs/database-design.md)
4. [Deployment Guide](docs/deployment-guide.md)
5. [Security Design](docs/security-design.md)

## License
Proprietary / Closed Source. All rights reserved.
