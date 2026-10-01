# Independent cumulative integration Review: FAIL

Subject `1ccb8c1ec831e4a27fdfc1c768f3de88a2e3fd48`; branch `task/LOOP1-ARCH-REMEDIATION`; base and merge-base `09cec968f64faf0db319aea8d9c21d4fffe8ec49`. Scope is the complete cumulative main-to-candidate integration: 1058 changed paths with rename detection disabled (872 research,142 spec,23 backend,8 tests,5 ci,3 tools,2 deploy,1 workflow plus root instructions/README). It is not only the last administrative commit.

Reviewer `/root/integration_review` is a fresh independent delegated context and neither implemented nor fixed this candidate. Clean detached checkout created at `H:/.codex/worktrees/architecture-remediation/integration-review-20261001/candidate`; exact HEAD and empty status verified initially and finally. The original candidate checkout can drift during the separately delegated Fix; all substantive review after isolation used this immutable detached object. No candidate repository file was edited. Only this external directory is reviewer-owned; ownership is released on handoff. Actual built-in delegation establishes independence; hidden internal metadata is unavailable.

| Review axis | Verdict | Findings |
| --- | --- | --- |
| Standards/authority/source responsibility/minimality | FAIL | Recovery-format contract violation blocks CI; no additional product/architecture finding |
| User scope/current Task acceptance/integration | FAIL | Independent clean recovery and exact PR CI fail; integration remains unfinished |

## Required corrections

**[P1] Restore machine-verifiable recovery fields before integration acceptance.** `spec/progress/current.md:11` uses `Completed Work` and omits the required nonempty `Immediately Relevant Completed Work`, `Current Blockers`, and `Changed Files or Migrations` sections. `current.md:15` uses prose instead of the supported exact Command/Result/Evidence fields. `spec/tasks/review/LOOP1-REMEDIATION-INTEGRATION-001.md:43` wraps full `pwsh ... -File tools/...` argv in inline code; the existing recovery verifier requires a discoverable inline tools/ path and therefore cannot discover the entry point. Preserve useful prose but add the supported recovery schema and explicit tools paths; do not weaken the verifier. Newly executed strict Acceptance returns exit1 with exactly seven diagnostics (three missing sections, three verification fields, one task entrypoint). This violates the repository handoff/recovery requirements and stops the real hosted classification job before product jobs can run.

