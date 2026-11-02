"""The live probe command is tested offline at its external-provider boundary."""

import subprocess
import sys

import pytest

from bolparchi.gemini import ExtractionResult, ProviderError
from scripts.probe_gemini import load_key, run_probes


PATCH = {"set": {"quantity": 1}, "clear": [], "spoken_job_id": None, "needs_clarification": False}
CASES = [{"id": f"case-{i}", "message": "ek", "expected": PATCH} for i in range(6)]


class Extractor:
    def __init__(self, failure=None):
        self.calls = []
        self.failure = failure

    def extract(self, message, current):
        self.calls.append((message, current))
        if self.failure:
            raise self.failure
        return ExtractionResult(PATCH, "gemini-test", {"totalTokenCount": 10}, 0.25)


def test_probe_never_exceeds_request_cap_and_records_comparison():
    extractor = Extractor()
    report = run_probes(extractor, CASES, max_requests=2)
    assert len(extractor.calls) == report["attempts"] == 2
    assert [result["exact_match"] for result in report["results"]] == [True, True]
    assert report["results"][0]["usage"] == {"totalTokenCount": 10}


@pytest.mark.parametrize("code", ["http_403", "http_429", "timeout", "invalid_response"])
def test_probe_stops_on_first_failure_without_retry(code):
    extractor = Extractor(ProviderError(code))
    report = run_probes(extractor, CASES, max_requests=6)
    assert len(extractor.calls) == report["attempts"] == 1
    assert report["results"][0]["error"] == code


@pytest.mark.parametrize("limit", [0, 7, -1, True, 1.5])
def test_probe_rejects_invalid_budget_before_calls(limit):
    extractor = Extractor()
    with pytest.raises(ValueError):
        run_probes(extractor, CASES, max_requests=limit)
    assert extractor.calls == []


def test_environment_wins_and_missing_key_has_safe_error(tmp_path):
    assert load_key(None, {"GEMINI_API_KEY": "fictional-key"}) == "fictional-key"
    with pytest.raises(ValueError, match="missing_api_key"):
        load_key(None, {})


def test_explicit_env_file_is_parsed_as_data_without_shell_execution(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        '# private config\nGNANI_API_KEY=unrelated\nGEMINI_API_KEY="fictional-key"\n'
    )
    assert load_key(env_file, {}) == "fictional-key"
    env_file.write_text("GEMINI_API_KEY=$(touch should-never-exist)\n")
    assert load_key(env_file, {}) == "$(touch should-never-exist)"
    assert not (tmp_path / "should-never-exist").exists()


def test_duplicate_key_assignments_are_rejected(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("GEMINI_API_KEY=one\nGEMINI_API_KEY=two\n")
    with pytest.raises(ValueError, match="duplicate_api_key"):
        load_key(env_file, {})


def test_cli_requires_explicit_live_flag_before_reading_credentials():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.probe_gemini"], capture_output=True, text=True
    )
    assert result.returncode == 2
    assert "--live" in result.stderr
