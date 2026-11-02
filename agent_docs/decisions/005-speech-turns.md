# ADR-005: Guard transcription before applying its transcript

Date: 28 October 2026. Status: implementation of the approved speech, stale-result and empty-input requirements (AC-06/AC-10), resumed by Ankit.

Context: the speech adapters return validated data, but a slow STT call could still finish after a newer message or cancellation. Calling typed submit only after transcription would assign that old audio a new turn and incorrectly make it current.

Decision: reserve the existing persisted input turn in `transcribing` state before calling STT. Revoke confirmation and block confirmation/save immediately. STT runs outside SQLite transactions. Completion and failure use the same draft/revision/turn/open-state guard as extraction. A successful transcript moves that same turn to `processing`, then enters the existing extraction path. A stale STT result is rejected before extraction, and extraction completion still has its own guard.

Keep the previous usable transcript while STT is pending or fails; replace it only with a validated nonempty transcript. During `transcribing`/`speech_error`, that text is previous input, not a claimed transcription of the new clip. No raw audio is stored. Speech failure offers a new recording or typing, while extraction failure retries the preserved transcript without another STT call.

An additive `draft_speech` table persists empty-attempt counts. Counts rise only for current empty results; accepted typed text or usable transcription resets them. Nonempty provider failures do not increment them. After two empty results, the view marks typing as preferred. These backend flags implement the accepted fallback requirement; browser focus/rendering remains pending. The additive table preserves old receipts and requires no destructive migration.

Alternatives: an in-memory lock, browser-only request IDs, or opening a fresh typed turn when STT returns. These do not protect cross-connection ordering or can promote stale audio. Holding a transaction across STT would block edits/cancellation. The existing guard is reused instead of adding a separate speech state machine.

Evidence: controlled concurrent tests with two real SQLite connections cover newer typing, newer audio, edits and cancellation before late success/error. Other tests cover approval revocation, empty/invalid speech, preserved text, extraction retry, reopening the empty counter, and preservation of receipts when upgrading an older schema. External responses are fixtures; microphone capture, playback cancellation, live extraction and uncertain-save recovery are separate work.
