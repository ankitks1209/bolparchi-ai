---
name: debug
description: use when the user explicitly invokes $debug to reproduce and diagnose a BolParchi defect, and to fix it only when that repair is authorized.
---

# Debug

User-invoked only; implicit invocation is disabled. Apply AGENTS.md and the preserved Skill Checklist.

## Process

1. **SCOPE** — Run baseline tests. If red, report first and diagnose read-only; request approval before edits. Determine whether the request authorizes diagnosis only or a repair.
2. **REPRODUCE** — Reduce the failure to fictional inputs and an observable expected/actual difference. Use the spec, current code and real store/provider boundary evidence as appropriate; avoid guessing the cause.
3. **ISOLATE** — Trace the first incorrect boundary. Distinguish provider failure, malformed output, stale state and database outcome. Preserve evidence without leaking keys or private data.
4. **RED / GREEN** — For an authorized repair, create a regression test, demonstrate the intended failure, then fix the smallest cause. Do not weaken assertions or silently alter guarantees.
5. **VERIFY / REPORT** — Rerun the regression and final checks; inspect the recovery path. Record cause, evidence and limitations. After two failed attempts at the same cause, stop repeating and propose a focused rule/skill change.

## Context pointers

- [agent_docs/testing.md](../../agent_docs/testing.md)
- [agent_docs/architecture.md](../../agent_docs/architecture.md)
- [docs/spec.md](../../docs/spec.md)

## Done checklist

- [ ] Reproduction and expected outcome are documented.
- [ ] Authorization and baseline-red boundary respected.
- [ ] If fixed, regression failed first and passes now; full checks reported.
- [ ] Unresolved causes or unavailable integration evidence remain explicit.
