from pathlib import Path
import subprocess,json,hashlib,fnmatch,importlib.util,copy
root=Path.cwd();base="a0304fcc7be18b87f5986d014849d6b48b96a071";head="b8200783ea3eadc1ed4e4050238f051a7ab708b3"
assert subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip()==head
assert subprocess.check_output(["git","rev-parse","--show-toplevel"]).decode().strip().replace("\\","/")=="H:/.codex/worktrees/sync-resume/IM-platform"
assert not subprocess.check_output(["git","status","--porcelain=v1"])
task=(root/"spec/tasks/review/LOOP1-SYNC-TRANSPORT-001.md").read_text(encoding="utf8")
paths=[x[2:] for x in task.split("# Allowed Paths\n",1)[1].split("# Acceptance",1)[0].splitlines() if x.startswith("- ")]
changed=subprocess.check_output(["git","diff","--name-only",base,head]).decode().splitlines()
assert all(any(fnmatch.fnmatch(f,p) for p in paths) for f in changed),[f for f in changed if not any(fnmatch.fnmatch(f,p) for p in paths)]
for directory in ["backend","clients","contracts/database","contracts/websocket","contracts/errors","contracts/plugin-api","ci"]:
 assert not subprocess.check_output(["git","diff","--name-only",base,head,"--",directory])
count=0
folder=root/"spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001/recovery-fix"
for name,prefix in [("import-manifest.json",folder),("research-import-manifest.json",folder/"research")]:
 for row in json.loads((folder/name).read_text()):
  b=(prefix/row["path"]).read_bytes();assert len(b)==row["size"] and hashlib.sha256(b).hexdigest()==row["sha256"],row;count+=1
# Compare every previously committed artifact with the latest candidate; archival increments add, never edit.
old="8c672a22c5fb9fd640791117c919e1b5a1b8bf69"
oldfiles=subprocess.check_output(["git","ls-tree","-r","--name-only",old,"--","spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001","spec/progress/evidence/LOOP1-SYNC-001"]).decode().splitlines()
for f in oldfiles:
 assert subprocess.check_output(["git","-c","core.longpaths=true","show",old+":"+f])==(root/f).read_bytes(),f
sp=importlib.util.spec_from_file_location("v",root/"tools/verify_sync_transport.py");v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
r=dict(syncVersion="1.0",type="sync.user.request",requestId="40000000-0000-4000-8000-000000000001",cursor="0",limit=10**100)
p=dict(syncVersion="1.0",type="sync.user.page",requestId=r["requestId"],events=[],nextCursor="0",hasMore=False)
def rejects(q,z):
 try:v.check_page("user",q,z)
 except v.Invalid:return
 raise AssertionError((q,z))
for k,x in [("unknown",1),("syncVersion","2.0"),("requestId","bad"),("cursor",""),("limit","100")]:
 q=dict(r);q[k]=x;rejects(q,p)
for k,x in [("unknown",1),("hasMore",1),("syncVersion","2.0"),("nextCursor","")]:
 z=dict(p);z[k]=x;rejects(r,z)
assert r["limit"]==10**100
print("PASS: exact clean root/head; allowed scope",len(changed),"files; zero product/checker/schema edits;",count,"archive manifest bytes verified;",len(oldfiles),"old evidence files unchanged; 9 independent invalid-field probes rejected, exact huge input preserved")
