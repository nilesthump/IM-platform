$ErrorActionPreference='Stop'
& 'C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B spec/progress/evidence/LOOP1-CLIENT-SQLITE-001/2026-10-01-independent-review-d792-fail/event-oracle.py
if($LASTEXITCODE){exit $LASTEXITCODE}
& H:/flutter/bin/dart.bat --packages=clients/shared/local-store/.dart_tool/package_config.json H:/.codex/evidence/s2-sqlite-fixed-independent-review-20261001/fixed-event-probe.dart
exit $LASTEXITCODE
