#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d ".venv" ]]; then
  echo "[1/6] Creating Python virtual environment (.venv)..."
  python -m venv .venv
fi

echo "[2/6] Activating virtual environment..."
# shellcheck disable=SC1091
source .venv/bin/activate

echo "[3/6] Installing backend dependencies..."
pip install -r backend/requirements.txt

echo "[4/6] Running tests..."
pytest -q

echo "[5/6] Starting backend server for smoke checks..."
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 > /tmp/health_ai_backend.log 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" >/dev/null 2>&1 || true' EXIT

sleep 2

echo "[6/6] Checking endpoints..."
curl -fsS http://127.0.0.1:8000/health

echo
curl -fsS -X POST http://127.0.0.1:8000/v1/agent/respond \
  -H "Content-Type: application/json" \
  -d @examples/sample_request.json

echo
printf "\nSmoke test complete.\n"
