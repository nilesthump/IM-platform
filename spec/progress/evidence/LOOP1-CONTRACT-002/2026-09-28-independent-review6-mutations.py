#!/usr/bin/env python3
"""Independent in-memory checks for same-Conversation request identity and schema shape."""
import copy
import importlib.util
from pathlib import Path

source = Path(__file__).resolve().parents[4] / "contracts/websocket/verify.py"
spec = importlib.util.spec_from_file_location("wss_review6", source)
wss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wss)
scenarios = {s["id"]: s for s in wss.fixtures()["scenarios"]}
failures = 0

changed = copy.deepcopy(scenarios["out-of-order-fanout"])
request_id = changed["steps"][0]["in"]["requestId"]
changed["steps"][1]["in"]["requestId"] = request_id
changed["steps"][1]["out"][0]["requestId"] = request_id
try:
    wss.check_scenario(changed)
except wss.Invalid as exc:
    print(f"REJECT same-Conversation duplicate request identity: {exc}")
else:
    print("ACCEPTED INVALID same-Conversation duplicate request identity: two distinct messages and sequences share sender/Conversation/requestId")
    failures += 1

schema = copy.deepcopy(wss.SCHEMA)
schema["$defs"]["MessageSend"]["allOf"][1]["properties"]["payload"]["type"] = "not-a-json-schema-type"
try:
    wss.lint_schema(schema, root=schema)
except wss.Invalid as exc:
    print(f"REJECT malformed schema type: {exc}")
else:
    print("ACCEPTED INVALID schema type: payload type is not a JSON Schema type")
    failures += 1

raise SystemExit(1 if failures else 0)
