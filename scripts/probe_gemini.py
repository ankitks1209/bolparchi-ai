"""Explicit, bounded live probes using fictional fixtures; never saves job records."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic

from bolparchi.fields import SCHEMA_VERSION
from bolparchi.gemini import ENDPOINT, MODEL, PROMPT_VERSION, GeminiExtractor, ProviderError
from bolparchi.validation import validate_extraction, validate_message
from scripts.prepare_provider_probes import CURRENT, ROOT


def run_probes(extractor, cases, *, max_requests, on_progress=None):
    """At most six calls per explicit invocation; stop at the first provider error."""
    if type(max_requests) is not int or not 1 <= max_requests <= 6:
        raise ValueError("request_limit_must_be_1_to_6")
    selected = cases[:max_requests]
    for case in selected:
        validate_message(case["message"])
        validate_extraction(case["expected"])
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "endpoint": ENDPOINT,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "request_limit": max_requests,
        "attempts": 0,
        "results": [],
        "evaluation": "development_fixtures_not_held_out",
    }
    for case in selected:
        report["attempts"] += 1
        started = monotonic()
        try:
            result = extractor.extract(case["message"], dict(CURRENT))
        except ProviderError as exc:
            report["results"].append(
                {
                    "id": case["id"],
                    "error": str(exc),
                    "elapsed_seconds": round(monotonic() - started, 3),
                }
            )
            if on_progress:
                on_progress(report)
            break
        report["results"].append(
            {
                "id": case["id"],
                "patch": result.patch,
                "expected": case["expected"],
                "exact_match": result.patch == case["expected"],
                "model_version": result.model_version,
                "usage": result.usage,
                "elapsed_seconds": round(result.elapsed_seconds, 3),
            }
        )
        if on_progress:
            on_progress(report)
    return report


def load_key(env_file, environ, *, name="GEMINI_API_KEY"):
    """Read one named key; no interpolation, shell evaluation or implicit dotenv."""
    if environ.get(name):
        return environ[name]
    values = []
    if env_file is not None:
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key_name, separator, value = line.partition("=")
            if separator and key_name.strip() == name:
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                values.append(value)
    if len(values) > 1:
        raise ValueError("duplicate_api_key")
    if not values or not values[0]:
        raise ValueError("missing_api_key")
    return values[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly permit external requests")
    parser.add_argument("--max-requests", type=int, choices=range(1, 7), default=1)
    parser.add_argument("--env-file", type=Path, help="Optional local config; never executed")
    args = parser.parse_args()
    if not args.live:
        parser.error("Pass --live only after approving the request allowance.")
    try:
        extractor = GeminiExtractor(load_key(args.env_file, os.environ))
    except (OSError, UnicodeError, ValueError):
        parser.error("Cannot load a valid GEMINI_API_KEY; check private environment configuration.")
    cases = json.loads((ROOT / "probes" / "extraction_cases.json").read_text())
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = ROOT / "artifacts" / "provider-probes" / f"gemini-{stamp}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)

    def save_progress(report):
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        latest = report["results"][-1]
        outcome = latest.get("error") or ("exact_match" if latest["exact_match"] else "mismatch")
        print(f"{latest['id']}: {outcome}", flush=True)

    report = run_probes(extractor, cases, max_requests=args.max_requests, on_progress=save_progress)
    print(f"Attempted {report['attempts']} request(s); redacted report: {destination}")
    return (
        1
        if any("error" in result or not result["exact_match"] for result in report["results"])
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
