from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from bolparchi import Store
from bolparchi.provider_http import ProviderError
from bolparchi.workflow import Workflow
from scripts.run_web import CappedExtractor


def test_live_allowance_is_shared_across_concurrent_browser_requests():
    calls = []

    def extract(message, current):
        calls.append(message)
        return {"set": {"quantity": 1}}

    capped = CappedExtractor(extract, 2)

    def request(number):
        try:
            return capped(str(number), {})
        except ProviderError:
            return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(request, range(4)))
    assert len(calls) == 2
    assert sum(item is not None for item in results) == 2


def test_provider_failure_stops_further_requests_without_exposing_error():
    calls = []

    def extract(message, current):
        calls.append(message)
        raise ProviderError("http_403")

    capped = CappedExtractor(extract, 3)
    with pytest.raises(ProviderError, match="http_403"):
        capped("first", {})
    with pytest.raises(ProviderError, match="request_allowance_exhausted"):
        capped("retry", {})
    assert calls == ["first"]


def test_explicit_retry_after_three_503s_uses_the_same_remaining_allowance(monkeypatch):
    calls = []
    monkeypatch.setattr("scripts.run_web.sleep", lambda _: None)

    def extract(message, current):
        calls.append(message)
        if len(calls) <= 3:
            raise ProviderError("http_503")
        return {"set": {"quantity": 1}}

    capped = CappedExtractor(extract, 4)
    with pytest.raises(ProviderError, match="http_503"):
        capped("original message", {})
    assert calls == ["original message"] * 3, "Stop after the third attempt in this action"
    assert capped("original message", {}) == {"set": {"quantity": 1}}
    with pytest.raises(ProviderError, match="request_allowance_exhausted"):
        capped("another request", {})
    assert calls == ["original message"] * 4


def test_503_recovers_with_bounded_backoff_and_counts_every_attempt(monkeypatch):
    calls, delays = [], []
    monkeypatch.setattr("scripts.run_web.sleep", delays.append, raising=False)

    def extract(message, current):
        calls.append((message, dict(current)))
        if len(calls) < 3:
            raise ProviderError("http_503")
        return {"set": {"quantity": 1}}

    capped = CappedExtractor(extract, 3)
    try:
        result = capped("Do nahi, ek motor.", {"quantity": 2})
    except ProviderError:
        result = None
    assert result == {"set": {"quantity": 1}}, "A transient 503 should recover within the action"
    assert calls == [("Do nahi, ek motor.", {"quantity": 2})] * 3
    assert delays == [1, 2]
    assert capped.remaining == 0


def test_cancel_during_backoff_prevents_the_next_provider_attempt(monkeypatch, tmp_path):
    calls = []

    def extract(message, current):
        calls.append(message)
        raise ProviderError("http_503")

    store = Store(str(tmp_path / "cancel.sqlite"))
    try:
        flow = Workflow(store, CappedExtractor(extract, 6))
        draft = flow.select_job("104").data

        def cancel(_):
            view = flow.review(draft["draft_id"]).data
            assert flow.cancel(draft["draft_id"], expected_revision=view["revision"]).ok

        monkeypatch.setattr("scripts.run_web.sleep", cancel)
        flow.submit(draft["draft_id"], "Motor kharab hai.", expected_revision=draft["revision"])
        assert calls == ["Motor kharab hai."], "Cancelled work must not spend another attempt"
        assert flow.review(draft["draft_id"]).data["state"] == "cancelled"
        assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
    finally:
        store.close()


@pytest.mark.parametrize(
    "code", ["http_400", "http_401", "http_403", "http_429", "invalid_response"]
)
def test_nontransient_errors_never_retry_or_spend_remaining_allowance(code, monkeypatch):
    calls, delays = [], []
    monkeypatch.setattr("scripts.run_web.sleep", delays.append)

    def extract(message, current):
        calls.append(message)
        raise ProviderError(code)

    capped = CappedExtractor(extract, 6)
    with pytest.raises(ProviderError, match=code):
        capped("message", {})
    with pytest.raises(ProviderError, match="request_allowance_exhausted"):
        capped("message", {})
    assert calls == ["message"] and delays == [] and capped.remaining == 5


