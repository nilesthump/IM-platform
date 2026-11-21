# LOOP1-JAVA-IM-001 fresh independent regular Review

PASS on 17471665fdbf7c5c5820c150c84823ee37e7398b. Reviewer /root/regular7 was independently dispatched and took no part in implementation, repair or prior reviews. Reviewed the task/LOOP1-JAVA-IM-001 branch range 18597c06f15c6ba5d50e055a88890a54f737fd52..17471665fdbf7c5c5820c150c84823ee37e7398b in clean detached managed checkout H:/.codex/worktrees/jir/IM-platform. Detached HEAD and branch ref matched. Initial and final explicit Git statuses were empty. No repository writes or push.

Frozen Markdown and historical PDF hashes matched the manifest. Resolved the unique review task. Reviewed the authority, source ownership, dependencies, scope and acceptance, including ADR-0004's deferred case. Sampled Core transactional Message/Outbox writes and Group/Sync locking and user scoping, actual JDBC imports, Gateway committed timestamp checks and Java ACK/fan-out probes. Go lowercase checks remain scoped to message.send correlation and storage. Verified the current delta against preceding independently reviewed 7ff6d1ed68dd30ec033b3e6f7f11c608cb216728. Exactly two executable files changed, the WSS verifier and its live Java fixture driver. The remaining five changes are task, progress and evidence. The unchanged product, CI workflow/classifier, go/java regression drivers, schemas, DB migrations and fixtures compare byte-for-byte. The classifier selects all 14 jobs.

The new branch inspects the source hour only when the parsed datetime is midnight. It catches Python 3.14 end-of-day normalization, retains the existing invalid-wire-data boundary and adds no dependencies. Direct assertions compare against explicit expected acceptance, independently of Java. The live fixture adds three labeled inputs and exercises both committed ACK and event delivery via the existing probes. The implementation and tester changes are within the specific Human authorization. No actionable findings.

Clean Control Acceptance passed and recovered the exact review task. Architecture scope all had zero violations and architecture tests ran 99 with one skip. Each of CPython 3.13.14 and 3.14.3 passed the canonical WSS suite (8 positive, 10 negative, 23 schema and 26 behavior mutations rejected) and 5,616 independently asserted hour/format combinations, including year-end, week/basic dates, offsets, fractions, and every hour 00..25. CPython 3.12.14 also passed. The additional script hours.py beside this report has SHA256 48e46862f0413db03592fbc6574f8b715f9e781d88afd522ff561abb1f13c49e. No repeat of the service suites in this review. Live Java/Go/Java under Python 3.14.3 was run by the fixer as documented in hosted-hour-fix.md. The preceding regular review on identical product blobs independently ran live IM, Maven and both TLS profiles. This review does not certify hosted CI, integration or S3.

Recorder R-20261120T141210Z-a4a84a02-b7c1-4ccc-acd7-713382500832 finished and validated 37 events. Startup, file inspections and interpreter discovery were direct commands. Prompt registration initially selected Python 2, and py launcher was absent. A direct WindowsApps executable launch was sandbox-denied, leaving an unpaired Recorder command start. Host invocation through the installed 3.13 app alias succeeded. Git warned of an inaccessible user ignore file on sandbox status. The independent clean Control Acceptance recorded zero status entries and diff lines.

## Recorded commands

- Exit 0, 47 ms — git rev-parse --show-toplevel HEAD refs/heads/task/LOOP1-JAVA-IM-001
- Exit 0, 78 ms — git status --porcelain=v1 --untracked-files=all
- Exit 0, 125 ms — C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B tools/verify_frozen_architecture.py
- Exit 0, 1203 ms — C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B ci/check_architecture.py --scope all --json
- Exit 0, 20812 ms — C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B -m unittest discover -s tests/architecture
- Exit 0, 22640 ms — pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance
- Exit 0, 94 ms — C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B contracts/websocket/verify.py
- Exit 0, 94 ms — C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B C:\Users\21441\AppData\Local\Temp/im-java-review7-17471665/hours.py
- Exit 0, 171 ms — C:\Users\21441\AppData\Local\Temp\im-java-hour-runtimes\cpython-3.14.3-windows-x86_64-none\python.exe -Xutf8 -B contracts/websocket/verify.py
- Exit 0, 109 ms — C:\Users\21441\AppData\Local\Temp\im-java-hour-runtimes\cpython-3.14.3-windows-x86_64-none\python.exe -Xutf8 -B C:\Users\21441\AppData\Local\Temp/im-java-review7-17471665/hours.py
- Exit 0, 31 ms — git diff --exit-code 7ff6d1ed HEAD -- . :!contracts/websocket/verify.py :!tools/verify_java_im.py :!spec/progress/current.md :!spec/tasks/review/LOOP1-JAVA-IM-001.md :!spec/progress/evidence/LOOP1-JAVA-IM-001/*
- Exit 0, 110 ms — C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B ci/classify.py --base 18597c06 --head HEAD
- Exit 0, 78 ms — git status --porcelain=v1 --untracked-files=all
- Exit 0, 172 ms — C:\Users\21441\AppData\Local/Microsoft/WindowsApps/python3.13.exe -Xutf8 -B contracts/websocket/verify.py
- Exit 0, 140 ms — C:\Users\21441\AppData\Local/Microsoft/WindowsApps/python3.13.exe -Xutf8 -B C:\Users\21441\AppData\Local\Temp/im-java-review7-17471665/hours.py
- Exit 0, 79 ms — git status --porcelain=v1 --untracked-files=all
