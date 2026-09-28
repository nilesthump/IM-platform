"""Independent CI path and gate controls for Review 3."""

import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "ci"))
from classify import FULL_COMPATIBILITY, classify, diff_paths
from check_gate import JOBS, check


def selected(paths):
    return {job for job, enabled in classify(paths).items() if enabled}


for path in ("contracts/x", "database/x", "sdk/x", "backend/java/migrations/x"):
    assert selected([path]) == FULL_COMPATIBILITY, path
for path, expected in (("backend/go/x", {"go"}), ("clients/mobile/x", {"mobile"}),
                       ("deploy/x", {"deploy"}), ("docs/x", set())):
    assert selected([path]) == expected, path

with tempfile.TemporaryDirectory() as directory:
    root = pathlib.Path(directory)
    def git(*args):
        return subprocess.check_output(["git", "-C", directory, *args], text=True).strip()
    git("init", "-q")
    git("config", "user.name", "Independent Review 3")
    git("config", "user.email", "review3@example.invalid")
    (root / "sdk").mkdir()
    (root / "docs").mkdir()
    source = root / "sdk" / "protocol.json"
    source.write_text("unique protocol fixture\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD")
    source.rename(root / "docs" / "protocol.json")
    git("add", "-A")
    git("commit", "-qm", "rename")
    head = git("rev-parse", "HEAD")
    previous = pathlib.Path.cwd()
    try:
        import os
        os.chdir(root)
        paths = diff_paths(base, head)
    finally:
        os.chdir(previous)
    assert set(paths) == {"sdk/protocol.json", "docs/protocol.json"}, paths
    assert selected(paths) == FULL_COMPATIBILITY, paths

for job in JOBS:
    for result in ("failure", "cancelled", "skipped"):
        outputs = {name: "false" for name in (*JOBS, "old_client", "plugin", "migration")}
        outputs[job] = "true"
        needs = {name: {"result": "skipped"} for name in JOBS}
        needs["classify"] = {"result": "success", "outputs": outputs}
        needs[job]["result"] = result
        try:
            check(needs)
        except ValueError:
            pass
        else:
            raise AssertionError((job, result))
        needs[job]["result"] = "success"
        check(needs)
        outputs[job] = "false"
        try:
            check(needs)
        except ValueError:
            pass
        else:
            raise AssertionError((job, "unselected success"))

print("PASS: shared rename, path isolation, and 24 fail/cancel/skip gate controls")
