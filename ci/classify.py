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


def classify_detailed(paths):
    """Classify paths and attribute every selection to its rule.

    Same selection semantics as classify(); the returned reasons list records
    one entry per (path, rule) pair that selected jobs, in evaluation order.
    A path can fire several rules; zero-selection paths produce no entries.
    """
    selected = set()
    reasons = []

    def select(raw, rule, jobs):
        selected.update(jobs)
        reasons.append({"path": raw, "rule": rule, "jobs": sorted(jobs)})

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
        if parts[:3] in (["tests", "clients", "sqlite"], ["tests", "clients", "send"]) or path in {"tools/verify-client-sqlite.ps1", "tools/verify_client_sqlite.py", "tools/verify_client_send.py"}:
            select(raw, "client-verifier", {"architecture", "desktop", "mobile", "shared", "compatibility"})
        if parts[0] == "clients":
            select(raw, "clients", {"architecture"})
        if path in {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb", "tsconfig.json"}:
            select(raw, "root-manifest", JOBS)
        if governance:
            select(raw, "governance", {"architecture", "source_go", "source_java"})
        shared = (
            parts[0] in {"contracts", "database", "migrations", "sdk", "sdks", "shared"}
            or parts[:2] in (["backend", "shared"], ["clients", "shared"])
            or (len(parts) > 2 and parts[0] == "backend" and parts[2] in {"migrations", "sdk", "sdks", "shared"})
            or parts[:2] == ["tests", "database"]
        )
        if shared:
            select(raw, "shared-contract", FULL_COMPATIBILITY)
        elif parts[:2] in (["tests", "go"], ["tests", "e2e"]):
            select(raw, "go-e2e-tests", {"go", "deploy", "architecture", "source_go"})
        elif parts[:2] == ["backend", "go"]:
            select(raw, "backend-go", {"go", "architecture", "source_go"})
        elif parts[:2] == ["backend", "java"]:
            select(raw, "backend-java", {"java", "architecture", "source_java"})
        elif parts[:2] == ["clients", "web"]:
            select(raw, "clients-web", {"web"})
        elif parts[:2] == ["clients", "desktop"]:
            select(raw, "clients-desktop", {"desktop"})
        elif parts[:2] == ["clients", "mobile"]:
            select(raw, "clients-mobile", {"mobile"})
        elif (parts[0] == "ci"
              or parts[:2] in ([".github", "workflows"], ["tests", "ci"])):
            select(raw, "ci-config", JOBS)
        elif (parts[0] == "deploy" or parts[:2] == ["tests", "infrastructure"]):
            select(raw, "deploy-infra", {"deploy"})
    return {job: job in selected for job in JOBS}, reasons


def classify(paths):
    return classify_detailed(paths)[0]


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
    parser.add_argument("--explain", action="store_true", help="attribute every selection to the rule that made it")
    parser.add_argument("--github-output", help="GitHub Actions output file")
    args = parser.parse_args(argv)
    if args.paths is None and not (args.base and args.head):
        parser.error("supply --paths or both --base and --head")
    if args.paths is not None and (args.base or args.head):
        parser.error("--paths and Git revisions are mutually exclusive")
    paths = args.paths if args.paths is not None else diff_paths(args.base, args.head)
    if args.explain:
        matrix, reasons = classify_detailed(paths)
    else:
        matrix, reasons = classify(paths), None
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as output:
            for job, selected in matrix.items():
                output.write(f"{job}={str(selected).lower()}\n")
    payload = {"paths": paths, "jobs": matrix}
    if reasons is not None:
        payload["reasons"] = reasons
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    main()
