---
task_id: LOOP1-RESEARCH-001
title: Insert Research Recorder control plane
status: review
owner: unassigned-independent-review-agent
stage: S0
gate: S0
---

# Goal

Add a file-based, auditable Research Recorder control plane for future Agent runs without implementing product behavior or changing product architecture or contracts.

# Inputs

- Human Architect's 2026-09-21 Research Instrumentation / Recorder Control-Plane Insertion authorization.
- `AGENTS.md`
- `spec/handoff/agent-context.md`
- `spec/progress/current.md`
- Frozen Architecture governance chapters 2, 10, 12 through 14, 19 and 21, resolved through `spec/architecture/README.md`.
- Approved ADRs in `spec/architecture/decisions/`.

# Dependencies

- `LOOP1-CTRL-001`, `LOOP1-CTRL-002`, and `LOOP1-SPEC-001` are done.
- `LOOP1-CONTRACT-001` remains paused in review; its ownership does not transfer to this task.

# Allowed Paths

- `research/**`
- `tools/research/**`
- `tests/research/**`
- `spec/tasks/**/LOOP1-RESEARCH-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-RESEARCH-001/**`
- `AGENTS.md`
- `spec/handoff/agent-context.md`

# Acceptance

- Recorder v1 provides deterministic standard-library entry points for prompt registration, run start/finish, command execution, semantic events, human decisions, CI evidence ingestion, retrospective backfill, and validation.
- Automatic capture covers observable Git and authority facts, append-only event sequencing and hash chaining, final state and diff, true command exit propagation, partial-run detection, immutable finished runs, and secret redaction.
- Tests cover requirements A through L in the Human authorization, including preservation of the paused task and absence of product changes.
- Bootstrap evidence is marked `bootstrap_partial`; backfills are explicitly retrospective; paused-task resume metadata is `prospective_resume` with incomplete pre-recorder trace.
- Fresh independent review and ADR-0001 acceptance are required before an Instrumentation Epoch may be established.

# Forbidden

- Implement any IM product feature or change product code, public contracts, ACK semantics, database business invariants, compatibility rules, or plugin security boundaries.
- Modify, move, clean, stash, or claim ownership of paused-Agent work.
- Create `.github/workflows/**` before the CI task permits it.
- Record or infer hidden reasoning, unavailable platform prompts, token usage, cost, CI success, or reviewer independence.
- Establish an Instrumentation Epoch before fresh independent acceptance.

# Verification

- `& .\tools\research\recorder.ps1 run-command --run-id R-LOOP1-RESEARCH-001-BOOTSTRAP-PARTIAL -- python3 -m unittest discover -s tests/research -v` (or the resolved Python 3 executable as the recorded command)
- `& .\tools\research\recorder.ps1 validate-repository --allow-partial`
- `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Development`
- `git diff --check 1e1523c127c5a0f3baf85d8b5eca11b7b34d80dc..HEAD -- . ':(exclude)research/runs/**/diff.patch'` (archived patches preserve observed whitespace as evidence)
- Independent acceptance from a clean committed checkout repeats the tests and repository verifier under ADR-0001.

# Evidence

- Baseline worktree was clean and detached at `1e1523c127c5a0f3baf85d8b5eca11b7b34d80dc` before branch creation.
- Frozen Architecture SHA-256 matched the manifest: `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`.
- Pre-insertion Auth/User/Friend contract verification passed with exit `0`.
- Recorder content candidate commit: `0a406aef9ecac899556ac6bad8145d8c01127e73`; this task cannot self-accept.
- Development evidence: `spec/progress/evidence/LOOP1-RESEARCH-001/2026-09-21-development.md`.
- Final implementation test run: 17 tests PASS. CTRL-002 Development verifier and diff whitespace check PASS. Exact command results and the preserved earlier FAIL are in the bootstrap event stream and development evidence.
- Bootstrap run finished with 17 events, final observed HEAD `0a406aef9ecac899556ac6bad8145d8c01127e73`, manifest hash `0a29742a25dd9158d91125506b57ad966fb4847d8f56bb92fef8049619d48f1d`, and `pre_recorder_trace_complete=false`. Its result is development evidence, not acceptance.
- The archived `diff.patch` intentionally preserves observed patch whitespace and is excluded from repository whitespace lint; the artifact remains hash-protected and unmodified after finish.

# Handoff

- Original paused task: `LOOP1-CONTRACT-001`, state `review`, owner `unassigned-independent-review-agent`, original worktree `H:\IM-platform`, branch `task/LOOP1-CONTRACT-001`, HEAD `1e1523c127c5a0f3baf85d8b5eca11b7b34d80dc` at insertion observation. Its untracked `contracts/http/schema-lint/` is unknown/paused-Agent-owned and must not be touched.
- Recorder work is isolated at `H:\.codex\worktrees\research-recorder\IM-platform` on `task/LOOP1-RESEARCH-001`.
- No Instrumentation Epoch exists until fresh independent review accepts a committed candidate.
- Implementation is complete but unaccepted. The Implementation Agent has not declared PASS or created an Epoch.

# Next Action

- Delegate a fresh independent Review Agent from a clean detached isolated checkout at the final handoff commit. It must run all Recorder tests, default `validate-repository`, CTRL-002 Acceptance mode, scope/secret/pyc checks, and diff checks. On PASS, record durable independent evidence, establish the Instrumentation Epoch at the accepted commit, then restore `LOOP1-CONTRACT-001` as Current Task without transferring ownership. On FAIL, use a fresh Fix Agent and repeat review.
