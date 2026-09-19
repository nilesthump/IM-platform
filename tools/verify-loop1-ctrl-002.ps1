[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$failures = [System.Collections.Generic.List[string]]::new()

function Add-Failure([string]$message) {
    $failures.Add($message)
}

function Require-File([string]$relativePath) {
    $path = Join-Path $repoRoot $relativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Add-Failure "Missing required file: $relativePath"
    }
}

function Require-Directory([string]$relativePath) {
    $path = Join-Path $repoRoot $relativePath
    if (-not (Test-Path -LiteralPath $path -PathType Container)) {
        Add-Failure "Missing required directory: $relativePath"
    }
}

function Require-Content([string]$content, [string[]]$requiredValues, [string]$sourceName) {
    foreach ($value in $requiredValues) {
        if (-not $content.Contains($value)) {
            Add-Failure "$sourceName is missing required content: $value"
        }
    }
}

function Require-OrderedContent([string]$content, [string[]]$orderedValues, [string]$sourceName) {
    $lastIndex = -1
    foreach ($value in $orderedValues) {
        $index = $content.IndexOf($value)
        if ($index -lt 0) {
            Add-Failure "$sourceName is missing startup step: $value"
            continue
        }
        if ($index -le $lastIndex) {
            Add-Failure "$sourceName has an out-of-order startup step: $value"
        }
        $lastIndex = $index
    }
}

$requiredFiles = @(
    'AGENTS.md',
    'CLAUDE.md',
    'spec/architecture/README.md',
    'spec/handoff/agent-context.md',
    'spec/progress/current.md',
    'spec/tasks/TASK_TEMPLATE.md',
    'spec/tasks/done/LOOP1-CTRL-001.md',
    'tools/verify-loop1-ctrl-001.ps1'
)
$requiredFiles | ForEach-Object { Require-File $_ }

$queueNames = @('backlog', 'ready', 'active', 'review', 'done')
$queueNames | ForEach-Object { Require-Directory "spec/tasks/$_" }

if ($failures.Count -eq 0) {
    $agentRules = Get-Content -Raw (Join-Path $repoRoot 'AGENTS.md')
    Require-OrderedContent $agentRules @(
        'spec/handoff/agent-context.md',
        'spec/progress/current.md',
        'spec/tasks/active/',
        'Every architecture document',
        'git status',
        'current diff',
        'Recent commits',
        'baseline verification'
    ) 'AGENTS.md'
    Require-Content $agentRules @(
        'spec/tasks/ready/',
        'allowed_paths',
        'BLOCKED_BY_ARCHITECTURE',
        'CI is the independent acceptance judge'
    ) 'AGENTS.md'

    $current = Get-Content -Raw (Join-Path $repoRoot 'spec/progress/current.md')
    Require-Content $current @(
        'Current Loop:',
        'Current Stage:',
        'Current Gate:',
        'S0 Gate Status: NOT YET PASSED',
        'Current Task: LOOP1-CTRL-002',
        '## Completed',
        '## In Progress',
        '## Blocked',
        '## Verification Evidence',
        '## Changed Files / Migrations',
        '## Known Failures / Risks / Assumptions',
        '## Next Exact Action',
        '## Last Known Good Commit',
        '## Latest Checkpoint',
        '## Uncommitted Changes'
    ) 'spec/progress/current.md'

    $context = Get-Content -Raw (Join-Path $repoRoot 'spec/handoff/agent-context.md')
    Require-Content $context @(
        'milestone-gated',
        'Frozen Architecture',
        'contracts/',
        'allowed_paths',
        'CI is an independent judge',
        'completed work',
        'changed files or migrations',
        'verification command and result',
        'known failures/risks/assumptions',
        'next exact action',
        'last known good commit',
        'uncommitted-change ownership',
        'architecture conflict',
        'checkpoint'
    ) 'spec/handoff/agent-context.md'

    $template = Get-Content -Raw (Join-Path $repoRoot 'spec/tasks/TASK_TEMPLATE.md')
    Require-Content $template @(
        'task_id:', 'title:', 'status:', 'owner:', 'stage:', 'gate:',
        '# Goal', '# Inputs', '# Dependencies', '# Allowed Paths', '# Acceptance',
        '# Forbidden', '# Verification', '# Evidence', '# Handoff', '# Next Action'
    ) 'spec/tasks/TASK_TEMPLATE.md'

    $claudeExpected = @'
Before doing any work in this repository, read and follow `./AGENTS.md`.

`AGENTS.md` is the authoritative repository-level instruction entrypoint. Do not maintain a separate copy of repository rules in `CLAUDE.md`.
'@.Trim()
    if ((Get-Content -Raw (Join-Path $repoRoot 'CLAUDE.md')).Trim() -cne $claudeExpected) {
        Add-Failure 'CLAUDE.md is not the approved minimal route to AGENTS.md.'
    }
}

