"""Opt-in evaluation of frozen fictional acceptance cases; at most six calls."""

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from time import sleep

from bolparchi.extraction import GeminiExtractor, PROMPT, SCHEMA_VERSION
from scripts.probe_gemini import ROOT, load_key, run_probes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--max-requests", type=int, choices=range(1, 7), required=True)
    args = parser.parse_args()
    if not args.live:
        parser.error("Use --live only for an authorized evaluation run.")
    case_bytes = (ROOT / "probes/acceptance_cases.json").read_bytes()
    cases = json.loads(case_bytes)
    extractor = GeminiExtractor(load_key(args.env_file, os.environ))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = ROOT / "artifacts/provider-probes" / f"acceptance-{stamp}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)

    def progress(report):
        report.update(
            evaluation="frozen_acceptance_cases",
            cases_sha256=hashlib.sha256(case_bytes).hexdigest(),
            prompt_sha256=hashlib.sha256(PROMPT.encode()).hexdigest(),
            schema_version=SCHEMA_VERSION,
            automatic_retries=0,
        )
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        latest = report["results"][-1]
        print(latest["id"], latest.get("error") or latest["exact_match"], flush=True)
        if "error" not in latest and report["attempts"] < min(args.max_requests, len(cases)):
            sleep(16)

    report = run_probes(extractor, cases, max_requests=args.max_requests, on_progress=progress)
    matches = sum(result.get("exact_match", False) for result in report["results"])
    print(f"{matches}/{report['attempts']} exact matches; report: {destination}")
    return 0 if matches == min(args.max_requests, len(cases)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
