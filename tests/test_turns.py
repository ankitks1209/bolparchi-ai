"""Typed turn ordering, held patches and cancellation against real SQLite."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from bolparchi import Store


FULL = {
    "job_id": "104",
    "diagnosis": "motor kharab",
    "status": "pending",
    "part_needed": "motor",
    "quantity": 2,
    "follow_up": "kal shaam",
}


def patch(changes=None, *, job=None, unclear=False):
    return {"set": changes or {}, "clear": [], "spoken_job_id": job, "needs_clarification": unclear}


@pytest.fixture
def store():
    instance = Store()
    yield instance
    instance.close()


def begin(store, draft, text="Ek motor chahiye."):
    result = store.begin_turn(draft["draft_id"], text, expected_revision=draft["revision"])
    assert result.ok
    return result.data["input"]["turn_id"]


def complete(store, draft, turn, raw):
    return store.complete_turn(draft["draft_id"], turn, raw, expected_revision=draft["revision"])


def test_processing_preserves_transcript_and_blocks_earlier_confirmation(store):
    draft = store.create_draft(FULL).data
    assert store.confirm(draft["draft_id"], 1, draft["content_hash"]).ok
    turn = begin(store, draft, "  Ek motor chahiye.\n")
    view = store.get_draft(draft["draft_id"])
    assert view["input"]["turn_id"] == turn
    assert view["input"]["transcript"] == "  Ek motor chahiye.\n"
    assert view["input"]["state"] == "processing"
    assert view["confirmed"] is False
    assert store.confirm(draft["draft_id"], 1, draft["content_hash"]).code == "pending_input"
    assert store.save(draft["draft_id"], "while-processing").code == "pending_input"


def test_extraction_applies_once_and_highlights_changed_fields(store):
    draft = store.create_draft(FULL).data
    turn = begin(store, draft)
    result = complete(store, draft, turn, patch({"quantity": 1}))
    assert result.ok and result.code == "updated"
    assert result.data["revision"] == 2
    assert result.data["proposal"] == {**FULL, "quantity": 1}
    assert result.data["input"]["changed_fields"] == ["quantity"]
    assert complete(store, draft, turn, patch({"quantity": 3})).code == "stale_response"
    assert store.get_draft(draft["draft_id"]) == result.data


@pytest.mark.parametrize("reason", ["edit", "new_turn", "cancel"])
def test_late_extraction_cannot_overwrite_current_state(store, reason):
    draft = store.create_draft(FULL).data
    turn = begin(store, draft)
    if reason == "edit":
        assert store.update_draft(draft["draft_id"], {"quantity": 4}, expected_revision=1).ok
    elif reason == "new_turn":
        begin(store, draft, "Chaar motor chahiye.")
    else:
        assert store.cancel_draft(draft["draft_id"], expected_revision=1).ok
    before = store.get_draft(draft["draft_id"])
    result = complete(store, draft, turn, patch({"quantity": 1}))
    assert result.code == ("cancelled" if reason == "cancel" else "stale_response")
    assert store.get_draft(draft["draft_id"]) == before
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0


def test_wrong_draft_and_wrong_turn_are_rejected(store):
    a, b = store.create_draft(FULL).data, store.create_draft(FULL).data
    turn = begin(store, a)
    begin(store, b)
    assert complete(store, b, turn, patch({"quantity": 1})).code == "stale_response"
    assert complete(store, a, "wrong-turn", patch({"quantity": 1})).code == "stale_response"
    assert store.get_draft(a["draft_id"])["proposal"] == FULL
    assert store.get_draft(b["draft_id"])["proposal"] == FULL


@pytest.mark.parametrize("action", ["apply", "discard"])
def test_mismatch_holds_whole_patch_until_explicit_resolution(store, action):
    draft = store.create_draft(FULL).data
    turn = begin(store, draft, "Job 105, pump chahiye, ek.")
    held = complete(store, draft, turn, patch({"part_needed": "pump", "quantity": 1}, job="105"))
    assert held.code == "job_mismatch"
    assert held.data["proposal"] == FULL
    assert held.data["revision"] == 1
    assert store.confirm(draft["draft_id"], 1, draft["content_hash"]).code == "pending_input"
    result = store.resolve_mismatch(draft["draft_id"], turn, action, expected_revision=1)
    assert result.ok
    expected = {**FULL, "part_needed": "pump", "quantity": 1} if action == "apply" else FULL
    assert result.data["proposal"] == expected
    assert result.data["revision"] == (2 if action == "apply" else 1)
    assert result.data["confirmed"] is False
    assert (
        store.resolve_mismatch(draft["draft_id"], turn, action, expected_revision=1).code
        == "stale_response"
    )


@pytest.mark.parametrize("reason", ["edit", "new_turn", "cancel"])
def test_mismatch_release_rechecks_revision_turn_and_open_state(store, reason):
    draft = store.create_draft(FULL).data
    turn = begin(store, draft)
    assert complete(store, draft, turn, patch({"quantity": 1}, job="105")).code == "job_mismatch"
    if reason == "edit":
        assert store.update_draft(draft["draft_id"], {"quantity": 4}, expected_revision=1).ok
    elif reason == "new_turn":
        begin(store, draft, "Chaar motor chahiye.")
    else:
        assert store.cancel_draft(draft["draft_id"], expected_revision=1).ok
    before = store.get_draft(draft["draft_id"])
    result = store.resolve_mismatch(draft["draft_id"], turn, "apply", expected_revision=1)
    assert result.code == ("cancelled" if reason == "cancel" else "stale_response")
    assert store.get_draft(draft["draft_id"]) == before


def test_ambiguous_message_applies_nothing_and_cannot_use_mismatch_release(store):
    draft = store.create_draft(FULL).data
    turn = begin(store, draft)
    result = complete(store, draft, turn, patch({"quantity": 1}, job="105", unclear=True))
    assert result.code == "clarification_required"
    assert result.data["proposal"] == FULL
    assert (
        store.resolve_mismatch(draft["draft_id"], turn, "apply", expected_revision=1).code
        == "stale_response"
    )
    assert store.confirm(draft["draft_id"], 1, draft["content_hash"]).code == "pending_input"


@pytest.mark.parametrize("raw", [{}, patch({"job_id": "105"}), patch({"quantity": True})])
def test_malformed_output_preserves_message_and_draft_for_retry(store, raw):
    draft = store.create_draft(FULL).data
    turn = begin(store, draft)
    result = complete(store, draft, turn, raw)
    assert result.code == "invalid_extraction"
    assert result.data["proposal"] == FULL
    assert result.data["input"]["transcript"] == "Ek motor chahiye."
    assert result.data["input"]["state"] == "error"
    assert store.confirm(draft["draft_id"], 1, draft["content_hash"]).code == "pending_input"
    assert complete(store, draft, turn, patch({"quantity": 1})).code == "stale_response"


def test_error_from_superseded_request_does_not_replace_new_message(store):
    draft = store.create_draft(FULL).data
    old_turn = begin(store, draft)
    begin(store, draft, "Naya message.")
    before = store.get_draft(draft["draft_id"])
    assert (
        store.fail_turn(draft["draft_id"], old_turn, expected_revision=1).code == "stale_response"
    )
    assert store.get_draft(draft["draft_id"]) == before


@pytest.mark.parametrize("message", ["", " \n", "x" * 2001, None])
def test_invalid_message_preserves_existing_review_and_confirmation(store, message):
    draft = store.create_draft(FULL).data
    assert store.confirm(draft["draft_id"], 1, draft["content_hash"]).ok
    before = store.get_draft(draft["draft_id"])
    assert store.begin_turn(draft["draft_id"], message, expected_revision=1).code == "invalid_input"
    assert store.get_draft(draft["draft_id"]) == before


def test_real_cancellation_is_persistent_and_changes_no_job(tmp_path):
    path = str(tmp_path / "cancel.sqlite")
    store = Store(path)
    draft = store.create_draft(FULL).data
    turn = begin(store, draft)
    cancelled = store.cancel_draft(draft["draft_id"], expected_revision=1)
    assert cancelled.code == "cancelled" and cancelled.ok
    assert cancelled.data["revision"] == 2
    store.close()
    store = Store(path)
    try:
        assert store.get_draft(draft["draft_id"])["state"] == "cancelled"
        assert complete(store, draft, turn, patch({"quantity": 1})).code == "cancelled"
        assert (
            store.confirm(draft["draft_id"], 2, cancelled.data["content_hash"]).code == "cancelled"
        )
        assert store.save(draft["draft_id"], "cancelled").code == "cancelled"
        assert (
            store.conn.execute("SELECT status FROM jobs WHERE job_id='104'").fetchone()[0] == "open"
        )
        assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
    finally:
        store.close()


def test_two_connections_reject_old_turn_even_at_same_revision(tmp_path):
    path = str(tmp_path / "turns.sqlite")
    first, second = Store(path), Store(path)
    try:
        draft = first.create_draft(FULL).data
        old = begin(first, draft)
        new = begin(second, draft, "Chaar motor.")
        assert complete(first, draft, old, patch({"quantity": 1})).code == "stale_response"
        assert complete(second, draft, new, patch({"quantity": 4})).ok
        assert first.get_draft(draft["draft_id"])["proposal"]["quantity"] == 4
    finally:
        first.close()
        second.close()


def test_saved_receipt_replays_and_saved_draft_cannot_cancel_or_start_turn(store):
    draft = store.create_draft(FULL).data
    assert store.confirm(draft["draft_id"], 1, draft["content_hash"]).ok
    saved = store.save(draft["draft_id"], "receipt")
    assert saved.ok
    assert store.cancel_draft(draft["draft_id"], expected_revision=1).code == "already_saved"
    assert (
        store.begin_turn(draft["draft_id"], "New text.", expected_revision=1).code
        == "already_saved"
    )
    assert store.save(draft["draft_id"], "receipt").data == saved.data


def test_existing_database_gains_input_table_without_losing_receipt(tmp_path):
    path = str(tmp_path / "upgrade.sqlite")
    original = Store(path)
    saved_draft = original.create_draft(FULL).data
    open_draft = original.create_draft(FULL).data
    assert original.confirm(saved_draft["draft_id"], 1, saved_draft["content_hash"]).ok
    receipt = original.save(saved_draft["draft_id"], "durable-receipt").data
    # Reproduce the previous schema, which had no draft_inputs table.
    original.conn.execute("DROP TABLE draft_inputs")
    original.close()
    upgraded = Store(path)
    try:
        assert upgraded.get_draft(saved_draft["draft_id"])["receipt"] == receipt
        assert upgraded.save(saved_draft["draft_id"], "durable-receipt").data == receipt
        turn = begin(upgraded, open_draft)
        assert complete(upgraded, open_draft, turn, patch({"quantity": 1})).ok
        assert upgraded.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 1
    finally:
        upgraded.close()


def test_cancellation_cannot_report_not_saved_while_save_transaction_commits(tmp_path):
    path = str(tmp_path / "save-cancel.sqlite")
    saving, cancelling = Store(path), Store(path)
    entered, release, cancel_started = Event(), Event(), Event()

    def pause_transaction():
        entered.set()
        assert release.wait(3), "test did not release the real SQLite transaction"
        return 1

    try:
        draft = saving.create_draft(FULL).data
        assert saving.confirm(draft["draft_id"], 1, draft["content_hash"]).ok
        saving.conn.create_function("pause_transaction", 0, pause_transaction)
        saving.conn.execute(
            "CREATE TEMP TRIGGER pause_save BEFORE INSERT ON submissions BEGIN SELECT pause_transaction(); END"
        )

        def cancel():
            cancel_started.set()
            return cancelling.cancel_draft(draft["draft_id"], expected_revision=1)

        with ThreadPoolExecutor(max_workers=2) as executor:
            save_result = executor.submit(saving.save, draft["draft_id"], "inflight-save")
            try:
                assert entered.wait(3)
                cancel_result = executor.submit(cancel)
                assert cancel_started.wait(3)
                assert not cancel_result.done()
            finally:
                release.set()
            assert save_result.result(timeout=3).code == "saved"
            assert cancel_result.result(timeout=3).code == "already_saved"
        assert cancelling.get_draft(draft["draft_id"])["state"] == "saved"
        assert cancelling.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 1
    finally:
        release.set()
        saving.close()
        cancelling.close()
