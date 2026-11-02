# BolParchi core — reviewed version

A local Python core for an appliance-repair technician's end-of-visit update.
The model proposes fields; Python validates them, tracks the exact confirmation,
and saves the record once. No API key or runtime dependency is needed.

## Run the fictional text demo

From this directory, with Python 3.10 or later:

```sh
python3 -m bolparchi
```

The demo applies a correction in code, reads back fictional job 104, and asks you
to type `yes`. It saves to an in-memory database and demonstrates an idempotent
retry. Records disappear when the demo exits. This is not a voice demonstration.

## Run tests

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Verified on Python 3.14.7 with pytest 9.1.1: **60 tests pass**. The untouched
supplied package separately passed its original 36 tests. The reviewed package
retains those 36 tests and adds 24 regression cases.

## Validation rules

- The proposal must be an object. Text fields accept strings or null, not lists,
  objects, numbers, or booleans. An integer job ID is also accepted.
- `job_id`, `diagnosis`, and `status` are required. Status is `completed` or `pending`.
- A requested part requires an integer quantity from 1 to 20. A quantity without
  a part is invalid. Selected romanized Hindi numbers are normalized in code.
- Pending jobs require follow-up text. Completed jobs do not require a part or
  follow-up; either may still be supplied. This is a prototype business rule.
- Python computes missing and invalid fields. Model-supplied completeness flags
  are ignored. Invalid proposal types raise ValueError from validation; the Store
  returns `invalid_input` without creating a draft.
- Job existence is checked before confirmation and again before saving.

## Confirmation and persistence

- A draft has an ID, revision, and normalized content hash. Every edit increments
  the revision and clears confirmation. Call `confirm` with the revision and hash
  actually shown or read to the user; do not fetch newer values to confirm an old reply.
- UI edits should pass `expected_revision` to `update_draft` so late requests cannot
  overwrite a newer correction. It is optional for compatibility with the original core.
- Create a submission ID once per logical save operation and preserve it across
  every retry. A duplicate click must not generate a new ID for the same operation.
- Saving updates the job, creates any part request and follow-up task, and marks
  the draft saved in one SQLite transaction. UNIQUE constraints enforce submission
  and draft uniqueness. An identical update in a separate draft remains possible.
- Both separate connections and shared Store calls are tested for concurrent retries.
  Use Store methods for application access; direct writes through `store.conn`
  bypass the locking and business rules. Call `close()` when finished.
- A confirmed rollback is reported as a rollback. An unexpected or uncertain failure
  does not claim that nothing was saved. Retry a save using its original submission ID.
- New databases enforce a non-null, nonblank submission ID in the schema. Existing
  databases also receive method-level checks, but this package does not migrate
  older table definitions automatically.

## Still to build and test

Microphone capture, Prisma transcription, extraction model and prompt, conversational
turn handling, Timbre synthesis, and a browser interface. There is no speech intent
classifier: an arbitrary transcript containing `haan` must not automatically save.

A future caller must tie each confirmation to the read-back turn, handle rejection
and corrections, and request a new confirmation after any edit. Follow-up values
are currently free text, not normalized appointment dates. Parts are text labels,
not validated inventory SKUs. No authentication or multi-user authorization exists.
Use this as a local prototype core, not an exposed production service.

The correction test changes the structured quantity to `ek` directly. It does not
prove recognition or extraction of spoken self-corrections. The concurrency test
uses a local SQLite database; it is not a distributed-system reliability claim.
Use fictional job data and disclose the reasoning model when speech is connected.

## Current engineering workflow

See [AGENTS.md](../AGENTS.md) for current commands and [status](../agent_docs/status.md)
for requirements that remain unbuilt. This core guide is not the full product spec.
