# BolParchi evaluation — 6 November 2026

**Real typed browser, retained-audio backend and one user-operated microphone task have passed. Final UI polish has scoped regression evidence.** These results describe a small fictional prototype, not general accuracy or production reliability.

## Human microphone task and final polish — 6 November

Ankit completed the fresh live microphone task and reported that recording and playback were clear. The browser's saved state and an independent SQLite read verified receipt `5bb647c0-7df0-4e64-89fa-1b4b9c8aa6f6`, one submission, one motor request with quantity 1, and follow-up `कल शाम आना है`. Evidence: `artifacts/human-voice-handoff-20261106/` and `artifacts/final-human-voice-20261106.sqlite`. Clarity is the user's assessment on this device; no independent listening study, multi-speaker accuracy or fresh-call latency measurement is claimed.

The final Unslop pass then changed presentation/static copy only. A separate fixture browser run covered empty/error/recovery, clarification, correction, sidebar keyboard/animation, desktop/mobile layout and explicit saving through real SQLite. It made no AI calls. See [polish review](../agent_docs/unslop-review.md) for attribution, per-pass changes, checked states and limits. No full new provider run was repeated for these presentation-only edits, and no uncut video has yet been captured.

## Configuration and separation of evidence

Current configuration: Gemini `gemini-3.5-flash-lite`, REST v1beta, LOW thinking, prompt `bolparchi-field-decisions-v2`, wire schema `bolparchi-field-decisions-v1`; Gnani Prisma `/stt/v3` with Hindi/verbatim transcription and Timbre v2.5/Nalini, 48 kHz mono PCM WAV. Shared transport identifies itself as `BolParchi/0.1`, refuses redirects and performs no automatic retries. Python owns validation, confirmation and transactional saving. Since 6 November the live runner separately permits up to two automatic retries on HTTP 503, after 1s/2s, within its shared request cap and a 30-second extraction wait; the underlying transport and standalone probes remain single-attempt. See [ADR-011](../agent_docs/decisions/011-bounded-extraction-recovery.md).

The offline suite injects provider responses and makes no AI requests. Development probes informed prompt changes. The six cases in [acceptance_cases.json](../probes/acceptance_cases.json) were frozen before their first execution and were not used for tuning. They are agent-authored, not independently labelled by technicians. Evidence files and private recordings remain Git-ignored; this document summarizes results without credentials or private audio.

## Frozen evaluation — 6 November 2026

**Six cases attempted once each: five exact patch matches, one provider failure, zero semantic mismatches among returned patches, zero unattempted cases.** The provider failure is not a semantic pass. This is a small agent-authored set, not evidence of general accuracy.

| Frozen case | Observed result | Request time |
| --- | --- | --- |
| New number correction: three → four | Exact patch: quantity 4 | 1.446s |
| Uncertain lower bound: more than two, exact count unknown | HTTP 503; no patch to assess | 2.100s |
| Complete work and remove follow-up | Exact status set and follow-up clear | 2.118s |
| Explicit reference to different job 106 | Exact pending status and separate spoken job ID | 1.623s |
| Native Hindi completion | Exact completed status | 1.915s |
| Explicit quantity removal | Exact quantity clear | 1.453s |

The first batch stopped after its second case returned 503. A separate batch attempted only the four untouched cases; it did not repeat the successful or failed prior cases. Both batches used the same prompt/schema/model and each retained stop-on-provider-error behavior. There were six Gemini calls in total, no automatic retries, no Gnani calls and no save operations. Successful request times range from 1.446–2.118s (median 1.623s), excluding 16-second pacing. These are five observations, not a latency guarantee.

Case-file SHA-256 remains `d9c64a3504d46ac8347f1eabe4b5730c03e5ea2d2f627f5a490ac3202c9c1ce0`; prompt SHA-256 is `383f946faea947c9e4f9e64ea864b864d1c276300e68431862077981bc5fc215`. No expected output, prompt, parser or product code was changed during this evaluation. The source reports and their aggregate are preserved:

- `artifacts/provider-probes/acceptance-20261106T123828733508Z.json`
- `artifacts/provider-probes/acceptance-continuation-20261106T123943221545Z.json`
- `artifacts/provider-probes/acceptance-summary-20261106.json`

At the end of the original run, the uncertain-lower-bound case had no semantic result. Its subsequent separate recheck passed, as recorded below; that supplemental evidence does not replace the original 5-match/1-error result. If future prompt changes use these cases, label them regression data and create a fresh evaluation set before making a new held-out claim.

