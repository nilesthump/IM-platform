# Repository Agent Entry Point

`AGENTS.md` is the authoritative repository-level instruction entrypoint for every coding agent.

## Mandatory startup sequence

Before doing any work, every agent MUST read and inspect, in this order:

1. `spec/handoff/agent-context.md`.
2. `spec/progress/current.md`.
3. Read the `Current Task` ID and resolve that exact ID across `spec/tasks/{review,active,ready,backlog,done}/`. It MUST exist in exactly one queue and its declared status MUST match that queue. Resume by actual state: `review` completes the independent review/fix cycle; `active` continues implementation; `ready` may activate only when dependencies and inputs are satisfied; `backlog` remains blocked on prerequisites; `done` permits selection of the next dependency-satisfied task. Never select work merely because `active/` is empty. Select another task only when the current task is complete and no unfinished current task exists.
4. Every architecture document, approved ADR or frozen decision, domain document, invariant, acceptance criterion, and contract referenced by the current Task Spec.
5. `git status`.
6. The current diff.
7. Recent commits.
8. The smallest baseline verification required by the current Task Spec.

Do not implement until the current Task Spec's goal, dependencies, `allowed_paths`, acceptance criteria, forbidden work, and verification are understood.

## Authority and architecture protection

The authority order is:

1. The Frozen Architecture resolved through `spec/architecture/README.md` and its baseline manifest, plus approved ADRs in `spec/architecture/decisions/`.
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
- A task may enter `done` only after accepted independent review and the applicable independent acceptance mechanism.

## Verification, handoff, and checkpoints

CI is the independent acceptance judge. An agent's statement that tests pass is local evidence, not final Gate PASS.

Before `LOOP1-CI-001` is operational and `done`, the approved temporary S0 bootstrap mechanism in `spec/architecture/decisions/` may satisfy a bootstrap/control-plane task's independent acceptance requirement only through a fresh independent reviewer, a clean committed checkout or isolated worktree, deterministic verification, and durable evidence under `spec/progress/evidence/<TASK_ID>/`. Evidence MUST record reviewed commit SHA, clean state/method, branch and diff range, exact command, exit code, elapsed time, result, git status, and reviewer independence. Development-mode output and self-review are never acceptance evidence. This exception expires automatically when `LOOP1-CI-001` becomes `done`; real CI is then mandatory wherever applicable.

Before ending work, update both the current Task Spec and `spec/progress/current.md` with completed work, verification commands and results, known failures or risks, next exact action, last known good commit, and ownership of uncommitted changes. Store run history in durable evidence rather than accumulating it in `current.md`.

Create a checkpoint in `spec/progress/checkpoints/` at a Gate, a stable vertical slice, a contract or schema transition, a release recovery point, or another important stable recovery point. `current.md` points to the latest checkpoint rather than duplicating it.

## Batch Orchestration Protocol

- A Coordinator may execute a named batch or current Stage. It recovers repository state, resolves dependencies, delegates fresh task contexts, waits for results, progresses task queues, updates progress/evidence/checkpoints, and evaluates the Stage Gate.
- Writer concurrency is one. At most one write-capable Agent may modify the repository at a time, especially across contracts, domain/invariants, database migrations, shared SDK/plugin API, and shared acceptance surfaces. Each implementation task SHOULD use a fresh Implementation Agent context.
- At `review`, the Coordinator MUST delegate to a fresh independent Review Agent; an implementer or fixer MUST NOT accept its own work. On PASS, satisfy applicable acceptance evidence, move the task to `done`, update recovery state, and select the next dependency-satisfied task. On FAIL, retain an unfinished state, delegate a fresh Fix Agent, then a new fresh Review Agent, repeating until PASS or a real stop condition.
- Select tasks by dependency satisfaction, not filename order. Use deterministic dependency order unless the batch manifest explicitly permits otherwise. A batch completes only when every required task is `done`, its Gate evidence passes, no blocker remains, `current.md` is current, and a stable recovery point exists.
- Return control only for Batch/Stage Gate PASS, `BLOCKED_BY_ARCHITECTURE`, destructive/high-risk approval, genuine `BLOCKED_EXTERNAL_ACCESS`, irreconcilable repository state, unresolved acceptance ambiguity, or unavailable real subagent delegation (`CAPABILITY_BLOCKED_SUBAGENTS`). Ordinary test or reviewer failures are repair cycles, not stop conditions. Never pretend the same context is independent.
