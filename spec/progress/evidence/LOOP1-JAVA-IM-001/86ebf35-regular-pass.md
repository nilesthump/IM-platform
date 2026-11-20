# Fresh independent regular review of LOOP1-JAVA-IM-001

PASS on 86ebf3510450013943c22311abb5d5a00c526457. Reviewer /root/regular4 was a fresh context, with no role in implementation, fixes, or previous reviews. Reviewed task/LOOP1-JAVA-IM-001 against accepted 18597c06f15c6ba5d50e055a88890a54f737fd52, range 18597c06f15c6ba5d50e055a88890a54f737fd52..86ebf3510450013943c22311abb5d5a00c526457. The managed detached checkout H:/.codex/worktrees/jir/IM-platform resolved to the branch tip. Initial and final status were clean. The sole queue entry is review and all eight declared prerequisites are done.

The control verifier passed on this exact candidate. Current Verification now cites fix2.md, whose real fixture command, scope and time agree with the record. The earlier report is preserved. Comparison against a7e85f34ccc0cf9cccf942d51cd42fc4654751a5 found exactly three task-owned records changed. An explicit git diff --exit-code excluding those three records established identical bytes for every other tracked input, including authority, fixtures, product, Maven inputs, Docker and CI. All 31 paths changed since the accepted base fall within the task scope.

Authority hash and historical provenance passed. Inspected JDBC/transaction use in Core Friend, Group, Messages and Sync; bounded JNATS Outbox publication; Spring Gateway proxy, WSS and local connection handling; role dependencies, changes to CI selection and actual workflow steps. The same transaction protects sequence, Message and Outbox. The successful ACK exits Core after the transaction completes. Receipts preserve original group outcomes, with current authorization before replay. Snapshot, Sync cursors and message history use actor-scoped checks. Stable user/session ordering and conversation/member locking address the prior concurrency findings. No new stack or public contract was introduced. The friend exception remains limited to ADR-0004.

The unchanged product and fixture trees have prior independent live evidence in spec/progress/evidence/LOOP1-JAVA-IM-001/a7e85f3-regular-fail.md. That review ran both real profiles, durable transactions, identity replay, login/send overlap, session retirement, TLS messaging, large Unicode texts, paginated Sync, cross-profile credential/cursor/receipt continuity and Maven. These remain prior executions on byte-identical inputs. This review reran the changed recovery surface and structural, contract and CI checks on the actual candidate. The architecture suite ran 99 tests with one skip and the CI suite ran 41 with four skips. Exact diff selects all 14 classifier jobs.

No blocking regular-review findings. A different fresh error specialist must review the same SHA before submission. Hosted checks, protected integration and verification of actual main remain pending. S3 OPEN.

## Review commands

Recorder R-20261120T123635Z-cd13eb35-ceec-49f3-a06b-477220e5ff29 finished and validated with 50 events. Direct preliminary repository reads and a mistaken Python 2 invocation preceded the recorded verification commands; the bundled Python 3 retry passed. Some read-only source inspections ran directly. A simultaneous attempt to register two test commands met the Recorder writer lock; the architecture suite ran successfully through the Recorder on sequential retry. Git warned that the user-global ignore file was unreadable; final porcelain including all untracked paths was empty.

- Exit 0, 31 ms, rg -n SRC-0[1-7]|ACK_COMMITTED|JNATS|Outbox|cursor|幂等 spec/architecture/frozen-architecture.md spec/architecture/decisions/ADR-0014-java-technology.md
- Exit 0, 16 ms, rg -l . spec/domain spec/invariants spec/acceptance contracts/fixtures contracts/http contracts/websocket contracts/database/migrations contracts/errors
- Exit 0, 47 ms, git rev-parse --show-toplevel
- Exit 0, 78 ms, git status --short --branch
- Exit 0, 62 ms, git diff HEAD
- Exit 0, 46 ms, git log -6 --oneline
- Exit 0, 31 ms, git diff --name-status 18597c06 HEAD
- Exit 0, 47 ms, git diff --name-status a7e85f34 HEAD
- Exit 0, 47 ms, git diff a7e85f34 HEAD spec/progress/current.md
- Exit 0, 31 ms, git show HEAD:spec/progress/evidence/LOOP1-JAVA-IM-001/a7e85f3-regular-fail.md
- Exit 0, 46 ms, git rev-parse HEAD task/LOOP1-JAVA-IM-001
- Exit 0, 31 ms, git diff --exit-code a7e85f34 HEAD . :!spec/progress/current.md :!spec/tasks/review/LOOP1-JAVA-IM-001.md :!spec/progress/evidence/LOOP1-JAVA-IM-001/a7e85f3-regular-fail.md
- Exit 0, 125 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tools/verify_frozen_architecture.py
- Exit 0, 937 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B ci/check_architecture.py --scope all --json
- Exit 0, 22031 ms, pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance
- Exit 0, 78 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B contracts/websocket/verify.py
- Exit 0, 406 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B contracts/http/verify-group.py
- Exit 0, 157 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tools/verify_sync_transport.py
- Exit 0, 6047 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B -m unittest discover -s tests/ci
- Exit 0, 20344 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B -m unittest discover -s tests/architecture
- Exit 0, 110 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B ci/classify.py --base 18597c06f15c6ba5d50e055a88890a54f737fd52 --head HEAD
- Exit 0, 78 ms, git status --porcelain=v1 --untracked-files=all
- Exit 0, 31 ms, git rev-parse HEAD
