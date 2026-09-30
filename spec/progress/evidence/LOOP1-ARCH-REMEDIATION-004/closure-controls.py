from pathlib import Path
import hashlib,json,subprocess
base="d0ae52f5615320790ae7039cb48831873de6f486"
def git(*args):return subprocess.check_output(["git",*args])
protected=["backend","contracts","deploy","tests","ci","tools",".github","spec/architecture/frozen-architecture.md","scalable-distributed-im-architecture.pdf"]
for path in protected:
 changed=git("diff",base,"--",path);assert not changed,path
for folder in ["research","spec/progress/evidence","spec/progress/checkpoints","spec/tasks/done"]:
 old=set(git("ls-tree","-r","--name-only",base,"--",folder).decode().splitlines())
 changed=set(git("diff","--name-only",base,"--",folder).decode().splitlines())
 staged=set(git("diff","--cached","--name-only",base,"--",folder).decode().splitlines())
 assert not old.intersection(changed|staged),folder
for path in ["AGENTS.md","spec/handoff/agent-context.md","spec/governance/execution-boundaries.md","spec/progress/current.md","spec/tasks/review/LOOP1-ARCH-REMEDIATION-004.md"]:
 t=Path(path).read_text(encoding="utf-8");assert "\ufffd" not in t and "\u64023" not in t,path
for name,want in [("spec/architecture/frozen-architecture.md","83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e"),("scalable-distributed-im-architecture.pdf","546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510")]:assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==want
q=list(Path("spec/tasks").glob("*/LOOP1-ARCH-REMEDIATION-004.md"));assert len(q)==1 and q[0].parent.name=="review" and "status: review" in q[0].read_text(encoding="utf-8")
assert "Current Task State: review" in Path("spec/progress/current.md").read_text(encoding="utf-8")
print("PASS protected product/checker/contracts/canonical/PDF and all historical Git blobs identical and working diffs clean; unique004review; UTF8/references/current aligned. No product tests claimed newly run.")
