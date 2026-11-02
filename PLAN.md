# BolParchi AI Service Update Agent

## Final project and delivery plan

Prepared for Ankit Singh on 20 October 2026, Asia Kolkata time. This is the consolidated planning baseline for review. It authorizes no new product implementation, deployment, paid service, or social posting by itself. Earlier drafts of the plan are superseded where they conflict with this document.

**Product decision:** build a focused voice-assisted application that converts a repair technician's visit update into a reviewed service record. The model interprets language; application code controls validation, confirmation, and saving. Ankit confirmed the name BolParchi on 20 October 2026. This is not a claim of trademark availability.

**Primary goal:** produce a useful, understandable working demonstration and a technical project Ankit can defend in an internship interview. Awards are secondary. No project or distribution plan can guarantee selection.

**Planning assumptions:** solo builder, approximately five focused hours per day through the first demo, Hindi/Hinglish, fictional job data, one business workflow. Time availability, provider access, and spending budget remain unverified. These are execution inputs to establish in the first session, not reasons for another round of product brainstorming.

**Engineering setup amendment (20 October 2026):** `docs/spec.md` now holds the consolidated product acceptance criteria; this plan retains delivery strategy and schedule. `AGENTS.md` and `agent_docs/` define the approved lean development workflow: pytest + Ruff, no hooks/typecheck/coverage gate. Product implementation remains paused.

**Execution start (21 October 2026):** Ankit explicitly authorized beginning this plan. Work has started with §18's field contract and provider preparation. This later authorization supersedes the paused setup state above; account setup is still required for live probes. See agent_docs/status.md for current evidence.

## 1 Selection strategy and verified requirements

Gnani's current page says verified engagement on the nominated demo posts determines the eligible-project shortlist; individual skills and interviews determine offers. Final submission closes on 10 November 2026 at 11:59 PM IST. Awards are separate. [1]

Entries require genuine Gnani technology, a working public demo, a written explanation, identified model/API use and contributions, and nominated LinkedIn/X links. Tag Gnani and use #GnaniAI and #GreatIndianAIInternshipChallenge. Purchased engagement, bots, paid promotion, and engagement exchanges are prohibited. [2]

The FAQ excludes Agent Builder, says Evon requires self-hosting, directs entrants to the emailed submission form, and asks for synthetic data. The registration text still mentions a participant workspace; use current emailed instructions and clarify contradictions with organizers. [1][2]

We will allocate effort to three outcomes: a complete user task, a clear public demonstration, and evidence of engineering decisions. We will not infer an engagement threshold or scoring weights that are not published. The useful award alignment is real-world usefulness, code-mixed speech, and demo clarity; we are not claiming eligibility for a telephonic-noise award from workshop microphone recordings.

## 2 User and problem

The primary user is an appliance-repair technician working with a small repair business. The task begins after a visit, when the technician needs to record the diagnosis, job status, required part, and follow-up. The owner can inspect the resulting record in the same prototype. Separate staff roles and enterprise integrations are outside v1.

The hypothesis is that an ordinary voice message leaves someone else to listen, find missing details, and enter the update. BolParchi prepares a structured record and asks about omissions immediately. This is a hypothesis until tested with users; we will not advertise time saved or fewer mistakes without measurement.

Within the first two days, ask two technicians or one technician and a shop owner how they currently record a visit, what gets missed, and whether a short confirmation interaction would help. Obtain permission for a fictional walkthrough. A positive conversation is initial feedback, not validated demand. If nobody is reachable, document the assumptions and continue with clearly labelled prototype evidence. Only change the workflow if feedback exposes a material mismatch; preserve the voice-to-confirmed-record architecture.

## 3 Product promise and demonstration

**Plain-language promise:** speak your service update, resolve missing details, and confirm a record you can inspect.

Example: the technician selects fictional job 104 and says, "Motor kharab hai. Do motor... sorry, ek motor chahiye." The application shows one motor and asks for the remaining follow-up detail. After the response, it presents the full update, reads it aloud, and saves only when the technician presses Confirm and save.

The demonstration must show the actual application, real provider calls, a visible clarification or correction, and the resulting saved record. A correction supplied directly as JSON is a core test, not evidence of speech understanding. A locally recorded real application demo is acceptable for our delivery plan; a public live application is optional, subject to organizer requirements at submission.

## 4 Feature boundary

