"""Fault regressions for the existing verifier processes; no live Docker/TLS claim."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[3]
SMOKE = ROOT / 'tests/infrastructure/smoke.ps1'
AUTH = ROOT / 'contracts/http/verify-auth-user-friend.ps1'


def quote(value):
    return "'" + str(value).replace("'", "''") + "'"


class VerificationFailureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pwsh = shutil.which('pwsh')
        cls.node = shutil.which('node')
        if not cls.pwsh or not cls.node:
            raise RuntimeError('pwsh and Node are required; these regressions must execute')

    def run_script(self, directory, name, source, *arguments):
        path = pathlib.Path(directory) / name
        path.write_text(source, encoding='utf-8', newline='\n')
        return subprocess.run([self.pwsh, '-NoProfile', '-File', str(path), *arguments],
                              cwd=ROOT, capture_output=True, text=True, encoding='utf-8')

    def auth_fault(self, mode):
        # The whole original verifier executes; only the native checker boundary
        # changes after its first real positive Node invocation.
        native = "import sys;sys.stderr.write('CHECKER_INTERNAL_SENTINEL\\n');sys.exit(" + mode + ")"
        if mode == 'abrupt':
            native = 'import os;os._exit(86)'
        fault = "throw [InvalidOperationException]::new('CHECKER_LAUNCH_SENTINEL')" if mode == 'throw' else (
            '$result = @($incoming | & ' + quote(sys.executable) + ' -c ' + quote(native) + ' 2>&1); $code = $LASTEXITCODE')
        shim = '''
$script:nodeCalls = 0
function node {
    $incoming = @($input) -join "`n"
    $script:nodeCalls++
    if ($script:nodeCalls -eq 1) {
        $result = @($incoming | & REAL_NODE @args 2>&1)
        $code = $LASTEXITCODE
    } else { FAULT }
    $result | Write-Output
    $global:LASTEXITCODE = $code
}
'''.replace('REAL_NODE', quote(self.node)).replace('FAULT', fault)
        source = AUTH.read_text(encoding='utf-8')
        marker = "$ErrorActionPreference = 'Stop'"
        self.assertEqual(source.count(marker), 1)
        source = source.replace(marker, marker + '\n' + shim, 1)
        with tempfile.TemporaryDirectory(prefix='group-auth-fault-') as directory:
            return self.run_script(directory, 'auth.ps1', source, '-RepoRoot', str(ROOT))

    def test_whole_auth_verifier_keeps_known_schema_exit_one_negative_controls(self):
        result = self.auth_fault('1')
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        for expected in ('PASS:', 'error_codes=16', 'positive=6', 'negative=21', 'mutation_regressions=15'):
            self.assertIn(expected, result.stdout)

    def test_whole_auth_verifier_fails_internal_native_and_launch_defects(self):
        for mode in ('2', '37', 'abrupt', 'throw'):
            with self.subTest(fault=mode):
                result = self.auth_fault(mode)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn('PASS:', result.stdout)
                if mode in ('2', '37'):
                    self.assertIn('CHECKER_INTERNAL_SENTINEL', result.stdout + result.stderr)
                    self.assertIn(mode, result.stdout + result.stderr)
                elif mode == 'throw':
                    self.assertIn('CHECKER_LAUNCH_SENTINEL', result.stderr)

    def test_actual_structure_helper_propagates_missing_node_and_serialization_defects(self):
        source = AUTH.read_text(encoding='utf-8')
        helper = source.split('function Get-OpenApiStructureErrors {', 1)[1].split('\nfunction Resolve-ResponseObject', 1)[0]
        helper = 'function Get-OpenApiStructureErrors {' + helper
        for fault in ("$env:PATH = ''", "function ConvertTo-Json { throw [InvalidOperationException]::new('CONVERT_INTERNAL_SENTINEL') }"):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory(prefix='group-auth-helper-') as directory:
                script = "$ErrorActionPreference = 'Stop'\n" + helper + '\n' + fault + '''
Get-OpenApiStructureErrors ([pscustomobject]@{}) 'unused-checker.js' 'fault'
Write-Output 'FALSE_HELPER_SUCCESS'
'''
                result = self.run_script(directory, 'helper.ps1', script)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn('FALSE_HELPER_SUCCESS', result.stdout)
                if 'CONVERT_' in fault:
                    self.assertIn('CONVERT_INTERNAL_SENTINEL', result.stderr)

    def smoke_fault(self, profile, *, rows=None, primary=0, cleanup=0, ledger_exit=0, observe_environment=True):
        rows = ['0001_initial', '0002_group_operations'] if rows is None else rows
        # Literal PostgreSQL JSON/text transcripts. The live PG regression also
        # checks the actual aggregate SQL against comma/newline-valued rows.
        plain = '\n'.join(rows)
        aggregate = json.dumps(rows, ensure_ascii=False) if rows else 'null'
        shim = '''
function Invoke-NativeFault([string]$OutputText, [int]$Code, [string]$Diagnostic) {
    & PYTHON -c 'import sys;sys.stdout.write(sys.argv[1]);sys.stderr.write(sys.argv[3]);sys.exit(int(sys.argv[2]))' $OutputText $Code $Diagnostic
}
function docker {
    if ('down' -in $args) { Invoke-NativeFault '' CLEANUP 'CLEANUP_NATIVE_SENTINEL'; return }
    if ('pg_isready' -in $args -and PRIMARY -ne 0) { Invoke-NativeFault '' PRIMARY 'PRIMARY_NATIVE_SENTINEL'; return }
    if ('ps' -in $args) { $expected; $global:LASTEXITCODE = 0; return }
    if ('-Atc' -in $args) {
        if ($args[-1] -ceq 'SELECT version FROM schema_migrations ORDER BY version') { $text = PLAIN }
        elseif ($args[-1] -ceq 'SELECT json_agg(version ORDER BY version) FROM schema_migrations') { $text = AGGREGATE }
        else { throw "Unrecognized ledger SQL: $($args[-1])" }
        Invoke-NativeFault $text LEDGER 'LEDGER_NATIVE_SENTINEL'; return
    }
    $global:LASTEXITCODE = 0
}
function Read-TlsResponse([string]$Path, [string[]]$Headers) {
    if ($Path -eq '/__infra/health') { return @{ Status='HTTP/1.1 200 OK'; Body="profile=$Profile role=gateway"; Protocol='isolated-probe'; Headers=@{} } }
    if ('Origin: https://foreign.invalid' -in $Headers) { return @{ Status='HTTP/1.1 403 Forbidden' } }
    return @{ Status='HTTP/1.1 101 Switching Protocols'; Headers=@{'sec-websocket-accept'='s3pPLMBiTxaQ9kYGzzhZRbK+xOo='}; Body=''; Protocol='isolated-probe' }
}
function Test-JavaAuthTransport([string]$base, [int]$port) {
    if ($base -ne "https://localhost:$port" -or $port -ne 18444) { throw 'Unexpected Java Auth smoke target' }
    Write-Output 'ISOLATED_JAVA_AUTH_TRANSPORT'
}
'''
        for key, value in (('PYTHON', quote(sys.executable)), ('CLEANUP', str(cleanup)), ('PRIMARY', str(primary)), ('PLAIN', quote(plain)), ('AGGREGATE', quote(aggregate)), ('LEDGER', str(ledger_exit))):
            # Replace whole placeholder tokens, not diagnostic sentinel names.
            import re
            shim = re.sub(r'\b' + key + r'\b', lambda _: value, shim)
        source = SMOKE.read_text(encoding='utf-8')
        source = source.replace("$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path", '$root = ' + quote(ROOT), 1)
        marker = "\ntry {\n    Compose @('config', '--quiet')"
        self.assertEqual(source.count(marker), 1)
        source = source.replace(marker, '\n' + shim + marker, 1)
        with tempfile.TemporaryDirectory(prefix='group-smoke-fault-') as directory:
            if not observe_environment:
                return self.run_script(directory, 'smoke.ps1', source, '-Profile', profile)
            target = pathlib.Path(directory) / 'smoke.ps1'
            target.write_text(source, encoding='utf-8', newline='\n')
            wrapper = '''
$code = 0
try { & TARGET -Profile PROFILE }
catch { [Console]::Error.WriteLine($_.ToString()); $code = 1 }
finally {
    [Console]::Out.WriteLine('ENV_CLEAN=' + (-not (Test-Path Env:IM_HTTPS_PORT) -and -not (Test-Path Env:COMPOSE_PROGRESS)))
}
exit $code
'''.replace('TARGET', quote(target)).replace('PROFILE', quote(profile))
            return self.run_script(directory, 'observe.ps1', wrapper)

    def test_smoke_success_primary_cleanup_and_dual_failures_preserve_causes_and_environment(self):
        for profile in ('go', 'java'):
            for primary, cleanup in ((0, 0), (23, 0), (0, 37), (23, 37)):
                with self.subTest(profile=profile, primary=primary, cleanup=cleanup):
                    result = self.smoke_fault(profile, primary=primary, cleanup=cleanup)
                    self.assertIn('ENV_CLEAN=True', result.stdout)
                    self.assertEqual(result.returncode == 0, primary == cleanup == 0, result.stdout + result.stderr)
                    self.assertEqual('PASS:' in result.stdout, primary == cleanup == 0, result.stdout + result.stderr)
                    self.assertEqual('ISOLATED_JAVA_AUTH_TRANSPORT' in result.stdout, profile == 'java' and primary == 0)
                    if primary:
                        self.assertIn('PRIMARY_NATIVE_SENTINEL', result.stderr)
                        self.assertIn('23', result.stderr)
                    if cleanup:
                        self.assertIn('CLEANUP_NATIVE_SENTINEL', result.stderr)
                        self.assertIn('37', result.stderr)

    def test_standalone_smoke_process_fails_native_cleanup(self):
        for profile in ('go', 'java'):
            with self.subTest(profile=profile):
                result = self.smoke_fault(profile, cleanup=37, observe_environment=False)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn('PASS:', result.stdout)
                self.assertIn('CLEANUP_NATIVE_SENTINEL', result.stderr)
                self.assertIn('37', result.stderr)

    def test_smoke_ledger_rejects_ambiguous_missing_extra_duplicate_order_case_and_native_failures(self):
        cases = [
            (['0001_initial', '0002_group_operations'], 0, True),
            (['0001_initial,0002_group_operations'], 0, False),
            (['0001_initial\n0002_group_operations'], 0, False),
            ([], 0, False), (['0001_initial'], 0, False),
            (['0001_initial', '0002_group_operations', '0003_unknown'], 0, False),
            (['0001_initial', '0001_initial', '0002_group_operations'], 0, False),
            (['0002_group_operations', '0001_initial'], 0, False),
            (['0001_initial', '0002_GROUP_operations'], 0, False),
            (['0001_initial', '0002_group_operations'], 37, False),
        ]
        for rows, native_exit, accepted in cases:
            with self.subTest(rows=rows, native_exit=native_exit):
                result = self.smoke_fault('go', rows=rows, ledger_exit=native_exit)
                self.assertEqual(result.returncode == 0, accepted, result.stdout + result.stderr)
                self.assertIn('ENV_CLEAN=True', result.stdout)
                self.assertEqual('PASS:' in result.stdout, accepted)


    def test_e2e_ledger_assertion_preserves_records_and_native_failures(self):
        import ast
        import os
        import types
        path = ROOT / 'tests/e2e/go_tls_messaging.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
        helpers = [next(node for node in main.body if isinstance(node, ast.FunctionDef) and node.name == name)
                   for name in ('docker', 'compose', 'sql')]
        require = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'require')
        assertions = [node for node in ast.walk(main) if isinstance(node, ast.Expr)
                      and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                      and node.value.func.id == 'require' and len(node.value.args) == 2
                      and isinstance(node.value.args[1], ast.Constant)
                      and node.value.args[1].value == 'canonical migration missing']
        self.assertEqual(len(assertions), 1)
        boundary = compile(ast.fix_missing_locations(ast.Module(body=[require, *helpers, assertions[0]], type_ignores=[])), str(path), 'exec')
        cases = (
            (['0001_initial', '0002_group_operations'], 0, True),
            (['0001_initial\n0002_group_operations'], 0, False),
            (['0001_initial,0002_group_operations'], 0, False),
            ([], 0, False), (['0001_initial'], 0, False),
            (['0001_initial', '0002_group_operations', '0003_unknown'], 0, False),
            (['0001_initial', '0001_initial', '0002_group_operations'], 0, False),
            (['0002_group_operations', '0001_initial'], 0, False),
            (['0001_initial', '0002_GROUP_operations'], 0, False),
            (['0001_initial', '0002_group_operations'], 37, False),
        )
        for rows, native_exit, accepted in cases:
            with self.subTest(rows=rows, native_exit=native_exit):
                observed = []
                def transport(arguments, **options):
                    query = arguments[-1]
                    observed.append(query)
                    if query == 'SELECT version FROM schema_migrations ORDER BY version':
                        transcript = '\n'.join(rows)
                    elif query == 'SELECT json_agg(version ORDER BY version) FROM schema_migrations':
                        transcript = json.dumps(rows) if rows else 'null'
                    else:
                        raise AssertionError('unexpected actual E2E ledger SQL: ' + query)
                    # Execute the real native failure path while replacing only
                    # Docker transport. This is not live Docker/TLS acceptance.
                    return subprocess.run([sys.executable, '-c',
                                           "import sys;sys.stdout.buffer.write(sys.argv[1].encode('utf-8'));sys.stderr.write('E2E_LEDGER_NATIVE_SENTINEL');sys.exit(int(sys.argv[2]))",
                                           transcript + '\n', str(native_exit)],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
                scope = {'json': json, 'env': os.environ.copy(), 'command': ['isolated-docker'],
                         'subprocess': types.SimpleNamespace(run=transport, PIPE=subprocess.PIPE)}
                if accepted:
                    exec(boundary, scope)
                elif native_exit:
                    with self.assertRaisesRegex(RuntimeError, 'E2E_LEDGER_NATIVE_SENTINEL'):
                        exec(boundary, scope)
                else:
                    with self.assertRaisesRegex(AssertionError, 'canonical migration missing'):
                        exec(boundary, scope)
                self.assertEqual(len(observed), 1)



if __name__ == '__main__':
    unittest.main()