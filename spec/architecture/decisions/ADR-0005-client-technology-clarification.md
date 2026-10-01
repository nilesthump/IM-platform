# ADR-0005: Client technology clarification and universal selection governance

Status: Human-approved clarification independently accepted at e7c80c7 under bounded Human GString waiver; final administrative confirmation pending before S2 activation.
Date: 2026-10-01
Approval source: spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/approval-and-recovery.md; full explicit Human instruction human-approved-request.txt and supplemental human-desktop-sqlx-mobile-emulator-decision.txt in the same directory (raw-byte SHA25691033f339f337105bc70f45b20c312b8ed2490d01c0b1607e197cda6e09c770b; normalized prompt SHA25678aa2191a4f3614185781a17ebd5204c949312d3a8eb159435af469d0d1929b5; Recorder P-CLIENT-SQLX-DECISION-20261001).

## Motivation and decision

PR7 implemented Dart SQLite despite missing architecture authorization. PR8 restored main3f352a8e465c0c4b093cca8e5f404ea587550b6e to accepted pre-PR7 tree. The withdrawn attempt and its tests/reviews are historical evidence, not authority or new acceptance.

Canonical §2.3 freezes universal no-unapproved-technology governance; §6.1 freezes React/TypeScript memory-only Web, Tauri/React/TypeScript SQLite Desktop and Android Kotlin + Jetpack Compose SQLite Mobile. Web/Desktop/shared protocol/plugin/models/Repository/domain/UI remain TypeScript, necessary Desktop Rust is confined to clients/desktop/src-tauri. Mobile uses Kotlin equivalent models/Repository/behavior/adapters under the SAME canonical contracts/fixtures; no mandatory direct TypeScript SDK reuse, new public contract, JS runtime/bridge/codegen or shared native rewrite. Android Studio emulator validates the real Mobile runtime; host tests/mocks cannot replace it. Android SDK/Gradle/Kotlin/Compose engineering identifiers and built-in Android SQLite access follow the approved stack, not arbitrary Room/ORM/network/native dependencies.

Supplemental Desktop approval remains Tauri + SQLx(SQLite). TypeScript holds shared Repository/models/transaction intent; Rust only connections, queries and atomic transaction adapter. Independent tauri-plugin-sql execute() calls MUST NOT simulate a cross-call transaction. Other sensitive dependency choices remain subject to §2.3.

Approval chain: original full Human instruction -> supplemental Desktop SQLx/emulator instruction -> NEW exact Human answer “moblie明确为kotlin jetpack compose，移除moblie ts技术栈”. Latest answer supersedes ONLY the original Mobile TS/TBD/direct-TS-reuse clauses. Raw evidence: spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/human-mobile-kotlin-compose-decision.txt; raw-byte SHA2561901f6dcd93069a19b6a88f5249858c8017ad36c71d61a109cbbad2ec5e9c061; normalized Recorder SHA256863da9423040acffa2c11b7e67d6c71673f5d7aeb7edd26954108884b5705dd4; prompt P-CLIENT-MOBILE-KOTLIN-20261001. Candidate188d24a / canonical ac042107 was superseded before independent acceptance, never an accepted baseline. Previous accepted canonical83d124b remains the lineage. Original prompt, approval/recovery and finished Recorder archives remain immutable.

Missing sensitive decision: stop affected work -> smallest question -> Human/Architect -> frozen body/approved ADR -> machine guards -> fresh independent Review/applicable exact-head hosted CI -> product implementation. Task text, allowed_paths, familiarity/popularity/installed tools or passing tests cannot authorize a technology. Go/Java internal variation does not bypass this universal rule.

## Normative effect and compatibility

semantic_change=true: this is a Human-approved architecture clarification, not a representation-only migration. Version remains v1.1; canonical bytes and hash change. Previous canonical SHA25683d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e is preserved in manifest revision history. PDF546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510 remains byte-for-byte unchanged. Older ADRs, checkpoints, PR7/FAIL/Review/Recorder/evidence are immutable. No contract, server schema, ACK/Sync, security or compatibility semantics change. S1 PASS; S2 OPEN.

## Implementation, effectiveness and migration

This bounded prerequisite changes authority, execution governance and existing checker/classifier/CI only, without S2 product code or dependencies. Source/dependency/import/config/workflow/task declaration controls inspect active clients; historical evidence is excluded by exact active path ownership, never deletion. Direct static checks supplement mandatory semantic independent Review of language/dependency authority and Rust responsibility.

New independent Review of clean committed candidate and real applicable exact-head hosted CI must accept this prerequisite before task done or S2 activation. Local/Recorder PASS cannot establish Task/S2 PASS. Acceptance SHA/run/effective point are pending and must be recorded by Coordinator truthfully after acceptance. S4/Java/Loop2 are not advanced. New S2 tasks require fresh authorized TypeScript/Kotlin implementation Review/CI; PR7 cannot be restored or reused as acceptance.

## Rollback

Before acceptance, retain accepted main and repair candidate on FAIL. After acceptance, any authority correction uses a Human-approved corrective ADR and new independently reviewed commit; do not rewrite historical commits/evidence/PDF or silently restore Dart. There is no product/data migration in this prerequisite.

Prompt raw-byte vs Recorder LF-normalized hashes are distinguished in spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/prompt-hash-normalization.md; original approval/recovery and prompt bytes are preserved.

## Accepted clarification discovery (2026-10-01)

Fresh independent Review accepts clean e7c80c726d4799ba3ddab026266be638c9e6b252 under scoped Human GString waiver; original4b5 Review FAIL immutable. Exactpush36881391141 selected5SUCCESS/8correctinactive and PR36881397009 all13/every stepSUCCESS. Canonicalaa2398020beeda5f7f9456aac346da57bd8b75212192123c943c35dfdc80f84c/PDF546915 unchanged. ADR0005 effective at accepted prerequisite. Evidence: spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/2026-10-01-coordinator-resume/acceptance.md. Earlier pending paragraphs are historical; later administrative closure needs NEW independent Review/exactHEADCI before S2activation. No product/contract change; S1PASS/S2OPEN.
