---
task_id: LOOP1-CLIENT-ARCH-CLARIFICATION-001
title: Human-approved v1.1 client technology clarification and selection guards
status: review
owner: Coordinator; fresh independent Review pending
stage: S2
gate: S2
---

# Goal

Complete the separately accepted authority/governance/machine-guard prerequisite to S2 restart. Freeze Human-approved React/TypeScript Web, Tauri/React/TypeScript Desktop, Android Kotlin + Jetpack Compose Mobile, Web/Desktop/shared TypeScript direction and strict universal Agent technology-selection process. Keep version v1.1, disclose changed canonical bytes/hash and preserve PDF/history. No S2 product code in this task.

# Inputs

- spec/architecture/README.md -> baseline.md -> canonical Frozen Architecture SHA25683d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e; unchanged PDF546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510.
- Canonical sections2,3,6,10 SRC-01 through SRC-07,11,12-15,19-21 and AppendixA/B. Existing ADR0001 expired, ADR0002/0003/0004 historical immutable.
- spec/governance/minimality.md, execution-boundaries.md, independent-review.md; AGENTS.md, agent-context.md, TASK_TEMPLATE.md.
- Full human-approved-request.txt and approval-and-recovery.md in this task evidence directory authorize this specific authority revision; not authority for unspecified dependencies/frameworks. Supplemental exact Human Desktop SQLx(SQLite)/Mobile emulator decision is byte-preserved at spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/human-desktop-sqlx-mobile-emulator-decision.txt (raw-byte SHA25691033f339f337105bc70f45b20c312b8ed2490d01c0b1607e197cda6e09c770b; normalized prompt SHA25678aa2191a4f3614185781a17ebd5204c949312d3a8eb159435af469d0d1929b5).
- ci/check_architecture.py, ci/classify.py, ci/check_gate.py, ci/architecture-checks.md, tools/verify_frozen_architecture.py and tests/architecture + tests/ci.

# Dependencies

- LOOP1-E2E-001 done; S1 PASS accepted actual maina0f0f137 restored by PR8.
- LOOP1-CI-001 done and operational; exact-head real hosted CI mandatory.
- LOOP1-RESEARCH-001 done with Instrumentation Epoch; prospective Recorder mandatory.

# Allowed Paths

- `spec/architecture/frozen-architecture.md`
- `spec/architecture/baseline.md`
- `spec/architecture/README.md`
- `spec/architecture/decisions/ADR-0005-client-technology-clarification.md`
- `AGENTS.md`
- `spec/handoff/agent-context.md`
- `spec/tasks/TASK_TEMPLATE.md`
- `spec/governance/technology-selection.md`
- `spec/governance/execution-boundaries.md`
- `spec/governance/independent-review.md`
- `ci/check_architecture.py`
- `ci/classify.py`
- `ci/architecture-checks.md`
- `.github/workflows/ci.yml`
- `tools/verify_frozen_architecture.py`
- `tests/architecture/**`
- `tests/ci/**`
- `spec/tasks/**/LOOP1-CLIENT-ARCH-CLARIFICATION-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/**`
- `spec/progress/checkpoints/*client-architecture*.md`
- `research/prompts/**`
- `research/runs/**`

allowed_paths does not waive architecture. Coordinator owns approval/recovery copies; new implementation may not rewrite them. External Recorder preferred. No modifications to historical ADR/evidence/Recorder/PDF, clients/, backend/, contracts/, migrations or deployment.

# Acceptance

