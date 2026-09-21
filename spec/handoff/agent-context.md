# Agent Context

## Project

This repository implements **Scalable Distributed Instant Messaging Platform for 100k-class Online Connections**. Loop 1 establishes a correct, testable single-machine baseline; future capacity targets must not be presented as current capability.

## Long-lived working rules

- Delivery is **milestone-gated**, not calendar-gated. Budget weeks do not authorize waiting after Gate PASS or advancing before Gate PASS.
- Frozen Architecture and approved ADRs MUST NOT be silently changed by implementation agents. Conflicts are recorded as `BLOCKED_BY_ARCHITECTURE` with the smallest decision question.
- `contracts/` is the sole machine-verifiable authority for public HTTP, WSS, error, database, sync, and plugin contracts. Implementations conform to contracts; they do not define them.
- Start by following the exact read and inspection order in `AGENTS.md`: this file, current progress, the exact Current Task resolved across all five queues, referenced authority inputs, repository state, then minimum baseline verification. A task under `review/` remains current even when `active/` is empty.
- Resolve the repository-resident Frozen Architecture through `spec/architecture/README.md` and verify its manifest hash before relying on it.
- A Task Spec's `allowed_paths` is a hard write boundary. Preserve unknown or other-agent uncommitted work.
- CI is an independent judge. Local verification is evidence, not final Gate PASS. Until LOOP1-CI-001 is operational and done, only the architect-approved bootstrap acceptance ADR may substitute a fresh independent clean-checkout review for the unavailable CI role; development mode and self-review never qualify.

## Handoff

Before yielding, update the current Task Spec and `spec/progress/current.md`. Record current task/stage/gate, completed work, changed files or migrations, exact verification command and result, durable evidence location, known failures/risks/assumptions, next exact action, last known good commit, uncommitted-change ownership, and any architecture conflict requiring ACP/ADR. Keep run history in `spec/progress/evidence/`, not in `current.md`.

After the independently accepted Research Recorder Instrumentation Epoch, register the visible prompt and create a Recorder run before prospective work. Use `prospective_resume` plus incomplete pre-Recorder-trace markers when resuming older work. Recorder artifacts are research evidence only; they neither replace acceptance evidence nor authorize changes to product authority.

## Checkpoints

Create a checkpoint for a stable Gate, important vertical slice, contract/schema version transition, release recovery point, or other important stable recovery state. A checkpoint records the commit (or `none` before the first commit), contract and migration versions when applicable, fixture/artifact versions when applicable, verified Gate state, and known limitations. `spec/progress/current.md` points to the latest checkpoint.
