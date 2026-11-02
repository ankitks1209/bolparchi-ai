---
name: write-spec
description: use when the user explicitly invokes $write-spec to specify or clarify a BolParchi change before implementation. Do not infer approval to build features.
---

# Write Spec

User-invoked only; implicit invocation is disabled. Apply AGENTS.md and the preserved Skill Checklist.

## Process

1. **SCOPE** — Run baseline tests and follow AGENTS if red. Read the requested change, docs/spec.md and the relevant accepted ADRs. Identify the user, outcome and affected acceptance criteria.
2. **INSPECT** — Check current code/status so the spec does not present planned behavior as implemented. Separate user requirements from reviewer suggestions.
3. **DECIDE** — Ask about undefined behavior. Mark unanswered items OPEN QUESTION; do not silently choose defaults or expand scope.
4. **WRITE** — Update only agreed users, flows, exclusions, edge cases and observable acceptance criteria. Record a non-obvious accepted choice as an ADR. Keep one authoritative product spec.
5. **VERIFY / PRUNE** — Check links and contradictions against AGENTS, PLAN and relevant skills. Remove duplicated rules. Report unresolved questions and explicitly state that no feature was implemented.

## Context pointers

- [docs/spec.md](../../docs/spec.md)
- [agent_docs/decisions/README.md](../../agent_docs/decisions/README.md)

## Done checklist

- [ ] Every behavior comes from an accepted requirement or is marked OPEN QUESTION.
- [ ] Acceptance criteria describe observable effects and relevant failure states.
- [ ] Conflicts and unanswered questions are reported; product code unchanged.
