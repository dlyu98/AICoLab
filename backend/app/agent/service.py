"""Core health agent orchestration service."""
from app.agent.llm_client import OpenAICompatibleClient
from app.models.schemas import ChatMessage, HealthRequest, HealthResponse, UrgencyLevel
from app.prompts.templates import MAIN_SYSTEM_PROMPT, TRIAGE_PROMPT
from app.safety.rules import DISCLAIMER, review_agent_output, review_user_input
from app.utils.memory import SessionMemoryStore


class HealthAgentService:
    def __init__(self, memory_store: SessionMemoryStore | None = None) -> None:
        self.memory = memory_store or SessionMemoryStore()
        self.llm = OpenAICompatibleClient()

    @staticmethod
    def _normalize_payload(payload: dict) -> dict:
        """Best-effort normalization so partial LLM JSON never crashes API validation."""
        normalized = dict(payload)
        normalized.setdefault(
            "user_friendly_answer",
            "I can share general health information, but I need a bit more detail to provide tailored guidance.",
        )
        normalized.setdefault("summary", "General health guidance based on the provided input.")
        normalized.setdefault("follow_up_questions", [])
        normalized.setdefault("possible_considerations", [])
        normalized.setdefault("urgency_level", UrgencyLevel.schedule_primary_care)
        normalized.setdefault("red_flags_detected", [])
        normalized.setdefault("self_care_guidance", [])
        normalized.setdefault("when_to_seek_care", [])
        return normalized

    async def handle(self, request: HealthRequest) -> tuple[HealthResponse, str | None]:
        user_safety = review_user_input(request.user_input)
        history = self.memory.get(request.session_id)

        messages = [
            {"role": "system", "content": MAIN_SYSTEM_PROMPT},
            {"role": "system", "content": TRIAGE_PROMPT},
        ]
        messages.extend([m.model_dump() for m in history])
        messages.append({"role": "user", "content": request.user_input})

        raw_output, payload = await self.llm.generate_json(messages)
        payload = self._normalize_payload(payload)
        payload["red_flags_detected"] = sorted(
            set(payload.get("red_flags_detected", []) + user_safety.red_flags_detected)
        )

        if payload["red_flags_detected"]:
            payload["urgency_level"] = UrgencyLevel.emergency_care
            payload["when_to_seek_care"] = list(
                {
                    *payload.get("when_to_seek_care", []),
                    "Call emergency services now for life-threatening symptoms.",
                }
            )

        payload["disclaimer"] = DISCLAIMER
        response = HealthResponse.model_validate(payload)

        output_safety = review_agent_output(response.user_friendly_answer)
        if output_safety.blocked:
            response.user_friendly_answer = (
                "I can't safely provide that level of certainty. I can share general information and suggest seeing a clinician."
            )
            response.disclaimer = DISCLAIMER

        self.memory.append(request.session_id, ChatMessage(role="user", content=request.user_input))
        self.memory.append(request.session_id, ChatMessage(role="assistant", content=response.user_friendly_answer))
        return response, raw_output
