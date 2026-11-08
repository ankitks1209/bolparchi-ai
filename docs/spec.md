# BolParchi v1 specification

Status: accepted scope consolidated from PLAN.md and Ankit's setup answers on 20 October 2026. This specifies target behavior, not implementation status; see [current evidence](../agent_docs/status.md). Ankit decides product changes. Undefined behavior is an OPEN QUESTION until resolved.

## Users and outcome

Primary user: an appliance-repair technician at a small repair business. After a visit, the technician records diagnosis, status, requested part and follow-up using Hinglish speech or typed text. The owner can inspect saved records in the same prototype. Use fictional customers/jobs only. No separate staff roles in v1.

## Core flow

1. Select a known fictional job. Its identity is fixed for that draft and remains visible.
2. Record a short message or type one. Prisma transcribes speech; both paths use the same extraction function. Preserve the transcript for review and recovery.
3. One extraction model proposes only this message's stated/corrected fields as `set`, explicit removals as `clear`, and a separate `spoken_job_id`. It cannot authorize a save.
4. Python applies a valid patch and computes missing/invalid fields. Ask one relevant question at a time. Corrections update the draft; never silently invent missing details.
5. Display the full current record, highlight edits and optionally speak the read-back with Timbre. The displayed revision/hash identify what the user reviews.
6. A Confirm and save button approves that exact revision/hash. Persist job update, any part request/follow-up and submission receipt atomically. These are local prototype records, not external orders/appointments.
7. Display the saved record and receipt. Outcome text comes from application state, not model improvisation.

## Field and patch contract

| Field | Requirement |
| --- | --- |
| `job_id` | Known job selected by UI, immutable after draft creation |
| `diagnosis` | Required short text preserving meaning |
| `status` | Required: `completed` or `pending` |
| `part_needed` | Optional requested-part label; no inventory inference |
| `quantity` | Integer 1–20 when a part is requested; invalid without a part |
| `follow_up` | Required for pending; optional for completed; free text, not a booked time |

A completed job may contain a part/follow-up but does not require either. FIELD_SPECS generates basic validation and the extraction schema; conditional rules remain tested Python functions.

Accepted 21 October: diagnosis/follow-up allow up to 500 Unicode code points and part labels up to 120 after whitespace normalization. Input messages allow up to 2,000 code points and are preserved unchanged. Reject empty input and over-limit values; never silently truncate. The extraction envelope contains exactly `set`, `clear`, `spoken_job_id` and a boolean `needs_clarification`. Ambiguous/unusable messages set that flag and hold the whole patch for clarification. Model set values use strict JSON types; null or blank values are rejected, and removal requires clear. See [ADR-003](../agent_docs/decisions/003-field-contract.md).

Reject unknown fields, wrong types and overlap between `set` and `clear`. Clearing `part_needed` clears quantity; clearing a part while setting quantity is rejected. Replacing the part preserves quantity unless explicitly changed/cleared, and the review exposes it. Null in `set` is not a deletion. Selected job is outside the mutable patch.

Within-message corrections use the final explicit value. Ambiguous content must lead to clarification rather than a guessed action. Neither structured output nor a low temperature proves semantic correctness.

## Edge cases and acceptance criteria

