# Agent Context

## Project

This repository implements **Scalable Distributed Instant Messaging Platform for 100k-class Online Connections**. Loop 1 establishes a correct, testable single-machine baseline; future capacity targets must not be presented as current capability.

## Long-lived working rules

- Delivery is **milestone-gated**, not calendar-gated. Budget weeks do not authorize waiting after Gate PASS or advancing before Gate PASS.
- Frozen Architecture and approved ADRs MUST NOT be silently changed by implementation agents. Conflicts are recorded as `BLOCKED_BY_ARCHITECTURE` with the smallest decision question.
- `contracts/` is the sole machine-verifiable authority for public HTTP, WSS, error, database, sync, and plugin contracts. Implementations conform to contracts; they do not define them.
- Start by following the exact read and inspection order in `AGENTS.md`: this file, current progress, the exact Current Task resolved across all five queues, referenced authority inputs, repository state, then minimum baseline verification. A task under `review/` remains current even when `active/` is empty.
- Resolve the repository-resident canonical Frozen Architecture Markdown through `spec/architecture/README.md` and verify its manifest hash before relying on it. The PDF is an immutable historical snapshot with a separate provenance hash.
- A Task Spec's `allowed_paths` is a hard write boundary. Preserve unknown or other-agent uncommitted work.
- CI is an independent judge. Local verification is evidence, not final Gate PASS. Until LOOP1-CI-001 is operational and done, only the architect-approved bootstrap acceptance ADR may substitute a fresh independent clean-checkout review for the unavailable CI role; development mode and self-review never qualify.

## Handoff

Before yielding, update the current Task Spec and `spec/progress/current.md`. Record current task/stage/gate, completed work, changed files or migrations, exact verification command and result, durable evidence location, known failures/risks/assumptions, next exact action, last known good commit, uncommitted-change ownership, and any architecture conflict requiring ACP/ADR. Keep run history in `spec/progress/evidence/`, not in `current.md`.

After the independently accepted Research Recorder Instrumentation Epoch, register the visible prompt and create a Recorder run before prospective work. Use `prospective_resume` plus incomplete pre-Recorder-trace markers when resuming older work. Recorder artifacts are research evidence only; they neither replace acceptance evidence nor authorize changes to product authority.

## Checkpoints

Create a checkpoint for a stable Gate, important vertical slice, contract/schema version transition, release recovery point, or other important stable recovery state. A checkpoint records the commit (or `none` before the first commit), contract and migration versions when applicable, fixture/artifact versions when applicable, verified Gate state, and known limitations. `spec/progress/current.md` points to the latest checkpoint.

## Current execution constraints

Before business implementation read canonical §3/§10 SRC-01 through SRC-07/§11 and spec/governance/execution-boundaries.md. allowed_paths is never an architecture exemption; narrow ordinary scopes, explicitly authorize temporary migration maps and exit. Review uses spec/governance/independent-review.md for behavior, actual ownership, imports and minimality. Java future tasks derive from canonical §20 and the current task template, not Go layout.

LOOP1-CI-001 is operational and done, so ADR-0001 is expired. Verify hosted candidate SHA and actual required job conclusions. Current four-stage remediation suspends Social/Message/E2E/Java/plugin business. Historical Auth done is retained under old checks; Go remediation product candidate d0ae52f5615320790ae7039cb48831873de6f486 is independently reviewed and accepted by hosted run36744072690; evidence004/final-hosted-acceptance.md. Historical stage003 source_go/Gate FAIL was expected before migration and remains preserved. Applicable source/dependency checks remain mandatory; no grandfather exception. Administrative candidate f4fdd82 is accepted by new CLI independent Review and hosted36749210695; final status-record confirmation follows current.md and external final acceptance summary; S1 product Gate remains OPEN. The unique task in current.md controls resumption. Stage-three checkers are bounded accepted at2afeac8/run36726926394: ci/check_architecture.py --scope all --json and tests/architecture (evidence003/hosted-acceptance.md); stage-three expected Go failures alone cannot close the batch or S1 Gate. Final administrative resumption is specified by current.md.

## Technology authorization

Read `spec/governance/technology-selection.md` and canonical §2.3 / §6.1 before implementation or Review. Every new architecture-sensitive language/framework/runtime/core dependency requires traceable accepted Frozen Architecture / approved ADR authority. Missing decision: stop affected work BLOCKED_BY_ARCHITECTURE -> smallest question -> Human/Architect decision -> freeze -> fresh independent Review/applicable exact-head hosted CI -> implementation. Task text/allowed_paths/tests cannot approve selection. Reviewer FAIL on absent authority; inspect real imports/native responsibility beyond static guards. Desktop native SQLite is explicitly Tauri + SQLx(SQLite) with atomic transaction adapter; TypeScript holds Repository/models/transaction intent. No separate tauri-plugin-sql execute-call transactions. Mobile is Android Kotlin + Jetpack Compose, validated on Android Studio emulator. Mobile models/Repository/protocol/plugin adapters implement equivalent behavior under the same canonical contracts/fixtures; direct TypeScript SDK reuse is not required. Web/Desktop/shared stay TypeScript. Android SDK/Gradle/Kotlin/Compose engineering identifiers do not authorize Room/ORM/network libraries, JS runtime/bridge/codegen or shared native rewrite.
