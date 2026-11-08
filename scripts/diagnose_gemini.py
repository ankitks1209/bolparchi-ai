"""Opt-in isolation of plain generation from the production extraction request."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic

from bolparchi.extraction import ENDPOINT, MODEL, PROMPT_VERSION, SCHEMA_VERSION, GeminiExtractor
from bolparchi.gemini import MAX_RESPONSE_BYTES
from bolparchi.provider_http import ProviderError, request_bytes, validate_key
from bolparchi.provider_json import strict_json
from bolparchi.validation import validate_extraction, validate_message
from scripts.prepare_provider_probes import CURRENT, ROOT
from scripts.probe_gemini import load_key


def plain_request():
    return {
        "contents": [{"role": "user", "parts": [{"text": "Reply with exactly READY."}]}],
        "generationConfig": {
            "maxOutputTokens": 256,
            "thinkingConfig": {"thinkingLevel": "LOW", "includeThoughts": False},
        },
    }


def plain_ready(raw):
    try:
        document = strict_json(raw)
        candidates = document["candidates"]
        if document.get("promptFeedback", {}).get("blockReason") or len(candidates) != 1:
            return False
        candidate = candidates[0]
        parts = candidate["content"]["parts"]
        return (
            candidate["finishReason"] == "STOP"
            and "".join(part["text"] for part in parts if part.get("thought") is not True).strip()
            == "READY"
        )
    except (ValueError, KeyError, TypeError, AttributeError, RecursionError):
        return False


def run_diagnostic(api_key, case, *, max_requests, transport=None, on_progress=None):
    if type(max_requests) is not int or max_requests not in (1, 2):
        raise ValueError("request_limit_must_be_1_or_2")
    validate_key(api_key)
    validate_message(case["message"])
    validate_extraction(case["expected"])
    extractor = GeminiExtractor(api_key, transport=transport)
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "endpoint": ENDPOINT,
        "request_limit": max_requests,
        "automatic_retries": 0,
        "attempts": 0,
        "results": [],
        "evaluation": "diagnostic_not_held_out",
    }
    for stage in ("plain_generation", "structured_extraction")[:max_requests]:
        report["attempts"] += 1
        result = {"stage": stage, "outcome": "started"}
        report["results"].append(result)
        if on_progress:
            on_progress(report)
        started = monotonic()
        try:
            if stage == "plain_generation":
                raw = request_bytes(
                    url=ENDPOINT,
                    headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                    body=json.dumps(plain_request()).encode(),
                    max_bytes=MAX_RESPONSE_BYTES,
                    transport=transport,
                )
                result["outcome"] = (
                    "plain_generation_ok" if plain_ready(raw) else "plain_response_unexpected"
                )
            else:
                extraction = extractor.extract(case["message"], dict(CURRENT))
                result.update(
                    {
                        "outcome": "extraction_match"
                        if extraction.patch == case["expected"]
                        else "extraction_mismatch",
                        "patch": extraction.patch,
                        "model_version": extraction.model_version,
                        "usage": extraction.usage,
                    }
                )
        except ProviderError as exc:
            result["outcome"] = str(exc)
        result["elapsed_seconds"] = round(monotonic() - started, 3)
        if on_progress:
            on_progress(report)
        if result["outcome"] not in {"plain_generation_ok", "extraction_match"}:
            break
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--max-requests", type=int, choices=(1, 2), required=True)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if not args.live:
        parser.error("Pass --live only after approving this new diagnostic allowance.")
    try:
        key = load_key(args.env_file, os.environ)
        validate_key(key)
    except (OSError, UnicodeError, ValueError):
        parser.error("Cannot load the requested provider key from private configuration.")
    case = json.loads((ROOT / "probes/extraction_cases.json").read_text())[0]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = ROOT / "artifacts/provider-probes" / f"gemini-isolation-{stamp}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)

    def save_progress(report):
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        latest = report["results"][-1]
        print(f"{latest['stage']}: {latest['outcome']}", flush=True)

    report = run_diagnostic(key, case, max_requests=args.max_requests, on_progress=save_progress)
    print(f"Attempted {report['attempts']} request(s); redacted report: {destination}")
    return (
        0 if report["results"][-1]["outcome"] in {"plain_generation_ok", "extraction_match"} else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
