# Microservices & Infrastructure Specification
## Folder Structures, Containerization, and Orchestration

### 1. Repository Folder Structures

#### 1.1 Backend Microservices Folder Structure
We organize the code into isolated service directories, sharing code patterns and utilizing specific DB configurations.

```
/
├── gateway/                    # API Gateway (FastAPI)
│   ├── app/
│   │   ├── core/               # Routing tables, JWT configs, rate limiting
│   │   └── main.py             # Gateway entry point & route proxies
│   ├── Dockerfile
│   └── requirements.txt
├── auth-service/              # Identity and Multi-Tenant Organization Service
│   │   ├── app/
│   │   │   ├── db/             # Auth Database sessions, tables (Roles, Orgs, Users)
│   │   │   ├── routers/        # /auth, /users, /org
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── ai-service/             # Face Recognition & Verification Service
│   │   ├── app/
│   │   │   ├── db/             # pgvector connections & models (FaceEmbedding)
│   │   │   ├── core/           # InsightFace & MediaPipe wrapper scripts
│   │   │   ├── services/       # FaceEngine (128-d generation, liveness validation)
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── attendance-service/     # Attendance Logic & Override Service
│   │   ├── app/
│   │   │   ├── db/             # Tables (AttendanceLog, ManualOverride, SyncQueue)
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── blockchain-service/     # Append-only hash anchoring service
│   │   ├── app/
│   │   │   ├── contracts/      # AttendanceAudit.sol Smart Contract
│   │   │   ├── services/       # Web3 integration & background listeners
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── analytics-service/      # Polars analytical aggregation service
│       ├── app/
│       │   ├── services/       # Burnout calculations & reports (Excel/PDF)
│       │   └── main.py
│       ├── Dockerfile
│       └── requirements.txt
├── docker-compose.yml          # Local microservices orchestrator
└── k8s/                        # Kubernetes deployment files
```

#### 1.2 Frontend Folder Structure
A modular React + Vite client using Zustand for global store states.
```
frontend/
├── public/
├── src/
│   ├── assets/                 # SVGs, Fonts, Images
│   ├── components/
│   │   ├── common/             # Button, Input, Modal, Sidebar
│   │   ├── ui/                 # Spinner, Alert, Card
│   │   ├── webcam/             # Biometric enrollment & verify webcam modules
│   │   └── ProtectedRoute.jsx  # Route guard for RBAC validation
│   ├── hooks/                  # Custom react hooks (useLiveness, useFetch)
│   ├── layouts/
│   │   └── DashboardLayout.jsx # Admin/Employee sidebars and layouts
│   ├── pages/
│   │   ├── LandingPage.jsx     # Modern marketing landing
│   │   ├── LoginPage.jsx       # Login form with CSRF checking
│   │   ├── Overview.jsx        # Burnout indicators, check-in records
│   │   └── Attendance.jsx      # Video capturing portal & liveness checking
│   ├── services/
│   │   ├── apiClient.js        # Axios instance configured with refresh rotation
│   │   └── biometricService.js # API endpoints for biometrics
│   ├── store/
│   │   └── authStore.js        # Auth state (JWT, User Details, Roles)
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
├── package.json
└── vite.config.js
```

---

### 2. Containerization (Docker Compose)
Use this `docker-compose.yml` to spin up local replicas of databases, caches, brokers, and services for testing.

```yaml
version: '3.8'

services:
  postgres:
    image: ankane/pgvector:v0.5.1
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgrespassword
      POSTGRES_DB: face_attendance_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"

  gateway:
    build:
      context: ./gateway
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - AUTH_SVC_URL=http://auth_svc:8001
      - BIO_SVC_URL=http://bio_svc:8002
      - ATT_SVC_URL=http://att_svc:8003
    depends_on:
      - postgres
      - redis

  auth_svc:
    build:
      context: ./auth-service
    environment:
      - DATABASE_URL=postgresql://postgres:postgrespassword@postgres:5432/face_attendance_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres

  bio_svc:
    build:
      context: ./ai-service
    environment:
      - DATABASE_URL=postgresql://postgres:postgrespassword@postgres:5432/face_attendance_db
    depends_on:
      - postgres

volumes:
  postgres_data:
```

---

### 3. Kubernetes Orchestration (k8s Manifests)

#### 3.1 Gateway Deployment & Service
`k8s/gateway-deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gateway-deployment
  namespace: face-attendance
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gateway
  template:
    metadata:
      labels:
        app: gateway
    spec:
      containers:
      - name: gateway
        image: gcr.io/face-attendance-platform/api-gateway:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "1"
            memory: 1Gi
          requests:
            cpu: "500m"
            memory: 512Mi
        envFrom:
        - configMapRef:
            name: gateway-config
---
apiVersion: v1
kind: Service
metadata:
  name: gateway-service
  namespace: face-attendance
spec:
  selector:
    app: gateway
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

#### 3.2 Kubernetes HPA (Horizontal Pod Autoscaler)
`k8s/hpa-biometrics.yaml`
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: biometrics-hpa
  namespace: face-attendance
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: biometrics-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75
```

---

### 4. CI/CD Pipelines (GitHub Actions)
`.github/workflows/deploy.yml`
```yaml
name: CI/CD Production Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install ruff pytest

    - name: Lint with Ruff
      run: ruff check .

    - name: Run unit tests
      run: pytest

  build-and-push:
    needs: lint-and-test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3

    - name: Log in to Google Container Registry
      uses: docker/login-action@v2
      with:
        registry: gcr.io
        username: _json_key
        password: ${{ secrets.GCP_SA_KEY }}

    - name: Build and Push API Gateway Image
      run: |
        docker build -t gcr.io/face-attendance-platform/api-gateway:${{ github.sha }} -t gcr.io/face-attendance-platform/api-gateway:latest ./gateway
        docker push gcr.io/face-attendance-platform/api-gateway:${{ github.sha }}
        docker push gcr.io/face-attendance-platform/api-gateway:latest
```
