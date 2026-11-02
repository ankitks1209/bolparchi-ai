# ADR-004: Persist typed turns and guard every completion

Date: 22 October 2026. Status: implementation of the approved typed-workflow and cancellation requirements, resumed by Ankit.

Context: the field contract could validate a model patch, but it had no conversational lifecycle. A delayed result could arrive after a correction or cancellation; the selected-job mismatch had no apply/discard path. Provider accounts are not set up, so the workflow must be testable with an injected extractor and real SQLite.

Decision: Store owns message-state writes in an additive `draft_inputs` table, with one latest message per draft. It stores the original transcript, starting revision, fresh turn ID, processing/held/error/applied state, validated held patch and changed fields. This is current-message recovery, not full conversation history or optional cross-session draft-resume UI.

Begin input atomically invalidates confirmation before extraction. The callback runs outside database transactions and receives only message text and a copied record. Completion, failure, retry and mismatch release share a guard checking draft identity, exact positive-integer revision, current turn ID and expected open/input state. Explicit new messages supersede previous requests, even when the record revision has not changed. Direct structured edits require a revision and supersede pending input. Rejected edits leave state intact.

Ambiguity holds the entire patch and asks for a clearer full update. A spoken-job mismatch holds the entire patch for explicit apply-to-selected-job or discard; release revalidates the stored patch. Only the explicit apply path may disregard the spoken job reference. Model output cannot confirm, save or release a mismatch.

Cancellation closes an open draft, increments its revision and clears confirmation. Cancelled drafts reject updates, confirmation, saves and late results. SQLite transaction serialization ensures a cancellation waiting behind a successful save returns already_saved; it cannot claim rollback while that transaction commits. The broader uncertain-save recovery wrapper remains a separate required task.

Workflow derives clarification, processing, error, review and terminal views from a stored snapshot. Blocking input prevents confirmation/saving. Failure keeps the message and permits a manual retry with a fresh guarded turn ID; raw provider exceptions are neither returned nor stored. The existing Store confirmation/save methods remain explicit actions and retain submission replay. The read-back asks for Confirm and save, not spoken authorization.

Alternatives: memory-only request IDs, browser-only locks, or holding the database transaction during extraction. Persisted state works across Store connections and lets cancellation/edits proceed during a slow call. A single additive table preserves existing records/receipts without rewriting the reviewed store. No queue, worker framework, new dependency or provider integration is introduced.

Evidence: deterministic request-ordering tests, real temporary SQLite databases, receipt preservation through schema upgrade, a save/cancel race paused inside a real transaction, and an offline clarification/correction/save walkthrough. Provider calls, speech capture, browser usability and uncertain-save status/retry behavior are not established by these tests.