| Required for v1 | Optional after the complete flow works | Deferred |
| --- | --- | --- |
| Fictional job list and fixed-job update screen | Direct field-editing form | Voice-only confirmation |
| Push-to-talk and typed-message fallback | Reopening unfinished drafts across sessions | More languages |
| Prisma transcription and one extraction model | Small noise-condition comparison | Telephony and streaming |
| Patch validation and one clarification at a time | Public hosted interactive demo | Inventory, payment, messaging integrations |
| Corrections, cancellation, stale-result rejection | Additional visual polish after usability is verified | Multi-agent runtime, vector database, RAG |
| Spoken-job mismatch hold and resolution | | Evon hosting and model training |
| Review card and explicit confirm button | | Recurring autonomous maintenance |
| Reliable save, duplicate protection, bounded recovery | | Full business administration platform |
| Saved-record view and collapsible trace panel | | |

**Cut rule:** if the voice flow is not complete by 24 October, remove the edit form and draft-resume work. Typed messages remain the correction fallback. Cut optional features before correctness controls. If required work slips, move the public posting date modestly instead of presenting simulated functionality as live.

## 5 User journey and interface

There are three main views: Jobs, Update job, and Saved record. Use a mobile-friendly layout, large record control, clear processing states, a readable draft card, highlighted changed fields, and an unmistakable confirm button. Keep engineering traces collapsed in normal use; expand them for evaluation and the technical demo.

1. Select a fictional job. Its identity stays visible and fixed for this draft.
2. Record a short message or type it. Show the transcript before applying the extracted patch.
3. If the spoken job differs, hold the entire patch. Offer Apply to selected job or Discard message. Revalidate any held patch before applying it.
4. Apply valid changes and ask one focused question when required information is missing or invalid.
5. Display the latest draft and optionally speak its read-back. An edit invalidates earlier approval. Timbre failure leaves visual review available.
6. On Confirm and save, bind approval to the exact displayed draft revision and hash. Disable confirmation during pending input processing or unresolved save operations.
7. Show the saved receipt and resulting job, part request, and follow-up task when present. These are records inside our own prototype, not external orders or appointments.
8. Cancel an open draft without updating the job. A late response cannot revive it. Cancellation is unavailable while a save may already be completing.

Empty audio leads to a repeat request and an immediate typing option; after two empty attempts, foreground typing. A transcription or extraction failure preserves usable text and offers retry. If extraction remains unavailable, the app does not pretend typed messages can bypass that same dependency; preserve the draft and explain the blocker. Stop old audio playback when the draft changes.

## 6 Responsibility and architecture

| Component | Responsibility | Boundary |
| --- | --- | --- |
| Browser UI | Job selection, recording, typed input, review and confirmation | No provider keys or database writes in browser code |
| Prisma | Speech to text | Transcript is evidence to interpret, not executable instructions |
| Extraction model | Current-message patch and spoken job reference | No validation verdict, confirmation authority, or save tool |
| Python application | Patch application, conditional validation, questions, read-back and state transitions | Sole workflow controller |
| SQLite store | Draft state, submission receipts, atomic job and task writes | Persistent local file; one service instance for hosted v1 |
| Timbre | Speak application-generated questions and results | Its failure cannot change the save outcome |
| Trace module | Operation names, versions, revisions, durations and result codes | Observable events, not private model reasoning |

Input paths converge on the same extraction function. The runtime is a controlled workflow using an LLM, not an autonomous planner. Calling it a Service Update Agent describes the product; the technical explanation will disclose the actual architecture.

## 7 Data and patch contract

Use a small FIELD_SPECS definition for field types, nullability, limits, allowed values, and whether a field is patchable. Derive the model-facing schema and basic Python validation from that source. Keep conditional business rules as ordinary tested functions. Tests must check behavior at boundaries and incompatible inputs, not just compare two schemas produced by the same generator.

| Field | Meaning and rule |
| --- | --- |
| job_id | Set from the UI at draft creation; immutable; must resolve to a known job |
| diagnosis | Required short text; preserve the technician's meaning |
| status | Required: completed or pending |
| part_needed | Optional requested part label; no inventory or compatibility claim |
| quantity | Required when a part is requested; integer 1 to 20 as a prototype limit |
| follow_up | Required for pending jobs; optional for completed jobs; free text rather than a scheduled appointment |

