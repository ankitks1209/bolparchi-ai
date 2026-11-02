"""Generate audio only for an exact, still-current review. No save authority."""

from .store import Outcome


class SpeechReview:
    def __init__(self, workflow, synthesizer):
        self.workflow = workflow
        self.synthesizer = synthesizer

    def speak(self, draft_id, *, revision, content_hash):
        if self.synthesizer is None:
            return Outcome(
                False, "speech_unavailable", "Read-back is unavailable. Read the record on screen."
            )
        before = self.workflow.review(draft_id)
        view = before.data
        if (
            not before.ok
            or not view.get("can_confirm")
            or type(revision) is not int
            or view["revision"] != revision
            or view["content_hash"] != content_hash
        ):
            return Outcome(False, "stale_review", "Review the current record before listening.")
        try:
            audio = self.synthesizer(view["readback"])
            if not isinstance(audio, bytes) or not audio:
                raise ValueError("invalid_audio")
        except Exception:
            return Outcome(
                False,
                "speech_failed",
                "Read-back could not be played. The text review is still available.",
            )
        after = self.workflow.review(draft_id)
        if not after.ok or after.data != view:
            return Outcome(
                False, "stale_review", "The record changed. Listen to the current review instead."
            )
        return Outcome(True, "audio", "Current review audio.", {"audio": audio})
