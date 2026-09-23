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
    function Test-Clauses([string]$text) {
        foreach ($clause in $clauses) {
            if (-not $text.Contains($clause)) { return $false }
        }
        return $true
    }
    Require (Test-Clauses $contract) 'canonical contract lacks a required governance clause'
}
$agents = Get-Content -Raw -LiteralPath $agentsPath
$template = Get-Content -Raw -LiteralPath $templatePath
Require ($agents.Contains('spec/governance/minimality.md')) 'AGENTS.md does not link canonical contract'
Require ($agents.Contains('MUST choose the simplest implementation') -and $agents.Contains('MUST NOT implement future-stage mechanisms')) 'implementation instruction missing'
Require ($agents.Contains('Review Agents MUST check unnecessary complexity')) 'review instruction missing'
Require ($template.Contains('# Minimality') -and $template.Contains('current justification')) 'Task Template minimality prompt missing'

# Disposable negative controls verify that the guard fails when its essential
# clauses are removed. They do not alter repository artifacts or score code.
if (Test-Path $contractPath) {
    $controls = @(
        @{ Name = 'future-only rationale'; Needle = 'insufficient on their own' },
        @{ Name = 'unjustified abstraction'; Needle = 'current approved requirements' },
        @{ Name = 'necessary complexity'; Needle = 'Necessary boundaries and abstractions remain valid' },
        @{ Name = 'architecture precedence'; Needle = 'subordinate to Frozen Architecture' },
        @{ Name = 'contract rewrite'; Needle = 'Reviewers cannot change product requirements, public contracts, or Frozen Architecture' }
    )
    foreach ($control in $controls) {
        $mutant = $contract.Replace($control.Needle, '')
        Require (-not (Test-Clauses $mutant)) "negative control failed: $($control.Name)"
    }
}

if (-not $SkipScope) {
    $base = '1c274bcbf92ebcc05c1bc208386c5976437d8221'
    $names = @(& git -C $root diff --name-only $base --)
    $names += @(& git -C $root ls-files --others --exclude-standard)
    foreach ($name in ($names | Sort-Object -Unique)) {
        $allowed = $name -eq 'AGENTS.md' -or
            $name -eq 'spec/governance/minimality.md' -or
            $name -eq 'spec/tasks/TASK_TEMPLATE.md' -or
            $name -match '^spec/tasks/(active|review|done)/LOOP1-MIN-001\.md$' -or
            $name -eq 'tools/verify-loop1-min-001.ps1' -or
            $name -eq 'spec/progress/current.md' -or
            $name -match '^spec/progress/(evidence/LOOP1-MIN-001/|checkpoints/.*loop1-min-001)' -or
            $name -match '^research/(prompts/P-d7268d90-c7bb-4440-9406-7a27b633f0bb/|runs/R-20260923T012916Z-b5c2c3a1-df94-402c-9360-647e21e0ea2b/)'
        Require $allowed "out-of-scope path: $name"
    }
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}
Write-Output 'PASS: minimality governance links, authority, review controls, negative controls, and scope verified.'