The extraction envelope contains set, clear, and spoken_job_id. Field changes omit unstated information; null is not an implicit delete. Clear is explicit. The selected job never appears in mutable set/clear operations.

- Reject unknown fields, invalid types, and a field appearing in both set and clear.
- Clearing part_needed also clears quantity. Reject contradictory simultaneous instructions to clear the part and set a quantity.
- Replacing a part keeps the existing quantity unless changed or cleared, a documented v1 assumption made visible at review.
- Resolve an explicit correction within a message to its final stated value. Ask when the meaning is unresolved; do not invent a quantity or appointment.
- A completed job does not require a part or follow-up, but supplying them is not automatically forbidden. Confirmation makes the resulting actions visible.
- Ignore any model-supplied completeness flags. Code computes missing and invalid fields and chooses the next question.
- Test both native-script and romanized transcripts. Number normalization must be measured against actual Prisma output rather than assuming it returns romanized Hindi.

Requests carry draft_id, starting revision, and request/turn identity. One application function verifies identity, expected revision, open state, and applicability before changing the draft. Reject stale extraction, transcription-triggered work, or held mismatch patches. Any edit increments the revision and invalidates confirmation.

## 8 Confirmation and save contract

The UI sends the exact revision and hash it displayed. The server verifies them and the complete valid record. The model cannot invoke commit. Freeze editing while a save attempt is unresolved. Store the submission ID on the server and retain it in the client so refresh or retry cannot silently create a new logical save.

A transaction updates the job, records any part request and follow-up task, stores a receipt, and marks the draft saved. Submission-ID and draft uniqueness prevent duplicate application. Successful replay returns the original receipt even though the draft is now saved. A genuinely new update uses a new draft.

Retry only known transient failures, at most three total attempts using the same submission ID, with short bounded backoff. Expected validation, stale-state, cancellation, and confirmation rejections return immediately. Retryability and outcome certainty are separate properties; a boolean retryable flag alone is not proof of rollback.

| Evidence | UI behavior |
| --- | --- |
| Matching successful submission receipt | Saved; display the receipt |
| Confirmed rollback or rejection with no attempt capable of committing | Not saved; offer an appropriate next action |
| Status unavailable or a previous attempt may still complete | Save status unresolved; editing remains locked |

A missing status row alone cannot prove failure. In-flight certainty must come from backend operation ownership/state, not just a browser spinner. Use bounded status checks, then a manual Check status action if needed. Do not add a distributed job system for this prototype; use a single-process backend and preserve uncertainty when it cannot be resolved. Saved receipts must survive restart when persistence is claimed.

## 9 Technology and tool use

| Tool | Planned use | Why it earns its place |
| --- | --- | --- |
| Gnani Prisma REST | Short push-to-talk transcription | Central Gnani use; simpler than streaming [3] |
| Gnani Timbre REST | Questions, read-back, final outcome speech | Makes the interaction usable by voice |
| Gemini structured output | Initial extraction-provider candidate | JSON-schema output is documented; application still checks semantics [4] |
| Python and FastAPI | Backend and API endpoints | Fits Ankit's primary language and can serve static assets [6] |
| HTML, CSS and small JavaScript modules | Responsive three-view interface and microphone capture | Avoids a second frontend build system for this scope |
| SQLite | Local transactional state and receipts | Reuses the prototype design; limited to one hosted service instance |
| pytest | Unit, integration, retry and state-transition tests | Deterministic evidence |
| One evaluation script and versioned JSONL cases | Transcript and real-audio evaluation | Repeatable comparisons with explicit denominators |
| Git and GitHub | Small commits, reviewable changes, reproducible submission | Evidence of ownership and development history |
| Codex | Scoped implementation, tests, review, documentation, debugging | One primary coding assistant and one source of truth |
| Browser inspection tools | Microphone, permission, confirmation, layout and recovery checks | Verifies user-visible behavior |
| Official documentation and organizer support | Contracts, access issues, eligibility ambiguities | Avoids relying on stale summaries |
| Screen recorder | Honest 60-second demo and longer technical walkthrough | Selection-facing output |
| Render, if a hosted demo is chosen | Single Python service with persistent storage | SQLite cannot rely on its default ephemeral filesystem [7] |

