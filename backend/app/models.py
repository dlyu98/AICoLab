from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field

Confidence = Literal["low", "medium", "high"]
Priority = Literal["low", "medium", "high"]


class Evidence(BaseModel):
    source: str
    snippet: str
    field: str | None = None


class Finding(BaseModel):
    label: str
    category: str
    value: Any | None = None
    priority: Priority | None = None
    reason: str
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence = "medium"
    requires_human_review: bool = True


class Recommendation(BaseModel):
    action: str
    priority: Priority = "medium"
    reason: str
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence = "medium"
    requires_human_review: bool = True


class AgentRequest(BaseModel):
    patient_id: str | None = None
    patient: dict[str, Any] | None = None
    note: str | None = None
    question: str | None = None
    user_id: str = "demo-clinician"
    role: str = "clinician"


class AgentResponse(BaseModel):
    agent_name: str
    patient_id: str | None = None
    summary: str
    findings: list[Finding] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    risk_score: float | None = None
    risk_tier: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence = "medium"
    requires_human_review: bool = True
    safety_notice: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    structured_output: dict[str, Any] = Field(default_factory=dict)


class RedactRequest(BaseModel):
    text: str


class RedactResponse(BaseModel):
    redacted_text: str
    redactions: list[dict[str, str]]
    safety_notice: str


class AuditLog(BaseModel):
    timestamp: datetime
    request_id: str
    user_id: str
    role: str
    action: str
    patient_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
