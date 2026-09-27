[CmdletBinding()]
param([string]$BaseCommit = '')

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$manifestPath = Join-Path $root 'spec/architecture/baseline.md'
$manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath $manifestPath
$errors = [System.Collections.Generic.List[string]]::new()

function Field([string]$name) {
    $m = [regex]::Match($manifest, '(?m)^- ' + [regex]::Escape($name) + ':\s*`([^`]+)`\s*$')
    if (-not $m.Success) { $errors.Add("Missing manifest field: $name"); return '' }
    return $m.Groups[1].Value.Trim()
}
function Sha([string]$relative, [string]$expected, [string]$label) {
    $path = Join-Path $root $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { $errors.Add("Missing $label`: $relative"); return }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
    if ($actual -ne $expected.ToLowerInvariant()) { $errors.Add("$label SHA-256 mismatch: $relative actual=$actual expected=$expected") }
}

$format = Field 'canonical_format'
$canonical = Field 'repository_path'
$hash = Field 'sha256'
$previousFormat = Field 'previous_canonical_format'
$previous = Field 'previous_repository_path'
$previousHash = Field 'previous_sha256'
$migration = Field 'migration_type'
$semantic = Field 'semantic_change'
$taskId = Field 'migration_task_id'
if ($format -ne 'markdown' -or $canonical -ne 'spec/architecture/frozen-architecture.md') { $errors.Add('Active canonical source must be the one Frozen Architecture Markdown.') }
if ($previousFormat -ne 'pdf' -or $previous -ne 'scalable-distributed-im-architecture.pdf') { $errors.Add('Historical PDF identity mismatch.') }
if ($canonical -eq $previous) { $errors.Add('Active and previous canonical paths cannot be equal.') }
if ($hash -notmatch '^[0-9a-fA-F]{64}$' -or $previousHash -notmatch '^[0-9a-fA-F]{64}$') { $errors.Add('Both SHA-256 fields must be 64 hexadecimal characters.') }
if ($hash -eq $previousHash) { $errors.Add('Markdown and PDF hashes must be separate actual values.') }
if ($migration -ne 'representation_only' -or $semantic -ne 'false' -or $taskId -ne 'LOOP1-ARCHDOC-001') { $errors.Add('Representation-only migration metadata mismatch.') }
Sha $canonical $hash 'Canonical Markdown'
Sha $previous $previousHash 'Historical PDF'
$candidates = @(Get-ChildItem -LiteralPath (Join-Path $root 'spec/architecture') -File -Filter '*.md' | Where-Object { $_.Name -notin @('README.md','baseline.md') })
if ($candidates.Count -ne 1 -or $candidates[0].Name -ne 'frozen-architecture.md') { $errors.Add('Canonical Markdown path is not unique.') }
$index = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $root 'spec/architecture/README.md')
$agents = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $root 'AGENTS.md')
$handoff = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $root 'spec/handoff/agent-context.md')
$adr = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $root 'spec/architecture/decisions/ADR-0002-frozen-architecture-canonical-markdown-migration.md')
if ($index -notmatch 'canonical Markdown' -or $agents -notmatch 'canonical Frozen Architecture Markdown' -or $handoff -notmatch 'canonical Frozen Architecture Markdown') { $errors.Add('Governance must route future Agent recovery to Markdown.') }
if ($adr -notmatch 'Architect-approved' -or $adr -notmatch 'representation-only') { $errors.Add('Approved representation-only ADR is missing.') }
if ($index -notmatch 'historical PDF' -or $manifest -notmatch 'historical snapshot') { $errors.Add('PDF historical status is not explicit.') }
if ($BaseCommit) {
    & git -C $root cat-file -e "$BaseCommit^{commit}" 2>$null
    if ($LASTEXITCODE -ne 0) { $errors.Add("Base commit does not exist: $BaseCommit") }
    else {
        $changed = @(& git -C $root diff --name-only $BaseCommit HEAD -- contracts backend clients plugins)
        $changed += @(& git -C $root diff --name-only -- contracts backend clients plugins)
        $changed += @(& git -C $root diff --cached --name-only -- contracts backend clients plugins)
        if (@($changed | Where-Object { $_ }).Count -gt 0) { $errors.Add("Product contracts/implementation changed: $($changed -join ', ')") }
    }
}
if ($errors.Count) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }
Write-Output "PASS: canonical Markdown=$canonical sha256=$hash; historical PDF=$previous sha256=$previousHash; semantic_change=false"
exit 0
