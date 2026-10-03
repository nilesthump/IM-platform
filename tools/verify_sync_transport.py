"""Bounded Sync HTTPS binding checks, reusing canonical schema and official OAI lint."""
import argparse
import json
from pathlib import Path
import runpy
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts/http/sync.openapi.json"
ORACLE = runpy.run_path(str(ROOT / "contracts/plugin-api/verify.py"))
Invalid = ORACLE["Invalid"]
SYNC = ORACLE["SYNC"]
BINDING = {"initialCursor":"0","cursorOwnership":"authenticated-user","cursorComparison":"opaque-equality-only","effectiveLimitCap":100,"limitPolicy":"accept-all-positive-integers-cap-before-conversion","authentication":"authoritative-session-each-request","authorization":"core-user-scope-and-conversation-membership","correlation":"decoded-valid-body-requestId-echo-else-server-uuid","emptyUserPage":"retain-request-cursor-hasMore-false","userOrder":"stable-committed-prefix","userNextCursor":"last-event-cursor","conversationOrder":"ascending-gap-free-afterSeq","hasMore":"additional-committed-item-exists","failure":"non-2xx-never-a-sync-page","queryParameters":"none","runtimeAcceptance":"deferred-until-human-approved-Go-plan","afterSeqPolicy":"accept-all-nonnegative-integers-above-storage-head-empty"}

def require(ok, why):
    if not ok:
        raise Invalid(why)

def resolve(ref):
    path, fragment = ref.split("#", 1)
    value = json.loads((CONTRACT.parent / path).resolve().read_text(encoding="utf8"))
    for part in fragment.lstrip("/").split("/"):
        value = value[part.replace("~1", "/").replace("~0", "~")]
    return value

def check_document(doc):
    require(doc["openapi"] == "3.1.0", "OpenAPI version")
    require(doc["servers"] == [{"url": "https://api.example.invalid"}], "HTTPS-only servers")
    require(doc["security"] == [{"bearerAuth": []}], "authenticated default")
    require(doc["x-sync-binding"] == BINDING, "binding semantics changed")
    require(doc["components"] == {"securitySchemes": {"bearerAuth": {"$ref": "./auth-user-friend.openapi.json#/components/securitySchemes/bearerAuth"}}}, "reuse sole bearer authority")
    require(resolve(doc["components"]["securitySchemes"]["bearerAuth"]["$ref"])["scheme"] == "bearer", "bearer reference unresolved")
    require(set(doc["paths"]) == {"/v1/sync/user", "/v1/sync/conversation"}, "exact two routes")
    auth = ["AUTH_REQUIRED", "AUTH_TOKEN_INVALID", "AUTH_TOKEN_EXPIRED", "AUTH_SESSION_REVOKED", "AUTH_SESSION_EPOCH_STALE", "AUTH_CLIENT_TYPE_MISMATCH"]
    catalog = resolve("../errors/http-errors.schema.json#/$defs/ErrorCode")["enum"]
    for kind, shape in (("user", "User"), ("conversation", "Conversation")):
        path = doc["paths"]["/v1/sync/" + kind]
        require(set(path) == {"post"}, "POST only")
        op = path["post"]
        require(op["security"] == [{"bearerAuth": []}] and not op.get("parameters"), "no query/body authentication substitute")
        require(op["requestBody"] == {"required": True, "content": {"application/json": {"schema": {"$ref": "../websocket/sync-v1.schema.json#/$defs/" + shape + "Request"}}}}, "exact canonical required request")
        expected = {"400": ["VALIDATION_FAILED"], "401": auth, "426": ["PROTOCOL_VERSION_UNSUPPORTED"]}
        if kind == "conversation":
            expected["403"] = ["AUTHORIZATION_DENIED"]
        require(set(op["responses"]) == {"200"} | set(expected), "exact statuses")
        success = op["responses"]["200"]
        require(success["content"] == {"application/json": {"schema": {"$ref": "../websocket/sync-v1.schema.json#/$defs/" + shape + "Page"}}}, "exact canonical page")
        require(success["headers"]["Cache-Control"]["schema"] == {"type": "string", "const": "no-store"}, "no-store")
        for status, codes in expected.items():
            response = op["responses"][status]
            require(response["headers"]["Cache-Control"]["schema"] == {"type": "string", "const": "no-store"}, "failure no-store")
            require(response["x-error-codes"] == codes and set(codes) <= set(catalog), "catalogue/status mapping")
            require(response["content"] == {"application/json": {"schema": {"$ref": "../errors/http-errors.schema.json#/$defs/ErrorResponse"}}}, "canonical error ref")
            resolve(response["content"]["application/json"]["schema"]["$ref"])
        for name in (shape + "Request", shape + "Page"):
            require(resolve("../websocket/sync-v1.schema.json#/$defs/" + name) == SYNC["$defs"][name], "external shape")
    ORACLE["lint"](SYNC, SYNC)