## Supplemental uncertainty recheck and retained-audio task — 6 November

The previously unavailable `uncertain-lower-bound` case returned the exact expected whole-patch clarification response on one separate recheck (1.627s). Prompt, schema and frozen cases were unchanged. Report: `artifacts/provider-probes/acceptance-supplement-20261106T124403041800Z.json`. Every frozen case now has a usable exact-match observation, but the original single-attempt result remains **five matches and one 503**, followed by this supplemental pass; it is not rewritten as a clean 6/6 run.

The strict retained-recording workflow then passed using the real providers with no retries: Gnani STT (0.767s), three Gemini extractions (1.942s, 1.351s, 2.032s), and Gnani TTS (2.275s). These timings exclude intentional 16-second pacing between extraction turns. The initial review contained diagnosis, pending status, motor, quantity 1 and `कल शाम आना है`. Explicit removal of follow-up caused clarification, and a subsequent answer restored review without changing quantity. An unconfirmed save was rejected; explicit test confirmation saved once and replaying the same submission returned its receipt without duplication.

A fresh read-only SQLite connection verified one submission, one quantity-1 part request and one follow-up task. Receipt: `924cb48691414af29c37ae9a7d27f89f`. Timbre produced a valid 11.68-second, mono, 48 kHz, 16-bit PCM WAV. Evidence: `artifacts/live-workflow/20261106T124416085267Z/report.json`, `persistence-proof.json`, `records.sqlite` and `readback.wav` in the same directory.

This is a retained human M4A recording sent through the backend, followed by typed clarification turns and programmatic test confirmation. It verifies real-provider integration and persistence; it does **not** verify fresh browser microphone capture, human listening quality, a technician walkthrough or an uncut submission video. Historical failures remain below.

## 6 November missing-follow-up verification

The active adapter requires all five field decisions with supporting source quotes, then converts them to the existing canonical patch; see [ADR-012](../agent_docs/decisions/012-field-decisions.md). Six targeted development checks passed with 1.604–2.734s inference times: the original Hindi message, reordered Hinglish, truly absent follow-up, explicit removal, ambiguous quantity and replacement of an old follow-up. The checks use exact structured values plus specified text fragments, not exact-patch accuracy. Their separate case file is [field_decision_cases.json](../probes/field_decision_cases.json). The frozen acceptance file is unchanged; its subsequent run is reported above.

A real typed browser check preserved all five stated fields, including quantity 1 and `कल शाम आना है`, through explicit saving. SQLite contained zero submissions/parts/tasks before confirmation and exactly one each afterward. Receipt `4bfa2109-1ced-4be7-9bc1-d60fb6b15f99`; desktop/mobile captures inspected and browser warning/error logs empty. Evidence: `artifacts/field-decisions-browser-20261106/`. No speech provider was enabled in that browser session.

A separate retained-audio run transcribed successfully but failed on its first Gemini call with HTTP 503; no TTS or save followed. Evidence: `artifacts/live-workflow/20261106T123100460609Z/report.json`. This remains a failed voice integration attempt. The earlier omission failures below are preserved as historical evidence, not current success claims.

## 6 November recovery verification

The offline browser check injected three consecutive 503s using the actual capped runner, real HTTP and SQLite. It observed loading, exhausted automatic attempts, preserved input and disabled saving, then recovery on manual retry. Follow-up and quantity correction succeeded; one explicit confirmation saved quantity 1. Desktop/390px captures were inspected, 390/320px overflow checks passed and no browser warning/error logs were recorded. Artifacts: `artifacts/retry-browser-20261106/`; reproduction: `.venv/bin/python -m scripts.demo_retry_recovery`. This check used **no live AI requests** and is separate from the 5 November live typed task. A separate 6 November live extraction through the new wrapper succeeded on its first attempt in 1.753s (`bounded-retry-20261106T085126.json`); it did not exercise actual 503 recovery.

## Results

