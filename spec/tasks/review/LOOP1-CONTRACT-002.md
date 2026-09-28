---
task_id: LOOP1-CONTRACT-002
title: Freeze WSS Envelope, Auth, and Message contracts
status: review
owner: /root/contract002_fix2
stage: S0
gate: S0
---

# Goal

Define canonical WSS envelopes and auth.bind/ack, message.send/ack/created, and session.revoked contracts.

# Inputs

- Architecture Baseline v1.0 chapters 2, 4, 5, 7, 11, 19 and appendix B, resolved through `spec/architecture/README.md`.
- Approved ADRs/frozen decisions in `spec/architecture/decisions/`.
- `spec/domain/messaging.md`
- `spec/invariants/messaging.md`
- `spec/acceptance/s0-messaging.md`
- Approved error and HTTP contracts from LOOP1-CONTRACT-001.

# Dependencies

- LOOP1-CONTRACT-001 done.
- LOOP1-SPEC-001 done.

# Allowed Paths

- `contracts/websocket/**`
- `contracts/errors/**`
- `contracts/fixtures/**`
- Relevant `spec/domain/**`, `spec/invariants/**`, and `spec/acceptance/**`
- `spec/tasks/**/LOOP1-CONTRACT-002.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CONTRACT-002/**` (Coordinator-authorized task evidence)
- `spec/progress/checkpoints/*loop1-contract-002*.md` (accepted transition only)
- `research/prompts/**` (only Recorder prompts linked to `LOOP1-CONTRACT-002`)
- `research/runs/**` (only Recorder runs linked to `LOOP1-CONTRACT-002`)

The Coordinator prospectively authorizes the task-linked evidence and Recorder paths above to satisfy `AGENTS.md` instrumentation and independent-acceptance requirements. This authorization adds no product contract scope beyond this Task's Goal.

# Acceptance

- Required WSS envelopes and message types are machine-verifiable.
- Contract generation and tests pass, including durable-commit ACK and idempotent retry vectors.

# Forbidden

- Implement Gateway/Core behavior.
- Weaken ACK, authentication, authorization, ordering, or idempotency semantics.
- Modify Sync or Plugin API beyond referenced shared envelope types.

# Verification

- Run `tools/verify-loop1-ctrl-002.ps1 -Mode Development` while editing; run Acceptance only from a clean committed independent review checkout.
- Run contract generator and WSS positive/negative fixture tests.

# Evidence

- Dependencies `LOOP1-CONTRACT-001` and `LOOP1-SPEC-001` are independently accepted and `done` on clean `main` at `7484901`.
- The canonical Markdown architecture and historical PDF hashes matched the baseline manifest; architecture verifier, CTRL-002 Acceptance recovery, and Recorder repository validation passed on clean `main` before activation.
- Coordinator resumed under Recorder prompt `P-ab3f11c8-309b-4368-8ab6-5528b9634839` and run `R-20260928T005917Z-da1e7bcf-0952-4664-b76d-b699a2b59840` with `prospective_resume`; branch activation and earlier same-turn checks are explicitly outside the complete prospective trace.
- Recorder-wrapped CTRL-002 Development initially rejected a short Last Known Good Commit and missing verification entry point, then passed after both records were corrected. Development PASS is not independent acceptance. Evidence: `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-activation.md`.
- Fresh Implementation Agent authored the strict WSS v1 JSON Schema, protocol semantics, deterministic generator/verifier, and 8 positive/10 negative shared Go/Java golden scenarios. Development evidence: `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-implementation-development.md`. Prospective Recorder run: `R-20260928T011345Z-3c7689c2-2116-4c18-97dc-efd0e2f946d1`. Development evidence is not independent acceptance.

- Fresh independent Review Agent `/root/contract002_review1` returned FAIL for clean committed candidate `55670c2`: in-memory negative controls found that `check_scenario` accepts wrong-Conversation delivery, omitted `session.revoked`, omitted negative auth rejection, and `message.created` before COMMIT. Baseline WSS verifier and clean detached CTRL-002 Acceptance passed, so those checks do not establish required behavioral assertions. Durable evidence: `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review-55670c2-fail.md`; review Recorder run `R-20260928T015007Z-9b76e656-7d6d-4f91-91dc-080318cb92a5`. The task remains unfinished in `review`; S0 Gate is not passed.
- Fresh Fix Agent `/root/contract002_fix1` added direct checks for all four review gaps and nine in-memory mutation regressions while preserving the five passing controls. Generator/fixture comparison and CTRL-002 Development passed; development evidence: `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-fix-development.md`; Recorder run `R-20260928T021000Z-97be66ca-3d6f-4b95-855d-3dd6f033714f`. This is not acceptance. Last known good baseline remains `7484901b3915535f60941a01116b730a845bd47d`.
- Fresh independent Review Agent `/root/contract002_review2` rejected clean candidate `102b0ef`: three in-memory auth.bind mutations were accepted (omitted successful auth.ack, valid bind left unauthenticated, and stale-epoch rejection left authenticated). The four prior failures and five earlier controls now reject correctly; baseline WSS verifier, architecture hashes, and clean detached CTRL-002 Acceptance passed. Durable evidence: `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-102b0ef-fail.md`; review Recorder run `R-20260928T022529Z-0d3417e3-6f8e-43df-aae6-2c75a1fe6c3c`. The task stays in review.
- Fresh Fix Agent `/root/contract002_fix2` added direct valid-bind acknowledgement and authenticated-state assertions, rejected-bind unauthenticated-state assertions, and three permanent behavior mutations. WSS verifier rejected 12 behavior mutations; the committed independent probe rejected 12/12 invalid outcomes; CTRL-002 Development passed. This is development evidence only. Details: `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-auth-bind-fix-development.md`; Recorder run `R-20260928T024701Z-63b628c9-0944-46da-b52b-c2f97020a7ee`.

# Handoff

- Activated from clean `main` commit `7484901` on `task/LOOP1-CONTRACT-002`. The original checkout's untracked `contracts/http/schema-lint/` remains owned by the paused Agent and was not touched.
- No architecture conflict or new dependency. Only task-allowed product contracts/fixtures, task-linked evidence/Recorder paths, and recovery records changed. Candidate review commit and clean-state audit are reported to the Coordinator at handoff.

# Next Action

- Delegate a different fresh independent Reviewer to inspect the exact clean committed candidate, repeat the committed in-memory auth.bind probe, and run applicable acceptance verification. Keep in `review` pending independent PASS.
