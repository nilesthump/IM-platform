"""Disposable source fixtures exercise real Go parsing and Java current/future rules.

These are new structural fixtures, not copies or replacements of canonical product
behavior vectors. The repository product tree is only read, never mutated.
"""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("source_checker", ROOT / "ci/check_architecture.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def go_base(self):
        self.put("backend/go/go.mod", "module boundary.test\n\ngo 1.23.0\n")
        self.put("backend/go/main.go", 'package main\nimport "boundary.test/core"\nfunc main(){core.Start()}\n')
        self.put("backend/go/core/core.go", 'package core\nimport "boundary.test/shared"\nfunc Start(){shared.Hash("x")}\ntype writer interface{Exec(string)}\nfunc Login(db writer){db.Exec("UPDATE sessions SET session_epoch=session_epoch+1")}\n')
        self.put("backend/go/shared/crypto.go", 'package shared\nimport("crypto/sha256";"encoding/hex")\nfunc Hash(s string)string{v:=sha256.Sum256([]byte(s));return hex.EncodeToString(v[:])}\n')
        self.put("backend/go/gateway/verify.go", 'package gateway\nimport "boundary.test/shared"\ntype reader interface{QueryRow(string) string}\nfunc Validate(){shared.Hash("x")}\nfunc SessionValid(db reader)string{return db.QueryRow("SELECT session_epoch FROM sessions WHERE status=1")}\n')

    def go_errors(self):
        return checker.check_go(self.root)[0]

    def assert_contains(self, errors, fragment):
        self.assertTrue(any(fragment in e for e in errors), (fragment, errors))

    def test_legal_single_module_go_runtime_and_blackbox_test(self):
        self.go_base()
        self.put("backend/go/tests/roles_test.go", 'package tests\nimport("testing";"boundary.test/core";"boundary.test/gateway")\nfunc TestRoles(t *testing.T){core.Start();gateway.Validate()}\n')
        self.assertEqual([], self.go_errors())
        subprocess.run(["go", "test", "./..."], cwd=self.root / "backend/go", check=True, capture_output=True)

    def test_root_new_business_and_unapproved_internal(self):
        self.go_base()
        self.put("backend/go/renamed.go", 'package main\nfunc Login(){}\n')
        self.put("backend/go/internal/renamed/x.go", 'package renamed\nfunc Register(){}\n')
        errors = self.go_errors()
        self.assert_contains(errors, "renamed.go: outside exact root whitelist")
        self.assert_contains(errors, "internal/renamed/x.go: outside exact root whitelist")

    def test_main_whitelisted_name_cannot_hide_business(self):
        self.go_base()
        self.put("backend/go/main.go", 'package main\nfunc main(){ _ = "INSERT INTO users(user_id) VALUES(1)" }\n')
        self.assert_contains(self.go_errors(), "root contains business SQL")

    def test_root_test_name_cannot_hide_business(self):
        self.go_base()
        self.put("backend/go/main_test.go", 'package main\nfunc Login(){_ = "INSERT INTO users VALUES(1)"}\n')
        self.assert_contains(self.go_errors(), "root contains business SQL")

    def test_cross_service_alias_import_and_build_tag(self):
        self.go_base()
        self.put("backend/go/gateway/hidden.go", '//go:build never\n\npackage gateway\nimport other "boundary.test/core"\nfunc Use(){other.Start()}\n')
        self.assert_contains(self.go_errors(), "gateway directly depends on core")

    def test_shared_reverse_dependency_and_moved_full_auth(self):
        self.go_base()
        self.put("backend/go/shared/renamed.go", 'package shared\nimport "boundary.test/core"\nfunc Hidden(){core.Start(); _ = "UPDATE sessions SET status=1"}\n')
        errors = self.go_errors()
        self.assert_contains(errors, "shared reverse dependency on core")
        self.assert_contains(errors, "shared contains business SQL")

    def test_gateway_cannot_write_session_or_outbox(self):
        self.go_base()
        self.put("backend/go/gateway/renamed.go", 'package gateway\nfunc Hidden(){ _ = "UPDATE outbox_events SET attempts=1"}\n')
        self.assert_contains(self.go_errors(), "gateway contains business SQL")

    def test_shared_generic_repository_call_rejected_without_sql_literal(self):
        self.go_base()
        self.put("backend/go/shared/renamed.go", 'package shared\nfunc Run(db interface{Exec(string)}, input string){db.Exec(input)}\n')
        self.assert_contains(self.go_errors(), "prohibited persistence call db.Exec")

    def test_real_old_go_layout_rejected_without_name_hardcoding(self):
        # Original root ownership pattern in a durable disposable fixture. Do not
        # bind this regression to the product tree remaining broken after stage004.
        self.go_base()
        self.put("backend/go/auth.go", 'package main\ntype authService struct{}\nfunc(s *authService) login(){_ = "UPDATE sessions SET status=1"}\n')
        errors, graph = checker.check_go(self.root)
        self.assertTrue(graph)
        self.assert_contains(errors, "backend/go/auth.go: outside exact root whitelist")
        self.assert_contains(errors, "root contains business SQL")

    def test_arbitrarily_named_go_root_assembly_helper_valid(self):
        self.go_base()
        self.put("backend/go/main.go", 'package main\nimport "boundary.test/core"\nfunc main(){runRole()}\nfunc runRole(){core.Start()}\n')
        self.assertEqual([], self.go_errors())

    def test_syntax_failure_cannot_be_skipped(self):
        self.go_base()
        self.put("backend/go/core/broken.go", "package core\nfunc Broken(\n")
        self.assert_contains(self.go_errors(), "Go parser failed (never skipped)")

    def java_base(self):
        self.put("backend/java/Main.java", 'import im.core.Service; public class Main { public static void main(String[] a){Service.start();} }')
        self.put("backend/java/core/Service.java", 'package im.core; public class Service {public static void start(){} }')
        self.put("backend/java/shared/Primitive.java", 'package im.shared; public class Primitive {public static String hash(String v){return v;} }')
        self.put("backend/java/gateway/Connection.java", 'package im.gateway; import im.shared.Primitive; public class Connection {public static void validate(){Primitive.hash("x");} }')

    def java_errors(self):
        return checker.check_java(self.root)[0]

    def test_current_java_placeholder_valid_and_no_early_business_required(self):
        self.put("backend/java/InfraPlaceholder.java", (ROOT / "backend/java/InfraPlaceholder.java").read_text(encoding="utf-8"))
        self.assertEqual([], self.java_errors())
        self.assertEqual([], checker.check_java(ROOT)[0])

    def test_future_java_single_layout_compiles_and_imports_checked(self):
        self.java_base()
        self.assertEqual([], self.java_errors())
        # The CI architecture job provisions a JDK; tool absence is failure, not skip.
        sources = list((self.root / "backend/java").rglob("*.java"))
        subprocess.run(["javac", "-d", str(self.root / "classes"), *map(str, sources)], check=True, capture_output=True)

    def test_arbitrarily_named_java_root_assembly_helper_valid(self):
        self.java_base()
        self.put("backend/java/Main.java", 'import im.core.Service; public class Main {public static void main(String[] a){runRole();} private static void runRole(){Service.start();}}')
        self.assertEqual([], self.java_errors())

    def test_java_gateway_readonly_session_and_shared_token_primitive_valid(self):
        self.java_base()
        self.put("backend/java/gateway/SessionCheck.java", 'package im.gateway; import java.sql.Connection; public class SessionCheck {public static void validate(Connection db)throws Exception{db.prepareStatement("SELECT session_epoch FROM sessions");}}')
        self.assertEqual([], self.java_errors())

    def test_java_dynamic_jdbc_shared_repository_and_gateway_write_rejected(self):
        self.java_base()
        self.put("backend/java/shared/Innocent.java", 'package im.shared; public class Innocent {public static void run(java.sql.Connection db,String q)throws Exception{db.prepareStatement(q).executeUpdate();}}')
        self.put("backend/java/gateway/Dynamic.java", 'package im.gateway; public class Dynamic {public static void run(java.sql.Connection db,String q)throws Exception{db.prepareStatement(q).executeUpdate();}}')
        errors = self.java_errors()
        self.assert_contains(errors, "shared owns prohibited JDBC persistence call prepareStatement")
        self.assert_contains(errors, "gateway owns prohibited JDBC persistence call executeUpdate")

    def test_java_gateway_execute_cannot_borrow_unrelated_select_literal(self):
        self.java_base()
        for operation in ('stmt.execute(q)', 'db.prepareStatement(q).execute()',
                          'stmt.execute("SELECT session_epoch FROM sessions")'):
            with self.subTest(operation=operation):
                self.put("backend/java/gateway/Dynamic.java", 'package im.gateway; import java.sql.Statement; import java.sql.Connection; public class Dynamic {public static void run(Connection db,Statement stmt,String q)throws Exception{String unused="SELECT session_epoch FROM sessions";'+operation+';}}')
                self.assert_contains(self.java_errors(), "gateway owns prohibited JDBC persistence call execute")

    def test_java_gateway_dynamic_update_with_select_decoy_rejected(self):
        self.java_base()
        self.put("backend/java/gateway/Dynamic.java", 'package im.gateway; import java.sql.Statement; public class Dynamic {public static void run(Statement stmt)throws Exception{String unrelated="SELECT session_epoch FROM sessions";String q="UPDATE "+"sessions SET status=1";stmt.execute(q);}}')
        self.assert_contains(self.java_errors(), "gateway owns prohibited JDBC persistence call execute")

    def test_java_noncore_jdbc_transaction_controls_rejected(self):
        self.java_base()
        for location in ("gateway", "shared"):
            for operation in ("commit()", "rollback()", "setAutoCommit(false)",
                              "setSavepoint()", "releaseSavepoint(null)"):
                with self.subTest(location=location, operation=operation):
                    self.put(f"backend/java/{location}/Transaction.java", f'package im.{location}; import java.sql.Connection; public class Transaction {{public static void run(Connection db)throws Exception{{db.{operation};}}}}')
                    self.assert_contains(self.java_errors(), f"{location} owns prohibited JDBC persistence call {operation.split('(')[0]}")

    def test_java_gateway_executequery_and_connection_lifecycle_valid(self):
        self.java_base()
        self.put("backend/java/gateway/SessionCheck.java", 'package im.gateway; import java.sql.Connection; public class SessionCheck {public static void validate(Connection db)throws Exception{try(var statement=db.prepareStatement("SELECT session_epoch FROM sessions")){statement.executeQuery();} db.close();}}')
        self.put("backend/java/shared/Connect.java", 'package im.shared; import java.sql.Connection; import java.sql.DriverManager; public class Connect {public static Connection open(String url)throws Exception{Connection db=DriverManager.getConnection(url);db.setReadOnly(true);return db;}}')
        self.assertEqual([], self.java_errors())

    def test_shared_java_connection_factory_is_support_not_repository(self):
        self.java_base()
        self.put("backend/java/shared/Connect.java", 'package im.shared; import java.sql.Connection; import java.sql.DriverManager; public class Connect {public static Connection open(String url)throws Exception{return DriverManager.getConnection(url);}}')
        self.assertEqual([], self.java_errors())

    def test_future_java_cross_service_shared_reverse_and_fully_qualified(self):
        self.java_base()
        self.put("backend/java/gateway/Connection.java", 'package im.gateway; public class Connection {public static void call(){ im.core.Service.start(); }}')
        self.put("backend/java/shared/Primitive.java", 'package im.shared; import im.core.Service; public class Primitive {public static void call(){Service.start();}}')
        errors = self.java_errors()
        self.assert_contains(errors, "gateway directly depends on core")
        self.assert_contains(errors, "shared reverse dependency on core")

    def test_java_unicode_import_cannot_bypass_dependency(self):
        self.java_base()
        self.put("backend/java/gateway/Connection.java", r'package im.gateway; import im.\u0063ore.Service; public class Connection {public static void call(){Service.start();}}')
        self.assert_contains(self.java_errors(), "gateway directly depends on core")

    def test_future_java_business_root_and_shared_disguise(self):
        self.java_base()
        self.put("backend/java/shared/Innocent.java", 'package im.shared; public class Innocent {public static void run(){String sql="UPDATE sessions SET status=1";}}')
        self.put("backend/java/Main.java", 'public class Main {public static void main(String[] a){String route="/v1/auth/login";}}')
        errors = self.java_errors()
        self.assert_contains(errors, "shared contains business SQL")
        self.assert_contains(errors, "shared owns business route")

    def test_placeholder_exit_and_business_not_permanent_exception(self):
        self.java_base()
        self.put("backend/java/InfraPlaceholder.java", 'public class InfraPlaceholder {public static void main(String[] a){} }')
        self.assert_contains(self.java_errors(), "placeholder expired")

    def test_java_placeholder_cannot_grow_business(self):
        self.put("backend/java/InfraPlaceholder.java", 'public class InfraPlaceholder {public static void main(String[] a){String sql="INSERT INTO users VALUES(1)";} }')
        self.assert_contains(self.java_errors(), "business SQL")

    def governance_base(self):
        for path in ("AGENTS.md", "CLAUDE.md", "spec/handoff/agent-context.md", "spec/tasks/TASK_TEMPLATE.md", "spec/governance/execution-boundaries.md", "spec/governance/independent-review.md", ".github/workflows/ci.yml"):
            target = ROOT / path
            if target.exists():
                self.put(path, target.read_text(encoding="utf-8"))

    def test_active_task_path_is_never_architecture_waiver(self):
        self.governance_base()
        self.put("spec/tasks/active/TASK.md", '# Inputs\n spec/architecture/README.md SRC-01 allowed_paths\n# Allowed Paths\n- `backend/go/internal/auth/**`\n- `backend/go/**`\n# Goal\nNew task\n')
        errors = checker.check_governance(self.root)
        self.assert_contains(errors, "conflicting allowed_path backend/go/internal/auth/**")
        self.assert_contains(errors, "conflicting allowed_path backend/go/**")

    def test_current_governance_and_task_migration_scope_valid(self):
        self.assertEqual([], checker.check_governance(ROOT))

    def test_plain_bullet_task_path_checked_and_legal_core_accepted(self):
        self.governance_base()
        self.put("spec/tasks/active/TASK.md", '# Inputs\n spec/architecture/README.md SRC-01 allowed_paths\n# Allowed Paths\n- backend/go/internal/auth/**\n# Goal\nCurrent task\n')
        self.assert_contains(checker.check_governance(self.root), "conflicting allowed_path backend/go/internal/auth/**")
        self.put("spec/tasks/active/TASK.md", '# Inputs\n spec/architecture/README.md SRC-01 allowed_paths\n# Allowed Paths\n- backend/go/core/auth/**\n# Goal\nCurrent task\n')
        self.assertEqual([], checker.check_governance(self.root))

    def test_workflow_missing_commands_dependencies_and_suppression_rejected(self):
        original = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertEqual([], checker.check_workflow(original))
        for changed in (
            original.replace("ci/check_architecture.py --scope clients --json", "echo client guard skipped"),
            original.replace("ci/check_architecture.py --scope go --json", "echo skipped"),
            original.replace("needs: [classify, architecture, source_go, source_java,", "needs: [classify, architecture, source_java,"),
            original.replace("  source_go:\n", "  source_go:\n    continue-on-error: true\n"),
            original.replace("if: needs.classify.outputs.source_java == 'true'", "if: false"),
            original.replace("  gate:\n", "  gate:\n    continue-on-error: true\n"),
            original.replace("python3 ci/check_gate.py", "python3 ci/check_gate.py || true"),
            original.replace("  classify:\n", "  classify:\n    continue-on-error: true\n"),
            original.replace("on:\n  push:\n  pull_request:", "on:\n  push:\n    paths-ignore: ['spec/**']\n  pull_request:"),
            original.replace("on:\n  push:\n  pull_request:", "on:\n  workflow_dispatch:"),
        ):
            self.assertNotEqual(original, changed)
            self.assertTrue(checker.check_workflow(changed))


if __name__ == "__main__":
    unittest.main()
