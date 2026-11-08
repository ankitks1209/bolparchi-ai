# Current implementation status

Updated 7 November 2026. **Ankit completed the fresh real-provider microphone task and reported clear recording/playback; its receipt and quantity-1 record are verified. Final Unslop polish and scoped browser regression are complete.** Current extraction: Gemini 3.5 Flash-Lite, field-decisions prompt v2/wire schema v1, converted to the existing canonical patch. Bounded 503 recovery is implemented; upstream availability remains intermittent.

## Current task — motion reference inspected; production brief prepared

Inspected sampled visual frames from Ankit's new 45.84-second style-reference recording. Saved [the reference breakdown and proposed 60-second storyboard](../docs/video-style-brief.md), including the reported toolchain, neutral BolParchi adaptation and a small motion-proof checkpoint. Audio is present but has not been listened to/transcribed; exact transition timing is not established. Private reference copy/frames remain ignored in `artifacts/video-style-reference-20261107/`.

Hyperframes is the proposed first renderer, consistent with the earlier Brag discussion; Remotion is an alternative and WhisperX optional for caption alignment. This is a proposal, not an installed or tested video pipeline. No dependency installation, voice-service purchase, provider request, rendered video or publication occurred. Next: local motion proof with an approved renderer setup, real workflow capture, final edit, source/CI and reviewed submission.

Documentation-only verification: **424 tests passed**, one existing Starlette/HTTPX warning; Ruff lint passed; Ruff format reported **95 files already formatted**; Git whitespace check passed. No application behavior changed or new browser-flow coverage claimed.

## Previous checkpoint — challenge recording extracted and remembered

Reviewed timestamped visual frames across Ankit's 28.26-second registration/terms recording and cross-checked the current official challenge pages. Saved [recording notes](../docs/challenge-recording-notes.md), updated the authoritative [submission checklist](../docs/SUBMISSION.md), and recorded Ankit's explicit preference for the landing-page visual in the design system. The file has one audio track, which was not transcribed; no audio-derived claim is made. Ignored local evidence: `artifacts/video-reference-20261107/` (source copy, frames and timestamp index).

Key carry-forward points: 10 November 2026 at 11:59 PM IST cutoff; public working video before final submission; genuine Gnani use and named contributions; nominated post links plus both hashtags; verified engagement for shortlisting; separate 60-second-demo award. Recommend a 60-second main edit with real workflow footage and restrained Brag graphics. Current FAQ directs participants to an emailed submission form despite older workspace wording in the terms. No installation, model change, provider request, public post or submission occurred. Video, final source/CI and approved submission remain pending.

Documentation-only final verification: **424 tests passed**, one existing Starlette/HTTPX warning; Ruff lint passed; Ruff format reported **94 files already formatted**; documentation-link and Git whitespace checks passed. No application/UI behavior changed and no new browser-flow verification is claimed.

## Previous checkpoint — local landing-page preview implemented

Built the presentation-only page in `site/`, served locally at `http://127.0.0.1:8772/`. It uses the established neutral paper identity, an upright/tilted navigation mark, a readable illustrative correction sheet, the Bolo/Dekho/Confirm sequence, review/save safeguards and actual interface captures. The hero illustration is explicitly labelled; the polished capture discloses fixture responses, while the separate real-provider receipt is identified as predating final polish. The missing video is honestly marked pending. No application workflow, provider adapter or persistence behavior changed.

The logo-opening browser assertion first returned false against the scaffold. The implemented page then passed 14 checks at 1280px, 390px and 320px: drawer opening/announcement, forward/backward keyboard wrapping, Escape/focus return, section navigation/focus, expandable real-voice evidence, valid anchor targets, absent-video disclosure and no horizontal overflow. Backdrop dismissal also passed. Desktop/mobile captures were inspected; the overlapping hero quotation was corrected. A deliberate missing-image check exposed a stale full-size link; fallback now hides the failed image and its links and displays useful text. Reloading the normal page restores both assets. Final browser warning/error logs were empty. Reduced-motion rules were inspected in source, not preference-emulated. Evidence: `artifacts/landing-20261107/`; reusable browser check: `scripts/check_landing_browser.mjs`.

This is a working local design candidate for Ankit's feedback, not final visual approval or a hosted demo. Instructions and screenshot provenance are in [site/README.md](../site/README.md). No dependency, provider request, public deployment or Git push occurred. Next: review this actual composition, record the real working video on the final app build, then complete source/CI and the reviewed public submission.

Final checks: **424 tests passed**, one existing Starlette/HTTPX deprecation warning; Ruff lint passed; Ruff format **93 files already formatted**. Both JavaScript syntax checks, Git whitespace, local asset resolution and byte-for-byte screenshot provenance passed. Five contrast pairs passed: normal text minimum 5.27:1 and control boundary 3.62:1. This scoped review is not a full accessibility certification.

## Previous checkpoint — landing-page design before submission video

Ankit requested a proper design and landing page before producing the upload video. Reviewed the supplied 26-page motion-graphics PDF, including the actual screenshot-based promo example, and adapted Janus Tiu's supplied template into [proposed visual tokens/components](design-system.md#proposed-landing-page-system--7-november-2026). The [landing-page and video brief](../docs/landing-page-brief.md) proposes concrete copy, sections, real-evidence assets and a motion plan around the spoken two-to-one correction. The existing neutral palette, subtle morphism and paper logo remain the starting point; exact landing composition awaits a rendered preview and Ankit's feedback.

This task changes documentation only. No landing page or video has been built, no PDF installation commands were executed and no dependency/provider/publication action occurred. Remaining order: design review → local landing-page specimen and inspection → real working video → final source/CI and reviewed public submission. Final verification: **424 tests passed**, one existing Starlette/HTTPX deprecation warning; Ruff lint passed; Ruff format reported **92 files already formatted**. Git whitespace and local documentation-link checks passed. No new browser validation is claimed for this documentation-only task.

## Previous checkpoint — human voice acceptance and final polish completed

