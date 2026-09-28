#!/usr/bin/env python3
"""Offline WSS contract generator and fixture verifier; Python standard library only."""

import argparse
import copy
import datetime as dt
import json
import pathlib
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "envelope.schema.json").read_text(encoding="utf-8"))
FIXTURE = ROOT.parent / "fixtures" / "websocket" / "golden.json"
U = "10000000-0000-4000-8000-000000000001"
S = "20000000-0000-4000-8000-000000000001"
C1 = "30000000-0000-4000-8000-000000000001"
C2 = "30000000-0000-4000-8000-000000000002"
R1 = "40000000-0000-4000-8000-000000000001"
R2 = "40000000-0000-4000-8000-000000000002"
M1 = "50000000-0000-4000-8000-000000000001"
M2 = "50000000-0000-4000-8000-000000000002"
T1 = "2026-09-28T00:00:01Z"
T2 = "2026-09-28T00:00:02Z"


class Invalid(Exception):
    pass


def lint_schema(node, path="$", root=SCHEMA):
    """Reject unsupported schema keywords instead of silently ignoring constraints."""
    allowed = {"$schema", "$id", "title", "description", "$defs", "$ref", "type", "required", "properties", "additionalProperties", "oneOf", "allOf", "const", "enum", "format", "minLength", "maxLength", "minimum", "maxProperties"}
    unknown = set(node) - allowed
    if unknown:
        raise Invalid(f"{path}: unsupported schema keywords {unknown}")
    if "$ref" in node:
        ref = node["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/$defs/") or ref.split("/")[-1] not in root["$defs"]:
            raise Invalid(f"{path}: unresolved reference {ref}")
    for name, child in node.get("$defs", {}).items():
        lint_schema(child, f"{path}.$defs.{name}", root)
    for name, child in node.get("properties", {}).items():
        lint_schema(child, f"{path}.properties.{name}", root)
    for branch in ("oneOf", "allOf"):
        for i, child in enumerate(node.get(branch, [])):
            lint_schema(child, f"{path}.{branch}[{i}]", root)


def validate(value, schema, path="$", root=SCHEMA):
    """Validate every JSON Schema keyword used by the canonical wire schema."""
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            raise Invalid(f"{path}: external reference {ref}")
        return validate(value, root["$defs"][ref.split("/")[-1]], path, root)
    if "allOf" in schema:
        for part in schema["allOf"]:
            validate(value, part, path, root)
    if "oneOf" in schema:
        successes = 0
        for part in schema["oneOf"]:
            try:
                validate(value, part, path, root)
                successes += 1
            except Invalid:
                pass
        if successes != 1:
            raise Invalid(f"{path}: oneOf matched {successes} branches")
    if "const" in schema and value != schema["const"]:
        raise Invalid(f"{path}: const mismatch")
    if "enum" in schema and value not in schema["enum"]:
        raise Invalid(f"{path}: enum mismatch")
    kind = schema.get("type")
    if kind == "object":
        if not isinstance(value, dict):
            raise Invalid(f"{path}: expected object")
        for name in schema.get("required", []):
            if name not in value:
                raise Invalid(f"{path}: missing {name}")
        if len(value) > schema.get("maxProperties", sys.maxsize):
            raise Invalid(f"{path}: too many properties")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False and set(value) - set(properties):
            raise Invalid(f"{path}: unknown properties {set(value) - set(properties)}")
        for name, child in properties.items():
            if name in value:
                validate(value[name], child, f"{path}.{name}", root)
    elif kind == "string":
        if not isinstance(value, str):
            raise Invalid(f"{path}: expected string")
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", sys.maxsize):
            raise Invalid(f"{path}: invalid length")
        if schema.get("format") == "uuid":
            try:
                if str(uuid.UUID(value)) != value:
                    raise ValueError()
            except ValueError as exc:
                raise Invalid(f"{path}: invalid UUID") from exc
        if schema.get("format") == "date-time":
            try:
                parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    raise ValueError()
            except ValueError as exc:
                raise Invalid(f"{path}: invalid timestamp") from exc
    elif kind == "integer":
        if isinstance(value, bool) or not isinstance(value, int) or value < schema.get("minimum", -sys.maxsize):
            raise Invalid(f"{path}: invalid integer")
    return True


