---
name: security-check
description: use when the user explicitly invokes $security-check for a bounded defensive review of BolParchi trust boundaries, secrets or data handling. Do not deploy, exploit external systems or perform a paid scan.
---

# Security Check

User-invoked only; implicit invocation is disabled. Apply AGENTS.md and the preserved Skill Checklist.

## Process

1. **SCOPE** — Run baseline tests and identify the requested files/boundaries. If red, report and inspect read-only. Read architecture and spec; establish which components exist.
2. **INSPECT** — Trace untrusted transcripts/model output, field validation, save authority and credential configuration. Check logs/errors, committed file names and local diffs without printing secret values. Check actual auth/upload/session boundaries only if implemented.
3. **VERIFY** — Use local fictional cases for invalid input, stale approval, duplicate writes or data exposure. Do not use real customer data, external exploitation or a new scanner dependency without authorization.
4. **REPORT** — Give finding, affected boundary, realistic impact and reproduction/evidence. Label missing components and unverified deployment concerns. Remediation is a separate authorized task using red/green tests; a clean review is not a security certification.

## Context pointers

- [agent_docs/architecture.md](../../agent_docs/architecture.md)
- [agent_docs/testing.md](../../agent_docs/testing.md)
- [docs/spec.md](../../docs/spec.md)

## Done checklist

- [ ] Review scope, threat boundaries and limitations are explicit.
- [ ] Secrets/private data were not disclosed or committed.
- [ ] Findings have evidence; absent features are not treated as secured.
- [ ] No unrequested remediation, external scan or deployment occurred.
