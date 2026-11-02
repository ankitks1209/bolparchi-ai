"""Run the local browser prototype. Choose fixtures or explicitly capped live use."""

import argparse
import os
import threading
from pathlib import Path

import uvicorn

from bolparchi import Store
from bolparchi.gemini import GeminiExtractor, ProviderError
from bolparchi.gnani import GnaniSpeech
from bolparchi.speech_runtime import CappedSpeech
from bolparchi.webapp import create_app
from scripts.demo_speech import FixtureSpeech
from scripts.demo_typed_workflow import MESSAGES, fixture_extractor
from scripts.probe_gemini import load_key


class CappedExtractor:
    """A launch-local allowance. Stop after a provider error; never auto-retry."""

    def __init__(self, extractor, limit):
        self.extractor = extractor
        self.remaining = limit
        self.lock = threading.Lock()
        self.stopped = False

    def __call__(self, message, current):
        with self.lock:
            if self.stopped or self.remaining <= 0:
                raise ProviderError("request_allowance_exhausted")
            self.remaining -= 1
            try:
                return self.extractor(message, current)
            except Exception:
                self.stopped = True
                raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--fixtures", action="store_true", help="Scripted extraction; no provider calls"
    )
    modes.add_argument("--live", action="store_true", help="Explicitly enable Gemini requests")
    parser.add_argument("--max-requests", type=int, choices=range(1, 7))
    parser.add_argument(
        "--max-speech-requests",
        type=int,
        choices=range(1, 7),
        help="Explicit combined Gnani STT/TTS allowance; omitted disables live speech",
    )
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--db", type=Path, help="Optional local SQLite path; never publicly served")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Choose a local port from 1024 to 65535.")
    if args.live and args.max_requests is None:
        parser.error("Live use requires --max-requests within your approved allowance.")
    if args.fixtures and (
        args.max_requests is not None
        or args.max_speech_requests is not None
        or args.env_file is not None
    ):
        parser.error("Fixture mode needs no credentials or request allowance.")
    speech_provider = None
    if args.live:
        try:
            extractor = CappedExtractor(
                GeminiExtractor(load_key(args.env_file, os.environ)), args.max_requests
            )
            if args.max_speech_requests is not None:
                speech_provider = CappedSpeech(
                    GnaniSpeech(load_key(args.env_file, os.environ, name="GNANI_API_KEY")),
                    args.max_speech_requests,
                )
        except (ValueError, OSError, UnicodeError):
            parser.error("Cannot load the requested provider keys from private configuration.")
    else:
        extractor = fixture_extractor
        speech_provider = FixtureSpeech()
    path = args.db or Path("artifacts") / (
        "local-live.sqlite" if args.live else "local-fixtures.sqlite"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    store = Store(str(path))
    try:
        app = create_app(
            store,
            extractor,
            mode="live" if args.live else "fixtures",
            examples=[item[0] for item in MESSAGES],
            transcriber=speech_provider.transcribe if speech_provider else None,
            synthesizer=speech_provider.synthesize if speech_provider else None,
        )
        print(
            f"BolParchi local {'LIVE' if args.live else 'FIXTURE'} mode: http://127.0.0.1:{args.port}",
            flush=True,
        )
        uvicorn.run(app, host="127.0.0.1", port=args.port, access_log=False, server_header=False)
    finally:
        store.close()


if __name__ == "__main__":
    main()
