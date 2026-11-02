# Repository setup verification

Date: 20 October 2026. Runtime tested: Python 3.14.7. Project dependencies: pytest 9.1.1, Ruff 0.17.1. Scope: approved engineering setup only; no product feature implementation.

## Every AGENTS command

Executed from the prepared repository root:

| Command | Actual result |
| --- | --- |
| `python3 -m venv .venv` | Passed; created a fresh isolated environment |
| `.venv/bin/python -m pip install -r requirements-dev.txt` | Passed; installed both pinned tools and pytest's dependencies |
| `.venv/bin/python -m pytest -q` | 60 passed in 0.25s |
| `.venv/bin/python -m ruff check .` | All checks passed! |
| `.venv/bin/python -m ruff format --check .` | 31 files already formatted |
| `.venv/bin/python -m bolparchi` | Passed with synthetic `yes` stdin; returned saved, then replayed for the same submission ID |

No configured command remains failing. Typecheck/build/coverage/hooks were deliberately removed from requirements by Ankit's approval; they were not executed and are not claimed as checks.

## Initial failures and resolutions

The first read-only baseline invocation was run from the wrong directory and had three import/collection errors. Repeating it from the actual repo root passed all 60 tests before editing. No code fix was made for this invocation error.

New Ruff checks initially reported nine intended package re-exports as unused plus formatting differences. Explicit same-name export aliases and automatic formatting resolved them. The existing eight Python application/test files have identical ASTs after normalization of those redundant aliases. No assertions, state transitions or product behavior were changed. This used the approved formatting-only exception rather than inventing a failing product test.

## Additional setup checks

- All six skills pass the skill-creator format validator; each has `description: use when ...`, numbered process and done-checklist.
- Every skill's implicit invocation is disabled, and each `.agents/skills` symlink resolves to its canonical `skills/` folder.
- AGENTS is below 150 lines; CLAUDE.md contains exactly `@AGENTS.md` and a newline.
- Local documentation links resolve. Git diff whitespace checks pass.
- Provider-marker selection was checked with temporary offline sentinel tests: default run had one offline pass and one provider deselection; explicit `-m provider` selected the intentionally failing provider sentinel. No network calls occurred. Credential-specific skipping belongs to the future provider fixtures; no real-provider test is implemented now.
- Workflow YAML structure and contents-read permissions checked locally. Commands match the documented checks and no provider secrets are referenced.
- A separate read-only trial of `$code-review` found no confirmed setup defects or contradictions; it independently ran 60 tests and Ruff checks and confirmed no product behavior changes.

## Contradictions and their resolution

| Earlier conflict | Resolution |
| --- | --- |
| Initial request mandated hooks, typecheck and coverage | Explicit lean-setup approval supersedes those requirements; ADR-001 records the choice |
| PLAN proposed an optional single engineering routine; new request requires six skills | The original Skill Checklist is preserved and mapped to six concise skills; the earlier unapplied patch is superseded |
| Requested `skills/` location versus Codex `.agents/skills` discovery | Canonical files in skills, relative discovery links; no duplicated skill bodies |
| Passing core tests could be confused with full product completion | Spec defines target behavior; status lists unimplemented patch, cancellation, provider and UI requirements |
| Model catalogue claim versus actual account behavior | Exact ID/settings/access remain OPEN QUESTIONS requiring official-doc and live-probe evidence |
| Current prototype behavior differs from the target spec | Explicitly recorded implementation gaps, not silently resolved or treated as complete |

No unresolved contradiction was found among AGENTS, the spec and the six skills. Known implementation gaps remain and must be addressed in authorized product tasks.

## Remaining inputs or unverified work

- Apply this update to the real Projects repository and open that folder in Codex; actual client discovery has not been exercised here.
- A GitHub remote/publication and branch/ruleset decision are needed before hosted CI and merge enforcement can be verified. No remote push or protection configuration was performed.
- Product implementation still needs an explicit task start. Provider access and non-secret environment-variable names, model/settings, recording limits, extraction ambiguity contract, and optional hosting/retention decisions remain in spec OPEN QUESTIONS.
- Exact visual tokens await the UI task; current design constraints are settled.
- Only Python 3.14.7 was run locally. The Python 3.10+ target is not a claim that every supported version was tested.

## Apply state

Prepared in a writable staging repository because this chat cannot write inside `/Users/golukakarot/Developer/Projects/BolParchi AI`. The generated `BolParchi-repo-setup.patch` is the complete update from the actual repo snapshot. Do not apply the earlier `BolParchi-engineering.patch`; it is superseded. The user's repository has not been modified by preparing this patch.