def frame(kind, request_id, payload):
    value = {"protocolVersion": "1.0", "type": kind, "requestId": request_id, "payload": payload}
    validate(value, SCHEMA)
    return value


def send(request_id=R1, conversation=C1, text="hello"):
    return frame("message.send", request_id, {"conversationId": conversation, "content": {"kind": "TEXT", "text": text}})


def ack(request_id=R1, conversation=C1, message=M1, seq=1, created=T1):
    return frame("message.ack", request_id, {"status": "committed", "conversationId": conversation, "messageId": message, "seq": seq, "createdAt": created})


def error_ack(kind, request_id, code):
    return frame(kind, request_id, {"status": "rejected", "error": {"code": code, "message": "Request rejected"}})


def created(request_id=R1, conversation=C1, message=M1, seq=1, created_at=T1):
    return frame("message.created", request_id, {"conversationId": conversation, "messageId": message, "senderId": U, "seq": seq, "createdAt": created_at, "content": {"kind": "TEXT", "text": "hello"}})


def case(case_id, polarity, rules, given, steps, expect):
    return {"id": case_id, "polarity": polarity, "rules": rules, "given": given, "steps": steps, "expect": expect}


def fixtures():
    bind = frame("auth.bind", R1, {"accessToken": "fixture-access-token-not-a-credential"})
    bound = frame("auth.ack", R1, {"status": "bound", "userId": U, "sessionId": S, "clientType": "WEB", "sessionEpoch": 1})
    revoked = frame("session.revoked", R2, {"sessionId": S, "reason": "REPLACED"})
    scenarios = [
        case("bind-valid-session", "positive", ["MSG-D-004"], {"socket": "UNAUTHENTICATED", "token": "valid; signature, expiry, session ID, client type and epoch match"}, [{"in": bind, "out": [bound]}], {"socket": "AUTHENTICATED", "messages": 0, "outbox": 0}),
        case("durable-send-and-created", "positive", ["MSG-A-001", "MSG-I-002", "MSG-I-003"], {"socket": "AUTHENTICATED", "member": True, "transaction": "message+seq+outbox committed", "conversationType": "DIRECT"}, [{"in": send(), "out": [ack(), created()]}], {"messages": 1, "outbox": 1, "seq": [1], "ackAfterCommit": True, "wrongConversationDelivery": False}),
        case("idempotent-retry", "positive", ["MSG-A-002", "MSG-I-001"], {"socket": "AUTHENTICATED", "member": True, "transaction": "first send committed; retry uses same sender/conversation/request and content"}, [{"in": send(), "out": [ack()]}, {"in": send(), "out": [ack()]}], {"messages": 1, "outbox": 1, "seq": [1], "stableAck": True}),
        case("same-request-different-conversation", "positive", ["MSG-A-003"], {"socket": "AUTHENTICATED", "member": True, "transaction": "both committed"}, [{"in": send(), "out": [ack()]}, {"in": send(conversation=C2), "out": [ack(conversation=C2, message=M2, created=T2)]}], {"messages": 2, "outbox": 2, "messageIdsGloballyUnique": True, "conversationSeq": {C1: [1], C2: [1]}}),
        case("group-single-message", "positive", ["MSG-A-006", "MSG-I-007"], {"socket": "AUTHENTICATED", "member": True, "transaction": "committed", "conversationType": "GROUP", "memberCount": 500}, [{"in": send(), "out": [ack()]}], {"messages": 1, "outbox": 1, "localFanoutIndependent": True}),
        case("duplicate-fanout", "positive", ["MSG-A-005", "MSG-I-005"], {"socket": "AUTHENTICATED", "transaction": "already committed; duplicate NATS delivery"}, [{"in": created(), "out": [created(), created()]}], {"messages": 1, "outbox": 1, "clientMaterializations": 1, "syncProvidesEventualCompleteness": True}),
        case("out-of-order-fanout", "positive", ["MSG-A-005", "MSG-A-007"], {"socket": "AUTHENTICATED", "transaction": "two committed messages; event seq 2 arrives before seq 1"}, [{"in": created(R2, C1, M2, 2, T2), "out": [created(R2, C1, M2, 2, T2)]}, {"in": created(), "out": [created()]}], {"messages": 2, "outbox": 2, "clientMaterializations": 2, "contiguousSeqAfterSync": 2, "permanentSeqGap": False}),
        case("ping-before-bind", "positive", [], {"socket": "UNAUTHENTICATED"}, [{"in": frame("ping", R1, {}), "out": [frame("pong", R1, {})]}], {"socket": "UNAUTHENTICATED"}),
        case("unauthenticated-send", "negative", ["MSG-D-004"], {"socket": "UNAUTHENTICATED"}, [{"in": send(), "out": [error_ack("message.ack", R1, "AUTH_REQUIRED")]}], {"messages": 0, "outbox": 0, "successAck": False}),
        case("non-member-send", "negative", ["MSG-A-004", "MSG-I-006"], {"socket": "AUTHENTICATED", "member": False}, [{"in": send(), "out": [error_ack("message.ack", R1, "AUTHORIZATION_DENIED")]}], {"messages": 0, "outbox": 0, "successAck": False}),
        case("rollback-before-ack", "negative", ["MSG-A-001", "MSG-I-002"], {"socket": "AUTHENTICATED", "member": True, "transaction": "rolled back before commit"}, [{"in": send(), "out": [error_ack("message.ack", R1, "MESSAGE_COMMIT_FAILED")]}], {"messages": 0, "outbox": 0, "seq": [], "successAck": False}),
        case("conflicting-retry", "negative", ["MSG-I-001"], {"socket": "AUTHENTICATED", "member": True, "transaction": "first send committed; same key different content"}, [{"in": send(), "out": [ack()]}, {"in": send(text="changed"), "out": [error_ack("message.ack", R1, "MESSAGE_REQUEST_CONFLICT")]}], {"messages": 1, "outbox": 1, "seq": [1], "secondSuccessAck": False}),
        case("stale-epoch-bind", "negative", [], {"socket": "UNAUTHENTICATED", "token": "signed but epoch stale"}, [{"in": bind, "out": [error_ack("auth.ack", R1, "AUTH_SESSION_EPOCH_STALE")]}], {"socket": "UNAUTHENTICATED", "messages": 0}),
        case("expired-token-bind", "negative", [], {"socket": "UNAUTHENTICATED", "token": "expired"}, [{"in": bind, "out": [error_ack("auth.ack", R1, "AUTH_TOKEN_EXPIRED")]}], {"socket": "UNAUTHENTICATED", "messages": 0}),
        case("wrong-client-type-bind", "negative", [], {"socket": "UNAUTHENTICATED", "token": "signed for DESKTOP while session is WEB"}, [{"in": bind, "out": [error_ack("auth.ack", R1, "AUTH_CLIENT_TYPE_MISMATCH")]}], {"socket": "UNAUTHENTICATED", "messages": 0}),
        case("invalid-signature-bind", "negative", [], {"socket": "UNAUTHENTICATED", "token": "invalid signature"}, [{"in": bind, "out": [error_ack("auth.ack", R1, "AUTH_TOKEN_INVALID")]}], {"socket": "UNAUTHENTICATED", "messages": 0}),
        case("wrong-conversation-fanout", "negative", ["MSG-I-004", "MSG-A-007"], {"socket": "AUTHENTICATED", "localMemberOf": C1, "eventConversation": C2}, [{"in": created(R2, C2, M2, 1, T2), "out": []}], {"messages": 1, "outbox": 1, "clientMaterializations": 0, "wrongConversationDelivery": False}),
        case("revoked-socket", "negative", [], {"socket": "AUTHENTICATED", "session": "replaced by newer WEB login"}, [{"in": revoked, "out": [revoked]}, {"in": send(), "out": []}], {"socket": "CLOSED", "messages": 0, "outbox": 0, "successAck": False}),
    ]
    timelines = {
        "durable-send-and-created": ["MEMBER_AUTHORIZED", "BEGIN", "SEQ_ALLOCATED", "MESSAGE_INSERTED", "OUTBOX_INSERTED", "COMMIT", "SUCCESS_ACK", "MESSAGE_CREATED"],
        "idempotent-retry": ["MEMBER_AUTHORIZED", "BEGIN", "SEQ_ALLOCATED", "MESSAGE_INSERTED", "OUTBOX_INSERTED", "COMMIT", "SUCCESS_ACK", "IDEMPOTENCY_HIT", "SUCCESS_ACK"],
        "group-single-message": ["MEMBER_AUTHORIZED", "BEGIN", "SEQ_ALLOCATED", "MESSAGE_INSERTED", "OUTBOX_INSERTED", "COMMIT", "SUCCESS_ACK", "LOCAL_FANOUT"],
        "rollback-before-ack": ["MEMBER_AUTHORIZED", "BEGIN", "SEQ_ALLOCATED", "MESSAGE_INSERTED", "OUTBOX_INSERTED", "ROLLBACK", "REJECTED_ACK"],
        "non-member-send": ["MEMBER_DENIED", "REJECTED_ACK"],
        "unauthenticated-send": ["AUTH_DENIED", "REJECTED_ACK"],
        "conflicting-retry": ["MEMBER_AUTHORIZED", "BEGIN", "SEQ_ALLOCATED", "MESSAGE_INSERTED", "OUTBOX_INSERTED", "COMMIT", "SUCCESS_ACK", "IDEMPOTENCY_CONFLICT", "REJECTED_ACK"],
    }
    for scenario in scenarios:
        scenario["timeline"] = timelines.get(scenario["id"], [])
    return {"fixtureVersion": "1.0", "contractVersion": "1.0", "profiles": ["go", "java"], "scenarios": scenarios}


