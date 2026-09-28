---
task_id: LOOP1-INFRA-001
title: Establish Compose, PostgreSQL, NATS, and TLS proxy skeleton
status: active
owner: /root
stage: S0
gate: S0
---

# Goal

Create the Go/Java profile Compose skeleton with shared PostgreSQL, Core NATS, and a real TLS entrypoint.

# Inputs

- Architecture Baseline v1.0 chapters 1, 3, 5, 7, 11, 15, 19 and appendix A, resolved through `spec/architecture/README.md` and its canonical Markdown manifest. Apply approved ADRs.
- Canonical contracts and database migration runner.

# Dependencies

- LOOP1-DB-001 done.

# Allowed Paths

- `deploy/**`
- Non-business profile placeholders under `backend/go/**` and `backend/java/**`
- Infrastructure smoke tests under `tests/**`
- `spec/tasks/**/LOOP1-INFRA-001.md`
- `spec/progress/current.md`

The Coordinator prospectively authorizes task-linked `spec/progress/evidence/LOOP1-INFRA-001/**`, accepted checkpoint `spec/progress/checkpoints/*loop1-infra-001*.md`, and this task's `research/prompts/**` and `research/runs/**` artifacts for instrumentation, review, and handoff only. These paths do not authorize product-scope expansion.

# Acceptance

- A clean checkout can start each backend profile separately with PostgreSQL, NATS, and TLS proxy.
- Smoke checks traverse the real TLS entrypoint.

# Forbidden

- Implement product business modules.
- Mix Go and Java profiles in one runtime profile.
- Introduce Redis, Kafka, Kubernetes, or other unapproved infrastructure.

# Verification

- Run clean-checkout Compose configuration and profile smoke verification.
- Run `tools/verify-loop1-ctrl-002.ps1 -Mode Development` during development; Acceptance must run only from a clean committed independent checkout.

# Evidence

- Activation prompt `P-cf192254-2cdd-4cd1-9944-79cb3708fadc`, Recorder run `R-20260928T181929Z-4868929c-ccfb-45e1-8edc-860dbc5fe2b9` finished and validated PASS (10 events). CTRL-002 Development recovered task in `active`; frozen architecture hashes passed; Docker Compose v5.1.4 is available. Pre-run activation steps and the corrected stale abbreviated commit are disclosed at `spec/progress/evidence/LOOP1-INFRA-001/2026-09-29-activation-development.md`. This is not independent acceptance.
- Dependency `LOOP1-DB-001` is independently accepted and `done` at clean local `main` `3e4d0f3cb3030731345288f677d2048d72651fd5`; post-integration PostgreSQL tests, frozen hashes, CTRL-002 Acceptance, and Recorder repository validation passed. S0 Gate remains NOT YET PASSED.

# Handoff

- Coordinator `/root` activated on isolated branch `task/LOOP1-INFRA-001` from clean accepted local `main` `3e4d0f3cb3030731345288f677d2048d72651fd5`. Fresh Implementation Agent to take product work after activation handoff. No product infrastructure file changed at activation; Coordinator owns only this task/current/evidence/Recorder activation set until committed. Original checkout's untracked `contracts/http/schema-lint` remains under a paused Agent's sole ownership and untouched.

# Next Action

- Fresh Implementation Agent: implement only the allowed Compose/TLS skeleton and meaningful smoke tests, record development verification, then hand off a clean candidate for fresh independent review. Do not claim Task or S0 Gate PASS from development output.
