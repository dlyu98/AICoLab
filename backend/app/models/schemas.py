"""Pydantic schemas for API I/O and agent responses."""
from enum import Enum
from pydantic import BaseModel, Field


class UrgencyLevel(str, Enum):
    self_care_monitor = "self-care / monitor"
    schedule_primary_care = "schedule primary care"
    urgent_care = "urgent care"
    emergency_care = "emergency care"


class ChatMessage(BaseModel):
    role: str = Field(description="system|user|assistant")
    content: str


class HealthRequest(BaseModel):
    session_id: str = Field(min_length=1)
    user_input: str = Field(min_length=1)
    context: dict[str, str] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    user_friendly_answer: str
    summary: str
    follow_up_questions: list[str] = Field(default_factory=list)
    possible_considerations: list[str] = Field(default_factory=list)
    urgency_level: UrgencyLevel
    red_flags_detected: list[str] = Field(default_factory=list)
    self_care_guidance: list[str] = Field(default_factory=list)
    when_to_seek_care: list[str] = Field(default_factory=list)
    disclaimer: str


class ApiResponse(BaseModel):
    session_id: str
    response: HealthResponse
    raw_model_output: str | None = None


class SafetyReviewResult(BaseModel):
    blocked: bool = False
    reasons: list[str] = Field(default_factory=list)
    red_flags_detected: list[str] = Field(default_factory=list)
