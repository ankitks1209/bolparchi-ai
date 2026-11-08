"""Opt-in real-provider acceptance with a supplied fictional repair recording.

At most 3 Gemini and 2 Gnani requests. Stops on any failure, never retries.
This tests a retained human recording, not fresh microphone capture or listening.
"""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from time import monotonic, sleep

from bolparchi import Store, new_submission_id
from bolparchi.extraction import GeminiExtractor, MODEL, PROMPT_VERSION, SCHEMA_VERSION
from bolparchi.gnani import GnaniSpeech
from bolparchi.provider_http import safe_error_code
from bolparchi.recovery import SaveRecovery
from bolparchi.speech_review import SpeechReview
from bolparchi.workflow import Workflow
from scripts.probe_gemini import load_key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("recording", type=Path)
    args = parser.parse_args()
    if not args.live:
        parser.error("Explicit --live is required for the authorized provider test.")
    raw = args.recording.read_bytes()
    file_format = args.recording.suffix.removeprefix(".").lower()
    gemini = GeminiExtractor(load_key(args.env_file, os.environ))
    gnani = GnaniSpeech(load_key(args.env_file, os.environ, name="GNANI_API_KEY"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    directory = Path("artifacts/live-workflow") / stamp
    directory.mkdir(parents=True)
    report = {
        "input": "retained_human_recording",
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "limits": {"gemini": 3, "gnani": 2},
        "calls": [],
        "steps": [],
        "outcome": "started",
    }

    def persist():
        (directory / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        )

    def call(provider, operation, fn):
        assert sum(c["provider"] == provider for c in report["calls"]) < report["limits"][provider]
        entry = {"provider": provider, "operation": operation, "outcome": "started"}
        report["calls"].append(entry)
        persist()
        started = monotonic()
        try:
            result = fn()
            entry["outcome"] = "ok"
            return result
        except Exception as exc:
            entry["outcome"] = safe_error_code(exc)
            raise
        finally:
            entry["seconds"] = round(monotonic() - started, 3)
            persist()
            print(provider, operation, entry["outcome"], flush=True)

    def extract(message, current):
        result = call("gemini", "extract", lambda: gemini.extract(message, current))
        report["calls"][-1].update(model_version=result.model_version, usage=result.usage)
        persist()
        return result.patch

    def transcribe(audio, *, file_format):
        return call("gnani", "stt", lambda: gnani.transcribe(audio, file_format=file_format))

    def synthesize(text):
        return call("gnani", "tts", lambda: gnani.synthesize(text))

    store = Store(str(directory / "records.sqlite"))
    flow = Workflow(store, extract, transcriber=transcribe)
    try:
        draft = flow.select_job("104").data
        result = flow.submit_audio(
            draft["draft_id"], raw, file_format=file_format, expected_revision=draft["revision"]
        )
        report["steps"].append({"step": "speech_to_review", "result": asdict(result)})
        persist()
        assert result.ok and result.data["phase"] == "review", "speech_to_review_failed"
        draft = result.data
        assert draft["proposal"]["quantity"] == 1, "within_message_correction_failed"
        assert draft["proposal"]["status"] == "pending", "status_mismatch"
        assert store.save(draft["draft_id"], new_submission_id()).code == "not_confirmed"
        for message, phase in [
            ("Follow-up hata do.", "clarify"),
            ("Kal shaam aana hai.", "review"),
        ]:
            sleep(16)
            result = flow.submit(draft["draft_id"], message, expected_revision=draft["revision"])
            report["steps"].append({"step": message, "result": asdict(result)})
            persist()
            assert result.ok and result.data["phase"] == phase, "clarification_flow_failed"
            draft = result.data
            assert draft["proposal"]["quantity"] == 1, "quantity_changed_unexpectedly"
        spoken = SpeechReview(flow, synthesize).speak(
            draft["draft_id"], revision=draft["revision"], content_hash=draft["content_hash"]
        )
        assert spoken.ok, "readback_failed"
        (directory / "readback.wav").write_bytes(spoken.data["audio"])
        assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
        submission = new_submission_id()
        saved = SaveRecovery(store).save(
            draft["draft_id"],
            submission,
            revision=draft["revision"],
            content_hash=draft["content_hash"],
        )
        report["steps"].append(
            {"step": "explicit_test_confirmation_and_save", "result": asdict(saved)}
        )
        assert saved.ok, "save_failed"
        assert store.save(draft["draft_id"], submission).ok
        assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 1
        assert store.conn.execute("SELECT quantity FROM parts_requests").fetchone()[0] == 1
        report["outcome"] = "passed"
    except Exception as exc:
        report["outcome"] = "failed"
        report["failure"] = str(exc) if isinstance(exc, AssertionError) else safe_error_code(exc)
    finally:
        store.close()
        persist()
    print(f"{report['outcome']}: {directory}")
    return 0 if report["outcome"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
