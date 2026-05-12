from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_patients_load():
    res = client.get("/patients")
    assert res.status_code == 200
    assert len(res.json()) >= 3


def test_patient_summary_endpoint():
    res = client.post("/agent/patient-summary", json={"patient_id": "SYN-1001", "note": "Follow-up with cardiology."})
    assert res.status_code == 200
    body = res.json()
    assert body["agent_name"] == "Patient Summary Agent"
    assert body["findings"]


def test_care_gaps_endpoint():
    res = client.post("/agent/care-gaps", json={"patient_id": "SYN-1001"})
    assert res.status_code == 200
    assert res.json()["requires_human_review"] is True


def test_readmission_endpoint():
    res = client.post("/agent/readmission-risk", json={"patient_id": "SYN-1001"})
    assert res.status_code == 200
    assert res.json()["risk_tier"] in {"low", "medium", "high"}


def test_note_extraction_endpoint_validation():
    res = client.post("/agent/note-extraction", json={"patient_id": "SYN-1001"})
    assert res.status_code == 422


def test_note_extraction_endpoint():
    res = client.post("/agent/note-extraction", json={"patient_id": "SYN-1001", "note": "CT showed edema. Follow-up appointment in one week."})
    assert res.status_code == 200
    assert "follow_up" in res.json()["structured_output"]


def test_operations_ask_endpoint():
    res = client.post("/agent/ask", json={"question": "Suggest SQL for readmission dashboard"})
    assert res.status_code == 200
    assert "suggested_sql" in res.json()["structured_output"]


def test_redact_phi_endpoint():
    res = client.post("/redact-phi", json={"text": "Name: Jane Doe phone 555-123-4567"})
    assert res.status_code == 200
    assert "PHONE_REDACTED" in res.json()["redacted_text"]
