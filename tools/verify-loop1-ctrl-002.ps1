[CmdletBinding()]
param(
    [ValidateSet('Acceptance', 'Development')]
    [string]$Mode = 'Acceptance'
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$failures = [System.Collections.Generic.List[string]]::new()
$queueNames = @('backlog', 'ready', 'active', 'review', 'done')

function Add-Failure([string]$message) {
    $failures.Add($message)
}

function Require-File([string]$relativePath) {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $relativePath) -PathType Leaf)) {
        Add-Failure "Missing required file: $relativePath"
        return $false
    }
    return $true
}

function Get-Section([string]$content, [string]$heading) {
    $pattern = "(?ms)^# $([regex]::Escape($heading))\s*\r?\n(.*?)(?=^# |\z)"
    $match = [regex]::Match($content, $pattern)
    if (-not $match.Success) { return '' }
    return $match.Groups[1].Value
}

function Invoke-Git([string[]]$arguments, [string]$purpose) {
    $output = @(& git -C $repoRoot -c core.excludesFile=.git/info/exclude @arguments 2>&1)
    if ($LASTEXITCODE -ne 0) {
        Add-Failure "Unable to inspect git $purpose (exit $LASTEXITCODE): $($output -join ' ')"
    }
    return $output
}

$coreFiles = @(
    'AGENTS.md',
    'spec/handoff/agent-context.md',
    'spec/progress/current.md',
    'spec/tasks/TASK_TEMPLATE.md',
    'spec/architecture/README.md'
)
$coreFiles | ForEach-Object { [void](Require-File $_) }
foreach ($queue in $queueNames) {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot "spec/tasks/$queue") -PathType Container)) {
        Add-Failure "Missing task queue: spec/tasks/$queue"
    }
}

$agents = if (Test-Path -LiteralPath (Join-Path $repoRoot 'AGENTS.md')) { Get-Content -Raw (Join-Path $repoRoot 'AGENTS.md') } else { '' }
$orderedRules = @(
    'spec/handoff/agent-context.md',
    'spec/progress/current.md',
    'Current Task',
    'spec/tasks/{review,active,ready,backlog,done}/',
    'Every architecture document',
    'git status',
    'current diff',
    'Recent commits',
    'baseline verification'
)
$lastRuleIndex = -1
foreach ($rule in $orderedRules) {
    $ruleIndex = $agents.IndexOf($rule)
    if ($ruleIndex -lt 0) {
        Add-Failure "AGENTS.md is missing recovery rule: $rule"
    } elseif ($ruleIndex -le $lastRuleIndex) {
        Add-Failure "AGENTS.md recovery rule is out of order: $rule"
    } else {
        $lastRuleIndex = $ruleIndex
    }
}
foreach ($requiredRule in @('review', 'active', 'ready', 'backlog', 'done', 'Never select work merely because `active/` is empty', 'spec/architecture/README.md', 'Development-mode output and self-review are never acceptance evidence')) {
    if (-not $agents.Contains($requiredRule)) { Add-Failure "AGENTS.md is missing required governance: $requiredRule" }
}

$currentPath = Join-Path $repoRoot 'spec/progress/current.md'
$current = if (Test-Path -LiteralPath $currentPath) { Get-Content -Raw $currentPath } else { '' }
$taskIdMatch = [regex]::Match($current, '(?m)^Current Task:\s*`?([A-Z][A-Z0-9-]+)`?\s*$')
$taskStateMatch = [regex]::Match($current, '(?m)^Current Task State:\s*`?(backlog|ready|active|review|done)`?\s*$')
if (-not $taskIdMatch.Success) { Add-Failure 'current.md does not contain a parseable Current Task ID.' }
if (-not $taskStateMatch.Success) { Add-Failure 'current.md does not contain a parseable Current Task State.' }

$taskFiles = @()
foreach ($queue in $queueNames) {
    $queuePath = Join-Path $repoRoot "spec/tasks/$queue"
    if (Test-Path -LiteralPath $queuePath) {
        $taskFiles += @(Get-ChildItem -LiteralPath $queuePath -File -Filter '*.md')
    }
}

