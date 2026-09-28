"""Independent, in-memory negative probes for the Contract 003 fixture oracle."""
import copy
import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("contract003", root / "contracts/plugin-api/verify.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cases = {c["id"]: c for c in json.loads((root / "contracts/fixtures/sync-plugin/golden.json").read_text(encoding="utf-8"))["cases"]}


def probe(name, case_id, mutate):
    case = copy.deepcopy(cases[case_id])
    mutate(case)
    try:
        actual = module.run(case)
        accepted = actual == case["expect"]
        detail = "unchanged expected result" if accepted else f"different result {actual}"
    except module.Invalid as exc:
        accepted = False
        detail = f"rejected {exc}"
    print(f"{name}: {'ACCEPTED_INVALID' if accepted else 'REJECTED'}: {detail}")
    return accepted


def remove_fault(case):
    case["steps"][0].pop("fault")


def alter_duplicate_body(case):
    case["steps"][1]["message"]["content"]["text"] = "conflicting-payload"


def reuse_identity_with_other_sequence(case):
    case["steps"][2]["message"]["messageId"] = case["steps"][0]["message"]["messageId"]
    case["steps"][2]["message"]["requestId"] = case["steps"][0]["message"]["requestId"]


def remove_first_action_authorization(case):
    case["steps"][0]["authorizedAtExecution"] = False


results = [
    probe("gap-outcome-with-no-intermediate-gap", "gap-out-of-order-duplicate", lambda c: c["steps"].insert(0, c["steps"].pop(2))),
    probe("message-fault-commits-before-retry", "message-rollback-and-retry", remove_fault),
    probe("user-fault-commits-before-retry", "user-rollback-and-retry", remove_fault),
    probe("duplicate-sequence-conflicting-content", "gap-out-of-order-duplicate", alter_duplicate_body),
    probe("same-message-and-request-at-two-sequences", "gap-out-of-order-duplicate", reuse_identity_with_other_sequence),
    probe("first-action-not-authorized-at-execution", "action-retry-audited", remove_first_action_authorization),
    probe("wrong-upgrade-failure-stage", "upgrade-fail-migration", lambda c: c["steps"][0].__setitem__("failAt", "snapshot")),
]
print(f"RESULT: {sum(results)}/{len(results)} invalid mutations accepted")
raise SystemExit(1 if any(results) else 0)
