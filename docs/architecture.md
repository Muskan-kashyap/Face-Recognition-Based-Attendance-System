# Architecture Blueprint

## High-Level Architecture
The system employs a **Hybrid Proxy Architecture**. The FastAPI `backend` handles 95% of requests natively but proxies heavy biometric processing to the isolated `ai-service`.

```mermaid
graph TD
    Client[Client App / Edge Kiosk] -->|HTTP/REST| API[FastAPI Backend Monolith]
    
    API <-->|Reads/Writes| DB[(PostgreSQL + pgvector)]
    API <-->|Caches/Rate Limits| Redis[(Redis)]
    
    API -->|HTTP Proxy| AI[AI-Service]
    AI <-->|Loads Models| Models[(DeepFace / Torch Models)]
    
    API -->|Async Web3 RPC| ETH[Ethereum Network]
    ETH -->|Anchors to| SC[AttendanceAudit.sol]
```

## Architectural Decisions & Trade-offs
1. **Proxy vs Message Queue**: We chose HTTP Proxying over Kafka/RabbitMQ for the AI-service communication because attendance check-ins require immediate, synchronous feedback to open physical doors. Event-driven architectures introduce asynchronous complexity that is detrimental to physical access control.
2. **PostgreSQL pgvector vs Milvus**: We consolidated vector storage into PostgreSQL using the `pgvector` extension rather than introducing a dedicated vector DB (like Pinecone or Milvus). This drastically simplifies deployment and ensures relational data (User IDs) and vector data are backed up simultaneously, preventing split-brain corruption.

## Component Flow
```mermaid
sequenceDiagram
    participant User
    participant Backend
    participant AIService
    participant DB
    participant Blockchain
    
    User->>Backend: POST /check-in (base64 image)
    Backend->>AIService: POST /extract
    AIService-->>Backend: 128-d vector
    Backend->>DB: L2 Distance Search < 0.6
    DB-->>Backend: User ID
    Backend->>DB: Insert Attendance Log
    Backend-->>User: 200 OK (Door Opens)
    
    Note over Backend,Blockchain: Asynchronous Background Task
    Backend->>Blockchain: Anchor Hash to Smart Contract
```
