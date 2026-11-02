# ADR-001: Lean engineering checks

Date: 20 October 2026. Status: accepted by Ankit's explicit approval of the lean setup.

Context: the initial request included type checking, a coverage threshold and hooks. The reviewer recommended a smaller setup, and Ankit approved it including Ruff as a new development dependency.

Decision: retain pip/venv and pytest; pin Ruff for lint and formatting. No mypy/typecheck, build step, coverage threshold or pre-commit/Claude/Codex hook. Prepare GitHub Actions for pytest and Ruff without provider secrets. It runs only after publication to GitHub. Keep provider tests explicitly opt-in and credential-gated.

Alternatives: full original gate set; tests alone. The selected setup adds low-cost consistent linting without the larger toolchain. Ruff is the sole new project development dependency. Changes to tooling pins/dependencies require approval; setup uses Python 3.14 in CI, matching the locally tested minor version, while code continues to target Python 3.10+.

Consequences: checks enforce only their configured cases. They do not prove type safety, coverage or absence of bugs. Local checks can be bypassed; merge enforcement requires GitHub branch/ruleset configuration after the remote exists. Do not claim hooks are installed or CI has run remotely.
