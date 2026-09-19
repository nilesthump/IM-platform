---
task_id: LOOP1-INFRA-001
title: Establish Compose, PostgreSQL, NATS, and TLS proxy skeleton
status: backlog
owner: unassigned
stage: S0
gate: S0
---

# Goal

Create the Go/Java profile Compose skeleton with shared PostgreSQL, Core NATS, and a real TLS entrypoint.

# Inputs

- Architecture Baseline v1.0 chapters 1, 3, 5, 7, 11, 15, 19 and appendix A.
- Canonical contracts and database migration runner.

# Dependencies

- LOOP1-DB-001 done.

# Allowed Paths

- `deploy/**`
- Non-business profile placeholders under `backend/go/**` and `backend/java/**`
- Infrastructure smoke tests under `tests/**`
- `spec/tasks/**/LOOP1-INFRA-001.md`
- `spec/progress/current.md`

# Acceptance

- A clean checkout can start each backend profile separately with PostgreSQL, NATS, and TLS proxy.
- Smoke checks traverse the real TLS entrypoint.

# Forbidden

- Implement product business modules.
- Mix Go and Java profiles in one runtime profile.
- Introduce Redis, Kafka, Kubernetes, or other unapproved infrastructure.

# Verification

- Run clean-checkout Compose configuration and profile smoke verification.

# Evidence

- Pending.

# Handoff

- Unassigned; no changes yet.

# Next Action

- Promote only after LOOP1-DB-001 is independently accepted.
