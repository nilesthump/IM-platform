# S2 Gate recovery baseline — 2026-11-13

Assigned managed root H:/.codex/worktrees/s2/IM-platform; branch task/LOOP1-S2-GATE-001; base555fd18e2f698189104360604eb2535d3c3b05c9. No main writes. Recorder R-S2-RECOVERY-20261113 under C:/Users/21441/.codex/visualizations/2026/11/13/01a1d3da-bff7-75e0-a3d1-dd00f62d0272/research. Early recovery reads incomplete; research trace not product acceptance.

Python executable: C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe; -Xutf8 used for recorder and subprocess.

| Command | Observed result |
| --- | --- |
| python -Xutf8 -B tools/verify_frozen_architecture.py | PASS exit0 |
| python -Xutf8 -B ci/check_s2_planning.py | PASS exit0; explicitly not Stage Gate evaluation |
| python -Xutf8 -B ci/check_architecture.py --scope all --json | PASS exit0; no violations |
| python -Xutf8 -B -m unittest discover -s tests/architecture | initial FAIL: disposable Go runtime cache access denied; unchanged retry PASS88 tests/1existing skip/25.705s after process-local GOCACHE points to owned writable visualization/go-cache |
| python -Xutf8 -B -m unittest discover -s tests/ci | PASS35 tests/4existing skips/6.417s |

Initial default Python was Python2 and failed SyntaxError. Initial recorder full architecture output failed GBK encoding; retry uses -Xutf8. Original failed events remain, no source repair or test weakening. GOCACHE change is child-process test environment only, not persistent user configuration. Full Control and final candidate acceptance pending.

## Deferred Windows tool regression

Original obligation: spec/progress/evidence/LOOP1-CLIENT-GUI-001/windows-tools-deferred-20261007/decision.md. Root observed normal sandbox command launch, supported @oai/sky import/initialization and sky.list_windows returning success with2 windows. Raw tool observations are in current parent conversation; windows-tooling-probe.json is the observer's semantic receipt, not manufactured command output. SHA25625208ae28cefa42a8283850a3d491b5e6bfcfe6fe7dd1f89cff31b2e1c8a6656. No helper/ACL/security/trust changes or UI input. This resolves the bounded tooling observation subject to fresh review; it is not a new product GUI test or S2 PASS.
