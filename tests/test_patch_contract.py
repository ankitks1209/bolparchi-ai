"""Accepted patch rules exercised through the real draft store (AC-04/AC-05)."""

from copy import deepcopy

import pytest

from bolparchi import Store, apply_changes


FULL = {
    "job_id": "104",
    "diagnosis": "motor kharab",
    "status": "pending",
    "part_needed": "motor",
    "quantity": 2,
    "follow_up": "kal shaam",
}


@pytest.fixture
def store():
    instance = Store()
    yield instance
    instance.close()


@pytest.mark.parametrize(
    "changes,clear",
    [
        ({"diagnosis": "naya diagnosis"}, ["diagnosis"]),
        ({"part_needed": "pump"}, ["part_needed"]),
        ({"quantity": 1}, ["part_needed"]),
        ({"job_id": "105"}, []),
        ({}, ["job_id"]),
        ({"colour": "red"}, []),
        ({}, ["colour"]),
        ({"diagnosis": []}, []),
        ([], []),
        ({}, "diagnosis"),
        ({}, [None]),
    ],
)
def test_rejected_patch_preserves_confirmed_draft_and_database(store, changes, clear):
    draft = store.create_draft(FULL).data
    assert store.confirm(draft["draft_id"], draft["revision"], draft["content_hash"]).ok
    before = store.get_draft(draft["draft_id"])
    result = store.update_draft(
        draft["draft_id"], changes, clear, expected_revision=before["revision"]
    )
    assert result.code == "invalid_input"
    assert store.get_draft(draft["draft_id"]) == before
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
    assert store.conn.execute("SELECT status FROM jobs WHERE job_id='104'").fetchone()[0] == "open"


def test_part_clear_also_clears_quantity_and_invalidates_confirmation(store):
    draft = store.create_draft(FULL).data
    assert store.confirm(draft["draft_id"], draft["revision"], draft["content_hash"]).ok
    result = store.update_draft(draft["draft_id"], {}, ["part_needed"], expected_revision=1)
    assert result.ok
    assert result.data["proposal"] == {**FULL, "part_needed": None, "quantity": None}
    assert result.data["revision"] == 2
    assert result.data["confirmed"] is False
    assert result.data["missing_fields"] == []
    assert result.data["invalid_fields"] == {}


def test_part_replacement_preserves_quantity_and_exposes_it_in_review(store):
    draft = store.create_draft(FULL).data
    result = store.update_draft(draft["draft_id"], {"part_needed": "pump"}, expected_revision=1)
    assert result.ok
    assert result.data["proposal"]["part_needed"] == "pump"
    assert result.data["proposal"]["quantity"] == 2


def test_patch_does_not_mutate_caller_data():
    current = deepcopy(FULL)
    changes = {"diagnosis": "pump kharab"}
    clear = ["part_needed"]
    updated = apply_changes(current, changes, clear)
    assert current == FULL
    assert changes == {"diagnosis": "pump kharab"}
    assert clear == ["part_needed"]
    assert updated == {**FULL, "diagnosis": "pump kharab", "part_needed": None, "quantity": None}


@pytest.mark.parametrize("selected_job", [None, "999", "motor"])
def test_draft_requires_known_selected_job_without_writing(store, selected_job):
    result = store.create_draft({**FULL, "job_id": selected_job})
    assert result.code == "unknown_job"
    assert store.conn.execute("SELECT COUNT(*) FROM drafts").fetchone()[0] == 0
