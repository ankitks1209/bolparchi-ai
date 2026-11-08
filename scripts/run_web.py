"""Run the local browser prototype. Choose fixtures or explicitly capped live use."""

import argparse
import logging
import os
import threading
from pathlib import Path
from time import monotonic, sleep

import uvicorn

from bolparchi import Store
from bolparchi.extraction import GeminiExtractor
from bolparchi.provider_http import ProviderError
from bolparchi.gnani import GnaniSpeech
from bolparchi.provider_http import safe_error_code
from bolparchi.speech_runtime import CappedSpeech
from bolparchi.webapp import create_app
from scripts.demo_speech import FixtureSpeech
from scripts.demo_typed_workflow import MESSAGES, fixture_extractor
from scripts.probe_gemini import load_key


class CappedExtractor:
    """Serialize extraction, cap all attempts, and bound caller wait to 30 seconds.

    Only HTTP 503 is retried automatically (three attempts, delays 1s and 2s).
    A timed-out transport may still finish in its daemon worker, but its result
    is discarded and no new transport starts until it exits. Workers never own
    workflow/store callbacks, so a late completion cannot mutate a draft.
    """

    def __init__(self, extractor, limit, *, timeout=30):
        if type(limit) is not int or not 1 <= limit <= 6:
            raise ValueError("invalid_request_limit")
        if not isinstance(timeout, (int, float)) or not 0 < timeout <= 30:
            raise ValueError("invalid_extraction_timeout")
        self.extractor = extractor
        self.remaining = limit
        self.timeout = timeout
        self.lock = threading.Lock()
        self.stopped = False
        self.in_flight = None

    def __call__(self, message, current):
        return self.extract_with_guard(message, current, is_current=lambda: True)

    def extract_with_guard(self, message, current, *, is_current):
        deadline = monotonic() + self.timeout
        if not self.lock.acquire(timeout=self.timeout):
            raise ProviderError("timeout")
        try:
            if self.in_flight is not None and not self.in_flight.is_set():
                raise ProviderError("request_in_progress")
            for attempt in range(3):
                if monotonic() >= deadline:
                    raise ProviderError("timeout")
                if not is_current():
                    raise ProviderError("request_superseded")
                if self.stopped or self.remaining <= 0:
                    raise ProviderError("request_allowance_exhausted")
                self.remaining -= 1
                finished = threading.Event()
                result = []
                self.in_flight = finished

                def invoke(done=finished, output=result):
                    try:
                        output.append((True, self.extractor(message, dict(current))))
                    except Exception as exc:
                        output.append((False, exc))
                    finally:
                        done.set()

                threading.Thread(target=invoke, daemon=True).start()
                if not finished.wait(max(0, deadline - monotonic())) or monotonic() >= deadline:
                    raise ProviderError("timeout")
                if not result:
                    raise ProviderError("transport_error")
                ok, value = result[0]
                if ok:
                    return value
                code = safe_error_code(value)
                self.stopped = code not in {
                    "http_408",
                    "http_500",
                    "http_502",
                    "http_503",
                    "http_504",
                    "timeout",
                    "network_error",
                }
                logging.getLogger(__name__).warning("Gemini request failed: %s", code)
                if code != "http_503" or attempt == 2 or self.remaining <= 0:
                    raise value
                delay = (1, 2)[attempt]
                if deadline - monotonic() <= delay:
                    raise ProviderError("timeout")
                sleep(delay)
            raise ProviderError("transport_error")  # Defensive; loop always returns/raises.
        finally:
            self.lock.release()


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
