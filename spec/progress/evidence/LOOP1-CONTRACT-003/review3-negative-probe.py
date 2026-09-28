"""Independent additional in-memory Contract 003 negative controls."""
import copy
import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("contract003", root / "contracts/plugin-api/verify.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cases = {case["id"]: case for case in json.loads((root / "contracts/fixtures/sync-plugin/golden.json").read_text(encoding="utf-8"))["cases"]}

def check(label, case_id, mutate):
    case = copy.deepcopy(cases[case_id])
    mutate(case)
    try:
        accepted = module.run(case) == case["expect"]
    except module.Invalid:
        accepted = False
    print(f"{label}: {'ACCEPTED_INVALID' if accepted else 'REJECTED'}")
    return accepted

checks = [
    ("query-missing-page", "query-read-only-paginated", lambda c: c["steps"][0].pop("response")),
    ("query-wrong-request-identity", "query-read-only-paginated", lambda c: c["steps"][0]["response"].__setitem__("conversationId", "30000000-0000-4000-8000-000000000099")),
    ("query-terminal-with-next-token", "query-read-only-paginated", lambda c: c["steps"][1]["response"].__setitem__("nextPageToken", "unexpected")),
    ("denied-query-leaks-page", "deny-query-permission", lambda c: c["steps"][0].__setitem__("response", copy.deepcopy(cases["allow-query"]["steps"][0]["response"]))),
    ("failed-send-mismatched-server-request", "failed-to-sent-terminal", lambda c: c["steps"][1]["message"].__setitem__("requestId", "40000000-0000-4000-8000-000000000099")),
    ("action-execution-revocation-ignored", "action-revoked-at-execution", lambda c: c["steps"][1].__setitem__("authorizedAtExecution", True)),
    ("upgrade-backend-renderer-split", "upgrade-atomic-switch", lambda c: c["steps"][0].__setitem__("rendererVersion", "3.0.0")),
]
results = [check(*check_spec) for check_spec in checks]
print(f"RESULT: {sum(results)}/{len(results)} invalid mutations accepted")
raise SystemExit(1 if any(results) else 0)