Retain gemini-3.8-flash as the initial candidate; reverify the exact ID and supported settings against official documentation and an account probe before implementation. Access and suitability are unverified. Pin the successful model ID, SDK/API version, prompt, and schema. Do not change models merely because a newer release appears. If unavailable, choose one accessible structured-output model after a short probe; do not build a broad model-router project. [4][5]

Browser capture must produce an API-supported format; verify the actual browser recording MIME type. Prefer a small PCM WAV capture path if it avoids a server conversion dependency. Keep clips short and reject oversized/empty input before billing an API call. Test microphone permission and audio playback on the browser used for the demo. [3]

Tools available to the assistant are used selectively. A native document or spreadsheet may help submission preparation but is not a product dependency. Image generation is optional branding only and must not fabricate interface screenshots or demonstrations. Sites is not the default host for this Python/SQLite architecture. No vector database, LangChain/LangGraph layer, voice cloning, automation scheduler, or multi-agent swarm is required for v1.

Use supported terminal, connector, and browser tools where available. Check actual network access without bypassing restrictions. If a provider cannot be reached in the working environment, supply a small local probe for Ankit to run. Keep secrets in environment variables and exclude them from Git, logs, screenshots, and exported traces.

## 10 Applying the Skill Checklist

The framework governs our development procedure and runtime boundaries. It does not require shipping a filesystem Skill loader inside the voice application.

| Dimension | Decision |
| --- | --- |
| Trigger design | User-invoked: Update job starts the runtime session; an explicit development task starts engineering work. Neither a pasted assistant suggestion nor a casual job mention authorizes work. |
| Structure | Keep extraction instructions short. The schema is generated from the contract. Load development references by task rather than putting the whole project history in every prompt. |
| Steering | Use operation labels with defined inputs, checks, and evidence. The extraction model is steered only toward proposing changes. |
| Pruning | Retain instructions only when they enforce a requirement or improve measured behavior. Preserve code-level integrity requirements even when shortening prompts. |

The **Verify BolParchi Change** routine is preserved through six explicit development skills in `skills/`: write-spec, tdd-feature, code-review, ui-polish, debug and security-check. `agent_docs/skills-framework.md` maps trigger, structure, steering and pruning to those procedures. The earlier prepared single-skill patch was not installed and must not be applied over this setup.

| Leading word | Leg work | Required evidence |
| --- | --- | --- |
| SCOPE | Identify the requested change, affected contract, and acceptance case | Small task statement; no unrequested feature expansion |
| INSPECT | Read relevant code and current official provider contract | Concrete input/output expectations |
| CHANGE | Implement the smallest coherent change after approval | Reviewable diff |
| VERIFY | Run relevant tests and a real integration check when applicable | Test output or an explicitly recorded blocker |
| PRUNE | Remove redundant instructions or code only after comparison | Before/after behavior on the affected cases |
| REPORT | Explain what works, limitations, and next task | Evidence-linked completion note |

Current context pointers are `docs/spec.md`, `agent_docs/architecture.md`, `agent_docs/testing.md`, `agent_docs/design-system.md` and `agent_docs/status.md`. Separate provider/evaluation references may be added when their implementation needs them; do not duplicate contracts. These development files are not loaded by the runtime product.

Runtime trace labels remain GROUND, EXTRACT, VALIDATE, CLARIFY, CONFIRM, COMMIT, and VERIFY, with separate STT and TTS timing events. They describe code operations; they do not ask the extraction model to perform unauthorized steps or reveal internal reasoning.

## 11 Applying the broader AI principles

**Measure then delete:** start with a concise extraction prompt. Compare at most two or three variants. Remove one instruction group at a time, run each variant several times, and keep a held-out set. Do not delete the production prompt or application protections on a model-release announcement. Pin a baseline and make experiments reversible.

**Allow useful flexibility:** accept out-of-order details, mixed language, and corrections. Preserve the user's meaning without forcing a long questionnaire when the message already contains the required facts. Fixed validation and save rules define the action boundary.

**Probe capabilities:** try harder fictional examples with two corrections, irrelevant speech, negation, native-script numbers, and a spoken job mismatch. Adopt additional behavior only if it is useful and reproducible. A large codebase rewrite is not an experiment needed for this deadline.

**Verify externally:** compare output with expected patches, explicit user corrections, validator results, and stored receipts. Model self-confidence or a second model's praise is not a correctness gate.

**Dynamic behavior:** code selects clarification, review, cancellation, or recovery from observed state. Add another model call or parallel worker only if a specific evaluation failure demonstrates the benefit. No runtime swarm is planned.

