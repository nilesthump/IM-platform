[CmdletBinding()]
param([string]$BaseCommit = '')
$ErrorActionPreference = 'Stop'
$python = $null
$prefix = @()
foreach ($name in @('python3', 'python')) {
    $candidate = Get-Command $name -ErrorAction SilentlyContinue
    if ($candidate) {
        $version = & $candidate.Source --version 2>&1
        if ($version -match '^Python 3\.') { $python = $candidate.Source; break }
    }
}
if (-not $python) {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        $version = & $launcher.Source -3 --version 2>&1
        if ($version -match '^Python 3\.') { $python = $launcher.Source; $prefix = @('-3') }
    }
}
if (-not $python) {
    $bundled = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Test-Path -LiteralPath $bundled -PathType Leaf) { $python = $bundled }
}
if (-not $python) { throw 'Frozen architecture verification requires Python 3.' }
$arguments = @((Join-Path $PSScriptRoot 'verify_frozen_architecture.py'))
if ($BaseCommit) { $arguments += @('--base-commit', $BaseCommit) }
& $python @prefix @arguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
# Negative controls are part of this integrity entry point, not optional CI coverage.
& $python @prefix -B -m unittest discover -s (Join-Path $PSScriptRoot '../tests/architecture') -v
exit $LASTEXITCODE
