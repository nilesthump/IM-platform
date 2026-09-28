"""Independent Contract 003 acceptance probes; no product files are changed."""
import copy
import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("contract003", root / "contracts/plugin-api/verify.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cases = {c["id"]: c for c in json.loads((root / "contracts/fixtures/sync-plugin/golden.json").read_text(encoding="utf-8"))["cases"]}


def check(name, case_id, mutate):
    case = copy.deepcopy(cases[case_id])
    mutate(case)
    try:
        actual = module.run(case)
        accepted = actual == case["expect"]
    except module.Invalid:
        accepted = False
    print(f"{name}: {'ACCEPTED_INVALID' if accepted else 'REJECTED'}")
    return accepted


results = [
    check("SP-A-002-no-prior-failed-item", "failed-to-sent-terminal", lambda c: c["steps"].pop(0)),
    check("SP-A-006-unbounded-query-response", "query-read-only-paginated", lambda c: c["steps"][0].update({"simulatedResponseCount": 1000000})),
]
print(f"RESULT: {sum(results)}/{len(results)} invalid mutations accepted")
raise SystemExit(1 if any(results) else 0)
