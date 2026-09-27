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
function Get-StructuralErrors([string]$doc) {
    $issues = [System.Collections.Generic.List[string]]::new()
    $fence = [string]::new([char]96, 3)
    if ($doc -match '(?m)^## 原 PDF 第 \d+ 页\s*$' -or ([regex]::Matches($doc, '(?m)^' + [regex]::Escape($fence) + 'text\s*$')).Count -ge 20) {
        $issues.Add('Canonical document is a page-fenced PDF text layout.')
    }
    foreach ($chapter in 0..21) {
        if ($doc -notmatch "(?m)^## $chapter\. \S") { $issues.Add("Missing native Markdown chapter $chapter.") }
    }
    foreach ($appendix in @('A','B')) {
        if ($doc -notmatch "(?m)^## 附录 $appendix\. \S") { $issues.Add("Missing native Markdown appendix $appendix.") }
    }
    $links = [regex]::Matches($doc, '(?m)^\s*- \[[^\]]+\]\(#([a-z0-9-]+)\)')
    $anchors = [regex]::Matches($doc, '(?m)^<a id="([a-z0-9-]+)"></a>$')
    $linkIds = @($links | ForEach-Object { $_.Groups[1].Value })
    $anchorIds = @($anchors | ForEach-Object { $_.Groups[1].Value })
    if ($linkIds.Count -lt 80 -or $linkIds.Count -ne $anchorIds.Count) { $issues.Add('Clickable table of contents is incomplete.') }
    if (@($linkIds | Sort-Object -Unique).Count -ne $linkIds.Count -or @($anchorIds | Sort-Object -Unique).Count -ne $anchorIds.Count) {
        $issues.Add('Table-of-contents anchors are not unique.')
    }
    foreach ($id in $linkIds) {
        if ($id -notin $anchorIds) { $issues.Add("TOC target missing: $id") }
    }
    $mermaid = [regex]::Matches($doc, '(?ms)^' + [regex]::Escape($fence) + 'mermaid\r?\n(.*?)^' + [regex]::Escape($fence) + '\s*$')
    if ($mermaid.Count -ne 9) { $issues.Add("Expected nine readable Mermaid figures; found $($mermaid.Count).") }
    $stageFigure = [regex]::Match($doc, '(?ms)^## 15\..*?^' + [regex]::Escape($fence) + 'mermaid\r?\n(.*?)^' + [regex]::Escape($fence))
    if (-not $stageFigure.Success) { $issues.Add('Missing Loop 1 stage figure 15-1.') }
    else {
        $stageGraph = $stageFigure.Groups[1].Value
        if (([regex]::Matches($stageGraph, 'Gate PASS')).Count -ne 7 -or ([regex]::Matches($stageGraph, '-->')).Count -ne 6) {
            $issues.Add('Figure 15-1 must retain seven stage Gate PASS labels and six progression arrows.')
        }
        foreach ($stage in 0..6) {
            if ($stageGraph -notmatch ('S' + $stage + '\["[^"\r\n]*<br/>Gate PASS"\]')) {
                $issues.Add("Figure 15-1 is missing the Gate PASS label for S$stage.")
            }
        }
    }
    foreach ($figure in @('0-1','3-1','4-1','5-1','6-1','9-1','12-1','14-1','15-1')) {
        if ($doc -notmatch [regex]::Escape("图 $figure")) { $issues.Add("Missing figure caption $figure.") }
    }
    if (([regex]::Matches($doc, '(?m)^\s*NATS --> PG\s*$')).Count -ne 2) {
        $issues.Add('Repeated deployment figures must retain the original NATS to PostgreSQL arrow.')
    }
    if (([regex]::Matches($doc, '(?m)^\| [^|]+ \|')).Count -lt 100) {
        $issues.Add('Native Markdown architecture tables are incomplete.')
    }
    return $issues
}
$architecture = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $root 'spec/architecture/frozen-architecture.md')
foreach ($issue in @(Get-StructuralErrors $architecture)) { $errors.Add($issue) }
# In-memory controls reject the prior layout, a lost index entry, and missing figures.
$fence = [string]::new([char]96, 3)
$oldLayoutMutant = ((1..28 | ForEach-Object { '## 原 PDF 第 ' + $_ + ' 页' + [Environment]::NewLine + $fence + 'text' + [Environment]::NewLine + 'PDF text' + [Environment]::NewLine + $fence }) -join [Environment]::NewLine)
if (@(Get-StructuralErrors $oldLayoutMutant | Where-Object { $_ -match 'page-fenced' }).Count -eq 0) {
    $errors.Add('Structural negative control accepted the old page-fenced layout.')
}
$missingTocMutant = $architecture -replace '(?m)^\s*- \[0\. 执行摘要\]\(#section-0\).*\r?\n', ''
if (@(Get-StructuralErrors $missingTocMutant).Count -eq 0) {
    $errors.Add('Structural negative control accepted a missing clickable TOC entry.')
}
$fence = [string]::new([char]96, 3)
$missingDiagramMutant = $architecture.Replace($fence + 'mermaid', $fence + 'text')
if (@(Get-StructuralErrors $missingDiagramMutant).Count -eq 0) {
    $errors.Add('Structural negative control accepted missing Mermaid diagrams.')
}
$missingFinalGateMutant = $architecture.Replace('W11-12<br/>Gate PASS', 'W11-12')
if (@(Get-StructuralErrors $missingFinalGateMutant | Where-Object { $_ -match 'Figure 15-1' }).Count -eq 0) {
    $errors.Add('Structural negative control accepted missing S6 Gate PASS in Figure 15-1.')
}

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
