# BolParchi AI — Service Update Agent

> Read the one-page pitch: [SOLUTION_PITCH.md](SOLUTION_PITCH.md).

> Demo video: [link to be added].

**Bolo. Dekho. Confirm karo.**

> **Work in progress — local prototype.** Recording, review, corrections and receipt-based saving are implemented. The offline demo uses scripted AI responses; real Gemini extraction and a user-operated microphone-to-receipt task have passed scoped checks. This is not a production service.

A voice-assisted service-update prototype for repair technicians. The planned app
turns a Hinglish update into a reviewed record, asks about missing information,
and saves only after explicit confirmation.

## Current status

The local FastAPI/plain-JavaScript app connects job selection, typed/recorded updates,
clarification, correction, read-back and explicit receipt-based saving to SQLite.
On 5 November a live typed browser task completed three Gemini extractions, real Gnani
read-back playback and a confirmed save with quantity 1. Offline checks pass (424 tests).

The retained human recording now passes real Gnani transcription, Gemini extraction,
clarification, Gnani read-back generation and receipt-backed saving. Ankit also completed a fresh browser microphone task and reported clear recording/playback;
its saved quantity-1 record is verified. Broader extraction/speech accuracy remains unverified.
The frozen evaluation produced five exact matches and one HTTP 503; a separate
unchanged recheck of the unavailable uncertainty case passed. These small samples
do not establish general accuracy or service availability.
The fixture walkthrough uses a fixed transcript, scripted extraction and a test tone;
it makes no provider requests. See [evaluation](docs/EVALUATION.md) and
[current evidence](agent_docs/status.md) for the successes, failures and remaining gates.

## Project files

- [docs/spec.md](docs/spec.md): product behavior, edge cases and acceptance criteria.
- [PLAN.md](PLAN.md): delivery strategy, scope history and schedule.
- [AGENTS.md](AGENTS.md): exact commands and universal development rules.
- [agent_docs/working-system.md](agent_docs/working-system.md): engineering, review and collaborative design process.
- [agent_docs/design-system.md](agent_docs/design-system.md): selected visual direction and pending preview decisions.
- [agent_docs/skills-framework.md](agent_docs/skills-framework.md): six explicit skills and context pointers.
- [agent_docs/status.md](agent_docs/status.md): current implementation and remaining gaps.
- `bolparchi/`: field contract, validation, store, typed workflow and read-back code.
- `tests/`: existing core and regression tests.
- [docs/CORE.md](docs/CORE.md): core setup, implemented behavior and limitations.
- [docs/CORE_REVIEW.md](docs/CORE_REVIEW.md): historical review and fixes.
- [docs/SETUP_VERIFICATION.md](docs/SETUP_VERIFICATION.md): checks from project organization.

## Run locally

Python 3.10 or later; first create the environment using the setup commands below:

```sh
.venv/bin/python -m scripts.run_web --fixtures
```

Open `http://127.0.0.1:8766` for the local typed/voice fixture walkthrough. Records persist in
ignored `artifacts/local-fixtures.sqlite`. See [the walkthrough and recovery limits](docs/LOCAL_WEB.md).
There is no automatic provider call or publication. Python 3.14.7 is the verified runtime.

The earlier terminal walkthrough remains available:

```sh
.venv/bin/python -m scripts.demo_typed_workflow
```

The walkthrough shows three fixture messages, a missing-detail question and a quantity
correction. Type `SAVE` to explicitly confirm the displayed fictional record, or another
response to cancel. Records disappear on exit. No provider keys or network access are needed.
The original direct-structured-input core demo remains available as `.venv/bin/python -m bolparchi`.

## Run the tests

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Engineering checks

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

FastAPI and Uvicorn serve the local browser app; HTTPX supports offline API tests.
These additions were explicitly approved. Type checking, a coverage gate, hooks
and a build step are intentionally omitted. Provider tests are excluded by default;
see [testing](agent_docs/testing.md) for explicit opt-in once they exist.

Six user-invoked skills live in `skills/`, with Codex discovery links under
`.agents/skills/`. Example: `Use $code-review to review this diff; do not edit.`
The existing Skill Checklist is preserved. Do not apply the older single-skill patch.

The GitHub Actions workflow runs offline pytest and both Ruff checks on pushes
and pull requests. The first [hosted run passed](https://github.com/ankitks1209/bolparchi-ai/actions/runs/41478046702)
on 2 November 2026. Branch protection was not configured as part of this setup.
See [setup verification](agent_docs/setup-verification.md) for local evidence.

## Git and GitHub

This folder is the repository root. Keep future application code, tests, planning,
evaluation fixtures, and submission documentation here. Review `git status` and
`git diff --cached` before committing. The ignore rules exclude credentials,
virtual environments, caches, local databases and generated recordings.

Use fictional data only. Add deliberately selected synthetic evaluation audio later;
do not commit real customer recordings or credentials. Source is available in the
public [bolparchi-ai repository](https://github.com/ankitks1209/bolparchi-ai). A public source repository does not
mean the application is deployed or ready for production use.
