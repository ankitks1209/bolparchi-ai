from bolparchi import Store
from bolparchi.recovery import SaveRecovery


def test_jobs_show_persisted_status_only_after_confirmed_save(tmp_path):
    path = str(tmp_path / "jobs.sqlite")
    store = Store(path)
    try:
        jobs = store.list_jobs()
        assert jobs == [
            {
                "job_id": "104",
                "appliance": "Washing machine",
                "customer_label": "Demo Customer A",
                "status": "open",
            },
            {
                "job_id": "105",
                "appliance": "Refrigerator",
                "customer_label": "Demo Customer B",
                "status": "open",
            },
            {
                "job_id": "106",
                "appliance": "Air conditioner",
                "customer_label": "Demo Customer C",
                "status": "open",
            },
        ]
        draft = store.create_draft(
            {"job_id": "104", "diagnosis": "belt adjusted", "status": "completed"}
        ).data
        assert store.list_jobs()[0]["status"] == "open"
        result = SaveRecovery(store).save(
            draft["draft_id"],
            "listing-save",
            revision=draft["revision"],
            content_hash=draft["content_hash"],
        )
        assert result.code == "saved"
    finally:
        store.close()
    reopened = Store(path)
    try:
        assert reopened.list_jobs()[0]["status"] == "completed"
    finally:
        reopened.close()


def test_no_jobs_is_an_empty_collection():
    store = Store(seed=False)
    try:
        assert store.list_jobs() == []
    finally:
        store.close()
