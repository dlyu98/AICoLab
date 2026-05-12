import re
from typing import Any
from backend.app.agents.rules import abnormal_labs, social_barriers
from backend.app.core.constants import EMERGENCY_NOTICE, SAFETY_NOTICE
from backend.app.models import AgentResponse, Evidence, Finding, Recommendation
from backend.app.security.prompt_guard import sanitize_clinical_text
from backend.app.security.phi import redact_phi
from backend.app.agents.readmission import ReadmissionRiskEngine

EMERGENCY_TERMS = ["chest pain", "stroke", "suicidal", "severe shortness of breath", "anaphylaxis", "sepsis"]


def _notice(note: str = "") -> str:
    if any(term in note.lower() for term in EMERGENCY_TERMS):
        return SAFETY_NOTICE + " " + EMERGENCY_NOTICE
    return SAFETY_NOTICE


def patient_summary(patient: dict[str, Any], note: str | None = None) -> AgentResponse:
    safe_note, flags = sanitize_clinical_text(note)
    redacted_note, _ = redact_phi(safe_note)
    labs = abnormal_labs(patient)
    barriers = social_barriers(patient)
    med_names = [m["name"] for m in patient.get("medications", [])]
    summary = (
        f"Synthetic patient {patient['patient_id']} has active problems: {', '.join(patient.get('problems', []) or ['none documented'])}. "
        f"Active medications include {', '.join(med_names) or 'none documented'}. "
        f"Abnormal labs: {', '.join(l['name'] for l in labs) or 'none documented'}. "
        f"Social barriers: {', '.join(b['domain'] for b in barriers) or 'none documented'}."
    )
    findings = [Finding(label=p, category="active_problem", reason="Problem listed in structured synthetic patient record.", evidence=[Evidence(source="patient.problems", snippet=p)], confidence="high") for p in patient.get("problems", [])]
    findings += [Finding(label=lab["name"], category="abnormal_lab", value=lab.get("value"), priority="high" if lab.get("flag") == "critical" else "medium", reason="Lab is flagged outside reference range.", evidence=[Evidence(source="labs", snippet=f"{lab['name']} {lab['value']} {lab['unit']} {lab['flag']}")], confidence="high") for lab in labs]
    if flags:
        findings.append(Finding(label="Prompt injection attempt removed", category="security", priority="high", reason="Clinical note contained text resembling instructions to the AI rather than patient data.", evidence=[Evidence(source="note", snippet="; ".join(flags))], confidence="high"))
    recommendations = [Recommendation(action="Review abnormal labs and documented follow-up needs with responsible clinician.", priority="medium", reason="Agent suggestions require human validation before action.", evidence=[Evidence(source="labs", snippet=str(len(labs)) + " abnormal labs")], confidence="medium")]
    return AgentResponse(agent_name="Patient Summary Agent", patient_id=patient["patient_id"], summary=summary, findings=findings, recommendations=recommendations, evidence=[Evidence(source="clinical_note_redacted", snippet=redacted_note[:240])], confidence="medium", safety_notice=_notice(safe_note), structured_output={"active_problems": patient.get("problems", []), "medications": med_names, "abnormal_labs": labs, "social_risk_factors": barriers, "prompt_injection_flags": flags})