$taskFiles = foreach ($queue in $queueNames) {
    Get-ChildItem -LiteralPath (Join-Path $repoRoot "spec/tasks/$queue") -File | Where-Object { $_.Name -ne '.gitkeep' }
}
$activeTasks = @($taskFiles | Where-Object { $_.Directory.Name -eq 'active' })
$currentTaskMatch = [regex]::Match($current, '(?m)^Current Task:\s*LOOP1-CTRL-002\s*\((active|review)\)\s*$')
if (-not $currentTaskMatch.Success) {
    Add-Failure 'Current Task must identify LOOP1-CTRL-002 in active or review state.'
    $currentTaskState = 'active'
} else {
    $currentTaskState = $currentTaskMatch.Groups[1].Value
}

$currentTaskFiles = @($taskFiles | Where-Object { $_.Name -eq 'LOOP1-CTRL-002.md' })
if ($currentTaskFiles.Count -ne 1) {
    Add-Failure "Expected exactly one LOOP1-CTRL-002 Task Spec across all task queues; found $($currentTaskFiles.Count)."
} elseif ($currentTaskFiles[0].Directory.Name -ne $currentTaskState) {
    Add-Failure "Current-state/task-queue mismatch for LOOP1-CTRL-002: current=$currentTaskState, queue=$($currentTaskFiles[0].Directory.Name)"
} else {
    $currentTask = Get-Content -Raw $currentTaskFiles[0].FullName
    Require-Content $currentTask @(
        'task_id: LOOP1-CTRL-002',
        "status: $currentTaskState",
        'owner: loop1-control-agent',
        '# Goal', '# Inputs', '# Dependencies', '# Allowed Paths', '# Acceptance',
        '# Forbidden', '# Verification', '# Evidence', '# Handoff', '# Next Action',
        'LOOP1-CTRL-001 done',
        'tools/**'
    ) "$currentTaskState LOOP1-CTRL-002 Task Spec"
}

if ($currentTaskState -eq 'active' -and ($activeTasks.Count -ne 1 -or $activeTasks[0].Name -ne 'LOOP1-CTRL-002.md')) {
    Add-Failure 'The active recovery state requires exactly one active task: LOOP1-CTRL-002.'
}
if ($currentTaskState -eq 'review' -and $activeTasks.Count -ne 0) {
    Add-Failure 'The review handoff state must not retain an active task.'
}

foreach ($taskFile in $taskFiles) {
    $declaredStatusMatch = Select-String -LiteralPath $taskFile.FullName -Pattern '^status:\s*(\w+)' | Select-Object -First 1
    if (-not $declaredStatusMatch) {
        Add-Failure "Task has no status field: $($taskFile.FullName)"
        continue
    }
    $declaredStatus = $declaredStatusMatch.Matches[0].Groups[1].Value
    if ($declaredStatus -ne $taskFile.Directory.Name) {
        Add-Failure "Task queue/status mismatch: $($taskFile.Name) is in $($taskFile.Directory.Name) but declares $declaredStatus"
    }
}

$activeS1Tasks = @($activeTasks | Where-Object {
    (Get-Content -Raw $_.FullName) -match '(?m)^stage:\s*S1\s*$'
})
if ($activeS1Tasks.Count -gt 0) {
    Add-Failure 'An S1 task is active before S0 Gate PASS.'
}

if (Test-Path -LiteralPath (Join-Path $repoRoot '.github/workflows') -PathType Container) {
    Add-Failure '.github/workflows must not be created before LOOP1-CI-001.'
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output 'DRY-RUN 1/6 PASS: read spec/handoff/agent-context.md for long-lived rules.'
Write-Output "DRY-RUN 2/6 PASS: read spec/progress/current.md and located Loop 1 / S0 / LOOP1-CTRL-002 ($currentTaskState)."
Write-Output 'DRY-RUN 3/6 PASS: found exactly one current Task Spec and recovered goal, dependencies, allowed paths, acceptance, forbidden work, verification, and next action.'
Write-Output 'DRY-RUN 4/6 PASS: resolved the referenced repository authority inputs without treating implementation as authority.'
Write-Output 'DRY-RUN 5/6 PASS: repository recovery sequence requires status, diff, and recent commits before implementation.'
Write-Output 'DRY-RUN 6/6 PASS: minimum CTRL-001 baseline verification is present and CTRL-002 recovery verification completed.'
Write-Output "PASS: LOOP1-CTRL-002 Agent recovery control-plane checks succeeded ($($taskFiles.Count) task files, $($queueNames.Count) task queues)."
