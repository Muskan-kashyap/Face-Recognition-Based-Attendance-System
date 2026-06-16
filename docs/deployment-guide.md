# Deployment Guide

## 1. Local Development

### Prerequisites
- Python 3.12+
- Docker & Docker Compose V2
- PostgreSQL client (`psql`) for DB inspection

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd Face-Recognition-Based-Attendance-System

# Set up Python virtual environment
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables
Copy the example `.env` file and fill in your values:
```bash
cp backend/.env.example backend/.env
```

Key variables to configure in `backend/.env`:
```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/attendance_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-very-long-secret-key-here
BLOCKCHAIN_ENABLED=false
```

### Startup Commands
```bash
# Start the database and Redis
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres ankane/pgvector
docker run -d -p 6379:6379 redis:7.2-alpine

# Run Alembic migrations
cd backend
alembic upgrade head

# Start backend
uvicorn main:app --reload --port 8000

# (In another terminal) Start AI service
cd ai-service
uvicorn app.main:app --reload --port 8002
```

---

## 2. Production Deployment (AWS EC2 + Docker Compose)

### Infrastructure Requirements
- **Compute**: AWS EC2 `g4dn.xlarge` (1 NVIDIA T4 GPU, 16GB RAM)
- **Database**: Amazon RDS PostgreSQL 15+ (`db.t4g.small`) — **Multi-AZ enabled**
- **Cache**: Amazon ElastiCache Redis
- **Container Registry**: Amazon ECR

### Step 1 — Configure GitHub Secrets
In your GitHub repository settings → Secrets, add:
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
- `EC2_HOST` — Public IP or Elastic IP of your EC2 instance
- `EC2_SSH_KEY` — Private SSH key for the `ubuntu` user
- `SECRET_KEY`, `BLOCKCHAIN_PRIVATE_KEY`

### Step 2 — Initial Server Setup (one-time)
SSH into your EC2 instance and run:
```bash
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin git awscli
git clone <your-repo-url> /home/ubuntu/Face-Recognition-Based-Attendance-System
```

### Step 3 — Configure Environment on EC2
Create `/home/ubuntu/Face-Recognition-Based-Attendance-System/.env.prod`:
```env
DATABASE_URL=postgresql+psycopg2://admin:password@<rds-endpoint>:5432/attendance_db
REDIS_URL=redis://<elasticache-endpoint>:6379/0
SECRET_KEY=<fetched-from-secrets-manager>
BLOCKCHAIN_ENABLED=false
```

### Step 4 — Deploy
Push to `main`. GitHub Actions will automatically:
1. Build and push Docker image to ECR.
2. SSH into EC2 and run `scripts/deploy.sh`.
3. `deploy.sh` runs Alembic migrations, then restarts containers.

---

## 3. CI/CD Pipeline
The pipeline is defined in `.github/workflows/deploy.yml` and runs on every push to `main`:

```mermaid
graph LR
    A[Push to main] --> B[Build Docker Image]
    B --> C[Push to AWS ECR]
    C --> D[SSH to EC2]
    D --> E[alembic upgrade head]
    E --> F[docker-compose up -d]
```

## 4. Rollback Procedures
If a deployment fails or introduces regressions:
```bash
# On the EC2 instance — instantly reverts to previous working containers
docker-compose -f docker-compose.prod.yml down
docker pull <ECR_REGISTRY>/attendance-backend:<previous-tag>
docker-compose -f docker-compose.prod.yml up -d
```
