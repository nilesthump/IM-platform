import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("sync_transport", ROOT / "tools/verify_sync_transport.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
R = "40000000-0000-4000-8000-000000000001"
C = "30000000-0000-4000-8000-000000000001"
E = "50000000-0000-4000-8000-000000000001"
U = "10000000-0000-4000-8000-000000000001"

class SyncTransportTests(unittest.TestCase):
    def test_binding_mutations(self):
        baseline = json.loads(v.CONTRACT.read_text(encoding="utf8"))
        v.check_document(baseline)
        mutations = [
            lambda d: d["servers"].__setitem__(0, {"url": "http://api.example.invalid"}),
            lambda d: d.__setitem__("security", []),
            lambda d: d["x-sync-binding"].__setitem__("effectiveLimitCap", 0),
            lambda d: d["x-sync-binding"].__setitem__("cursorOwnership", "global"),
            lambda d: d["x-sync-binding"].__setitem__("correlation", "random"),
            lambda d: d["paths"]["/v1/sync/user"]["post"].__setitem__("security", []),
            lambda d: d["paths"]["/v1/sync/user"]["post"]["requestBody"].__setitem__("required", False),
            lambda d: d["paths"]["/v1/sync/user"]["post"]["responses"]["200"]["content"]["application/json"]["schema"].__setitem__("$ref", "../websocket/sync-v1.schema.json#/$defs/ConversationPage"),
            lambda d: d["paths"]["/v1/sync/conversation"]["post"]["responses"].pop("403"),
            lambda d: d["paths"]["/v1/sync/user"]["post"]["responses"]["401"].__setitem__("x-error-codes", ["INTERNAL_ERROR"]),
            lambda d: d["paths"]["/v1/sync/user"].__setitem__("get", {}),
        ]
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                d = copy.deepcopy(baseline)
                mutation(d)
                with self.assertRaises(v.Invalid):
                    v.check_document(d)

    def test_user_pages_and_negative_controls(self):
        request = dict(syncVersion="1.0", type="sync.user.request", requestId=R, cursor="0", limit=10**100)
        event = dict(eventId=E, cursor="opaque-account-event", kind="friend.changed", subjectId=U, revision=1)
        page = dict(syncVersion="1.0", type="sync.user.page", requestId=R, events=[event], nextCursor=event["cursor"], hasMore=False)
        v.check_page("user", request, page)
        empty = dict(page, events=[], nextCursor="0")
        v.check_page("user", request, empty)
        mutations = [
            lambda p: p.__setitem__("requestId", E),
            lambda p: p.__setitem__("nextCursor", "0"),
            lambda p: p.__setitem__("events", p["events"] * 101),
            lambda p: p["events"][0].__setitem__("kind", "message.created"),
            lambda p: p["events"][0].__setitem__("cursor", "0"),
        ]
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                p = copy.deepcopy(page); mutation(p)
                with self.assertRaises(v.Invalid): v.check_page("user", request, p)
        with self.assertRaises(v.Invalid): v.check_page("user", request, dict(empty, hasMore=True))
        with self.assertRaises(v.Invalid): v.check_page("user", request, dict(empty, nextCursor=event["cursor"]))
        for limit in (0, -1, True, 1.5):
            with self.assertRaises(v.Invalid): v.check_page("user", dict(request, limit=limit), empty)

    def test_conversation_gap_and_isolation(self):
        request = dict(syncVersion="1.0", type="sync.conversation.request", requestId=R, conversationId=C, afterSeq=0, limit=2)
        message = dict(conversationId=C, seq=1, messageId=E, senderId=U, requestId=R, createdAt="2026-10-03T00:00:00Z", content=dict(kind="TEXT", text="test"))
        page = dict(syncVersion="1.0", type="sync.conversation.page", requestId=R, conversationId=C, messages=[message], hasMore=True)
        v.check_page("conversation", request, page)
        v.check_page("conversation", request, dict(page, messages=[], hasMore=False))
        v.check_page("conversation", dict(request, afterSeq=10**100), dict(page, messages=[], hasMore=False))
        for field, value in (("seq", 2), ("conversationId", E)):
            p = copy.deepcopy(page); p["messages"][0][field] = value
            with self.assertRaises(v.Invalid): v.check_page("conversation", request, p)
        with self.assertRaises(v.Invalid): v.check_page("conversation", request, dict(page, messages=[]))

    def test_catalogued_auth_error_correlation(self):
        request = dict(requestId=R)
        v.check_error("user", None, 400, dict(error=dict(code="VALIDATION_FAILED", message="Rejected"), requestId=R))
        with self.assertRaises(v.Invalid):
            v.check_error("user", None, 400, dict(error=dict(code="VALIDATION_FAILED", message="Rejected"), requestId="invalid"))
        for status, code in ((401, "AUTH_REQUIRED"), (401, "AUTH_SESSION_REVOKED"), (400, "VALIDATION_FAILED"), (426, "PROTOCOL_VERSION_UNSUPPORTED")):
            v.check_error("user", request, status, dict(error=dict(code=code, message="Rejected"), requestId=R))
        v.check_error("conversation", request, 403, dict(error=dict(code="AUTHORIZATION_DENIED", message="Rejected"), requestId=R))
        for status, code, rid in ((401, "AUTH_REQUIRED", E), (401, "AUTHORIZATION_DENIED", R), (500, "INTERNAL_ERROR", R)):
            with self.assertRaises(v.Invalid):
                v.check_error("user", request, status, dict(error=dict(code=code, message="Rejected"), requestId=rid))

if __name__ == "__main__":
    unittest.main()
