# ADR-002: Preserve the checklist with six focused skills

Date: 20 October 2026. Status: accepted requested structure; discovery mapping is an implementation detail.

Context: PLAN.md already captures trigger, structure, steering and pruning. Ankit requests six concise skills in `skills/` and Codex is the sole coding client. The earlier staged single-skill patch is not installed.

Decision: canonical skill files stay in `skills/<name>/SKILL.md`; `.agents/skills/<name>` uses a relative symlink to each folder for Codex discovery. Every skill is explicitly invoked and has a numbered procedure, done-checklist and direct references. CLAUDE.md contains only `@AGENTS.md` for compatibility, not a second instruction source.

Alternatives: duplicate skill contents in both folders; move all skills away from the requested layout; keep the one broad proposed skill. Symlinks avoid drift while respecting the requested structure. Preserve the original framework's behavior, not a redundant copy of its text in each skill.

Consequences: Git must preserve symlinks; clients that do not resolve them should be given the canonical SKILL.md path explicitly. Do not apply the earlier BolParchi-engineering.patch over this setup. No runtime skill loader or agent swarm is added.