Ankit reported: “Completed; recording and playback were clear.” The live browser showed saved receipt `5bb647c0-7df0-4e64-89fa-1b4b9c8aa6f6`. A separate read-only connection verified exactly one submission, one motor part request with quantity 1 and one follow-up task `कल शाम आना है`. Evidence: `artifacts/human-voice-handoff-20261106/human-acceptance.json`, `saved.png` and `artifacts/final-human-voice-20261106.sqlite`. This is one user/device/example, not an independent technician study or broad speech-quality result. No uncut submission video was captured by the agent.

Applied the authorized final Unslop pass using the existing neutral service-sheet direction: sentence-case/readable metadata, consistent row/control spacing, simpler action buttons, softer neutral shadows and a repair-specific picker heading. Preserved the logo/tilt, recording control, section order and all workflow authority. See [polish review and attribution](unslop-review.md).

Post-polish browser checks used fixture providers through real HTTP/SQLite: empty/error states, recovery, follow-up clarification, quantity correction, explicit saving and receipt. Sidebar tilt/upright state, backward keyboard wrap and Escape focus return passed. Desktop/mobile captures inspected, 390/320px overflow checks passed and browser warning/error logs were empty. One quantity-1 fixture submission persisted. Five contrast checks passed; no new provider calls were made for polish. Capture/save/recovery runtime logic was unchanged.

Baseline: **424 tests passed** with one existing warning. Final checks: **424 passed**, one existing warning; Ruff lint passed; Ruff format reported **91 files already formatted**; JavaScript syntax, PCM encoder and Git whitespace checks passed. No new dependency, billing change, publication or Git push. **Remaining delivery: record the real working demo, record the final commit and update GitHub, then review the concrete public post/submission with Ankit before publishing.** Ankit's final visual preference can still guide small refinements.

## Previous checkpoint — retained-audio backend acceptance passed; human check pending

The separate uncertainty-case recheck returned the exact whole-patch clarification response in 1.627s, without changing the frozen cases or prompt. All six cases now have usable exact-match observations. Preserve the original evaluation as five exact matches plus one 503, followed by this supplemental pass; do not report a clean first-attempt 6/6 result. Report: `artifacts/provider-probes/acceptance-supplement-20261106T124403041800Z.json`.

The strict retained-human-recording workflow passed all five provider calls without retries: one Gnani STT, three Gemini extractions and one Gnani TTS. Initial extraction preserved quantity 1 and the final Hindi follow-up. Removing follow-up caused clarification, answering restored review, unconfirmed save was refused, explicit test confirmation saved, and replay returned the same receipt. A fresh read-only connection verified one submission, one part request (quantity 1) and one follow-up task. Receipt `924cb48691414af29c37ae9a7d27f89f`; retained evidence: `artifacts/live-workflow/20261106T124416085267Z/`. TTS is a valid 11.68-second PCM WAV; listening quality has not been judged.

A fresh live browser session is prepared at `http://127.0.0.1:8770/`, job 104, database `artifacts/final-human-voice-20261106.sqlite`. It permits six extraction attempts and four combined speech calls for the process. The user has been asked to record the fictional correction, check the fields, listen and confirm. Do not simulate this human step or label a retained recording as fresh microphone evidence. The browser handoff is pending.

This checkpoint changed evidence documentation only. Final checks: **424 passed**, one existing Starlette/HTTPX warning; Ruff lint passed; Ruff format reported **90 files already formatted**; PCM encoder checks passed. No new dependency, billing change, publication or Git push. **Remaining: fresh microphone/listening task, final Unslop polish, final regression, actual demo video and reviewed submission.**

## Previous checkpoint — issue #3 evaluated; one case was unverified

Ran the unchanged six-case frozen evaluation against the active field-decision adapter. **Five exact patch matches, one HTTP 503, zero semantic mismatches among returned patches and zero unattempted cases.** The initial batch stopped on case two; a separate continuation attempted only cases three through six. Each case was sent once, with no automatic retry. No prompt, parser, expected output or product code was changed.

Passing cases covered a new quantity correction, completed status plus follow-up removal, a separate spoken job 106, native Hindi completion and quantity removal. The uncertain-lower-bound case returned HTTP 503 in 2.100s and has no usable semantic result. Successful requests took 1.446–2.118s (median 1.623s), excluding pacing. This small agent-authored set is not general accuracy evidence; the run is complete but the six-case semantic gate is not fully passed.

Reports: `artifacts/provider-probes/acceptance-20261106T123828733508Z.json`, `acceptance-continuation-20261106T123943221545Z.json` and `acceptance-summary-20261106.json`. The aggregate checks unique case coverage and unchanged case/prompt hashes. See [evaluation](../docs/EVALUATION.md) for the per-case table and limitations. Preserve the original result if the unavailable case is rechecked later.

Checks: **424 tests passed**, one existing Starlette/HTTPX warning; Ruff lint passed and Ruff format reported **90 files already formatted**. This step changed evidence documentation only; no UI behavior changed, so no new browser usability claim is made. Six Gemini requests, no Gnani requests, no dependencies/billing/publication changes. Source remains local and uncommitted.

**Next: issue #4, full real voice workflow**, with the uncertainty-case availability gap still tracked. Human microphone/listening quality remains separate. Unslop stays last before final recording/submission.

## Previous checkpoint — issue #2 completed for the reproduced omission

Recovered the interrupted six-case development run: all six checks passed, including native Hindi with a correction before the final follow-up, reordered Hinglish, genuinely absent follow-up, explicit removal, uncertainty holding the whole patch, and replacement of an old follow-up. Inference times were 1.604–2.734 seconds, excluding pacing. This is a targeted development set, not exact-patch or held-out accuracy. Report: `artifacts/provider-probes/field-decision-cases-20261106T090937.json`.

The active adapter now requires decisions for all five fields and supporting quotes for stated facts. Python converts them into the existing validated patch. No inferred follow-up, model fallback or save authority was added. All live entry points and offline request preparation use the same configuration. See [ADR-012](decisions/012-field-decisions.md) for the observed failure, regression-first changes and semantic limitations.

