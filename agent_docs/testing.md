# Testing and evidence

## Offline commands

From the repository root, after creating `.venv` and installing `requirements-dev.txt`:

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

Use the same three checks locally and in CI. pytest and Ruff are pinned. Ruff is not a type checker. There is no build command, coverage gate, mypy dependency or pre-commit/client hook, per ADR-001. The earlier pushed repository commit passed GitHub Actions; unpushed local changes have not run in hosted CI. Merge protection must be configured separately; a YAML file alone does not block merges.

## Red -> green -> refactor

Run baseline first. If it fails, report and stop edits; diagnose read-only and ask before fixing a baseline defect. For a behavior change, derive the expected result from the spec/user case, write the focused test and run it. Record the specific failing assertion and command before changing implementation. A collection/import failure or intentionally false assertion is not useful red evidence. Fix the smallest boundary, rerun the test, then the offline suite/checks. Refactor only while the same behavior tests stay green.

Documentation or formatting-only changes can use link/command/diff inspection instead. Do not weaken tests or raise tolerances because the implementation disagrees. A changed requirement needs an explicit accepted decision.

## Choose evidence for the changed boundary

| Boundary | Evidence |
| --- | --- |
| Patch/validation | Exact valid/invalid/missing/conflicting outcomes and resulting draft; dependent fields and immutable job identity |
| Store | Real temporary SQLite databases; receipts and row counts, stale confirmation, replay, rollback, concurrency; reopen DB for durability claims |
| Async/recovery | Controlled ordering of edit/cancel/late result; lost response versus rollback; late commit while status is missing |
| Extraction | Hand-labelled transcript expectations; negation, corrections, omissions, mismatch, malformed output; held-out cases |
| Provider | Real opt-in call plus error/timeout cases; record provider/model/config and observed result without keys |
| UI | Browser interaction for the changed flow and recovery, keyboard, small viewport and console/network failures |

Mocks stop at external-provider boundaries; do not mock the write behavior you are testing. Structured correction tests do not establish speech recognition. Compare observable outcomes, not a second model's approval. Report core, stubbed integration, real provider and UI results separately.

## Provider isolation

`provider` is registered in pyproject.toml; default `addopts` selects `not provider`. This keeps normal test runs offline even when credentials exist. Future live tests must all be marked and may not perform network work at import time or fixture discovery.

Once real provider tests exist, explicit opt-in is:

```sh
.venv/bin/python -m pytest -q -m provider
```

Each future provider test/fixture must check its required environment configuration before any network call and use `pytest.skip` when missing. The configured names are `GEMINI_API_KEY` and `GNANI_API_KEY`. Presence of keys alone never opts in. Record skipped/deselected counts separately from passing calls. No live pytest tests are implemented; an empty provider selection is not successful integration evidence. Do not put provider credentials in CI.

`tests/test_gemini.py` and `tests/test_gemini_probes.py` run offline. They inject external responses/errors, exercise the HTTP read/redirect boundary without networking, verify strict parsing and redaction, and test Workflow with real SQLite confirmation and durable saving. They also verify the probe cap, stop-on-error behavior, explicit opt-in and non-executing key-file parsing. Real live evidence is recorded separately in [provider notes](providers.md).

`tests/test_gemini_diagnostic.py` checks the separately opt-in plain-vs-structured diagnostic: request order, shared cap, progress recorded before calls, stopping after provider/unusable plain output and error redaction. It uses injected transports and does not establish real provider availability. Live diagnostics require authorization and an explicit cap. The original six-request limit was exhausted on 1 November; Ankit subsequently authorized necessary free-tier/existing-credit completion tests on 5 November.

Use `.venv/bin/python -m scripts.probe_gemini --live --max-requests N --env-file .env` only within an authorized allowance. N is 1–6, default 1. The file argument is optional when GEMINI_API_KEY is in the environment. No automatic retry occurs; the runner stops after its first provider failure. A later invocation is a new set of requests, not automatically authorized by the command's cap.

## Test collection and style

`tests/test_save_recovery.py` uses real SQLite transactions with delivery/commit fault boundaries. It checks response loss after commit, delayed commits, definite rollback, fencing before unlock, durable/concurrent retry budgets, nonretryable rejection precedence, malformed responses, exact-review binding and old receipt preservation. No test substitutes an in-memory fake for job/receipt writes. Browser interruption and refresh now have separate evidence below.

