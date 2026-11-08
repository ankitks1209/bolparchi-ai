# 010 — Identify the client and allow explicit transient extraction retries

Date: 5 November 2026. Status: implemented within the authorized provider diagnosis and AC-11 recovery work.

Update 6 November: the named User-Agent and redaction decisions remain current. [ADR-011](011-bounded-extraction-recovery.md) supersedes the manual-only extraction policy with bounded automatic retries for HTTP 503 in the live runner. Shared transport, speech and standalone probes still do not retry automatically.

## Evidence and decision

Gnani returned HTTP 403 with a plain-text body through Python's default HTTP client. Ankit verified 4,999 credits and an active matching key. The same endpoint, credential and retained recording succeeded through curl. A controlled Python request with `User-Agent: BolParchi/0.1` then succeeded. Set that truthful application identifier in the shared HTTP transport. This isolates a request-header difference; it does not prove the provider's internal blocking rule. Do not replace keys, relax TLS, follow redirects or introduce a curl runtime dependency.

The browser offered Retry extraction after a transient failure, but the launch wrapper permanently stopped every later call. Let an explicit retry use the same remaining process allowance after HTTP 408/500/502/503/504, timeout or network failure. Decrement the allowance before each attempt, serialize access and never retry automatically. Authentication, quota, malformed-output and other failures still stop the wrapper. Speech and diagnostic/evaluation runners retain their separate stop-on-error behavior.

Operator warnings contain only allowlisted HTTP/provider codes. Unexpected exception messages and raw provider bodies are not logged. The UI continues to preserve the transcript/draft and require review and explicit confirmation.

## Validation and limitations

The request-header assertion failed before the transport fix. The transient-retry test failed when the wrapper rejected the second explicit call; it now verifies no automatic retry, success on the next explicit call and refusal after the shared cap. Error-log tests verify redaction. Live Gnani transcription and browser read-back now succeed. The successful live typed run did not encounter an error; explicit retry after an actual 503 remains demonstrated by offline tests, not that live run.

The server cap is not a daily provider quota, and a restart does not authorize more spending. Provider availability and extraction semantics remain separate release risks. No billing settings or dependencies changed.
