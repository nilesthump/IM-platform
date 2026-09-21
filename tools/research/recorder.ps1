[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RecorderArguments
)

$ErrorActionPreference = 'Stop'
$script = Join-Path $PSScriptRoot 'recorder.py'
$python = $null
$prefix = @()

foreach ($name in @('python3', 'python')) {
    $candidate = Get-Command $name -ErrorAction SilentlyContinue
    if ($candidate) {
        $version = & $candidate.Source --version 2>&1
        if ($version -match '^Python 3\.') {
            $python = $candidate.Source
            break
        }
    }
}

if (-not $python) {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        $version = & $launcher.Source -3 --version 2>&1
        if ($version -match '^Python 3\.') {
            $python = $launcher.Source
            $prefix = @('-3')
        }
    }
}

if (-not $python) {
    $bundled = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Test-Path -LiteralPath $bundled -PathType Leaf) {
        $python = $bundled
    }
}

if (-not $python) {
    throw 'Research Recorder requires Python 3. No compatible interpreter was found.'
}

& $python @prefix $script @RecorderArguments
exit $LASTEXITCODE
