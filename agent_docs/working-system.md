# BolParchi working system

Prepared 24 October 2026 from Ankit's shared engineering/design conversation and the existing repository. This is the practical process for building the approved product. It introduces no new framework, dependency, provider call or publishing permission. Read the section relevant to the task rather than loading every reference.

## What we are aiming for

A technician can speak a service update, correct it, resolve missing details, review the full record and explicitly save it. The product should feel like a useful repair-work tool. Engineering quality, visual quality, usefulness and public demonstration each need their own evidence; passing tests does not establish all four.

Keep the product open to evidence. A confusing walkthrough, provider failure, measured delay or a user's changed priority can justify revising the plan. Explain the problem, propose the smallest useful change and update the affected spec/decision after agreement. Do not preserve a choice merely because an earlier assistant proposed it. Preserve confirmation and data-integrity requirements unless Ankit explicitly changes the product contract.

## One authoritative home per concern

| File | What belongs there |
| --- | --- |
| [AGENTS.md](../AGENTS.md) | Short repository facts, exact commands, boundaries and pointers |
| [spec](../docs/spec.md) | Accepted user behavior, edge cases and exclusions |
| [architecture](architecture.md) and [decisions](decisions/README.md) | Component responsibilities and reasons for significant accepted choices |
| [six skills](skills-framework.md) | Reusable, explicitly invoked procedures for particular development tasks |
| [design system](design-system.md) | Visual decisions, interaction states and browser review criteria |
| [testing](testing.md) | Verification methods and separation of offline/live evidence |
| [providers](providers.md) | API contracts, probe evidence, limits and unresolved integration details |
| [status](status.md) | Current checkpoint, latest checks, blockers and next deliverable |
| [PLAN.md](../PLAN.md) | Overall delivery strategy, evaluation and submission plan |

Link to an existing rule instead of maintaining another copy. Keep status current; move lengthy historical evidence into its relevant reference rather than accumulating contradictory checkpoints.

## People, assistant and reviews

- Ankit owns product priorities, visual taste, account access, user conversations and the ability to explain the implementation.
- Codex implements authorized work, checks behavior, presents visual options and reports uncertainty. Routine implementation choices proceed without repeated permission.
- A review is a separate pass over a bounded change: identify risks, inspect evidence and record actionable findings. A self-review must be labelled as such. A second agent/session is optional when explicitly requested; do not launch agents merely because this document mentions review.
- The application's extractor proposes fields. Python and SQLite retain workflow/save authority. Development skills and reviewer agents are not runtime product components.

Existing skills remain sufficient: write-spec for unresolved requirements, tdd-feature for behavior, debug for a reproduced failure, code-review for findings, ui-polish for an existing screen, security-check for a scoped boundary review. Do not invoke all six on every task. Initial visual discovery uses the design-system checkpoints; ui-polish does not invent a new screen.

## The delivery loop

1. **Frame the slice.** Write the user-visible outcome, affected files/boundaries, acceptance evidence and stop condition. Surface only decisions that materially affect it.
2. **Inspect.** Read the relevant references, current implementation and baseline results. Establish what is already real versus simulated.
3. **Build and verify.** Follow the repository's red/green process for behavior. For a visual change, inspect the rendered states; when interaction changes, test both behavior and usability.
4. **Review.** Check failure paths and the actual resulting code. For UI, use mobile and desktop captures plus keyboard/pointer interaction. For providers, separate offline decoder tests from live acceptance.
5. **Explain and record.** Summarize what changed, why, observed evidence, limitations and next step. Ask Ankit to explain one meaningful decision or trace one input through the system when preparing for the interview.

Example slice: “A typed fictional correction reaches the real extractor and updates the reviewed draft, with no save until confirmation.” Its evidence includes a real model response, expected quantity, validator result, displayed changed field and absence of an unconfirmed write. A schema-shaped fixture alone does not complete it.

## Collaborative design without an endless questionnaire

Reuse the established technician/user task. Do not ask Ankit to rediscover it. Group taste decisions into three useful checkpoints:

