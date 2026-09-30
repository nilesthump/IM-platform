"""Reviewer-only negative control: mutate one canonical expected outcome temporarily.

The candidate checkout is restored byte-for-byte before this script exits.
"""

import json
import os
from pathlib import Path
import subprocess
import sys

repo = Path(sys.argv[1])
fixture = repo / "contracts/fixtures/auth-user-friend/negative.json"
original = fixture.read_bytes()
try:
    data = json.loads(original)
    scenario = next(s for s in data["scenarios"] if s["id"] == "invalid-credentials")
    step = scenario["steps"][0]
    expected = step["expected"]
    assert expected["status"] == 401
    expected["status"] = 418
    fixture.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    result = subprocess.run(
        ["go", "-C", "backend/go", "test", "-run", "^TestCanonicalAuthHTTPFixtures/invalid-credentials$", "-count=1", "./..."],
        cwd=repo,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    output = result.stdout + result.stderr
    print(output)
    if result.returncode == 0 or "status 401, want fixture 418" not in output:
        raise SystemExit("FAIL: runtime fixture mutation was not rejected as expected")
    print("PASS: changed canonical HTTP expected status caused the live Go fixture test to fail")
finally:
    fixture.write_bytes(original)
