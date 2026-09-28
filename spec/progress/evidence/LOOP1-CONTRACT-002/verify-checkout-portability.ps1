[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repo = (git rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve repository root' }
$python = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'Bundled Python is unavailable' }
$fixture = 'contracts/fixtures/websocket/golden.json'
$tempRoot = Join-Path ([IO.Path]::GetTempPath()) ('LOOP1-CONTRACT-002-portability-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempRoot | Out-Null

try {
    foreach ($setting in @('true', 'false')) {
        $checkout = Join-Path $tempRoot $setting
        & git -C $repo -c "core.autocrlf=$setting" worktree add --detach $checkout HEAD
        if ($LASTEXITCODE -ne 0) { throw "Failed to create $setting checkout" }

        $worktreeHash = (& git -C $checkout hash-object --no-filters -- $fixture).Trim()
        $blobHash = (& git -C $checkout rev-parse "HEAD:$fixture").Trim()
        if ($LASTEXITCODE -ne 0 -or $worktreeHash -ne $blobHash) {
            throw "Fixture bytes differ from committed blob with core.autocrlf=$setting"
        }
        $status = (& git -C $checkout status --porcelain=v1)
        if ($LASTEXITCODE -ne 0 -or $status) { throw "Checkout is not clean with core.autocrlf=$setting" }
        & $python (Join-Path $checkout 'contracts/websocket/verify.py')
        if ($LASTEXITCODE -ne 0) { throw "WSS verification failed with core.autocrlf=$setting" }
        Write-Output "PASS core.autocrlf=$setting fixture=$blobHash clean=true"
    }
}
finally {
    foreach ($setting in @('true', 'false')) {
        $checkout = Join-Path $tempRoot $setting
        if (Test-Path -LiteralPath $checkout) {
            & git -C $repo worktree remove --force $checkout
            if ($LASTEXITCODE -ne 0) { Write-Warning "Could not remove disposable worktree $checkout" }
        }
    }
    Remove-Item -LiteralPath $tempRoot -Force -ErrorAction SilentlyContinue
}
