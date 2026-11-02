"""Recovery uses real SQLite writes; injected delivery can lose/delay responses."""

import pytest
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from bolparchi import Store
from bolparchi.recovery import SaveRecovery


@pytest.fixture
def store(tmp_path):
    instance = Store(str(tmp_path / "recovery.db"))
    yield instance
    instance.close()


def draft(store):
    return store.create_draft(
        {
            "job_id": "104",
            "diagnosis": "motor",
            "status": "pending",
            "part_needed": "motor",
            "quantity": 1,
            "follow_up": "kal shaam",
        }
    ).data


def send(recovery, current, submission_id="save-one"):
    return recovery.save(
        current["draft_id"],
        submission_id,
        revision=current["revision"],
        content_hash=current["content_hash"],
    )


def test_confirm_save_returns_a_durable_receipt_and_replays_it_once(store, tmp_path):
    current = draft(store)
    recovery = SaveRecovery(store)
    saved = send(recovery, current)
    assert saved.code == "saved"
    assert saved.data["receipt"]["submission_id"] == "save-one"
    assert send(recovery, current).data["receipt"] == saved.data["receipt"]
    reopened = Store(str(tmp_path / "recovery.db"))
    try:
        checked = SaveRecovery(reopened).check_status(current["draft_id"], "save-one")
        assert checked.code == "saved" and checked.data["receipt"] == saved.data["receipt"]
        for table in ("submissions", "parts_requests", "tasks"):
            assert reopened.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 1
    finally:
        reopened.close()


def test_lost_response_after_real_commit_is_recovered_without_another_write(store):
    calls = []

    def delivery(draft_id, submission_id):
        calls.append(submission_id)
        assert store.save(draft_id, submission_id).ok
        raise TimeoutError("private transport detail")

    current = draft(store)
    result = send(SaveRecovery(store, send_save=delivery), current)
    assert result.code == "saved"
    assert result.data["receipt"]["submission_id"] == "save-one"
    assert calls == ["save-one"]
    assert "private transport detail" not in repr(result)


def test_missing_receipt_is_unresolved_and_draft_stays_locked(store):
    calls = []

    def lost(draft_id, submission_id):
        calls.append(submission_id)
        raise TimeoutError("unknown delivery")

    current = draft(store)
    recovery = SaveRecovery(store, send_save=lost)
    result = send(recovery, current)
    assert len(calls) == 3
    assert calls == ["save-one"] * 3
    assert result.code == "unresolved" and result.data["locked"]
    assert (
        store.update_draft(current["draft_id"], {"quantity": 2}, expected_revision=1).code
        == "draft_locked"
    )
    assert store.cancel_draft(current["draft_id"], expected_revision=1).code == "draft_locked"
    assert recovery.check_status(current["draft_id"], "save-one").code == "unresolved"
    assert len(calls) == 3


class CommitFailure:
    """Fault at a real SQLite commit; all actual writes/rollback still use SQLite."""

    def __init__(self, connection, *, failures, transient):
        self.connection = connection
        self.failures = failures
        self.transient = transient
        self.saving = False

    def __getattr__(self, name):
        return getattr(self.connection, name)

    def execute(self, sql, *args):
        if sql.startswith("INSERT INTO submissions"):
            self.saving = True
        if sql == "ROLLBACK":
            self.saving = False
        if sql == "COMMIT" and self.saving:
            self.saving = False
            if self.failures:
                self.failures -= 1
                if self.transient:
                    error = sqlite3.OperationalError("private lock detail")
                    error.sqlite_errorcode = sqlite3.SQLITE_BUSY
                    raise error
                raise RuntimeError("private storage detail")
        return self.connection.execute(sql, *args)


def test_transient_rollback_retries_same_id_then_commits_once(store):
    current = draft(store)
    store.conn = CommitFailure(store.conn, failures=2, transient=True)
    saved = send(SaveRecovery(store), current)
    assert saved.code == "saved"
    assert saved.data["attempts"] == 3
    for table in ("submissions", "parts_requests", "tasks"):
        assert store.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 1


