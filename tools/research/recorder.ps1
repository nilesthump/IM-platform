[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RecorderArguments
)

$ErrorActionPreference = 'Stop'
$script = Join-Path $PSScriptRoot 'recorder.py'

function Test-Python3 {
    param([string]$Exe, [string[]]$Prefix = @())
    # Probes must tolerate failing executables (for example the Windows Store
    # python/python3 alias stub) instead of aborting the whole discovery loop.
    $output = & $Exe @Prefix --version 2>&1
    return ($LASTEXITCODE -eq 0 -and "$output" -match '^Python 3\.')
}

$python = $null
$prefix = @()

# Explicit override first. A set-but-unusable value fails loudly; it never
# silently falls back to discovery.
if ($env:RESEARCH_RECORDER_PYTHON) {
    $override = $env:RESEARCH_RECORDER_PYTHON
    if (-not (Test-Path -LiteralPath $override -PathType Leaf)) {
        throw "RESEARCH_RECORDER_PYTHON is set but does not point to an executable file: $override"
    }
    if (-not (Test-Python3 $override)) {
        throw "RESEARCH_RECORDER_PYTHON is set but is not a working Python 3 interpreter: $override"
    }
    $python = $override
}

if (-not $python) {
    $ErrorActionPreference = 'Continue'
    try {
        foreach ($name in @('python3', 'python')) {
            $candidate = Get-Command $name -ErrorAction SilentlyContinue
            if ($candidate -and (Test-Python3 $candidate.Source)) {
                $python = $candidate.Source
                break
            }
        }
        if (-not $python) {
            $launcher = Get-Command py -ErrorAction SilentlyContinue
            if ($launcher -and (Test-Python3 $launcher.Source @('-3'))) {
                $python = $launcher.Source
                $prefix = @('-3')
            }
        }
        if (-not $python) {
            $bundled = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
            if ((Test-Path -LiteralPath $bundled -PathType Leaf) -and (Test-Python3 $bundled)) {
                $python = $bundled
            }
        }
    } finally {
        $ErrorActionPreference = 'Stop'
    }
}

if (-not $python) {
    throw 'Research Recorder requires Python 3. No compatible interpreter was found; set RESEARCH_RECORDER_PYTHON to a Python 3 executable path.'
}

& $python @prefix $script @RecorderArguments
exit $LASTEXITCODE
