# Local browser prototype

The local browser uses the existing Workflow, SaveRecovery and SQLite Store. It has a fictional-job selector, a typed/recorded Update sheet, optional read-back playback and an inline saved receipt. A live typed Gemini clarification/correction/save task and one user-operated microphone task have passed; general extraction/speech quality remains unverified. See [evaluation](EVALUATION.md).

## Start the offline walkthrough

Install the approved dependencies into the repository environment, then start the server:

```sh
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m scripts.run_web --fixtures
```

Open `http://127.0.0.1:8766`. Only loopback is bound; this is not a deployment. Five UI assets (HTML, CSS, app, recorder and audio worklet) are explicitly served; the repository, `.env` and SQLite file are not served. Fixture records persist in ignored `artifacts/local-fixtures.sqlite`. Use `--db /path/to/another.sqlite` for a separate local demonstration database; do not delete existing evidence to reset a walkthrough.

Select job 104 and use these exact fixture messages in order, pressing Review update each time:

1. `Motor kharab. Do motor chahiye. Kaam pending hai.`
2. `Kal shaam aana hai.`
3. `Do nahi, ek motor.`

Check quantity 1, pending status and the follow-up. Confirm and save is the only action that authorizes a write. Any unsubmitted text disables confirmation of the previous review. Unknown fixture text produces extraction failure; the fixture is not a language parser. Expand “Try a fixture message” to fill the input without submitting it.

## Recording and read-back

In fixture mode, Record update captures real browser audio, but **every recording returns the first sample message above regardless of what you say**. Continue with messages 2 and 3 to exercise clarification and correction. Listen to review plays a quiet two-second test tone, not spoken synthesis; the actual review text remains visible. Both fixture limitations are labelled in the UI.

Capture uses native AudioWorklet with a 30-second sample bound, mono 16 kHz/16-bit PCM WAV, and at most 960,044 bytes. Stop and review sends the recording; reaching the limit also sends it. Discard recording, leaving/hiding the page or cancelling the draft stops capture and releases microphone tracks. Unsupported capture or permission denial offers typing. Raw recordings stay in memory and are never written by the app; validated transcripts remain in the draft. Live providers receive the audio when enabled, so this local retention rule does not describe provider-side retention.

The server rejects malformed, empty or oversize WAV before speech calls. STT uses the existing persisted turn guard; cancellation stays responsive and late results cannot overwrite newer work. After two empty transcriptions, typing receives focus. A lost response can be checked with Refresh draft while transcription is still pending. Recording never confirms or saves.

Read-back requests identify the exact revision/hash. The server generates text from the current review and rechecks it after synthesis; changed reviews discard late audio. The browser stops playback on typing, new actions, recording or leaving the page. Failed playback leaves text review and explicit confirmation available. Device compatibility and human listening quality remain unverified beyond the tested Chrome environment.

## Save and interruption behaviour

The sheet-shaped logo opens the workspace sidebar: upright when closed, tilted when open. Its shortcuts move within the current page and preserve typed input. Escape, the backdrop or the logo closes it. The sidebar displays the current job/status and available update, review, receipt and fixture-message shortcuts. It cannot change job identity or authorize saving. During microphone capture the toggle is disabled; opening it otherwise stops read-back playback. Keyboard focus and reduced-motion behavior are supported.

Before sending a save, the browser writes its draft ID, submission ID, revision and hash to tab-scoped `sessionStorage`. It stores no provider keys or audio. A refresh retains this save identity; general unfinished drafts are not resumed. Keep the same tab while a save is unresolved. Clearing browser storage or closing the tab can lose the client reference; server receipts remain durable.

Response loss keeps editing locked. Check save status reads authoritative state and never starts a delivery. If the server has no pending reservation yet, Retry same save can send the original identity/review again, with at most three client sends retained across refresh. SQLite separately enforces at most three actual delivery attempts. Neither request absence nor a network error means “not saved.” Only a receipt or a definitive rejection/fenced rollback resolves the outcome.

An extraction request can be cancelled while its provider call continues. Store rejects late results, and the browser ignores superseded responses. A 45-second browser wait limit stops waiting, not the server's underlying work; refresh checks state without inventing a result.

## Live mode is explicit and separate

