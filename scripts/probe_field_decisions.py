"""Opt-in targeted development checks; not the frozen acceptance evaluation."""

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from time import sleep

from bolparchi.gemini import MODEL
from bolparchi.gemini_decisions import (
    FieldDecisionExtractor,
    PROMPT,
    PROMPT_VERSION,
    SCHEMA_VERSION,
)
from bolparchi.provider_http import safe_error_code
from scripts.probe_gemini import load_key


def matches(patch, case):
    values = patch["set"]
    return (
        all(values.get(k) == v for k, v in case["set_values"].items())
        and all(
            isinstance(values.get(k), str) and v.casefold() in values[k].casefold()
            for k, v in case["text_contains"].items()
        )
        and all(k not in values for k in case.get("absent", []))
        and patch["clear"] == case["clear"]
        and patch["needs_clarification"] == case["needs_clarification"]
        and patch["spoken_job_id"] is None
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--max-requests", type=int, choices=range(1, 7), required=True)
    args = parser.parse_args()
    if not args.live:
        parser.error("Explicit --live is required for authorized provider testing.")
    data = Path("probes/field_decision_cases.json").read_bytes()
    cases = json.loads(data)[: args.max_requests]
    extractor = FieldDecisionExtractor(load_key(args.env_file, os.environ))
    path = Path("artifacts/provider-probes") / (
        "field-decision-cases-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + ".json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "evaluation": "targeted_development_checks_not_exact_patch_or_held_out_accuracy",
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "cases_sha256": hashlib.sha256(data).hexdigest(),
        "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest(),
        "request_limit": args.max_requests,
        "automatic_retries": 0,
        "results": [],
    }
    for case in cases:
        entry = {"id": case["id"], "outcome": "started"}
        report["results"].append(entry)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        try:
            result = extractor.extract(case["message"], case["current"])
            entry.update(
                outcome="ok",
                checks_passed=matches(result.patch, case),
                patch=result.patch,
                model_version=result.model_version,
                seconds=round(result.elapsed_seconds, 3),
            )
        except Exception as exc:
            entry["outcome"] = safe_error_code(exc)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(case["id"], entry.get("checks_passed", entry["outcome"]), flush=True)
        if entry["outcome"] != "ok":
            break
        if len(report["results"]) < len(cases):
            sleep(16)
    passed = sum(r.get("checks_passed", False) for r in report["results"])
    print(
        f"{passed}/{len(cases)} targeted cases passed; {len(report['results'])} attempted; {path}"
    )
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
