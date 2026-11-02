"""Draft -> confirm -> save, with duplicate protection.

Two separate mechanisms, deliberately:
  * draft_id + revision + content_hash identify the EXACT proposal a user confirmed.
    Any edit bumps the revision and clears the confirmation.
  * submission_id is created once per save attempt and reused on retries. The save
    runs in one transaction and a UNIQUE constraint on submission_id (and on
    draft_id) stops a second write even under concurrent retries.
Expected rejections come back as an Outcome; an action that failed is never
reported as saved.
"""

from __future__ import annotations

import functools
import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .validation import (
    FIELDS,
    apply_changes,
    normalize,
    proposal_hash,
    validate,
    validate_extraction,
    validate_message,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY, appliance TEXT, customer_label TEXT,
    status TEXT NOT NULL DEFAULT 'open', diagnosis TEXT, follow_up TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS drafts (
    draft_id TEXT PRIMARY KEY,
    revision INTEGER NOT NULL,
    proposal_json TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    confirmed_revision INTEGER,
    state TEXT NOT NULL DEFAULT 'open'
);
CREATE TABLE IF NOT EXISTS submissions (
    submission_id TEXT PRIMARY KEY NOT NULL CHECK(length(trim(submission_id)) BETWEEN 1 AND 128),
    draft_id TEXT NOT NULL UNIQUE,
    revision INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    saved_at TEXT NOT NULL,
    result_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS parts_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id TEXT NOT NULL UNIQUE REFERENCES submissions(submission_id),
    job_id TEXT NOT NULL, part TEXT NOT NULL, quantity INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id TEXT NOT NULL UNIQUE REFERENCES submissions(submission_id),
    job_id TEXT NOT NULL, description TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS draft_inputs (
    draft_id TEXT PRIMARY KEY REFERENCES drafts(draft_id),
    turn_id TEXT NOT NULL UNIQUE,
    starting_revision INTEGER NOT NULL,
    transcript TEXT NOT NULL,
    input_state TEXT NOT NULL,
    patch_json TEXT,
    changed_fields_json TEXT NOT NULL DEFAULT '[]',
    error_code TEXT
);
CREATE TABLE IF NOT EXISTS draft_speech (
    draft_id TEXT PRIMARY KEY REFERENCES drafts(draft_id),
    empty_attempts INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS save_requests (
    submission_id TEXT PRIMARY KEY,
    draft_id TEXT NOT NULL REFERENCES drafts(draft_id),
    revision INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    error_code TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS one_pending_save_per_draft
ON save_requests(draft_id) WHERE state='pending';
"""

BLOCKING_INPUT_STATES = {
    "transcribing",
    "speech_error",
    "processing",
    "mismatch",
    "clarification",
    "error",
}

# Fictional records only.
DEMO_JOBS = [
    ("104", "Washing machine", "Demo Customer A"),
    ("105", "Refrigerator", "Demo Customer B"),
    ("106", "Air conditioner", "Demo Customer C"),
]


@dataclass
class Outcome:
    ok: bool
    code: str
    message: str
    data: dict = field(default_factory=dict)


class _Stop(Exception):
    def __init__(self, outcome: Outcome):
        self.outcome = outcome


class _RolledBack(Exception):
    """The transaction was still active and was successfully rolled back."""


def _retryable_storage_error(exc):
    code = getattr(exc, "sqlite_errorcode", None)
    return (
        isinstance(exc, sqlite3.OperationalError)
        and type(code) is int
        and (code & 0xFF) in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED}
    )


def _guarded(fn):
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except _Stop as stop:
            return stop.outcome
        except _RolledBack as exc:
            return Outcome(
                False,
                "failed",
                "Transaction rolled back; nothing was recorded.",
                {
                    "transaction_rolled_back": True,
                    "retryable": _retryable_storage_error(exc.__cause__),
                },
            )
        except ValueError as exc:
            return Outcome(False, "invalid_input", str(exc))
        except Exception as exc:
            return Outcome(
                False,
                "failed",
                "Action could not be completed. Verify its state; retry saves with the same submission ID.",
                {"transaction_rolled_back": False, "retryable": _retryable_storage_error(exc)},
            )

    return wrapper


def new_submission_id() -> str:
    """Create ONCE per save attempt; reuse the same value on every retry of that attempt."""
    return uuid.uuid4().hex


class Store:
    def __init__(self, path: str = ":memory:", seed: bool = True):
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(path, timeout=10, isolation_level=None, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        if path != ":memory:":
            self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)
        if seed:
            for job_id, appliance, label in DEMO_JOBS:
                self.conn.execute(
                    "INSERT OR IGNORE INTO jobs (job_id, appliance, customer_label) VALUES (?,?,?)",
                    (job_id, appliance, label),
                )

    # ---------- helpers ----------
    @contextmanager
    def _tx(self):
        # One connection must never run overlapping transactions. Separate Store
        # instances still coordinate via SQLite's write lock and UNIQUE keys.
        with self._lock:
            self.conn.execute("BEGIN IMMEDIATE")
            try:
                yield
                self.conn.execute("COMMIT")
            except BaseException as exc:
                if self.conn.in_transaction:
                    self.conn.execute("ROLLBACK")
                    if isinstance(exc, Exception) and not isinstance(exc, (_Stop, ValueError)):
                        raise _RolledBack() from exc
                raise

    def _draft_row(self, draft_id):
        return self.conn.execute("SELECT * FROM drafts WHERE draft_id=?", (draft_id,)).fetchone()

    @staticmethod
    def _check_revision(revision):
        if type(revision) is not int or revision < 1:
            raise ValueError("An explicit positive integer revision is required.")

    def _open_draft(self, draft_id):
        row = self._draft_row(draft_id)
        if row is None:
            raise _Stop(Outcome(False, "not_found", "No such draft."))
        if row["state"] == "cancelled":
            raise _Stop(Outcome(False, "cancelled", "This draft was cancelled; nothing was saved."))
        if row["state"] == "saved":
            raise _Stop(Outcome(False, "already_saved", "This update was already saved."))
        if row["state"] != "open":
            raise _Stop(Outcome(False, "draft_locked", "This draft is locked; check its status."))
        return row

    def _input_row(self, draft_id):
        return self.conn.execute(
            "SELECT * FROM draft_inputs WHERE draft_id=?", (draft_id,)
        ).fetchone()

    def _require_resolved_input(self, draft_id):
        current = self._input_row(draft_id)
        if current is not None and current["input_state"] in BLOCKING_INPUT_STATES:
            raise _Stop(
                Outcome(False, "pending_input", "Resolve the current message before saving.")
            )

    def _guard_turn(self, draft_id, turn_id, expected_revision, *, state):
        """One atomic applicability guard for completions, errors and held releases."""
        self._check_revision(expected_revision)
        if not isinstance(turn_id, str) or not turn_id:
            raise ValueError("A turn ID is required.")
        row = self._open_draft(draft_id)
        current = self._input_row(draft_id)
        if (
            row["revision"] != expected_revision
            or current is None
            or current["turn_id"] != turn_id
            or current["starting_revision"] != expected_revision
            or current["input_state"] != state
        ):
            raise _Stop(
                Outcome(
                    False, "stale_response", "This result belongs to an older message or draft."
                )
            )
        return row, current

    def _write_proposal(self, draft_id, proposal):
        self.conn.execute(
            "UPDATE drafts SET revision=revision+1, proposal_json=?, content_hash=?, "
            "confirmed_revision=NULL WHERE draft_id=?",
            (json.dumps(proposal, ensure_ascii=False), proposal_hash(proposal), draft_id),
        )

    def _apply_turn_patch(self, row, patch):
        before = json.loads(row["proposal_json"])
        merged = apply_changes(before, patch["set"], patch["clear"])
        changed = [name for name in FIELDS if merged[name] != before[name]]
        self._write_proposal(row["draft_id"], merged)
        self.conn.execute(
            "UPDATE draft_inputs SET input_state='applied', changed_fields_json=? WHERE draft_id=?",
            (json.dumps(changed), row["draft_id"]),
        )

    def _start_turn(self, draft_id, transcript, revision, *, state="processing"):
        self.conn.execute(
            "INSERT INTO draft_inputs (draft_id, turn_id, starting_revision, transcript, input_state) "
            "VALUES (?,?,?,?,?) ON CONFLICT(draft_id) DO UPDATE SET "
            "turn_id=excluded.turn_id, starting_revision=excluded.starting_revision, "
            "transcript=excluded.transcript, input_state=excluded.input_state, patch_json=NULL, "
            "changed_fields_json='[]', error_code=NULL",
            (draft_id, uuid.uuid4().hex, revision, transcript, state),
        )
        self.conn.execute("UPDATE drafts SET confirmed_revision=NULL WHERE draft_id=?", (draft_id,))

    def _job_exists(self, job_id) -> bool:
        return (
            self.conn.execute("SELECT 1 FROM jobs WHERE job_id=?", (job_id,)).fetchone() is not None
        )

    def _reset_empty_speech(self, draft_id):
        self.conn.execute("DELETE FROM draft_speech WHERE draft_id=?", (draft_id,))

    def _record_speech_failure(self, draft_id, *, empty):
        code = "empty_transcript" if empty else "transcription_failed"
        self.conn.execute(
            "UPDATE draft_inputs SET input_state='speech_error', error_code=? WHERE draft_id=?",
            (code, draft_id),
        )
        if empty:
            self.conn.execute(
                "INSERT INTO draft_speech (draft_id, empty_attempts) VALUES (?,1) "
                "ON CONFLICT(draft_id) DO UPDATE SET empty_attempts=empty_attempts+1",
                (draft_id,),
            )
        return Outcome(
            False, code, "Please record again or type your update.", self.get_draft(draft_id)
        )

    @staticmethod
    def _view(row) -> dict:
        proposal = json.loads(row["proposal_json"])
        v = validate(proposal)
        return {
            "draft_id": row["draft_id"],
            "revision": row["revision"],
            "content_hash": row["content_hash"],
            "proposal": proposal,
            "confirmed": row["confirmed_revision"] == row["revision"],
            "state": row["state"],
            "missing_fields": list(v.missing_fields),
            "invalid_fields": dict(v.invalid_fields),
        }

    def list_jobs(self):
        """Return the fictional jobs available for selection."""
        with self._lock:
            rows = self.conn.execute(
                "SELECT job_id, appliance, customer_label, status FROM jobs ORDER BY job_id"
            ).fetchall()
            return [dict(row) for row in rows]

    def get_draft(self, draft_id):
        with self._lock:
            # One SELECT gives a coherent snapshot even across Store connections.
            row = self.conn.execute(
                "SELECT d.*, i.turn_id, i.starting_revision, i.transcript, i.input_state, "
                "i.patch_json, i.changed_fields_json, i.error_code, s.result_json AS receipt_json, "
                "COALESCE(sp.empty_attempts,0) AS empty_speech_attempts, "
                "sr.submission_id AS pending_submission_id, sr.attempts AS save_attempts "
                "FROM drafts d LEFT JOIN draft_inputs i ON d.draft_id=i.draft_id "
                "LEFT JOIN submissions s ON d.draft_id=s.draft_id "
                "LEFT JOIN draft_speech sp ON d.draft_id=sp.draft_id "
                "LEFT JOIN save_requests sr ON d.draft_id=sr.draft_id AND sr.state='pending' "
                "WHERE d.draft_id=?",
                (draft_id,),
            ).fetchone()
            if row is None:
                return None
            view = self._view(row)
            view["empty_speech_attempts"] = row["empty_speech_attempts"]
            view["save_request"] = (
                {"submission_id": row["pending_submission_id"], "attempts": row["save_attempts"]}
                if row["pending_submission_id"]
                else None
            )
            view["receipt"] = json.loads(row["receipt_json"]) if row["receipt_json"] else None
            view["input"] = None
            if row["turn_id"] is not None:
                view["input"] = {
                    "turn_id": row["turn_id"],
                    "starting_revision": row["starting_revision"],
                    "transcript": row["transcript"],
                    "state": row["input_state"],
                    "patch": json.loads(row["patch_json"]) if row["patch_json"] else None,
                    "changed_fields": json.loads(row["changed_fields_json"]),
                    "error_code": row["error_code"],
                }
            return view

    def close(self):
        with self._lock:
            self.conn.close()

    # ---------- draft lifecycle ----------
    @_guarded
    def create_draft(self, raw_proposal) -> Outcome:
        proposal = normalize(raw_proposal)
        draft_id = uuid.uuid4().hex
        with self._tx():
            if not self._job_exists(proposal["job_id"]):
                raise _Stop(
                    Outcome(False, "unknown_job", "Select a known job before creating a draft.")
                )
            self.conn.execute(
                "INSERT INTO drafts (draft_id, revision, proposal_json, content_hash) VALUES (?,?,?,?)",
                (draft_id, 1, json.dumps(proposal, ensure_ascii=False), proposal_hash(proposal)),
            )
            view = self.get_draft(draft_id)
        return Outcome(True, "created", "Draft created.", view)

    @_guarded
    def update_draft(self, draft_id, changes, clear=(), *, expected_revision=None) -> Outcome:
        """Any edit bumps the revision and invalidates the previous confirmation."""
        self._check_revision(expected_revision)
        with self._tx():
            row = self._open_draft(draft_id)
            if expected_revision != row["revision"]:
                raise _Stop(
                    Outcome(False, "stale_update", "Reload the latest draft before editing.")
                )
            merged = apply_changes(json.loads(row["proposal_json"]), changes, clear)
            self._write_proposal(draft_id, merged)
            self.conn.execute(
                "UPDATE draft_inputs SET input_state='superseded', changed_fields_json='[]' "
                "WHERE draft_id=?",
                (draft_id,),
            )
            view = self.get_draft(draft_id)
        return Outcome(True, "updated", "Draft updated; please confirm again.", view)

    @_guarded
    def begin_turn(self, draft_id, transcript, *, expected_revision) -> Outcome:
        """Persist input and revoke approval before the extractor runs outside the transaction."""
        validate_message(transcript)
        self._check_revision(expected_revision)
        with self._tx():
            row = self._open_draft(draft_id)
            if row["revision"] != expected_revision:
                raise _Stop(
                    Outcome(False, "stale_update", "Reload the latest draft before editing.")
                )
            self._start_turn(draft_id, transcript, expected_revision)
            self._reset_empty_speech(draft_id)
            view = self.get_draft(draft_id)
        return Outcome(True, "processing", "Interpreting the message.", view)

    @_guarded
    def retry_turn(self, draft_id, turn_id, *, expected_revision) -> Outcome:
        """Retry a still-current failed message with a fresh turn ID, atomically."""
        with self._tx():
            _, current = self._guard_turn(draft_id, turn_id, expected_revision, state="error")
            self._start_turn(draft_id, current["transcript"], expected_revision)
            view = self.get_draft(draft_id)
        return Outcome(True, "processing", "Retrying the preserved message.", view)

    @_guarded
    def begin_audio_turn(self, draft_id, *, expected_revision) -> Outcome:
        """Reserve a turn before STT; keep the previous usable transcript until success."""
        self._check_revision(expected_revision)
        with self._tx():
            row = self._open_draft(draft_id)
            if row["revision"] != expected_revision:
                raise _Stop(
                    Outcome(False, "stale_update", "Reload the latest draft before recording.")
                )
            current = self._input_row(draft_id)
            transcript = current["transcript"] if current else ""
            self._start_turn(draft_id, transcript, expected_revision, state="transcribing")
            view = self.get_draft(draft_id)
        return Outcome(True, "transcribing", "Transcribing the recording.", view)

    @_guarded
    def complete_audio_turn(self, draft_id, turn_id, transcript, *, expected_revision) -> Outcome:
        with self._tx():
            self._guard_turn(draft_id, turn_id, expected_revision, state="transcribing")
            try:
                validate_message(transcript)
                transcript.encode("utf-8")
            except ValueError:
                return self._record_speech_failure(
                    draft_id, empty=isinstance(transcript, str) and not transcript.strip()
                )
            self.conn.execute(
                "UPDATE draft_inputs SET transcript=?, input_state='processing', error_code=NULL WHERE draft_id=?",
                (transcript, draft_id),
            )
            self._reset_empty_speech(draft_id)
            view = self.get_draft(draft_id)
        return Outcome(True, "processing", "Interpreting the transcript.", view)

    @_guarded
    def fail_audio_turn(self, draft_id, turn_id, *, expected_revision, empty=False) -> Outcome:
        if type(empty) is not bool:
            raise ValueError("An explicit boolean empty-speech indicator is required.")
        with self._tx():
            self._guard_turn(draft_id, turn_id, expected_revision, state="transcribing")
            result = self._record_speech_failure(draft_id, empty=empty)
        return result

    @_guarded
    def complete_turn(self, draft_id, turn_id, raw_patch, *, expected_revision) -> Outcome:
        with self._tx():
            row, _ = self._guard_turn(draft_id, turn_id, expected_revision, state="processing")
            try:
                patch = validate_extraction(raw_patch)
            except ValueError:
                self.conn.execute(
                    "UPDATE draft_inputs SET input_state='error', error_code='invalid_extraction' "
                    "WHERE draft_id=?",
                    (draft_id,),
                )
                result = Outcome(
                    False, "invalid_extraction", "The message could not be interpreted. Retry it."
                )
            else:
                self.conn.execute(
                    "UPDATE draft_inputs SET patch_json=? WHERE draft_id=?",
                    (json.dumps(patch, ensure_ascii=False), draft_id),
                )
                if patch["needs_clarification"]:
                    self.conn.execute(
                        "UPDATE draft_inputs SET input_state='clarification' WHERE draft_id=?",
                        (draft_id,),
                    )
                    result = Outcome(
                        True,
                        "clarification_required",
                        "Please restate the full update more clearly.",
                    )
                elif patch["spoken_job_id"] not in (
                    None,
                    json.loads(row["proposal_json"])["job_id"],
                ):
                    self.conn.execute(
                        "UPDATE draft_inputs SET input_state='mismatch' WHERE draft_id=?",
                        (draft_id,),
                    )
                    result = Outcome(
                        True,
                        "job_mismatch",
                        "The message names a different job. Apply to the selected job or discard it.",
                    )
                else:
                    self._apply_turn_patch(row, patch)
                    result = Outcome(True, "updated", "Draft updated; review the current record.")
            result.data = self.get_draft(draft_id)
        return result

    @_guarded
    def fail_turn(self, draft_id, turn_id, *, expected_revision) -> Outcome:
        """Only a current request may record failure; raw provider errors are never stored."""
        with self._tx():
            self._guard_turn(draft_id, turn_id, expected_revision, state="processing")
            self.conn.execute(
                "UPDATE draft_inputs SET input_state='error', error_code='extraction_failed' WHERE draft_id=?",
                (draft_id,),
            )
            view = self.get_draft(draft_id)
        return Outcome(
            False,
            "extraction_failed",
            "Extraction failed. Your message is preserved; retry it.",
            view,
        )

    @_guarded
    def resolve_mismatch(self, draft_id, turn_id, action, *, expected_revision) -> Outcome:
        if action not in ("apply", "discard"):
            raise ValueError("Choose apply or discard for the held message.")
        with self._tx():
            row, current = self._guard_turn(draft_id, turn_id, expected_revision, state="mismatch")
            if action == "discard":
                self.conn.execute(
                    "UPDATE draft_inputs SET input_state='discarded' WHERE draft_id=?", (draft_id,)
                )
            else:
                # Only this explicit resolution path may ignore the spoken job.
                patch = validate_extraction(json.loads(current["patch_json"]))
                if patch["needs_clarification"]:
                    raise ValueError("Clarify the message before applying it.")
                self._apply_turn_patch(row, patch)
            view = self.get_draft(draft_id)
        return Outcome(
            True,
            "updated" if action == "apply" else "discarded",
            "Message resolved; review the current record.",
            view,
        )

    @_guarded
    def cancel_draft(self, draft_id, *, expected_revision) -> Outcome:
        self._check_revision(expected_revision)
        with self._tx():
            row = self._open_draft(draft_id)
            if row["revision"] != expected_revision:
                raise _Stop(
                    Outcome(False, "stale_update", "Reload the latest draft before cancelling.")
                )
            self.conn.execute(
                "UPDATE drafts SET state='cancelled', revision=revision+1, confirmed_revision=NULL WHERE draft_id=?",
                (draft_id,),
            )
            self.conn.execute(
                "UPDATE draft_inputs SET input_state='cancelled' WHERE draft_id=?", (draft_id,)
            )
            view = self.get_draft(draft_id)
        return Outcome(True, "cancelled", "Draft cancelled; nothing was saved.", view)

    @_guarded
    def confirm(self, draft_id, revision: int, content_hash: str) -> Outcome:
        """Confirms one exact revision+hash. Only possible for a complete, valid draft of a known job."""
        self._check_revision(revision)
        with self._tx():
            row = self._open_draft(draft_id)
            self._require_resolved_input(draft_id)
            if revision != row["revision"] or content_hash != row["content_hash"]:
                raise _Stop(
                    Outcome(
                        False,
                        "stale_confirmation",
                        "The record changed after that read-back; review the latest version.",
                    )
                )
            proposal = json.loads(row["proposal_json"])
            v = validate(proposal)
            if not v.complete:
                raise _Stop(
                    Outcome(
                        False,
                        "incomplete",
                        "The record is not complete yet.",
                        {
                            "missing_fields": list(v.missing_fields),
                            "invalid_fields": dict(v.invalid_fields),
                        },
                    )
                )
            if not self._job_exists(proposal["job_id"]):
                raise _Stop(
                    Outcome(False, "unknown_job", f"Job {proposal['job_id']} was not found.")
                )
            self.conn.execute(
                "UPDATE drafts SET confirmed_revision=? WHERE draft_id=?", (revision, draft_id)
            )
            view = self.get_draft(draft_id)
        return Outcome(True, "confirmed", "Confirmed.", view)

    # ---------- the only write path ----------
    def _save_request(self, submission_id):
        return self.conn.execute(
            "SELECT * FROM save_requests WHERE submission_id=?", (submission_id,)
        ).fetchone()

    @_guarded
    def save_status(self, draft_id, submission_id) -> Outcome:
        """Missing receipt/request is unknown, never proof of rollback."""
        with self._lock:
            receipt = self.conn.execute(
                "SELECT draft_id, result_json FROM submissions WHERE submission_id=?",
                (submission_id,),
            ).fetchone()
            request = self._save_request(submission_id)
            if (receipt is not None and receipt["draft_id"] != draft_id) or (
                request is not None and request["draft_id"] != draft_id
            ):
                return Outcome(False, "submission_conflict", "Submission belongs to another draft.")
            data = {
                "submission_id": submission_id,
                "receipt": None,
                "locked": True,
                "attempts": request["attempts"] if request else 0,
            }
            if receipt is not None:
                data.update(receipt=json.loads(receipt["result_json"]), locked=False, phase="saved")
                return Outcome(True, "saved", "Saved.", data)
            if request is not None and request["state"] == "closed":
                data.update(locked=False, phase="not_saved", error_code=request["error_code"])
                return Outcome(False, "not_saved", "Not saved. Review before trying again.", data)
            data["phase"] = "unresolved"
            return Outcome(
                False, "pending" if request else "unknown", "Save outcome is not yet known.", data
            )

    @_guarded
    def prepare_save(self, draft_id, submission_id, *, revision, content_hash) -> Outcome:
        """Explicitly approve an exact review and durably reserve its submission ID."""
        self._check_revision(revision)
        if (
            not isinstance(submission_id, str)
            or not submission_id.strip()
            or len(submission_id) > 128
        ):
            return Outcome(False, "invalid_submission_id", "A valid submission ID is required.")
        with self._tx():
            existing = self._save_request(submission_id)
            status = self.save_status(draft_id, submission_id)
            previous = self.conn.execute(
                "SELECT revision,content_hash FROM submissions WHERE submission_id=?",
                (submission_id,),
            ).fetchone()
            if previous is not None and (
                previous["revision"] != revision or previous["content_hash"] != content_hash
            ):
                return Outcome(
                    False, "submission_conflict", "Submission is bound to a different review."
                )
            if existing is not None and (
                existing["revision"] != revision or existing["content_hash"] != content_hash
            ):
                return Outcome(
                    False, "submission_conflict", "Submission is bound to a different review."
                )
            if status.code in {"saved", "submission_conflict", "not_saved"}:
                return status
            if existing is not None:
                return status
            row = self._open_draft(draft_id)
            self._require_resolved_input(draft_id)
            if row["revision"] != revision or row["content_hash"] != content_hash:
                raise _Stop(
                    Outcome(False, "stale_confirmation", "Review the latest record before saving.")
                )
            proposal = json.loads(row["proposal_json"])
            if not validate(proposal).complete:
                raise _Stop(Outcome(False, "incomplete", "The record is not complete."))
            if not self._job_exists(proposal["job_id"]):
                raise _Stop(Outcome(False, "unknown_job", "Select a known job."))
            self.conn.execute(
                "INSERT INTO save_requests (submission_id,draft_id,revision,content_hash) VALUES (?,?,?,?)",
                (submission_id, draft_id, revision, content_hash),
            )
            self.conn.execute(
                "UPDATE drafts SET state='saving', confirmed_revision=? WHERE draft_id=?",
                (revision, draft_id),
            )
            status = self.save_status(draft_id, submission_id)
        return status

    @_guarded
    def begin_save_attempt(self, draft_id, submission_id) -> Outcome:
        """The budget survives process restarts and concurrent callers."""
        with self._tx():
            status = self.save_status(draft_id, submission_id)
            if status.code != "pending":
                return status
            request = self._save_request(submission_id)
            if request["attempts"] >= 3:
                return Outcome(
                    False, "attempts_exhausted", "Automatic save attempts exhausted.", status.data
                )
            self.conn.execute(
                "UPDATE save_requests SET attempts=attempts+1 WHERE submission_id=?",
                (submission_id,),
            )
            status = self.save_status(draft_id, submission_id)
        return Outcome(True, "attempt", "Sending the reserved save.", status.data)

    @_guarded
    def mark_save_unresolved(self, draft_id, submission_id) -> Outcome:
        with self._tx():
            status = self.save_status(draft_id, submission_id)
            if status.code == "pending":
                self.conn.execute(
                    "UPDATE drafts SET state='save_unresolved' WHERE draft_id=? AND state='saving'",
                    (draft_id,),
                )
        return status

    @_guarded
    def close_failed_save(self, draft_id, submission_id, *, error_code) -> Outcome:
        """Fence all late deliveries in a write transaction before allowing edits."""
        allowed = {
            "failed",
            "not_confirmed",
            "incomplete",
            "stale_confirmation",
            "cancelled",
            "integrity_error",
            "unknown_job",
            "pending_input",
            "save_closed",
            "draft_locked",
        }
        if error_code not in allowed:
            raise ValueError("A known save rejection code is required.")
        with self._tx():
            status = self.save_status(draft_id, submission_id)
            if status.code != "pending":
                return status
            self.conn.execute(
                "UPDATE save_requests SET state='closed', error_code=? WHERE submission_id=?",
                (error_code, submission_id),
            )
            self.conn.execute(
                "UPDATE drafts SET state='open', confirmed_revision=NULL WHERE draft_id=? "
                "AND state IN ('saving','save_unresolved')",
                (draft_id,),
            )
            status = self.save_status(draft_id, submission_id)
        return status

    @_guarded
    def save(self, draft_id, submission_id) -> Outcome:
        if (
            not isinstance(submission_id, str)
            or not submission_id.strip()
            or len(submission_id) > 128
        ):
            return Outcome(
                False,
                "invalid_submission_id",
                "A nonempty submission ID of at most 128 characters is required.",
            )
        with self._tx():
            prior = self.conn.execute(
                "SELECT draft_id, result_json FROM submissions WHERE submission_id=?",
                (submission_id,),
            ).fetchone()
            if prior is not None:
                if prior["draft_id"] != draft_id:
                    raise _Stop(
                        Outcome(
                            False,
                            "submission_conflict",
                            "That submission ID belongs to a different draft.",
                        )
                    )
                return Outcome(
                    True,
                    "replayed",
                    "Already saved; returning the original result.",
                    json.loads(prior["result_json"]),
                )

            request = self._save_request(submission_id)
            if request is None:
                row = self._open_draft(draft_id)
            else:
                if request["draft_id"] != draft_id:
                    raise _Stop(
                        Outcome(
                            False, "submission_conflict", "Submission belongs to another draft."
                        )
                    )
                if request["state"] != "pending":
                    raise _Stop(Outcome(False, "save_closed", "This save attempt is closed."))
                if request["attempts"] < 1:
                    raise _Stop(
                        Outcome(False, "attempt_not_started", "Reserve a delivery attempt first.")
                    )
                row = self._draft_row(draft_id)
                if row is None or row["state"] not in {"saving", "save_unresolved"}:
                    raise _Stop(Outcome(False, "draft_locked", "This save does not own the draft."))
                if (
                    row["revision"] != request["revision"]
                    or row["content_hash"] != request["content_hash"]
                ):
                    raise _Stop(
                        Outcome(False, "stale_confirmation", "The reserved review changed.")
                    )
            self._require_resolved_input(draft_id)
            if row["confirmed_revision"] != row["revision"]:
                raise _Stop(
                    Outcome(False, "not_confirmed", "The current version has not been confirmed.")
                )

            proposal = json.loads(row["proposal_json"])
            if proposal_hash(proposal) != row["content_hash"]:
                raise _Stop(
                    Outcome(False, "integrity_error", "Stored record does not match its hash.")
                )
            v = validate(proposal)
            if not v.complete:
                raise _Stop(Outcome(False, "incomplete", "The record is not complete."))
            if not self._job_exists(proposal["job_id"]):
                raise _Stop(
                    Outcome(False, "unknown_job", f"Job {proposal['job_id']} was not found.")
                )

            now = datetime.now(timezone.utc).isoformat()
            result = {
                "submission_id": submission_id,
                "job_id": proposal["job_id"],
                "status": proposal["status"],
                "parts_request_id": None,
                "task_id": None,
            }

            # submissions row first: parts_requests/tasks reference it, and its UNIQUE keys are the guard
            self.conn.execute(
                "INSERT INTO submissions (submission_id, draft_id, revision, content_hash, saved_at, result_json) "
                "VALUES (?,?,?,?,?,?)",
                (submission_id, draft_id, row["revision"], row["content_hash"], now, "{}"),
            )
            self.conn.execute(
                "UPDATE jobs SET status=?, diagnosis=?, follow_up=?, updated_at=? WHERE job_id=?",
                (
                    proposal["status"],
                    proposal["diagnosis"],
                    proposal["follow_up"],
                    now,
                    proposal["job_id"],
                ),
            )
            if proposal["part_needed"]:
                cur = self.conn.execute(
                    "INSERT INTO parts_requests (submission_id, job_id, part, quantity) VALUES (?,?,?,?)",
                    (
                        submission_id,
                        proposal["job_id"],
                        proposal["part_needed"],
                        proposal["quantity"],
                    ),
                )
                result["parts_request_id"] = cur.lastrowid
            if proposal["follow_up"]:
                cur = self.conn.execute(
                    "INSERT INTO tasks (submission_id, job_id, description) VALUES (?,?,?)",
                    (submission_id, proposal["job_id"], proposal["follow_up"]),
                )
                result["task_id"] = cur.lastrowid
            self.conn.execute(
                "UPDATE submissions SET result_json=? WHERE submission_id=?",
                (json.dumps(result), submission_id),
            )
            self.conn.execute("UPDATE drafts SET state='saved' WHERE draft_id=?", (draft_id,))
            self.conn.execute(
                "UPDATE save_requests SET state='saved' WHERE submission_id=?", (submission_id,)
            )
        return Outcome(True, "saved", "Saved.", result)