- Canonical body explicitly captures every Human-approved client rule; v1.1 remains, current hash and revision metadata updated truthfully. New Human-approved ADR records motivation/impact/effectiveness/migration/rollback, PR7 withdrawn deviation, unchanged PDF and previous hash. Old ADR facts unchanged.
- Web memory-only/noSQLite/no offline history over HTTPS/WSS; Desktop Tauri native Rust only clients/desktop/src-tauri, business/repository API/protocol/model/plugin SDK stay TypeScript; Mobile Android Kotlin + Jetpack Compose with equivalent behavior/models/adapters under same contracts/fixtures and Android Studio emulator validation; no mandatory direct TS reuse. No S4 implementation.
- Universal selection governance covers all listed architecture-sensitive categories; missing decision stops affected work BLOCKED_BY_ARCHITECTURE, smallest question -> Human/Architect decision -> frozen body/approved ADR -> independent Review/applicable CI -> product implementation. Task paths/tests/popularity/installed tools cannot authorize selection. Reviewer traces every new sensitive technology to accepted authority.
- Effective guard examines current clients/shared/web/desktop/mobile plus client CI/build configuration; rejects Dart/pubspec/Flutter/setup-dart and unapproved framework/runtime/dependency; source allowlist respects TS ecosystem/config/assets and limited Desktop Rust boundary. Historical archives are not active product and remain preserved. No grep-zero destruction.
- Negative controls prove forbidden sources/config/workflow/dependencies and unapproved new framework proposed in Task or implementation FAIL despite allowed_paths/tests. Positive controls show authorized TS/Tauri and Mobile Android Kotlin/Compose Gradle/source/tooling resources pass; negative controls directly reject Android plugin/dependency/build/workflow changes including Room/network/unapproved frameworks and Mobile TS. Future authorization only via changed authority/new accepted decision, never task-only allowlist.
- Path-aware classification selects architecture for every client change including deletion plus applicable jobs; current workflow includes effective checking and gate enforcement with no failure suppression. Sourceall/current tests remain mandatory.
- Fresh independent Review of clean exact committed candidate/range, followed by actual applicable exact-head hosted successful required jobs. Missing/failed/cancelled/anomalously skipped jobs cannot PASS. S2 product coding begins only after this task is accepted done; S2 Gate stays OPEN.

# Forbidden

- S1 implementation/public contracts/ACK/Sync invariants/security/compatibility/server schema changes; PDF/old ADR/archive changes; Dart/Flutter restoration; selecting any additional Mobile framework/ORM/network/runtime/native dependency, Mobile TS/JS runtime/bridge/codegen/shared native rewrite, or Desktop native SQLite crate/plugin other than approved SQLx(SQLite); early Java/S4/Loop2.
- Presenting previous PR7 tests/Review, local or Recorder PASS as this task/new TS/S2 acceptance.

# Minimality

Extend existing architecture verifier/checker/classifier and governance documents directly. No product dependency, general framework or speculative plugin machinery. Negative controls are currently required for the concrete PR7 selection failure.

# Verification

Entry points: `tools/verify-loop1-ctrl-002.ps1` and `tools/verify-frozen-architecture.ps1`.

Baseline: pwsh -NoProfile -File tools/verify-frozen-architecture.ps1 PASS34 tests; hashes/tree/audit confirmed in approval-and-recovery.md. Recheck isolated baseline Recovery Development before edits.

- pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development; independent clean committed -Mode Acceptance.
- pwsh -NoProfile -File tools/verify-frozen-architecture.ps1
- bundled Python -B ci/check_architecture.py --scope all --json
- bundled Python -B -m unittest discover -s tests/architecture -v
- bundled Python -B -m unittest discover -s tests/ci -v
- git diff --check; hash/tree preservation and current active-client audit.
- Real hosted CI exact candidate: verify selection and each actual required conclusion, not aggregate alone. Full workflow-trigger changes select all jobs.

# Evidence

spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/approval-and-recovery.md
External Coordinator Recorder H:/.codex/evidence/client-architecture-20261001/research/runs/R-CLIENT-ARCH-20261001; incomplete read-only pre-Recorder startup disclosed.

# Handoff

Current review task remains unfinished during new Human-authorized Mobile correction. Sole writer Fix Agent owns H:/ica candidate edits; original H:/IM-platform and H:/icr preserved. Prior implementation evidence/Recorder immutable. Last known good rollback main3f352a8e465c0c4b093cca8e5f404ea587550b6e; S1 PASS/S2 OPEN. No product code or services started by this Fix Agent; Coordinator owns its adb tooling daemon.

# Next Action

Commit locally verified revised candidate, finish/validate linked Recorder and expose any archive-only postfinish commit. Release sole writer to Coordinator; NEW fresh independent Review from rollback base3f352a8, clean Recovery Acceptance and real exact-head hosted CI before done/product activation.