**Routines:** run the regression command before merging a change. Later CI may run it automatically on commits. No recurring background task is scheduled by this plan.

**Evidence before claims:** a failed scenario becomes a reproducible case before selecting a fix. The supplied talk's timestamps and named model examples are reference ideas, not verified evidence that coding is solved or safeguards can generally be removed.

## 12 Evaluation and release evidence

Maintain three separate forms of evidence:

1. **Core tests:** patch conflicts, dependent clears, immutable job ID, missing/invalid fields, revision invalidation, cancelled-state rejection, duplicate attempts, concurrency, rollback, late responses, and uncertain outcomes. The earlier review reported 60 passing core tests; that historical result is not evidence for subsequently planned features. Rerun and extend the suite during implementation.
2. **Extraction cases:** approximately 30 distinct transcript scenarios split into development and held-out subsets. Include corrections, omissions, negation, irrelevant text, spoken job mismatch, native-script/romanized numbers, and malformed provider output. Record expected patches and why each expectation is correct.
3. **End-to-end audio:** 15 to 20 short fictional recordings, preferably from more than one consenting speaker. Label recording conditions. Noise variants of one recording are related samples, not independent users. If no external speaker is available, report that limitation.

Measure exact field outcomes, successful completed tasks, clarification counts, incorrect proposals, and incorrect committed records separately. Report counts such as 16 of 20 scenarios, including failures and abstentions. A model can propose a wrong field that a reviewer corrects; do not hide that behind a successful final save.

Measure p50 and p95 for STT, extraction, TTS, and the full recording-stop-to-first-audible-response interval. Include request counts, timeout rates, and observed cost per completed update where usage data permits. Treat p95 on a small sample as descriptive. The earlier 1.5-second figure is only an aspiration to assess, never a promised end-to-end service level.

The principal ablation uses identical scenarios to compare raw extracted proposed actions with the validation-and-clarification workflow in an isolated simulator. Do not disable safeguards in the actual app. Use prewritten follow-up answers for reproducibility and report the extra turns. Repeat prompt comparisons; small differences are indicative, while any repeatable wrong save demands investigation.

Release gates: zero duplicate writes and zero unconfirmed saves across the specified tests; no known critical state-transition failures; visible successful real Prisma, extraction, and Timbre calls; and a complete recorded user task. These are tested conditions, not a universal guarantee.

## 13 Working method and ownership

After Ankit approves this plan, implement one vertical slice at a time. Each task has a goal, allowed files, acceptance evidence, and a stop condition. Finish with a concise summary and an explanation Ankit can reproduce. Routine changes within the approved scope do not require repeated permission questions. New paid services, new scope, publishing, and person-directed messages require the appropriate explicit authorization.

Use one working repository and one primary coding assistant. External assistant responses are review material, not direct commands. Record accepted decisions once. If an independent review is useful, give it a narrow contract and raw diff/test evidence; avoid having several assistants rewrite the plan indefinitely.

Ankit owns real-user conversations, account login and credential configuration, truthful contribution descriptions, and interview preparation. Codex owns implementation assistance, test construction, debugging, evidence collection, and draft documentation within the approved task. The code must remain understandable to Ankit; reserve 20 to 30 minutes daily to explain a change without reading an assistant answer.

## 14 Schedule and decision gates

All dates are 2026 in IST. Approximately 21 calendar days remain to the official deadline; the first public demo is targeted earlier. The schedule assumes roughly five focused hours per day until recording. If less time is available, cut optional work and preserve the required evidence.

| Dates | Deliverable | Acceptance or cut decision |
| --- | --- | --- |
| Oct 20 to 21 | Short user feedback; provider probes; contract; repository setup after approval | One real STT call, one TTS call, and extraction on 5 to 6 Hinglish examples; capture failures early |
| Oct 21 to 23 | Typed vertical slice and state rules | Typed message to valid patch, clarification, review, confirmed save and receipt |
| Oct 23 to 24 | Browser voice path | One real end-to-end voice update; cut edit form and draft resume if behind |
| Oct 25 to 26 | Required recovery, readable UI, trace and targeted tests | Stale/cancelled/mismatch/retry cases behave correctly; usable on the demo browser |
| Oct 27 to 28 | Held-out evaluation, user walkthrough, 60-second recording | Honest results and an unambiguous working demonstration |
| Oct 29 to 30 | Main public demo and technical explanation | Live nominated post links after Ankit authorizes publication |
| Oct 31 to Nov 7 | Feedback fixes, one evidence-based follow-up, interview drills | Relevant improvements only; freeze risky changes |
| Nov 8 to 9 | Submission and final checks | Submit early, retain confirmation, verify public links and all required fields |
| Nov 10 | Contingency only | Avoid treating the last hour as the planned submission time |