The real browser check typed the complete Hindi transcript into the live app. Its review retained `कल शाम आना है`, quantity 1 and the other stated fields. A separate read-only SQLite connection saw zero submissions/parts/tasks before confirmation and exactly one of each afterward. Receipt: `4bfa2109-1ced-4be7-9bc1-d60fb6b15f99`. Desktop/390px screenshots were inspected; 390/320px overflow checks passed and warning/error logs were empty. Evidence: `artifacts/field-decisions-browser-20261106/` and its adjacent SQLite database. This browser session used real Gemini, with speech deliberately disabled; it is not voice acceptance.

A separate retained-recording check succeeded at Gnani STT but stopped at Gemini HTTP 503, before review/TTS/save. It made one request to each provider and did not retry. Failure evidence remains in `artifacts/live-workflow/20261106T123100460609Z/report.json`. The successful typed check does not erase that failure.

Baseline on resume: **418 passed**. After wiring the active adapter: **424 passed**, one existing Starlette/HTTPX deprecation warning. Final checks: Ruff lint **all checks passed**, Ruff format **90 files already formatted**, and Git diff whitespace check passed. No new dependencies, billing changes or publication. Changes remain local and uncommitted. **Next: issue #3, the unchanged frozen evaluation**, followed by full voice/device acceptance. Unslop remains last before final recording/submission.

## Previous checkpoint — issue #1 completed: bounded Gemini 503 recovery

Ankit approved tackling the ordered issue list one at a time and resumed after a network interruption. Implemented at most three attempts per extraction action, with 1s/2s delays only for HTTP 503, a shared process request cap and a 30-second overall extraction wait. Authentication/quota/invalid-output failures do not retry automatically. Standalone probes and Gnani adapters remain single-attempt. See [ADR-011](decisions/011-bounded-extraction-recovery.md).

Tests first exposed immediate failure on a recoverable 503 and a subsequent request after cancellation during backoff. Both are fixed. A workflow guard checks state/revision/turn before each attempt. Timed-out transport output cannot update a draft; while its worker remains active, new transports are refused without spending an attempt. The deadline limits application waiting, not upstream service execution, and excludes prior speech transcription.

The offline browser check used three injected 503s with real backoff, followed by manual retry, clarification, quantity correction and explicit saving through real HTTP/SQLite. There were zero submissions before confirmation and one afterward, with one quantity-1 part request and one follow-up task. Desktop/390px captures were inspected, 390/320px overflow checks passed and browser warning/error logs were empty. Evidence: `artifacts/retry-browser-20261106/`, `artifacts/retry-browser.sqlite`; reproduce with `scripts.demo_retry_recovery.py`. This test used no AI requests.

A separate live check through the new wrapper succeeded on its first attempt in 1.753s with model version `gemini-3.5-flash-lite`. No automatic retry was needed in that live call; it does not prove service-wide recovery. Report: `artifacts/provider-probes/bounded-retry-20261106T085126.json`.

Checkpoint checks: **394 tests passed**, one existing Starlette/HTTPX warning; Ruff lint passed; Ruff format reported **85 files already formatted**. No dependency, billing, publication or UI-style change. **Next is #2: missing follow-up in longer Hindi extraction.** Its failure evidence and frozen evaluation remain unchanged. Unslop is still scheduled last, after core/evaluation and before the final submission video.

## Previous checkpoint — 5 November live typed task passed; voice acceptance blocked


Ankit authorized necessary tests and completion work within the reported Gemini free tier and existing Gnani credits. This supersedes the earlier per-run six/two-request limits described in historical entries below; it does not authorize paid billing or publication. The Gnani dashboard showed 4,999 credits, and Ankit confirmed the matching key is active. Neither provider key was printed or changed.

- **Baseline:** 381 offline tests passed with one existing Starlette/HTTPX deprecation warning on this resume.
- **Transport:** Gnani returned plain-text 403 with Python's default request headers, but the same recording/key/endpoint succeeded with curl and then with Python using `User-Agent: BolParchi/0.1`. The shared transport now identifies the application. TLS, no-redirect protection, bounded reads and no automatic retries remain intact. See [ADR-010](decisions/010-provider-transport-and-retry.md).
- **Extraction:** 3.8 plain generation continued to return 503; 2.5 returned 404. 3.5 Flash-Lite produced plain and structured responses and is the explicit configured model. It still intermittently returns 503. No automatic model fallback or fixture substitution exists. See [ADR-009](decisions/009-extraction-model.md).
- **Recovery:** the browser's explicit extraction retry can use the remaining process cap after transient errors. Authentication/quota/invalid-output errors stop the wrapper. Tests verify no automatic retry, shared caps and safe logs. A successful live run did not exercise this error branch.
- **Live typed browser task:** three actual Gemini calls produced initial diagnosis/part/quantity 2/pending, then a follow-up, then quantity 1. Gnani read-back was invoked twice; the second was observed in “Playing the current review.” Before confirmation, SQLite contained zero submissions/part requests/tasks. One explicit Confirm and save produced one receipt, one quantity-1 part request and one follow-up task. A separate read-only SQLite connection verified persistence after browser refresh. Refresh returns to job selection; completed-receipt history is not a UI feature. Evidence: `artifacts/live-typed/cua-20261105/report.json` and ignored `artifacts/release-check-20261105.sqlite`.
- **Voice gap:** retained human M4A transcription preserved the whole Hindi sentence, including the two-to-one correction and final follow-up. Both strict integrated runs failed because Gemini omitted the follow-up, so Python asked for clarification and prevented saving. V4/schema descriptions and a 3.6 comparison did not resolve that omission. A later one-shot clarification continuation returned 503 and stopped before TTS/save. Original failures remain untouched; no complete voice-to-receipt success is claimed.
- **Evaluation:** six development cases gave 4 exact patches and 2 mismatches under v2. The v3 uncertainty recheck passed, but redundant named-part omission remained. The frozen six-case acceptance run stopped on its first case with HTTP 503; five cases were never sent. No held-out accuracy score is available. See [evaluation](../docs/EVALUATION.md).

## Agreed delivery order

1. Complete and verify the core voice/typed workflow and recovery. Keep provider failures and semantic omissions visible; do not keep repeating identical failed calls or tune the frozen evaluation to pass.
2. Finish the evaluation and concrete submission draft. A technician/user walkthrough and a complete real microphone task are still pending.
3. **Apply Unslop last**, as explicitly requested on 5 November: focused polish of the existing neutral, subtly raised service sheet and animated paper logo. The skill is installed, but no Unslop UI edits have been made. See [design-system record](design-system.md).
4. Repeat final browser/engineering checks and record the actual working demo. Publish or submit only after Ankit reviews the concrete result and explicitly approves.

