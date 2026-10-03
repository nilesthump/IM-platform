# Fresh SEND Fix local evidence (2026-10-03)

This is fix evidence only: original independent Review remains FAIL; no new independent Review, hosted acceptance, Task PASS, done or S2 Gate PASS is claimed.

Assigned root H:/.codex/worktrees/client-mvp-planning/IM-platform verified against git rev-parse before writes. Branch task/LOOP1-CLIENT-SEND-001; fix base1822e29682eccafd75ee293c31a2d35e29746eb6. Accepted main10b77b22386234c98409ca41b3622ad6d25f3884 remains last known good; main synchronization PENDING. Full accepted-main diff includes separately owned Coordinator activation/UIARCH closure preceding SEND. This fixer never pushed, merged, wrote main, moved queues or started SYNC/GUI/WEB.

## Review finding correction and present minimality

Original report SHA256edfdeb7f094e3ca788c88df4c7a41e0d710ce179a2660972eb4c9308f6976a93 is unchanged. Both old hosted37109255423/37109294362 completed JSON and the independent finished Recorder are archived exact bytes using gzip/manifest, including all29-event run artifacts; LF readability report is explicitly a copy. Successful old CI does not override Review FAIL or accept a new SHA.

Mobile dispose now retires the account and clears messages before fallible storage work. Direct finally ensures owned Repository cleanup and scope/timer cancellation even when disconnect markFailed/refresh throws. Generic storage failure remains observable in empty retired state. Tests invoke actual dispose on a closed SDK SQLite Repository, both after the retained async-storage timer-liveness case and with a currently pending attempt; assert old messages empty, offline, socket closed, retired=true and owned scope inactive. No lifecycle-only escape replaces disposal.

Desktop/Mobile rejected ACK has no CID under unchanged canonical contract. Only a sole attributable send may fail immediately. The actual intermediate delayed-reject RED proves current-attempt count alone becomes unsafe after another CID commits. A single RID-to-soleCID/null map retains the connection identity ambiguity until disconnect/generation retirement; null means multiple CIDs used that RID. It is written only after a real send and cleared with the connection (also Mobile lifecycle retirement). This small current responsibility prevents the reviewed cross-Conversation defect; no new wire field/global uniqueness, Repository, scheduler/framework or future extension is introduced. One-CID rejections remain direct. Independent attempts retain timers, commit individually, and late committed ACK converges a timed-out CID to terminal SENT.

Product fix scope is two production files and their two existing behavior test files. Repository/native/schema/backend/contracts/frozen/dependencies/CI are unchanged by this fix. Canonical v1.1 hash16e9c7b488e00dd39c7c2b5da7286c22be6ac67c163f0e89733bbe00297d0a3c and PDF546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510 verify; accepted ADR0005/6/7 plus canonical2.3/3/6/10SRC01-07/11/19/20 remain authority.

## Actual feedback loop and final local verification

All commands use bundled Python3 -X utf8 -B with Node24, JDK17/Gradle8.9/API34 emulator5590, approved existing SQLx adapter/MSVC and external existing Rust target; exact argv/exit/timing/output hashes and compressed redacted outputs are in commands.json and outputs/. Final SEND APK bytes are preserved in own Git metadata with android-artifacts.json hashes.

- Pre-fix Desktop SQLx RED: ambiguous reject produced FAILED instead of expected SENDING.
- Pre-fix API34 RED: dispose failed to clear old messages (assertion37); a separate same-RID/two-CID run failed assertion27, actual FAILED vs expected SENDING.
- Intermediate pending-count-only Desktop RED: after first CID committed, delayed rejection incorrectly changed the second CID to FAILED. Intermediate Android PASS65 precedes this final attribution fix and is not the final result.
- Final python -B tools/verify_client_send.py --scope desktop: PASS actual SQLx and builtin verified TLS/WSS, shared strict/golden codec included; same-RID CIDs independently confirm/time out/converge, both timers survive ambiguity, delayed reject remains ignored after one commits. Existing ordinary reject/offline/retry/stale socket/ACK persistence/terminal SENT cases retained.
- Final python -B tools/verify_client_send.py --scope mobile --serial emulator-5590: PASS66 actual API34 SDK SQLite/StateFlow/platform TLS. Both same-RID CIDs retain independent timers/ACKs, delayed rejection after settlement remains ambiguous; closed-storage no-pending/pending retirement tests above pass. Existing actual TLS/default-trust rejection and async timer-storage liveness retained.
- python -B tools/verify_client_sqlite.py --scope desktop: PASS13cases/141assertions plus native atomic rollback/read-only-query test.
- python -B tools/verify_client_sqlite.py --scope mobile --serial emulator-5590: PASS13cases/137assertions API34 SQLite3.39.2 both install and data-clear; original storage runner unchanged.
- python -B tests/clients/send/go_smoke.py H:/.codex/toolchains/client-sqlite/target-final/debug/storage_probe.exe: PASS current Desktop application+SQLx through actual Go verified TLS WSS to exact PostgreSQL Message/Outbox rows; inspected owned smoke resources removed. Controlled TLS fixture results are separately client behavior, not PostgreSQL durability.
- python -B ci/check_architecture.py --scope all --json: PASS0violations after only own verified ignored output cleanup; frozen integrity PASS.
- python -B -m unittest discover -s tests/architecture -v: PASS53 no skips.
- python -B -m unittest discover -s tests/ci -v:33tests succeed with4 pre-existing Windows symlink privilege cases explicitly skipped/unexecuted, hosted Linux required.

Recovery Development PASS and git diff --check10b77b22386234c98409ca41b3622ad6d25f3884 PASS are recorded before clean commit. Final clean Recovery Acceptance and HEAD-range audit follow the handoff commit in the external immutable Recorder. Local Recovery mode is not hosted Task acceptance.

## Failures, instrumentation and pending acceptance

Early Windows private launcher quoting/PATH preparation failures are distinct from actual behavior RED. Two pre-run-command quoting errors retain transcript-only facts; exact raw output hashes/timings unavailable. Recorded cargo/PATH setup FAIL is preserved. Initial guarded cleanup stopped on gen parent not directly ignored; narrowed to verified ignored gen/schemas, preserved other paths. Recovery initially rejected rewritten metadata field formatting, then absent not-yet-exported evidence paths; exact fields/evidence repaired before fresh PASS. A Recorder semantic event rejected unsupported event_type; exposed, replaced with supported repair_finished event, no existing event or finished stream edited.

Recorder prompt P-SEND-FIX-20261003/run R-SEND-FIX-20261003 at H:/IM-platform/.git/worktrees/IM-platform4/send-fix-research. prospective_resume explicitly marks earlier read-only startup incomplete; no fabricated complete early trace. Commands are prospective where possible. Own finished run stays outside candidate until Coordinator archives it; commands.json is explicitly a completed-command snapshot, not a finished-run claim. Finish/validate is required after clean final HEAD and Recorder PASS cannot accept this task.

NEW independent Review of exact clean final HEAD/full10b..HEAD, NEW exact-head hosted required jobs via existing CI/PR16, protected integration/actual-main independent verification and verified main synchronization remain necessary. Task stays unique review, S1PASS/S2OPEN, accepted main unchanged, original main unknown781bytes/three backups untouched. Root Coordinator receives writer release and exact final SHA, then delegates fresh Review; stop at SEND accepted endpoint, never activate SYNC/GUI/WEB.
