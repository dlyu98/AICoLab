from app.safety.rules import review_user_input, review_agent_output


def test_red_flag_detection_chest_pain():
    result = review_user_input("I have severe chest pain and trouble breathing")
    assert "chest_pain" in result.red_flags_detected


def test_output_blocklist_detects_diagnosis_language():
    result = review_agent_output("You definitely have pneumonia.")
    assert result.blocked
