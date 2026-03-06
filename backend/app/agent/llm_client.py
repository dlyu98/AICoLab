"""OpenAI-compatible client abstraction with deterministic fallback."""
import json
import httpx

from app.config import get_settings
from app.models.schemas import HealthResponse, UrgencyLevel
from app.safety.rules import DISCLAIMER


class OpenAICompatibleClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_json(self, messages: list[dict[str, str]]) -> tuple[str, dict]:
        if not self.settings.openai_api_key:
            fallback = HealthResponse(
                user_friendly_answer="I can share general education, but I need more detail to give tailored guidance.",
                summary="General health support response generated without external LLM.",
                follow_up_questions=["How long have symptoms been present?", "Any fever, chest pain, or breathing difficulty?"],
                possible_considerations=["Mild viral illness", "Stress or sleep disruption"],
                urgency_level=UrgencyLevel.schedule_primary_care,
                red_flags_detected=[],
                self_care_guidance=["Hydrate", "Rest", "Monitor for worsening symptoms"],
                when_to_seek_care=["Seek urgent care for severe worsening", "Emergency care for chest pain or breathing distress"],
                disclaimer=DISCLAIMER,
            )
            return "fallback", fallback.model_dump()

        url = f"{self.settings.openai_base_url}/chat/completions"
        payload = {
            "model": self.settings.llm_model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_s) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            raw = response.json()["choices"][0]["message"]["content"]
            return raw, json.loads(raw)
