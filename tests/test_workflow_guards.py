"""Existing entry points must enforce the accepted revision/cancel contract."""

import pytest

from bolparchi import Store, readback_text


FULL = {"job_id": "104", "diagnosis": "motor theek", "status": "completed"}


@pytest.fixture
def store():
    instance = Store()
    yield instance
    instance.close()


@pytest.mark.parametrize("revision", [None, True, 1.0, "1", 0])
def test_edit_requires_an_explicit_integer_revision(store, revision):
    draft = store.create_draft(FULL).data
    result = store.update_draft(
        draft["draft_id"], {"diagnosis": "pump"}, expected_revision=revision
    )
    assert result.code == "invalid_input"
    assert store.get_draft(draft["draft_id"]) == draft


@pytest.mark.parametrize("revision", [True, 1.0])
def test_confirmation_rejects_noninteger_revision(store, revision):
    draft = store.create_draft(FULL).data
    result = store.confirm(draft["draft_id"], revision, draft["content_hash"])
    assert result.code == "invalid_input"
    assert store.get_draft(draft["draft_id"])["confirmed"] is False


@pytest.mark.parametrize("action", ["edit", "confirm", "save"])
def test_cancelled_state_is_never_reported_as_saved(store, action):
    draft = store.create_draft(FULL).data
    # Seed the persisted state to exercise the pre-existing entry points before
    # adding the cancel command. Real cancellation gets separate lifecycle tests.
    store.conn.execute("UPDATE drafts SET state='cancelled' WHERE draft_id=?", (draft["draft_id"],))
    if action == "edit":
        result = store.update_draft(draft["draft_id"], {"diagnosis": "pump"}, expected_revision=1)
    elif action == "confirm":
        result = store.confirm(draft["draft_id"], 1, draft["content_hash"])
    else:
        result = store.save(draft["draft_id"], "cancelled-test")
    assert result.code == "cancelled"
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0


def test_readback_requests_explicit_confirm_action():
    text = readback_text(FULL)
    assert "Confirm and save" in text
    assert "Haan bolein" not in text
