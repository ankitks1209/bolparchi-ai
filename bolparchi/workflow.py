"""Typed and recorded-message workflow; Store owns all mutations.

An extractor receives only a message and a copy of the current record, and
returns the strict patch envelope. This module makes no provider calls itself
and never confirms or saves on the model's behalf. An optional transcriber runs
outside transactions after Store reserves a guarded speech turn.
"""

from .readback import question_for, readback_text
from .store import Outcome, Store
from .provider_http import ProviderError
from .validation import validate


def present(draft: dict) -> dict:
    """Derive one user-facing state from a coherent stored snapshot."""
    view = dict(draft)
    current = draft["input"]
    input_state = current["state"] if current else None
    view.update(
        question=None,
        readback=None,
        can_confirm=False,
        can_retry=False,
        offer_typing=False,
        prefer_typing=False,
        can_cancel=draft["state"] == "open",
        changed_fields=current["changed_fields"] if current else [],
    )
    if draft["state"] != "open":
        view["phase"] = draft["state"]
    elif input_state == "transcribing":
        view["phase"] = "transcribing"
        view["offer_typing"] = True
    elif input_state == "speech_error":
        view["phase"] = "speech_error"
        view["offer_typing"] = True
        view["prefer_typing"] = draft["empty_speech_attempts"] >= 2
        view["question"] = "Dobara record karein ya apna update type karein."
    elif input_state == "processing":
        view["phase"] = "processing"
    elif input_state == "mismatch":
        view["phase"] = "job_mismatch"
        view["question"] = (
            f"Message mein job {current['patch']['spoken_job_id']} hai. "
            f"Selected job {draft['proposal']['job_id']} par lagayein ya message hata dein?"
        )
    elif input_state == "clarification":
        view["phase"] = "clarify_message"
        view["question"] = "Apna poora update dobara saaf bata sakte hain?"
    elif input_state == "error":
        view["phase"] = "extraction_error"
        view["can_retry"] = True
    else:
        validation = validate(draft["proposal"])
        if validation.complete:
            view["phase"] = "review"
            view["readback"] = readback_text(validation.proposal)
            view["can_confirm"] = True
        else:
            view["phase"] = "clarify"
            view["question"] = question_for(validation)
    return view


def _present_result(result: Outcome) -> Outcome:
    if "draft_id" in result.data:
        return Outcome(result.ok, result.code, result.message, present(result.data))
    return result


class Workflow:
    def __init__(self, store: Store, extractor, *, transcriber=None):
        self.store = store
        self.extractor = extractor
        self.transcriber = transcriber

    def submit_audio(self, draft_id, audio, *, file_format, expected_revision) -> Outcome:
        if self.transcriber is None:
            return Outcome(
                False, "transcription_unavailable", "Speech is unavailable; type your update."
            )
        if (
            not isinstance(audio, bytes)
            or not audio
            or not isinstance(file_format, str)
            or not file_format
        ):
            return Outcome(
                False, "invalid_input", "A nonempty recording and audio format are required."
            )
        started = self.store.begin_audio_turn(draft_id, expected_revision=expected_revision)
        if not started.ok:
            return started
        turn_id = started.data["input"]["turn_id"]
        try:
            transcript = self.transcriber(audio, file_format=file_format)
        except Exception as exc:
            failed = self.store.fail_audio_turn(
                draft_id,
                turn_id,
                expected_revision=expected_revision,
                empty=isinstance(exc, ProviderError) and str(exc) == "empty_transcript",
            )
            return _present_result(failed)
        completed = self.store.complete_audio_turn(
            draft_id, turn_id, transcript, expected_revision=expected_revision
        )
        return self._extract(completed) if completed.ok else _present_result(completed)

    def select_job(self, job_id) -> Outcome:
        return _present_result(self.store.create_draft({"job_id": job_id}))

    def review(self, draft_id) -> Outcome:
        draft = self.store.get_draft(draft_id)
        if draft is None:
            return Outcome(False, "not_found", "No such draft.")
        return Outcome(True, "draft", "Current record.", present(draft))

    def _extract(self, started: Outcome) -> Outcome:
        if not started.ok:
            return started
        draft = started.data
        current = draft["input"]

        # The callback runs outside every SQLite transaction/lock. Cancellation,
        # newer messages and direct edits remain possible while it is running.
        def is_current():
            latest = self.store.get_draft(draft["draft_id"])
            return bool(
                latest
                and latest["state"] == "open"
                and latest["revision"] == current["starting_revision"]
                and latest["input"]
                and latest["input"]["turn_id"] == current["turn_id"]
                and latest["input"]["state"] == "processing"
            )

        try:
            guarded = getattr(self.extractor, "extract_with_guard", None)
            if guarded is not None:
                raw = guarded(current["transcript"], dict(draft["proposal"]), is_current=is_current)
            else:
                raw = self.extractor(current["transcript"], dict(draft["proposal"]))
        except Exception:
            result = self.store.fail_turn(
                draft["draft_id"],
                current["turn_id"],
                expected_revision=current["starting_revision"],
            )
        else:
            result = self.store.complete_turn(
                draft["draft_id"],
                current["turn_id"],
                raw,
                expected_revision=current["starting_revision"],
            )
        return _present_result(result)

    def submit(self, draft_id, message, *, expected_revision) -> Outcome:
        return self._extract(
            self.store.begin_turn(draft_id, message, expected_revision=expected_revision)
        )

    def retry(self, draft_id, turn_id, *, expected_revision) -> Outcome:
        return self._extract(
            self.store.retry_turn(draft_id, turn_id, expected_revision=expected_revision)
        )

    def resolve_mismatch(self, draft_id, turn_id, action, *, expected_revision) -> Outcome:
        return _present_result(
            self.store.resolve_mismatch(
                draft_id,
                turn_id,
                action,
                expected_revision=expected_revision,
            )
        )

    def cancel(self, draft_id, *, expected_revision) -> Outcome:
        return _present_result(
            self.store.cancel_draft(draft_id, expected_revision=expected_revision)
        )
