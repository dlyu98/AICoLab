from typing import Any
from backend.app.agents.rules import abnormal_labs, age_years, social_barriers
from backend.app.models import Evidence, Finding, Recommendation

class ReadmissionRiskEngine:
    """Transparent baseline rule engine; replace score() with an ML adapter later."""

    def score(self, patient: dict[str, Any]) -> tuple[float, str, list[Finding], list[Recommendation]]:
        points = 0
        findings: list[Finding] = []

        def add(label: str, pts: int, reason: str, source: str, snippet: str, priority: str = "medium"):
            nonlocal points
            points += pts
            findings.append(Finding(label=label, category="readmission_risk_driver", value=pts, priority=priority, reason=reason, evidence=[Evidence(source=source, snippet=snippet)], confidence="medium"))

        age = age_years(patient)
        if age and age > 65:
            add("Age over 65", 10, "Older age is associated with higher post-discharge complexity.", "patient.date_of_birth", f"Calculated age {age}", "low")
        admissions = [e for e in patient.get("encounters", []) if e.get("type") == "inpatient"]
        if len(admissions) >= 1:
            add("Recent hospitalization", 20, "Recent inpatient stay increases 30-day readmission risk.", "encounters", admissions[-1].get("reason", "inpatient encounter"), "high")
        ed_visits = [e for e in patient.get("encounters", []) if e.get("type") == "emergency"]
        if len(ed_visits) >= 2:
            add("Frequent ED utilization", 15, "Two or more ED visits indicate unstable symptoms or access barriers.", "encounters", f"{len(ed_visits)} ED visits recorded", "medium")
        if len(patient.get("problems", [])) >= 4:
            add("High comorbidity count", 15, "Multiple active problems increase care complexity.", "patient.problems", ", ".join(patient.get("problems", [])), "medium")
        for lab in abnormal_labs(patient):
            if lab.get("code") in {"CREAT", "HGB"}:
                add(f"Abnormal {lab.get('name')}", 10, "Abnormal renal function or anemia can increase risk.", "labs", f"{lab.get('name')} {lab.get('value')} {lab.get('unit')} ({lab.get('flag')})", "medium")
        if len(patient.get("medications", [])) >= 5:
            add("Polypharmacy", 10, "Five or more active medications may increase adverse event risk.", "medications", f"{len(patient.get('medications', []))} medications", "medium")
        for barrier in social_barriers(patient):
            add(f"Social barrier: {barrier.get('domain')}", 10, "Social needs may impede follow-up or medication access.", "social_determinants", barrier.get("detail", barrier.get("domain", "barrier")), "medium")
        if any("missed" in str(e.get("status", "")).lower() for e in patient.get("encounters", [])):
            add("Missed follow-up", 10, "Missed appointments can leave abnormal results unresolved.", "encounters", "Missed follow-up status present", "high")

        risk_score = min(points, 100)
        tier = "high" if risk_score >= 60 else "medium" if risk_score >= 30 else "low"
        recs = [
            Recommendation(action="Care manager review within 1 business day" if tier == "high" else "Schedule routine care-management outreach", priority="high" if tier == "high" else "medium", reason="Human review is required before clinical decisions or patient outreach.", confidence="medium"),
            Recommendation(action="Verify follow-up appointment, medication access, and transportation plan", priority="medium", reason="Targets modifiable readmission drivers identified by the rule engine.", confidence="medium"),
        ]
        return float(risk_score), tier, findings, recs
