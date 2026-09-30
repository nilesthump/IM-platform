"""Execute canonical SRC-01..07. Static evidence supplements independent semantic Review.

No legacy Go waiver: source violations return nonzero even during stage003.
Every Go file is parsed (not only the host build tags). Java imports and qualified
references are checked now; the Java job also compiles its explicit S0 transport.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SERVICES = {"gateway", "core", "plugin-host"}
SOURCE_DIRS = SERVICES | {"shared", "tests"}
ROOT_FILES = {
    "go": {"main.go", "main_test.go", "go.mod", "go.sum", "Dockerfile", "README.md", "config.example.json"},
    "java": {"Main.java", "MainTest.java", "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts", "gradle.properties", "Dockerfile", "README.md", "config.example.json"},
}
BUSINESS_SQL = re.compile(r"\b(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM|SELECT\b[\s\S]*?\bFROM)\s+(?:public\.)?(?:users|sessions|outbox_events|user_sync_events|messages|conversations|friendships|conversation_members)\b", re.I)
WRITE_SQL = re.compile(r"\b(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+(?:public\.)?(?:users|sessions|outbox_events|user_sync_events|messages|conversations|friendships|conversation_members)\b", re.I)
BUSINESS_ROUTE = re.compile(r"/v\d+/(?:auth|users|friends|conversations|messages|sync|plugins)(?:/|\b)")


def owner(path):
    parts = Path(path).parts
    return parts[0] if len(parts) > 1 else "root"


def source_paths(root, language):
    directory = root / "backend" / language
    violations = []
    if directory.is_symlink():
        return [], [f"SRC-01 {directory}: backend symlink prohibited"]
    files = []
    for path in directory.rglob("*"):
        relative = path.relative_to(directory).as_posix()
        if path.is_symlink():
            violations.append(f"SRC-01 backend/{language}/{relative}: symlink bypass prohibited")
        elif path.is_file():
            if path.name == ".gitkeep" and path.read_bytes() in (b"", b"\n", b"\r\n"):
                continue
            parts = Path(relative).parts
            allowed = relative in ROOT_FILES[language] or (len(parts) > 1 and parts[0] in SOURCE_DIRS)
            # One explicit historical placeholder, never inferred from a task name.
            if language == "java" and relative == "InfraPlaceholder.java":
                allowed = True
            if not allowed:
                violations.append(f"SRC-01/02 backend/{language}/{relative}: outside exact root whitelist/service ownership")
            if path.suffix == (".go" if language == "go" else ".java"):
                files.append(path)
    return files, violations


def semantic_violations(path, unit_owner, strings, functions, types, is_test=False):
    errors = []
    # Black-box test helpers may exercise real behavior under tests/ or service dirs;
    # root tests only assemble and shared tests must not hide runtime business.
    if is_test and unit_owner not in {"root", "shared"}:
        return errors
    if unit_owner in {"root", "shared", "gateway", "plugin-host"}:
        for value in strings:
            sql = BUSINESS_SQL if unit_owner in {"root", "shared", "plugin-host"} else WRITE_SQL
            if sql.search(value):
                errors.append(f"SRC-01/03 {path}: {unit_owner} contains business SQL: {value[:100]}")
            if unit_owner in {"root", "shared", "plugin-host"} and BUSINESS_ROUTE.search(value):
                errors.append(f"SRC-01/03 {path}: {unit_owner} owns business route {value[:100]}")
    # Declaration names are recorded for Review, not a responsibility verdict.
    # Assembly may use helpers/types of any name; SQL/routes/persistence and actual
    # imports are the machine guardrails. Semantic Review remains mandatory.
    return errors


def dependency_violation(path, origin, target, is_blackbox=False):
    if origin == "root" and target == "tests" and not is_blackbox:
        return f"SRC-04 {path}: assembly depends on test implementation"
    if is_blackbox or origin in {"root", "tests"}:
        return None
    if origin == "shared" and target in SERVICES:
        return f"SRC-03/04 {path}: shared reverse dependency on {target}"
    if origin in SERVICES and target in SERVICES and target != origin:
        return f"SRC-04 {path}: {origin} directly depends on {target} implementation"
    if origin in SERVICES | {"shared"} and target in {"root", "tests"}:
        return f"SRC-04 {path}: runtime implementation depends on assembly/tests"
    return None


def check_go(root):
    files, errors = source_paths(root, "go")
    if not files:
        return errors, []
    directory = root / "backend/go"
    module_file = directory / "go.mod"
    if not module_file.exists():
        return errors + ["SRC-04 Go module missing; import graph cannot be verified"], []
    match = re.search(r"^module\s+(\S+)", module_file.read_text(encoding="utf-8"), re.M)
    if not match:
        return errors + ["SRC-04 Go module declaration missing"], []
    module = match.group(1)
    command = ["go", "run", str(ROOT / "tools/architecture/go_source_graph.go"), str(directory)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    except OSError as error:
        return errors + ["Go parser unavailable (never skipped): " + str(error)], []
    if result.returncode:
        return errors + ["Go parser failed (never skipped): " + result.stderr.strip()], []
    graph = json.loads(result.stdout)
    for unit in graph:
        path = "backend/go/" + unit["path"]
        origin = owner(unit["path"])
        test = unit["path"].endswith("_test.go")
        errors += semantic_violations(path, origin, unit["strings"] or [], unit["functions"] or [], unit["types"] or [], test)
        if not test or origin in {"root", "shared"}:
            for call in unit["calls"] or []:
                method = call.rsplit(".", 1)[-1]
                prohibited = {"Exec", "ExecContext", "Query", "QueryRow", "QueryContext", "QueryRowContext", "Begin", "BeginTx"}
                # net/url URL.Query is protocol parsing, not persistence. SELECT
                # literals remain independently checked; no DB query is exempted.
                if call.endswith(".URL.Query") and "net/http" in (unit["imports"] or []):
                    continue
                if origin == "gateway":
                    prohibited = {"Exec", "ExecContext", "Begin", "BeginTx"}
                if origin in {"root", "shared", "gateway", "plugin-host"} and method in prohibited:
                    errors.append(f"SRC-01/03 {path}: {origin} owns prohibited persistence call {call}")
        for dependency in unit["imports"] or []:
            if dependency == module or dependency.startswith(module + "/"):
                target_path = dependency[len(module):].lstrip("/")
                target = target_path.split("/")[0] if target_path else "root"
                violation = dependency_violation(path, origin, target, test and (origin == "tests" or unit["package"].endswith("_test")))
                if violation:
                    errors.append(violation + " (" + dependency + ")")
                if target not in SOURCE_DIRS | {"root"}:
                    errors.append(f"SRC-01/04 {path}: imports unowned local package {dependency}")
    return errors, graph


def java_tokens(text):
    # Preserve string literals (SQL/routes) and discard comments, including comments
    # containing forged imports. Handle escapes before collecting actual tokens.
    # Java processes Unicode escapes before tokenization, including imports.
    text = re.sub(r"\\u+([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), text)
    pattern = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/'
    strings = []
    def clean(match):
        value = match.group()
        if value.startswith('"'):
            strings.append(value[1:-1])
            return " "
        return " " if value.startswith(("//", "/*", "'")) else value
    return re.sub(pattern, clean, text), strings


def check_java(root):
    files, errors = source_paths(root, "java")
    units = []
    declarations = {}
    for path in files:
        relative = path.relative_to(root / "backend/java").as_posix()
        code, strings = java_tokens(path.read_text(encoding="utf-8"))
        package_match = re.search(r"\bpackage\s+([\w.]+)\s*;", code)
        package = package_match.group(1) if package_match else ""
        types = re.findall(r"\b(?:class|interface|enum|record)\s+(\w+)", code)
        origin = owner(relative)
        for declaration in types:
            qualified = (package + "." if package else "") + declaration
            if qualified in declarations:
                errors.append(f"SRC-04 duplicate Java type {qualified}")
            declarations[qualified] = origin
        units.append(dict(path=relative, owner=origin, package=package, code=code, strings=strings, types=types))
    has_business = any(x["owner"] in SERVICES for x in units)
    placeholder = [x for x in units if x["path"] == "InfraPlaceholder.java"]
    for unit in units:
        path = "backend/java/" + unit["path"]
        code = unit["code"]
        methods = re.findall(r"\b(\w+)\s*\([^;{}]*\)\s*(?:throws\s+[\w., ]+)?\s*\{", code)
        if unit in placeholder:
            if has_business:
                errors.append(f"SRC-06 {path}: placeholder expired at Java first service implementation")
            # Exact bounded transport behavior, with no business route/SQL/import.
            errors += semantic_violations(path, "shared", unit["strings"], methods, unit["types"])
            bad_routes = [s for s in unit["strings"] if s.startswith("/") and s not in {"/__infra/ws", "/__infra/health"}]
            if bad_routes:
                errors.append(f"SRC-06 {path}: unapproved placeholder routes {bad_routes}")
        elif unit["owner"] == "root":
            errors += semantic_violations(path, "shared", unit["strings"], methods, unit["types"])
        else:
            errors += semantic_violations(path, unit["owner"], unit["strings"], methods, unit["types"], unit["path"].endswith("Test.java"))
        jdbc = bool(re.search(r"\b(?:java|javax)\.sql\b", code))
        if jdbc and unit["owner"] in {"root", "shared", "gateway", "plugin-host"}:
            calls = re.findall(r"\.\s*(\w+)\s*\(", code)
            forbidden = {"prepareStatement", "prepareCall", "createStatement", "execute", "executeQuery", "executeUpdate", "executeLargeUpdate", "executeBatch", "executeLargeBatch"}
            if unit["owner"] == "gateway":
                forbidden = {"executeUpdate", "executeLargeUpdate", "executeBatch", "executeLargeBatch"}
                # execute() may write; allow it only with a literal proven SELECT.
                if "execute" in calls and not any(re.match(r"\s*SELECT\b", s, re.I) for s in unit["strings"]):
                    forbidden.add("execute")
            for call in set(calls) & forbidden:
                errors.append(f"SRC-01/03 {path}: {unit['owner']} owns prohibited JDBC persistence call {call}")
        # Includes explicit imports, static imports, wildcard packages, same-package
        # references and fully qualified usages without import declarations.
        references = re.findall(r"\bimport\s+(?:static\s+)?([\w.*]+)\s*;", code)
        for qualified, target in declarations.items():
            package, _, simple = qualified.rpartition(".")
            present = bool(re.search(r"(?<![\w$])" + re.escape(qualified) + r"(?![\w$])", code))
            present |= unit["package"] == package and bool(re.search(r"\b" + re.escape(simple) + r"\b", code))
            present |= any(r == qualified or r.startswith(qualified + ".") or r == package + ".*" for r in references)
            if present:
                violation = dependency_violation(path, unit["owner"], target, unit["owner"] == "tests")
                if violation:
                    errors.append(violation + " (" + qualified + ")")
        for dependency in references:
            # Unresolved project service imports are rejected too; renaming/deleting
            # the destination cannot erase a prohibited dependency classification.
            for segment in dependency.split("."):
                target = "plugin-host" if segment in {"pluginhost", "plugin_host"} else segment
                if target in SERVICES:
                    violation = dependency_violation(path, unit["owner"], target, unit["owner"] == "tests")
                    if violation:
                        errors.append(violation + " (" + dependency + ")")
    return errors, [{k: v for k, v in u.items() if k != "code"} for u in units]


def task_paths(text):
    section = re.search(r"(?ms)^# Allowed Paths\s*\n(.*?)(?=^# |\Z)", text)
    if not section:
        return []
    paths = []
    for line in section.group(1).splitlines():
        bullet = re.match(r"^\s*[-*+]\s+(.+)", line)
        if not bullet:
            continue
        item = bullet.group(1).strip()
        if item.startswith("`"):
            match = re.match(r"`([^`]+)`", item)
            if not match:
                raise ValueError("unparseable allowed_path: " + item)
            paths.append(match.group(1))
        else:
            match = re.match(r"([\w.*?/-]+)(?:\s|$)", item)
            if not match:
                raise ValueError("unparseable allowed_path: " + item)
            paths.append(match.group(1))
    if not paths:
        raise ValueError("Allowed Paths section has no parseable path entries")
    return paths


def check_governance(root):
    errors = []
    # This is subordinate discovery validation; current authority/hash/ADR semantics
    # are verified by the independent frozen integrity verifier, not duplicated here.
    required = {
        "AGENTS.md": ["spec/architecture/README.md", "SRC-01", "allowed_paths", "spec/governance/independent-review.md"],
        "spec/handoff/agent-context.md": ["spec/architecture/README.md", "SRC-01", "allowed_paths"],
        "spec/tasks/TASK_TEMPLATE.md": ["spec/architecture/README.md", "SRC-01", "allowed_paths", "source"],
        "spec/governance/execution-boundaries.md": ["SRC-01", "allowed_paths", "placeholder", "stage"],
        "spec/governance/independent-review.md": ["SRC-01", "imports", "minimality", "hosted"],
    }
    for path, tokens in required.items():
        text = (root / path).read_text(encoding="utf-8") if (root / path).exists() else ""
        for token in tokens:
            if token.lower() not in text.lower():
                errors.append(f"governance {path}: missing canonical execution reference {token}")
    claude = root / "CLAUDE.md"
    if claude.exists() and "AGENTS.md" not in claude.read_text(encoding="utf-8"):
        errors.append("governance CLAUDE.md: must route to authoritative Agent entry")
    for queue in ("backlog", "ready", "active", "review"):
        for path in (root / "spec/tasks" / queue).glob("*.md"):
            text = path.read_text(encoding="utf-8")
            try:
                allowed_paths = task_paths(text)
            except ValueError as error:
                errors.append(f"SRC-07 {path.relative_to(root)}: {error}")
                continue
            for allowed in allowed_paths:
                if allowed.startswith(("backend/go/", "backend/java/")):
                    parts = allowed.split("/")
                    if len(parts) > 3 and parts[2] in SOURCE_DIRS:
                        continue
                    if len(parts) == 3 and parts[2] in ROOT_FILES[parts[1]]:
                        continue
                    # Explicit one-time migration, exact task and exit, never a
                    # runtime source-check waiver. Adding broad paths elsewhere fails.
                    if path.name == "LOOP1-ARCH-REMEDIATION-004.md" and allowed == "backend/go/**" and "one-time migration authorization" in text and "exits on batch completion" in text:
                        continue
                    errors.append(f"SRC-07 {path.relative_to(root)}: conflicting allowed_path {allowed}")
            if allowed_paths and any(p.startswith("backend/") for p in allowed_paths):
                for token in ("spec/architecture/README.md", "SRC-01", "allowed_paths"):
                    if token not in text:
                        errors.append(f"SRC-07 {path.relative_to(root)}: missing {token}")
    errors += check_workflow((root / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    return errors


def check_workflow(text):
    errors = []
    blocks = {m.group(1): m.group(2) for m in re.finditer(r"(?ms)^  ([a-z_]+):\n(.*?)(?=^  [a-z_]+:\n|\Z)", text)}
    trigger = re.search(r"(?ms)^on:(.*?)(?=^\S|\Z)", text)
    trigger_text = trigger.group(1) if trigger else ""
    if not (re.search(r"\bpush\b", trigger_text) and re.search(r"\bpull_request\b", trigger_text)):
        errors.append("CI on: push/pull_request triggers required")
    if re.search(r"\b(?:paths|paths-ignore|branches|branches-ignore)\s*:", trigger_text):
        errors.append("CI on: trigger filters cannot bypass applicable checks")
    commands = {"architecture": ["./tools/verify-frozen-architecture.ps1", "ci/check_architecture.py --scope governance", "unittest discover -s tests/architecture"],
                "source_go": ["ci/check_architecture.py --scope go --json"],
                "source_java": ["ci/check_architecture.py --scope java --json"]}
    for job, required in commands.items():
        block = blocks.get(job, "")
        if f"if: needs.classify.outputs.{job} == 'true'" not in block:
            errors.append(f"CI {job}: missing exact path selection condition")
        for command in required:
            if command not in block:
                errors.append(f"CI {job}: missing required command {command}")
        if "continue-on-error" in block or "|| true" in block:
            errors.append(f"CI {job}: failure suppression forbidden")
        if f"{job}: ${{{{ steps.paths.outputs.{job} }}}}" not in blocks.get("classify", ""):
            errors.append(f"CI classify: missing output {job}")
        if not re.search(r"needs:\s*\[[^\]]*\b" + job + r"\b", blocks.get("gate", "")):
            errors.append(f"CI gate: missing required dependency {job}")
    if "if: always()" not in blocks.get("gate", "") or "python3 ci/check_gate.py" not in blocks.get("gate", ""):
        errors.append("CI gate: required unconditional result verification missing")
    for job in ("classify", "gate"):
        block = blocks.get(job, "")
        if "continue-on-error" in block or "|| true" in block:
            errors.append(f"CI {job}: failure suppression forbidden")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--scope", choices=("go", "java", "governance", "all"), default="all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    errors = []
    graphs = {}
    if args.scope in {"governance", "all"}:
        errors += check_governance(args.root)
    for language, checker in (("go", check_go), ("java", check_java)):
        if args.scope in {language, "all"}:
            found, graph = checker(args.root)
            errors += found
            graphs[language] = graph
    errors = sorted(set(errors))
    if args.json:
        print(json.dumps({"result": "FAIL" if errors else "PASS", "scope": args.scope, "violations": errors, "graphs": graphs}, ensure_ascii=False, indent=2))
    else:
        for error in errors:
            print("FAIL: " + error)
        print(f"{ 'FAIL' if errors else 'PASS'}: scope={args.scope} violations={len(errors)}; static checks supplement independent Review")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