def test_process_allowance_stops_retries_before_the_action_limit(monkeypatch):
    calls, delays = [], []
    monkeypatch.setattr("scripts.run_web.sleep", delays.append)

    def extract(message, current):
        calls.append(message)
        raise ProviderError("http_503")

    capped = CappedExtractor(extract, 2)
    with pytest.raises(ProviderError, match="http_503"):
        capped("message", {})
    assert calls == ["message", "message"] and delays == [1]
    with pytest.raises(ProviderError, match="request_allowance_exhausted"):
        capped("message", {})
    assert len(calls) == 2


def test_deadline_returns_without_waiting_for_late_transport_and_blocks_overlap():
    entered, release, finished = Event(), Event(), Event()
    calls = []

    def extract(message, current):
        calls.append(message)
        entered.set()
        try:
            assert release.wait(2)
            return {"set": {"quantity": 1}}
        finally:
            finished.set()

    capped = CappedExtractor(extract, 6, timeout=0.05)
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(capped, "slow", {})
            assert entered.wait(1)
            with pytest.raises(ProviderError, match="timeout"):
                future.result(timeout=1)
        with pytest.raises(ProviderError, match="request_in_progress"):
            capped("overlap", {})
        assert calls == ["slow"] and capped.remaining == 5
    finally:
        release.set()
        assert finished.wait(1)


def test_backoff_must_fit_inside_overall_deadline(monkeypatch):
    now, delays, calls = [0], [], []
    monkeypatch.setattr("scripts.run_web.monotonic", lambda: now[0])
    monkeypatch.setattr("scripts.run_web.sleep", delays.append)

    def extract(message, current):
        calls.append(message)
        now[0] = 29.5
        raise ProviderError("http_503")

    with pytest.raises(ProviderError, match="timeout"):
        CappedExtractor(extract, 6)("message", {})
    assert calls == ["message"] and delays == []


def test_newer_turn_during_backoff_prevents_retry_even_at_same_revision(monkeypatch, tmp_path):
    calls = []

    def extract(message, current):
        calls.append(message)
        raise ProviderError("http_503")

    store = Store(str(tmp_path / "superseded.sqlite"))
    try:
        flow = Workflow(store, CappedExtractor(extract, 6))
        draft = flow.select_job("104").data

        def replace(_):
            assert store.begin_turn(
                draft["draft_id"], "Newer update", expected_revision=draft["revision"]
            ).ok

        monkeypatch.setattr("scripts.run_web.sleep", replace)
        flow.submit(draft["draft_id"], "Old update", expected_revision=draft["revision"])
        assert calls == ["Old update"]
        view = flow.review(draft["draft_id"]).data
        assert view["phase"] == "processing" and view["input"]["transcript"] == "Newer update"
    finally:
        store.close()


def test_timed_out_success_cannot_mutate_the_workflow_later(tmp_path):
    release = Event()

    def extract(message, current):
        assert release.wait(2)
        return {
            "set": {"diagnosis": "Motor repaired", "status": "completed"},
            "clear": [],
            "spoken_job_id": None,
            "needs_clarification": False,
        }

    store = Store(str(tmp_path / "late.sqlite"))
    capped = CappedExtractor(extract, 2, timeout=0.05)
    try:
        flow = Workflow(store, capped)
        draft = flow.select_job("104").data
        failed = flow.submit(draft["draft_id"], "Repair done", expected_revision=draft["revision"])
        assert failed.data["phase"] == "extraction_error"
        assert failed.data["proposal"] == draft["proposal"]
        release.set()
        assert capped.in_flight.wait(1)
        assert flow.review(draft["draft_id"]).data == failed.data
        assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
    finally:
        release.set()
        store.close()


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (ProviderError("http_429"), "http_429"),
        (RuntimeError("private-key-value"), "provider_failure"),
    ],
)
def test_live_failure_logs_only_an_allowlisted_code(caplog, error, expected):
    def extract(message, current):
        raise error

    with pytest.raises(type(error)):
        CappedExtractor(extract, 1)("fictional update", {})
    assert expected in caplog.text
    assert "private-key-value" not in caplog.text