The runner requires either `--fixtures` or `--live`. Merely starting the app or opening a page makes no provider call. Live mode requires a `--max-requests` allowance from 1 to 6 and private environment configuration. It uses GeminiExtractor directly, never falls back to fixtures, and allows explicit retries after transient errors within the remaining cap. Authentication, quota, invalid-response and other nontransient errors stop further calls. HTTP 503 is retried at most twice within the action, after 1 and 2 seconds; every attempt counts against the same cap. Other errors are not automatically retried. The 30-second extraction wait deadline includes queueing/backoff. A timed-out transport may still finish, but its output is discarded and overlapping transport is blocked until it exits. Cancelled/superseded turns are checked before further attempts; see [ADR-011](../agent_docs/decisions/011-bounded-extraction-recovery.md). The cap is for that server process; restarting does not grant permission or restore the project's approved allowance.

Live speech is disabled unless `--max-speech-requests N` is also supplied (N is 1–6), with `GNANI_API_KEY` in the environment or the explicitly supplied `--env-file`. STT and TTS share that process-local allowance. Calls consume an attempt before networking; provider failures stop later calls, except empty transcripts may be repeated within the cap. Speech does not retry automatically. The extraction wrapper retries only HTTP 503 as described above; the underlying adapters and standalone probes remain single-attempt. Limits in a command are not authorization to spend credits; restarting does not reset the project's approved allowance. Fixture mode rejects credential and allowance arguments.

Current authorization (5 November): Ankit authorized necessary provider tests within the reported free tier and existing Gnani credits while completing the project. Do not enable billing or paid overage. The old six-request/two-request diagnostic limits are historical; process-local caps still bound every launch. Keys remain private in `.env`, parsed only when explicitly named.

Example bounded live launch within that authorization:

```sh
.venv/bin/python -m scripts.run_web --live --max-requests 6 --max-speech-requests 2 --env-file .env --db artifacts/local-live.sqlite
```

This makes no calls until an input/read-back action. Six extraction attempts and two combined STT/TTS attempts are the maximum for that process. Exhaustion requires a deliberately reviewed new launch; it is not a reason to loop restarts. Current model/prompt and failure evidence are in [status](../agent_docs/status.md).

## Check the browser

The Python suite runs offline HTTP tests through FastAPI TestClient with real SQLite and injected provider boundaries. The browser scripts use an existing Playwright installation and installed Chrome; they install neither a package nor a browser:

```sh
node scripts/check_browser.mjs /absolute/path/to/playwright
node scripts/check_browser_real.mjs /absolute/path/to/playwright
node scripts/check_voice_browser.mjs /absolute/path/to/playwright
node scripts/check_readback_browser.mjs /absolute/path/to/playwright
node scripts/check_voice_real.mjs /absolute/path/to/playwright
node scripts/check_pcm.mjs
node scripts/check_sidebar.mjs /absolute/path/to/playwright
```

Browser scripts default to the loopback URL above; an optional third argument changes it. Run a fixture server first. `check_browser.mjs` intercepts HTTP responses to exercise client error/loading/empty and recovery states. `check_browser_real.mjs` sends real local requests, saves fictional records, drops a response after commit, and also drops a request before arrival. `check_voice_browser.mjs` uses Chrome's synthetic microphone and intercepted API outcomes for permission/discard/empty/refresh checks. `check_readback_browser.mjs` tests synthetic playback and stale response suppression. `check_voice_real.mjs` sends native WAV through the actual local HTTP/SQLite workflow and explicitly saves its corrected record; providers remain fixtures. `check_pcm.mjs` checks the exact sample/encoder bound without a browser or server. No script uses a human microphone or calls an AI provider. Captures go to ignored `artifacts/browser/`.

The first screen's neutral design is a working candidate. After Ankit requested more character, it gained a job-number stamp, a layered paper surface and raised charcoal controls. It has been visually inspected at desktop and narrow widths; this is not a general accessibility certification or technician usability study.

Direct dependency versions were checked against their package releases: [FastAPI 0.162.0](https://pypi.org/project/fastapi/0.162.0/), [Uvicorn 0.54.0](https://pypi.org/project/uvicorn/0.54.0/) and [HTTPX 0.28.1](https://pypi.org/project/httpx/0.28.1/). Installed Starlette 1.10.0 currently emits an HTTPX TestClient deprecation warning; tests pass, and no extra replacement dependency was installed. Runtime Python used for these checks is 3.14.7; other versions are not verified.

## Offline 503 recovery check

Run `.venv/bin/python -m scripts.demo_retry_recovery`, then open `http://127.0.0.1:8768`. It uses no keys or AI requests. The first fixture message triggers exactly three simulated 503s with real backoff. The UI must preserve the submitted message, keep saving disabled and offer Retry extraction. That button recovers on attempt four; the normal follow-up and correction use attempts five and six. Confirm explicitly to save. The isolated SQLite evidence lives in `artifacts/retry-browser.sqlite`; restarting resets this test double's attempt sequence, not provider authorization.
