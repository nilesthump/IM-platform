import subprocess,json,hashlib
from pathlib import Path
r=Path(r"H:/IM-platform/.git/worktrees/IM-platform5/sync-final-candidate-review/actual-main")
def gh(*a):return subprocess.check_output(["gh",*a])
p=json.loads(gh("api","repos/nilesthump/IM-platform/actions/runs/37122484526"))
assert p["head_sha"]=="c2ff0502fdad80f463abe038a960ca1b798e6d7a" and p["status"]=="completed" and p["conclusion"]=="success",(p["status"],p["conclusion"])
j=json.loads(gh("api","repos/nilesthump/IM-platform/actions/runs/37122484526/jobs?per_page=100"))
expected={"classify","architecture","source_go","source_java","go","java","web","desktop","mobile","shared","compatibility","deploy","gate"}
assert len(j["jobs"])==13 and {x["name"] for x in j["jobs"]}==expected
assert all(x["status"]=="completed" and x["conclusion"]=="success" and x["steps"] and all(y["status"]=="completed" and y["conclusion"]=="success" for y in x["steps"]) for x in j["jobs"])
(r/"provider.json").write_text(json.dumps(dict(run=p,jobs=j),ensure_ascii=False),encoding="utf8")
manifest=[]
for name in ["classify","architecture","shared","desktop","mobile","go","deploy"]:
 x=next(x for x in j["jobs"] if x["name"]==name);b=gh("run","view","37122484526","--job",str(x["id"]),"--log","--repo","nilesthump/IM-platform")
 (r/(name+".log")).write_bytes(b);manifest.append(dict(job=name,jobid=x["id"],size=len(b),sha256=hashlib.sha256(b).hexdigest()))
(r/"logs-manifest.json").write_text(json.dumps(manifest,indent=2))
print("PASS independent live provider exact c2ff: 13 completed SUCCESS jobs,",sum(len(x["steps"]) for x in j["jobs"]),"all steps SUCCESS, seven exact-job actualmain logs downloaded; no skipped required jobs")
