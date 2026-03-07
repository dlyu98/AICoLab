# Health AI Agent MVP

Production-quality MVP for a healthcare-focused AI agent with safety-first triage-style guidance, educational Q&A, structured JSON output, and a minimal frontend.

> **Important:** Informational support only. This tool is **not** a substitute for professional medical advice, diagnosis, or treatment.

## Features
- Natural language health Q&A with conservative wording.
- Symptom intake + triage-style urgency estimation.
- Medication/condition education scaffolding.
- Human-readable + structured JSON response schema.
- Safety guardrails for red flags and risky outputs.
- In-memory session conversation memory.
- FastAPI backend + React frontend.
- Docker and docker-compose support.
- Unit tests (safety, schema, workflow).

## Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agent/
│   │   ├── models/
│   │   ├── prompts/
│   │   ├── safety/
│   │   └── utils/
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
├── examples/
├── frontend/
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── LICENSE
```

## Architecture
See [`docs/architecture.md`](docs/architecture.md).

## Environment Variables
Copy `.env.example` to `.env` and edit as needed:

- `OPENAI_API_KEY`: Required for live LLM responses. If omitted, deterministic fallback response is used.
- `OPENAI_BASE_URL`: OpenAI-compatible endpoint.
- `LLM_MODEL`: Model name.
- `REQUEST_TIMEOUT_S`: API timeout.
- `VITE_API_URL`: Frontend backend endpoint.

## Local Setup

### 1) Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

### 3) Run tests
```bash
pytest -q
```

## Quick Smoke Test (Recommended)
Run from the **repository root** (`AICoLab/`).

### macOS/Linux (bash)
```bash
bash scripts/smoke_test.sh
```

### Windows (PowerShell)
Open **PowerShell** in the repository root, then run:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```

What it does:
1. Creates/activates `.venv`
2. Installs backend dependencies
3. Runs `pytest -q`
4. Starts backend
5. Calls `/health`
6. Calls `/v1/agent/respond` with `examples/sample_request.json`

## Docker
```bash
docker compose up --build
```

## API Example
Use `examples/sample_request.json` and `examples/curl_example.sh`.

## Prompting Strategy
- Main assistant system prompt: conservative health educator behavior.
- Triage prompt: urgency + follow-up questioning.
- Safety review prompt: blocks unsafe certainty/prescription language.

## Screenshots
- Add frontend screenshots here after deployment testing:
  - `docs/images/ui-home.png`
  - `docs/images/ui-response.png`

## Future Roadmap
- Persistent memory (Redis/Postgres).
- User auth and audit logs.
- Clinical content retrieval with citations.
- Expanded medication safety knowledge base.
- i18n and accessibility enhancements.
- Deployment templates (Fly.io/Render/Kubernetes).

## Safety Disclaimer
This project provides general informational support only and is not medical advice. If you have severe symptoms (e.g., chest pain, severe trouble breathing, stroke-like symptoms, suicidal thoughts, severe allergic reaction, uncontrolled bleeding), seek emergency care immediately.

## GitHub Publish Commands
```bash
git init
git add .
git commit -m "feat: initial health ai agent mvp"
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```
