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

- Fresh independent Review Agent `/root/contract003_review3` accepted clean Fix 2 candidate `15b2477ca44c106e8e69b22b46eacfb7ca301623` under ADR-0001. Baseline verifier passed 79 cases/16 controls; all seven Review 1, both Review 2, and seven new negative mutations rejected; frozen hashes, Fix 2 Recorder integrity, scope, whitespace, and clean detached CTRL-002 Acceptance passed. At S0, SP-A-012's separate static Go/Java normalized artifacts are contract vectors, not backend-produced results; dual-profile runtime parity remains S3 work. Task stays `review` pending Coordinator closure; S0 Gate NOT YET PASSED. Evidence: `spec/progress/evidence/LOOP1-CONTRACT-003/2026-09-28-independent-review3-15b2477-pass.md`; review Recorder run `R-20260928T141143Z-0bf14a8e-dc44-4222-8830-64a84237e98e`.
- Fresh Fix Agent `/root/contract003_fix2` repaired the two Review 2 findings. SP-A-002 now asserts a single pre-existing FAILED local item, convergence to SENT on matching server identity, and terminal SENT after a later failure signal. SP-A-006 now has a machine-verifiable bounded `query.page` response and two linked read-only fixture pages. The task verifier passes 79 cases and 16 controls; Review 1 and Review 2 probes reject 7/7 and 2/2 invalid mutations; CTRL-002 Development passes. This is development evidence only, not independent acceptance. Evidence: `spec/progress/evidence/LOOP1-CONTRACT-003/2026-09-28-fix2-development.md`; Recorder run `R-20260928T132300Z-2ceed8fb-fea6-4ab2-9320-73547e743d4c`. SP-A-012 static-vector interpretation remains the narrow acceptance question.
- Fresh independent Review Agent `/root/contract003_review2` rejected clean Fix 1 candidate `56c14b18a3378ebaade1b4ad4fe85e26aa2f474b`. Task verifier, all seven prior probes, frozen hashes, Fix Recorder integrity, and clean detached CTRL-002 Acceptance passed. Two new mutations are accepted: removing the initial locally FAILED state in SP-A-002 and adding an unbounded simulated Query response to SP-A-006's request-only pagination case. SP-A-012's S0 static-vector interpretation remains unresolved. Task stays `review`; S0 Gate NOT YET PASSED. Evidence: `spec/progress/evidence/LOOP1-CONTRACT-003/2026-09-28-independent-review2-56c14b1-fail.md`; probe: `spec/progress/evidence/LOOP1-CONTRACT-003/review2-negative-probe.py`; review Recorder run `R-20260928T124947Z-fcdac40d-4b7d-406d-ba60-f61ae57ed4a8`.
- Fresh Fix Agent `/root/contract003_fix1` repaired Review 1's oracle findings: staged local materialization and rollback/retry checkpoints, the intermediate gap, full Message identity, each Action attempt's authorization/audit, and ordered upgrade stages/rollback. Separately stored Go/Java normalized contract vectors are checked against canonical outcomes with divergence controls. These are static vectors initially populated from canonical fixtures, not backend execution evidence. The committed review probe rejects 7/7 invalid mutations; the verifier passes 79 cases and 11 mutation controls; CTRL-002 Development passes. This is development evidence only. Evidence: `spec/progress/evidence/LOOP1-CONTRACT-003/2026-09-28-fix1-development.md`; Recorder run `R-20260928T114841Z-4641b577-7645-4011-be22-1baaa30290e5`. Acceptance ambiguity: does SP-A-012 at S0 contract freeze require live backend-produced outcomes, or are distinct static profile contract vectors sufficient pending backend implementation?
- Fresh independent Review Agent `/root/contract003_review1` rejected exact candidate `9a14f6370bf0fb36e9bd51f8b8c91b252e3060ff`. The baseline verifier and clean detached CTRL-002 Acceptance passed, but six of seven in-memory negative mutations retained the expected fixture result: rollback was unobserved, conflicting duplicate content was accepted, first-attempt Action authorization was masked, and upgrade failure stages were interchangeable. The profile loop also repeats one Python oracle without distinct Go/Java outcomes. Task stays `review`; S0 Gate NOT YET PASSED. Durable evidence: `spec/progress/evidence/LOOP1-CONTRACT-003/2026-09-28-independent-review1-9a14f63-fail.md`; probe: `spec/progress/evidence/LOOP1-CONTRACT-003/review1-negative-probe.py`; review Recorder run `R-20260928T112306Z-787dfce3-503e-46a6-9ba8-07bc78565d12`.
- Coordinator review-state transition preserves implementation candidate `9a14f6370bf0fb36e9bd51f8b8c91b252e3060ff`. CTRL-002 Development passed after the queue move; linked Recorder run `R-20260928T110320Z-c950949e-ba78-488e-bd28-2b0a2258efcd` finished and validated (6 events). Evidence: `spec/progress/evidence/LOOP1-CONTRACT-003/2026-09-28-review-transition.md`. Independent acceptance remains pending.
- Fresh Implementation Agent `/root/contract003_impl` added canonical Sync v1 and Plugin API v1 schemas, a machine-readable permission/limit/lifecycle policy, and deterministic shared Go/Java fixtures. Its verifier checks schema structure and values, exact expected outcomes for 79 cases (22 positive, 57 negative), and acceptance IDs SP-A-001 through SP-A-013. It also checks fixture source consistency and two malformed/outcome mutation controls. Development command `python contracts/plugin-api/verify.py` passed with exit 0 (118.3817 ms for the final recorded run). `tools/verify-loop1-ctrl-002.ps1 -Mode Development` passed with exit 0 (1039.2365 ms for the final recorded run). These are development results, not independent acceptance. Evidence: `spec/progress/evidence/LOOP1-CONTRACT-003/2026-09-28-implementation-development.md`; prospective Recorder run `R-20260928T103052Z-d740d63c-ff5a-442e-9080-fbc0d54e86ae`.
- Dependencies `LOOP1-CONTRACT-002` and `LOOP1-SPEC-001` are independently accepted and `done` on clean local `main` at `eb9ebea`. Frozen architecture, WSS, CTRL-002 Acceptance, and Recorder repository checks passed on that checkout before activation. S0 Gate remains NOT YET PASSED.
- Activation Recorder run `R-20260928T100002Z-a86d5739-b9d3-46d6-87f4-c34921fbb4df` finished and validated PASS with 8 events. The current checkout's `tools/verify-loop1-ctrl-002.ps1 -Mode Development` passed with exit 0; this is recovery evidence, not Task acceptance.