No new dependency, billing change, deployment or public post occurred. Current source changes are local and not yet committed/pushed. The earlier public repository CI success applies to the earlier commit, not these changes. The sections below preserve historical evidence; superseded provider counts and readiness statements are not current conclusions.

Final local verification for this checkpoint: pytest **381 passed, 1 existing warning in 1.11s**; Ruff lint **all checks passed**; Ruff format **83 files already formatted**; PCM encoder checks passed; Git diff whitespace check passed. Documentation links resolved, and a scan of the 25 changed/untracked source files found zero configured-key matches. UI styles were not changed. The live typed browser interaction was exercised, but new mobile/desktop review captures were not completed in this checkpoint; prior layout evidence is historical. Human microphone/listening validation remains open.

## Previous task: initial Git commit and GitHub push

Ankit explicitly requested committing and pushing the existing code to GitHub on 2 November. Created initial commit `529e140` on main with 107 source/test/documentation/configuration files. Configured credentials and common credential patterns were checked without printing values, with no matches. `.env`, private recordings, databases, artifacts and the virtual environment are ignored. Baseline: 377 tests passed, one existing warning in 1.26s; Ruff lint passed and format reported 77 files already formatted. A clean temporary archive of only committed files also passed all 377 tests with one warning in 1.49s, using the existing environment.

