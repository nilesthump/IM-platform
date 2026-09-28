#!/usr/bin/env python3
"""Offline schema and deterministic Sync/Plugin v1 fixture verifier."""
import copy
import datetime
import json
import pathlib
import runpy
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
SYNC = json.loads((ROOT / "websocket/sync-v1.schema.json").read_text(encoding="utf-8"))
PLUGIN = json.loads((ROOT / "plugin-api/v1.schema.json").read_text(encoding="utf-8"))
POLICY = json.loads((ROOT / "plugin-api/policy-v1.json").read_text(encoding="utf-8"))
FIXTURE = ROOT / "fixtures/sync-plugin/golden.json"
ALLOWED = {"$schema", "$id", "title", "description", "$defs", "$ref", "type", "const", "enum", "oneOf", "allOf", "required", "properties", "additionalProperties", "items", "minLength", "maxLength", "minimum", "maximum", "format", "maxItems", "minItems", "uniqueItems"}


class Invalid(Exception):
    pass


def lint(node, root, path="$", stack=()):
    if not isinstance(node, dict) or set(node) - ALLOWED:
        raise Invalid(f"{path}: malformed or unsupported schema keywords {set(node) - ALLOWED if isinstance(node, dict) else node}")
    if "type" in node and node["type"] not in ("object", "array", "string", "integer", "boolean"):
        raise Invalid(f"{path}: unsupported type")
    if "format" in node and node["format"] not in ("uuid", "date-time"):
        raise Invalid(f"{path}: unsupported format")
    for key in ("$schema", "$id", "title", "description", "format"):
        if key in node and not isinstance(node[key], str):
            raise Invalid(f"{path}.{key}: expected string")
    for key in ("$defs", "properties"):
        if key in node and not isinstance(node[key], dict):
            raise Invalid(f"{path}.{key}: expected object")
    if "required" in node and (not isinstance(node["required"], list) or any(not isinstance(x, str) for x in node["required"]) or len(node["required"]) != len(set(node["required"]))):
        raise Invalid(f"{path}.required: expected unique strings")
    for key in ("oneOf", "allOf"):
        if key in node and (not isinstance(node[key], list) or not node[key]):
            raise Invalid(f"{path}.{key}: expected nonempty array")
    if "enum" in node and (not isinstance(node["enum"], list) or not node["enum"]):
        raise Invalid(f"{path}.enum: expected nonempty array")
    for key in ("minimum", "maximum", "minLength", "maxLength", "minItems", "maxItems"):
        if key in node and (type(node[key]) is not int or node[key] < 0):
            raise Invalid(f"{path}.{key}: expected nonnegative integer")
    for key in ("additionalProperties", "uniqueItems"):
        if key in node and type(node[key]) is not bool:
            raise Invalid(f"{path}.{key}: expected boolean")
    if "$ref" in node:
        ref = node["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/$defs/") or ref[8:] not in root.get("$defs", {}):
            raise Invalid(f"{path}: unresolved local reference")
    for group in ("$defs", "properties"):
        for key, child in node.get(group, {}).items():
            lint(child, root, f"{path}.{group}.{key}", stack)
    if "items" in node:
        lint(node["items"], root, f"{path}.items", stack)
    for group in ("oneOf", "allOf"):
        for i, child in enumerate(node.get(group, [])):
            lint(child, root, f"{path}.{group}[{i}]", stack)


