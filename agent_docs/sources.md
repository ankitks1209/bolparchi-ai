# Engineering sources

Checked on 20 October 2026. These inform the workflow; the project's accepted scope remains authoritative.

- [OpenAI: Harness engineering, Ryan Lopopolo](https://openai.com/index/harness-engineering/): short navigable instructions and mechanically checked boundaries.
- [Anthropic: Effective harnesses, Justin Young](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents): incremental work, durable progress and actual end-to-end verification.
- [Anthropic: Agent Skills, Barry Zhang, Keith Lazuka and Mahesh Murag](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills): progressive disclosure and evaluation-driven skill improvements.
- [GitHub: AGENTS.md lessons, Matt Nigh](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/): actionable commands and boundaries rather than a vague persona.
- [Codex skill documentation](https://developers.openai.com/codex/skills/): repository discovery under `.agents/skills`, symlink support and explicit invocation policy.
- [Ruff configuration](https://docs.astral.sh/ruff/configuration/): pyproject configuration for target Python and lint/format rules.
- [pytest markers](https://docs.pytest.org/en/stable/example/markers.html): registered markers, strict checking and selection with `-m`.
- [actions/setup-python](https://github.com/actions/setup-python) and [actions/checkout](https://github.com/actions/checkout): documented v7 usage and minimal contents-read permissions.

Hooks are deliberately omitted under ADR-001; no guessed hook syntax or hook behavior is claimed. Hosted CI and client skill discovery still require verification in the actual project/client after applying this setup.
