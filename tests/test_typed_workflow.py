"""Offline integration: only the external extractor is replaced by a fixture."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from bolparchi import Store
from bolparchi.workflow import Workflow


def patch(changes, *, job=None, unclear=False):
    return {"set": changes, "clear": [], "spoken_job_id": job, "needs_clarification": unclear}


@pytest.fixture
def store():
    instance = Store()
    yield instance
    instance.close()


def test_typed_clarification_correction_review_and_explicit_save(store):
    answers = {
        "Motor kharab. Do motor chahiye. Kaam pending hai.": patch(
            {
                "diagnosis": "motor kharab",
                "status": "pending",
                "part_needed": "motor",
                "quantity": 2,
            }
        ),
        "Kal shaam aana hai.": patch({"follow_up": "kal shaam"}),
        "Do nahi, ek motor.": patch({"quantity": 1}),
    }
    requests = []

    def extract(message, current):
        requests.append((message, current))
        return answers[message]

    flow = Workflow(store, extract)
    draft = flow.select_job("104").data
    assert draft["phase"] == "clarify" and draft["question"]
    first = flow.submit(draft["draft_id"], next(iter(answers)), expected_revision=1)
    assert first.ok and first.data["question"] == "Aage kya karna hai? Customer se kab milna hai?"
    assert first.data["can_confirm"] is False
    second = flow.submit(draft["draft_id"], "Kal shaam aana hai.", expected_revision=2)
    assert second.data["phase"] == "review" and second.data["can_confirm"] is True
    assert store.confirm(draft["draft_id"], 3, second.data["content_hash"]).ok
    corrected = flow.submit(draft["draft_id"], "Do nahi, ek motor.", expected_revision=3)
    assert corrected.data["proposal"]["quantity"] == 1
    assert corrected.data["changed_fields"] == ["quantity"]
    assert corrected.data["confirmed"] is False
    assert "1 motor" in corrected.data["readback"]
    assert requests[1][1]["part_needed"] == "motor"
    assert requests[2][1]["follow_up"] == "kal shaam"
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
    assert store.save(draft["draft_id"], "typed-save").code == "not_confirmed"
    assert (
        store.confirm(draft["draft_id"], 3, second.data["content_hash"]).code
        == "stale_confirmation"
    )
    assert store.confirm(draft["draft_id"], 4, corrected.data["content_hash"]).ok
    saved = store.save(draft["draft_id"], "typed-save")
    assert saved.ok and saved.code == "saved"
    assert saved.data["job_id"] == "104" and saved.data["submission_id"] == "typed-save"
    assert store.save(draft["draft_id"], "typed-save").data == saved.data
    assert store.conn.execute("SELECT quantity FROM parts_requests").fetchone()[0] == 1
    assert flow.review(draft["draft_id"]).data["receipt"] == saved.data


@pytest.mark.parametrize("message", ["", "  ", "x" * 2001])
def test_invalid_message_never_calls_extractor(store, message):
    calls = []
    flow = Workflow(store, lambda *args: calls.append(args))
    draft = flow.select_job("104").data
    result = flow.submit(draft["draft_id"], message, expected_revision=1)
    assert result.code == "invalid_input"
    assert calls == []
    assert store.get_draft(draft["draft_id"])["input"] is None


def test_failure_is_redacted_and_retry_reuses_the_preserved_message(store):
    calls = []

    def extract(message, current):
        calls.append(message)
        if len(calls) == 1:
            raise RuntimeError("API_KEY=DO_NOT_LOG_THIS provider-body")
        return patch({"diagnosis": "motor theek", "status": "completed"})

    flow = Workflow(store, extract)
    draft = flow.select_job("104").data
    failed = flow.submit(draft["draft_id"], "Motor theek ho gaya.", expected_revision=1)
    assert failed.code == "extraction_failed"
    assert failed.data["phase"] == "extraction_error"
    assert failed.data["can_retry"] and not failed.data["can_confirm"]
    assert "DO_NOT_LOG_THIS" not in repr(failed)
    old = failed.data["input"]["turn_id"]
    retried = flow.retry(draft["draft_id"], old, expected_revision=1)
    assert retried.ok and retried.data["phase"] == "review"
    assert retried.data["input"]["turn_id"] != old
    assert calls == ["Motor theek ho gaya.", "Motor theek ho gaya."]
    assert store.get_draft(draft["draft_id"])["input"]["error_code"] is None


def test_old_retry_cannot_replace_newer_input_at_same_revision(store):
    def broken(*args):
        raise TimeoutError()

    flow = Workflow(store, broken)
    draft = flow.select_job("104").data
    failed = flow.submit(draft["draft_id"], "Old message", expected_revision=1)
    old = failed.data["input"]["turn_id"]
    newer = flow.submit(draft["draft_id"], "New message", expected_revision=1)
    assert flow.retry(draft["draft_id"], old, expected_revision=1).code == "stale_response"
    assert store.get_draft(draft["draft_id"])["input"] == newer.data["input"]


@pytest.mark.parametrize("finish", ["result", "error"])
def test_cancellation_during_real_inflight_callback_rejects_late_completion(store, finish):
    entered, release = Event(), Event()

    def slow(message, current):
        entered.set()
        assert release.wait(3), "test did not release extractor"
        if finish == "error":
            raise TimeoutError("redacted")
        return patch({"diagnosis": "motor theek", "status": "completed"})

    flow = Workflow(store, slow)
    draft = flow.select_job("104").data
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            flow.submit, draft["draft_id"], "Motor theek.", expected_revision=1
        )
        try:
            assert entered.wait(3)
            processing = flow.review(draft["draft_id"])
            assert processing.data["phase"] == "processing"
            assert not processing.data["can_confirm"]
            assert flow.cancel(draft["draft_id"], expected_revision=1).ok
        finally:
            release.set()
        assert future.result(timeout=3).code == "cancelled"
    assert flow.review(draft["draft_id"]).data["phase"] == "cancelled"
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0


def test_held_mismatch_and_ambiguity_have_distinct_actions(store):
    flow = Workflow(
        store, lambda *_: patch({"diagnosis": "pump", "status": "completed"}, job="105")
    )
    draft = flow.select_job("104").data
    held = flow.submit(draft["draft_id"], "Job 105 pump theek.", expected_revision=1)
    assert held.data["phase"] == "job_mismatch"
    assert held.data["proposal"]["diagnosis"] is None
    assert held.data["readback"] is None and not held.data["can_confirm"]
    released = flow.resolve_mismatch(
        draft["draft_id"], held.data["input"]["turn_id"], "apply", expected_revision=1
    )
    assert released.data["phase"] == "review"
    unclear_flow = Workflow(store, lambda *_: patch({"quantity": 1}, unclear=True))
    unclear = unclear_flow.submit(draft["draft_id"], "Ek ya do?", expected_revision=2)
    assert unclear.data["phase"] == "clarify_message"
    assert unclear.data["question"] and not unclear.data["can_confirm"]
    assert unclear.data["proposal"] == released.data["proposal"]
