"""Reviewer-only negative control for the WSS requestId guard.

The candidate checkout is restored byte-for-byte before this script exits.
"""

from pathlib import Path
import subprocess
import sys

repo = Path(sys.argv[1])
source = repo / "backend/go/gateway.go"
original = source.read_bytes()
needle = b" || !validUUID(e.RequestID)"
assert original.count(needle) == 1
try:
    source.write_bytes(original.replace(needle, b"", 1))
    result = subprocess.run(
        ["go", "-C", "backend/go", "test", "-run", "^TestCanonicalWSSPrebindFixturesAndMalformedRequestID$", "-count=1", "./..."],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    print(output)
    if result.returncode == 0 or "malformed requestId accepted" not in output:
        raise SystemExit("FAIL: WSS UUID-guard mutation was not rejected as expected")
    print("PASS: removing the UUID guard caused the live WSS regression to fail")
finally:
    source.write_bytes(original)
