from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest
from fastapi.testclient import TestClient

from bolparchi import Store
from bolparchi.recovery import SaveRecovery
from bolparchi.webapp import create_app
from scripts.demo_typed_workflow import MESSAGES, fixture_extractor
from scripts.run_web import CappedExtractor
from bolparchi.provider_http import ProviderError


@pytest.fixture
def store(tmp_path):
    instance = Store(str(tmp_path / "web.sqlite"))
    yield instance
    instance.close()


def client_for(store, extractor=fixture_extractor, recovery=None):
    return TestClient(
        create_app(store, extractor, recovery=recovery),
        base_url="http://127.0.0.1:8766",
        headers={"X-BolParchi-Request": "1", "Origin": "http://127.0.0.1:8766"},
    )


def new_draft(client):
    response = client.post("/api/drafts", json={"job_id": "104"})
    assert response.status_code == 200
    return response.json()["view"]


def completed_draft(client):
    draft = new_draft(client)
    for message, _ in MESSAGES:
        response = client.post(
            f"/api/drafts/{draft['draft_id']}/message",
            json={"message": message, "expected_revision": draft["revision"]},
        )
        assert response.status_code == 200
        draft = response.json()["view"]
    return draft


def test_browser_http_flow_saves_exact_review_once(store):
    with client_for(store) as client:
        response = client.get("/api/jobs")
        assert response.status_code == 200
        assert response.json()["jobs"][0]["job_id"] == "104"
        draft = completed_draft(client)
        assert draft["phase"] == "review"
        assert draft["proposal"]["quantity"] == 1
        assert store.list_jobs()[0]["status"] == "open"
        body = {
            "submission_id": "http-save",
            "revision": draft["revision"],
            "content_hash": draft["content_hash"],
        }
        url = f"/api/drafts/{draft['draft_id']}/save"
        saved = client.post(url, json=body).json()
        assert saved["code"] == "saved"
        assert saved["view"]["receipt"]["submission_id"] == "http-save"
        assert client.post(url, json=body).json()["view"]["receipt"] == saved["view"]["receipt"]
        assert store.conn.execute("SELECT COUNT(*) FROM parts_requests").fetchone()[0] == 1
        assert store.conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 1
        assert store.list_jobs()[0]["status"] == "pending"


def test_http_extractor_error_keeps_transcript_and_retry_uses_it(store):
    calls = []

    def extract(message, current):
        calls.append(message)
        if len(calls) == 1:
            raise RuntimeError("PRIVATE_PROVIDER_BODY")
        return fixture_extractor(message, current)

    with client_for(store, extract) as client:
        draft = new_draft(client)
        path = f"/api/drafts/{draft['draft_id']}"
        failed = client.post(
            path + "/message", json={"message": MESSAGES[0][0], "expected_revision": 1}
        )
        assert "PRIVATE_PROVIDER_BODY" not in failed.text
        view = failed.json()["view"]
        assert view["phase"] == "extraction_error"
        assert view["input"]["transcript"] == MESSAGES[0][0]
        retried = client.post(
            path + "/retry",
            json={"turn_id": view["input"]["turn_id"], "expected_revision": view["revision"]},
        ).json()
        assert retried["view"]["proposal"]["quantity"] == 2
        assert calls == [MESSAGES[0][0], MESSAGES[0][0]]


def test_http_503_exhaustion_preserves_draft_then_manual_retry_recovers(store, monkeypatch):
    calls = []
    monkeypatch.setattr("scripts.run_web.sleep", lambda _: None)

    def extract(message, current):
        calls.append(message)
        if len(calls) <= 3:
            raise ProviderError("http_503")
        return fixture_extractor(message, current)

    capped = CappedExtractor(extract, 4)
    with client_for(store, capped) as client:
        draft = new_draft(client)
        path = f"/api/drafts/{draft['draft_id']}"
        response = client.post(
            path + "/message",
            json={"message": MESSAGES[0][0], "expected_revision": draft["revision"]},
        ).json()
        view = response["view"]
        assert view["phase"] == "extraction_error" and view["can_retry"]
        assert view["proposal"] == draft["proposal"] and not view["can_confirm"]
        assert view["input"]["transcript"] == MESSAGES[0][0]
        assert len(calls) == 3 and capped.remaining == 1
        recovered = client.post(
            path + "/retry",
            json={"turn_id": view["input"]["turn_id"], "expected_revision": view["revision"]},
        ).json()["view"]
        assert recovered["phase"] == "clarify" and recovered["proposal"]["quantity"] == 2
        assert calls == [MESSAGES[0][0]] * 4
        assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0