Ankit created and supplied the public [bolparchi-ai repository](https://github.com/ankitks1209/bolparchi-ai). Added a prominent README work-in-progress label explaining fixture responses and pending real Gemini/voice validation. Confirmed the destination was empty, set origin to the supplied HTTPS URL and pushed main with tracking. Commit `a615bd3` matches the pushed branch; its [first GitHub Actions run](https://github.com/ankitks1209/bolparchi-ai/actions/runs/41478046702) completed successfully. Local verification before pushing: 377 passed, one existing warning in 1.21s; Ruff lint passed and format reported 77 files already formatted. These checks do not establish live AI readiness. No website deployment, billing/provider call or change to the existing Sites preview occurred.

## Previous task: Gemini isolation diagnostic — stopped on plain-generation failure

On 1 November, both local provider entries passed presence/shape checks without printing values; `.env` remains mode 0600. The current model documentation still lists `gemini-3.8-flash` with structured output and LOW thinking. Google's rendered [status page filtered to free tier](https://aistudio.google.com/status?tier=free) reported all free-tier systems operational; it also listed an API-key outage resolved on 30 October. This was new availability evidence, not proof of account-specific inference access or an explanation of the older errors.

Used the final previously approved request for the unchanged fictional quantity-correction probe. It returned HTTP 503 in 7.855 seconds and stopped without retry. Report: `artifacts/provider-probes/gemini-20261101T182137344275Z.json`. The original six-attempt allowance is now exhausted: one sandbox failure, one successful model metadata GET, and four generation HTTP 503 responses. Zero successful extractions. No Gnani calls, billing changes, model substitution or publication occurred.

Ankit then explicitly approved up to two additional diagnostic requests: plain generation first, extraction only if it succeeded, stopping on failure. Ran `scripts/diagnose_gemini.py` against the same model. The first request asked for exactly READY without an extraction schema or system prompt and returned HTTP 503 in 5.663 seconds. The command stopped after one call; the second, conditional extraction request was not sent. Report: `artifacts/provider-probes/gemini-isolation-20261101T182744000377Z.json`. No retry, model change, billing change or Gnani call occurred.

The failure therefore also occurs without our extraction prompt/schema; this does not identify account access, model availability or capacity as the root cause, nor prove the full extraction request valid. Seven total attempts are conservatively counted across both approvals (five generation 503 responses, one metadata GET, one sandbox failure). One of the new two-request allowance remains unused, but the approved run stopped and its extraction-success prerequisite was not met; do not repurpose it for another retry or changed-model test. Next investigate the project's access/quota and selected model availability before proposing further calls.

Six test-first offline diagnostic cases cover ordering, cap, stopping on provider/unusable output and redaction. Initial assertions failed against the stub; all six pass. The report records the started attempt before networking, then its safe outcome; credentials and raw provider errors are not logged.

Final checks: 377 passed, 1 existing warning in 1.24s; Ruff lint passed; 77 Python files already formatted. UI was unchanged in this diagnostic task; browser evidence below is from the preceding voice/sidebar tasks. Human voice-to-save validation remains pending successful extraction and an authorized provider allowance.

## Previous task: functional logo and animated sidebar

Implemented Ankit's 1 November request: the sheet logo is straight at rest, tilts nine degrees when opening a frosted left sidebar, and returns upright on close. Contextual shortcuts focus existing update/review/receipt sections and fixture examples without navigation or draft mutation. Current job and save state come from the existing snapshot. Escape, backdrop and logo dismissal work; focus wraps inside the dialog and returns to the toggle or chosen section. Reduced motion disables animation. Opening stops read-back, and capture keeps the toggle disabled so microphone controls remain reachable.

The new browser test first failed because the logo was not an operable button, then exposed missing backward focus wrapping. Both are fixed. Sidebar checks pass for typed-input preservation, zero mutation requests, straight/tilted states, focus, dismissal, reduced motion and 1280/390/320 layouts; captures inspected. Read-back checks additionally verify stopping playback and resetting controls when opening the sidebar. The existing browser suite passes; cancellation selectors now target the service sheet because the sidebar repeats that status label. No assertion was removed. Final Python checks: 371 passed, 1 existing warning in 1.09s; Ruff lint passed and format reported 75 files already formatted. No provider calls, dependencies or publication occurred.

## Previous task: local browser voice and read-back

Ankit delegated the initial recording choice. Implemented a 30-second, mono 16 kHz/16-bit PCM WAV contract with a 960,044-byte ceiling; see [spec](../docs/spec.md) and [ADR-008](decisions/008-browser-speech.md). The audio worklet enforces the sample bound independently of the UI timer. Stop or reaching the limit sends the recording for review; discard/cancel/page hiding stops tracks, including a late permission grant. Raw audio stays in memory; no recording files are persisted by the app. Invalid, empty and oversized WAV are rejected before STT.

The HTTP speech path uses the existing persisted turn guard and runs provider work off the event loop, so cancellation remains responsive and late STT cannot overwrite a newer draft. Two empty transcriptions preserve usable text and focus typing. After a lost response, a pending transcription remains manually refreshable. Read-back accepts an exact revision/hash and synthesizes server-generated text; a changed review discards late audio. Browser edits/actions stop playback and revoke its audio URL. Playback failure leaves text review available. Neither recording nor listening can authorize a save.

The runner now exposes explicitly labelled fixture speech: every recording returns the same fictional sample transcript and Listen plays a quiet test tone. Live Gnani wiring requires a separate combined STT/TTS request cap, alongside the existing Gemini cap. This prepares integration; it does not authorize calls. No provider requests, new dependencies, publication or sharing changes occurred in this voice task. The default local launch remains `.venv/bin/python -m scripts.run_web --fixtures`; the latest checks used a separate ignored `artifacts/voice-check.sqlite` database.

Test-first evidence: speech-review assertions failed before implementation; strict WAV and HTTP route assertions failed before validation/routing; capped speech tests failed against stubs. Resuming the unfinished named-key loader produced 370 passing tests plus its new failure; after adding the signature, the behavioral assertion exposed Gemini's key being returned for a Gnani lookup, then passed after the parser fix. A browser regression exposed a hidden Refresh draft button while STT was still pending, then passed after the rendering fix. The pre-voice baseline was 346 passing tests.

Chrome checks cover native synthetic microphone capture/encoding, stop/upload, discard, permission denial, late permission cleanup, two-empty typing focus, previous-transcript preservation and pending-STT refresh. Separate playback checks cover actual synthetic WAV playback, stop on typing, provider failure and ignored obsolete audio. A real local HTTP/SQLite check completes capture → fixture STT/extraction → follow-up → two-to-one correction → test-tone playback → explicit confirmation → receipt, and verifies zero save requests before confirmation. Existing typed and lost-save recovery checks still pass. Desktop/390/320 screenshots were inspected; controls/fields wrap without horizontal overflow. These are fixture and synthetic-device results, not human speech or extraction-quality evidence.

## Previous task: first local browser slice

Implemented the planned FastAPI/plain HTML-CSS-JavaScript connection. Ankit explicitly approved FastAPI 0.162.0, Uvicorn 0.54.0, HTTPX 0.28.1 and their required dependencies; they were installed into `.venv`. The runner binds only 127.0.0.1, serves three named UI assets and requires explicit fixture or capped live mode. No provider request, publication or sharing change occurred in this slice. See [local walkthrough](../docs/LOCAL_WEB.md) and [ADR-007](decisions/007-local-browser.md).

The Update sheet supports typed patches, missing-detail questions, changed-field labels, wrong-job apply/discard, extraction retry, cancellation and explicit exact-review confirmation. Unsubmitted text blocks saving the previous review. The browser can cancel while extraction runs and ignores superseded responses. No microphone or read-back control is presented as working.

Before sending a save, the browser retains the submission/review identity in tab-scoped storage. A lost response locks editing; refresh recovers the stored receipt without another save. A request lost before reservation may be retried with its original identity, at most three client sends across refresh; the server separately enforces its durable delivery limit. Known rejection/fenced rollback unlocks; missing receipts remain uncertain. Clearing storage/closing the tab can lose the client reference; general cross-session draft resume is still cut.

Test-first evidence: job-list assertions failed against the stub, the first browser test failed at the absent Start update control, and 14 HTTP assertions failed before route implementation. Later regressions exposed a fabricated empty view for an unknown draft, a rejected save that stayed locked, unavailable cancellation during extraction and missing retry for a request lost before arrival. Those cases are fixed. The Python additions include real SQLite HTTP/concurrency tests and a launch-local live-call allowance tested without provider networking.

Chrome checks with intercepted HTTP fixtures cover clarification/correction, unsent edits, extraction retry, wrong-job discard, rejected/uncertain saves, refresh/receipts, jobs loading/error/empty, cancellation plus late responses, input limits, long Hindi/part text and HTML escaping, focus/reduced motion, blocked browser storage, and retry-cap persistence. A separate browser script uses real local HTTP/SQLite, drops one response after commit and one request before arrival, and verifies receipt recovery/same-ID retry. Both use scripted extraction; neither is evidence of model quality. Desktop/390/320 captures are in ignored `artifacts/browser/` and were visually inspected. Final visual acceptance and technician usability feedback remain open.

The working preview is started with `.venv/bin/python -m scripts.run_web --fixtures` at `http://127.0.0.1:8766`. It persists fictional records in ignored `artifacts/local-fixtures.sqlite`. Exact sample messages are exposed in the UI and walkthrough. Other text deliberately fails fixture extraction; it is not a hidden AI fallback.

## Previous task: durable save recovery

Implemented `SaveRecovery` with persisted submission/review binding, a three-attempt delivery budget and bounded status checks. `prepare_save` atomically approves the exact reviewed revision/hash and locks the draft; edits, input and cancellation cannot proceed while its outcome is uncertain. The new additive `save_requests` table preserves older receipts and exposes the pending ID/attempt count in draft snapshots.

Only a stored receipt establishes saved. A lost response or exception after real commit is recovered from that receipt. Retryable transport/SQLite lock failures use the same ID; known validation/stale/cancelled/not-confirmed rejections never retry. A definitive failed save is closed under a write transaction before editing unlocks, so late deliveries cannot write after the user changes the record. If a commit wins the race, closure returns its receipt instead. Unknown outcomes stay locked and can be checked manually without another delivery. See [ADR-006](decisions/006-save-recovery.md).

Test-first evidence: initial tests failed to recover saved receipts or make bounded attempts. Further failing tests exposed rollback classification, persisted identity, review binding and malformed-response handling. All 23 added tests pass using real SQLite, controlled transaction faults and delayed/lost delivery. They cover late commits, fencing, concurrent/reopened budgets and older-schema receipts. HTTP/browser disconnect behavior remains untested because the web application is still unbuilt. Reservation/database failures may conservatively remain unresolved rather than inventing a definite result.

No provider requests, dependencies, deployment or UI changes occurred in this task. The existing typed walkthrough still uses fixture extraction and the older direct confirm/save API; future application endpoints should use SaveRecovery.

## Previous task: guarded speech workflow and Gemini diagnosis

`Workflow.submit_audio` reserves a persisted transcription turn before calling the injected transcriber outside transactions. It revokes old approval, blocks premature confirmation/save, and checks draft/revision/turn/open-state before accepting either success or failure. Late STT cannot replace newer typing, audio, edits or cancellation, including across separate Store connections. Usable transcription enters the existing extraction/review flow; the model still cannot save.

Speech errors preserve the previous usable transcript and current proposal. The view offers typing immediately and marks it preferred after two current empty attempts. Counts survive reopening and reset on accepted text or usable transcription. Extraction retries reuse the stored transcript without retranscription. An additive `draft_speech` table preserves earlier receipts; no raw audio is stored. See [ADR-005](decisions/005-speech-turns.md). Browser focus and microphone behavior are not implemented by these backend flags.

The first two tests failed because speech did not reach review or reserve a transcribing state. Later empty/invalid-response tests failed before recovery implementation. All 23 added tests now pass, including two-connection ordering, approval guards, empty-text preservation, schema upgrade and composition of the actual adapters with fixture transports. This is offline integration evidence, not a live microphone-to-save task.

Read-only Gemini `models.get` returned HTTP 200 for the configured model and advertised generateContent support. A single subsequent correction probe returned HTTP 503, provider status UNAVAILABLE and an allowlisted capacity/demand category. No raw error message, key or thought output was logged. Reports: `artifacts/provider-probes/gemini-model-check-20261028.json` and `gemini-generation-check-20261028.json`. No further generation call followed. Counting conservatively, five of the six approved request attempts have been used: one sandbox failure, three generation HTTP 503 responses and one metadata GET. Model metadata access is established; schema acceptance/extraction quality and account billing state are not.

No dependency, deployment or new Gnani request was introduced this task.

## Previous task: Gnani speech adapters

Implemented `bolparchi/gnani.py` with Prisma multipart transcription and Timbre WAV synthesis. Neither adapter owns draft/save state. Credentials are supplied explicitly, responses are bounded and transport errors are redacted without automatic retries. Shared transport and strict JSON handling moved to `provider_http.py` and `provider_json.py`; the existing Gemini tests stayed green.

Transcription preserves the returned text, rejects empty/overlong/non-string responses and requires a true success flag. File extensions are restricted to the documented formats, but the adapter does not decode uploaded audio to verify its codec or duration. The configurable input byte ceiling defaults to 10 MiB; this is a resource guard, not an agreed browser recording limit. Capture validation remains a separate pending boundary.

Timbre decoding validates the requested 48 kHz mono 16-bit PCM container and repairs only the observed RIFF/data `0xffffffff` length sentinels after receipt. Invalid/truncated finite lengths, duplicate chunks and unsupported formats are rejected. Replaying the retained 138,284-byte real TTS response produced exactly the previously normalized WAV, with identical PCM samples and zero new Gnani requests. Evidence: ignored `artifacts/provider-probes/gnani-adapter-replay-20261027.json`. Audible quality was not assessed.

Test-first evidence: the initial normalizer failed the exact repaired-byte assertion; speech methods returned no transcript/audio. Further tests failed on malformed/unsuccessful STT responses and empty/overlong transcripts before implementation. All 56 added tests now pass. Tests use synthetic audio/response fixtures; they are separate from the retained-response replay and earlier live probes. No new dependency or deployment was introduced.

One Gemini check within the remaining approved six-attempt allowance returned HTTP 503 in 3.067 seconds. Total across the two implementation sessions: three attempts (one sandbox network error, two HTTP 503 responses), zero successful extractions. Report: `artifacts/provider-probes/gemini-20261027T160904371393Z.json`. Stop identical retries after these two consecutive HTTP 503 failures; diagnose service/model/account availability before another generation call. No model or billing setting was changed.

## Previous task: Gemini extraction boundary

Implemented `bolparchi/gemini.py` using the standard library, with no new dependency. It plugs into Workflow and returns validated proposals. It rejects incomplete/blocked/malformed output and duplicate JSON keys, excludes thought output, refuses redirects, caps response reads at 256 KiB plus one detection byte, and redacts transport failures. Its 30-second socket-operation timeout is not an absolute wall-clock deadline. There are no automatic retries. Model and numeric usage metadata are allowlisted; no raw provider body is persisted.

The offline preparation script shares the adapter's prompt/schema/request builder. The explicit `--live` probe runner caps each invocation at six calls and stops on the first provider error. It reads the environment or an explicitly named local key file without shell evaluation. The ordinary walkthrough and pytest remain offline.

Red/green evidence: the first two acceptance tests failed because the adapter returned no proposal and the workflow entered extraction_error instead of review. Further red tests covered rejection/redaction/read bounds/redirect protection and probe limits. All 57 new tests pass, including a real SQLite reopen after confirmed saving and preservation of the draft/transcript after provider failure. Fixture responses do not establish real extraction quality.

Ankit authorized up to six fictional free-tier requests. The sandbox attempt returned `network_error`; one subsequent network-enabled attempt returned HTTP 503. Each invocation stopped after its first failure; no automatic retry or later call occurred after 503. Two attempts total, zero successful extractions. Remaining cases were not sent; model/usage metadata was unavailable. No billing setting changed; actual usage is unknown. Redacted reports: `artifacts/provider-probes/gemini-20261027T131857356955Z.json` and `gemini-20261027T131945464506Z.json`. No deployment occurred.

## Current priority and publication control

Ankit clarified that the objective is a competitive working hackathon entry, and future publication must be explicitly confirmed after he reviews the concrete result. All development is local by default. Visual iteration supports the working product; it is not the main deliverable. The next deliverables below are internal readiness criteria, not an official judging rubric or a prediction of selection.

An earlier explicit Sites publication request deployed the supplied visualization unchanged as an owner-private Site. Ankit subsequently said that publication was not his intended action. Current access was checked: owner only, no other users/groups and zero external visitors. Available Sites tools expose no unpublish operation; the preview remains deployed, and no removal is claimed. No further deployment or audience change is authorized. Project ID: `appgprj_6ae060f8d1e08191abd8ad72771d0f84`. Source checkout: `/Users/golukakarot/.codex/.chatgpt-projects/g-p-6acf8aefdf3881919d96d3c922541664/sites/bolparchi-minimal`. This static visualization has no provider keys or real workflow integration.

## Previous task: neutral preview and design-skill research

Latest iteration: Ankit requested morphism mixed with minimalism. Updated the neutral specimen with a frosted translucent sheet, subtle neutral depth, soft raised recording control and closer field spacing. Twelve layout/state checks at outer widths 1280/390/320 passed, with no page errors; recording/confirmation simulation, visible focus and reduced motion checked. Mobile and desktop captures inspected. The treatment is proposed and remains disconnected from real recording/saving. Evidence: ignored `artifacts/design-preview/morphism-*` files. No backend behavior changed.

Ankit rejected both colored proposals and asked for a minimalist design, polished website references and GitHub skills to trial before selection. Reviewed Linear, Vercel Geist and Raycast; applied Anthropic frontend-design and Vercel web-design-guidelines as session-only guidance. Inspected Impeccable's current skill entry but did not run its launcher/install hooks. No new skill, dependency or application feature was installed. The [research note](design-research.md) records sources, fit, trial changes and limits.

The new monochrome preview passed 12 layout/state checks at outer widths 1280/390/320, recording/readback/confirmation simulations, keyboard focus and reduced-motion checks. Desktop/mobile/dark captures inspected; minimum measured text contrast 5.74:1 and control boundaries 3.95:1. It remains a mock with no microphone/provider/save connection, awaiting visual feedback. Prior preview evidence below is historical.

Ankit supplied a conversation about AGENTS, skills, review and visual craft, and requested that its useful parts be adapted to BolParchi. Created working-system.md; expanded design-system.md; refined the existing UI-polish skill; added a short AGENTS pointer and mobile/desktop review requirement. Preserved all six explicit-only skills, the approved stack and existing product guarantees. No feature code, dependency, external message or provider call was added during this task.

Ankit selected a **modern service sheet** for the first visual preview: readable job details, visible corrections and one strong recording control. Created Field sheet (blue, desktop input/review split) and Focused sheet (green, review above corrections) as inline previews. Both use fictional data and local simulated interactions only. No microphone, extraction or persistence is connected. Final palette/typeface/composition await feedback; the actual browser application remains unbuilt.

Browser checks covered both variants across review, missing follow-up, extraction failure and unresolved-save states at outer widths 1280, 390 and 320 pixels (iframe content widths 1248, 358 and 288). No horizontal overflow or JavaScript page errors were observed. Exercised recording simulation, disabled confirmation, typing/readback simulation, keyboard focus and actual carousel navigation. Inspected desktop/mobile and dark-theme captures. Forty-eight candidate color pairs met their text/control targets; minimum checked text contrast 5.25:1, control boundary contrast 3.42:1. This is limited preview evidence, not a full accessibility audit or real workflow verification. Ignored evidence lives in `artifacts/design-preview/`.

On 27 October Ankit saved the Gemini key. Presence of both provider entries and `.env` mode 0600 were checked without displaying values. No provider call occurred in this design research task.

## Historical verification — 1 November 2026

Commands ran from `/Users/golukakarot/Developer/Projects/BolParchi AI` using Python 3.14.7. Pre-voice baseline: 346 passed. The resumed unfinished voice task had one new named-key test failing and 370 passing; the completed change now passes:

| Check | Actual result |
| --- | --- |
| `.venv/bin/python -m pytest -q` | 377 passed, 1 warning in 1.24s |
| `.venv/bin/python -m ruff check .` | All checks passed! |
| `.venv/bin/python -m ruff format --check .` | 77 files already formatted |
| `scripts/check_browser.mjs` in installed Chrome | Passed intercepted-HTTP client/recovery/layout checks |
| `scripts/check_sidebar.mjs` in installed Chrome | Passed logo state, contextual shortcuts, input preservation/no writes, focus, dismissal, reduced motion and desktop/mobile checks |
| `scripts/check_browser_real.mjs` in installed Chrome | Passed real HTTP/SQLite save, lost response, refresh and same-ID retry; fixture extraction |
| `scripts/check_voice_browser.mjs` in installed Chrome | Passed native synthetic capture, permission/discard/empty/focus/pending-STT refresh and layout checks; HTTP outcomes are fixtures |
| `scripts/check_readback_browser.mjs` in installed Chrome | Passed synthetic playback, text fallback, stop-on-edit and obsolete audio suppression |
| `scripts/check_voice_real.mjs` in installed Chrome | Passed native synthetic capture through real local HTTP/SQLite, correction, test-tone playback and explicit receipt-backed saving; providers are fixtures |
| `scripts/check_pcm.mjs` | Passed exact sample/byte bound, PCM clipping/endianness and single completion |
| Six skill frontmatters, process/checklists, canonical symlinks and explicit invocation settings | Passed structural inspection on 1 November; skill files unchanged |
| Relative reference links in AGENTS, README, docs, agent_docs and skills | Passed on 1 November; no missing targets |
| Current neutral preview | 12 layout/state checks; interactions, keyboard, reduced motion, contrast and captures inspected |

The one pytest warning is Starlette 1.10.0 deprecating HTTPX with TestClient; tests pass and no replacement package was installed. The earlier standard skill-creator validator could not run because its runtime lacked PyYAML; that narrower structural check is not a full YAML validator or evidence of client discovery. Skills are unchanged. Hosted CI and deployed application behavior have not been verified.

## Historical implementation inventory — 1 November 2026

- Core validation/normalization, shared field contract/schema, immutable selected job, exact revision/hash confirmation, transactional saving and submission replay.
- Persisted latest typed input/turn identity; injected extraction outside transactions; clarification, changed fields, review, mismatch apply/discard, cancellation and stale-result guards. Tests use real SQLite, including concurrent ordering and durability cases. See [architecture](architecture.md), [ADR-003](decisions/003-field-contract.md) and [ADR-004](decisions/004-typed-turns.md).
- Offline typed walkthrough with fixture extraction, explicit SAVE, receipt replay and CANCEL paths. `.venv/bin/python -m scripts.demo_typed_workflow` still makes no provider calls.
- Gemini REST adapter and opt-in fictional probe runner; fixture-backed workflow integration tested. Successful live extraction remains unverified after the observed HTTP 503.
- Gnani STT/TTS adapters, bounded shared provider transport and strict JSON decoding. WAV replay matches retained real-response evidence. Browser wiring is implemented; live end-to-end use remains pending.
- Guarded STT-to-extraction orchestration, previous-transcript preservation and persisted empty-speech fallback state; tested offline with real SQLite.
- Durable save recovery, shared three-attempt budget, exact-review binding, receipt lookup and terminal fencing before unlock; backend tested with real SQLite faults/concurrency.
- Local typed browser/HTTP integration and receipt recovery across refresh, including real commits with deliberately lost responses and same-ID retry when a request never arrived.
- Local browser capture, bounded WAV validation, guarded STT routes and exact-review playback, verified with a synthetic Chrome microphone and fixture speech/extraction through explicit SQLite saving.
- Six explicit development skills, pytest/Ruff setup and a prepared CI workflow. No remote CI success or configured merge protection is claimed.

## Historical accounts and provider evidence — through 1 November 2026

Ankit's registration email confirmed challenge enrolment. An organizer reply allowed personal-email registration. Ankit reported Gnani dashboard access and 5,000 visible credits on 23 October. On 24 October he privately configured the key in Git-ignored `.env`; presence and owner-only permissions were checked without displaying it.

| Provider | Actual evidence | Remaining limit |
| --- | --- | --- |
| Gnani Timbre | Two earlier live requests returned HTTP 200. The new adapter reproduces the earlier normalization exactly using the retained 1.44-second WAV. No new live call this task. | Listening quality and integrated playback remain unverified; first response body was not retained |
| Gnani Prisma | One user-supplied 10.168889-second AAC/M4A recording returned HTTP 200 and `gnani-prisma-v2.5` in 5.508 seconds. Transcript preserved the requested two-to-one motor correction, pending status and follow-up. | Comparison against the suggested script only; no independent listening check, varied-speaker evaluation or app integration |
| Gemini | Metadata GET succeeded on 28 October. Five generation calls through 1 November returned HTTP 503, including the newly approved plain one-word diagnostic without extraction schema/system prompt. | Zero successful generations/extractions. Original six attempts exhausted; one of two additional diagnostic calls used. Conditional extraction skipped after failure; no automatic retry authorized |

There was one sandbox DNS failure before the first live TTS request. No automatic live retries occurred. Actual Gnani credit consumption is unknown. Provider results, input hash and recordings remain in ignored `artifacts/provider-probes/`; see [provider notes](providers.md) for evidence and decoder lessons. These probes do not establish end-to-end application readiness or general accuracy. No paid overage is authorized.

## Historical remaining-work snapshot — 3 November 2026

| Boundary | Gap |
| --- | --- |
| Extraction/providers | Gemini and Gnani adapters implemented/tested offline. Successful live Gemini extraction and fresh adapter-level Gnani calls pending. Ordinary typed walkthrough still uses fixtures |
| Save recovery | Backend/HTTP/client path implemented and tested; tab closure/storage clearing can lose the client recovery reference |
| Browser | Fictional-job selector, typed/recorded Update, playback and inline saved receipt implemented. Broader record-history UI, final visual acceptance and technician walkthrough remain pending |
| Voice | Browser capture/playback, denial/empty fallback, cancellation and stale-response guards implemented/tested with synthetic audio. Human microphone quality, live integrated read-back and other demo devices remain unverified |
| Evaluation/usefulness | No broader transcript/audio evaluation, technician walkthrough or complete real recorded task |
| Delivery | Public source repository on GitHub, main pushed and first hosted CI successful. Earlier owner-private static visualization remains separate; no hosted working application, public demo/post or final submission |

Optional direct field editing and cross-session draft resume remain cut under the accepted 24 October rule. Hosting is optional; fresh confirmation is required for future deployment, and no social publication is implied. Current programme deadline checked 24 October: 10 November 2026, 11:59 PM IST; follow the emailed submission form and recheck requirements before submission.

## Earlier delivery plan — superseded by the current checkpoint

1. Inspect the AI Studio project's access/tier/quota and selected-model availability. The approved plain-generation diagnostic also returned 503, so do not keep repeating extraction or modify its schema based on that error alone. The conditional second request was not sent. Successful generation/extraction and later held-out evaluation remain required; further changed diagnostics need a concrete justified plan within authorization.
2. Complete one real local task: microphone → Gnani transcription → extraction → Python validation/clarification → review/readback → explicit confirmation → durable record/receipt. Use the neutral morphism direction as a working visual reference while functionality progresses.
3. Validate the completed browser voice path on the intended human microphone/device and inspect real spoken read-back. Duration/format are settled and synthetic Chrome denial/empty/cancellation/late-response tests pass; these do not substitute for human acoustic and live-provider acceptance.
4. Produce evaluation evidence: a held-out set of fictional updates, varied phrasing and recordings, reported field accuracy/task completion/latency, and failure examples. Keep development probes separate from evaluation and report sample sizes. Compare the same tasks against a manual form with a technician walkthrough when available; do not invent time savings.
5. Prepare a convincing submission: a real recorded task showing “two motors… sorry, one”, clarification and the saved receipt; explain the repair-business problem, why voice helps and what remains limited. Verify the official submission requirements before final packaging. Publish/share only after Ankit reviews and explicitly approves the concrete result.

Work may adapt to user feedback, provider results and demonstrated problems. Keep one authoritative product spec and one current checkpoint. See [working system](working-system.md) for roles and review gates, [design system](design-system.md) for pending visual choices, and [PLAN](../PLAN.md) for the wider delivery strategy.
