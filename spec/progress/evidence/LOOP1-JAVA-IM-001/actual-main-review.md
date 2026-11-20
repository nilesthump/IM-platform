# Independent PR107 actual-main verification

PASS on e809cc83ed0288fb3070ac27ba8fcb6bc0ffa785. Fresh /root/actualmain participated in neither implementation, fixes, regular or specialist review, nor integration. Detached clean managed worktree H:/.codex/worktrees/jir/IM-platform. Parent range 18597c06f15c6ba5d50e055a88890a54f737fd52..17471665fdbf7c5c5820c150c84823ee37e7398b, task/LOOP1-JAVA-IM-001. Merged PR107 at 2026-11-20T14:32:53Z. Git first and second parents matched base and candidate, respectively. Main and candidate share complete tree fa92b4d63934b20d6a5c1bc480bbad1379458b8d. Remote main resolved to the merge SHA. Clean status, zero diff, final HEAD verified.

## Independent review reports

- C:\Users\21441\AppData\Local\Temp\im-java-review7-17471665\regular-review.md — SHA-256 0e2e6a533167377bf6134871d63a19789c3cd9cf6094b7a260daceb9f4ba49fc
- C:\Users\21441\AppData\Local\Temp\im-17471665-specialist3\specialist-review.md — SHA-256 0dd1fafc94ae9245edbc6b896cef7331f3fe5f0b7d2c685659f9d603832e7fd5

Fresh regular7 PASS followed by separately dispatched specialist3 PASS on the exact head. Report metadata last-write times 14:16:09Z and 14:21:59Z, both before GitHub scheduled the candidate push workflow. Reports cite individual clean-checkout Recorder runs. Their purpose is candidate review. This independent verification covers the integrated main SHA.

## Exact hosted checks


https://github.com/nilesthump/IM-platform/actions/runs/44752847965 — push 17471665fdbf7c5c5820c150c84823ee37e7398b, 2026-11-20T14:22:37Z through 2026-11-20T14:31:35Z.
- architecture SUCCESS (12 successful steps).
- classify SUCCESS (8 successful steps).
- compatibility SUCCESS (11 successful steps).
- deploy skipped (classifier false for preceding branch head).
- desktop (ubuntu-latest) SUCCESS (8 successful steps; skipped Approved Windows GUI assembly and auth controls).
- desktop (windows-latest) SUCCESS (7 successful steps; skipped Actual TypeScript Repository on SQLx SQLite, Native Tauri prerequisites and approved Rust compiler).
- gate SUCCESS (5 successful steps).
- go SUCCESS (11 successful steps).
- java SUCCESS (16 successful steps).
- mobile SUCCESS (9 successful steps).
- shared SUCCESS (8 successful steps).
- source_go SUCCESS (7 successful steps).
- source_java SUCCESS (5 successful steps).
- web SUCCESS (8 successful steps).
Java real IM, Java TLS messaging/durable ACK, and TLS Sync/cursor recovery all succeeded.

https://github.com/nilesthump/IM-platform/actions/runs/44752860335 — pull_request 17471665fdbf7c5c5820c150c84823ee37e7398b, 2026-11-20T14:22:41Z through 2026-11-20T14:30:46Z.
- architecture SUCCESS (12 successful steps).
- classify SUCCESS (8 successful steps).
- compatibility SUCCESS (11 successful steps).
- deploy SUCCESS (16 successful steps).
- desktop (ubuntu-latest) SUCCESS (8 successful steps; skipped Approved Windows GUI assembly and auth controls).
- desktop (windows-latest) SUCCESS (7 successful steps; skipped Actual TypeScript Repository on SQLx SQLite, Native Tauri prerequisites and approved Rust compiler).
- gate SUCCESS (5 successful steps).
- go SUCCESS (11 successful steps).
- java SUCCESS (16 successful steps).
- mobile SUCCESS (9 successful steps).
- shared SUCCESS (8 successful steps).
- source_go SUCCESS (7 successful steps).
- source_java SUCCESS (5 successful steps).
- web SUCCESS (8 successful steps).
Java real IM, Java TLS messaging/durable ACK, and TLS Sync/cursor recovery all succeeded.

https://github.com/nilesthump/IM-platform/actions/runs/44754507275 — push e809cc83ed0288fb3070ac27ba8fcb6bc0ffa785, 2026-11-20T14:32:56Z through 2026-11-20T14:41:34Z.
- architecture SUCCESS (12 successful steps).
- classify SUCCESS (8 successful steps).
- compatibility SUCCESS (11 successful steps).
- deploy SUCCESS (16 successful steps).
- desktop (ubuntu-latest) SUCCESS (8 successful steps; skipped Approved Windows GUI assembly and auth controls).
- desktop (windows-latest) SUCCESS (7 successful steps; skipped Actual TypeScript Repository on SQLx SQLite, Native Tauri prerequisites and approved Rust compiler).
- gate SUCCESS (5 successful steps).
- go SUCCESS (11 successful steps).
- java SUCCESS (16 successful steps).
- mobile SUCCESS (9 successful steps).
- shared SUCCESS (8 successful steps).
- source_go SUCCESS (7 successful steps).
- source_java SUCCESS (5 successful steps).
- web SUCCESS (8 successful steps).
Java real IM, Java TLS messaging/durable ACK, and TLS Sync/cursor recovery all succeeded.

