# ADR-008 — Bounded browser audio and exact-review playback

Date: 1 November 2026. Status: accepted implementation within the authorized voice task; Ankit delegated initial recording choices on 31 October.

## Context

The guarded speech workflow and adapters exist, but the browser needs a consistent format, recording lifecycle and read-back boundary. The current Gnani REST reference inspected on 31 October lists a 30-second STT maximum. Existing save authority, fictional-data scope and local-only publication preference continue to apply.

## Decision

Capture mono 16 kHz/16-bit PCM with native AudioWorklet. Enforce 480,000 samples on the audio thread, independently of the UI timer. Encode one canonical 44-byte WAV header; accept at most 960,044 bytes server-side and reject empty/malformed/oversize audio before any provider call. Stop or the duration limit sends the recording for review. Discard, page hiding/leaving and draft cancellation release tracks; a late permission grant is also released. Raw audio stays in memory; transcripts use the existing persisted turn guard.

Read-back accepts revision/hash, never arbitrary client text. SpeechReview obtains server-generated review text, synthesizes outside transactions, and rejects audio if the review changed meanwhile. Client cancellation/epochs and object-URL cleanup suppress obsolete playback. TTS has no confirmation or save authority; failure preserves text review.

Fixture mode explicitly returns a fixed transcript and plays a test tone. Live speech requires a separate combined STT/TTS request allowance. Attempts are counted before calls and share a lock; provider errors stop further requests except the supported empty-speech repeat path. This is a process cap, not a durable credit ledger or permission to make new requests.

## Alternatives

MediaRecorder would produce browser-dependent encoded formats and could require conversion. Streaming adds complexity outside v1. A 60-second limit contradicts the newly inspected provider reference. Temporary audio files are unnecessary for this short local flow. Client-supplied TTS text would weaken the exact-review boundary.

## Consequences

No new dependency or persistence migration is required. Unsupported microphone/AudioWorklet/sample-rate environments offer typing. Chrome synthetic-device checks establish capture and HTTP composition, not microphone acoustics, browser portability, model quality or a complete real AI task. Human speech/read-back checks and successful Gemini extraction remain release gates. See [local walkthrough](../../docs/LOCAL_WEB.md) and [status](../status.md).
