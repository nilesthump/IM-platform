---
task_id: LOOP1-REMEDIATION-INTEGRATION-001
title: Integrate accepted remediation through PR and verify synchronized main
status: done
owner: /root Coordinator
stage: S1 integration
gate: LOOP1-REMEDIATION-INTEGRATION
---

# Goal

Integrate accepted architecture remediation into main by normal PR, verify actual merge CI, safely fast-forward local main, then hand off to the next dependency-satisfied Social task only.

# Inputs

Human 2026-10-01 integration and business restoration request; delivered subject0e92cde and product subjectd0ae52f; canonical resolver/baseline/v1.1 and approved ADRs; spec/governance/minimality.md, execution-boundaries.md, independent-review.md; completed remediation checkpoint/batch; LOOP1-S1 and Auth/Social specs; unchanged affected domain/invariants/acceptance/contracts.

# Dependencies

All four LOOP1-ARCH-REMEDIATION tasks done; S0 Gate PASS; product/final administrative independent Review and exact hosted evidence recovered.

# Allowed Paths

Human2026-10-01 explicitly authorizes combining finite postmerge recovery with next-task path binding. Exact administrative transition additionally includes `spec/tasks/backlog/LOOP1-GO-SOCIAL-001.md` and `spec/progress/evidence/LOOP1-GO-SOCIAL-001/2026-10-01-recovery-path-map.md`; no product authorization or architecture exemption.

- `spec/tasks/**/LOOP1-REMEDIATION-INTEGRATION-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-REMEDIATION-INTEGRATION-001/**`
- `spec/progress/checkpoints/2026-10-01-remediation-integrated.md`
- `research/prompts/P-INTEGRATION-20261001-ROOT/**`
- `research/runs/R-INTEGRATION-20261001-ROOT/**`

Coordinator control-plane scope authorized by Human request, not an architecture exemption. Subsequent independent external Review/Coordinator traces may use isolated external research directories; product fixes need separately narrowed task authorization before edits. Historical done task records/authority/contracts stay unchanged.

# Acceptance

New independent full main-to-candidate Review PASS; actual PR CI runs all classifier-selected categories and applicable live PostgreSQL/NATS/Auth/race/TLS/roles regressions without integration skips; protection and required Review/checks satisfied; ordinary SHA-guarded PR merge; exact merge/main CI PASS; clean local main fast-forward sync equals origin/main and includes actual merge; stable shareable evidence/checkpoint. These are integration acceptance, not S1 product Gate PASS.

# Forbidden

No main push/force push/remote or old-worktree deletion/admin bypass/rule changes/public semantics changes or automatic Social merge. No unknown uncommitted file contents/ownership takeover.

# Verification

Discoverable entry points: `tools/verify-loop1-ctrl-002.ps1` and `tools/verify-frozen-architecture.ps1`. Execute the recovery verifier as a standalone process and capture its actual exit code, full output and elapsed time; preceding or following successful commands cannot establish its result.

`pwsh -NoProfile -File tools/verify-frozen-architecture.ps1`; `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` during preparation and Acceptance from clean committed checkout; bundled Python3 -B `ci/check_architecture.py --scope all --json`; full diff classification plus actual hosted job/checkout/step/log checks. Independent Review may cite accepted live product tests by proven tree identity but cannot substitute five-job administrative CI for full PR CI. Re-run affected regressions on actual merge as applicable.

# Evidence

Current accepted closure: `spec/progress/evidence/LOOP1-REMEDIATION-INTEGRATION-001/merged-acceptance.md`; independent a9f1393 Review/fullPR36763289936 and actualmerge279c1dc/main36764254107 all13SUCCESS, clean local main FF. Earlier paragraphs below are historical repair observations.

Bounded recovery repair: `spec/progress/evidence/LOOP1-REMEDIATION-INTEGRATION-001/fix-recovery-development.md`. Actual PR CI 36761927418 failed candidate 1ccb8c1 with seven control-record parser requirements; earlier composite Development output did not establish recovery PASS. Fresh Fix reproduces and repairs the exact parser failures without editing verifiers. Local checks are development evidence only; a new fresh independent Review and exact candidate hosted CI remain required. Coordinator subsequently observed delivered 0e92cde full PR CI 36761878401 SUCCESS, all 13 jobs; this inherited result does not accept the repaired candidate.

`spec/progress/evidence/LOOP1-REMEDIATION-INTEGRATION-001/delivery-verification.md` and delivered summaries/hashes. Startup Recorder finished/validated 17 events; not product acceptance. Full integration Review/PR/merge/main acceptance pending.

# Handoff

Current accepted integration closure: fresh independent a9f1393 ReviewPASS/fullPR36763289936, actualmerge279c1dc/main36764254107 all13SUCCESS; clean localmainFF=origin/main. Root owns only subsequent bounded recovery records until commit. All prior Fix/Review writer ownership is released. Historical original/Auth/remediation/oldSocial worktrees preserved. No Social product writer; acceptance-context input is pending on new restoration branch. Earlier repair paragraphs record their historical pending states and are superseded by merged-acceptance.md.

# Next Action

Integration complete. Resolve the preserved Social canonical403 authorization precondition in a fresh independent context; do not implement or change contracts until readiness inputs are executable. Current unique task is Social backlog in new verified-base restoration worktree.

# Last Known Good Commit

Actual merged/main accepted279c1dc4681683e2af3b3534a00e5222dde36be6. Candidatea9f1393 independently accepted/fullPRsuccess. Postmerge recovery records are subsequent subject-bound evidence, never self-acceptance.
