[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$failures = [System.Collections.Generic.List[string]]::new()

function Require-Path([string]$relativePath, [string]$kind = 'Any') {
    $path = Join-Path $repoRoot $relativePath
    $exists = if ($kind -eq 'Container') { Test-Path -LiteralPath $path -PathType Container } elseif ($kind -eq 'Leaf') { Test-Path -LiteralPath $path -PathType Leaf } else { Test-Path -LiteralPath $path }
    if (-not $exists) { $failures.Add("Missing $kind path: $relativePath") }
}

$requiredFiles = @(
    'AGENTS.md',
    'CLAUDE.md',
    'README.md',
    'scalable-distributed-im-architecture.pdf',
    'spec/architecture/frozen-architecture.md',
    'spec/architecture/README.md',
    'spec/architecture/baseline.md',
    'spec/architecture/decisions/ADR-0001-temporary-s0-bootstrap-acceptance-before-ci-availability.md',
    'spec/batches/LOOP1-S0.md',
    'spec/handoff/agent-context.md',
    'spec/progress/current.md',
    'spec/tasks/TASK_TEMPLATE.md'
)
$requiredDirectories = @(
    'spec/architecture', 'spec/architecture/decisions', 'spec/domain', 'spec/invariants', 'spec/acceptance',
    'spec/batches', 'spec/progress/checkpoints', 'spec/progress/evidence', 'spec/tasks/backlog', 'spec/tasks/ready', 'spec/tasks/active', 'spec/tasks/review', 'spec/tasks/done',
    'contracts', 'contracts/http', 'contracts/websocket', 'contracts/errors', 'contracts/database', 'contracts/plugin-api', 'contracts/fixtures',
    'backend/go/gateway', 'backend/go/core', 'backend/go/plugin-host', 'backend/go/tests',
    'backend/java/gateway', 'backend/java/core', 'backend/java/plugin-host', 'backend/java/tests',
    'clients/shared/protocol-sdk', 'clients/shared/plugin-sdk', 'clients/shared/ui', 'clients/web', 'clients/desktop', 'clients/mobile',
    'plugins/fixtures/echo', 'plugins/fixtures/poll',
    'tests/contract', 'tests/integration', 'tests/e2e', 'tests/compatibility', 'tests/load',
    'deploy/compose', 'deploy/proxy', 'deploy/observability', 'ci', 'tools'
)

$requiredFiles | ForEach-Object { Require-Path $_ 'Leaf' }
$requiredDirectories | ForEach-Object { Require-Path $_ 'Container' }

$claudeExpected = @'
Before doing any work in this repository, read and follow `./AGENTS.md`.

`AGENTS.md` is the authoritative repository-level instruction entrypoint. Do not maintain a separate copy of repository rules in `CLAUDE.md`.
'@.Trim()
if ((Get-Content -Raw (Join-Path $repoRoot 'CLAUDE.md')).Trim() -cne $claudeExpected) {
    $failures.Add('CLAUDE.md must contain only the approved AGENTS.md routing text.')
}

$readme = Get-Content -Raw (Join-Path $repoRoot 'README.md')
if ($readme -notmatch 'AI / coding agents must read \[AGENTS\.md\]\(\./AGENTS\.md\) first\.') {
    $failures.Add('README.md does not direct AI/coding agents to AGENTS.md first.')
}

$agentRules = Get-Content -Raw (Join-Path $repoRoot 'AGENTS.md')
$agentRulePatterns = @(
    'spec/handoff/agent-context\.md', 'spec/progress/current\.md', 'spec/tasks/\{review,active,ready,backlog,done\}/',
    'git status', 'current diff', 'Recent commits', 'baseline verification', 'allowed_paths', 'contracts/',
    'BLOCKED_BY_ARCHITECTURE', 'CI is the independent acceptance judge', 'spec/architecture/README\.md', 'checkpoint'
)
foreach ($pattern in $agentRulePatterns) {
    if ($agentRules -notmatch $pattern) { $failures.Add("AGENTS.md is missing required rule pattern: $pattern") }
}

$taskTemplate = Get-Content -Raw (Join-Path $repoRoot 'spec/tasks/TASK_TEMPLATE.md')
$taskFields = @('task_id', 'title', 'status', 'owner', 'stage', 'gate', '# Goal', '# Inputs', '# Dependencies', '# Allowed Paths', '# Acceptance', '# Forbidden', '# Verification', '# Evidence', '# Handoff', '# Next Action')
foreach ($field in $taskFields) {
    if (-not $taskTemplate.Contains($field)) { $failures.Add("Task template is missing: $field") }
}

$expectedTasks = @('LOOP1-CTRL-002', 'LOOP1-SPEC-001', 'LOOP1-CONTRACT-001', 'LOOP1-CONTRACT-002', 'LOOP1-CONTRACT-003', 'LOOP1-DB-001', 'LOOP1-INFRA-001', 'LOOP1-CI-001')
foreach ($taskId in $expectedTasks) {
    $matches = @(Get-ChildItem -LiteralPath (Join-Path $repoRoot 'spec/tasks') -Recurse -File -Filter "$taskId.md")
    if ($matches.Count -ne 1) {
        $failures.Add("Expected exactly one Task Spec for $taskId across all task queues; found $($matches.Count).")
        continue
    }
    $declaredStatusMatch = Select-String -LiteralPath $matches[0].FullName -Pattern '^status:\s*(\w+)' | Select-Object -First 1
    if (-not $declaredStatusMatch) {
        $failures.Add("Task Spec has no status field: $taskId")
        continue
    }
    $declaredStatus = $declaredStatusMatch.Matches[0].Groups[1].Value
    if ($declaredStatus -ne $matches[0].Directory.Name) {
        $failures.Add("Task queue/status mismatch for ${taskId}: directory=$($matches[0].Directory.Name), status=$declaredStatus")
    }
}

$architectureFiles = @(Get-ChildItem -LiteralPath (Join-Path $repoRoot 'spec/architecture') -File -Recurse | ForEach-Object { $_.FullName.Substring($repoRoot.Length + 1).Replace('\', '/') })
$unexpectedArchitectureFiles = @($architectureFiles | Where-Object {
    $_ -notin @('spec/architecture/README.md', 'spec/architecture/baseline.md', 'spec/architecture/frozen-architecture.md', 'spec/architecture/decisions/.gitkeep') -and
    $_ -notmatch '^spec/architecture/decisions/ADR-[0-9]{4}-.+\.md$'
})
if ($unexpectedArchitectureFiles.Count -gt 0) {
    $failures.Add("Unexpected architecture authority file(s): $($unexpectedArchitectureFiles -join ', ')")
}

$manifest = Get-Content -Raw (Join-Path $repoRoot 'spec/architecture/baseline.md')
$manifestPathMatch = [regex]::Match($manifest, '(?m)^- repository_path:\s*`([^`]+)`\s*$')
$manifestHashMatch = [regex]::Match($manifest, '(?m)^- sha256:\s*`([0-9a-fA-F]{64})`\s*$')
if (-not $manifestPathMatch.Success -or -not $manifestHashMatch.Success) {
    $failures.Add('Architecture baseline manifest is not machine-resolvable.')
} else {
    $baselinePath = Join-Path $repoRoot $manifestPathMatch.Groups[1].Value
    if (-not (Test-Path -LiteralPath $baselinePath -PathType Leaf)) {
        $failures.Add("Frozen Architecture artifact is missing: $($manifestPathMatch.Groups[1].Value)")
    } else {
        $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $baselinePath).Hash.ToLowerInvariant()
        if ($actualHash -ne $manifestHashMatch.Groups[1].Value.ToLowerInvariant()) { $failures.Add('Frozen Architecture artifact hash does not match the baseline manifest.') }
        & git -C $repoRoot -c core.excludesFile=.git/info/exclude ls-files --error-unmatch -- $manifestPathMatch.Groups[1].Value *> $null
        if ($LASTEXITCODE -ne 0) { $failures.Add('Frozen Architecture artifact is not tracked by Git.') }
    }
}

$implementationRoots = @('backend', 'clients', 'plugins')
$prematureFiles = foreach ($root in $implementationRoots) {
    Get-ChildItem -LiteralPath (Join-Path $repoRoot $root) -File -Recurse | Where-Object { $_.Name -ne '.gitkeep' }
}
if (@($prematureFiles).Count -gt 0) {
    $failures.Add("Premature S1/product implementation files found: $((@($prematureFiles).FullName | ForEach-Object { $_.Substring($repoRoot.Length + 1) }) -join ', ')")
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output "PASS: LOOP1-CTRL-001 repository structure and governance checks succeeded ($($requiredFiles.Count) files, $($requiredDirectories.Count) directories, $($expectedTasks.Count) tracked S0 tasks)."
& (Join-Path $repoRoot 'tools/verify-frozen-architecture.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