def test_unknown_save_is_locked_across_http_refresh_then_recovers_receipt(store):
    deliveries = []

    def delayed(draft_id, submission_id):
        deliveries.append((draft_id, submission_id))
        raise TimeoutError()

    with client_for(store, recovery=SaveRecovery(store, send_save=delayed)) as client:
        draft = completed_draft(client)
        path = f"/api/drafts/{draft['draft_id']}"
        body = {
            "submission_id": "late-http",
            "revision": draft["revision"],
            "content_hash": draft["content_hash"],
        }
        assert client.post(path + "/save", json=body).json()["code"] == "unresolved"
        assert len(deliveries) == 3
        refreshed = client.get(path).json()["view"]
        assert refreshed["state"] == "save_unresolved"
        assert refreshed["save_request"]["submission_id"] == "late-http"
        assert (
            client.post(path + "/cancel", json={"expected_revision": draft["revision"]}).json()[
                "code"
            ]
            == "draft_locked"
        )
        assert (
            client.post(path + "/save-status", json={"submission_id": "late-http"}).json()["code"]
            == "unresolved"
        )
        assert len(deliveries) == 3
        assert store.save(*deliveries[0]).code == "saved"
        assert (
            client.post(path + "/save-status", json={"submission_id": "late-http"}).json()["view"][
                "receipt"
            ]["submission_id"]
            == "late-http"
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"job_id": "104", "diagnosis": "injected"},
        {"job_id": 104},
        {"job_id": ""},
        {"job_id": "x" * 20000},
    ],
)
def test_http_creation_rejects_invalid_or_extra_inputs(store, payload):
    with client_for(store) as client:
        response = client.post("/api/drafts", json=payload)
        assert response.status_code in {413, 422}
        assert store.conn.execute("SELECT COUNT(*) FROM drafts").fetchone()[0] == 0


@pytest.mark.parametrize(
    "headers",
    [
        {"Origin": "https://external.example", "X-BolParchi-Request": "1"},
        {"Origin": "null", "X-BolParchi-Request": "1"},
        {"X-BolParchi-Request": "1"},
        {"Origin": "http://127.0.0.1:8766"},
    ],
)
def test_local_api_rejects_cross_origin_or_non_app_mutations(store, headers):
    with TestClient(
        create_app(store, fixture_extractor), base_url="http://127.0.0.1:8766"
    ) as client:
        assert (
            client.post("/api/drafts", json={"job_id": "104"}, headers=headers).status_code == 403
        )
        assert store.conn.execute("SELECT COUNT(*) FROM drafts").fetchone()[0] == 0


