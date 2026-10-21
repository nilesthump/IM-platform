# Scalable Distributed IM Platform

Monorepo for the milestone-gated implementation of the Loop 1 architecture baseline.

AI / coding agents must read [AGENTS.md](./AGENTS.md) first.

Resolve [current architecture](spec/architecture/README.md), follow [execution constraints](spec/governance/execution-boundaries.md) and [independent Review](spec/governance/independent-review.md), and recover the unique Current Task from [spec/progress/current.md](spec/progress/current.md) before selecting work. Current Stage/Gate state and permitted resumption are recorded in `spec/progress/current.md` only; this README intentionally does not duplicate execution state, which changes with every task transition.

## Repository layout

| Path | Role |
| --- | --- |
| `spec/` | Governance and control plane: architecture, ADRs, task queues, domain, invariants, acceptance criteria, progress, evidence |
| `contracts/` | Machine-verifiable public contracts (HTTP, WebSocket, errors, database, plugin API, fixtures); sole authority for public contracts |
| `backend/` | Server sources: `go/` implements the Loop 1 baseline (core, gateway); `java/` is a reserved placeholder path |
| `clients/` | `web/` React, `desktop/` Tauri, `mobile/` Android Kotlin/Jetpack Compose, `shared/` shared TypeScript sources |
| `plugins/` | Plugin fixtures |
| `deploy/` | Deployment topology for the Loop 1 baseline (compose, proxy, observability) |
| `tests/` | Cross-cutting suites: architecture, ci, clients, compatibility, contract, database, e2e, go, infrastructure, integration, load, research |
| `ci/` | Bounded diff classifier and architecture/gate/planning checkers driving the CI job matrix |
| `tools/` | Verification helpers and the Research Recorder |
| `research/` | Non-product research control plane (Recorder prompts, runs, schema); research evidence is never product acceptance evidence |
| `scalable-distributed-im-architecture.pdf` | Immutable historical architecture provenance; the canonical architecture is the Markdown resolved through `spec/architecture/README.md` |
