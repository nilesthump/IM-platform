# Fresh stage003 JDBC Fix candidate

Independent Review FAIL source: Coordinator relayed /root/stage3_review read-only exact candidate a27f6552316106cd9ef67f9c5a53dbcdab1bb22a. ci/check_architecture.py lines189-199 accepted Gateway stmt.execute(q) when unrelated SELECT string existed, and accepted Gateway setAutoCommit(false)/commit/rollback. Reviewer did not write implementation/evidence. Fresh fixer /root/stage3_jdbc_fix repaired this candidate; never self-accepts. Branch task/LOOP1-ARCH-REMEDIATION; base clean a27f655. Independent Review and exact-head hosted acceptance remain pending.

Authority: frozen v1.1 §3.1 Core Auth/Session writes, §10 SRC-01/03 Gateway read-only validation/shared support no business transactions. Smallest conservative fix removes ambiguous execute entirely outside Core; Gateway SELECT uses executeQuery. Core execution unchanged. Non-Core JDBC transaction controls commit/rollback/setAutoCommit/setSavepoint/releaseSavepoint fail; getConnection, setReadOnly, close remain support operations. No SQL literal or class-name blacklist substituted for operations. Shared connection factory, Gateway read-only query and root role helpers remain positive controls. These static checks supplement semantic Review and do not claim to infer arbitrary program semantics.

Four added tests: unrelated SELECT cannot exempt dynamic stmt.execute(q), prepared execute(), or literal SELECT execute(); split-string UPDATE with SELECT decoy rejected; Gateway/shared transaction controls rejected (ten subcases); legal executeQuery and connection lifecycle pass. All34 architecture tests passed, no skips. CI24 passed with four historical Windows symlink subcases skipped WinError1314, explicitly not counted as executed; Linux hosted verification pending. Canonical verifier now includes all34 architecture tests; recovery Development passed (not acceptance). Governance/Java actual tree pass, old Go FAIL unchanged72 violations. Existing Go inventory unchanged; manual root HTTP/WSS/NATS/business transport and Gateway full-authService coupling remain phase004 inputs. No product Go/Java/public contracts/canonical/PDF/historical evidence modified.

Before Recorder: mandatory startup reads/status/diff/log/minimum verifier performed in default read-only sandbox. Minimum verifier exit1 because tempfile creation unavailable (27 errors), not checker regression. Reran authorized escalation successfully. This pre-Recorder segment is incomplete, never represented as prospective complete. Delegation summary prompt P-8398fc18-6a08-4483-b0f8-14e9c5bda5d1 explicitly agent source, not full Human prompt. Fresh Fix run R-20260930T134747Z-dd0072a1-c1af-4472-9fe3-d506491b2a83 prospective_resume/pre_recorder_trace_complete=false. Run-local blobs/** -text; old finished runs untouched. Actual Go JSON capture is recorder-redacted (secret_redaction_applied=true) so raw hash differs redacted saved blob by design; do not claim saved redacted bytes are original raw. Public current inventory remains unchanged.

## Recorded commands

Python below is bundled Python3 C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe, pwsh7. Windows native environment. Exact output/event IDs and raw hashes in new run; all times milliseconds.

| Command | Exit | Duration ms | Result |
| --- | --- | --- | --- |
| `C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m unittest discover -s tests/architecture -v` | 0 | 5297.0 | PASS |
| `C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m unittest discover -s tests/ci -v` | 0 | 2937.0 | PASS |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | 5343.0 | PASS |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | 0 | 5750.0 | PASS |
| `C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe ci/check_architecture.py --scope governance` | 0 | 141.0 | PASS |
| `C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe ci/check_architecture.py --scope java` | 0 | 125.0 | PASS |
| `C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe ci/check_architecture.py --scope go --json` | 1 | 437.0 | FAIL |

Task003 remains review,004 backlog,overall batch/S1 Gate NOT PASSED. Next exact action: Coordinator delegates a new independent Review Agent who neither implemented nor fixed this candidate, verifies clean commit and actual new controls, then exact-head hosted bounded evidence. No push performed by fixer.
