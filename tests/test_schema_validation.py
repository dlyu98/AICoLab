from app.models.schemas import HealthResponse, UrgencyLevel


def test_health_response_schema_validation():
    response = HealthResponse(
        user_friendly_answer="Test",
        summary="Summary",
        follow_up_questions=[],
        possible_considerations=[],
        urgency_level=UrgencyLevel.self_care_monitor,
        red_flags_detected=[],
        self_care_guidance=[],
        when_to_seek_care=[],
        disclaimer="info",
    )
    assert response.urgency_level == UrgencyLevel.self_care_monitor
