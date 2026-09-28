"""Independent in-memory WSS scenario precondition audit; no product edits."""
import copy
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("wss", Path("contracts/websocket/verify.py"))
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
base = {case["id"]: case for case in w.fixtures()["scenarios"]}

checks = [
    ("durable-unauthenticated", "durable-send-and-created", lambda s: s["given"].update(socket="UNAUTHENTICATED")),
    ("durable-nonmember", "durable-send-and-created", lambda s: s["given"].update(member=False)),
    ("durable-rollback", "durable-send-and-created", lambda s: s["given"].update(transaction="rolled back before commit")),
    ("retry-unauthenticated", "idempotent-retry", lambda s: s["given"].update(socket="UNAUTHENTICATED")),
    ("cross-conversation-rollback", "same-request-different-conversation", lambda s: s["given"].update(transaction="both rolled back")),
    ("group-nonmember", "group-single-message", lambda s: s["given"].update(member=False)),
    ("preauth-send-authenticated", "unauthenticated-send", lambda s: s["given"].update(socket="AUTHENTICATED")),
    ("rollback-declared-committed", "rollback-before-ack", lambda s: s["given"].update(transaction="committed")),
    ("bind-invalid-token", "bind-valid-session", lambda s: s["given"].update(token="invalid signature")),
]

rejected = 0
for label, case_id, mutate in checks:
    case = copy.deepcopy(base[case_id])
    mutate(case)
    try:
        w.check_scenario(case)
    except w.Invalid as exc:
        rejected += 1
        print(f"REJECT {label}: {exc}")
    else:
        print(f"ACCEPT INVALID {label}")

print(f"REJECTED {rejected}/{len(checks)} invalid precondition mutations")
raise SystemExit(0 if rejected == len(checks) else 1)
