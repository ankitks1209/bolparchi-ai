# BolParchi AI — Service Update Agent

**Bolo. Dekho. Confirm karo.** A voice-assisted prototype that turns a Hinglish visit update into a reviewed service record. Prototype with fictional data — not a production service.

> Read the one-page pitch: [SOLUTION_PITCH.md](SOLUTION_PITCH.md).

## What it does

A repair technician selects a known fictional job, speaks or types the update, reviews the sheet, hears it read back, and presses Confirm and save. That button is the only write path. The job stays fixed for the draft, the app asks one relevant question when details are missing, and corrections update the draft and cancel prior approval. Recordings are capped at 30 seconds, held in memory, and an uncertain save stays locked until its outcome is known.

## How it works

Gnani Prisma transcribes the recording (REST /stt/v3, default Prisma v2.5, Hindi input). Gemini 3.5 Flash-Lite (REST v1beta, LOW thinking, prompt bolparchi-field-decisions-v2, wire schema v1) proposes a structured patch with one decision per field. Python validates it, keeps the selected job fixed, and asks the follow-up. Gnani Timbre v2.5 (Nalini voice, 48 kHz mono PCM WAV) reads the reviewed record aloud. The model never saves; only Confirm creates the SQLite record and receipt.

## Quick start

Fixtures mode needs no keys and makes no provider calls. The app serves at `http://127.0.0.1:8766`.

macOS / Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m scripts.run_web --fixtures
```

Windows (PowerShell):

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m scripts.run_web --fixtures
```

Open `http://127.0.0.1:8766`, select job 104, and use the fixture messages in [LOCAL_WEB](docs/LOCAL_WEB.md). Records persist in ignored `artifacts/local-fixtures.sqlite`.

Terminal demo (offline, no keys):

```sh
.venv/bin/python -m bolparchi
.venv/bin/python -m scripts.demo_typed_workflow
```

Lint and format:

```sh
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

Live mode (optional, real calls, fictional data only): copy `.env.example` to `.env` and set `GEMINI_API_KEY` and `GNANI_API_KEY` there — never commit `.env`. Then, for example:

```sh
.venv/bin/python -m scripts.run_web --live --max-requests 6 --max-speech-requests 2 --env-file .env --db artifacts/local-live.sqlite
```

Caps bound that process only (1–6 each); every attempt counts before networking, failures stop later calls except the bounded HTTP 503 path, and restarting does not grant more allowance. It makes real Gnani and Gemini calls, and spoken updates are sent to Gemini, so use fictional data only. Never run `--live` without an explicit allowance, and never print `.env` values.

## Evidence and limits

Only facts from [EVALUATION](docs/EVALUATION.md) and [SOLUTION_PITCH](SOLUTION_PITCH.md): 424 offline tests pass. Frozen evaluation: six cases attempted once each, five exact patch matches, one HTTP 503, zero semantic mismatches among returned patches; a separate unchanged recheck of the unavailable uncertainty case passed. Scoped live runs passed: one typed browser task with three extractions and receipt `56956688…` for quantity 1, one retained recording through STT, extraction, read-back and saving, and one fresh microphone task with receipt `5bb647c0…` for quantity 1. Limits: fictional data, one user and one device, no technician study, intermittent provider 503s, no time-savings claim.

## Project layout

- [docs/spec.md](docs/spec.md): product behavior, edge cases and acceptance criteria.
- [PLAN.md](PLAN.md): delivery strategy, scope history and schedule.
- [AGENTS.md](AGENTS.md): exact commands and universal development rules.
- [agent_docs/working-system.md](agent_docs/working-system.md): engineering, review and collaborative design process.
- [agent_docs/design-system.md](agent_docs/design-system.md): selected visual direction and pending preview decisions.
- [agent_docs/skills-framework.md](agent_docs/skills-framework.md): six explicit skills and context pointers.
- [agent_docs/status.md](agent_docs/status.md): current implementation and remaining gaps.
- `bolparchi/`: field contract, validation, store, typed workflow and read-back code.
- `tests/`: offline checks (provider tests excluded by default).
- `probes/`: frozen and development evaluation cases.
- `scripts/`: local runners, checks, and bounded live probes.
- `site/`: presentation-only landing preview (serve that directory only; not deployed).
- `docs/`: spec, evaluation, submission, walkthrough, and demo scripts.

## Docs

- [SOLUTION_PITCH.md](SOLUTION_PITCH.md): one-page pitch.
- [docs/spec.md](docs/spec.md): product behavior, edge cases and acceptance criteria.
- [docs/EVALUATION.md](docs/EVALUATION.md): evidence, failures, and remaining gates.
- [docs/SUBMISSION.md](docs/SUBMISSION.md): submission requirements and demo plan.
- [docs/LOCAL_WEB.md](docs/LOCAL_WEB.md): fixture walkthrough and recovery limits.
- [docs/DEMO_SCRIPT_FINAL.md](docs/DEMO_SCRIPT_FINAL.md): timed 2:30-2:45 demo script.
- [docs/DEMO_SCRIPT_3MIN.md](docs/DEMO_SCRIPT_3MIN.md): earlier 2.5-minute script.
- [PLAN.md](PLAN.md): delivery strategy, scope history and schedule.
- [AGENTS.md](AGENTS.md): exact commands and universal development rules.
- [agent_docs/status.md](agent_docs/status.md): current implementation and remaining gaps.
- [agent_docs/testing.md](agent_docs/testing.md): offline checks and provider isolation.

## Who built what

Ankit Singh directed the work and ran the acceptance tasks. Codex and Cline (AI coding tools) assisted with code, tests and docs.

Use fictional data only. Do not commit `.env`, credentials, customer recordings, databases, or generated media. A public repository does not mean the app is deployed or production-ready.
