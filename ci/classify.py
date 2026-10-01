"""Classify a Git diff into the Loop 1 CI job matrix.

The classifier consumes repository-relative paths, including deleted paths. A
shared contract change runs every profile/client and compatibility check.
"""

import argparse
import json
import os
import subprocess
import sys


JOBS = (
    "go", "java", "web", "desktop", "mobile", "shared",
    "old_client", "plugin", "migration", "compatibility", "deploy",
    "architecture", "source_go", "source_java",
)
FULL_COMPATIBILITY = frozenset(JOBS) - {"deploy"}


def classify(paths):
    selected = set()
    for raw in paths:
        path = raw.replace("\\", "/").removeprefix("./")
        if not path or path.startswith("/") or ".." in path.split("/"):
            raise ValueError(f"not a repository-relative path: {raw!r}")
        parts = path.split("/")
        governance = (
            path in {"AGENTS.md", "CLAUDE.md", "README.md"}
            or parts[:2] in (["spec", "architecture"], ["spec", "handoff"],
                             ["spec", "tasks"], ["spec", "batches"],
                             ["spec", "acceptance"], ["spec", "governance"],
                             ["tests", "architecture"], ["tools", "architecture"])
            or path.startswith("tools/verify-frozen-architecture")
            or path == "tools/verify_frozen_architecture.py"
            or path.startswith("tools/verify-loop1-ctrl-")
            or path.startswith("tools/verify-loop1-min-")
        )
        if parts[0] == "clients":
            selected.add("architecture")
        if path in {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb", "tsconfig.json"}:
            selected.update(JOBS)
        if governance:
            selected.update({"architecture", "source_go", "source_java"})
        shared = (
            parts[0] in {"contracts", "database", "migrations", "sdk", "sdks", "shared"}
            or parts[:2] in (["backend", "shared"], ["clients", "shared"])
            or (len(parts) > 2 and parts[0] == "backend" and parts[2] in {"migrations", "sdk", "sdks", "shared"})
            or parts[:2] == ["tests", "database"]
        )
        if shared:
            selected.update(FULL_COMPATIBILITY)
        elif parts[:2] in (["tests", "go"], ["tests", "e2e"]):
            selected.update({"go", "deploy", "architecture", "source_go"})
        elif parts[:2] == ["backend", "go"]:
            selected.update({"go", "architecture", "source_go"})
        elif parts[:2] == ["backend", "java"]:
            selected.update({"java", "architecture", "source_java"})
        elif parts[:2] == ["clients", "web"]:
            selected.add("web")
        elif parts[:2] == ["clients", "desktop"]:
            selected.add("desktop")
        elif parts[:2] == ["clients", "mobile"]:
            selected.add("mobile")
        elif (parts[0] == "ci"
              or parts[:2] in ([".github", "workflows"], ["tests", "ci"])):
            selected.update(JOBS)
        elif (parts[0] == "deploy" or parts[:2] == ["tests", "infrastructure"]):
            selected.add("deploy")
    return {job: job in selected for job in JOBS}


def diff_paths(base, head):
    result = subprocess.run(
        ["git", "diff", "--no-renames", "--name-only", "-z", base, head, "--"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return [os.fsdecode(path) for path in result.stdout.split(b"\0") if path]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Git base commit")
    parser.add_argument("--head", help="Git head commit")
    parser.add_argument("--paths", nargs="*", help="Explicit paths for local inspection")
    parser.add_argument("--github-output", help="GitHub Actions output file")
    args = parser.parse_args(argv)
    if args.paths is None and not (args.base and args.head):
        parser.error("supply --paths or both --base and --head")
    if args.paths is not None and (args.base or args.head):
        parser.error("--paths and Git revisions are mutually exclusive")
    paths = args.paths if args.paths is not None else diff_paths(args.base, args.head)
    matrix = classify(paths)
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as output:
            for job, selected in matrix.items():
                output.write(f"{job}={str(selected).lower()}\n")
    json.dump({"paths": paths, "jobs": matrix}, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
