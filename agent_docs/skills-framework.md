# Preserved Skill Checklist

This implements the framework already recorded in PLAN.md; it does not replace it with a new agent architecture.

| Dimension | Implementation |
| --- | --- |
| Trigger | Six user-invoked development skills. Each has `allow_implicit_invocation: false`; invoking one authorizes only the stated task. Runtime push-to-talk is unrelated. |
| Structure | Canonical files in `skills/<name>/SKILL.md`, numbered process, done-checklist and direct context pointers to agent_docs. |
| Steering | SCOPE, INSPECT, RED, GREEN, VERIFY, PRUNE and REPORT name observable work, selected per skill. They are not requests for private reasoning traces. |
| Pruning | Keep a rule only for a requirement, observed failure or otherwise missing context. Do not duplicate product contracts or copy generic advice. |

## Discovery and use

Codex discovers project skills under `.agents/skills`. Those entries are relative symlinks to the canonical `skills/` folders, so edits have one source of truth. Do not copy SKILL.md to both places. The supported client docs describe repository discovery and symlink support. Reopen the project if new skills are not visible.

| Explicit invocation | Use |
| --- | --- |
| `$write-spec` | Specify an agreed change and surface unresolved decisions |
| `$tdd-feature` | Implement one authorized behavior using observed red/green evidence |
| `$code-review` | Review a scoped diff and report findings without silently fixing it |
| `$ui-polish` | Improve an existing interface against design and accessibility constraints |
| `$debug` | Reproduce and isolate a defect; fix only when authorized |
| `$security-check` | Review local trust boundaries, secrets and failure paths without exploitation |

The workflow composes sequentially: write-spec when needed, then tdd-feature/debug, then review; UI and security skills apply only to relevant boundaries. Do not invoke all six for every change or automatically spawn agents. The earlier single-skill patch was never applied to this repository; do not apply it over this setup.

See [working system](working-system.md) for ownership, review evidence and initial collaborative design. Keep the six procedures focused: ui-polish improves existing screens; an initial design discussion does not require creating a seventh skill or launching a reviewer agent. A fresh review pass is distinct from the implementing pass, but claim independent review only when a different reviewer actually performed it.

## Evidence-driven maintenance

After two failed attempts with the same cause, propose a specific rule/skill change and explain the failure. Add an enforceable invariant to code/tests where possible; use instructions for process. Remove redundant guidance only after checking behavior on representative tasks. New model releases do not justify deleting database or confirmation protections.

Do not make large rewrites, recurring routines or runtime multi-agent orchestration part of skill maintenance. Keep acceptance evidence and actual implementation status visible across sessions.