All workflow-declared names and action steps matched job metadata. All reported steps inspected. The exact classifier ranges reproduced 13 selected candidate push jobs, 14 PR jobs and 14 main jobs. Raw GitHub job and step records reside beside this report. Whole-run log download via gh returned HTTP 403; authenticated run/job/step metadata was available.

## Local checks

Frozen verifier PASS, architecture all PASS (0 violations), architecture tests 99 with one skip, detached clean Control Acceptance PASS (task review, 0 status entries, 0 diff lines). Initial architecture invocation lacked UTF-8 on the output stream; the recorded UTF-8 rerun passed. Initial interpreter/authority discovery was outside the research run. System python alias selected Python 2, py launcher missing. Used bundled Python 3. Global Git ignores warning during initial direct status; explicit clean check used repository excludes. No repository files changed. Research Recorder separate from product acceptance: C:\Users\21441\AppData\Local\Temp\im-actualmain-e809cc83\research\runs\R-20261120T143710Z-d689ba08-85cb-4182-a66a-cb8368a2151d. Stage S3 remains OPEN; repository recovery records in merged product tree still indicate review. Main synchronization is a separate coordinator step.

## Commands and times

Independent final inspection 2026-11-20T14:42:02.294413+00:00 through 2026-11-20T14:42:15.242222+00:00; Recorder and raw CI snapshots retain prior timings.

- `git rev-parse --show-toplevel` — exit 0, 0.047 s
- `git rev-list --parents -1 HEAD` — exit 0, 0.031 s
- `git rev-parse HEAD^{tree}` — exit 0, 0.032 s
- `git rev-parse 17471665fdbf7c5c5820c150c84823ee37e7398b^{tree}` — exit 0, 0.031 s
- `git ls-remote origin refs/heads/main` — exit 0, 1.390 s
- `gh api repos/nilesthump/IM-platform/pulls/107 --jq [.merged,.merge_commit_sha,.head.sha,.base.ref,.head.ref,.merged_at]` — exit 0, 1.735 s
- `gh run view 44752847965 --json event,headBranch,headSha,status,conclusion,jobs,url,startedAt,updatedAt` — exit 0, 3.172 s
- `gh run view 44752860335 --json event,headBranch,headSha,status,conclusion,jobs,url,startedAt,updatedAt` — exit 0, 2.984 s
- `gh run view 44754507275 --json event,headBranch,headSha,status,conclusion,jobs,url,startedAt,updatedAt` — exit 0, 3.328 s
- `git -c core.excludesFile=.git/info/exclude status --porcelain=v1 --untracked-files=all` — exit 0, 0.094 s
- `git diff HEAD --` — exit 0, 0.062 s
- `git rev-parse HEAD` — exit 0, 0.032 s
- ['C:\\Users\\21441\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe', '-B', 'tools/verify_frozen_architecture.py'] — exit 0, 110.0 ms, 2026-11-20T14:37:20.819487Z
- ['C:\\Users\\21441\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe', '-B', 'ci/check_architecture.py', '--scope', 'all', '--json'] — exit 1, 969.0 ms, 2026-11-20T14:37:21.893699Z
- ['C:\\Users\\21441\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe', '-Xutf8', '-B', 'ci/check_architecture.py', '--scope', 'all', '--json'] — exit 0, 891.0 ms, 2026-11-20T14:37:31.427898Z
- ['C:\\Users\\21441\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe', '-Xutf8', '-B', '-m', 'unittest', 'discover', '-s', 'tests/architecture'] — exit 0, 21203.0 ms, 2026-11-20T14:37:52.748202Z
- ['pwsh', '-NoProfile', '-File', 'tools/verify-loop1-ctrl-002.ps1', '-Mode', 'Acceptance'] — exit 0, 24031.0 ms, 2026-11-20T14:38:16.901651Z
- ['C:\\Users\\21441\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe', '-Xutf8', '-B', 'ci/classify.py', '--base', '7ff6d1ed68dd30ec033b3e6f7f11c608cb216728', '--head', '17471665fdbf7c5c5820c150c84823ee37e7398b'] — exit 0, 110.0 ms, 2026-11-20T14:38:54.918734Z
- ['C:\\Users\\21441\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe', '-Xutf8', '-B', 'ci/classify.py', '--base', '18597c06f15c6ba5d50e055a88890a54f737fd52', '--head', '17471665fdbf7c5c5820c150c84823ee37e7398b'] — exit 0, 125.0 ms, 2026-11-20T14:38:55.139813Z
- ['C:\\Users\\21441\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe', '-Xutf8', '-B', 'ci/classify.py', '--base', '18597c06f15c6ba5d50e055a88890a54f737fd52', '--head', 'HEAD'] — exit 0, 110.0 ms, 2026-11-20T14:38:55.368249Z
\nRecorder final validation: {"event_count": 22, "run_id": "R-20261120T143710Z-d689ba08-85cb-4182-a66a-cb8368a2151d", "status": "finished"}