def check_page(kind, request, page):
    shape = "User" if kind == "user" else "Conversation"
    # Existing offline oracle uses a host-int ceiling absent from the public schema.
    # Validate unbounded request scalars exactly, then reuse it for every other field.
    checked = dict(request)
    require(type(request.get("limit")) is int and request["limit"] >= 1, "positive exact integer limit")
    checked["limit"] = min(request["limit"], BINDING["effectiveLimitCap"])
    if kind == "conversation":
        require(type(request.get("afterSeq")) is int and request["afterSeq"] >= 0, "nonnegative exact afterSeq")
        checked["afterSeq"] = min(request["afterSeq"], 2**63-1)
    ORACLE["validate"](checked, SYNC["$defs"][shape + "Request"], SYNC)
    ORACLE["validate"](page, SYNC["$defs"][shape + "Page"], SYNC)
    require(page["requestId"] == request["requestId"], "success correlation")
    items = page["events" if kind == "user" else "messages"]
    require(len(items) <= min(request["limit"], BINDING["effectiveLimitCap"]), "bounded page")
    require(not page["hasMore"] or bool(items), "hasMore needs progress")
    if kind == "user":
        if not items:
            require(not page["hasMore"] and page["nextCursor"] == request["cursor"], "empty retains cursor")
        else:
            require(page["nextCursor"] == items[-1]["cursor"] and page["nextCursor"] != request["cursor"], "last cursor progress")
            require(len({x["eventId"] for x in items}) == len(items) and len({x["cursor"] for x in items}) == len(items), "unique event identity")
            require(all(x["cursor"] != request["cursor"] for x in items), "no previous cursor replay")
    else:
        require(page["conversationId"] == request["conversationId"], "page account/conversation isolation")
        for index, message in enumerate(items):
            require(message["conversationId"] == request["conversationId"] and message["seq"] == request["afterSeq"] + index + 1, "gap-free conversation")

def check_error(kind, request, status, error):
    doc = json.loads(CONTRACT.read_text(encoding="utf8"))
    mapping = doc["paths"]["/v1/sync/" + kind]["post"]["responses"]
    require(str(status) in mapping and status != 200, "catalogued failure status")
    root = json.loads((ROOT / "contracts/errors/http-errors.schema.json").read_text(encoding="utf8"))
    ORACLE["validate"](error, root, root)
    require(error["error"]["code"] in mapping[str(status)]["x-error-codes"], "error status/code")
    ORACLE["validate"](error["requestId"], SYNC["$defs"]["Id"], SYNC)
    if request is not None:
        require(error["requestId"] == request["requestId"], "valid decoded failure correlation")

def structural_lint(doc, node=None):
    node = node or shutil.which("node")
    require(bool(node), "Node required for existing official OAI structural lint")
    result = subprocess.run([node, str(ROOT / "contracts/http/check-openapi-3.1.js")], input=json.dumps(doc).encode(), capture_output=True)
    require(result.returncode == 0, result.stderr.decode(errors="replace"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--node")
    args = parser.parse_args()
    doc = json.loads(CONTRACT.read_text(encoding="utf8"))
    check_document(doc)
    structural_lint(doc, args.node)
    print("PASS: canonical external refs, HTTPS/Auth/error/pagination binding and official OpenAPI 3.1 lint; no runtime acceptance claimed")

if __name__ == "__main__":
    main()
