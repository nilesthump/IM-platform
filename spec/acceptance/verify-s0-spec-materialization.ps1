[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

$requiredFiles = @(
    'spec/domain/auth-user-friend.md',
    'spec/domain/messaging.md',
    'spec/domain/sync-plugin.md',
    'spec/invariants/auth-user-friend.md',
    'spec/invariants/messaging.md',
    'spec/invariants/sync-plugin.md',
    'spec/acceptance/s0-auth-user-friend.md',
    'spec/acceptance/s0-messaging.md',
    'spec/acceptance/s0-sync-plugin.md'
)

$failures = @()
$allRuleIds = @()

foreach ($relativePath in $requiredFiles) {
    $fullPath = Join-Path $repoRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        $failures += "missing required file: $relativePath"
        continue
    }

    $content = Get-Content -LiteralPath $fullPath -Raw
    $rows = @($content -split "`r?`n" | Where-Object { $_ -match '^\| (AUF|MSG|SP)-(D|I|A)-\d{3} \|' })
    if ($rows.Count -eq 0) {
        $failures += "no rule rows found: $relativePath"
        continue
    }

    foreach ($row in $rows) {
        $ruleId = [regex]::Match($row, '^\| ((AUF|MSG|SP)-(D|I|A)-\d{3}) \|').Groups[1].Value
        $allRuleIds += $ruleId
        if ($row -notmatch '\b(MUST|MUST NOT|MAY)\b') {
            $failures += "normative keyword missing: $relativePath $ruleId"
        }
        if ($row -notmatch 'Architecture Baseline v1\.0, (chapter|chapters|appendix) ') {
            $failures += "exact baseline citation missing: $relativePath $ruleId"
        }
    }

    $forbiddenPatterns = @(
        '(?im)^\s*```(?:json|ya?ml|sql|java|go|typescript|ts)\s*$',
        '(?im)\bCREATE\s+TABLE\b',
        '(?im)\bALTER\s+TABLE\b',
        '(?im)\bDROP\s+TABLE\b',
        '(?im)\b(class|interface)\s+[A-Z][A-Za-z0-9_]*\s*[\{:]'
    )
    foreach ($pattern in $forbiddenPatterns) {
        if ($content -match $pattern) {
            $failures += "forbidden implementation/schema leakage: $relativePath pattern=$pattern"
        }
    }
}

$duplicates = @($allRuleIds | Group-Object | Where-Object Count -gt 1 | Select-Object -ExpandProperty Name)
if ($duplicates.Count -gt 0) {
    $failures += "duplicate rule identifiers: $($duplicates -join ', ')"
}

$expectedPrefixes = @('AUF-D', 'MSG-D', 'SP-D', 'AUF-I', 'MSG-I', 'SP-I', 'AUF-A', 'MSG-A', 'SP-A')
foreach ($prefix in $expectedPrefixes) {
    if (-not ($allRuleIds | Where-Object { $_ -like "$prefix-*" })) {
        $failures += "missing rule family: $prefix"
    }
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "PASS: S0 specification materialization verified files=$($requiredFiles.Count) rules=$($allRuleIds.Count) citations=exact forbidden_leakage=absent."
exit 0
