"""Bounded save orchestration; only authoritative receipts establish success."""

from .store import Outcome


REJECTIONS = {
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


class SaveRecovery:
    def __init__(self, store, *, send_save=None):
        self.store = store
        self.send_save = send_save or store.save

    def save(self, draft_id, submission_id, *, revision, content_hash):
        prepared = self.store.prepare_save(
            draft_id, submission_id, revision=revision, content_hash=content_hash
        )
        if prepared.code != "pending":
            if prepared.code == "failed":
                return self.check_status(draft_id, submission_id)
            return prepared
        for _ in range(3):
            attempt = self.store.begin_save_attempt(draft_id, submission_id)
            if attempt.code == "saved":
                return attempt
            if attempt.code != "attempt":
                break
            delivery_timed_out = False
            try:
                result = self.send_save(draft_id, submission_id)
            except (TimeoutError, ConnectionError):
                result = None
                delivery_timed_out = True
            except Exception:
                break
            status = self.store.save_status(draft_id, submission_id)
            if status.code in {"saved", "not_saved", "submission_conflict"}:
                return status
            if delivery_timed_out:
                continue
            if (
                not isinstance(result, Outcome)
                or not isinstance(result.data, dict)
                or not isinstance(result.code, str)
            ):
                break
            if result.code in REJECTIONS or result.data.get("transaction_rolled_back") is True:
                if (
                    result.code == "failed"
                    and result.data.get("retryable") is True
                    and attempt.data["attempts"] < 3
                ):
                    continue
                closed = self.store.close_failed_save(
                    draft_id, submission_id, error_code=result.code
                )
                if closed.code in {"saved", "not_saved", "submission_conflict"}:
                    return closed
                break
            if result.code != "failed" or result.data.get("retryable") is not True:
                break
        return self.check_status(draft_id, submission_id)

    def check_status(self, draft_id, submission_id):
        for _ in range(2):
            status = self.store.save_status(draft_id, submission_id)
            if status.code in {"saved", "not_saved", "submission_conflict"}:
                return status
        status = self.store.mark_save_unresolved(draft_id, submission_id)
        if status.code in {"saved", "not_saved", "submission_conflict"}:
            return status
        return Outcome(
            False,
            "unresolved",
            "Still checking. Keep this submission ID and check status again.",
            {
                "phase": "unresolved",
                "submission_id": submission_id,
                "receipt": None,
                "locked": True,
                "attempts": status.data.get("attempts", 0),
            },
        )
