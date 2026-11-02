from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest
from fastapi.testclient import TestClient

from bolparchi import Store
from bolparchi.webapp import create_app
from tests.test_browser_audio import wav


def client_for(store, extractor=None, **kwargs):
    return TestClient(
        create_app(store, extractor, **kwargs),
        base_url="http://127.0.0.1:8766",
        headers={"Origin": "http://127.0.0.1:8766", "X-BolParchi-Request": "1"},
    )


@pytest.fixture
def store():
    instance = Store()
    yield instance
    instance.close()


def test_readback_endpoint_returns_audio_for_exact_server_review(store):
    calls = []

    def synthesize(text):
        calls.append(text)
        return b"wav-fixture"

    draft = store.create_draft(
        {"job_id": "104", "diagnosis": "fixed belt", "status": "completed"}
    ).data
    with client_for(store, synthesizer=synthesize) as client:
        response = client.post(
            f"/api/drafts/{draft['draft_id']}/readback",
            json={"revision": 1, "content_hash": draft["content_hash"]},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert response.content == b"wav-fixture"
        assert calls == [
            "Job 104: fixed belt. Kaam ho gaya. Sab sahi hai? Confirm and save dabayein, ya badlav bataiye."
        ]
        assert "blob:" in client.get("/").headers["Content-Security-Policy"]


def test_readback_unavailable_or_stale_never_returns_audio(store):
    draft = store.create_draft({"job_id": "104"}).data
    body = {"revision": 1, "content_hash": draft["content_hash"]}
    path = f"/api/drafts/{draft['draft_id']}/readback"
    with client_for(store) as client:
        assert client.post(path, json=body).json()["code"] == "speech_unavailable"
    with client_for(store, synthesizer=lambda text: b"unexpected") as client:
        response = client.post(path, json=body)
        assert response.json()["code"] == "stale_review"
        assert "audio" not in response.json()["data"]
        assert client.post(path, json={**body, "text": "client supplied speech"}).status_code == 422


def test_recorded_wav_reaches_guarded_transcription_and_review(store):
    calls = []

    def transcribe(audio, *, file_format):
        calls.append((audio, file_format))
        return "motor fixed"

    def extract(message, current):
        assert message == "motor fixed"
        return {
            "set": {"diagnosis": message, "status": "completed"},
            "clear": [],
            "spoken_job_id": None,
            "needs_clarification": False,
        }

    draft = store.create_draft({"job_id": "104"}).data
    with client_for(store, extract, transcriber=transcribe) as client:
        response = client.post(
            f"/api/drafts/{draft['draft_id']}/audio?expected_revision=1",
            content=wav(),
            headers={"Content-Type": "audio/wav"},
        )
        assert response.status_code == 200
        view = response.json()["view"]
        assert view["phase"] == "review"
        assert view["input"]["transcript"] == "motor fixed"
        assert calls == [(wav(), "wav")]
        assert store.list_jobs()[0]["status"] == "open"


def test_invalid_or_oversize_recording_never_reaches_provider(store):
    calls = []
    draft = store.create_draft({"job_id": "104"}).data
    with client_for(store, transcriber=lambda *args, **kwargs: calls.append(1)) as client:
        path = f"/api/drafts/{draft['draft_id']}/audio?expected_revision=1"
        for data in [b"not audio", wav(rate=48000), wav()[:-1]]:
            assert (
                client.post(path, content=data, headers={"Content-Type": "audio/wav"}).status_code
                == 422
            )
        assert (
            client.post(
                path, content=wav(480001), headers={"Content-Type": "audio/wav"}
            ).status_code
            == 413
        )
        assert (
            client.post(path, content=wav(), headers={"Content-Type": "audio/webm"}).status_code
            == 415
        )
        assert calls == []
        assert store.get_draft(draft["draft_id"])["input"] is None


def test_two_empty_transcriptions_prioritize_typing(store):
    draft = store.create_draft({"job_id": "104"}).data
    with client_for(store, transcriber=lambda *args, **kwargs: "") as client:
        for _ in range(2):
            response = client.post(
                f"/api/drafts/{draft['draft_id']}/audio?expected_revision=1",
                content=wav(),
                headers={"Content-Type": "audio/wav"},
            )
            assert response.status_code == 200
        assert response.json()["view"]["prefer_typing"] is True
        assert response.json()["view"]["phase"] == "speech_error"


def test_cancelled_audio_does_not_reach_extraction_after_stt_returns(store):
    started, release = Event(), Event()
    calls = []

    def transcribe(audio, *, file_format):
        started.set()
        assert release.wait(5)
        return "late transcript"

    draft = store.create_draft({"job_id": "104"}).data
    with (
        client_for(store, lambda *args: calls.append(1), transcriber=transcribe) as client,
        ThreadPoolExecutor(max_workers=1) as pool,
    ):
        path = f"/api/drafts/{draft['draft_id']}"
        result = pool.submit(
            client.post,
            path + "/audio?expected_revision=1",
            content=wav(),
            headers={"Content-Type": "audio/wav"},
        )
        try:
            assert started.wait(5)
            assert (
                client.post(path + "/cancel", json={"expected_revision": 1}).json()["view"]["state"]
                == "cancelled"
            )
        finally:
            release.set()
        assert result.result(timeout=5).json()["view"]["state"] == "cancelled"
        assert calls == []