@pytest.mark.parametrize("transient,attempts", [(True, 3), (False, 1)])
def test_definite_rollback_closes_and_fences_old_delivery_before_unlocking(
    store, transient, attempts
):
    current = draft(store)
    store.conn = CommitFailure(store.conn, failures=3, transient=transient)
    recovery = SaveRecovery(store)
    failed = send(recovery, current)
    assert failed.code == "not_saved"
    assert failed.data["attempts"] == attempts
    assert not failed.data["locked"]
    assert "private" not in repr(failed)
    # A queued old delivery must remain fenced even after the draft is edited.
    assert store.save(current["draft_id"], "save-one").code == "save_closed"
    edited = store.update_draft(current["draft_id"], {"quantity": 2}, expected_revision=1)
    assert edited.ok and not edited.data["confirmed"]
    assert send(recovery, current).code == "not_saved"
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0


def test_late_commit_after_missing_status_is_found_by_manual_check(store, tmp_path):
    release = Event()
    worker_store = Store(str(tmp_path / "recovery.db"))
    futures = []
    with ThreadPoolExecutor(max_workers=1) as pool:

        def late_commit(draft_id, submission_id):
            assert release.wait(5)
            return worker_store.save(draft_id, submission_id)

        def delivery(draft_id, submission_id):
            if not futures:
                futures.append(pool.submit(late_commit, draft_id, submission_id))
            raise TimeoutError("response may arrive later")

        current = draft(store)
        recovery = SaveRecovery(store, send_save=delivery)
        try:
            result = send(recovery, current)
            assert result.code == "unresolved" and result.data["locked"]
            assert recovery.check_status(current["draft_id"], "save-one").code == "unresolved"
            assert (
                store.begin_audio_turn(current["draft_id"], expected_revision=1).code
                == "draft_locked"
            )
        finally:
            release.set()
        assert futures[0].result(timeout=5).ok
    worker_store.close()
    checked = recovery.check_status(current["draft_id"], "save-one")
    assert checked.code == "saved" and checked.data["receipt"]["submission_id"] == "save-one"
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 1


def test_attempt_budget_and_submission_identity_survive_reopening(store, tmp_path):
    calls = []

    def lost(*args):
        calls.append(args)
        raise TimeoutError()

    current = draft(store)
    assert send(SaveRecovery(store, send_save=lost), current).code == "unresolved"
    reopened = Store(str(tmp_path / "recovery.db"))
    try:
        assert send(SaveRecovery(reopened, send_save=lost), current).code == "unresolved"
        snapshot = reopened.get_draft(current["draft_id"])
        assert snapshot["save_request"]["submission_id"] == "save-one"
        assert snapshot["save_request"]["attempts"] == 3
        assert send(SaveRecovery(reopened), current, "different-id").code == "draft_locked"
    finally:
        reopened.close()
    assert len(calls) == 3


@pytest.mark.parametrize("rejection", ["stale", "incomplete", "cancelled", "pending"])
def test_rejected_reviews_never_send_or_retry(store, rejection):
    current = draft(store)
    if rejection == "stale":
        store.update_draft(current["draft_id"], {"quantity": 2}, expected_revision=1)
    elif rejection == "incomplete":
        current = store.create_draft({"job_id": "104"}).data
    elif rejection == "cancelled":
        store.cancel_draft(current["draft_id"], expected_revision=1)
    else:
        store.begin_turn(current["draft_id"], "Still extracting", expected_revision=1)
    calls = []
    result = send(SaveRecovery(store, send_save=lambda *args: calls.append(args)), current)
    assert not result.ok
    assert not calls
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0


def test_same_id_cannot_claim_a_different_review_was_saved(store):
    current = draft(store)
    recovery = SaveRecovery(store)
    assert send(recovery, current).code == "saved"
    changed = dict(current, content_hash="different-reviewed-content")
    assert send(recovery, changed).code == "submission_conflict"


def test_legacy_receipt_is_also_bound_to_its_exact_review(store):
    current = draft(store)
    assert store.confirm(current["draft_id"], 1, current["content_hash"]).ok
    assert store.save(current["draft_id"], "save-one").ok
    changed = dict(current, content_hash="different-review")
    assert send(SaveRecovery(store), changed).code == "submission_conflict"


