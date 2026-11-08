"""Boundary expectations for the shared field and extraction contract."""

from copy import deepcopy

import pytest

from bolparchi import fields, validation
from bolparchi.readback import question_for


BASE = {"job_id": "104", "diagnosis": "motor kharab", "status": "completed"}


@pytest.mark.parametrize(
    "field,limit", [("diagnosis", 500), ("follow_up", 500), ("part_needed", 120)]
)
def test_text_length_boundaries_and_clarification(field, limit):
    extra = {"quantity": 1} if field == "part_needed" else {}
    assert validation.validate({**BASE, **extra, field: "क" * limit}).complete
    invalid = validation.validate({**BASE, **extra, field: "क" * (limit + 1)})
    assert invalid.invalid_fields == {field: "too_long"}
    assert question_for(invalid)


def test_generated_schema_has_sparse_nonnullable_changes_and_fixed_job():
    schema = fields.extraction_schema()
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {"set", "clear", "spoken_job_id", "needs_clarification"}
    changes = schema["properties"]["set"]
    assert changes["additionalProperties"] is False
    assert changes.get("required", []) == []
    assert set(changes["properties"]) == {
        "diagnosis",
        "status",
        "part_needed",
        "quantity",
        "follow_up",
    }
    assert changes["properties"]["diagnosis"]["maxLength"] == 500
    assert changes["properties"]["part_needed"]["maxLength"] == 120
    assert changes["properties"]["quantity"] == {
        "type": "integer",
        "minimum": 1,
        "maximum": 20,
        "description": "The final explicitly stated count after corrections; never choose between uncertain alternatives.",
    }
    assert changes["properties"]["status"]["enum"] == ["completed", "pending"]
    assert schema["properties"]["spoken_job_id"]["type"] == ["string", "null"]
    assert "job_id" not in schema["properties"]["clear"]["items"]["enum"]
    changes["properties"]["diagnosis"]["maxLength"] = 1
    assert (
        fields.extraction_schema()["properties"]["set"]["properties"]["diagnosis"]["maxLength"]
        == 500
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"job_id": "105"},
        {"unknown": "x"},
        {"diagnosis": None},
        {"part_needed": " "},
        {"diagnosis": "x" * 501},
        {"part_needed": "x" * 121},
        {"follow_up": "x" * 501},
        {"status": "done"},
        {"quantity": True},
        {"quantity": "ek"},
        {"quantity": 2.0},
        {"quantity": 0},
        {"quantity": 21},
        {"diagnosis": []},
    ],
)
def test_extraction_values_are_strict_even_when_legacy_normalizer_accepts_words(changes):
    envelope = {"set": changes, "clear": [], "spoken_job_id": None, "needs_clarification": False}
    with pytest.raises(ValueError):
        validation.validate_extraction(envelope)


@pytest.mark.parametrize(
    "update",
    [
        {"extra": True},
        {"set": []},
        {"clear": "diagnosis"},
        {"clear": ["job_id"]},
        {"clear": [{}]},
        {"spoken_job_id": 105},
        {"spoken_job_id": "Job 105"},
        {"needs_clarification": "false"},
        {"set": {"quantity": 1}, "clear": ["part_needed"]},
        {"set": {"diagnosis": "x"}, "clear": ["diagnosis"]},
    ],
)
def test_extraction_envelope_rejects_malformed_or_conflicting_output(update):
    envelope = {"set": {}, "clear": [], "spoken_job_id": None, "needs_clarification": False}
    with pytest.raises(ValueError):
        validation.validate_extraction({**envelope, **update})


def test_extraction_keeps_only_stated_fields_and_does_not_mutate_input():
    raw = {
        "set": {"quantity": 1},
        "clear": [],
        "spoken_job_id": "104",
        "needs_clarification": False,
    }
    before = deepcopy(raw)
    assert validation.validate_extraction(raw) == before
    assert raw == before
    current = {**BASE, "part_needed": "motor", "quantity": 2}
    assert validation.apply_extraction(current, raw) == {
        **current,
        "quantity": 1,
        "follow_up": None,
    }


@pytest.mark.parametrize("flag,job", [(True, None), (False, "105")])
def test_ambiguous_message_or_job_mismatch_cannot_apply_any_fields(flag, job):
    raw = {
        "set": {"diagnosis": "pump kharab"},
        "clear": [],
        "spoken_job_id": job,
        "needs_clarification": flag,
    }
    before = deepcopy(BASE)
    expected_error = validation.ClarificationRequired if flag else validation.SpokenJobMismatch
    with pytest.raises(expected_error):
        validation.apply_extraction(BASE, raw)
    assert BASE == before


@pytest.mark.parametrize("raw", [None, [], {}, {"set": {}, "clear": []}])
def test_missing_extraction_fields_are_rejected(raw):
    with pytest.raises(ValueError, match="four contract fields"):
        validation.validate_extraction(raw)


def test_overlong_record_cannot_be_confirmed_or_saved():
    from bolparchi import Store

    store = Store()
    try:
        draft = store.create_draft({**BASE, "diagnosis": "x" * 501}).data
        result = store.confirm(draft["draft_id"], draft["revision"], draft["content_hash"])
        assert result.code == "incomplete"
        assert result.data["invalid_fields"] == {"diagnosis": "too_long"}
        assert store.save(draft["draft_id"], "length-test").code == "not_confirmed"
        assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
    finally:
        store.close()


@pytest.mark.parametrize("message", ["", " \n ", "x" * 2001, None, []])
def test_empty_oversized_or_wrong_type_message_cannot_reach_extraction(message):
    with pytest.raises(ValueError):
        validation.validate_message(message)


def test_message_boundary_preserves_original_text():
    message = "क" * 2000
    assert validation.validate_message(message) == message
