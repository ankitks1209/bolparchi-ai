"""Tests for defects found while reviewing the supplied core."""

from concurrent.futures import ThreadPoolExecutor
import sqlite3

import pytest
from bolparchi import Store, new_submission_id, validate

BASE = {"job_id": "104", "diagnosis": "motor kharab", "status": "completed"}


def confirmed(store):
    d = store.create_draft(BASE).data
    assert store.confirm(d["draft_id"], d["revision"], d["content_hash"]).ok
    return d


@pytest.mark.parametrize("bad", [[], ["proposal"], "proposal", 3, False])
def test_non_object_model_output_rejected(bad):
    with pytest.raises(ValueError):
        validate(bad)
    s = Store()
    try:
        assert s.create_draft(bad).code == "invalid_input"
        assert s.conn.execute("SELECT COUNT(*) FROM drafts").fetchone()[0] == 0
    finally:
        s.close()


@pytest.mark.parametrize(
    "field,bad",
    [
        ("diagnosis", {"unexpected": "object"}),
        ("diagnosis", []),
        ("diagnosis", False),
        ("part_needed", ["motor"]),
        ("follow_up", 123),
        ("status", ["completed"]),
        ("job_id", True),
    ],
)
def test_wrong_field_types_are_never_stringified(field, bad):
    with pytest.raises(ValueError):
        validate({**BASE, field: bad})


@pytest.mark.parametrize("bad", [None, "", "   ", 123, True, "x" * 129])
def test_invalid_submission_id_does_not_mutate_state(bad):
    s = Store()
    try:
        d = confirmed(s)
        assert s.save(d["draft_id"], bad).code == "invalid_submission_id"
        assert s.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
        assert s.get_draft(d["draft_id"])["state"] == "open"
        assert s.save(d["draft_id"], new_submission_id()).code == "saved"
    finally:
        s.close()


def test_untrusted_completeness_flags_are_ignored():
    v = validate({"job_id": "104", "missing_fields": [], "complete": True})
    assert not v.complete
    assert v.missing_fields == ("diagnosis", "status")


def test_read_failure_before_return_rolls_back_draft(monkeypatch):
    s = Store()

    def broken_view(_):
        raise RuntimeError("result preparation failed")

    monkeypatch.setattr(s, "get_draft", broken_view)
    try:
        result = s.create_draft(BASE)
        assert not result.ok
        assert s.conn.execute("SELECT COUNT(*) FROM drafts").fetchone()[0] == 0
        assert not s.conn.in_transaction
    finally:
        s.close()


class FailCommitOnce:
    def __init__(self, conn):
        self.conn = conn
        self.failed = False

    def __getattr__(self, name):
        return getattr(self.conn, name)

    def execute(self, sql, *args):
        if sql == "COMMIT" and not self.failed:
            self.failed = True
            raise sqlite3.OperationalError("simulated commit failure")
        return self.conn.execute(sql, *args)


def test_commit_failure_rolls_back_and_allows_same_id_retry():
    s = Store()
    try:
        d = confirmed(s)
        sub = new_submission_id()
        s.conn = FailCommitOnce(s.conn)
        failed = s.save(d["draft_id"], sub)
        assert not failed.ok
        assert not s.conn.in_transaction
        assert s.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
        assert s.conn.execute("SELECT status FROM jobs WHERE job_id='104'").fetchone()[0] == "open"
        assert s.save(d["draft_id"], sub).code == "saved"
        assert s.save(d["draft_id"], sub).code == "replayed"
    finally:
        s.close()


def test_shared_store_concurrent_retries_write_once():
    s = Store()
    try:
        d = confirmed(s)
        sub = new_submission_id()
        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(pool.map(lambda _: s.save(d["draft_id"], sub), range(8)))
        assert all(o.ok for o in outcomes)
        assert [o.code for o in outcomes].count("saved") == 1
        assert [o.code for o in outcomes].count("replayed") == 7
        assert s.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 1
    finally:
        s.close()


def test_stale_edit_cannot_overwrite_newer_correction():
    s = Store()
    try:
        d = s.create_draft(BASE).data
        updated = s.update_draft(d["draft_id"], {"diagnosis": "new diagnosis"}, expected_revision=1)
        assert updated.ok
        stale = s.update_draft(d["draft_id"], {"diagnosis": "old diagnosis"}, expected_revision=1)
        assert stale.code == "stale_update"
        assert s.get_draft(d["draft_id"])["proposal"]["diagnosis"] == "new diagnosis"
    finally:
        s.close()


def test_superscript_quantity_is_invalid_without_parser_crash():
    v = validate({**BASE, "part_needed": "motor", "quantity": "²"})
    assert v.invalid_fields["quantity"] == "invalid_quantity"