def check_scenario(s):
    if not s["id"] or s["polarity"] not in ("positive", "negative") or not s["steps"]:
        raise Invalid("invalid scenario metadata")
    for step in s["steps"]:
        validate(step["in"], SCHEMA)
        for output in step["out"]:
            validate(output, SCHEMA)
    e = s["expect"]
    timeline = s["timeline"]
    if "SUCCESS_ACK" in timeline:
        commit = timeline.index("COMMIT") if "COMMIT" in timeline else -1
        if commit < 0 or any(i < commit for i, event in enumerate(timeline) if event == "SUCCESS_ACK"):
            raise Invalid("success ACK before durable commit")
    if "ROLLBACK" in timeline and ("COMMIT" in timeline or "SUCCESS_ACK" in timeline):
        raise Invalid("rollback followed by committed outcome")
    if "MEMBER_DENIED" in timeline or "AUTH_DENIED" in timeline:
        if any(event in timeline for event in ("BEGIN", "MESSAGE_INSERTED", "OUTBOX_INSERTED", "COMMIT", "SUCCESS_ACK")):
            raise Invalid("unauthorized persistence")
    if timeline.count("MESSAGE_INSERTED") != timeline.count("OUTBOX_INSERTED"):
        raise Invalid("message/outbox insertion mismatch")
    if s["id"] in ("idempotent-retry", "conflicting-retry", "group-single-message") and timeline.count("MESSAGE_INSERTED") != 1:
        raise Invalid("duplicate logical persistence")
    if timeline:
        observed_success = sum(output["type"] == "message.ack" and output["payload"]["status"] == "committed" for step in s["steps"] for output in step["out"])
        observed_rejected = sum(output["type"] == "message.ack" and output["payload"]["status"] == "rejected" for step in s["steps"] for output in step["out"])
        if observed_success != timeline.count("SUCCESS_ACK") or observed_rejected != timeline.count("REJECTED_ACK"):
            raise Invalid("ACK frames disagree with transaction timeline")
    if e.get("messages", 0) < 0 or e.get("outbox", 0) < 0:
        raise Invalid("negative persistence count")
    if "messages" in e and "outbox" in e and e["messages"] != e["outbox"]:
        raise Invalid("message/outbox mismatch")
    for step in s["steps"]:
        request = step["in"]
        for output in step["out"]:
            if output["type"] in ("auth.ack", "message.ack") and output["requestId"] != request["requestId"]:
                raise Invalid("ACK request identity mismatch")
            if output["type"] == "message.ack" and output["payload"]["status"] == "committed":
                if s["id"] in ("unauthenticated-send", "non-member-send", "rollback-before-ack", "revoked-socket"):
                    raise Invalid("forbidden success ACK")
    if s["id"] == "idempotent-retry" and s["steps"][0]["out"] != s["steps"][1]["out"]:
        raise Invalid("unstable retry")
    if s["id"] == "same-request-different-conversation":
        first, second = [step["out"][0]["payload"] for step in s["steps"]]
        if first["messageId"] == second["messageId"] or first["conversationId"] == second["conversationId"]:
            raise Invalid("conversation identity collision")


