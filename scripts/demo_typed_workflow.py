"""Offline walkthrough with fixture extraction and real in-memory SQLite.

Run from the repository root: .venv/bin/python -m scripts.demo_typed_workflow
This demonstrates workflow behavior, not language-model or speech accuracy.
"""

from bolparchi import Store, new_submission_id
from bolparchi.workflow import Workflow


MESSAGES = (
    (
        "Motor kharab. Do motor chahiye. Kaam pending hai.",
        {
            "diagnosis": "motor kharab",
            "status": "pending",
            "part_needed": "motor",
            "quantity": 2,
        },
    ),
    ("Kal shaam aana hai.", {"follow_up": "kal shaam"}),
    ("Do nahi, ek motor.", {"quantity": 1}),
)


def fixture_extractor(message, current):
    changes = dict(dict(MESSAGES)[message])
    return {"set": changes, "clear": [], "spoken_job_id": None, "needs_clarification": False}


def main():
    print("OFFLINE WORKFLOW DEMO — fictional data, fixture extraction, no AI or speech calls.")
    store = Store()
    try:
        flow = Workflow(store, fixture_extractor)
        selected = flow.select_job("104")
        if not selected.ok:
            print(selected.code, selected.message)
            return
        draft = selected.data
        print("Selected job:", draft["proposal"]["job_id"])
        for message, _ in MESSAGES:
            print("\nFixture message:", message)
            result = flow.submit(draft["draft_id"], message, expected_revision=draft["revision"])
            if not result.ok:
                print(result.code, result.message)
                return
            draft = result.data
            print("State:", draft["phase"])
            print("Changed fields:", ", ".join(draft["changed_fields"]))
            print(draft["question"] or draft["readback"])
        print("\nReviewed record:", draft["proposal"])
        print("No job update has been saved yet.")
        if (
            input("Type SAVE to explicitly confirm this record; anything else cancels: ").strip()
            != "SAVE"
        ):
            result = flow.cancel(draft["draft_id"], expected_revision=draft["revision"])
            print(result.code, result.message)
            return
        confirmed = store.confirm(draft["draft_id"], draft["revision"], draft["content_hash"])
        if not confirmed.ok:
            print(confirmed.code, confirmed.message)
            return
        submission = new_submission_id()
        saved = store.save(draft["draft_id"], submission)
        print(saved.code, saved.message)
        if saved.ok:
            print("Receipt:", saved.data)
            print("Same submission retried:", store.save(draft["draft_id"], submission).code)
    finally:
        store.close()


if __name__ == "__main__":
    main()
