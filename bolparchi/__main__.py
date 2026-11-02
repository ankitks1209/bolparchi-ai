"""Run a fictional, text-only demonstration: python -m bolparchi."""

from . import Store, new_submission_id, readback_text


def main():
    store = Store()
    try:
        print("BolParchi core demo: fictional records; no speech or model calls.")
        result = store.create_draft(
            {
                "job_id": "104",
                "diagnosis": "motor kharab",
                "status": "pending",
                "part_needed": "motor",
                "quantity": 2,
                "follow_up": "customer kal shaam available",
            }
        )
        if not result.ok:
            print(result.message)
            return
        draft = result.data
        result = store.update_draft(
            draft["draft_id"], {"quantity": "ek"}, expected_revision=draft["revision"]
        )
        if not result.ok:
            print(result.message)
            return
        draft = result.data
        print("Correction applied in code: quantity 2 -> 1.")
        print(readback_text(draft["proposal"]))
        answer = input("Type yes to confirm and save this fictional record: ").strip().lower()
        if answer != "yes":
            print("Not saved.")
            return
        result = store.confirm(draft["draft_id"], draft["revision"], draft["content_hash"])
        if not result.ok:
            print(result.message)
            return
        submission = new_submission_id()
        saved = store.save(draft["draft_id"], submission)
        print(saved.code, saved.data)
        if saved.ok:
            print("Retry with same ID:", store.save(draft["draft_id"], submission).code)
    finally:
        store.close()


if __name__ == "__main__":
    main()
