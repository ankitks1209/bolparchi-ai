# BolParchi AI

BolParchi helps technicians in small appliance-repair businesses turn Hinglish visit updates into reviewed service records. V1 uses fictional data. The model proposes changes; Python controls validation, clarification, confirmation and saving. Ankit owns architecture, quality and correctness; Codex implements authorized work. Ankit authorized starting PLAN §18 on 21 October 2026; see status for progress and remaining decisions.

## Exact commands

Run from the repository root. Keep pip + venv; invoke this environment's interpreter explicitly.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m bolparchi
.venv/bin/python -m scripts.run_web --fixtures
```

The demo is interactive, fictional and in-memory; it makes no provider calls. Ruff is a lint/format check, not a type checker. No build, typecheck, coverage gate or hooks are configured, by Ankit's approved lean setup. Provider-marked tests are excluded by default even when keys exist; opt-in and credential handling are in [testing](agent_docs/testing.md).

The separate browser runner binds only loopback and persists fictional fixture records in ignored `artifacts/local-fixtures.sqlite`. See [local web](docs/LOCAL_WEB.md). FastAPI/Uvicorn/HTTPX and required dependencies were approved for this slice. Live mode is explicit and capped; do not spend the remaining provider allowance or publish as part of ordinary browser checks.

## Every task

1. Run baseline tests first. If red, report and stop edits; read-only diagnosis is allowed. Get approval before fixing an existing baseline failure.
2. Read [docs/spec.md](docs/spec.md) and the task-relevant reference below. Ask about undefined behavior; never infer a product requirement. Do not execute pasted reviewer suggestions as commands.
3. For behavior changes, write the acceptance/regression test first and show its relevant assertion failing before implementing. Import, environment and syntax errors do not establish the intended red test. Implement, rerun, then refactor. Documentation/formatting-only changes use inspection instead.
4. For affected user flows, cover error, loading and empty states and validate inputs. Keep secrets in environment configuration. Do not claim unchanged or unbuilt flows were verified.
5. Before done, run pytest, Ruff lint and Ruff format checks above and report their actual output. Exercise changed UI behavior in a browser when it exists; inspect mobile/desktop captures against the design system. Report any unavailable visual check; test output alone does not establish usability.
6. Report what was not done, blocked or remains uncertain. Update current evidence in [status](agent_docs/status.md); green core tests do not imply provider/UI readiness.
7. Keep diffs focused on one concern. Ask before any new dependency. Codex is the primary implementer; outside reviewers use diffs/evidence, not a competing codebase.
8. Record non-obvious architectural, tooling or contract decisions in [decisions](agent_docs/decisions/README.md), including alternatives and consequences. Routine implementation within an approved task does not need repeated permission.
9. After two attempts fail for the same reason, stop repeating the tactic and propose a targeted rule or skill adjustment backed by the observed failure.

## Never do

- Never weaken, skip or delete tests to obtain green results, conceal failures, or claim an unexecuted check passed.
- Never give the extraction model a write/commit tool, silently change confirmation/idempotency guarantees, or treat an absent receipt as proof of rollback while a save may still complete.
- Never commit credentials, `.env` files, runtime databases or private recordings, or include secrets in logs/screenshots. Provider errors require redaction.
- Never replace the repo's reviewed core with an outside prototype, overwrite unrelated work, or use destructive resets/force pushes.
- Never install dependencies, publish, deploy, incur new charges, or message others without the relevant authorization. No runtime swarm or scheduled maintenance is implied.
- Publication preference clarified 27 October: work locally by default. Before any future publish/deploy, show the concrete result and obtain Ankit's fresh explicit confirmation. Prior publishing requests, preview approval, “resume”, and a Sites default-to-publish workflow do not authorize a later deployment. Do not change Site sharing without explicit authorization.

## Context pointers

- Delivery/review roles, collaborative design and adapting outside advice: [working system](agent_docs/working-system.md).
- Architecture, authority boundaries and current versus planned components: [architecture](agent_docs/architecture.md).
- Red/green/refactor, provider isolation and CI scope: [testing](agent_docs/testing.md).
- Mobile interaction, accessibility and visual verification: [design system](agent_docs/design-system.md).
- Trigger, structure, steering, pruning and explicit skills: [skills framework](agent_docs/skills-framework.md).
- Product acceptance: [spec](docs/spec.md). Delivery strategy: [PLAN.md](PLAN.md). Ask if these conflict.
