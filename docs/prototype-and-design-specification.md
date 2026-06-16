# Prototype and Design Specification

## Design Philosophy
1. **API-First**: The backend is completely headless, exposing RESTful endpoints documented automatically via OpenAPI (Swagger).
2. **Stateless Operations**: No data is kept in memory. This ensures horizontal scalability and resilience.
3. **Fail-Open Security**: Security is paramount, but physical throughput at an office door is equally important. If secondary validation systems fail, the system fails open to prevent physical bottlenecks, relying on asynchronous reconciliation later.

## Module Decomposition
1. `app.routers`: The API surface area. Strictly handles HTTP requests, JWT validation, and input parsing.
2. `app.services`: The Business Logic layer. Contains `FaceEngine` (proxy to AI), `BlockchainService`, and `AttendanceController`.
3. `app.crud`: The Data Access layer. Strictly handles SQLAlchemy ORM queries and mutations.
4. `app.db.models`: The Schema layer.

## Constraints
* **Synchronous AI Processing**: Currently, the FastAPI backend blocks synchronously while waiting for the `ai-service` to return a facial embedding. This is a deliberate design choice over an Event-Driven architecture (Kafka/RabbitMQ) to ensure the physical door/turnstile opens *immediately* for the user upon a 200 OK response.
* **Image Size**: The system restricts incoming base64 payload sizes to 5MB to prevent memory exhaustion attacks.
