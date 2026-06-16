# System Specifications

## Hardware Requirements
### Core API (Backend)
* **CPU**: 2+ vCPUs
* **RAM**: 2GB+ Memory
* **Disk**: 10GB SSD

### AI Service
* **CPU**: 4+ vCPUs
* **RAM**: 16GB+ Memory
* **GPU**: NVIDIA T4 or better (Highly Recommended for sub-second DeepFace embedding extraction).

## Software Requirements
* **OS**: Ubuntu 22.04 LTS (or equivalent Linux distribution)
* **Containerization**: Docker Server 24.x+, Docker Compose V2
* **Python**: 3.12+ (For local development)

## Runtime Dependencies
* **PostgreSQL**: Version 15+ (MUST have the `pgvector` extension installed).
* **Redis**: Version 7.x (Used for async rate limiting and token blacklisting).
* **Blockchain Node**: Infura, Alchemy, or a local Hardhat/Ganache node for Ethereum interaction.

## Third-Party Services
* **Ethereum Network**: The `web3.py` client requires a funded wallet (Sepolia testnet or Mainnet) to pay gas fees for the `AttendanceAudit.sol` contract.