`tests/test_webapp.py` uses FastAPI TestClient, injected extraction and real SQLite. It covers the typed HTTP path, exact confirmation/replay, held mismatches, missing receipts, locked recovery, provider errors, concurrent cancellation, strict/oversize inputs, asset allowlisting and same-origin/Host boundaries. `test_job_listing.py` checks persisted job status; `test_web_runner.py` checks capped concurrency, bounded 503 backoff, explicit retry within the same allowance, total extraction wait, late-result rejection, cancellation/newer-turn guards, stopping after other failures and redacted operator logs without networking. The composed HTTP test preserves the failed transcript/draft, then recovers on explicit retry without saving. The approved HTTPX 0.28.1 works with installed Starlette 1.10.0 but emits a TestClient deprecation warning; do not silently install a replacement.

`scripts/check_browser.mjs` exercises client states with intercepted HTTP fixtures. `scripts/check_browser_real.mjs` uses a running fixture-mode app with real HTTP/SQLite, loses a save response after commit and a request before arrival, and checks receipt recovery/same-ID retry. These browser scripts require an existing Playwright and Chrome, are separate from pytest, and make no AI requests. Run instructions and limitations are in [local web](../docs/LOCAL_WEB.md). Captures alone do not prove behaviour; each script also asserts outcomes. Neither script establishes speech recognition, model extraction quality or deployed access safety.

`test_browser_audio.py`, `test_web_speech.py` and `test_speech_review.py` cover strict recording bounds, HTTP speech composition, two-empty fallback, concurrent cancellation, exact-review TTS and rejection of obsolete audio. `test_speech_runtime.py` covers the shared speech request allowance, stop-on-error behavior and named key parsing without shell evaluation. These use synthetic audio and provider responses, never live APIs.

`scripts/check_voice_browser.mjs` uses Chrome's synthetic microphone through the real AudioWorklet/encoder and intercepted API outcomes: upload contract, discard, permission denial, late permission cleanup, two-empty typing focus, transcript preservation and continued refresh during pending transcription. `check_readback_browser.mjs` checks playback, interruption, TTS failure and stale-response suppression with synthetic WAV. `check_voice_real.mjs` runs native capture through the real local HTTP/SQLite app, then clarification, correction, fixture-tone playback and explicit receipt-backed saving. `check_pcm.mjs` verifies sample bounds, clipping/endianness and single completion directly. Desktop/390/320 captures were inspected. Human-device acoustics, actual speech recognition/TTS quality and a real Gemini-to-save task are separate pending evidence.

`tests/test_speech_workflow.py` checks speech-to-extraction/review with real SQLite and external response fixtures. Controlled events order late STT success/failure against newer typed/audio turns, edits and cancellation across two connections. It also verifies confirmation blocking, empty-speech fallback, preserved text, extraction-only retries, reopening counters and old-receipt preservation after schema addition. Browser capture/focus/playback and real acoustic/extraction quality remain outside this evidence.

`tests/test_gnani.py` uses synthetic bytes and injected provider responses to check multipart preservation, strict transcription decoding, empty/oversize input, redacted failures, response caps and WAV handling. It does not test acoustic recognition or microphone capture. The retained real TTS response was separately replayed through the adapter with no network call; see the evidence in provider notes. Ordinary pytest never reads private recordings or requires ignored artifacts.

Tests live in `tests/`; functions use `test_` names. Use fictional records, deterministic assertions and explicit expected values. A test must not compute its oracle using the same production helper it tests. Register new markers; strict marker checking catches typos. Avoid sleeps in concurrency tests where controlled events can express the required ordering.

For prompt ablations, retain a pinned baseline, compare at most 2–3 variants on unchanged cases and repeat trials. Small count differences are tentative. Never disable real save protections; compare unsafe proposals only in an isolated simulator.

## Active field-decision extraction

`tests/test_gemini_decisions.py` covers complete-field accounting, quoted text, direct quote fragments, omissions, invalid values, removals, whole-patch uncertainty and separate job references. It verifies the Hindi follow-up through the workflow and every live entry point. The old direct-patch adapter remains explicitly tested for historical comparisons; `bolparchi/extraction.py` selects the active configuration. Six development cases in `probes/field_decision_cases.json` can be run through `scripts.probe_field_decisions --live --max-requests 6 --env-file .env` within an authorized allowance. They are distinct from frozen evaluation and make no general accuracy claim.
