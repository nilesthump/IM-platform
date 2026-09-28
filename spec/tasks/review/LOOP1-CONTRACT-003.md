---
task_id: LOOP1-CONTRACT-003
title: Freeze Sync and Plugin API v1 contracts
status: review
owner: /root
stage: S0
gate: S0
---

# Goal

Define canonical user cursor, per-conversation sequence Sync, and Plugin API v1 Events/Queries/Actions/UI Host contracts.

# Inputs

- Architecture Baseline v1.0 chapters 2, 6, 8, 9, 11, 19 and appendix B, resolved through `spec/architecture/README.md`.
- Approved ADRs/frozen decisions in `spec/architecture/decisions/`.
- `spec/domain/sync-plugin.md`
- `spec/invariants/sync-plugin.md`
- `spec/acceptance/s0-sync-plugin.md`
- Approved HTTP, WSS, and error contracts from LOOP1-CONTRACT-001 and LOOP1-CONTRACT-002.

# Dependencies

- LOOP1-CONTRACT-002 done.
- LOOP1-SPEC-001 done.

# Allowed Paths

- `contracts/plugin-api/**`
- `contracts/websocket/**`
- `contracts/errors/**`
- `contracts/fixtures/**`
- Relevant `spec/domain/**`, `spec/invariants/**`, and `spec/acceptance/**`
- `spec/tasks/**/LOOP1-CONTRACT-003.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CONTRACT-003/**` (Coordinator-authorized task evidence)
- `spec/progress/checkpoints/*loop1-contract-003*.md` (accepted transition only)
- `research/prompts/**` (only Recorder prompts linked to `LOOP1-CONTRACT-003`)
- `research/runs/**` (only Recorder runs linked to `LOOP1-CONTRACT-003`)

The Coordinator prospectively authorizes the task-linked evidence and Recorder paths above to satisfy `AGENTS.md` instrumentation and independent-acceptance requirements. This authorization adds no product contract scope beyond this Task's Goal.

# Acceptance

- User cursor and conversation sequence Sync contracts are machine-verifiable.
- Plugin API v1 Events/Queries/Actions/UI Host contracts are machine-verifiable.
- Fixtures cover duplicate, out-of-order, gap, and permission-denial cases.

# Forbidden

- Implement Sync or plugin runtime behavior.
- Weaken cursor, contiguous sequence, capability, permission, sandbox, or immutable-version rules.

# Verification

- Run `tools/verify-loop1-ctrl-002.ps1 -Mode Development` while editing; use Acceptance only from a clean committed independent review checkout.
- Run schema lint and duplicate/out-of-order/gap/permission fixture tests.

# Evidence

- Fresh independent Review Agent `/root/contract003_review1` rejected exact candidate `9a14f6370bf0fb36e9bd51f8b8c91b252e3060ff`. The baseline verifier and clean detached CTRL-002 Acceptance passed, but six of seven in-memory negative mutations retained the expected fixture result: rollback was unobserved, conflicting duplicate content was accepted, first-attempt Action authorization was masked, and upgrade failure stages were interchangeable. The profile loop also repeats one Python oracle without distinct Go/Java outcomes. Task stays `review`; S0 Gate NOT YET PASSED. Durable evidence: `spec/progress/evidence/LOOP1-CONTRACT-003/2026-09-28-independent-review1-9a14f63-fail.md`; probe: `spec/progress/evidence/LOOP1-CONTRACT-003/review1-negative-probe.py`; review Recorder run `R-20260928T112306Z-787dfce3-503e-46a6-9ba8-07bc78565d12`.
- Coordinator review-state transition preserves implementation candidate `9a14f6370bf0fb36e9bd51f8b8c91b252e3060ff`. CTRL-002 Development passed after the queue move; linked Recorder run `R-20260928T110320Z-c950949e-ba78-488e-bd28-2b0a2258efcd` finished and validated (6 events). Evidence: `spec/progress/evidence/LOOP1-CONTRACT-003/2026-09-28-review-transition.md`. Independent acceptance remains pending.
- Fresh Implementation Agent `/root/contract003_impl` added canonical Sync v1 and Plugin API v1 schemas, a machine-readable permission/limit/lifecycle policy, and deterministic shared Go/Java fixtures. Its verifier checks schema structure and values, exact expected outcomes for 79 cases (22 positive, 57 negative), and acceptance IDs SP-A-001 through SP-A-013. It also checks fixture source consistency and two malformed/outcome mutation controls. Development command `python contracts/plugin-api/verify.py` passed with exit 0 (118.3817 ms for the final recorded run). `tools/verify-loop1-ctrl-002.ps1 -Mode Development` passed with exit 0 (1039.2365 ms for the final recorded run). These are development results, not independent acceptance. Evidence: `spec/progress/evidence/LOOP1-CONTRACT-003/2026-09-28-implementation-development.md`; prospective Recorder run `R-20260928T103052Z-d740d63c-ff5a-442e-9080-fbc0d54e86ae`.
- Dependencies `LOOP1-CONTRACT-002` and `LOOP1-SPEC-001` are independently accepted and `done` on clean local `main` at `eb9ebea`. Frozen architecture, WSS, CTRL-002 Acceptance, and Recorder repository checks passed on that checkout before activation. S0 Gate remains NOT YET PASSED.
- Activation Recorder run `R-20260928T100002Z-a86d5739-b9d3-46d6-87f4-c34921fbb4df` finished and validated PASS with 8 events. The current checkout's `tools/verify-loop1-ctrl-002.ps1 -Mode Development` passed with exit 0; this is recovery evidence, not Task acceptance.

# Handoff

- Candidate `9a14f6370bf0fb36e9bd51f8b8c91b252e3060ff` failed fresh independent review despite clean-checkout CTRL-002 Acceptance. The reviewer changed only task-linked evidence, probe, recovery files, and Recorder artifacts; no product contract file. The original checkout's other-Agent-owned untracked HTTP schema-lint directory remains untouched.

# Next Action

- Coordinator delegates a fresh Fix Agent to repair the independent findings recorded in `2026-09-28-independent-review1-9a14f63-fail.md`, then a different fresh independent Review Agent. Keep task in `review`; do not claim acceptance or Gate PASS from baseline checks.