@pytest.mark.parametrize("bad_response", [{"ok": True, "receipt": "untrusted"}, "saved", 42, None])
def test_malformed_delivery_response_does_not_claim_saved_or_expose_data(store, bad_response):
    current = draft(store)
    calls = []

    def delivery(*args):
        calls.append(args)
        return bad_response

    result = send(SaveRecovery(store, send_save=delivery), current)
    assert result.code == "unresolved" and result.data["receipt"] is None
    assert result.data["locked"]
    assert len(calls) == 1


def test_error_reported_after_actual_commit_still_resolves_saved(store):
    class CommitThenError(CommitFailure):
        def execute(self, sql, *args):
            if sql.startswith("INSERT INTO submissions"):
                self.saving = True
            if sql == "COMMIT" and self.saving:
                self.saving = False
                self.connection.execute(sql, *args)
                raise RuntimeError("private post-commit failure")
            return self.connection.execute(sql, *args)

    current = draft(store)
    store.conn = CommitThenError(store.conn, failures=1, transient=False)
    result = send(SaveRecovery(store), current)
    assert result.code == "saved"
    assert result.data["attempts"] == 1
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 1


def test_terminal_fence_waits_for_inflight_commit_and_returns_its_receipt(store, tmp_path):
    current = draft(store)
    assert (
        store.prepare_save(
            current["draft_id"], "save-one", revision=1, content_hash=current["content_hash"]
        ).code
        == "pending"
    )
    assert store.begin_save_attempt(current["draft_id"], "save-one").ok
    entered, release, fence_entered = Event(), Event(), Event()
    worker = Store(str(tmp_path / "recovery.db"))

    class PausedCommit(CommitFailure):
        def execute(self, sql, *args):
            if sql.startswith("INSERT INTO submissions"):
                self.saving = True
            if sql == "COMMIT" and self.saving:
                entered.set()
                assert release.wait(5)
                self.saving = False
            return self.connection.execute(sql, *args)

    class ObserveFence(CommitFailure):
        def execute(self, sql, *args):
            if sql == "BEGIN IMMEDIATE":
                fence_entered.set()
            return self.connection.execute(sql, *args)

    worker.conn = PausedCommit(worker.conn, failures=0, transient=False)
    store.conn = ObserveFence(store.conn, failures=0, transient=False)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            commit = pool.submit(worker.save, current["draft_id"], "save-one")
            try:
                assert entered.wait(5)
                closing = pool.submit(
                    store.close_failed_save, current["draft_id"], "save-one", error_code="failed"
                )
                assert fence_entered.wait(5)
            finally:
                release.set()
            assert commit.result(timeout=5).ok
            result = closing.result(timeout=5)
            assert result.code == "saved" and result.data["receipt"]["submission_id"] == "save-one"
    finally:
        worker.close()


def test_retry_hint_cannot_override_a_nonretryable_rejection(store):
    from bolparchi.store import Outcome

    calls = []

    def rejected(*args):
        calls.append(args)
        return Outcome(False, "not_confirmed", "Do not retry.", {"retryable": True})

    result = send(SaveRecovery(store, send_save=rejected), draft(store))
    assert result.code == "not_saved"
    assert len(calls) == 1


def test_concurrent_recovery_callers_share_the_three_attempt_budget(store):
    current = draft(store)
    calls = []

    def lost(*args):
        calls.append(args)
        raise TimeoutError()

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(
            pool.map(lambda _: send(SaveRecovery(store, send_save=lost), current), range(6))
        )
    assert all(result.code == "unresolved" for result in results)
    assert len(calls) == 3
    assert store.save_status(current["draft_id"], "save-one").data["attempts"] == 3


def test_old_database_receipts_survive_recovery_schema_upgrade(tmp_path):
    path = str(tmp_path / "legacy.db")
    old = Store(path)
    current = draft(old)
    assert old.confirm(current["draft_id"], 1, current["content_hash"]).ok
    receipt = old.save(current["draft_id"], "save-one").data
    old.close()
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE save_requests")
    reopened = Store(path)
    try:
        assert send(SaveRecovery(reopened), current).data["receipt"] == receipt
        assert reopened.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 1
    finally:
        reopened.close()