$currentTaskFile = $null
$currentTaskContent = ''
if ($taskIdMatch.Success) {
    $taskId = $taskIdMatch.Groups[1].Value
    $matches = @($taskFiles | Where-Object { $_.BaseName -eq $taskId })
    if ($matches.Count -ne 1) {
        Add-Failure "Current Task $taskId must resolve exactly once across all five queues; found $($matches.Count)."
    } else {
        $currentTaskFile = $matches[0]
        $currentTaskContent = Get-Content -Raw $currentTaskFile.FullName
        $declaredStatus = [regex]::Match($currentTaskContent, '(?m)^status:\s*(backlog|ready|active|review|done)\s*$')
        if (-not $declaredStatus.Success) {
            Add-Failure "Current Task $taskId has no valid status field."
        } else {
            $queueState = $currentTaskFile.Directory.Name
            if ($declaredStatus.Groups[1].Value -ne $queueState) { Add-Failure "Current Task status/queue mismatch: declared=$($declaredStatus.Groups[1].Value), queue=$queueState" }
            if ($taskStateMatch.Success -and $taskStateMatch.Groups[1].Value -ne $queueState) { Add-Failure "current.md/task queue mismatch: current=$($taskStateMatch.Groups[1].Value), queue=$queueState" }
        }
    }
}

foreach ($taskFile in $taskFiles) {
    $content = Get-Content -Raw $taskFile.FullName
    $idMatch = [regex]::Match($content, '(?m)^task_id:\s*([A-Z][A-Z0-9-]+)\s*$')
    $statusMatch = [regex]::Match($content, '(?m)^status:\s*(backlog|ready|active|review|done)\s*$')
    if (-not $idMatch.Success -or $idMatch.Groups[1].Value -ne $taskFile.BaseName) { Add-Failure "Task ID/file mismatch: $($taskFile.FullName)" }
    if (-not $statusMatch.Success -or $statusMatch.Groups[1].Value -ne $taskFile.Directory.Name) { Add-Failure "Task queue/status mismatch: $($taskFile.FullName)" }
}

$architectureIndexPath = Join-Path $repoRoot 'spec/architecture/README.md'
if (Test-Path -LiteralPath $architectureIndexPath) {
    $architectureIndex = Get-Content -Raw $architectureIndexPath
    $manifestLink = [regex]::Match($architectureIndex, '\[baseline manifest\]\(([^)]+)\)')
    if (-not $manifestLink.Success) {
        Add-Failure 'Architecture index does not resolve a baseline manifest.'
    } else {
        $manifestPath = [IO.Path]::GetFullPath((Join-Path (Split-Path $architectureIndexPath) $manifestLink.Groups[1].Value))
        if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
            Add-Failure "Architecture baseline manifest is missing: $manifestPath"
        } else {
            $manifest = Get-Content -Raw $manifestPath
            $artifactMatch = [regex]::Match($manifest, '(?m)^- repository_path:\s*`([^`]+)`\s*$')
            $hashMatch = [regex]::Match($manifest, '(?m)^- sha256:\s*`([0-9a-fA-F]{64})`\s*$')
            if (-not $artifactMatch.Success -or -not $hashMatch.Success) {
                Add-Failure 'Architecture manifest must contain repository_path and SHA-256.'
            } else {
                $artifactRelative = $artifactMatch.Groups[1].Value
                $artifactPath = Join-Path $repoRoot $artifactRelative
                if (-not (Test-Path -LiteralPath $artifactPath -PathType Leaf)) {
                    Add-Failure "Frozen Architecture artifact is missing: $artifactRelative"
                } else {
                    $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $artifactPath).Hash.ToLowerInvariant()
                    if ($actualHash -ne $hashMatch.Groups[1].Value.ToLowerInvariant()) { Add-Failure "Frozen Architecture hash mismatch: $artifactRelative" }
                    [void](Invoke-Git @('ls-files', '--error-unmatch', '--', $artifactRelative) 'tracked Frozen Architecture artifact')
                    [void](Invoke-Git @('cat-file', '-e', ":$artifactRelative") 'staged/committed Frozen Architecture blob')
                    $trackedPdfs = @(Invoke-Git @('ls-files', '--', '*.pdf') 'tracked PDF authority inventory')
                    if ($trackedPdfs.Count -ne 1 -or $trackedPdfs[0] -ne $artifactRelative) { Add-Failure "Expected exactly one tracked architecture PDF ($artifactRelative); found: $($trackedPdfs -join ', ')" }
                }
            }
        }
    }
}

