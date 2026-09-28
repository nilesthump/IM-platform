---
task_id: LOOP1-CONTRACT-002
title: Freeze WSS Envelope, Auth, and Message contracts
status: active
owner: /root
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

# Handoff

- Activated from clean `main` commit `7484901` on `task/LOOP1-CONTRACT-002`. The original checkout's untracked `contracts/http/schema-lint/` remains owned by the paused Agent and was not touched.

# Next Action

- Register the visible continuation prompt, start a prospective Recorder run, then implement the WSS contracts and task verifier within the allowed paths. Hand off a clean committed candidate for fresh independent review.