def test_static_assets_are_allowlisted_and_errors_do_not_echo_input(store):
    with client_for(store) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]
        assert response.headers["Cache-Control"] == "no-store"
        assert client.get("/style.css").status_code == 200
        assert client.get("/app.js").status_code == 200
        for path in ["/.env", "/requirements.txt", "/bolparchi/store.py", "/docs", "/openapi.json"]:
            assert client.get(path).status_code == 404
        response = client.post(
            "/api/drafts",
            content='{"job_id":"104","token":"DO_NOT_ECHO"}',
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422
        assert "DO_NOT_ECHO" not in response.text
        assert client.get("/", headers={"Host": "external.example"}).status_code == 400


def test_stale_review_and_pending_input_cannot_save_over_http(store):
    with client_for(store) as client:
        draft = completed_draft(client)
        path = f"/api/drafts/{draft['draft_id']}"
        body = {
            "submission_id": "stale-http",
            "revision": draft["revision"] - 1,
            "content_hash": draft["content_hash"],
        }
        rejected = client.post(path + "/save", json=body).json()
        assert rejected["code"] == "stale_confirmation"
        assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
        store.begin_turn(draft["draft_id"], "newer message", expected_revision=draft["revision"])
        body["revision"] = draft["revision"]
        assert client.post(path + "/save", json=body).json()["code"] == "pending_input"


def test_status_lookup_without_receipt_never_claims_rollback(store):
    with client_for(store) as client:
        draft = completed_draft(client)
        response = client.post(
            f"/api/drafts/{draft['draft_id']}/save-status", json={"submission_id": "never-arrived"}
        ).json()
        assert response["code"] == "unresolved"
        assert response["data"]["locked"] is True


@pytest.mark.parametrize("action", ["apply", "discard"])
def test_wrong_job_patch_is_held_until_browser_resolves_it(store, action):
    def extract(message, current):
        return {
            "set": {"diagnosis": "belt adjusted", "status": "completed"},
            "clear": [],
            "spoken_job_id": "105",
            "needs_clarification": False,
        }

    with client_for(store, extract) as client:
        draft = new_draft(client)
        path = f"/api/drafts/{draft['draft_id']}"
        held = client.post(
            path + "/message", json={"message": "Job 105 fixed", "expected_revision": 1}
        ).json()["view"]
        assert held["phase"] == "job_mismatch"
        assert held["proposal"].get("diagnosis") is None
        assert held["can_confirm"] is False
        resolved = client.post(
            path + "/mismatch",
            json={
                "turn_id": held["input"]["turn_id"],
                "action": action,
                "expected_revision": held["revision"],
            },
        ).json()["view"]
        assert resolved["proposal"]["job_id"] == "104"
        assert resolved["can_confirm"] is (action == "apply")
        assert store.list_jobs()[0]["status"] == "open"


def test_http_request_limits_apply_to_streamed_bodies_before_extraction(store):
    calls = []

    def extract(message, current):
        calls.append(message)
        return fixture_extractor(message, current)

    with client_for(store, extract) as client:
        draft = new_draft(client)
        path = f"/api/drafts/{draft['draft_id']}/message"
        response = client.post(
            path,
            content=iter([b'{"message":"', b"x" * 40000, b'","expected_revision":1}']),
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 413
        for payload in [
            {"message": "x" * 2001, "expected_revision": 1},
            {"message": "valid", "expected_revision": True},
            {"message": "valid", "expected_revision": "1"},
        ]:
            assert client.post(path, json=payload).status_code == 422
        assert calls == []


def test_http_unknown_draft_has_no_fabricated_view(store):
    with client_for(store) as client:
        result = client.get("/api/drafts/missing").json()
        assert result["code"] == "not_found"
        assert result["view"] is None


def test_http_cancel_can_complete_while_provider_request_is_still_running(store):
    started, release = Event(), Event()

    def extract(message, current):
        started.set()
        assert release.wait(5)
        return fixture_extractor(message, current)

    with client_for(store, extract) as client, ThreadPoolExecutor(max_workers=1) as pool:
        draft = new_draft(client)
        path = f"/api/drafts/{draft['draft_id']}"
        future = pool.submit(
            client.post, path + "/message", json={"message": MESSAGES[0][0], "expected_revision": 1}
        )
        try:
            assert started.wait(5)
            cancelled = client.post(path + "/cancel", json={"expected_revision": 1}).json()
            assert cancelled["view"]["state"] == "cancelled"
        finally:
            release.set()
        late = future.result(timeout=5).json()
        assert late["view"]["state"] == "cancelled"
        assert late["view"]["proposal"].get("diagnosis") is None
        assert store.list_jobs()[0]["status"] == "open"
