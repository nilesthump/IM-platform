"""Reject a selected GitHub Actions job that did not succeed."""

import json
import os
import sys


JOBS = ("go", "java", "web", "desktop", "mobile", "shared", "compatibility", "deploy", "architecture", "source_go", "source_java")


def check(needs):
    missing = (set(JOBS) | {"classify"}) - needs.keys()
    if missing:
        raise ValueError(f"required job entries missing: {sorted(missing)}")
    if needs["classify"]["result"] != "success":
        raise ValueError("classification and repository recovery did not pass")
    outputs = needs["classify"]["outputs"]
    for job in JOBS:
        if outputs.get(job) not in {"true", "false"}:
            raise ValueError(f"missing/invalid selection for {job}")
        selected = outputs[job] == "true"
        result = needs[job]["result"]
        if selected and result != "success":
            raise ValueError(f"selected {job} job ended {result}")
        if not selected and result != "skipped":
            raise ValueError(f"unselected {job} job unexpectedly ended {result}")
    for subcheck in ("old_client", "plugin", "migration"):
        if outputs.get(subcheck) not in {"true", "false"}:
            raise ValueError(f"missing/invalid selection for {subcheck}")
        if outputs[subcheck] == "true" and outputs["compatibility"] != "true":
            raise ValueError(f"{subcheck} selected without compatibility job")


if __name__ == "__main__":
    try:
        check(json.loads(os.environ["NEEDS_JSON"]))
    except (KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
    print("PASS: every selected CI job succeeded")
