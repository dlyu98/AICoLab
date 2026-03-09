"""Configurable safety rule checks for user input and model output."""
from dataclasses import dataclass
from typing import Iterable

from app.models.schemas import SafetyReviewResult


DISCLAIMER = (
    "This tool provides informational support only and is not a substitute for "
    "professional medical advice, diagnosis, or treatment. If symptoms are severe, "
    "worsening, or you feel unsafe, seek immediate care."
)


@dataclass(frozen=True)
class SafetyRule:
    name: str
    keywords: tuple[str, ...]


RED_FLAG_RULES: tuple[SafetyRule, ...] = (
    SafetyRule("chest_pain", ("chest pain", "chest pressure")),
    SafetyRule("severe_shortness_of_breath", ("can't breathe", "severe shortness of breath", "gasping")),
    SafetyRule("stroke_like_symptoms", ("face droop", "slurred speech", "one-sided weakness")),
    SafetyRule("suicidal_ideation", ("suicidal", "want to die", "kill myself", "self harm")),
    SafetyRule("severe_allergic_reaction", ("anaphylaxis", "throat closing", "swollen tongue")),
    SafetyRule("uncontrolled_bleeding", ("uncontrolled bleeding", "won't stop bleeding")),
)

OUTPUT_BLOCKLIST: tuple[SafetyRule, ...] = (
    SafetyRule("certain_diagnosis", ("you definitely have", "this confirms you have")),
    SafetyRule("prescription_instruction", ("take 500mg", "start this dosage", "prescribe")),
    SafetyRule("avoid_doctor", ("do not see a doctor", "ignore your clinician")),
)


def _matched_rules(text: str, rules: Iterable[SafetyRule]) -> list[str]:
    lower = text.lower()
    matches: list[str] = []
    for rule in rules:
        if any(keyword in lower for keyword in rule.keywords):
            matches.append(rule.name)
    return matches


def review_user_input(user_input: str) -> SafetyReviewResult:
    red_flags = _matched_rules(user_input, RED_FLAG_RULES)
    reasons = ["red_flag_detected"] if red_flags else []
    return SafetyReviewResult(blocked=False, reasons=reasons, red_flags_detected=red_flags)


def review_agent_output(output_text: str) -> SafetyReviewResult:
    risky = _matched_rules(output_text, OUTPUT_BLOCKLIST)
    return SafetyReviewResult(blocked=bool(risky), reasons=risky, red_flags_detected=[])