The failure is independently confirmed by actual [PR run36761927418](https://github.com/nilesthump/IM-platform/actions/runs/36761927418): exact head1ccb8c1, completed failure, classify `Verify clean repository recovery` failed, path tests/classification skipped, gate failed, all11 dependent jobs skipped. Those skips cannot be counted as inactive profiles or execution PASS. No integration merge or S1 Gate PASS is accepted by this report. A fresh Fix plus fresh Review and a new full PR run are required.

## Authority, inherited product, boundaries and scope

Startup followed handoff -> current -> exact unique integration Task review -> referenced authority -> Git status/diff/recent commits -> baseline. Resolver/baseline/approved ADRs, canonical source, execution/minimality/independent review guides, Auth domain/invariants/acceptance and canonical contract artifacts, Auth done task, remediation batch/tasks/checkpoint and LOOP1-S1 were inspected. Large initial displays were truncated; targeted subsequent reads, Git identity proof and recorded verifier output supplied relevant bounded evidence. No lossless full read transcript is claimed.

Canonical v1.1 actual SHA256 `83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e` and historical PDF `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510` match approved manifest. ADR-0003 and approval-and-recovery bind the four-stage scope. ADR-0001 is expired; no local acceptance substitution applies. Main-to-candidate contracts tree is identical; historical PDF blob is identical. All3589 delivered pre-existing research/evidence/checkpoint/done-task blobs remain unchanged. Four remediation tasks uniquely done, current integration task uniquely review. Historical Auth remains accepted under old requirements, remediation PASS stays distinct from S1 OPEN. No Social product implementation, Message/E2E/Java/client/plugin business, public contract/schema/ACK/security expansion is introduced by this integration candidate.

Actual inherited Auth was inspected in `core/auth.go/http.go/outbox.go`, Gateway handler/validator/hub and root assembly/shared support. Core owns registration/login/refresh/logout and user routes, row-locked Session writes, atomic revocation Outbox/Sync and dispatch. Gateway imports only shared service support, maintains connection binding/fan-out, validates readonly Session state, forwards HTTP to Core, and bounds fallback revocation-cause lookup to committed exact user/session facts. No per-message PostgreSQL access was introduced. Shared code contains configuration, token/crypto/error primitives and infrastructure health; no complete Auth repository/session-write workflow. Root is assembly/lifecycle only; plugin-host stays placeholder infrastructure. Single module/role binary and necessary present dependencies are retained; no speculative framework or service was found. Migration map precedes product changes and broad authorization expired at batch closure. New integration control paths match task allowed paths.

Direct Git tree identities prove **d0ae52f -> delivered0e92cde -> exact1ccb8c1** equality for backend, contracts, tests, ci, .github, deploy, tools, clients, plugins, domain and invariants. Full machine evidence is `structural-proof.json`. Thus unchanged independently reviewed real PostgreSQL16/NATS/full unit/race/canonical/rollback/security/revocation/TLS/raw-NATS product evidence remains relevant to exact1ccb8c1; those live suites were not newly executed in this Review. Product evidence is attributed to `revocation-independent-review.md` at6339f8e/product closured0ae52f and hosted36744072690, with explicitly attributed earlier deploy evidence. Corrected fallback behavior and old failed36738064831 remain preserved. Four historical Windows symlink subcases were covered by recorded Linux execution in prior hosted evidence, but must still execute in new full PR CI.

All six new copied final-delivery artifacts match committed `delivery-hashes.json`; copied review reports accept exact0e92cde and say CI pending at their report time, while subsequent summary binds actual hosted36751729344. Source proof/process metadata identifies distinct fresh CLI reviewer, not self-review. Copied historical rendering loss/redaction/prospective limitations remain disclosed. Repository copies and hosted URLs establish shared recovery; external historical H:/ paths remain provenance. No raw CLI transcript or unknown original-worktree contents were copied by this reviewer.

## Full CI selection and tested object

New local classification of complete base-to-head diff selects every14 classifier category. Actual workflow has13 jobs: classify/gate plus11 concrete selected jobs, with old_client/plugin/migration aggregated into compatibility. Required new execution includes architecture/source_go/source_java, Go recursive fmt/build/vet/full unit/race and DB_TEST_ENABLE=1 migrated PostgreSQL16/NATS, canonical contracts, compatibility/migration, Java/client placeholder checks and deploy Go/Java transport plus Go actual-role TLS smoke. Prior five-job administrative runs cannot satisfy full integration.

Workflow classify explicitly checks `github.event.pull_request.head.sha`; dependent jobs/default checkout test the GitHub PR merge ref. Head/run metadata alone is not proof those default jobs tested the head; actual checkout SHA and generated merge/test SHA must be captured on the next successful PR run. After authorized ordinary merge, actual main/merge CI remains mandatory. No CI guard weakening/continue-on-error was found; gate rejects failed/missing/selected-skipped jobs.

## Newly executed verification

Exact argv, timestamps, exit code, elapsed milliseconds and immutable stdout/stderr captures are in `command-results.json` and external Recorder events/blobs. Independent newly executed checks:

| Check | Exit | Seconds | Result/limits |
| --- | ---: | ---: | --- |
| `git status --porcelain=v1 --untracked-files=all` |0|0.187|clean detached subject |
| `git rev-parse HEAD` |0|0.016|exact1ccb8c1 |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` |1|7.453|FAIL seven recovery diagnostics |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` |0|5.094|PASS34 controls,0skips; canonical/provenance valid |
| Bundled Python3 `-B ci/check_architecture.py --scope all --json` |0|0.359|PASS0violations; output intentionally recorder-redacted |
| Bundled Python3 `-B -m unittest discover -s tests/ci -v` |0|2.609|27 tests;4 Windows symlink subcase skips, not executed |
| Bundled Python3 `-B ci/classify.py --base 09cec968... --head 1ccb8c1...` |0|0.110|all categories selected,1058paths |
| Bundled Python3 `-B external structural_checks.py` |0|1.313|tree/hash/history/scope/queue/clean assertions PASS |
| `gh run view 36761927418 --repo nilesthump/IM-platform --json headSha,status,conclusion,jobs,url` |0|1.610|API succeeded; actual CI FAILURE |

Initial pre-Recorder baseline attempt in read-only sandbox failed temporary-directory creation (31 test setup errors), not product assertions; elevated clean-checkout baseline above passed. Initial external checks.ps1 argument forwarding produced seven recorder.ps1 positional-parameter failures before commands ran; corrected runner directly used recorder.py, preserving disclosed attempts without inventing events. Several guessed filenames were absent and resolved through inventory. Read-only outside-recorder diagnostics, external report/script writes and large display truncations make this a prospective_resume trace with incomplete startup capture. One AST dump is explicitly secret-redacted; no raw-byte equality is claimed for that dump. GBK-like replacement in OS symlink error display is not repaired or misrepresented as lossless evidence. No candidate fixes, mutation of finished research history or test result suppression occurred.

Coordinator next action: apply separately owned finite recovery-record fix, delegate a new fresh independent reviewer on new exact subject, rerun all selected PR jobs and capture real head/merge checkout identities, then proceed only after real CI and ordinary protected merge conditions. Current task stays review; integration Gate OPEN and S1 product Gate OPEN.

Recorder R-INTEGRATION-REVIEW-20261001 finished FAIL and validates with 23 events (exit0); recorder-validation.json. Recorder integrity is not product acceptance.
