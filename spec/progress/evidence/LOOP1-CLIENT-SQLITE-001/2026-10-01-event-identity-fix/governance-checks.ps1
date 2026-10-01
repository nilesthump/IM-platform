$ErrorActionPreference='Stop'
$python=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development
if($LASTEXITCODE){exit $LASTEXITCODE}
pwsh -NoProfile -File tools/verify-frozen-architecture.ps1
if($LASTEXITCODE){exit $LASTEXITCODE}
& $python -B ci/check_architecture.py --scope all --json
if($LASTEXITCODE){exit $LASTEXITCODE}
& $python -B -m unittest discover -s tests/architecture -v
if($LASTEXITCODE){exit $LASTEXITCODE}
& $python -B -m unittest discover -s tests/ci -v
if($LASTEXITCODE){exit $LASTEXITCODE}
& $python -B contracts/websocket/verify.py
if($LASTEXITCODE){exit $LASTEXITCODE}
& $python -B contracts/plugin-api/verify.py
exit $LASTEXITCODE