## Implementation completion (2026-10-01)

Bounded authority/governance/guards completed; local verification above PASS with exposed first Recovery/CI fixture failures repaired. Final architecture42 no skips, CI30 with4 existing Windows privilege skips, sourceall zero violations, frozen/product/hash/diff checks PASS. Durable implementation-local.md and implementation-command-history.json record limitations, exact commands and timings. No product code. Prior Mobile TBD statement is superseded by the new Human decision below. Supplemental Human approval freezes Desktop SQLx(SQLite), not product implementation. Last known good rollback main3f352a8e465c0c4b093cca8e5f404ea587550b6e. Isolated writer Implementation Agent owns changed candidate; Coordinator receives clean commit and sole writer release. Next exact action: NEW independent Review of final clean HEAD/range and clean Recovery Acceptance; then actual exact-head hosted CI before done or S2 product activation. S2 OPEN. Checkpoint2026-10-01-client-architecture-review-candidate.md.

Prompt raw-byte vs Recorder LF-normalized hashes are distinguished in spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/prompt-hash-normalization.md; original approval/recovery and prompt bytes are preserved.

Finished linked Recorder PASS67 events/manifest6277d2e77cfd34d406d133c2ba38fe1d32b2f17040bd51ebe80d4576b7812a46; immutable archive and exposed postfinish boundary in task evidence implementation-recorder-summary.md. Clean Recovery Acceptance PASS at implementation c709c2e87b55717cc92a7a662949457af9aa4beb; final archive-only candidate HEAD needs fresh independent Review/exact-head hosted CI. No Gate acceptance.

## Human Mobile correction (2026-10-01; unfinished review)

New exact prompt spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/human-mobile-kotlin-compose-decision.txt (raw SHA1901f6dcd93069a19b6a88f5249858c8017ad36c71d61a109cbbad2ec5e9c061; normalized SHA863da9423040acffa2c11b7e67d6c71673f5d7aeb7edd26954108884b5705dd4) supersedes original Mobile TS/TBD before acceptance. Same allowed_paths; sole correction writer H:/ica, no product changes. Candidate188d24a was never accepted; original full prompt/approval/recovery/Recorder/evidence immutable. New linked Recorder external H:/.codex/evidence/mobile-architecture-correction-20261001/research/runs/R-CLIENT-MOBILE-CORRECTION-20261001; parentR-CLIENT-ARCH-20261001 and relatedR-CLIENT-ARCH-IMPLEMENTATION-20261001. Fresh independent Review from rollback base3f352a8 and real exact-head hosted CI remain mandatory. Current task stays review; S1 PASS/S2 OPEN.

## Mobile correction completion (2026-10-01)

Local candidate84a8868e9f17924e34caded18f2a1c808e60dbd6: Frozen44/no skips, sourceall0, CI30/4 existing Windows symlink privilege skips, Recovery Development + clean committed Acceptance, frozen base scope, whitespace and5797 existing immutable byte hashes PASS. Evidence mobile-correction-local.md, mobile-correction-command-history.json, mobile-correction-preservation.json. Linked Recorder finished/validated PASS52; immutable mobile-correction-recorder.zip and summary expose postfinish archive-only boundary. All initial failures preserved. Final reviewed candidate is final branch HEAD after archive commit, not accepted84a or superseded188. Unique task remains review; new independent Review from rollback3f352a8 and actual exact-head hosted CI before done/product coding. Last known good accepted rollback main3f352a8; Fix Agent releases writer after clean finalHEAD check. No product code/services; Coordinator owns adb tooling daemon.

## Independent Review FAIL and Gradle guard correction (2026-10-01)

Fresh Review exactb941df7bcf202c4f72f0443eaf34f222b38ca3b3 FAIL despite all13 hosted36861112222 SUCCESS: variable apply plugin and unresolved alias.get bypass architecture guard. Immutable full report/probes copied byte-for-byte to spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/gradle-plugin-guard-fix/. Fresh sole writer Fix Agent /root/gradle_plugin_guard_fix directly repairs existing check_android fail-closed declaration recognition and adds bounded RED/GREEN negative + approved literal/directcatalog controls. No authority/product/public contract changes. Task remains review; S1 PASS/S2 OPEN.

