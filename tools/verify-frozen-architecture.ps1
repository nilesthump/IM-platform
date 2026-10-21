[CmdletBinding()]
param(
    [string]$BaseCommit = '',
    # Optional explicit Python 3 executable; defaults to tolerant PATH discovery
    # so Microsoft Store python/python3 alias stubs cannot cut the discovery
    # chain (python3 -> python -> py -3 -> bundled runtime) short.
    [string]$Python = ''
)
$ErrorActionPreference = 'Stop'
# NOTE: keep internal state names distinct from the $Python parameter;
# PowerShell variable names are case-insensitive.
$interpreter = $null
$prefix = @()
if ($Python) {
    if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
        throw "Specified -Python path does not exist: $Python"
    }
    $ErrorActionPreference = 'Continue'
    try {
        $version = & $Python --version 2>&1
    } finally {
        $ErrorActionPreference = 'Stop'
    }
    if ($LASTEXITCODE -ne 0 -or "$version" -notmatch '^Python 3\.') {
        throw "Specified -Python is not a working Python 3: $Python"
    }
    $interpreter = $Python
}
if (-not $interpreter) {
    # Probes must tolerate failing executables instead of aborting discovery.
    $ErrorActionPreference = 'Continue'
    try {
        foreach ($name in @('python3', 'python')) {
            $candidate = Get-Command $name -ErrorAction SilentlyContinue
            if (-not $candidate) { continue }
            $version = & $candidate.Source --version 2>&1
            if ($LASTEXITCODE -eq 0 -and "$version" -match '^Python 3\.') { $interpreter = $candidate.Source; break }
        }
        if (-not $interpreter) {
            $launcher = Get-Command py -ErrorAction SilentlyContinue
            if ($launcher) {
                $version = & $launcher.Source -3 --version 2>&1
                if ($LASTEXITCODE -eq 0 -and "$version" -match '^Python 3\.') { $interpreter = $launcher.Source; $prefix = @('-3') }
            }
        }
    } finally {
        $ErrorActionPreference = 'Stop'
    }
}
if (-not $interpreter) {
    $bundled = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Test-Path -LiteralPath $bundled -PathType Leaf) { $interpreter = $bundled }
}
if (-not $interpreter) { throw 'Frozen architecture verification requires Python 3.' }
$arguments = @((Join-Path $PSScriptRoot 'verify_frozen_architecture.py'))
if ($BaseCommit) { $arguments += @('--base-commit', $BaseCommit) }
# Native stderr (for example unittest progress under Windows PowerShell 5.1)
# must not become a terminating error; real failures surface via $LASTEXITCODE.
$ErrorActionPreference = 'Continue'
try {
    & $interpreter @prefix @arguments
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    # Negative controls are part of this integrity entry point, not optional CI coverage.
    & $interpreter @prefix -B -m unittest discover -s (Join-Path $PSScriptRoot '../tests/architecture') -v
    exit $LASTEXITCODE
} finally {
    $ErrorActionPreference = 'Stop'
}
