# Face Recognition Based Attendance System

This repository contains a full-stack attendance system using face recognition, with a FastAPI backend and a Vite + React frontend.

## What is included
- `backend/`: FastAPI server, PostgreSQL/Redis configuration, face recognition and blockchain integration
- `frontend/`: React application built with Vite
- `Dockerfile.prod`: production build container setup for backend and frontend

## Prerequisites
- Python 3.10+ / 3.12 recommended
- Node 18+ / npm 10+
- Git installed locally
- PostgreSQL database
- Redis server
- Optional: Docker for containerized deployment

## Full local setup script
From the repository root, run:

```bash
chmod +x setup.sh
./setup.sh
```

This will create the backend virtual environment, install backend and frontend dependencies, and prepare the project for local development.

## Backend setup
1. Create a Python virtual environment:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

2. Upgrade pip and install backend dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Copy the example environment file and update values:

```bash
cp .env.example .env
```

4. Edit `backend/.env` and set the PostgreSQL credentials, `SECRET_KEY`, and any other required values.

5. Start the backend server:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend API will be available at `http://127.0.0.1:8000` and Swagger docs at `http://127.0.0.1:8000/docs`.

## Frontend setup
1. Install frontend dependencies:

```bash
cd frontend
npm install
```

2. Confirm the frontend API URL in `frontend/.env`:

```text
VITE_API_URL=http://localhost:8000/api/v1
VITE_ENVIRONMENT=development
```

3. Start the frontend development server:

```bash
npm run dev
```

The frontend will typically be available at `http://localhost:5173`.

## Running both locally
1. Start the backend first.
2. Start the frontend second.
3. Open the frontend URL in your browser.

## Docker production build
Build the image with:

```bash
docker build -f Dockerfile.prod -t facerec-attendance .
```

Run the container:

```bash
docker run -p 80:80 facerec-attendance
```

## Notes
- Backend environment variables are loaded from `backend/.env`.
- The frontend reads `frontend/.env` to determine the API URL.
- If you use PostgreSQL on a different host or port, update `POSTGRES_HOST` and `POSTGRES_PORT` in `backend/.env`.
