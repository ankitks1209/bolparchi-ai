# Current implementation status

Updated 2 November 2026. Current checkpoint: the local browser connects typed/recorded input, clarification/correction, review/read-back playback and receipt-based saving to SQLite. The neutral service sheet retains its job-number stamp, layered paper and raised controls. Native Chrome capture and the full local voice-to-receipt path pass with a synthetic microphone and fixture providers. Successful live Gemini extraction, human acoustic/playback validation and one complete real AI task remain pending.

## Current task: initial Git commit and GitHub push

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

## Latest verification — 1 November 2026

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

## Implemented and demonstrated

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

## Accounts and live provider evidence

Ankit's registration email confirmed challenge enrolment. An organizer reply allowed personal-email registration. Ankit reported Gnani dashboard access and 5,000 visible credits on 23 October. On 24 October he privately configured the key in Git-ignored `.env`; presence and owner-only permissions were checked without displaying it.

| Provider | Actual evidence | Remaining limit |
| --- | --- | --- |
| Gnani Timbre | Two earlier live requests returned HTTP 200. The new adapter reproduces the earlier normalization exactly using the retained 1.44-second WAV. No new live call this task. | Listening quality and integrated playback remain unverified; first response body was not retained |
| Gnani Prisma | One user-supplied 10.168889-second AAC/M4A recording returned HTTP 200 and `gnani-prisma-v2.5` in 5.508 seconds. Transcript preserved the requested two-to-one motor correction, pending status and follow-up. | Comparison against the suggested script only; no independent listening check, varied-speaker evaluation or app integration |
| Gemini | Metadata GET succeeded on 28 October. Five generation calls through 1 November returned HTTP 503, including the newly approved plain one-word diagnostic without extraction schema/system prompt. | Zero successful generations/extractions. Original six attempts exhausted; one of two additional diagnostic calls used. Conditional extraction skipped after failure; no automatic retry authorized |

There was one sandbox DNS failure before the first live TTS request. No automatic live retries occurred. Actual Gnani credit consumption is unknown. Provider results, input hash and recordings remain in ignored `artifacts/provider-probes/`; see [provider notes](providers.md) for evidence and decoder lessons. These probes do not establish end-to-end application readiness or general accuracy. No paid overage is authorized.

## Remaining work

| Boundary | Gap |
| --- | --- |
| Extraction/providers | Gemini and Gnani adapters implemented/tested offline. Successful live Gemini extraction and fresh adapter-level Gnani calls pending. Ordinary typed walkthrough still uses fixtures |
| Save recovery | Backend/HTTP/client path implemented and tested; tab closure/storage clearing can lose the client recovery reference |
| Browser | Fictional-job selector, typed/recorded Update, playback and inline saved receipt implemented. Broader record-history UI, final visual acceptance and technician walkthrough remain pending |
| Voice | Browser capture/playback, denial/empty fallback, cancellation and stale-response guards implemented/tested with synthetic audio. Human microphone quality, live integrated read-back and other demo devices remain unverified |
| Evaluation/usefulness | No broader transcript/audio evaluation, technician walkthrough or complete real recorded task |
| Delivery | Public source repository on GitHub, main pushed and first hosted CI successful. Earlier owner-private static visualization remains separate; no hosted working application, public demo/post or final submission |

Optional direct field editing and cross-session draft resume remain cut under the accepted 24 October rule. Hosting is optional; fresh confirmation is required for future deployment, and no social publication is implied. Current programme deadline checked 24 October: 10 November 2026, 11:59 PM IST; follow the emailed submission form and recheck requirements before submission.

## Next deliverables

1. Inspect the AI Studio project's access/tier/quota and selected-model availability. The approved plain-generation diagnostic also returned 503, so do not keep repeating extraction or modify its schema based on that error alone. The conditional second request was not sent. Successful generation/extraction and later held-out evaluation remain required; further changed diagnostics need a concrete justified plan within authorization.
2. Complete one real local task: microphone → Gnani transcription → extraction → Python validation/clarification → review/readback → explicit confirmation → durable record/receipt. Use the neutral morphism direction as a working visual reference while functionality progresses.
3. Validate the completed browser voice path on the intended human microphone/device and inspect real spoken read-back. Duration/format are settled and synthetic Chrome denial/empty/cancellation/late-response tests pass; these do not substitute for human acoustic and live-provider acceptance.
4. Produce evaluation evidence: a held-out set of fictional updates, varied phrasing and recordings, reported field accuracy/task completion/latency, and failure examples. Keep development probes separate from evaluation and report sample sizes. Compare the same tasks against a manual form with a technician walkthrough when available; do not invent time savings.
5. Prepare a convincing submission: a real recorded task showing “two motors… sorry, one”, clarification and the saved receipt; explain the repair-business problem, why voice helps and what remains limited. Verify the official submission requirements before final packaging. Publish/share only after Ankit reviews and explicitly approves the concrete result.

Work may adapt to user feedback, provider results and demonstrated problems. Keep one authoritative product spec and one current checkpoint. See [working system](working-system.md) for roles and review gates, [design system](design-system.md) for pending visual choices, and [PLAN](../PLAN.md) for the wider delivery strategy.
