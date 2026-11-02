# ADR-006: Persist save identity, attempts and terminal fences

Date: 28 October 2026. Status: implementation of the accepted confirmation, idempotency and uncertain-save requirements (AC-07/08/09/13), resumed by Ankit.

Context: receipts and duplicate protection existed, but a caller could not distinguish a lost response from a failed transaction or safely unlock a draft after uncertainty. A missing receipt alone cannot rule out a later commit.

Decision: `SaveRecovery.save` is the application entry point for an explicit Confirm and save action. It requires the reviewed revision/hash and one client-created submission ID. Store atomically validates the review, confirms it and creates a durable `save_requests` reservation while locking the draft as `saving`. A partial unique index allows one pending reservation per draft. The same ID is bound to the same review, including replay of older receipts.

Delivery attempts are reserved in separate transactions before sending, so rollback, concurrent callers and process reopening cannot reset the three-attempt budget. A crash between reservation and delivery can conservatively consume an attempt. The normal business write still uses Store's atomic transaction and unique receipt. The legacy direct confirm/save API remains for core tests/demo; future application endpoints must use SaveRecovery for the full recovery contract.

Timeouts/connection failures and identified SQLite BUSY/LOCKED errors may retry with the same ID. Validation, stale review, cancellation and not-confirmed responses never retry. Malformed responses are unresolved, never trusted as success. Only a stored receipt establishes saved. Store distinguishes a confirmed rollback from an exception that may follow commit; raw exceptions are redacted.

Before reporting not saved after a definitive rejection/rollback, Store closes the reservation under a write transaction and clears confirmation. This fences every queued delivery with that ID before unlocking editing. If another writer is already committing, the fence waits for SQLite serialization, rechecks the receipt and returns saved if the commit won. A closed ID cannot be reused for a new review.

Unknown outcomes keep the durable reservation and `save_unresolved` draft state. Two explicit status polls are followed by a transactional unresolved-state update/recheck; manual Check status performs no new delivery. A late commit can subsequently resolve to saved. Database failures can leave the result conservatively unresolved; neither missing rows nor a timeout causes an unlock. SQLite's existing busy timeout applies per operation, not as an overall wall-clock deadline. HTTP/UI scheduling and retry presentation remain pending.

Alternatives: browser-only locks/counters, new IDs on retry, or interpreting missing status as rollback. These lose identity after refresh, reset budgets or permit duplicate/late writes. The additive table preserves old receipts and keeps coordination within the existing single-instance SQLite architecture.

Evidence: 23 new tests with real SQLite and controlled delivery/commit faults cover lost response after commit, late commit, rollback, terminal fencing, concurrent retry budgets, reopened state, nonretryable rejections, exact-review binding, malformed replies and old-schema receipts. These are backend recovery tests, not browser disconnection tests or proof of universal correctness.