If access is blocked on day one, build the typed/stubbed path while resolving access through legitimate support. A mock-only application is not a completed Gnani integration. Do not spend three days polishing architecture before discovering a provider cannot be used.

## 15 Demo and genuine distribution

A suggested 60-second sequence: 0 to 8 seconds show the technician's recording problem; 8 to 25 seconds show a natural spoken update and correction; 25 to 38 seconds show one clarification and the resulting record; 38 to 48 seconds show explicit confirmation and the saved receipt; 48 to 60 seconds identify Prisma, Timbre, the extraction model, and one measured result or honest limitation. Use captions and fictional customer labels. Do not cut around hidden manual changes or speed up a latency claim without disclosure.

Start sharing useful build observations once there is something concrete to show. Publish the principal working video by the target date. Share with relevant college, developer, and small-business communities where their rules permit; ask for specific feedback, not reciprocal engagement. Nominate one main post per platform and point follow-ups back to it. Do not assume follow-up likes count toward the nominated post.

Aim for one credible user walkthrough and one concise technical evidence post. Explain the problem, what the system actually does, why Gnani speech matters, and what happened in testing. Retain failures in the evaluation report. A polished video cannot substitute for being able to explain the implementation.

## 16 Submission and interview package

Prepare a repository with reproducible setup, synthetic fixtures, a sample environment file without secrets, actual model versions, architecture and limitations, test instructions, and the evaluation counts. Include the main demo, public post links, written project explanation, and an accurate account of Ankit's work and AI assistance. Follow the current official submission form rather than invented requirements.

Practice explaining why the model returns patches, why the job cannot change, how stale requests are rejected, how retries differ from new submissions, what validation catches and cannot catch, and which failure led to each important design choice. Be able to trace one recording through every stage and change a small rule independently.

## 17 Cost and deployment decisions

Use available programme credits and existing provider allowances first; their coverage and remaining balance must be checked in the actual account. No monetary budget or free-tier entitlement is assumed. Log request counts and actual usage, cap clip duration and retries, and estimate a completed-update cost from probes before a public endpoint is exposed.

Local execution plus a real demo video is the baseline. If Ankit chooses hosting, run one backend instance and put SQLite on persistent storage. Render documents paid persistent disks and an otherwise ephemeral filesystem. Do not promise saved data survives restart on an ephemeral deployment. [7]

Before public interactive access, configure server-side secrets, limited access, request limits, and separation of each demo session's fictional drafts. A protected reviewer demo is sufficient for the optional hosting path; production multi-user administration is outside v1.

## 18 Final decisions and next action

The name, user task, architecture, feature cut lines, tool responsibilities, framework application, evaluation approach, and schedule are now consolidated. Reopen a decision only for evidence of user mismatch, provider failure, material cost, a rule conflict, or a demonstrated correctness problem. An interesting new feature alone does not reopen scope.

The first authorized implementation task will be provider probes and the field contract, followed by the typed vertical slice. Account access, available time, and budget are checked during that first session. They do not require another planning cycle. This plan does not authorize product implementation, automation, deployment or social posting. The separately approved engineering setup adds repository skills and checks, not product features.

## Sources checked on 20 October 2026

[1] Gnani challenge and FAQ: https://www.gnani.ai/internship

[2] Gnani participation terms: https://www.gnani.ai/great-indian-ai-internship-registration-form

[3] Gnani quick start: https://docs.gnani.ai/api/introduction/quick-start

[4] Google structured output documentation: https://ai.google.dev/gemini-api/docs/structured-output

[5] Google model catalogue: https://ai.google.dev/gemini-api/docs/models

[6] FastAPI static files: https://fastapi.tiangolo.com/tutorial/static-files/

[7] Render persistent disks: https://render.com/docs/disks

The Skill Checklist and the talk summary were supplied by Ankit. Their useful principles are applied above; model-release claims and timestamps from that summary were not independently verified.
