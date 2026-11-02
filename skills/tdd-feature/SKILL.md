---
name: tdd-feature
description: use when the user explicitly invokes $tdd-feature for one authorized BolParchi behavior change with acceptance criteria. Do not use to start an unapproved backlog.
---

# Tdd Feature

User-invoked only; implicit invocation is disabled. Apply AGENTS.md and the preserved Skill Checklist.

## Process

1. **SCOPE** — Run the baseline suite; stop edits/report if red. Read the spec and selected acceptance case. Ask about gaps and new dependencies before implementation.
2. **RED** — Add a focused test with an independent expected outcome. Run it before implementation and record the intended failing assertion. A broken import is not red evidence.
3. **GREEN** — Implement the smallest change that satisfies that case while preserving architecture and authority boundaries. Validate inputs and cover affected error/loading/empty states.
4. **REFACTOR** — Simplify only after the test passes; keep behavior unchanged. Complete one acceptance case before starting another.
5. **VERIFY / REPORT** — Run pytest and both Ruff checks from AGENTS. Exercise the relevant real boundary/browser path. Record ADRs/status and report untested behavior, blocked checks and remaining uncertainty. If the same cause defeats two attempts, propose a targeted workflow change.

## Context pointers

- [docs/spec.md](../../docs/spec.md)
- [agent_docs/testing.md](../../agent_docs/testing.md)
- [agent_docs/architecture.md](../../agent_docs/architecture.md)

## Done checklist

- [ ] Relevant test failed before implementation and then passed.
- [ ] Final tests/lint/format checks and their actual results are recorded.
- [ ] Recovery and authority boundaries remain intact; no new dependency without approval.
- [ ] Spec/status/ADRs reflect the change; no unsupported done claim.
