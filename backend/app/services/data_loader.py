import json
from pathlib import Path
from typing import Any
from backend.app.core.config import get_settings


def _base() -> Path:
    return Path(get_settings().synthetic_data_dir)


def load_json(name: str) -> list[dict[str, Any]]:
    with (_base() / name).open() as f:
        return json.load(f)


def list_patients() -> list[dict[str, Any]]:
    return load_json("patients.json")


def get_patient(patient_id: str) -> dict[str, Any] | None:
    patients = {p["patient_id"]: p for p in list_patients()}
    patient = patients.get(patient_id)
    if not patient:
        return None
    bundle = dict(patient)
    for name, key in [
        ("encounters.json", "encounters"),
        ("labs.json", "labs"),
        ("medications.json", "medications"),
        ("notes.json", "notes"),
        ("social_determinants.json", "social_determinants"),
    ]:
        bundle[key] = [r for r in load_json(name) if r.get("patient_id") == patient_id]
    return bundle


def dataset_profile() -> dict[str, Any]:
    return {
        "patients": len(list_patients()),
        "encounters": len(load_json("encounters.json")),
        "labs": len(load_json("labs.json")),
        "medications": len(load_json("medications.json")),
        "notes": len(load_json("notes.json")),
        "social_determinants": len(load_json("social_determinants.json")),
        "note": "Synthetic demonstration data only; no real PHI is included.",
    }