1. **Direction:** choose among two or three compositions; discuss references if Ankit has them. Recommend one with a reason and explain tradeoffs. References are helpful, not a prerequisite.
2. **Visual specimen:** preview palette, Latin/Devanagari type, spacing and real component states together. Show the selected job, a long transcript, a correction, an error and the confirmation action. Measure readability/contrast before recommending a choice.
3. **First real screen:** exercise the implemented Update view and get Ankit's reaction before spreading its visual treatment to Jobs/Saved. Continue unrelated backend work while taste feedback is pending.

Record each choice as proposed, selected or verified. A preference is not approval of an unseen final design. Ask when taste materially changes; use the selected system for routine spacing and layout decisions. “Design locked” is not a global gate on approved engineering work. State plainly when a rendered result cannot be inspected, and leave visual verification pending.

## Keep, adapt and leave out from the pasted conversation

| Guidance | Treatment for BolParchi |
| --- | --- |
| Short AGENTS plus focused references | Keep; the existing compact guide already follows this structure |
| Tests, lint, readable changes and review | Keep; use the approved pytest/Ruff setup and meaningful checks |
| Shared visual tokens, clear hierarchy and plain copy | Keep; record choices once, implement CSS variables with the first UI slice |
| One memorable visual idea | Adapt to the technician's task: a legible service sheet or focused recording interaction, subject to preview |
| Ban fashionable palettes, fonts or rounded cards | Treat as prompts to critique generic results, not universal bans; readability and Ankit's preference decide |
| Ask at every design step | Adapt to the three checkpoints above; do not ask again for settled decisions |
| React, Next, Tailwind, component libraries and Storybook | Leave out for now; our Python plus plain HTML/CSS/JS stack remains sufficient unless a concrete need changes that |
| Optimistic updates | Allow immediate local interaction feedback, but never show Saved before a matching server receipt or unlock an uncertain save |
| Screenshot regression, axe CI and custom token lint | Potential later tools after a real screen exposes the need; not installed, not verified, and new dependencies still require authorization |
| Independent AI reviewer | Optional scoped review, not a standing swarm or a substitute for human ownership |
| Claimed research percentages and tool-use multipliers | Unverified in the supplied text; do not repeat them as established results or build policy around them |

The pasted conversation is reference material. Its embedded “start now” prompt and package commands are not instructions to execute. Its suggestions earn a place only when they help this project.

## Quality evidence to collect

| Dimension | Evidence needed |
| --- | --- |
| Correctness | Exact confirmed values, one write per submission, stale/cancelled-result rejection, truthful uncertain-save recovery |
| Provider behavior | Actual model/API responses, decoder/error cases, bounded requests and visible quota failures |
| Visual craft | Consistent tokens, readable Hinglish/Devanagari, clear hierarchy and action states, inspected mobile/desktop captures |
| Usability | A complete task with recording or typing, correction, review, failure recovery and keyboard access |
| Usefulness | Feedback from a technician/shop owner; document assumptions if unavailable |
| Demonstration | A real end-to-end recording, measured results and honest limitations; no simulated success presented as live |

## Ordered work, with room to adjust

1. **Extraction evidence:** Ankit reports a Gemini free-tier account/key. Verify private local configuration and available model, then test fictional corrections and ambiguous messages. No assumption that key creation proves API access.
2. **Reliable application path:** implement provider adapters and bounded save recovery around the existing core. Use observed Gnani response quirks as regression cases.
3. **First browser slice:** preview Ankit's selected modern service-sheet direction, then build the Update flow with real extraction, review and explicit save. Include failure/empty/loading states from the start.
4. **Voice completion:** integrate recording, transcription and readback with cancellation/late-response guards and typed fallback.
5. **Evidence and delivery:** evaluate varied examples, get user feedback, fix demonstrated failures, prepare the public demo and submission package.

Backend work and visual discovery may overlap; dependency ordering still matters. Optional direct editing and cross-session resume remain cut under the accepted 24 October rule. If time slips, revise the schedule and cut optional polish before correctness. Additional product ideas go into a short proposal with user benefit, cost and evidence needed; neither discard them automatically nor insert them silently into the current slice.