# Handoff

- Review 3 changed no product contract or runtime file. It owns only the task-linked independent probe, PASS evidence, Task Spec/current recovery updates, prompt, and Recorder artifacts until review closure commit. Its detached Acceptance checkout is clean at candidate `15b2477`; original `H:\IM-platform\contracts\http\schema-lint` was untouched.
- Fix 2 owns only task-allowed contract, fixture, README, recovery, evidence, and Recorder artifacts until the clean candidate commit. The task remains `review`; no self-acceptance. The original `H:\IM-platform\contracts\http\schema-lint` was untouched.
- Candidate `56c14b18a3378ebaade1b4ad4fe85e26aa2f474b` failed fresh independent Review 2 despite clean-checkout CTRL-002 Acceptance. Reviewer changed only task-linked probe, evidence, prompt, Recorder and recovery files. Detached Acceptance checkout remained clean. Original other-Agent-owned HTTP schema-lint directory was untouched.
- Fix 1 owns only task-allowed oracle/fixture/README changes and linked evidence/Recorder/recovery updates until its clean candidate commit. The task stays `review`; the Fix Agent has not self-accepted. The original `H:\IM-platform` other-Agent-owned untracked HTTP schema-lint directory was untouched.
- Candidate `9a14f6370bf0fb36e9bd51f8b8c91b252e3060ff` failed fresh independent review despite clean-checkout CTRL-002 Acceptance. The reviewer changed only task-linked evidence, probe, recovery files, and Recorder artifacts; no product contract file. The original checkout's other-Agent-owned untracked HTTP schema-lint directory remains untouched.

# Next Action

- Coordinator: close independently accepted Contract 003 under ADR-0001, move this Task Spec to `done`, update progress/checkpoint, and select the next dependency-satisfied task. Keep S0 Gate NOT YET PASSED until all required tasks and Gate evidence pass.
