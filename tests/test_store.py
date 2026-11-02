import threading

import pytest

from bolparchi import Store, new_submission_id

FULL = {
    "job_id": "104",
    "diagnosis": "motor kharab",
    "status": "pending",
    "part_needed": "motor",
    "quantity": 2,
    "follow_up": "customer kal shaam available",
}


def count(store, table):
    return store.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def make_confirmed(store, raw=FULL):
    d = store.create_draft(raw).data
    assert store.confirm(d["draft_id"], d["revision"], d["content_hash"]).ok
    return d["draft_id"]


@pytest.fixture
def store():
    return Store()


def test_happy_path_updates_job_parts_and_task(store):
    draft_id = make_confirmed(store)
    out = store.save(draft_id, new_submission_id())
    assert out.ok and out.code == "saved"
    job = store.conn.execute("SELECT * FROM jobs WHERE job_id='104'").fetchone()
    assert job["status"] == "pending" and job["diagnosis"] == "motor kharab"
    assert count(store, "parts_requests") == 1 and count(store, "tasks") == 1
    assert store.get_draft(draft_id)["state"] == "saved"


def test_cannot_save_unconfirmed(store):
    d = store.create_draft(FULL).data
    out = store.save(d["draft_id"], new_submission_id())
    assert not out.ok and out.code == "not_confirmed"
    assert count(store, "parts_requests") == 0 and count(store, "submissions") == 0


def test_cannot_confirm_incomplete_draft(store):
    d = store.create_draft({"job_id": "104", "diagnosis": "x", "status": "pending"}).data
    out = store.confirm(d["draft_id"], d["revision"], d["content_hash"])
    assert not out.ok and out.code == "incomplete" and out.data["missing_fields"] == ["follow_up"]


def test_cannot_confirm_unknown_job(store):
    # A selected job must exist at creation, and confirmation rechecks it.
    d = store.create_draft(FULL).data
    store.conn.execute("DELETE FROM jobs WHERE job_id='104'")
    out = store.confirm(d["draft_id"], d["revision"], d["content_hash"])
    assert not out.ok and out.code == "unknown_job"


def test_edit_invalidates_confirmation(store):
    draft_id = make_confirmed(store)
    old = store.get_draft(draft_id)
    upd = store.update_draft(draft_id, {"quantity": 1}, expected_revision=old["revision"]).data
    assert upd["revision"] == old["revision"] + 1 and upd["confirmed"] is False
    assert store.save(draft_id, new_submission_id()).code == "not_confirmed"
    # confirming the OLD revision/hash must not work
    assert (
        store.confirm(draft_id, old["revision"], old["content_hash"]).code == "stale_confirmation"
    )
    # confirming the new one works
    assert store.confirm(draft_id, upd["revision"], upd["content_hash"]).ok


def test_two_motors_sorry_one(store):
    d = store.create_draft(FULL).data  # first heard: quantity 2
    upd = store.update_draft(
        d["draft_id"], {"quantity": "ek"}, expected_revision=d["revision"]
    ).data
    assert upd["proposal"]["quantity"] == 1
    assert store.confirm(d["draft_id"], upd["revision"], upd["content_hash"]).ok
    assert store.save(d["draft_id"], new_submission_id()).ok
    rows = store.conn.execute("SELECT quantity FROM parts_requests").fetchall()
    assert [r["quantity"] for r in rows] == [1]


def test_retry_with_same_submission_id_is_replayed_not_duplicated(store):
    draft_id = make_confirmed(store)
    sub = new_submission_id()
    first = store.save(draft_id, sub)
    again = store.save(draft_id, sub)
    assert first.code == "saved" and again.code == "replayed" and again.ok
    assert again.data == first.data
    assert count(store, "parts_requests") == 1 and count(store, "tasks") == 1


def test_second_save_with_new_submission_id_is_blocked(store):
    draft_id = make_confirmed(store)
    assert store.save(draft_id, new_submission_id()).ok
    out = store.save(draft_id, new_submission_id())  # e.g. a second "haan" with a fresh id
    assert not out.ok and out.code == "already_saved"
    assert count(store, "parts_requests") == 1


def test_identical_content_in_two_legitimate_updates_both_save(store):
    a, b = make_confirmed(store), make_confirmed(store)
    assert store.save(a, new_submission_id()).ok and store.save(b, new_submission_id()).ok
    assert count(store, "parts_requests") == 2


def test_submission_id_cannot_be_reused_for_another_draft(store):
    a, b = make_confirmed(store), make_confirmed(store)
    sub = new_submission_id()
    assert store.save(a, sub).ok
    out = store.save(b, sub)
    assert not out.ok and out.code == "submission_conflict"
    assert count(store, "parts_requests") == 1
    assert store.get_draft(b)["state"] == "open"


def test_failure_rolls_back_everything_and_reports_failure(store):
    store.conn.execute(
        "CREATE TRIGGER boom BEFORE INSERT ON tasks BEGIN SELECT RAISE(ABORT, 'simulated outage'); END"
    )
    draft_id = make_confirmed(store)
    sub = new_submission_id()
    out = store.save(draft_id, sub)
    assert not out.ok and out.code == "failed" and "nothing was recorded" in out.message
    job = store.conn.execute("SELECT * FROM jobs WHERE job_id='104'").fetchone()
    assert job["status"] == "open" and job["diagnosis"] is None
    assert count(store, "parts_requests") == 0 and count(store, "submissions") == 0
    assert store.get_draft(draft_id)["state"] == "open"
    # outage over: retrying with the SAME submission id succeeds exactly once
    store.conn.execute("DROP TRIGGER boom")
    assert store.save(draft_id, sub).code == "saved"
    assert count(store, "parts_requests") == 1


def test_concurrent_retries_across_connections_write_once(tmp_path):
    path = str(tmp_path / "k.db")
    setup = Store(path)
    draft_id = make_confirmed(setup)
    sub = new_submission_id()
    results = []

    def worker():
        results.append(Store(path).save(draft_id, sub).code)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(results).count("saved") == 1
    assert all(r in ("saved", "replayed") for r in results)
    assert count(setup, "parts_requests") == 1 and count(setup, "tasks") == 1
