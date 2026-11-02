# Architecture and authority

Read [spec](../docs/spec.md) for product behavior and [status](status.md) for implementation evidence.

## Approved direction

Python 3.10+ core; FastAPI backend; SQLite; plain HTML/CSS/JavaScript; Prisma STT; one structured-output extractor; Timbre TTS. Keep pip/venv. Test on the installed version and state it. CI is configured for Python 3.14; broader Python-version compatibility is not proven by that single job.

Browser input -> STT if speech -> extraction patch -> Python validation/clarification -> review/confirmation -> transactional store -> outcome-derived response. Typed input skips STT, not extraction. UI selection owns job identity. The model owns no commit authority.

## Boundaries

- Keep validation/patch rules pure and provider-independent. FIELD_SPECS supplies basic field rules and the generated extraction schema. Conditional rules stay in validation.py.
- Store methods own state transitions and transactional writes. Do not bypass them with caller-side SQL. Tests may inspect stored rows to establish effects.
- Provider adapters own network payloads, timeouts, response decoding and redaction. They must not mutate job records. Network/SDK code does not belong in validation or Store.
- Application orchestration owns typed/speech flow, questions and outcome wording. Store persists turn identity and mismatch holds and guards their release. SaveRecovery handles bounded delivery/status checks using Store's persisted reservation and receipt. The UI renders authoritative state; browser flags cannot establish rollback.
- UI never receives provider keys. Logs should use request/draft/submission IDs, durations and outcome codes; do not log raw credentials or private recordings.
- Preserve server receipt and submission identity across retry/recovery. Do not introduce a distributed worker architecture for this single-instance prototype.

## Current implementation

`bolparchi/validation.py`, `store.py`, `readback.py` and `__main__.py` are the local core. `fields.py` defines shared field metadata. `validate_extraction` strictly checks provider proposals; pure `apply_extraction` blocks ambiguity and spoken-job mismatch.

`workflow.py` now connects an injected extractor to stored typed turns, clarification and review. Store owns `begin_turn`, `complete_turn`, `fail_turn`, `retry_turn`, `resolve_mismatch` and `cancel_draft`; one shared guard checks completion identity, revision and state. Extractor calls occur outside transactions. The additive `draft_inputs` table keeps the latest transcript/held patch; the draft snapshot joins it and any saved receipt atomically. See [ADR-004](decisions/004-typed-turns.md).

`Workflow.submit_audio` optionally calls a transcriber after `begin_audio_turn` reserves the persisted turn and clears approval. `complete_audio_turn`/`fail_audio_turn` recheck the shared guard before changing state. Successful transcription enters extraction with the same turn ID; stale STT never becomes a fresh typed message. The previous usable transcript survives speech errors. An additive `draft_speech` table stores empty-attempt counts for the typing fallback. See [ADR-005](decisions/005-speech-turns.md).

`recovery.py` implements explicit Confirm and save with a durable `save_requests` reservation, shared three-attempt budget and receipt-based status. Store owns reservation, attempt counting, locking, terminal fencing and the actual transaction. Unknown outcomes remain `save_unresolved`; a definitive rejection/rollback must be fenced against late deliveries before reopening the draft. Existing direct confirm/save methods remain for the core demo/tests; the future application must route saves through SaveRecovery. See [ADR-006](decisions/006-save-recovery.md).

`bolparchi/gemini.py` implements a callable REST extractor that can be injected into Workflow. Its transport uses a 30-second socket-operation timeout, capped reads and no redirects/retries. Its decoder rejects invalid or incomplete responses before invoking the patch validator. `extract()` also returns allowlisted model/usage metadata for diagnostics. No Store or save tool is supplied to the provider. Successful live extraction remains unverified after HTTP 503.

`gnani.py` implements encoded-file transcription and text-to-WAV synthesis without access to Store. Transcripts are checked for success/type/length and preserved unchanged. WAV decoding validates the requested PCM format and normalizes only observed streaming length placeholders. `provider_http.py` supplies the shared no-redirect, bounded-read, redacted-error transport; `provider_json.py` rejects duplicate keys and non-JSON numeric constants. No adapter automatically retries.

`webapp.py` exposes narrow typed/speech-workflow routes and exactly five UI assets. Strict bodies reject extra fields and coercion; bounded JSON/WAV uploads plus origin/host checks keep repository files and provider credentials out of the browser. Routes call Workflow and SaveRecovery without direct writes. Provider work runs outside the ASGI event loop, so cancellation can complete during extraction or STT. `web/app.js` renders snapshots, suppresses superseded responses and retains pending save identity in tab-scoped storage. Receipt recovery is independent of extraction; see [ADR-007](decisions/007-local-browser.md).

`web/recorder.js` owns microphone lifecycle and WAV encoding; `web/pcm-worklet.js` independently bounds samples to 30 seconds. `browser_audio.py` validates the exact mono 16 kHz PCM contract before Workflow reserves a speech turn. `speech_review.py` checks the exact review before and after synthesis and has no save authority. Client playback epochs, aborts and object-URL cleanup stop obsolete audio. See [ADR-008](decisions/008-browser-speech.md).

`scripts/run_web.py` requires explicit fixture or capped live mode, uses separate default SQLite files and binds only 127.0.0.1. Startup performs no provider request. FixtureSpeech returns a fixed transcript and a test tone; live speech is separately enabled with a combined STT/TTS allowance using `speech_runtime.py`. `scripts/demo_typed_workflow.py` still demonstrates terminal fixture extraction. `scripts/prepare_provider_probes.py` prepares offline requests with the shared builder. `scripts/probe_gemini.py` is an explicit, capped live diagnostic with no store access. Browser wiring is tested with fixture providers; complete live acoustic/extraction quality is still unverified.

For architecture or contract changes, propose the decision to Ankit, then record the accepted choice and consequences in [ADRs](decisions/README.md). An OPEN QUESTION blocks the affected behavior; unrelated approved work may continue.
