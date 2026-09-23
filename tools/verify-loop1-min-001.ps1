param([switch]$SkipScope)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$contractPath = Join-Path $root 'spec/governance/minimality.md'
$agentsPath = Join-Path $root 'AGENTS.md'
$templatePath = Join-Path $root 'spec/tasks/TASK_TEMPLATE.md'
$taskPaths = @('active', 'review', 'done') | ForEach-Object { Join-Path $root "spec/tasks/$_/LOOP1-MIN-001.md" }
$failures = [System.Collections.Generic.List[string]]::new()

function Require([bool]$condition, [string]$message) {
    if (-not $condition) { $script:failures.Add($message) }
}

Require (Test-Path $contractPath) 'canonical Minimality Contract missing'
Require ((@($taskPaths | Where-Object { Test-Path $_ })).Count -eq 1) 'LOOP1-MIN-001 must exist in exactly one active/review/done queue'
if (Test-Path $contractPath) {
    $contract = Get-Content -Raw -LiteralPath $contractPath
    $clauses = @(
        'Every additional abstraction must pay rent',
        'current approved requirements',
        'observed implementation constraints',
        'future stages',
        'insufficient on their own',
        'Necessary boundaries and abstractions remain valid',
        'If this code or abstraction were removed or simplified',
        'Personal style preference',
        'not findings',
        'Reviewers cannot change product requirements, public contracts, or Frozen Architecture',
        'subordinate to Frozen Architecture'
    )
    function Test-Policy([string]$text) {
        foreach ($clause in $clauses) {
            if (-not $text.Contains($clause)) { return $false }
        }
        # These narrow checks reject explicit permissions that negate the guard.
        # They are representative policy controls, not a style or complexity score.
        $contradictions = @(
            'future.stage infrastructure[^.\r\n]{0,160}\b(may|can|allowed|permitted)\b[^.\r\n]{0,160}\b(solely|only)\b[^.\r\n]{0,160}\b(future|might|possible)\b',
            'abstractions?[^.\r\n]{0,160}\bwithout current (requirements?|justification)\b[^.\r\n]{0,160}\b(may|can|allowed|permitted)\b',
            'minimality[^.\r\n]{0,160}\b(overrides?|supersedes?)\b[^.\r\n]{0,160}\bFrozen Architecture\b',
            'reviewers?[^.\r\n]{0,160}\b(may|can|allowed|permitted)\b[^.\r\n]{0,160}\b(rewrite|change|modify)\b[^.\r\n]{0,160}\b(public contracts?|contracts?)\b'
        )
        foreach ($pattern in $contradictions) {
            if ([regex]::IsMatch($text, $pattern, [Text.RegularExpressions.RegexOptions]::IgnoreCase)) { return $false }
        }
        return $true
    }
    Require (Test-Policy $contract) 'canonical contract lacks a required clause or contains contradictory permission'
}
$agents = Get-Content -Raw -LiteralPath $agentsPath
$template = Get-Content -Raw -LiteralPath $templatePath
Require ($agents.Contains('spec/governance/minimality.md')) 'AGENTS.md does not link canonical contract'
Require ($agents.Contains('MUST choose the simplest implementation') -and $agents.Contains('MUST NOT implement future-stage mechanisms')) 'implementation instruction missing'
Require ($agents.Contains('Review Agents MUST check unnecessary complexity')) 'review instruction missing'
Require ($template.Contains('# Minimality') -and $template.Contains('current justification')) 'Task Template minimality prompt missing'

# Exercise the same policy check against disposable contradictory clauses.
# Necessary, currently justified complexity must still be accepted.
if (Test-Path $contractPath) {
    $controls = @(
        @{ Name = 'future-only rationale'; Clause = 'Future-stage infrastructure may be added solely because a future stage might need it.' },
        @{ Name = 'unjustified abstraction'; Clause = 'Abstractions without current requirements may be added for future reuse.' },
        @{ Name = 'architecture precedence'; Clause = 'Minimality overrides Frozen Architecture when simpler.' },
        @{ Name = 'contract rewrite'; Clause = 'Reviewers may rewrite public contracts to simplify them.' }
    )
    foreach ($control in $controls) {
        $mutant = "$contract`n$($control.Clause)"
        Require (-not (Test-Policy $mutant)) "negative control failed: $($control.Name)"
    }
    $necessary = "$contract`nA repository abstraction is required by the current atomic transaction boundary."
    Require (Test-Policy $necessary) 'necessary current complexity was mechanically rejected'
}

if (-not $SkipScope) {
    $base = '1c274bcbf92ebcc05c1bc208386c5976437d8221'
    $names = @(& git -C $root diff --name-only $base --)
    $names += @(& git -C $root ls-files --others --exclude-standard)
    function Test-TaskRecorderPath([string]$name) {
        if ($name -notmatch '^research/(prompts/(P-[0-9a-f-]{36})/(metadata\.json|prompt\.txt)|runs/(R-[0-9]{8}T[0-9]{6}Z-[0-9a-f-]{36})/(metadata\.json|initial_state\.json|events\.jsonl|final_state\.json|summary\.json|diff\.patch|blobs/C-[0-9a-f-]{36}\.(stdout|stderr)\.txt))$') {
            return $false
        }
        $kind = if ($Matches[2]) { 'prompts' } else { 'runs' }
        $id = if ($kind -eq 'prompts') { $Matches[2] } else { $Matches[4] }
        $metadataPath = Join-Path $root "research/$kind/$id/metadata.json"
        if (-not (Test-Path -LiteralPath $metadataPath)) { return $false }
        try { $metadata = Get-Content -Raw -LiteralPath $metadataPath | ConvertFrom-Json }
        catch { return $false }
        return $metadata.task_id -eq 'LOOP1-MIN-001' -and
            $(if ($kind -eq 'prompts') { $metadata.prompt_id -eq $id } else { $metadata.run_id -eq $id })
    }
    foreach ($name in ($names | Sort-Object -Unique)) {
        $allowed = $name -eq 'AGENTS.md' -or
            $name -eq 'spec/governance/minimality.md' -or
            $name -eq 'spec/tasks/TASK_TEMPLATE.md' -or
            $name -match '^spec/tasks/(active|review|done)/LOOP1-MIN-001\.md$' -or
            $name -eq 'tools/verify-loop1-min-001.ps1' -or
            $name -eq 'spec/progress/current.md' -or
            $name -match '^spec/progress/(evidence/LOOP1-MIN-001/|checkpoints/.*loop1-min-001)' -or
            (Test-TaskRecorderPath $name)
        Require $allowed "out-of-scope path: $name"
    }
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}
Write-Output 'PASS: minimality governance links, authority, review controls, negative controls, and scope verified.'
