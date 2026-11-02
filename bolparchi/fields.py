"""Shared field metadata; conditional business rules remain in validation.py."""

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class FieldSpec:
    json_type: str
    required: bool = False
    patchable: bool = True
    choices: tuple[str, ...] = ()
    minimum: int | None = None
    maximum: int | None = None
    pattern: str | None = None
    max_length: int | None = None


FIELD_SPECS = MappingProxyType(
    {
        "job_id": FieldSpec("string", required=True, patchable=False, pattern=r"\d{1,6}"),
        "diagnosis": FieldSpec("string", required=True, max_length=500),
        "status": FieldSpec("string", required=True, choices=("completed", "pending")),
        "part_needed": FieldSpec("string", max_length=120),
        "quantity": FieldSpec("integer", minimum=1, maximum=20),
        "follow_up": FieldSpec("string", max_length=500),
    }
)

MAX_MESSAGE_LENGTH = 2000
SCHEMA_VERSION = "bolparchi-extraction-v1"


def field_schema(spec: FieldSpec) -> dict:
    """Model proposals contain normalized values; null never means deletion."""
    schema = {"type": spec.json_type}
    if spec.choices:
        schema["enum"] = list(spec.choices)
    if spec.minimum is not None:
        schema["minimum"] = spec.minimum
    if spec.maximum is not None:
        schema["maximum"] = spec.maximum
    if spec.pattern:
        schema["pattern"] = f"^{spec.pattern}$"
    if spec.max_length is not None:
        schema.update(minLength=1, maxLength=spec.max_length)
    return schema


def extraction_schema() -> dict:
    """Fresh schema from FIELD_SPECS; Python also enforces cross-field rules."""
    patchable = {name: field_schema(spec) for name, spec in FIELD_SPECS.items() if spec.patchable}
    spoken_job = field_schema(FIELD_SPECS["job_id"])
    spoken_job["type"] = ["string", "null"]
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "set": {"type": "object", "properties": patchable, "additionalProperties": False},
            "clear": {"type": "array", "items": {"type": "string", "enum": list(patchable)}},
            "spoken_job_id": spoken_job,
            "needs_clarification": {"type": "boolean"},
        },
        "required": ["set", "clear", "spoken_job_id", "needs_clarification"],
    }