Local Frozen46/sourceall0/architecture46/CI30 PASS with4 exposed Windows real-symlink privilege skips; RED3 and external edit-script AssertionError preserved. Recovery Development/clean committed Acceptance and immutable tree/whitespace verification discovery in gradle-plugin-guard-fix/local.md and command-history.json, finished linked Recorder archive follows. Startup read-only work disclosed prospective_resume; full delegated assignment/activation registered with parentR-CLIENT-ARCH-20261001 and relatedR-KOTLIN-REVIEW-20261001. Last known good accepted rollback3f352a8. Writer owns only correction until clean finalcommit/release; no services, Coordinator adbdaemon ownership. Next exact action: NEW independent Reviewer of final cleanHEAD/full3f..HEAD and actual applicable exact-head hosted CI before done/product activation. Prior Human attachments/approval/evidence/Recorder/history immutable, original744 files preserved. Raw Human Markdown12 hardbreak whitespace exception remains exposed; new correction diff checked separately.

Gradle guard Fix Recorder finished/validated PASS61 manifest4b8c3cf2dad66bf2a99e51f80f4f31c7e14b67d7f3a9a054f4ca0e8742b73781; immutable archive/limitations/postfinish boundary in gradle-plugin-guard-fix/recorder-summary.md. Clean Recovery Acceptance PASS5157b4c; final archive-onlyHEAD checks external gradle-plugin-guard-fix-20261001/postfinish.json. Sole writer released after finalcleancommit; NEW independent Review/full3f..HEAD and actual exact-head hosted CI required before done/product. Task remains review/S2 OPEN; no self-acceptance.

## Independent Review FAIL and complete plugin selector correction (2026-10-01)

Fresh Review exact8109b5ec1101efc18294618fd0a88b7499d4cccf FAIL despite all13 hosted36863598509 SUCCESS: approved literal prefix can transform into builtin java plugin; actual Gradle9.1/Java25 proof. Fresh sole writer Fix Agent /root/plugin_literal_guard_fix validates complete id/kotlin arguments, rejects unsupported plugins block entries and typedapply, preserves approved literal/catalog/version/applyfalse and Kotlin configuration notation. Added concrete RED/GREEN controls; no authority/public contract/dependency/product change. Local Frozen49/no skips, sourceall0, CI30/4 existing Windows real-symlink privilege skips PASS. Initial RED18 and first GREEN1 repaired failure preserved. Required Recovery, immutable Git tree scope/whitespace audit and clean committed Acceptance discovery follows in plugin-literal-guard-fix/local.md and command-history.json. Full independent report/probe/runtimeproof copies byte-preserved there. Complete delegated assignment/dispatch/activation registered; Recorder prospective_resume parentR-CLIENT-ARCH-20261001/relatedR-GRADLE-INDEPENDENT-REVIEW-20261001. Prior authority/approval/human prompts/PDF/ADRs/evidence/Recorder unchanged. Sole Fix writer owns this bounded correction until clean final commit/release, then NEW independent Review/full3f..HEAD + actual exact-head hosted CI; no selfacceptance/push/merge/done/product. Last known good rollback3f352a8; task review/S2 OPEN; no services; Coordinator adb ownership. Latest checkpoint2026-10-01-client-architecture-plugin-literal-guard-fix.md.

Complete-selector Fix local Recovery Acceptance PASS clean0479af2;5943 prior Git tree objects and744 original unknown files unchanged,23 copied raw proof hashes verified. CR-aware correction/fullrange excludingONLY unchangedrawHuman PASS; fullrangeFAIL12 intentional rawHuman hardbreaks preserved. Raw Gradle/CI logs stored byte-identical ZIP members; initial staged log whitespace/audit/provenance errors retained and corrected. Final clean Recorder archive and release discovery follows plugin-literal-guard-fix/recorder-summary.md; NEW fresh independent Review/exact-head CI required. Task review/S2 OPEN, no product changes.