def negative_schema_controls():
    base = send()
    mutations = []
    for modify in (
        lambda x: x.update(protocolVersion="2.0"),
        lambda x: x.update(type="message.unknown"),
        lambda x: x.update(extra=1),
        lambda x: x["payload"].update(extra=1),
        lambda x: x["payload"].update(conversationId="not-a-uuid"),
        lambda x: x["payload"]["content"].update(text=""),
        lambda x: x.pop("requestId"),
    ):
        changed = copy.deepcopy(base)
        modify(changed)
        mutations.append(changed)
    bad_ack = ack()
    bad_ack["payload"].pop("messageId")
    mutations.append(bad_ack)
    bad_ack = ack()
    bad_ack["payload"]["seq"] = 0
    mutations.append(bad_ack)
    wrong_auth_error = error_ack("auth.ack", R1, "AUTH_TOKEN_INVALID")
    wrong_auth_error["payload"]["error"]["code"] = "MESSAGE_REQUEST_CONFLICT"
    mutations.append(wrong_auth_error)
    wrong_message_error = error_ack("message.ack", R1, "AUTH_REQUIRED")
    wrong_message_error["payload"]["error"]["code"] = "AUTH_TOKEN_EXPIRED"
    mutations.append(wrong_message_error)
    for changed in mutations:
        try:
            validate(changed, SCHEMA)
        except Invalid:
            continue
        raise Invalid(f"schema accepted invalid mutation: {changed}")
    return len(mutations)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write deterministic golden fixtures")
    args = parser.parse_args()
    lint_schema(SCHEMA)
    expected = fixtures()
    for scenario in expected["scenarios"]:
        check_scenario(scenario)
    count = negative_schema_controls()
    encoded = json.dumps(expected, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        FIXTURE.parent.mkdir(parents=True, exist_ok=True)
        FIXTURE.write_text(encoded, encoding="utf-8", newline="\n")
    elif FIXTURE.read_bytes() != encoded.encode("utf-8"):
        raise Invalid("golden fixture differs from deterministic generator; run --write intentionally")
    actual = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if actual != expected:
        raise Invalid("golden fixture mismatch")
    positives = sum(s["polarity"] == "positive" for s in actual["scenarios"])
    negatives = len(actual["scenarios"]) - positives
    print(f"PASS WSS v1: {positives} positive, {negatives} negative shared Go/Java scenarios; {count} schema mutations rejected")


if __name__ == "__main__":
    try:
        main()
    except (Invalid, OSError, KeyError, ValueError) as exc:
        print(f"FAIL WSS v1: {exc}", file=sys.stderr)
        sys.exit(1)
