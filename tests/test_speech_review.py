from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from bolparchi import Store
from bolparchi.speech_review import SpeechReview
from bolparchi.workflow import Workflow


@pytest.fixture
def store():
    instance = Store()
    yield instance
    instance.close()


def reviewed(store):
    return store.create_draft(
        {
            "job_id": "104",
            "diagnosis": "motor kharab",
            "status": "pending",
            "part_needed": "motor",
            "quantity": 1,
            "follow_up": "kal shaam",
        }
    ).data


def test_speech_uses_server_review_text_without_confirming_or_saving(store):
    draft = reviewed(store)
    calls = []

    def synthesize(text):
        calls.append(text)
        return b"wave-fixture"

    flow = Workflow(store, None)
    result = SpeechReview(flow, synthesize).speak(
        draft["draft_id"], revision=draft["revision"], content_hash=draft["content_hash"]
    )
    assert result.code == "audio"
    assert result.data["audio"] == b"wave-fixture"
    assert calls == [
        "Job 104: motor kharab. Kaam abhi baaki hai. 1 motor chahiye. Aage: kal shaam. Sab sahi hai? Confirm and save dabayein, ya badlav bataiye."
    ]
    assert not store.get_draft(draft["draft_id"])["confirmed"]
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0


@pytest.mark.parametrize("change", ["edit", "cancel", "new_turn"])
def test_obsolete_readback_is_discarded_after_provider_returns(store, change):
    draft = reviewed(store)
    started, release = Event(), Event()

    def synthesize(text):
        started.set()
        assert release.wait(5)
        return b"obsolete-audio"

    speech = SpeechReview(Workflow(store, None), synthesize)
    with ThreadPoolExecutor(max_workers=1) as pool:
        result = pool.submit(
            speech.speak, draft["draft_id"], revision=1, content_hash=draft["content_hash"]
        )
        try:
            assert started.wait(5)
            if change == "edit":
                store.update_draft(draft["draft_id"], {"quantity": 2}, expected_revision=1)
            elif change == "cancel":
                store.cancel_draft(draft["draft_id"], expected_revision=1)
            else:
                store.begin_turn(draft["draft_id"], "another correction", expected_revision=1)
        finally:
            release.set()
        outcome = result.result(timeout=5)
    assert outcome.code == "stale_review"
    assert "audio" not in outcome.data


def test_provider_failure_keeps_text_review_usable_and_redacts_error(store):
    draft = reviewed(store)

    def fail(text):
        raise RuntimeError("PRIVATE_PROVIDER_BODY")

    flow = Workflow(store, None)
    result = SpeechReview(flow, fail).speak(
        draft["draft_id"], revision=1, content_hash=draft["content_hash"]
    )
    assert result.code == "speech_failed"
    assert "PRIVATE" not in repr(result)
    assert flow.review(draft["draft_id"]).data["can_confirm"] is True


def test_stale_or_incomplete_review_does_not_call_provider(store):
    calls = []
    speech = SpeechReview(Workflow(store, None), lambda text: calls.append(text))
    draft = store.create_draft({"job_id": "104"}).data
    assert (
        speech.speak(draft["draft_id"], revision=1, content_hash=draft["content_hash"]).code
        == "stale_review"
    )
    draft = reviewed(store)
    assert (
        speech.speak(draft["draft_id"], revision=2, content_hash=draft["content_hash"]).code
        == "stale_review"
    )
    assert calls == []
