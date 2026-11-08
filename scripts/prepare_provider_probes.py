"""Prepare fictional request files offline: python -m scripts.prepare_provider_probes.

This utility makes no requests and reads no credentials. It shares the adapter's
request builder; generating inputs is not evidence of provider success.
"""

import argparse
import json
from pathlib import Path

from bolparchi.extraction import (
    ENDPOINT,
    MODEL,
    PROMPT_VERSION,
    SCHEMA_VERSION,
    build_request,
    extraction_schema,
)
from bolparchi.validation import validate_extraction, validate_message


ROOT = Path(__file__).resolve().parents[1]
CURRENT = {
    "job_id": "104",
    "diagnosis": "motor kharab",
    "status": "pending",
    "part_needed": "motor",
    "quantity": 2,
    "follow_up": "kal shaam",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "provider-probes")
    args = parser.parse_args()
    cases = json.loads((ROOT / "probes" / "extraction_cases.json").read_text())
    args.output.mkdir(parents=True, exist_ok=True)

    def write(name, value):
        (args.output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")

    write("schema.json", extraction_schema())
    for case in cases:
        validate_message(case["message"])
        validate_extraction(case["expected"])
        write(case["id"] + ".json", build_request(case["message"], CURRENT))
    write(
        "timbre.json",
        {
            "text": "कितने मोटर चाहिए?",
            "voice": "Nalini",
            "model": "timbre-v2.5",
            "language": "hi-IN",
            "speed": 1.0,
            "audio_config": {
                "sample_rate": 48000,
                "num_channels": 1,
                "sample_width": 2,
                "encoding": "linear_pcm",
                "container": "wav",
            },
        },
    )
    write(
        "manifest.json",
        {
            "status": "prepared_offline_not_probed",
            "model": MODEL,
            "prompt_version": PROMPT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "gemini_endpoint": ENDPOINT,
            "tts_endpoint": "https://api.vachana.ai/api/v1/tts/inference",
            "stt_endpoint": "https://api.vachana.ai/stt/v3",
            "cases": [case["id"] for case in cases],
            "expected": {case["id"]: case["expected"] for case in cases},
        },
    )
    print(f"Prepared {len(cases)} extraction cases and one TTS request in {args.output}.")
    print("No credentials read; no network calls made. Real provider results remain unverified.")


if __name__ == "__main__":
    main()
