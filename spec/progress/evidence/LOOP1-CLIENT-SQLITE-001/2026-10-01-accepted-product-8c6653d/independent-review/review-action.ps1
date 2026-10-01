param([string]$Action)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath 'H:/.codex/worktrees/s2-sqlite-fixed-review/IM-platform'
switch ($Action) {
 authority {
 Get-FileHash spec/architecture/frozen-architecture.md,scalable-distributed-im-architecture.pdf
 Get-Content -Encoding utf8 spec/architecture/frozen-architecture.md
 Get-ChildItem spec/architecture/decisions/*.md | ForEach-Object { Get-Content -Encoding utf8 $_.FullName }
 Get-Content -Encoding utf8 spec/governance/minimality.md,spec/governance/execution-boundaries.md,spec/governance/independent-review.md,spec/domain/messaging.md,spec/domain/sync-plugin.md,spec/invariants/messaging.md,spec/invariants/sync-plugin.md,spec/acceptance/s0-messaging.md,spec/acceptance/s0-sync-plugin.md,contracts/websocket/envelope.schema.json,contracts/websocket/sync-v1.schema.json,contracts/fixtures/websocket/golden.json,contracts/fixtures/sync-plugin/golden.json,contracts/plugin-api/verify.py
 }
 state { git status --porcelain=v1; git rev-parse HEAD; git diff; git log -6 --oneline; git diff --stat a0f0f137 8c6653d; git diff 79d9a2d 8c6653d; Get-ChildItem spec/progress/evidence/LOOP1-CLIENT-SQLITE-001/2026-10-01-independent-review-d792-fail -Recurse -File | Select-Object FullName }
 baseline { & pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance; exit $LASTEXITCODE }
}
