import io
import json
from urllib.error import HTTPError

import pytest

from scripts.diagnose_gemini import run_diagnostic

PATCH = {"set": {"quantity": 1}, "clear": [], "spoken_job_id": None, "needs_clarification": False}
CASE = {"id": "correction", "message": "Do nahi, ek motor.", "expected": PATCH}
DECISIONS = {
    "fields": {
        "diagnosis": {"operation": "not_mentioned", "value": None, "evidence": ""},
        "status": {"operation": "not_mentioned", "value": None, "evidence": ""},
        "part_needed": {"operation": "not_mentioned", "value": None, "evidence": ""},
        "quantity": {"operation": "set", "value": 1, "evidence": "ek motor"},
        "follow_up": {"operation": "not_mentioned", "value": None, "evidence": ""},
    },
    "spoken_job_id": None,
    "job_evidence": "",
    "needs_clarification": False,
}


def response(text):
    return json.dumps(
        {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": text}]}}]}
    ).encode()


def test_plain_generation_precedes_unchanged_extraction_with_a_shared_cap():
    calls, progress = [], []

    def transport(**kwargs):
        calls.append(json.loads(kwargs["body"]))
        return response("READY" if len(calls) == 1 else json.dumps(DECISIONS))

    report = run_diagnostic(
        "test-key",
        CASE,
        max_requests=2,
        transport=transport,
        on_progress=lambda r: progress.append(json.loads(json.dumps(r))),
    )
    assert len(calls) == report["attempts"] == 2
    assert "responseFormat" not in calls[0]["generationConfig"]
    assert "systemInstruction" not in calls[0]
    assert "responseFormat" in calls[1]["generationConfig"]
    assert [r["outcome"] for r in report["results"]] == ["plain_generation_ok", "extraction_match"]
    assert [r["attempts"] for r in progress] == [1, 1, 2, 2]


def test_single_request_cap_never_reaches_extraction():
    calls = []

    def transport(**kwargs):
        calls.append(kwargs)
        return response("READY")

    report = run_diagnostic("test-key", CASE, max_requests=1, transport=transport)
    assert len(calls) == report["attempts"] == 1
    assert report["results"][0]["outcome"] == "plain_generation_ok"


def test_first_provider_error_stops_and_redacts_without_retry():
    calls = []

    def transport(**kwargs):
        calls.append(kwargs)
        raise HTTPError(
            kwargs["url"], 503, "secret test-key details", {}, io.BytesIO(b"private provider body")
        )

    report = run_diagnostic("test-key", CASE, max_requests=2, transport=transport)
    assert len(calls) == report["attempts"] == 1
    assert report["results"][0]["outcome"] == "http_503"
    assert "secret" not in json.dumps(report) and "test-key" not in json.dumps(report)


@pytest.mark.parametrize(
    "raw", [b"not JSON", response("unexpected private output"), b'{"candidates": []}']
)
def test_unusable_plain_response_stops_before_extraction_and_is_not_logged(raw):
    calls = []

    def transport(**kwargs):
        calls.append(kwargs)
        return raw

    report = run_diagnostic("test-key", CASE, max_requests=2, transport=transport)
    assert len(calls) == report["attempts"] == 1
    assert report["results"][0]["outcome"] == "plain_response_unexpected"
    assert "private output" not in json.dumps(report)
