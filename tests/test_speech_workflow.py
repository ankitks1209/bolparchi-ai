"""Real SQLite speech-turn lifecycle; only external providers are substituted."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from bolparchi import Store
from bolparchi.provider_http import ProviderError
from bolparchi.workflow import Workflow


def patch(**changes):
    return {"set": changes, "clear": [], "spoken_job_id": None, "needs_clarification": False}


@pytest.fixture
def store(tmp_path):
    instance = Store(str(tmp_path / "speech.db"))
    yield instance
    instance.close()


def test_speech_transcript_enters_same_review_and_explicit_save_path(store):
    calls = []

    def transcribe(audio, *, file_format):
        calls.append((audio, file_format))
        return "Motor theek. Do nahi, ek motor laga. Kaam poora."

    def extract(message, current):
        assert message == "Motor theek. Do nahi, ek motor laga. Kaam poora."
        assert current["job_id"] == "104"
        return patch(diagnosis="motor theek", status="completed", part_needed="motor", quantity=1)

    flow = Workflow(store, extract, transcriber=transcribe)
    draft = flow.select_job("104").data
    result = flow.submit_audio(
        draft["draft_id"], b"fictional audio", file_format="wav", expected_revision=1
    )
    assert result.data.get("phase") == "review"
    assert calls == [(b"fictional audio", "wav")]
    assert result.data["input"]["transcript"] == "Motor theek. Do nahi, ek motor laga. Kaam poora."
    assert result.data["proposal"]["quantity"] == 1
    assert store.save(draft["draft_id"], "speech-save").code == "not_confirmed"
    assert store.confirm(draft["draft_id"], 2, result.data["content_hash"]).ok
    assert store.save(draft["draft_id"], "speech-save").ok
    assert store.conn.execute("SELECT COUNT(*) FROM parts_requests").fetchone()[0] == 1


def test_recording_revokes_old_approval_and_blocks_save_during_transcription(store):
    draft = store.create_draft({"job_id": "104", "diagnosis": "motor", "status": "completed"}).data
    assert store.confirm(draft["draft_id"], 1, draft["content_hash"]).ok
    observed = []

    def transcribe(audio, *, file_format):
        snapshot = flow.review(draft["draft_id"]).data
        observed.append(snapshot["phase"])
        assert not snapshot["confirmed"] and not snapshot["can_confirm"]
        assert store.confirm(draft["draft_id"], 1, draft["content_hash"]).code == "pending_input"
        assert store.save(draft["draft_id"], "early-save").code == "pending_input"
        return "Ek motor laga"

    flow = Workflow(
        store, lambda *_: patch(part_needed="motor", quantity=1), transcriber=transcribe
    )
    flow.submit_audio(draft["draft_id"], b"fictional", file_format="wav", expected_revision=1)
    assert observed == ["transcribing"]
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0


@pytest.mark.parametrize("finish", ["result", "error"])
@pytest.mark.parametrize("replacement", ["typed", "audio", "edit", "cancel"])
def test_late_transcription_cannot_replace_new_work_across_connections(
    store, tmp_path, finish, replacement
):
    entered, release = Event(), Event()
    extracted = []

    def transcribe(audio, *, file_format):
        if audio == b"old":
            entered.set()
            assert release.wait(5)
            if finish == "error":
                raise ProviderError("empty_transcript")
            return "old transcript"
        return "new transcript"

    def extract(message, current):
        extracted.append(message)
        return patch(diagnosis=message, status="completed")

    other_store = Store(str(tmp_path / "speech.db"))
    flow = Workflow(store, extract, transcriber=transcribe)
    other = Workflow(other_store, extract, transcriber=transcribe)
    draft = flow.select_job("104").data
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                flow.submit_audio, draft["draft_id"], b"old", file_format="wav", expected_revision=1
            )
            try:
                assert entered.wait(5)
                if replacement == "typed":
                    replacement_result = other.submit(
                        draft["draft_id"], "new transcript", expected_revision=1
                    )
                elif replacement == "audio":
                    replacement_result = other.submit_audio(
                        draft["draft_id"], b"new", file_format="wav", expected_revision=1
                    )
                elif replacement == "edit":
                    replacement_result = other_store.update_draft(
                        draft["draft_id"], {"diagnosis": "new transcript"}, expected_revision=1
                    )
                else:
                    replacement_result = other.cancel(draft["draft_id"], expected_revision=1)
                assert replacement_result.ok
                before = other_store.get_draft(draft["draft_id"])
            finally:
                release.set()
            assert future.result(timeout=5).code == (
                "cancelled" if replacement == "cancel" else "stale_response"
            )
        assert store.get_draft(draft["draft_id"]) == before
        assert "old transcript" not in extracted
        assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
    finally:
        other_store.close()


@pytest.mark.parametrize("returned_empty", [True, False])
def test_two_empty_attempts_preserve_previous_text_and_prioritize_typing(store, returned_empty):
    def transcribe(*args, **kwargs):
        if returned_empty:
            return " \n "
        raise ProviderError("empty_transcript")

    extracted = []

    def extract(message, current):
        extracted.append(message)
        return patch(diagnosis="motor", status="completed")

    flow = Workflow(store, extract, transcriber=transcribe)
    draft = flow.select_job("104").data
    previous = flow.submit(draft["draft_id"], "Original usable message", expected_revision=1).data
    for count in (1, 2):
        failed = flow.submit_audio(
            draft["draft_id"], b"empty speech", file_format="wav", expected_revision=2
        )
        assert failed.data.get("phase") == "speech_error"
        assert failed.data["proposal"] == previous["proposal"]
        assert failed.data["input"]["transcript"] == "Original usable message"
        assert failed.data["offer_typing"] is True
        assert failed.data["prefer_typing"] is (count == 2)
        assert failed.data["empty_speech_attempts"] == count
        assert not failed.data["can_confirm"] and not failed.data["can_retry"]
        assert store.save(draft["draft_id"], "empty-save").code == "pending_input"
    assert extracted == ["Original usable message"]
    typed = flow.submit(draft["draft_id"], "Typed replacement", expected_revision=2)
    assert typed.data["phase"] == "review"
    assert typed.data["empty_speech_attempts"] == 0


@pytest.mark.parametrize("transcript", [None, 123, "x" * 2001])
def test_invalid_transcript_leaves_recoverable_speech_error_without_extraction(store, transcript):
    extracted = []
    flow = Workflow(
        store, lambda *args: extracted.append(args), transcriber=lambda *a, **kw: transcript
    )
    draft = flow.select_job("104").data
    failed = flow.submit_audio(
        draft["draft_id"], b"fictional", file_format="wav", expected_revision=1
    )
    assert failed.data.get("phase") == "speech_error"
    assert failed.data["offer_typing"] and failed.data["can_cancel"]
    assert not failed.data["can_confirm"]
    assert extracted == []


def test_extraction_retry_reuses_transcript_without_retranscribing(store):
    transcribed, extracted = [], []

    def transcribe(audio, *, file_format):
        transcribed.append(audio)
        return "Motor theek"

    def extract(message, current):
        extracted.append(message)
        if len(extracted) == 1:
            raise RuntimeError("private provider error")
        return patch(diagnosis="motor", status="completed")

    flow = Workflow(store, extract, transcriber=transcribe)
    draft = flow.select_job("104").data
    failed = flow.submit_audio(
        draft["draft_id"], b"fictional", file_format="wav", expected_revision=1
    )
    assert failed.data["phase"] == "extraction_error"
    assert failed.data["input"]["transcript"] == "Motor theek"
    assert "private provider error" not in repr(failed)
    retried = flow.retry(draft["draft_id"], failed.data["input"]["turn_id"], expected_revision=1)
    assert retried.data["phase"] == "review"
    assert len(transcribed) == 1 and extracted == ["Motor theek", "Motor theek"]


@pytest.mark.parametrize("audio", [b"", None, "not bytes"])
def test_invalid_audio_does_not_reserve_a_turn_or_call_provider(store, audio):
    calls = []
    flow = Workflow(store, lambda *_: {}, transcriber=lambda *a, **kw: calls.append(a))
    draft = flow.select_job("104").data
    result = flow.submit_audio(draft["draft_id"], audio, file_format="wav", expected_revision=1)
    assert result.code == "invalid_input"
    assert not calls and store.get_draft(draft["draft_id"])["input"] is None


def test_empty_attempt_count_survives_reopen_and_successful_speech_resets_it(store, tmp_path):
    flow = Workflow(
        store,
        lambda *_: patch(diagnosis="motor", status="completed"),
        transcriber=lambda *a, **kw: "",
    )
    draft = flow.select_job("104").data
    flow.submit_audio(draft["draft_id"], b"empty", file_format="wav", expected_revision=1)
    flow.submit_audio(draft["draft_id"], b"empty", file_format="wav", expected_revision=1)
    reopened = Store(str(tmp_path / "speech.db"))
    try:
        next_flow = Workflow(
            reopened,
            lambda *_: patch(diagnosis="motor", status="completed"),
            transcriber=lambda *a, **kw: "Motor theek",
        )
        assert next_flow.review(draft["draft_id"]).data["prefer_typing"]
        result = next_flow.submit_audio(
            draft["draft_id"], b"usable", file_format="wav", expected_revision=1
        )
        assert result.data["phase"] == "review"
        assert result.data["empty_speech_attempts"] == 0
    finally:
        reopened.close()


def test_speech_schema_addition_preserves_an_existing_saved_receipt(tmp_path):
    import sqlite3

    path = str(tmp_path / "old.db")
    old = Store(path)
    draft = old.create_draft({"job_id": "104", "diagnosis": "motor", "status": "completed"}).data
    assert old.confirm(draft["draft_id"], 1, draft["content_hash"]).ok
    receipt = old.save(draft["draft_id"], "old-submission").data
    old.close()
    # Remove only the new additive table from this temporary DB to represent
    # the previous schema. Existing records and receipts remain real SQLite data.
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE draft_speech")
    upgraded = Store(path)
    try:
        assert upgraded.get_draft(draft["draft_id"])["receipt"] == receipt
        assert upgraded.save(draft["draft_id"], "old-submission").data == receipt
        assert upgraded.get_draft(draft["draft_id"])["empty_speech_attempts"] == 0
    finally:
        upgraded.close()


def test_transcription_unavailable_preserves_current_draft(store):
    flow = Workflow(store, lambda *_: {})
    draft = flow.select_job("104").data
    before = store.get_draft(draft["draft_id"])
    result = flow.submit_audio(draft["draft_id"], b"audio", file_format="wav", expected_revision=1)
    assert result.code == "transcription_unavailable"
    assert store.get_draft(draft["draft_id"]) == before


def test_provider_adapters_compose_with_the_guarded_speech_workflow(store):
    import json

    from bolparchi.gemini import GeminiExtractor
    from bolparchi.gnani import GnaniSpeech

    stt_body = json.dumps({"success": True, "transcript": "Motor theek. Kaam poora."}).encode()
    model_body = json.dumps(
        {
            "candidates": [
                {
                    "finishReason": "STOP",
                    "content": {
                        "parts": [
                            {"text": json.dumps(patch(diagnosis="motor theek", status="completed"))}
                        ]
                    },
                }
            ]
        }
    ).encode()
    speech = GnaniSpeech("fictional-key", transport=lambda **_: stt_body)
    extractor = GeminiExtractor("fictional-key", transport=lambda **_: model_body)
    flow = Workflow(store, extractor, transcriber=speech.transcribe)
    draft = flow.select_job("104").data
    result = flow.submit_audio(
        draft["draft_id"], b"synthetic encoded audio", file_format="wav", expected_revision=1
    )
    assert result.data["phase"] == "review"
    assert result.data["proposal"]["diagnosis"] == "motor theek"
    assert result.data["input"]["transcript"] == "Motor theek. Kaam poora."
    assert not result.data["confirmed"]
    assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
