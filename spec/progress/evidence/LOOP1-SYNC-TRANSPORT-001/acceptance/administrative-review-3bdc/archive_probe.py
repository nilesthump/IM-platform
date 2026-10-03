import pathlib,json,hashlib,subprocess
base=pathlib.Path("spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001")
m=json.loads((base/"independent-review-archive.json").read_text(encoding="utf8")); src=pathlib.Path(m["source"]); dst=base/"independent-review-57404dcc"
files={str(x.relative_to(dst)).replace("\\","/") for x in dst.rglob("*") if x.is_file()}; assert files==set(m["files"]),(files,set(m["files"]))
for f,h in m["files"].items():
 a=(src/f).read_bytes(); b=(dst/f).read_bytes(); assert a==b and hashlib.sha256(a).hexdigest()==h,f
changed=subprocess.check_output(["git","diff","--name-only","57404dcc..HEAD"],text=True).splitlines()
assert all(f in ("spec/progress/current.md","spec/tasks/review/LOOP1-SYNC-TRANSPORT-001.md") or f.startswith(str(base).replace("\\","/")+"/") for f in changed),changed
assert not subprocess.check_output(["git","diff","--name-only","57404dcc..HEAD","--","contracts",".github","tools","tests","backend","clients","spec/architecture"],text=True).strip()
assert len(list(pathlib.Path("spec/tasks").glob("*/LOOP1-SYNC-TRANSPORT-001.md")))==1
assert len(list(pathlib.Path("spec/tasks").glob("*/LOOP1-SYNC-001.md")))==1
assert pathlib.Path("spec/tasks/backlog/LOOP1-SYNC-001.md").exists()
assert subprocess.check_output(["git","-C","H:/IM-platform","rev-parse","HEAD"],text=True).strip()=="a0304fcc7be18b87f5986d014849d6b48b96a071"
print("PASS archive byte-exact manifest",len(files),"files; precise admin scope, authority/source unchanged, unique queues, main HEAD unchanged")
