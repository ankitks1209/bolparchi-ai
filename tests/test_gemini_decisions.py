import json
import importlib
from copy import deepcopy

import pytest

from bolparchi.gemini_decisions import FieldDecisionExtractor
from bolparchi.provider_http import ProviderError
from bolparchi import Store
from bolparchi.workflow import Workflow


MESSAGE = "मोटर खराब है, दो मोटर, सॉरी, एक मोटर चाहिए, काम पेंडिंग है, कल शाम आना है।"
EXPECTED = {
    "set": {
        "diagnosis": "मोटर खराब है",
        "status": "pending",
        "part_needed": "मोटर",
        "quantity": 1,
        "follow_up": "कल शाम आना है",
    },
    "clear": [],
    "spoken_job_id": None,
    "needs_clarification": False,
}


def decision(operation="not_mentioned", value=None, evidence=""):
    return {"operation": operation, "value": value, "evidence": evidence}


def complete_decisions():
    return {
        "fields": {
            "diagnosis": decision("set", "मोटर खराब है", "मोटर खराब है"),
            "status": decision("set", "pending", "काम पेंडिंग है"),
            "part_needed": decision("set", "मोटर", "मोटर"),
            "quantity": decision("set", 1, "एक मोटर चाहिए"),
            "follow_up": decision("set", "कल शाम आना है", "कल शाम आना है"),
        },
        "spoken_job_id": None,
        "job_evidence": "",
        "needs_clarification": False,
    }


def response(value):
    return json.dumps(
        {
            "candidates": [
                {
                    "finishReason": "STOP",
                    "content": {"parts": [{"text": json.dumps(value, ensure_ascii=False)}]},
                }
            ]
        }
    ).encode()


@pytest.mark.parametrize(
    "module",
    [
        "scripts.run_web",
        "scripts.probe_gemini",
        "scripts.evaluate_extraction",
        "scripts.check_live_workflow",
        "scripts.diagnose_gemini",
    ],
)
def test_live_entrypoints_preserve_the_supported_followup(module):
    entrypoint = importlib.import_module(module)
    extractor = entrypoint.GeminiExtractor(
        "fictional-key", transport=lambda **_: response(complete_decisions())
    )
    try:
        patch = extractor(MESSAGE, {"job_id": "104"})
    except ProviderError:
        patch = None
    assert patch == EXPECTED, "Live tools must use the verified all-field extraction contract"


def test_prepared_requests_require_followup_accounting():
    from scripts.prepare_provider_probes import build_request

    request = build_request(MESSAGE, {"job_id": "104"})
    schema = request["generationConfig"]["responseFormat"]["text"]["schema"]
    assert "fields" in schema["required"]


def test_all_field_decisions_preserve_followup_after_the_quantity_correction():
    requests = []

    def transport(**request):
        requests.append(request)
        return response(complete_decisions())

    extractor = FieldDecisionExtractor("fictional-key", transport=transport)
    try:
        patch = extractor(MESSAGE, {"job_id": "104"})
    except ProviderError:
        patch = None
    assert patch == EXPECTED, "The adapter must retain the explicitly supported follow-up"
    schema = json.loads(requests[0]["body"])["generationConfig"]["responseFormat"]["text"]["schema"]
    assert set(schema["properties"]["fields"]["required"]) == set(EXPECTED["set"])


def extract(value, message=MESSAGE):
    return FieldDecisionExtractor("fictional-key", transport=lambda **_: response(value))(
        message, {"job_id": "104", "follow_up": "Old visit", "quantity": 2}
    )


def test_component_name_can_be_a_direct_fragment_of_its_supporting_phrase():
    value = complete_decisions()
    value["fields"]["part_needed"]["evidence"] = "एक मोटर चाहिए"
    try:
        patch = extract(value)
    except ProviderError:
        patch = None
    assert patch == EXPECTED, "A component copied from its longer quote is supported"


@pytest.mark.parametrize("field", list(EXPECTED["set"]))
def test_omitted_field_decision_is_rejected(field):
    value = complete_decisions()
    del value["fields"][field]
    with pytest.raises(ProviderError, match="^invalid_response$"):
        extract(value)


@pytest.mark.parametrize(
    "change",
    [
        {"operation": "set", "value": "Tomorrow at 5", "evidence": "कल शाम आना है"},
        {"operation": "set", "value": "कल शाम आना है", "evidence": "not in transcript"},
        {"operation": "set", "value": None, "evidence": "कल शाम आना है"},
        {"operation": "not_mentioned", "value": "Old visit", "evidence": ""},
        {"operation": "not_mentioned", "value": None, "evidence": "कल शाम आना है"},
        {"operation": "clear", "value": None, "evidence": ""},
        {"operation": "clear", "value": "Old visit", "evidence": "कल शाम आना है"},
        {"operation": "save", "value": None, "evidence": "कल शाम आना है"},
    ],
)
def test_unsupported_or_inconsistent_field_output_is_rejected(change):
    value = complete_decisions()
    value["fields"]["follow_up"] = change
    with pytest.raises(ProviderError, match="^invalid_response$"):
        extract(value)


@pytest.mark.parametrize("quantity", [True, 0, 21, "1", None])
def test_set_values_still_obey_the_existing_strict_patch_contract(quantity):
    value = complete_decisions()
    value["fields"]["quantity"]["value"] = quantity
    with pytest.raises(ProviderError, match="^invalid_response$"):
        extract(value)


def test_unmentioned_values_are_not_copied_and_explicit_removal_is_preserved():
    value = complete_decisions()
    value["fields"] = {name: decision() for name in EXPECTED["set"]}
    value["fields"]["follow_up"] = decision("clear", None, "Follow-up hata do")
    assert extract(value, "Follow-up hata do.") == {
        "set": {},
        "clear": ["follow_up"],
        "spoken_job_id": None,
        "needs_clarification": False,
    }


def test_uncertainty_holds_all_other_proposed_changes():
    value = complete_decisions()
    value["fields"]["quantity"] = decision("uncertain", None, "दो मोटर")
    value["needs_clarification"] = True
    assert extract(value) == {
        "set": {},
        "clear": [],
        "spoken_job_id": None,
        "needs_clarification": True,
    }
    value["needs_clarification"] = False
    with pytest.raises(ProviderError, match="^invalid_response$"):
        extract(value)


def test_model_output_cannot_add_authority_or_change_selected_job():
    for value in [
        {**complete_decisions(), "save": True},
        {**complete_decisions(), "spoken_job_id": "105", "job_evidence": "Job 105"},
    ]:
        with pytest.raises(ProviderError, match="^invalid_response$"):
            extract(value)
    value = complete_decisions()
    value.update(spoken_job_id="105", job_evidence="Job 105")
    assert extract(value, "Job 105. " + MESSAGE)["spoken_job_id"] == "105"


def test_full_hindi_patch_replaces_old_followup_but_still_needs_confirmation(tmp_path):
    store = Store(str(tmp_path / "decisions.sqlite"))
    try:
        draft = store.create_draft({"job_id": "104", "follow_up": "Old visit"}).data
        flow = Workflow(
            store,
            FieldDecisionExtractor(
                "fictional-key", transport=lambda **_: response(deepcopy(complete_decisions()))
            ),
        )
        result = flow.submit(draft["draft_id"], MESSAGE, expected_revision=draft["revision"])
        assert result.ok and result.data["phase"] == "review"
        assert result.data["proposal"]["follow_up"] == "कल शाम आना है"
        assert result.data["proposal"]["quantity"] == 1
        assert store.save(draft["draft_id"], "unconfirmed").code == "not_confirmed"
        assert store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
    finally:
        store.close()
