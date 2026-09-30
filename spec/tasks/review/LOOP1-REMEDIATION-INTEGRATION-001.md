---
task_id: LOOP1-REMEDIATION-INTEGRATION-001
title: Integrate accepted remediation through PR and verify synchronized main
status: review
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

Bounded recovery repair: `spec/progress/evidence/LOOP1-REMEDIATION-INTEGRATION-001/fix-recovery-development.md`. Actual PR CI 36761927418 failed candidate 1ccb8c1 with seven control-record parser requirements; earlier composite Development output did not establish recovery PASS. Fresh Fix reproduces and repairs the exact parser failures without editing verifiers. Local checks are development evidence only; a new fresh independent Review and exact candidate hosted CI remain required. Coordinator subsequently observed delivered 0e92cde full PR CI 36761878401 SUCCESS, all 13 jobs; this inherited result does not accept the repaired candidate.

`spec/progress/evidence/LOOP1-REMEDIATION-INTEGRATION-001/delivery-verification.md` and delivered summaries/hashes. Startup Recorder finished/validated 17 events; not product acceptance. Full integration Review/PR/merge/main acceptance pending.

# Handoff

Fresh Fix Agent /root/integration_records_fix owns only current.md, this review Task Spec and new fix-recovery evidence until its clean repair commit, then releases repository writer ownership. Its trace is external H:/.codex/worktrees/architecture-remediation/integration-records-fix-20261001/research; startup before Recorder is explicitly incomplete. Root/Reviewer do not write during repair. Original checkout unknown files and historical Social/main/Auth worktrees preserved. No active product writer observed. Integration candidate is prepared; tests/review/merge not yet accepted.

# Next Action

Fresh independent Integration Reviewer reviews the clean bounded repair and complete origin/main-to-candidate; create/reuse PR, verify all selected jobs, repair via fresh Fix/new Review if needed, then normal protected merge and safe main synchronization. Do not activate Social before merged-result verification.

# Last Known Good Commit

Delivered remediation0e92cde18a360435f606299552697871209f9e56; integration base09cec968f64faf0db319aea8d9c21d4fffe8ec49. No integration PASS yet.
