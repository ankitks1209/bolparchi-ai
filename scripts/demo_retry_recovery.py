"""Offline browser check: three synthetic 503s, then ordinary fixture extraction.

No credentials or provider networking. Run on loopback port 8768; use the fixture
messages shown in the UI. First submit fails after three attempts; Retry extraction
recovers on attempt four. Follow-up and correction consume attempts five and six.
"""

from pathlib import Path

import uvicorn

from bolparchi import Store
from bolparchi.provider_http import ProviderError
from bolparchi.webapp import create_app
from scripts.demo_typed_workflow import MESSAGES, fixture_extractor
from scripts.run_web import CappedExtractor


def main():
    attempts = 0

    def extract(message, current):
        nonlocal attempts
        attempts += 1
        print(f"Offline extraction attempt {attempts}", flush=True)
        if attempts <= 3:
            raise ProviderError("http_503")
        return fixture_extractor(message, current)

    path = Path("artifacts/retry-browser.sqlite")
    path.parent.mkdir(parents=True, exist_ok=True)
    store = Store(str(path))
    try:
        app = create_app(
            store,
            CappedExtractor(extract, 6),
            mode="fixtures",
            examples=[item[0] for item in MESSAGES],
        )
        uvicorn.run(app, host="127.0.0.1", port=8768, access_log=False, server_header=False)
    finally:
        store.close()


if __name__ == "__main__":
    main()