| ID | Scenario | Observable acceptance |
| --- | --- | --- |
| AC-01 | Valid update | Exact reviewed values persist only after explicit confirmation; receipt is visible |
| AC-02 | Missing/invalid field | No save; one relevant question; answer patches the same draft |
| AC-03 | Correction | `do… sorry, ek` yields quantity 1 through actual extraction when integrated; any edit invalidates earlier approval |
| AC-04 | Set/clear/dependencies | Conflicts rejected without mutation; part removal clears quantity |
| AC-05 | Spoken job mismatch | Hold the entire patch; user can apply to selected job or discard; recheck current draft/revision/open state on release |
| AC-06 | Stale or cancelled work | Shared draft/expected-revision/turn/open-state guard rejects late transcription, extraction and mismatch releases; cancelled draft cannot update, confirm or save |
| AC-07 | Duplicate/retry | One submission ID survives retries; repeated request returns original receipt; fresh-ID second save of same draft cannot write again; a separate legitimate draft may save identical content |
| AC-08 | Uncertain save | Saved only with receipt; Not saved only with confirmed rejection/rollback and no possible in-flight commit; otherwise unresolved and editing locked |
| AC-09 | Recovery | Retry transient failures at most three total attempts with same ID; do not retry validation/stale/cancelled/not-confirmed errors; bounded status checks then manual Check status |
| AC-10 | Empty speech/STT failure | Ask to repeat, offer typing immediately; foreground typing after two empty attempts; preserve usable text/draft |
| AC-11 | Extraction failure | Preserve transcript/draft and offer retry; typing is not presented as bypassing the same failed model dependency |
| AC-12 | TTS failure | Text review remains usable; stop obsolete speech when draft changes; no false success announcement |
| AC-13 | Cancel | Cancel an open draft without updating the job; cancellation unavailable while save may complete |
| AC-14 | Interaction | Jobs, Update, Saved views; keyboard controls, visible focus, large tap targets, text for every spoken message; mobile layout works |

Release evidence: zero duplicate/unconfirmed writes in the defined tests, no known critical transition failure, real STT/extraction/TTS probes and one complete recorded user task. Report counts and limitations. Do not claim universal correctness, general speech accuracy or guaranteed selection.

## Out of scope and cut lines

Deferred: streaming, telephony, voice-only confirmation, more languages, inventory/payments/messaging, staff administration, RAG/vector DB, multi-agent runtime, model training/Evon hosting and recurring autonomous maintenance.

Optional: direct field editor, cross-session draft resume, noise comparison, hosted reviewer demo. If voice flow is incomplete on 24 October 2026, cut direct field editing and draft resume. Local application plus a truthful recording is the baseline; hosting stays Ankit's decision. Correctness controls are not optional cuts.

Accepted 31 October: Ankit delegated the initial recording choice. Browser recordings use at most 30 seconds of mono, 16 kHz, 16-bit PCM WAV (maximum 960,044 bytes with the canonical 44-byte header). Stop at the limit; reject malformed/oversize uploads before calling speech APIs. Keep raw audio in memory only and release it after completion/cancellation; retain the validated transcript in the existing draft. Typing remains available after microphone/recording failure. Gnani's current REST reference now lists a 30-second maximum, superseding the older 60-second note. Human acoustic quality still requires a live check.

Accepted 6 November, issue #1: the live browser extraction runner may retry HTTP 503 at most twice after the initial attempt, with 1s/2s backoff and a 30-second overall extraction wait budget. Each attempt uses the launch-local allowance. Cancellation/newer turns are checked before another attempt; late output cannot mutate the draft. Other errors are not automatically retried. Exhaustion preserves the message/draft and offers explicit retry. This is independent of the durable save-delivery retry budget in AC-09 and of speech transcription time. See [ADR-011](../agent_docs/decisions/011-bounded-extraction-recovery.md).

Implementation boundary, 6 November, issue #2: the provider wire response accounts for all five fields with set/clear/not_mentioned/uncertain decisions and verbatim supporting quotes. Python converts it to the unchanged canonical extraction envelope above. Quotes constrain text provenance but do not prove semantic completeness. See [ADR-012](../agent_docs/decisions/012-field-decisions.md).

## OPEN QUESTIONS

- Exact extraction model/version, supported reasoning settings, SDK/API version and prompt/schema version: verify official docs and real account probe. `gemini-3.8-flash` remains the PLAN candidate, not validated access or a mandatory hardcoded choice.
- Provider credential environment-variable names and available access/credits: establish during probes; never request secret values in chat.
- Browser recording support and acoustic quality across the intended demo devices: verify capture against the accepted WAV/30-second contract above.
- Whether a public hosted demo is needed; access model, storage, budget and audio/log retention if hosting is chosen.
- Final brand palette/typeface: no reference app required; accessible design constraints are accepted, exact visual tokens await the UI task.
