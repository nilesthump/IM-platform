import pathlib,json,hashlib,subprocess,stat
d=json.loads(pathlib.Path("H:/IM-platform/.git/worktrees/IM-platform5/sync-transport-coordinator-research/main-before.json").read_text())
for e in d["entries"]:
 f=pathlib.Path("H:/IM-platform")/e["path"]
 if f.is_file():
  s=f.stat(); assert s.st_size==e["size"],"size changed"
  assert hashlib.sha256(f.read_bytes()).hexdigest()==e["sha256"],"bytes changed"
 elif e["sha256"] not in (None,"unavailable"): raise AssertionError("file missing")
assert subprocess.check_output(["git","-C","H:/IM-platform","rev-parse","HEAD"],text=True).strip()==d["head"]
print("PASS all",len(d["entries"]),"main snapshot entries preserve content/size and HEAD; no unknown contents printed")
