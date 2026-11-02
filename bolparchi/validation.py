"""Deterministic validation for BolParchi job updates.

The extraction model only PROPOSES values. Everything here is plain code:
normalisation, conditional required-field rules, allowed values, and the
content hash that identifies exactly what a user is confirming.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass

from .fields import FIELD_SPECS, MAX_MESSAGE_LENGTH

FIELDS = tuple(FIELD_SPECS)
ALLOWED_STATUS = FIELD_SPECS["status"].choices
MAX_QUANTITY = FIELD_SPECS["quantity"].maximum

# Spoken Hindi/Hinglish number words (romanised). Extend after testing real ASR output.
HINDI_NUMBERS = {
    "ek": 1,
    "do": 2,
    "teen": 3,
    "char": 4,
    "chaar": 4,
    "paanch": 5,
    "panch": 5,
    "chhe": 6,
    "che": 6,
    "saat": 7,
    "aath": 8,
    "nau": 9,
    "das": 10,
}

_JOB_PREFIX = re.compile(r"(?:job\s*)?#?(\d{1,6})", re.I)


def _text(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Text fields must be strings or null.")
    s = " ".join(value.split())
    return s or None


def _quantity(value):
    """Coerce to int where unambiguous; otherwise return the raw value so validation flags it."""
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    s = _text(value)
    if s is None:
        return None
    low = s.lower()
    if low.isdecimal():
        return int(low)
    return HINDI_NUMBERS.get(low, s)


def normalize(raw) -> dict:
    if raw is None:
        raw = {}
    if not isinstance(raw, Mapping):
        raise ValueError("The proposal must be a JSON object.")
    out = {f: None for f in FIELDS}
    job_value = raw.get("job_id")
    if isinstance(job_value, int) and not isinstance(job_value, bool):
        job_value = str(job_value)
    job = _text(job_value)
    if job:
        m = _JOB_PREFIX.fullmatch(job)
        out["job_id"] = m.group(1) if m else job
    out["diagnosis"] = _text(raw.get("diagnosis"))
    status = _text(raw.get("status"))
    out["status"] = status.lower() if status else None
    out["part_needed"] = _text(raw.get("part_needed"))
    out["quantity"] = _quantity(raw.get("quantity"))
    out["follow_up"] = _text(raw.get("follow_up"))
    return out


def _field_error(field, value):
    """Check a normalized value against the shared, unconditional field rules."""
    spec = FIELD_SPECS[field]
    if spec.json_type == "integer":
        if type(value) is not int:
            return "invalid_quantity"
        if spec.minimum is not None and value < spec.minimum:
            return "invalid_quantity"
        if spec.maximum is not None and value > spec.maximum:
            return "invalid_quantity"
    elif not isinstance(value, str):
        raise ValueError("Text fields must be strings or null.")
    if spec.max_length is not None and len(value) > spec.max_length:
        return "too_long"
    if spec.choices and value not in spec.choices:
        return "not_allowed"
    if spec.pattern and not re.fullmatch(spec.pattern, value):
        return "not_a_job_number"
    return None


@dataclass(frozen=True)
class Validation:
    proposal: dict
    missing_fields: tuple
    invalid_fields: dict

    @property
    def complete(self) -> bool:
        return not self.missing_fields and not self.invalid_fields


def validate(raw) -> Validation:
    """Compute missing/invalid fields in code. Rules are conditional:
    - job_id, diagnosis, status always required
    - a requested part requires a valid quantity; a quantity without a part is invalid
    - a pending job requires a follow-up; a completed job needs no part or follow-up
    """
    p = normalize(raw)
    missing: list[str] = []
    invalid: dict[str, str] = {}

    for field, spec in FIELD_SPECS.items():
        value = p[field]
        if value is None:
            if spec.required:
                missing.append(field)
        else:
            error = _field_error(field, value)
            if error:
                invalid[field] = error

    q = p["quantity"]
    if p["part_needed"] is not None:
        if q is None:
            missing.append("quantity")
    elif q is not None:
        invalid["quantity"] = "quantity_without_part"

    if p["status"] == "pending" and p["follow_up"] is None:
        missing.append("follow_up")

    return Validation(p, tuple(missing), invalid)


def proposal_hash(proposal) -> str:
    """Stable hash of the normalised content. Identifies WHAT is confirmed, not WHETHER it was saved."""
    canon = json.dumps(normalize(proposal), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _check_patch_structure(changes, clear):
    if not isinstance(changes, Mapping):
        raise ValueError("Changes must be an object.")
    if not isinstance(clear, (list, tuple)):
        raise ValueError("Clear must be a list of field names.")
    for key in (*changes, *clear):
        if not isinstance(key, str) or key not in FIELDS:
            raise ValueError(f"unknown field: {key}")
        if not FIELD_SPECS[key].patchable:
            raise ValueError("The selected job cannot be changed or cleared.")
    if set(changes).intersection(clear):
        raise ValueError("A field cannot be set and cleared in the same patch.")
    if "part_needed" in clear and "quantity" in changes:
        raise ValueError("Cannot set quantity while clearing the requested part.")


def apply_changes(current, changes, clear=()) -> dict:
    """Apply a patch without changing the selected job or mutating the inputs.

    Legacy callers retain quantity normalization and None-as-no-change. Model
    output must pass validate_extraction, which requires strict JSON types.
    """
    if changes is None:
        changes = {}
    _check_patch_structure(changes, clear)
    merged = dict(normalize(current))
    for key, value in changes.items():
        if value is not None:
            merged[key] = value
    for key in clear:
        merged[key] = None
    if "part_needed" in clear:
        merged["quantity"] = None
    return normalize(merged)


def validate_message(message) -> str:
    """Preserve the transcript; reject unusable input before any provider call."""
    if not isinstance(message, str) or not message.strip():
        raise ValueError("A nonempty text message is required.")
    if len(message) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Keep the message within {MAX_MESSAGE_LENGTH} characters.")
    return message


def validate_extraction(raw) -> dict:
    """Validate untrusted model output independently of provider schema guarantees."""
    required = {"set", "clear", "spoken_job_id", "needs_clarification"}
    if not isinstance(raw, Mapping) or set(raw) != required:
        raise ValueError("Extraction must contain exactly the four contract fields.")
    if type(raw["needs_clarification"]) is not bool:
        raise ValueError("needs_clarification must be a boolean.")
    if not isinstance(raw["clear"], list):
        raise ValueError("Clear must be an array.")
    _check_patch_structure(raw["set"], raw["clear"])
    changes = {}
    for name, value in raw["set"].items():
        spec = FIELD_SPECS[name]
        if spec.json_type == "integer":
            if type(value) is not int:
                raise ValueError(f"{name} must be an integer.")
        else:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be nonempty text; use clear to remove it.")
            value = _text(value)
        error = _field_error(name, value)
        if error:
            raise ValueError(f"Invalid {name}: {error}.")
        changes[name] = value
    spoken = raw["spoken_job_id"]
    if spoken is not None and (not isinstance(spoken, str) or _field_error("job_id", spoken)):
        raise ValueError("spoken_job_id must be a job number string or null.")
    return {
        "set": changes,
        "clear": list(raw["clear"]),
        "spoken_job_id": spoken,
        "needs_clarification": raw["needs_clarification"],
    }


class ClarificationRequired(ValueError):
    """The whole message is held; no field from it may be applied."""


class SpokenJobMismatch(ValueError):
    """The whole patch is held until the application resolves the job mismatch."""


def apply_extraction(current, raw) -> dict:
    """Pure application boundary; future orchestration must also guard draft/turn state."""
    patch = validate_extraction(raw)
    if patch["needs_clarification"]:
        raise ClarificationRequired("Please clarify the message before applying any changes.")
    selected_job = normalize(current)["job_id"]
    if patch["spoken_job_id"] not in (None, selected_job):
        raise SpokenJobMismatch("The message names a different job; no changes were applied.")
    return apply_changes(current, patch["set"], patch["clear"])
