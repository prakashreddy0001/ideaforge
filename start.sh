#!/bin/bash

# Start IdeaForge backend and frontend concurrently

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

trap 'kill 0' EXIT

echo "Starting IdeaForge..."

# Backend (FastAPI)
echo "Starting backend on http://localhost:8000"
if [ ! -d "$ROOT_DIR/backend/venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv "$ROOT_DIR/backend/venv"
  "$ROOT_DIR/backend/venv/bin/pip" install -r "$ROOT_DIR/backend/requirements.txt"
fi
(cd "$ROOT_DIR/backend" && "$ROOT_DIR/backend/venv/bin/uvicorn" app.main:app --reload --port 8000) &

# Frontend (Next.js)
echo "Starting frontend on http://localhost:3000"
cd "$ROOT_DIR/frontend" && npm run dev &

wait
