---
name: ui-polish
description: use when the user explicitly invokes $ui-polish to improve an existing BolParchi interface within the agreed design constraints. Do not create new screens or flows from an aesthetic request.
---

# Ui Polish

User-invoked only; implicit invocation is disabled. Apply AGENTS.md and the preserved Skill Checklist.

## Process

1. **SCOPE** — Run baseline tests; stop edits if red. Read the requested UI change, spec and design-system reference. If the UI does not exist or a product decision is missing, report/ask instead of inventing it.
2. **INSPECT** — Capture the current affected states at narrow mobile and desktop sizes. Critique hierarchy, text legibility, action clarity and task-specific identity against the design system. Identify a concrete usability/accessibility issue. If rendering is unavailable, report the limit; do not call an unseen design verified.
3. **CHANGE** — Make a focused visual adjustment using existing tokens/components. For an unresolved material taste choice, show two or three options and a reasoned recommendation; record Ankit's selection in the design system. Apply settled choices without repeated approval. Ask before new dependencies. A behavioral change requires the tdd-feature red/green process; cosmetic changes use inspection. Never optimistically announce a save before a receipt.
4. **VERIFY** — Exercise controls with keyboard and pointer, visible focus, text equivalents, wrapping and affected empty/loading/error states. Review browser console/network errors. Screenshots alone do not prove a working interaction.
5. **PRUNE / REPORT** — Remove placeholder/decorative elements that obstruct the task only within scope. Run final checks and report before/after evidence, untested states and any unresolved visual choice.

## Context pointers

- [agent_docs/design-system.md](../../agent_docs/design-system.md)
- [agent_docs/working-system.md](../../agent_docs/working-system.md) — collaborative checkpoints and review roles
- [docs/spec.md](../../docs/spec.md)
- [agent_docs/testing.md](../../agent_docs/testing.md)

## Done checklist

- [ ] Change respects the approved task and visual constraints.
- [ ] Actual browser interaction and relevant failure state checked or explicitly blocked.
- [ ] Mobile/desktop visual evidence reviewed; taste decisions and unverified observations distinguished.
- [ ] No hidden behavior change without red/green evidence; final checks reported.
