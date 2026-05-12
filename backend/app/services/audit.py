import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from backend.app.core.config import get_settings


def write_audit(action: str, user_id: str, role: str, patient_id: str | None = None, metadata: dict | None = None, request_id: str | None = None) -> str:
    rid = request_id or str(uuid4())
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": rid,
        "user_id": user_id,
        "role": role,
        "action": action,
        "patient_id": patient_id,
        "metadata": metadata or {},
    }
    path = Path(get_settings().audit_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(event) + "\n")
    return rid


def read_audit(limit: int = 100) -> list[dict]:
    path = Path(get_settings().audit_log_path)
    if not path.exists():
        return []
    lines = path.read_text().splitlines()[-limit:]
    return [json.loads(line) for line in lines if line.strip()]
