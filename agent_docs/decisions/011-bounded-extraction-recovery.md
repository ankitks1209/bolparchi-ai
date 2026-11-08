# 011 — Bound automatic recovery from Gemini 503

Date: 6 November 2026. Status: implemented after Ankit approved issue #1 in the ordered fix list. Supersedes ADR-010's manual-only extraction retry policy; other transport/speech policies remain unchanged.

## Decision

The local live runner's `CappedExtractor` makes at most three attempts per extraction action, retrying **only HTTP 503**, with delays of 1 and 2 seconds. Every attempt consumes the same process allowance before networking. No fixture or model fallback is added. Authentication, quota and invalid-output errors are never retried automatically; the existing wrapper stop policy remains. Other transient failures can still be retried explicitly within the remaining allowance.

The caller's 30-second extraction deadline includes waiting for the shared lock, provider results and backoff. It is separate from speech transcription and the browser's 45-second HTTP wait. A daemon worker owns only the external extractor call, not a Store or workflow callback. If the deadline expires, the caller returns a safe timeout and discards any later output. Python cannot forcibly stop that underlying transport thread; while it remains active, new extraction actions fail without spending another attempt. At most one transport is in flight per wrapper. This preserves bounded application waiting without claiming upstream cancellation.

Workflow supplies an optional `extract_with_guard` callback that checks draft state, revision, turn ID and processing state before every attempt. Cancelled or superseded turns do not start further retries after backoff. Existing completion guards remain authoritative for a cancellation racing with an already-started request. Simple injected extractors continue to use the unchanged callable interface.

After all permitted attempts fail, the existing UI preserves the submitted message and draft, disables saving and offers manual Retry extraction. Successful recovery produces only a proposal; confirmation/save authority is unchanged.

## Alternatives

- Unlimited retries or resetting the cap would conceal failures and overspend requests.
- Changing the shared HTTP helper would also retry Gnani and standalone diagnostic calls, broadening scope unnecessarily.
- A socket timeout alone is not a total deadline; repeated socket reads can outlive it.
- Waiting for a timed-out worker during cleanup would defeat the deadline. Starting another transport before it ends would permit overlapping requests and unbounded worker accumulation.
- A new SDK or process-based cancellation is unnecessary for this local runner. The one-worker containment and existing read/socket limits are explicit limitations.

## Evidence

The recovery test first failed because one 503 ended the action; it now verifies three identical inputs, delays 1/2 and exact allowance consumption. A separate cancellation test then failed because cancelled work made another attempt; the workflow guard fixes it. Added checks cover HTTP/manual recovery, cap exhaustion, nonretryable failures, overall deadline, late-result rejection, overlap prevention and same-revision turn replacement.

The offline browser server in `scripts/demo_retry_recovery.py` injects three 503s, then fixture extraction. Browser interaction observed loading, preserved input/error, successful manual retry, clarification, quantity correction and explicit receipt-backed save. Desktop/390px captures were inspected, 390/320px overflow checks passed, and browser warning/error logs were empty. This proves controlled recovery behavior, not Gemini service uptime or extraction accuracy.
