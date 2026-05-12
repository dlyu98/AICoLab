from datetime import date, datetime
from typing import Any


def parse_date(value: str) -> date:
    return datetime.fromisoformat(value).date()


def age_years(patient: dict[str, Any]) -> int | None:
    dob = patient.get("date_of_birth")
    if not dob:
        return None
    born = parse_date(dob)
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def abnormal_labs(patient: dict[str, Any]) -> list[dict[str, Any]]:
    return [lab for lab in patient.get("labs", []) if lab.get("flag") in {"high", "low", "critical"}]


def social_barriers(patient: dict[str, Any]) -> list[dict[str, Any]]:
    barriers = []
    for row in patient.get("social_determinants", []):
        if str(row.get("status", "")).lower() in {"barrier", "unstable", "positive"}:
            barriers.append(row)
    return barriers