def validate(value, schema, root, path="$"):
    if "$ref" in schema:
        return validate(value, root["$defs"][schema["$ref"][8:]], root, path)
    for child in schema.get("allOf", []):
        validate(value, child, root, path)
    if "oneOf" in schema:
        matches = 0
        for child in schema["oneOf"]:
            try:
                validate(value, child, root, path)
                matches += 1
            except Invalid:
                pass
        if matches != 1:
            raise Invalid(f"{path}: oneOf matched {matches} branches")
    if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
        raise Invalid(f"{path}: const mismatch")
    if "enum" in schema and value not in schema["enum"]:
        raise Invalid(f"{path}: enum mismatch")
    kind = schema.get("type")
    if kind == "object":
        if not isinstance(value, dict):
            raise Invalid(f"{path}: expected object")
        if set(schema.get("required", [])) - set(value):
            raise Invalid(f"{path}: missing {set(schema['required']) - set(value)}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and set(value) - set(props):
            raise Invalid(f"{path}: unknown properties {set(value)-set(props)}")
        for key in set(value) & set(props):
            validate(value[key], props[key], root, f"{path}.{key}")
    elif kind == "array":
        if not isinstance(value, list) or len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", sys.maxsize):
            raise Invalid(f"{path}: invalid array")
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise Invalid(f"{path}: duplicate items")
        for i, child in enumerate(value):
            validate(child, schema["items"], root, f"{path}[{i}]")
    elif kind == "string":
        if not isinstance(value, str) or not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", sys.maxsize):
            raise Invalid(f"{path}: invalid string")
        if schema.get("format") == "uuid":
            try:
                if str(uuid.UUID(value)) != value:
                    raise ValueError()
            except ValueError as exc:
                raise Invalid(f"{path}: invalid UUID") from exc
        if schema.get("format") == "date-time":
            try:
                if datetime.datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is None:
                    raise ValueError()
            except ValueError as exc:
                raise Invalid(f"{path}: invalid timestamp") from exc
    elif kind == "integer":
        if type(value) is not int or not schema.get("minimum", -sys.maxsize) <= value <= schema.get("maximum", sys.maxsize):
            raise Invalid(f"{path}: invalid integer")
    elif kind == "boolean" and type(value) is not bool:
        raise Invalid(f"{path}: expected boolean")


def run(case):
    state = {"cursor": "0", "contiguous": 0, "messages": {}, "conversations": {}, "local": {}, "sideEffects": 0, "auditAttempts": 0, "activeVersion": "1.0.0", "oldVersionServed": True, "snapshotRestored": False, "dataPreserved": True, "autoDisabled": False, "failureCount": 0, "last": "NONE"}
    state.update(copy.deepcopy(case.get("initial", {})))
    seen_actions = set()
    seen_events = set()
    artifact_hashes = {}
    request_messages = {}
    for step in case["steps"]:
        op = step["op"]
        if op == "sync.user":
            page = step["page"]
            validate(page, SYNC, SYNC)
            if page["type"] != "sync.user.page":
                raise Invalid("sync.user requires user page")
            if step.get("fault") == "before_commit":
                state["last"] = "ROLLED_BACK"
                continue
            for event in page["events"]:
                if event["kind"] not in ("friend.changed", "conversation.changed", "membership.changed", "plugin.changed"):
                    raise Invalid("message event in user cursor")
                seen_events.add(event["eventId"])
            state["cursor"] = page["nextCursor"]
            state["last"] = "APPLIED"
        elif op == "sync.message":
            msg = step["message"]
            validate(msg, SYNC["$defs"]["Message"], SYNC)
            if step.get("fault") == "before_commit":
                state["last"] = "ROLLED_BACK"
                continue
            if msg["conversationId"] != case.get("conversationId", msg["conversationId"]):
                raise Invalid("wrong conversation")
            conv = state["conversations"].setdefault(msg["conversationId"], {"contiguous": 0, "messages": {}})
            key = str(msg["seq"])
            prior = conv["messages"].get(key)
            if prior and prior != msg["messageId"]:
                raise Invalid("sequence collision")
            identity = msg["conversationId"] + "/" + msg["requestId"]
            if identity in request_messages and request_messages[identity] != msg["messageId"]:
                raise Invalid("request identity collision")
            request_messages[identity] = msg["messageId"]
            conv["messages"][key] = msg["messageId"]
            while str(conv["contiguous"] + 1) in conv["messages"]:
                conv["contiguous"] += 1
            state["messages"] = conv["messages"]
            state["contiguous"] = conv["contiguous"]
            state["local"][identity] = "SENT"
            state["last"] = "APPLIED"
        elif op == "local.failed":
            identity = step["conversationId"] + "/" + step["requestId"]
            if state["local"].get(identity) != "SENT":
                state["local"][identity] = "FAILED"
            state["last"] = state["local"][identity]
        elif op == "plugin.call":
            call = step["call"]
            validate(call, PLUGIN, PLUGIN)
            typ = call["type"]
            cap = POLICY["capabilityForType"][typ]
            field = {"event.subscribe": "event", "query": "query", "action": "action", "ui.host": "slot"}[typ]
            permission = {"event.subscribe": "permissionForEvent", "query": "permissionForQuery", "action": "permissionForAction", "ui.host": "permissionForSlot"}[typ]
            required = POLICY[permission][call[field]]
            allowed = cap in step.get("capabilities", []) and required in step.get("permissions", []) and not step.get("directAccess", False)
            if typ == "query" and (call["pageSize"] > POLICY["maxQueryPageSize"] or step.get("mutates", False)):
                allowed = False
            if typ == "action":
                state["auditAttempts"] += 1
                allowed = allowed and step.get("authorizedAtExecution", False)
                if allowed:
                    identity = call["pluginId"] + "/" + call["conversationId"] + "/" + call["requestId"]
                    if identity not in seen_actions:
                        state["sideEffects"] += 1
                        seen_actions.add(identity)
            state["last"] = "ALLOWED" if allowed else "DENIED"
        elif op == "plugin.manifest":
            validate(step["manifest"], PLUGIN, PLUGIN)
            if step["manifest"]["type"] != "manifest":
                raise Invalid("expected Plugin manifest")
            state["last"] = "VALID"
        elif op == "plugin.artifact":
            artifact = step["artifact"]
            validate(artifact, PLUGIN, PLUGIN)
            identity = artifact["pluginId"] + "/" + artifact["version"]
            hashes = [artifact[k] for k in ("packageHash", "backendHash", "rendererHash")]
            checks = all(artifact[k] for k in POLICY["rendererChecks"] if k != "packageHash")
            checks = checks and step.get("hashValid", False) and step.get("signatureValid", False) and artifact["sandbox"] in POLICY["rendererSandboxes"]
            checks = checks and step.get("backendVersion", artifact["version"]) == artifact["version"] and step.get("rendererVersion", artifact["version"]) == artifact["version"]
            if identity in artifact_hashes and artifact_hashes[identity] != hashes:
                checks = False
            if checks:
                artifact_hashes[identity] = hashes
            state["last"] = "VERIFIED" if checks else "REJECTED"
        elif op == "plugin.wasm":
            resource = step.get("resource")
            violation = resource in POLICY["wasmDeniedResources"] or (resource in POLICY["wasmLimitedResources"] and step.get("overLimit", False)) or step.get("timeout", False) or step.get("panic", False)
            if violation:
                state["failureCount"] += 1
                if state["failureCount"] >= POLICY["autoDisableAfterConsecutiveFailures"]:
                    state["autoDisabled"] = True
                state["last"] = "AUTO_DISABLED" if state["autoDisabled"] else "DENIED"
            elif state["autoDisabled"]:
                state["last"] = "DENIED"
            else:
                state["failureCount"] = 0
                state["last"] = "ALLOWED"
        elif op == "plugin.renderer_runtime":
            sandbox = step.get("sandbox")
            resource = step.get("resource")
            permitted = sandbox in POLICY["rendererSandboxes"] and step.get("throughBridge") is True and resource not in ("database", "core_internal", "server_file", "os_resource", "arbitrary_network")
            state["last"] = "ALLOWED" if permitted else "DENIED"
        elif op == "plugin.upgrade":
            stages = POLICY["upgradeStages"]
            failed = step.get("failAt")
            if failed is not None and failed not in stages:
                raise Invalid("unknown upgrade stage")
            if step.get("backendVersion") != step.get("rendererVersion"):
                state["last"] = "REJECTED"
            elif failed:
                state["snapshotRestored"] = True
                state["last"] = "ROLLED_BACK"
            else:
                state["activeVersion"] = step["backendVersion"]
                state["oldVersionServed"] = False
                state["last"] = "SWITCHED"
        elif op == "plugin.lifecycle":
            action = step["action"]
            if action in ("DISABLE", "UNINSTALL"):
                state["last"] = "DISABLED" if action == "DISABLE" else "RETAINED"
            elif action == "PURGE":
                if all(step.get(k) is True for k in POLICY["purgeRequirements"]):
                    state["dataPreserved"] = False
                    state["last"] = "PURGED"
                else:
                    state["last"] = "DENIED"
            else:
                raise Invalid("unknown lifecycle action")
        else:
            raise Invalid(f"unknown operation {op}")
    return {key: state[key] for key in case["expect"]}


def verify():
    for schema in (SYNC, PLUGIN):
        lint(schema, schema)
    fixtures = json.loads(FIXTURE.read_text(encoding="utf-8"))
    source_cases = runpy.run_path(str(FIXTURE.parent / "generate.py"))["cases"]
    if fixtures.get("cases") != source_cases:
        raise Invalid("golden vectors differ from deterministic source")
    if fixtures.get("fixtureVersion") != "1.0" or fixtures.get("profiles") != ["go", "java"]:
        raise Invalid("fixture version or profile list mismatch")
    cases = fixtures["cases"]
    if len({c["id"] for c in cases}) != len(cases):
        raise Invalid("duplicate case IDs")
    covered = set()
    positives = negatives = 0
    for case in cases:
        if case["polarity"] not in ("positive", "negative") or not case["rules"]:
            raise Invalid(f"{case['id']}: invalid polarity or missing rules")
        covered.update(case["rules"])
        positives += case["polarity"] == "positive"
        negatives += case["polarity"] == "negative"
        for profile in fixtures["profiles"]:
            if case.get("expectError"):
                try:
                    run(copy.deepcopy(case))
                except Invalid:
                    continue
                raise Invalid(f"{profile}/{case['id']}: expected contract rejection")
            actual = run(copy.deepcopy(case))
            if actual != case["expect"]:
                raise Invalid(f"{profile}/{case['id']}: expected {case['expect']}, got {actual}")
    required = {f"SP-A-{i:03d}" for i in range(1, 14)}
    if not required <= covered:
        raise Invalid(f"missing acceptance coverage {required-covered}")
    # Controls prove schema and scenario oracle reject malformed or wrong outcomes.
    bad = copy.deepcopy(cases[0]); bad["expect"]["last"] = "NEVER"
    if run(bad) == bad["expect"]:
        raise Invalid("outcome mutation accepted")
    malformed = {"syncVersion":"1.0","type":"sync.user.page","requestId":"not-a-uuid","events":[],"nextCursor":"1","hasMore":False}
    try:
        validate(malformed, SYNC, SYNC)
    except Invalid:
        pass
    else:
        raise Invalid("malformed Sync UUID accepted")
    print(f"PASS: Sync/Plugin v1 schemas, {len(cases)} shared Go/Java cases ({positives} positive, {negatives} negative), SP-A-001..013, 2 mutation controls")


if __name__ == "__main__":
    try:
        verify()
    except (Invalid, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
