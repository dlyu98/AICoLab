import logging
import time
from collections import defaultdict, deque
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.agents.clinical import care_gaps, note_extraction, patient_summary, readmission_risk
from backend.app.agents.operations import ask_operations
from backend.app.core.constants import SAFETY_NOTICE
from backend.app.models import AgentRequest, RedactRequest, RedactResponse
from backend.app.security.phi import redact_phi
from backend.app.services.audit import read_audit, write_audit
from backend.app.services.data_loader import get_patient, list_patients
from backend.app.core.config import get_settings

_RATE_BUCKETS: dict[str, deque[float]] = defaultdict(deque)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("carebridge")
app = FastAPI(title="CareBridge AI Agent API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def tracing(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    start = time.time()
    client_id = request.headers.get("x-api-client", "demo-client")
    bucket = _RATE_BUCKETS[client_id]
    now = time.time()
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= int(get_settings().rate_limit_per_minute):
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded", "request_id": request_id})
    bucket.append(now)
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception("Unhandled request error", extra={"request_id": request_id})
        return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request_id})
    response.headers["x-request-id"] = request_id
    logger.info("request", extra={"request_id": request_id, "path": request.url.path, "duration_ms": int((time.time() - start) * 1000)})
    return response

@app.get("/health")
def health():
    return {"status": "ok", "service": "CareBridge AI Agent", "safety_notice": SAFETY_NOTICE}

@app.get("/patients")
def patients():
    write_audit("list_patients", "demo-user", "clinician")
    return list_patients()

@app.get("/patients/{patient_id}")
def patient(patient_id: str):
    bundle = get_patient(patient_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Synthetic patient not found")
    write_audit("get_patient", "demo-user", "clinician", patient_id)
    return bundle


def _bundle(req: AgentRequest):
    if req.patient:
        return req.patient
    if not req.patient_id:
        raise HTTPException(status_code=422, detail="patient_id or patient is required")
    bundle = get_patient(req.patient_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Synthetic patient not found")
    return bundle

@app.post("/agent/patient-summary")
def patient_summary_endpoint(req: AgentRequest):
    res = patient_summary(_bundle(req), req.note)
    write_audit("agent.patient_summary", req.user_id, req.role, res.patient_id, {"findings": len(res.findings)})
    return res

@app.post("/agent/care-gaps")
def care_gaps_endpoint(req: AgentRequest):
    res = care_gaps(_bundle(req))
    write_audit("agent.care_gaps", req.user_id, req.role, res.patient_id, {"findings": len(res.findings)})
    return res

@app.post("/agent/readmission-risk")
def readmission_endpoint(req: AgentRequest):
    res = readmission_risk(_bundle(req))
    write_audit("agent.readmission_risk", req.user_id, req.role, res.patient_id, {"risk_score": res.risk_score, "risk_tier": res.risk_tier})
    return res

@app.post("/agent/note-extraction")
def note_extraction_endpoint(req: AgentRequest):
    if not req.note:
        raise HTTPException(status_code=422, detail="note is required")
    res = note_extraction(req.note, req.patient_id)
    write_audit("agent.note_extraction", req.user_id, req.role, req.patient_id, {"findings": len(res.findings)})
    return res

@app.post("/agent/ask")
def ask_endpoint(req: AgentRequest):
    if not req.question:
        raise HTTPException(status_code=422, detail="question is required")
    res = ask_operations(req.question)
    write_audit("agent.ask", req.user_id, req.role, req.patient_id, {"question_length": len(req.question)})
    return res

@app.get("/audit-logs")
def audit_logs(limit: int = 100):
    return read_audit(limit)

@app.post("/redact-phi")
def redact_endpoint(req: RedactRequest):
    redacted, redactions = redact_phi(req.text)
    write_audit("redact_phi", "demo-user", "clinician", metadata={"redaction_count": len(redactions)})
    return RedactResponse(redacted_text=redacted, redactions=[r.__dict__ for r in redactions], safety_notice="Conservative regex redaction for demos only; validate before PHI use.")