if ($currentTaskFile) {
    $requiredHeadings = @('Goal', 'Inputs', 'Dependencies', 'Allowed Paths', 'Acceptance', 'Forbidden', 'Verification', 'Evidence', 'Handoff', 'Next Action')
    foreach ($heading in $requiredHeadings) {
        if ([string]::IsNullOrWhiteSpace((Get-Section $currentTaskContent $heading))) { Add-Failure "Current Task is missing a non-empty # $heading section." }
    }

    $inputs = Get-Section $currentTaskContent 'Inputs'
    $inputPaths = [regex]::Matches($inputs, '`([^`]+)`')
    foreach ($pathMatch in $inputPaths) {
        $inputPath = $pathMatch.Groups[1].Value
        if ($inputPath -match '[/\\]' -or $inputPath -match '\.[A-Za-z0-9]+$') {
            $resolvedInput = Join-Path $repoRoot $inputPath
            if (-not (Test-Path -LiteralPath $resolvedInput)) { Add-Failure "Unresolved Current Task input: $inputPath" }
        }
    }
    if ($inputs -match 'Architecture Baseline' -and $inputs -notmatch 'spec/architecture/README\.md') {
        Add-Failure 'Architecture inputs must resolve through spec/architecture/README.md.'
    }

    $dependencies = Get-Section $currentTaskContent 'Dependencies'
    foreach ($dependencyMatch in [regex]::Matches($dependencies, '([A-Z][A-Z0-9-]+)\s+done')) {
        $dependencyId = $dependencyMatch.Groups[1].Value
        $dependencyFiles = @($taskFiles | Where-Object { $_.BaseName -eq $dependencyId -and $_.Directory.Name -eq 'done' })
        if ($dependencyFiles.Count -ne 1) { Add-Failure "Unresolved completed dependency: $dependencyId" }
    }

    $verification = Get-Section $currentTaskContent 'Verification'
    $entryPoints = @([regex]::Matches($verification, '`(?:&\s+)?(?:\.\\)?(tools[\\/][^`\s]+)') | ForEach-Object { $_.Groups[1].Value.Replace('\', '/') })
    if ($entryPoints.Count -eq 0) {
        Add-Failure 'Current Task verification exposes no discoverable tools/ entry point.'
    } else {
        foreach ($entryPoint in $entryPoints) {
            if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $entryPoint) -PathType Leaf)) { Add-Failure "Missing verification entry point: $entryPoint" }
        }
    }
}

$branch = Invoke-Git @('rev-parse', '--abbrev-ref', 'HEAD') 'branch'
$status = Invoke-Git @('status', '--porcelain=v1', '--untracked-files=all') 'status'
$diff = Invoke-Git @('diff', '--stat', 'HEAD') 'current diff'
$recent = Invoke-Git @('log', '--oneline', '--decorate', '-n', '5') 'recent commits'
if ($Mode -eq 'Acceptance' -and @($status).Count -gt 0) {
    Add-Failure 'Acceptance mode requires a clean worktree and index. Re-run only from a clean committed checkout or isolated worktree.'
}
if ($Mode -eq 'Development') {
    Write-Output 'NON-ACCEPTANCE DEVELOPMENT MODE: dirty worktree is permitted; this output MUST NOT be used as acceptance evidence.'
}

if (Test-Path -LiteralPath (Join-Path $repoRoot '.github/workflows') -PathType Container) {
    $ciTask = @($taskFiles | Where-Object { $_.BaseName -eq 'LOOP1-CI-001' })
    if ($ciTask.Count -ne 1 -or $ciTask[0].Directory.Name -in @('backlog', 'ready')) {
        Add-Failure '.github/workflows exists before LOOP1-CI-001 is active.'
    }
}

if ($failures.Count -gt 0) {
    Write-Output "FAIL: recovery verification found $($failures.Count) issue(s)."
    $failures | ForEach-Object { Write-Output " - $_" }
    exit 1
}

$resolvedTask = if ($taskIdMatch.Success) { $taskIdMatch.Groups[1].Value } else { '<unresolved>' }
$resolvedState = if ($taskStateMatch.Success) { $taskStateMatch.Groups[1].Value } else { '<unresolved>' }
Write-Output "PASS: generic repository recovery verified task=$resolvedTask state=$resolvedState mode=$Mode queues=$($queueNames.Count) task_specs=$($taskFiles.Count)."
Write-Output "GIT: branch=$($branch -join '') status_entries=$(@($status).Count) diff_lines=$(@($diff).Count) recent_commits=$(@($recent).Count)."
