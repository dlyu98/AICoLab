import pytest

from app.agent.service import HealthAgentService
from app.models.schemas import HealthRequest, UrgencyLevel


@pytest.mark.asyncio
async def test_agent_emergency_escalation_from_red_flag():
    service = HealthAgentService()
    request = HealthRequest(session_id="s1", user_input="I have chest pain and chest pressure", context={})
    response, _ = await service.handle(request)
    assert response.urgency_level == UrgencyLevel.emergency_care
    assert response.disclaimer


@pytest.mark.asyncio
async def test_agent_handles_partial_llm_payload_without_crashing():
    service = HealthAgentService()

    async def fake_generate_json(messages):
        return "raw", {
            "summary": "User reports sore throat and fatigue.",
            "urgency_level": "schedule primary care",
        }

    service.llm.generate_json = fake_generate_json
    request = HealthRequest(session_id="s2", user_input="I feel sick", context={})

    response, raw = await service.handle(request)

    assert raw == "raw"
    assert response.user_friendly_answer
    assert response.summary == "User reports sore throat and fatigue."
    assert response.urgency_level == UrgencyLevel.schedule_primary_care
