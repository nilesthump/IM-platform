"""Independent in-memory WSS fixture mutation audit; never rewrites product files."""
import copy
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("wss", Path("contracts/websocket/verify.py"))
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
base = {s["id"]: s for s in w.fixtures()["scenarios"]}

def test(name, case_id, mutate):
    s = copy.deepcopy(base[case_id])
    mutate(s)
    try:
        w.check_scenario(s)
    except w.Invalid as exc:
        print(f"REJECT {name}: {exc}")
        return True
    print(f"ACCEPT INVALID {name}")
    return False

checks = [
    ("bind-wrong-user", "bind-valid-session", lambda s: s["steps"][0]["out"][0]["payload"].update(userId=w.M1)),
    ("bind-wrong-epoch", "bind-valid-session", lambda s: s["steps"][0]["out"][0]["payload"].update(sessionEpoch=2)),
    ("durable-missing-created", "durable-send-and-created", lambda s: s["steps"][0]["out"].pop()),
    ("durable-ack-wrong-seq", "durable-send-and-created", lambda s: s["steps"][0]["out"][0]["payload"].update(seq=2)),
    ("durable-created-wrong-message", "durable-send-and-created", lambda s: s["steps"][0]["out"][1]["payload"].update(messageId=w.M2)),
    ("durable-zero-persistence", "durable-send-and-created", lambda s: s["expect"].update(messages=0, outbox=0)),
    ("durable-no-seq-allocation", "durable-send-and-created", lambda s: s["timeline"].remove("SEQ_ALLOCATED")),
    ("retry-stable-wrong-ack", "idempotent-retry", lambda s: [step["out"][0]["payload"].update(messageId=w.M2) for step in s["steps"]]),
    ("retry-duplicate-persistence", "idempotent-retry", lambda s: s["expect"].update(messages=2, outbox=2, seq=[1,2])),
    ("cross-conversation-wrong-ack", "same-request-different-conversation", lambda s: s["steps"][1]["out"][0]["payload"].update(conversationId=w.S)),
    ("group-duplicate-message", "group-single-message", lambda s: s["expect"].update(messages=2, outbox=2)),
    ("duplicate-fanout-double-materialization", "duplicate-fanout", lambda s: s["expect"].update(clientMaterializations=2)),
    ("out-of-order-permanent-gap", "out-of-order-fanout", lambda s: s["expect"].update(permanentSeqGap=True)),
    ("ping-before-bind-authenticated", "ping-before-bind", lambda s: s["expect"].update(socket="AUTHENTICATED")),
    ("ping-no-pong", "ping-before-bind", lambda s: s["steps"][0]["out"].clear()),
    ("preauth-wrong-rejection-code", "unauthenticated-send", lambda s: s["steps"][0]["out"][0]["payload"]["error"].update(code="AUTHORIZATION_DENIED")),
    ("nonmember-wrong-rejection-code", "non-member-send", lambda s: s["steps"][0]["out"][0]["payload"]["error"].update(code="AUTH_REQUIRED")),
    ("rollback-persisted-message", "rollback-before-ack", lambda s: s["expect"].update(messages=1, outbox=1)),
    ("conflicting-retry-false-outcome", "conflicting-retry", lambda s: s["expect"].update(secondSuccessAck=True)),
    ("expired-token-wrong-rejection", "expired-token-bind", lambda s: s["steps"][0]["out"][0]["payload"]["error"].update(code="AUTH_TOKEN_INVALID")),
    ("wrong-client-type-wrong-rejection", "wrong-client-type-bind", lambda s: s["steps"][0]["out"][0]["payload"]["error"].update(code="AUTH_TOKEN_INVALID")),
    ("invalid-signature-wrong-rejection", "invalid-signature-bind", lambda s: s["steps"][0]["out"][0]["payload"]["error"].update(code="AUTH_TOKEN_EXPIRED")),
    ("wrong-conversation-false-expected-flag", "wrong-conversation-fanout", lambda s: s["expect"].update(wrongConversationDelivery=True)),
    ("revoked-persisted-message", "revoked-socket", lambda s: s["expect"].update(messages=1, outbox=1)),
]
rejected = sum(test(*item) for item in checks)
print(f"REJECTED {rejected}/{len(checks)} independent invalid mutations")
raise SystemExit(0 if rejected == len(checks) else 1)
