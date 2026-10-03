from pathlib import Path
import json,subprocess,re,hashlib
r=Path(r"H:/IM-platform/.git/worktrees/IM-platform5/sync-final-candidate-review/actual-main")
d=json.loads((r/"provider.json").read_text());assert d["run"]["head_sha"]=="c2ff0502fdad80f463abe038a960ca1b798e6d7a"
for m in json.loads((r/"logs-manifest.json").read_text()):
 b=(r/(m["job"]+".log")).read_bytes();assert hashlib.sha256(b).hexdigest()==m["sha256"] and len(b)==m["size"]
def log(n):return (r/(n+".log")).read_text(encoding="utf8",errors="replace")
c=log("classify");assert "BASE_SHA: a0304fcc7be18b87f5986d014849d6b48b96a071" in c and "HEAD_SHA: c2ff0502fdad80f463abe038a960ca1b798e6d7a" in c
q=json.loads(subprocess.check_output(["C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe","-B","ci/classify.py","--base","a0304fcc7be18b87f5986d014849d6b48b96a071","--head","c2ff0502fdad80f463abe038a960ca1b798e6d7a"]))
assert all(q["jobs"].values())
for k in q["jobs"]:assert re.search('"'+k+'": true',c)
s=log("shared")
for needle in ["PASS: canonical external refs, HTTPS/Auth/error/pagination binding and official OpenAPI 3.1 lint", "Ran 4 tests", "PASS WSS v1", "79 distinct Go/Java outcome artifacts", "mutation_regressions=15"]:assert needle in s,needle
# four test groups contain 13 document mutations in identical independently reviewed source, tests truly ran/OK
src=Path("tests/contract/test_sync_transport.py").read_text();assert src.count("lambda d:")==13
assert re.search(r"HTTP, WSS, Sync and Plugin contracts.*Z OK",s)
des=log("desktop")
for needle in ['"engine":"actual SQLx SQLite"','"canonicalCases":13','"assertions":141','PASS: actual SQLx + builtin WSS TLS send','1 passed; 0 failed']:assert needle in des,needle
mo=log("mobile")
for needle in ['api-level: 34','engine=actual Android SDK SQLite','canonicalCases=13','assertions=137','engine=actual Android SDK SQLite + standard verified TLS WSS + StateFlow','assertions=66','result=PASS','sdkInt=34','phase=data-clear']:assert needle in mo,needle
go=log("go")
for needle in ['postgres service is healthy','DB_TEST_ENABLE: 1','go test -race -count=1 ./...','im-platform/backend/go/tests']:assert needle in go,needle
de=log("deploy")
for needle in ['PASS TLS: trusted CA/CERT_REQUIRED/hostname HTTPS+WSS','PASS fixtures: HTTPS register/login/search/friend unique DIRECT; WSS hello/SQL durable ACK/one Outbox/NATS recipient','PASS revocation:','no runtime skips','DEFERRED_BY_HUMAN: friend-add-authorization-denied only (ADR-0004); not counted PASS']:assert needle in de,needle
ar=log("architecture");assert 'Ran 53 tests' in ar and 'violations=0' in ar
print("PASS: independently read actual c2ff full a030..c2ff flags, all selected; 13 document mutations inside true four-group test execution, livePG/race/TLS and actualSQLx/AndroidAPI34 evidence; known ADR0004 deferred denial explicitly not PASS")
