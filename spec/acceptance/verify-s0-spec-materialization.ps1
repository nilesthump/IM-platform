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
$expectedRuleCounts = @{
    'spec/domain/auth-user-friend.md' = 9
    'spec/domain/messaging.md' = 9
    'spec/domain/sync-plugin.md' = 13
    'spec/invariants/auth-user-friend.md' = 7
    'spec/invariants/messaging.md' = 7
    'spec/invariants/sync-plugin.md' = 10
    'spec/acceptance/s0-auth-user-friend.md' = 8
    'spec/acceptance/s0-messaging.md' = 8
    'spec/acceptance/s0-sync-plugin.md' = 13
}

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
    if ($rows.Count -ne $expectedRuleCounts[$relativePath]) {
        $failures += "unexpected rule count: $relativePath expected=$($expectedRuleCounts[$relativePath]) actual=$($rows.Count)"
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

$syncPluginPaths = @(
    'spec/domain/sync-plugin.md',
    'spec/invariants/sync-plugin.md',
    'spec/acceptance/s0-sync-plugin.md'
)
foreach ($relativePath in $syncPluginPaths) {
    $content = Get-Content -LiteralPath (Join-Path $repoRoot $relativePath) -Raw
    if ($content -match '(?i)Action[^\r\n|]*rate[- ]limit') {
        $failures += "invented Action rate-limiting requirement: $relativePath"
    }
}

$syncPluginDomain = Get-Content -LiteralPath (Join-Path $repoRoot 'spec/domain/sync-plugin.md') -Raw
$syncPluginInvariants = Get-Content -LiteralPath (Join-Path $repoRoot 'spec/invariants/sync-plugin.md') -Raw
$syncPluginAcceptance = Get-Content -LiteralPath (Join-Path $repoRoot 'spec/acceptance/s0-sync-plugin.md') -Raw
if ($syncPluginDomain -notmatch '(?m)^\| SP-D-008 \| .*each Action MUST be re-authorized, idempotent, and audited') {
    $failures += 'incomplete Action domain semantics: spec/domain/sync-plugin.md SP-D-008'
}
if ($syncPluginInvariants -notmatch '(?m)^\| SP-I-006 \| .*each Action MUST be re-authorized at execution, MUST be idempotent, and MUST be auditable') {
    $failures += 'incomplete Action invariant semantics: spec/invariants/sync-plugin.md SP-I-006'
}
if ($syncPluginAcceptance -notmatch '(?m)^\| SP-A-013 \| .*repeated execution of the same Action.*one idempotent observable outcome.*no duplicate side effect.*audit evidence') {
    $failures += 'missing repeated-Action idempotent-outcome acceptance requirement: spec/acceptance/s0-sync-plugin.md SP-A-013'
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
