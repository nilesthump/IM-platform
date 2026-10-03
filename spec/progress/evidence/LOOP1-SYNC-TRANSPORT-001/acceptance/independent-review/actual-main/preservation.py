from pathlib import Path
import subprocess,json,hashlib,os
r=Path(r"H:/IM-platform/.git/worktrees/IM-platform5/sync-final-candidate-review/actual-main")
main=Path("H:/IM-platform");d=json.loads(Path(r"H:/IM-platform/.git/worktrees/IM-platform5/sync-transport-coordinator-research/main-before.json").read_text())
assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=main).decode().strip()==d["head"]
assert len(d["entries"])==781
for row in d["entries"]:
 p=main/row["path"];st=p.lstat();assert st.st_size==row["size"] and st.st_mode==row["mode"],row["path"]
 b=os.readlink(p).encode() if p.is_symlink() else p.read_bytes();assert hashlib.sha256(b).hexdigest()==row["sha256"],row["path"]
# status set unchanged, excluding only global excludes so unknown files are never hidden
raw=subprocess.check_output(["git","-c","core.excludesFile=.git/info/exclude","status","--porcelain=v1","--untracked-files=all","-z"],cwd=main).decode().split("\0")
actual=[(x[:2],x[3:]) for x in raw if x];expected=[(x["status"],x["path"]) for x in d["entries"]]
assert actual==expected
assert subprocess.check_output(["git","rev-parse","HEAD^{tree}"]).decode()==subprocess.check_output(["git","rev-parse","b8200783ea3eadc1ed4e4050238f051a7ab708b3^{tree}"]).decode()
assert not subprocess.check_output(["git","status","--porcelain=v1"])
for f,h in [("spec/architecture/frozen-architecture.md","ef90846ba380df14086795a3c58aef43f6503447fe0cb83ee2d0772d725d8e03"),("scalable-distributed-im-architecture.pdf","546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510")]:assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h
print("PASS: c2ff tree equals independently reviewed b820; clean; canonical/PDF SHA unchanged; main remains a030 with all781 status/size/mode/hash entries preserved before synchronization")
