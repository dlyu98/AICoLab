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
