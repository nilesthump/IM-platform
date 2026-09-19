# Repository Agent Entry Point

`AGENTS.md` is the authoritative repository-level instruction entrypoint for every coding agent.

## Mandatory startup sequence

Before doing any work, every agent MUST read and inspect, in this order:

1. `spec/handoff/agent-context.md`.
2. `spec/progress/current.md`.
3. `spec/tasks/active/`. If an active task exists, continue it. Otherwise select the first dependency-satisfied task from `spec/tasks/ready/`.
4. Every architecture document, approved ADR or frozen decision, domain document, invariant, acceptance criterion, and contract referenced by the current Task Spec.
5. `git status`.
6. The current diff.
7. Recent commits.
8. The smallest baseline verification required by the current Task Spec.

Do not implement until the current Task Spec's goal, dependencies, `allowed_paths`, acceptance criteria, forbidden work, and verification are understood.

## Authority and architecture protection

The authority order is:

1. Frozen Architecture and approved ADRs in `spec/architecture/decisions/`.
2. Machine-verifiable public contracts in `contracts/`.
3. `spec/domain/` and `spec/invariants/`.
4. `spec/acceptance/`.
5. The current Task Spec.
6. Implementation code.

Frozen Architecture and approved ADRs override implementation code. `contracts/` is the sole authority for machine-verifiable public contracts; implementation MUST NOT define or reverse-author contracts.

Without explicit approval, an agent MUST NOT change Frozen Architecture, public contracts, security boundaries, ACK semantics, compatibility rules, or architectural invariants. If a task conflicts with architecture, stop the conflicting portion, mark the task `BLOCKED_BY_ARCHITECTURE`, and record the smallest decision question. Do not redesign silently.

## Change scope and ownership

- Modify only paths listed in the current Task Spec's `allowed_paths`.
- Do not overwrite uncommitted work whose source or ownership is unknown, including work from another agent.
- Do not broaden task scope to make implementation easier.
- Keep task state in exactly one queue: `backlog -> ready -> active -> review -> done`.
- A task may enter `done` only after independent CI Gate PASS and accepted review.

## Verification, handoff, and checkpoints

CI is the independent acceptance judge. An agent's statement that tests pass is local evidence, not final Gate PASS.

Before ending work, update both the current Task Spec and `spec/progress/current.md` with completed work, verification commands and results, known failures or risks, next exact action, last known good commit, and ownership of uncommitted changes.

Create a checkpoint in `spec/progress/checkpoints/` at a Gate, a stable vertical slice, a contract or schema transition, a release recovery point, or another important stable recovery point. `current.md` points to the latest checkpoint rather than duplicating it.

