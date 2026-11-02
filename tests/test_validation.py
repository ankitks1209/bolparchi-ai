import pytest
from bolparchi.validation import validate, proposal_hash, apply_changes, MAX_QUANTITY
from bolparchi.readback import question_for, readback_text

BASE = {"job_id": "104", "diagnosis": "motor kharab", "status": "completed"}


def test_completed_job_needs_no_part_or_follow_up():
    assert validate(BASE).complete


def test_part_without_quantity_is_missing():
    v = validate({**BASE, "part_needed": "motor"})
    assert v.missing_fields == ("quantity",)


def test_pending_requires_follow_up_but_completed_does_not():
    assert validate({**BASE, "status": "pending"}).missing_fields == ("follow_up",)
    assert validate(BASE).missing_fields == ()


@pytest.mark.parametrize("bad", [0, -1, True, 2.5, MAX_QUANTITY + 1, "kuch"])
def test_invalid_quantities_rejected(bad):
    v = validate({**BASE, "part_needed": "motor", "quantity": bad})
    assert v.invalid_fields.get("quantity") == "invalid_quantity"


@pytest.mark.parametrize("raw,expected", [("do", 2), ("Ek", 1), ("3", 3), (2, 2), (2.0, 2)])
def test_quantity_normalisation(raw, expected):
    v = validate({**BASE, "part_needed": "motor", "quantity": raw})
    assert v.complete and v.proposal["quantity"] == expected


def test_quantity_without_part_is_invalid():
    assert validate({**BASE, "quantity": 2}).invalid_fields == {"quantity": "quantity_without_part"}


def test_status_must_be_allowed_value():
    assert validate({**BASE, "status": "done"}).invalid_fields == {"status": "not_allowed"}


@pytest.mark.parametrize("raw", ["Job 104", "#104", 104, " 104 "])
def test_job_id_normalisation(raw):
    assert validate({**BASE, "job_id": raw}).proposal["job_id"] == "104"


def test_nonnumeric_job_id_invalid():
    assert validate({**BASE, "job_id": "motor"}).invalid_fields == {"job_id": "not_a_job_number"}


def test_hash_stable_and_content_sensitive():
    a = {**BASE, "part_needed": "motor", "quantity": 1}
    b = dict(reversed(list(a.items())))
    assert proposal_hash(a) == proposal_hash(b)
    assert proposal_hash(a) != proposal_hash({**a, "quantity": 2})


def test_correction_replaces_earlier_value_and_clear_removes():
    cur = {**BASE, "part_needed": "motor", "quantity": 2}
    assert apply_changes(cur, {"quantity": 1})["quantity"] == 1
    assert apply_changes(cur, {"quantity": None})["quantity"] == 2
    assert apply_changes(cur, {}, clear=("part_needed", "quantity"))["part_needed"] is None
    with pytest.raises(ValueError):
        apply_changes(cur, {"colour": "red"})


def test_question_and_readback():
    assert "part" in question_for(validate({**BASE, "quantity": 2})).lower()
    assert "motor" in question_for(validate({**BASE, "part_needed": "motor"}))
    assert question_for(validate(BASE)) is None
    p = validate({**BASE, "part_needed": "motor", "quantity": 1}).proposal
    assert "1 motor" in readback_text(p)
