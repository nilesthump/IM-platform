"""Independent byte audit for the two historical Recorder blob directories."""

from pathlib import Path
import subprocess
import sys

BASE = "1d9ec9f"
CANDIDATE = "0621f2b76aedecfb4fcb7a657bd977cc79e8e8ac"
RUNS = (
    "R-20260928T050925Z-2cc0954c-0cd6-43fa-8b41-b014d633a5bb",
    "R-20260928T053447Z-5aa0c014-0381-4fba-9457-7acb7cf3da9a",
)
DIRS = tuple(f"research/runs/{run}/blobs" for run in RUNS)
CLONES = tuple(Path(arg) for arg in sys.argv[1:])


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def tree(repo, revision):
    entries = {}
    for record in git(repo, "ls-tree", "-r", "-z", revision, "--", *DIRS).split(b"\0"):
        if not record:
            continue
        metadata, path = record.split(b"\t", 1)
        entries[path.decode()] = metadata.split(b" ")[-1].decode()
    return entries


for clone in CLONES:
    assert not (clone / ".git" / "info" / "attributes").exists(), clone
    assert git(clone, "rev-parse", "HEAD").decode().strip() == CANDIDATE, clone
    before = tree(clone, BASE)
    after = tree(clone, CANDIDATE)
    additions = {f"{directory}/.gitattributes" for directory in DIRS}
    assert set(after) - set(before) == additions, clone
    assert set(before) - set(after) == set(), clone
    assert len(before) == 42, (clone, len(before))
    for path, oid in before.items():
        assert after[path] == oid, (clone, path, "Git object changed")
        checkout_oid = git(clone, "hash-object", "--no-filters", path).decode().strip()
        assert checkout_oid == oid, (clone, path, "checkout bytes differ")
    status = git(clone, "status", "--porcelain=v1", "--untracked-files=all")
    assert status == b"", (clone, status)
    print(f"PASS clone={clone} original_blobs={len(before)} added_transport_rules=2 byte_mismatches=0 status_entries=0")
