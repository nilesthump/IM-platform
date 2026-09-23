# LOOP1-CONTRACT-001 Recorder Path Authorization

- Date: 2026-09-23 (Asia/Shanghai)
- Human decision: `ok`, in direct response to the Coordinator's request to authorize `research/prompts/**` and `research/runs/**` for Task-linked Recorder artifacts and commit the preserved Review artifacts.
- Scope: only Recorder prompts and runs linked to `LOOP1-CONTRACT-001`. This is a Task write-boundary amendment, not a change to Frozen Product Architecture, public contracts, acceptance criteria, or the prior independent FAIL findings.
- Task queue/status at decision: `review` / `review`; owner: `unassigned-fresh-fix-agent`.
- Previous independent FAIL evidence: `spec/progress/evidence/LOOP1-CONTRACT-001/2026-09-23-independent-review-5d1d165-fail.md`.
- Previously preserved, untracked Recorder artifacts: prompts `P-5c367892-2b36-4268-9f32-5f29ba567263`, `P-3031f02c-67f1-49c7-b890-295c85627dba`, and empty-registration limitation artifact `P-6d2dcdca-d1e2-400f-b4d8-f180f46d8e23`; runs `R-20260921T080248Z-b5e568c3-afdd-4f81-8ef7-5c3d236e16f4` and `R-20260921T085657Z-61a82ea3-f63b-4315-87b2-d090f3f48905`.
- The earlier commit of Fix-run Recorder artifacts outside the then-declared Task paths remains a permanent governance finding. This authorization does not retroactively mark it compliant.
- The paused Agent's untracked `contracts/http/schema-lint/` remains outside this authorization and must be preserved untouched.

## Coordinator verification

- Recorder prompt `P-34eabb13-8f9a-40e9-a206-d8c3250c295f` captured the Human's `ok` authorization. Coordinator run `R-20260923T033814Z-3344589d-017a-4d5e-9d0f-fd04c8d38abb` uses `prospective_resume`, `pre_recorder_work=true`, `pre_recorder_trace_complete=false`, and experiment group `full_governance`.
- `& .\tools\research\recorder.ps1 run-command --run-id R-20260923T033814Z-3344589d-017a-4d5e-9d0f-fd04c8d38abb -- pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`: exit `0`; repository recovery PASS. This is development evidence, not Task acceptance.
- Both preserved Review runs passed `validate-run` through the Coordinator command wrapper: resumed run `103` events; re-review run `71` events.
- `git diff --check` through the Coordinator command wrapper: exit `0`.
- Before staging, `contracts/http/schema-lint/` still had `554` untracked files and was excluded from the authorized Recorder artifact list.

## Coordinator verification

- Recorder prompt `P-34eabb13-8f9a-40e9-a206-d8c3250c295f` captured the Human's `ok` authorization. Coordinator run `R-20260923T033814Z-3344589d-017a-4d5e-9d0f-fd04c8d38abb` uses `prospective_resume`, `pre_recorder_work=true`, `pre_recorder_trace_complete=false`, and experiment group `full_governance`.
- `& .\tools\research\recorder.ps1 run-command --run-id R-20260923T033814Z-3344589d-017a-4d5e-9d0f-fd04c8d38abb -- pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`: exit `0`; repository recovery PASS. This is development evidence, not Task acceptance.
- Both preserved Review runs passed `validate-run` through the Coordinator command wrapper: resumed run `103` events; re-review run `71` events.
- `git diff --check` through the Coordinator command wrapper: exit `0`.
- Before staging, `contracts/http/schema-lint/` still had `554` untracked files and was excluded from the authorized Recorder artifact list.