def care_gaps(patient: dict[str, Any]) -> AgentResponse:
    findings: list[Finding] = []
    recs: list[Recommendation] = []
    for lab in abnormal_labs(patient):
        priority = "high" if lab.get("flag") == "critical" else "medium"
        evidence = [Evidence(source="labs", snippet=f"{lab['date']} {lab['name']} {lab['value']} {lab['unit']} {lab['flag']}")]
        findings.append(Finding(label=f"Review abnormal {lab['name']}", category="abnormal_result_follow_up", priority=priority, reason="Abnormal results should be reviewed by the care team.", evidence=evidence, confidence="high"))
        recs.append(Recommendation(action=f"Route {lab['name']} result to clinician for review", priority=priority, reason="Human review required for abnormal result follow-up.", evidence=evidence, confidence="high"))
    if not any(e.get("type") == "primary_care" for e in patient.get("encounters", [])):
        findings.append(Finding(label="No primary care follow-up documented", category="missing_follow_up", priority="medium", reason="Synthetic record lacks a primary care follow-up encounter.", evidence=[Evidence(source="encounters", snippet="No primary_care encounter found")], confidence="medium"))
    for barrier in social_barriers(patient):
        findings.append(Finding(label=f"Potential barrier: {barrier['domain']}", category="social_barrier", priority="medium", reason="Documented social need may interfere with care plan completion.", evidence=[Evidence(source="social_determinants", snippet=barrier.get("detail", "barrier"))], confidence="medium"))
    summary = f"Identified {len(findings)} care-gap or follow-up items requiring human review."
    return AgentResponse(agent_name="Care Gap Agent", patient_id=patient["patient_id"], summary=summary, findings=findings, recommendations=recs, evidence=[Evidence(source="synthetic_bundle", snippet="labs, encounters, medications, social determinants")], safety_notice=SAFETY_NOTICE, structured_output={"care_gap_count": len(findings)})


def readmission_risk(patient: dict[str, Any]) -> AgentResponse:
    score, tier, findings, recs = ReadmissionRiskEngine().score(patient)
    return AgentResponse(agent_name="Readmission Risk Assistant", patient_id=patient["patient_id"], summary=f"Transparent rule-based 30-day readmission risk estimate is {tier} ({score:.0f}/100).", findings=findings, recommendations=recs, risk_score=score, risk_tier=tier, evidence=[Evidence(source="rule_engine", snippet="Age, utilization, comorbidities, labs, medications, SDOH")], confidence="medium", safety_notice=SAFETY_NOTICE, structured_output={"model_type": "rule_based_baseline", "key_drivers": [f.label for f in findings]})


def note_extraction(note: str, patient_id: str | None = None) -> AgentResponse:
    safe_note, flags = sanitize_clinical_text(note)
    redacted, _ = redact_phi(safe_note)
    categories = {
        "diagnoses": r"\b(?:diabetes|heart failure|copd|hypertension|pneumonia|asthma)\b",
        "procedures": r"\b(?:ct|mri|x-ray|biopsy|colonoscopy|echo|ekg)\b",
        "symptoms": r"\b(?:pain|dyspnea|fever|cough|nausea|fatigue|edema)\b",
        "follow_up": r"\b(?:follow[- ]up|return|refer|appointment|recheck)\b[^.]*",
    }
    structured: dict[str, list[str]] = {}
    findings: list[Finding] = []
    for cat, pattern in categories.items():
        matches = sorted(set(m.group(0) for m in re.finditer(pattern, redacted, re.I)))
        structured[cat] = matches
        for match in matches:
            findings.append(Finding(label=match, category=cat, reason="Term or phrase extracted from supplied note text.", evidence=[Evidence(source="note", snippet=match)], confidence="medium"))
    if flags:
        structured["prompt_injection_flags"] = flags
        findings.append(Finding(label="Prompt injection attempt removed", category="security", priority="high", reason="Note contained instruction-like text that was treated as untrusted data.", evidence=[Evidence(source="note", snippet="; ".join(flags))], confidence="high"))
    return AgentResponse(agent_name="Clinical Note Intelligence", patient_id=patient_id, summary=f"Extracted {len(findings)} structured findings from the redacted note.", findings=findings, recommendations=[Recommendation(action="Clinician should verify extracted note facts against source documentation.", priority="medium", reason="Regex/local extraction can miss context and negation.", confidence="medium")], evidence=[Evidence(source="redacted_note", snippet=redacted[:240])], confidence="medium", safety_notice=_notice(redacted), structured_output=structured)
