# 007 — Connect the local browser to existing workflow authority

Date: 31 October 2026. Status: implemented within the approved FastAPI/plain-JavaScript direction; Ankit explicitly approved FastAPI 0.162.0, Uvicorn 0.54.0, HTTPX 0.28.1 and their required dependencies. This decision grants no deployment or provider budget.

## Context

The tested Store/Workflow/SaveRecovery needed a browser entry point. A standalone visualization could not establish that visible confirmation, network interruptions and persisted receipts behaved correctly together.

## Decision

Use a small FastAPI factory with injected Store/extractor/recovery, plain static assets, and a loopback-only runner. API handlers delegate all mutations to existing owners. Bound JSON before parsing, reject unrecognized fields/types, check Host and same-origin/custom-header writes, redact validation bodies, and serve only named UI assets under a restrictive CSP. There is no public authentication/access model; the runner is local only.

Before a Confirm/save request, retain its exact draft/review/submission tuple in `sessionStorage`. Refresh resumes only that pending save reference. This is deliberately narrower than optional cross-session draft resume. No typed transcript, key or raw audio is placed in browser storage. Failure to write the reference blocks saving. Clearing browser storage/closing the tab loses the client reference; durable server receipts remain.

Check status never redelivers. A request possibly lost before reservation may be explicitly resent with the same tuple, up to three client sends retained across refresh; Store separately enforces the shared three-delivery budget. Known rejection/fenced rollback unlocks, a matching receipt establishes success, and absence/transport failure stays uncertain. Do not create a new submission ID to escape an unresolved save.

The client blocks confirmation while there is unsubmitted text, allows cancellation during extraction, and uses a request sequence to ignore late UI responses. A browser wait timeout does not imply server cancellation or rollback. Provider guards remain the authority even if browser state is bypassed.

The runner requires explicit fixture or live mode. Fixture mode has visible labels and exact example messages, with real SQLite persistence. Live mode has an explicit per-process cap and stops after an error; restarting is not a new project allowance. No successful live Gemini extraction is claimed.

## Alternatives and consequences

- A new frontend framework or database layer would duplicate existing capabilities; keep the approved lean stack.
- Serving the entire repository would expose private configuration; serve named assets instead.
- Optimistic Saved or a new ID on retry could hide a late commit or duplicate work; retain uncertainty and identity.
- General local draft caching would reintroduce a cut feature; retain only pending save recovery in this slice.

HTTP tests use real SQLite. Browser tests separate intercepted HTTP scenarios from real local HTTP/store requests; both use fixture extraction. Capture, playback, live model quality, a broader record-history view and public hosting remain outside this checkpoint.
