import re
from dataclasses import dataclass

@dataclass
class Redaction:
    type: str
    value: str
    replacement: str

PATTERNS = [
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("PHONE", re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),
    ("DATE", re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b", re.I)),
    ("MRN", re.compile(r"\b(?:MRN|Medical Record|Patient ID|ID)[:#\s-]*[A-Z0-9-]{4,}\b", re.I)),
    ("ADDRESS", re.compile(r"\b\d{1,5}\s+[A-Za-z0-9 .'-]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b", re.I)),
    ("NAME", re.compile(r"\b(?:Patient|Name|Pt)[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)\b")),
]


def redact_phi(text: str) -> tuple[str, list[Redaction]]:
    redactions: list[Redaction] = []
    redacted = text
    for label, pattern in PATTERNS:
        def repl(match: re.Match) -> str:
            value = match.group(1) if label == "NAME" and match.lastindex else match.group(0)
            token = f"[{label}_REDACTED]"
            redactions.append(Redaction(label, value, token))
            if label == "NAME" and match.lastindex:
                return match.group(0).replace(value, token)
            return token
        redacted = pattern.sub(repl, redacted)
    return redacted, redactions