| Boundary | Observed result | Limit |
| --- | --- | --- |
| Offline core/HTTP/provider-boundary checks | 424 passed as of 6 November; one existing Starlette TestClient/HTTPX deprecation warning | Does not prove real speech/LLM accuracy |
| Six development extractions, prompt v2 | 4 exact patch matches, 2 mismatches | Development data; pacing contaminated most elapsed times, so these are not model latency measurements |
| Two targeted rechecks, prompt v3 | Uncertainty correctly held the patch; named-part omission remained | Same development cases, not independent evaluation |
| Frozen acceptance, prompt v4/schema v2 | First case returned HTTP 503 in 1.953s; stopped immediately; five cases unattempted | Zero usable semantic outputs; no accuracy percentage can be computed |
| Frozen acceptance, field-decisions v2/wire schema v1 | 5 exact matches, 1 HTTP 503, all 6 attempted once across two batches | Uncertainty case unverified; no six-case semantic pass or general accuracy claim |
| Retained human audio transcription | Full Hindi transcript preserved the two-to-one motor correction, pending status and next-evening follow-up | One recording; not a varied-speaker or acoustic-quality evaluation |
| Strict retained-audio integration | Two runs reached extraction but omitted the final follow-up; Python entered clarification and prevented save | Neither run reached TTS or save; neither is a passed end-to-end voice task |
| Targeted 3.6 Flash comparison | Also omitted that follow-up | No evidence to justify switching the default to 3.6 |
| Retained-task clarification continuation | HTTP 503; stopped before TTS/save | Original failures preserved; no voice-task completion claim |
| Live typed browser task | Three Gemini extractions completed clarification and two-to-one correction; Gnani read-back reached playback; explicit confirmation returned a durable receipt | No fresh microphone, listening-quality judgement or live transient retry in this successful run |
| Persistence of that typed task | Zero submissions/parts/tasks before confirmation; exactly one of each after; quantity 1 verified via a fresh read-only SQLite connection | Local fictional data, not a deployed service |

## Successful typed task

The actual browser messages were:

1. `Motor kharab hai. Do motor chahiye. Kaam pending hai.` — diagnosis, part, quantity 2 and pending status; follow-up question shown; saving disabled.
2. `Kal shaam aana hai.` — complete review with quantity 2.
3. `Do nahi, ek motor.` — quantity changed to 1, other values retained, explicit confirmation enabled.

Listen to review was invoked twice; the second request was observed in the browser's “Playing the current review” state. This establishes synthesized-audio delivery/playback initiation, not pronunciation or intelligibility. One Confirm and save action produced receipt `56956688-5940-45ce-8d73-9aebf1f66e15`. Reopening SQLite verified one submission, one part request with quantity 1 and one task. The browser returns to job selection after refreshing a completed save; it has no general saved-record-history view. Unresolved-save refresh recovery is covered separately by existing offline/local fixture checks.

## Known failures and safeguards

- Under the previous direct-patch prompt, the long native-script transcript explicitly included a follow-up, but Gemini omitted it. The initial record had no follow-up, so required-field validation prevented saving and asked a question. Validation cannot generally detect a semantically wrong but structurally valid field or an omitted correction to an existing field. Human review remains essential.
- The v2 uncertainty case incorrectly cleared quantity. The v3 targeted recheck held the patch correctly, but one passing recheck does not establish robust ambiguity handling.
- A named part already present in the record was omitted from the patch. The resulting record was unchanged, but the exact extraction contract was not met; expected outputs were not loosened.
- HTTP 503 occurred intermittently, including a one-word probe. It also occurs without the extraction prompt. Its cause has not been established; a free-tier quota display does not guarantee availability.
- Gnani's earlier plain-text 403 was isolated to a request-header difference: Python with an explicit application User-Agent succeeded. This is not evidence of an invalid key or depleted credit balance.

## Evidence locations

All locations below are ignored local artifacts, not public links:

- `artifacts/provider-probes/development-20261105-v2.json`
- `artifacts/provider-probes/development-recheck-20261105-v3.json`
- `artifacts/provider-probes/acceptance-20261105T122250927744Z.json`
- `artifacts/provider-probes/gnani-named-agent-20261105.json`
- `artifacts/live-workflow/20261105T115803297063Z/report.json`
- `artifacts/live-workflow/20261105T121747741374Z/report.json` and its separate continuation reports
- `artifacts/live-typed/cua-20261105/report.json`
- `artifacts/release-check-20261105.sqlite`

## Remaining release gates

1. Record the actual working microphone → review/read-back → explicit save/receipt demonstration on the polished build. Keep any retries or edited waits disclosed.
2. Retain the one-device human clarity feedback; verify any different recording device before filming. Do not present this as broad speech accuracy.
3. Preserve the frozen run’s five exact matches/one 503 and its separate successful uncertainty recheck in the submission evidence. Further tuning on these cases makes them regression data, not a fresh held-out set.
4. Record the exact final commit and update GitHub after the completed polish/checks. The uncut demonstration remains to be made.
5. Obtain user review of the concrete video/explanation before any publication or final submission.

No technician time-savings, user-study results, broad language accuracy, universal error-free behavior or guaranteed hackathon selection are claimed.
