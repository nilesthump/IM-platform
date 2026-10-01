---
task_id: LOOPX-AREA-NNN
title: Short task title
status: backlog
owner: unassigned
stage: SX
gate: SX
---

# Goal

State one bounded outcome.

# Inputs

- Resolve/hash-check spec/architecture/README.md -> baseline.md -> canonical Markdown; list exact approved ADR, domain, invariant, acceptance and contract inputs.
- Business tasks MUST read canonical §3/§10 SRC-01 through SRC-07/§11 plus spec/governance/minimality.md, execution-boundaries.md and independent-review.md. Java uses these same authorities, never Go layout.

# Technology Authorization

- Cite the accepted canonical clause/ADR for every new sensitive language, framework, runtime and dependency. For client paths declare one exact `client_language:`, `client_framework:`, `client_runtime:` or `client_dependency:` name per line. Unapproved/TBD runtime work is BLOCKED_BY_ARCHITECTURE; this section cannot authorize itself.

# Dependencies

- List completed prerequisite task IDs or `none`.

# Allowed Paths

- `backend/<language>/<responsible-service>/<task-area>/**` (replace with actual narrow paths)
- List exact presently required assembly/build/test/support exceptions within SRC rules. allowed_paths is never an architecture waiver.
- Temporary migration: name source/destination files, responsibility, approval, scope and acceptance exit before edits; unresolved conflicts escalate before implementation.

# Acceptance

- State independently verifiable behavior plus applicable ownership, root whitelist and service/shared dependency outcomes.
- Require fresh independent Review of actual responsibility/imports/minimality and hosted CI for exact candidate SHA/required jobs. Local or Recorder PASS is not acceptance; Task PASS is not Stage Gate PASS.

# Forbidden

- State changes that are out of scope or require architecture approval.

# Minimality

- What is the smallest implementation satisfying this task?
- Which new abstractions, dependencies, or infrastructure have a current justification?
- Which future work stays outside this task?
- For non-obvious complexity, cite the current requirement or evidence.

# Verification

- Record exact available commands, expected results and minimum baseline verification, including frozen integrity and recovery.
- Bind structural/dependency commands to independently accepted stage-three checkers before business activation; planned tools are not executable evidence.
- List integration enable conditions/services; an unset-variable skip is unexecuted. Check each backend stage independently without requiring premature Java business or permanent exemptions.

# Evidence

- Record actual command results and durable evidence locations. Local PASS is not Gate PASS.

# Handoff

- Record completed work, changed files/migrations, known failures/risks/assumptions, uncommitted-change ownership, last known good commit, checkpoint, and architecture conflicts.

# Next Action

- State one exact next action.


## Technology authorization

Read `spec/governance/technology-selection.md` and canonical §2.3 / §6.1 before implementation or Review. Every new architecture-sensitive language/framework/runtime/core dependency requires traceable accepted Frozen Architecture / approved ADR authority. Missing decision: stop affected work BLOCKED_BY_ARCHITECTURE -> smallest question -> Human/Architect decision -> freeze -> fresh independent Review/applicable exact-head hosted CI -> implementation. Task text/allowed_paths/tests cannot approve selection. Reviewer FAIL on absent authority; inspect real imports/native responsibility beyond static guards. Desktop native SQLite is explicitly Tauri + SQLx(SQLite) with atomic transaction adapter; TypeScript holds Repository/models/transaction intent. No separate tauri-plugin-sql execute-call transactions. Mobile is Android Kotlin + Jetpack Compose, validated on Android Studio emulator. Mobile models/Repository/protocol/plugin adapters implement equivalent behavior under the same canonical contracts/fixtures; direct TypeScript SDK reuse is not required. Web/Desktop/shared stay TypeScript. Android SDK/Gradle/Kotlin/Compose engineering identifiers do not authorize Room/ORM/network libraries, JS runtime/bridge/codegen or shared native rewrite.
