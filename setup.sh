#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ ! -d "backend/.venv" ]; then
  echo "Creating Python virtual environment for backend..."
  python3 -m venv backend/.venv
fi

echo "Activating backend virtual environment..."
source backend/.venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Setup complete."
echo "To run the backend: source backend/.venv/bin/activate && cd backend && uvicorn main:app --reload --host 127.0.0.1 --port 8000"
echo "To run the frontend: cd frontend && npm run dev"
