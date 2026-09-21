---
task_id: LOOP1-RESEARCH-001
title: Insert Research Recorder control plane
status: done
owner: accepted-independent-review
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
- `& .\tools\research\recorder.ps1 validate-repository`
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
- Fresh independent Review Agent `/root/recorder_review` reviewed commit `96fc13d5e953a8a926a9295dd82847789ed222fc` from a clean detached isolated checkout and returned FAIL. Durable evidence: `spec/progress/evidence/LOOP1-RESEARCH-001/2026-09-21-independent-review-96fc13d-fail.md`.
- Blocking findings: the committed bootstrap run fails default repository validation with a manifest hash mismatch; structured secret keys and quoted JSON prompt values are persisted without redaction; CI ingestion accepts and persists secret-bearing extra fields; and the committed bootstrap prompt bytes do not match their recorded SHA-256.
- Fresh Fix Agent `/root/recorder_fix1` repaired all four findings at content commit `1d850cf8cbe6c9aeec94e43f7395b8901bcb5f78`; 22 tests, default repository validation, CTRL-002 Development mode, prompt blob/hash comparison, diff/scope and generated-file checks pass. This is development evidence, not acceptance.
- Fix evidence: `spec/progress/evidence/LOOP1-RESEARCH-001/2026-09-21-fix-1d850cf-development.md`.
- Fresh independent Review Agent `/root/recorder_review2` accepted candidate `ab3b507241cf51822af79cbcb63dfdf40e273359` from a clean detached isolated checkout under ADR-0001 after repeating all 22 A-L tests, default repository validation, CTRL-002 Acceptance, scope checks, and the four prior-blocker negative controls.
- Durable PASS evidence: `spec/progress/evidence/LOOP1-RESEARCH-001/2026-09-21-independent-review-ab3b507-pass.md`.
- Instrumentation Epoch: `research/INSTRUMENTATION_EPOCH.json`; schema `1.0.0`. Earlier bootstrap/backfill/pilot evidence is not complete prospective trace data.

# Handoff

- Original paused task: `LOOP1-CONTRACT-001`, state `review`, owner `unassigned-independent-review-agent`, original worktree `H:\IM-platform`, branch `task/LOOP1-CONTRACT-001`, HEAD `1e1523c127c5a0f3baf85d8b5eca11b7b34d80dc` at insertion observation. Its untracked `contracts/http/schema-lint/` is unknown/paused-Agent-owned and must not be touched.
- Recorder repair is isolated at `H:\.codex\worktrees\research-recorder-fix\IM-platform` on `fix/LOOP1-RESEARCH-001-1`.
- The Recorder is independently accepted at candidate `ab3b507241cf51822af79cbcb63dfdf40e273359`, and the Instrumentation Epoch is established by the independent acceptance closure.
- Resume `LOOP1-CONTRACT-001` without transferring ownership or rewriting its pre-Recorder history. Before the first resumed operation, safely fast-forward the paused branch to include this acceptance closure, register the actual resume prompt, and start a new `prospective_resume` run with `pre_recorder_work=true` and `pre_recorder_trace_complete=false`.

# Next Action

- Resume the existing paused `LOOP1-CONTRACT-001` review from its owned worktree only after safely incorporating the Recorder acceptance closure, then begin prospective instrumentation at the first post-resume observable operation. Do not select or implement another product task.
