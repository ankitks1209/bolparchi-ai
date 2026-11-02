"""Short spoken text for Timbre. Keep replies to one or two sentences; detail goes on screen.
These are Hinglish templates to tune after hearing real Timbre output."""

from __future__ import annotations

from .validation import FIELDS, Validation
from .fields import FIELD_SPECS

_QUESTIONS = {
    "job_id": "Kaun si job ka update hai? Job number bataiye.",
    "diagnosis": "Kya kharabi mili? Thoda bataiye.",
    "status": "Kaam ho gaya ya abhi baaki hai?",
    "follow_up": "Aage kya karna hai? Customer se kab milna hai?",
}


def _clean(s: str) -> str:
    return s.rstrip(" .")


def question_for(v: Validation):
    """One question for the first problem, ordered by field. None when the record is complete."""
    pending = set(v.missing_fields) | set(v.invalid_fields)
    for f in FIELDS:
        if f not in pending:
            continue
        if v.invalid_fields.get(f) == "too_long":
            return f"{f.replace('_', ' ')} ko {FIELD_SPECS[f].max_length} characters tak chhota karein."
        if f == "quantity":
            if v.invalid_fields.get("quantity") == "quantity_without_part":
                return "Kaun sa part chahiye?"
            part = v.proposal.get("part_needed") or "part"
            return f"Kitne {part} chahiye?"
        return _QUESTIONS.get(f)
    return None


def readback_text(p: dict) -> str:
    parts = [f"Job {p['job_id']}: {_clean(p['diagnosis'])}."]
    parts.append("Kaam ho gaya." if p["status"] == "completed" else "Kaam abhi baaki hai.")
    if p.get("part_needed"):
        parts.append(f"{p['quantity']} {_clean(p['part_needed'])} chahiye.")
    if p.get("follow_up"):
        parts.append(f"Aage: {_clean(p['follow_up'])}.")
    parts.append("Sab sahi hai? Confirm and save dabayein, ya badlav bataiye.")
    return " ".join(parts)
