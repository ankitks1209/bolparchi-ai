---
name: code-review
description: use when the user explicitly invokes $code-review to review a scoped BolParchi diff or implementation against its spec. Report findings without editing unless separately authorized.
---

# Code Review

User-invoked only; implicit invocation is disabled. Apply AGENTS.md and the preserved Skill Checklist.

## Process

1. **SCOPE** — Identify the diff and accepted behavior. Run baseline tests; if red report and limit work to read-only diagnosis.
2. **INSPECT** — Trace changed inputs, state transitions and writes against the spec. Check tests exercise independent outcomes rather than mirror implementation. Consult relevant architecture/design references.
3. **VERIFY** — Reproduce suspected defects using minimal fictional cases and real local boundaries where possible. Check credentials/log exposure and error handling when relevant. Never perform live provider calls just because keys exist.
4. **REPORT** — List findings by impact with file/function, trigger, expected versus observed behavior and evidence. Separate confirmed defects from questions. Report checked commands and missing coverage; do not silently fix findings or claim absence of bugs.

## Context pointers

- [docs/spec.md](../../docs/spec.md)
- [agent_docs/testing.md](../../agent_docs/testing.md)
- [agent_docs/architecture.md](../../agent_docs/architecture.md)

## Done checklist

- [ ] Review scope and actual verification are explicit.
- [ ] Every finding has evidence or is labelled unverified/question.
- [ ] No repository mutation or new features from a review-only request.
