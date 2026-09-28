"""Refresh the clean existing main checkout from its exact committed fixture bytes."""

from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
relative = Path("contracts/fixtures/websocket/golden.json")
target = root / relative
status = subprocess.run(
    ["git", "-C", str(root), "status", "--porcelain=v1", "--", str(relative)],
    capture_output=True,
    check=True,
).stdout
if status.strip():
    raise SystemExit("refusing to overwrite a modified fixture")
blob = subprocess.run(
    ["git", "-C", str(root), "show", "HEAD:contracts/fixtures/websocket/golden.json"],
    capture_output=True,
    check=True,
).stdout
target.write_bytes(blob)
if target.read_bytes() != blob:
    raise SystemExit("fixture refresh did not preserve committed bytes")
print(f"restored exact committed fixture bytes: {len(blob)}")
