# ADR-0005: Client technology clarification and universal selection governance

Status: Human-approved clarification candidate; independent Review and exact-head hosted CI pending. Product implementation cannot use this candidate until acceptance.
Date: 2026-10-01
Approval source: spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/approval-and-recovery.md; full explicit Human instruction human-approved-request.txt and supplemental human-desktop-sqlx-mobile-emulator-decision.txt in the same directory (raw-byte SHA25691033f339f337105bc70f45b20c312b8ed2490d01c0b1607e197cda6e09c770b; normalized prompt SHA25678aa2191a4f3614185781a17ebd5204c949312d3a8eb159435af469d0d1929b5; Recorder P-CLIENT-SQLX-DECISION-20261001).

## Motivation and decision

PR7 implemented Dart SQLite despite missing architecture authorization. PR8 restored main3f352a8e465c0c4b093cca8e5f404ea587550b6e to accepted pre-PR7 tree. The withdrawn attempt and its tests/reviews are historical evidence, not authority or new acceptance.

Canonical §2.3 freezes universal no-unapproved-technology governance; §6.1 freezes React/TypeScript memory-only Web, Tauri/React/TypeScript SQLite Desktop and TypeScript SQLite Mobile with framework TBD, shared TypeScript protocol/plugin/models/domain/UI direction and limited necessary Desktop Rust native adapter. Repository API/business/protocol/model/plugin SDK remain TypeScript. Supplemental Human decision explicitly approves Tauri + SQLx(SQLite) Desktop native boundary. TypeScript holds shared Repository, models and transaction intent; Rust only provides database connections, queries and atomic transaction adapter. Multiple independent tauri-plugin-sql execute() calls MUST NOT simulate a transaction spanning calls. Other native dependencies are not selected. Mobile framework remains undecided: Android Studio emulator is a test environment, not framework approval; affected Mobile runtime work stops BLOCKED_BY_ARCHITECTURE, independent shared authorized work may proceed.

Missing sensitive decision: stop affected work -> smallest question -> Human/Architect -> frozen body/approved ADR -> machine guards -> fresh independent Review/applicable exact-head hosted CI -> product implementation. Task text, allowed_paths, familiarity/popularity/installed tools or passing tests cannot authorize a technology. Go/Java internal variation does not bypass this universal rule.

## Normative effect and compatibility

semantic_change=true: this is a Human-approved architecture clarification, not a representation-only migration. Version remains v1.1; canonical bytes and hash change. Previous canonical SHA25683d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e is preserved in manifest revision history. PDF546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510 remains byte-for-byte unchanged. Older ADRs, checkpoints, PR7/FAIL/Review/Recorder/evidence are immutable. No contract, server schema, ACK/Sync, security or compatibility semantics change. S1 PASS; S2 OPEN.

## Implementation, effectiveness and migration

This bounded prerequisite changes authority, execution governance and existing checker/classifier/CI only, without S2 product code or dependencies. Source/dependency/import/config/workflow/task declaration controls inspect active clients; historical evidence is excluded by exact active path ownership, never deletion. Direct static checks supplement mandatory semantic independent Review of language/dependency authority and Rust responsibility.

New independent Review of clean committed candidate and real applicable exact-head hosted CI must accept this prerequisite before task done or S2 activation. Local/Recorder PASS cannot establish Task/S2 PASS. Acceptance SHA/run/effective point are pending and must be recorded by Coordinator truthfully after acceptance. S4/Java/Loop2 are not advanced. New S2 tasks require fresh TypeScript implementation Review/CI; PR7 cannot be restored or reused as acceptance.

## Rollback

Before acceptance, retain accepted main and repair candidate on FAIL. After acceptance, any authority correction uses a Human-approved corrective ADR and new independently reviewed commit; do not rewrite historical commits/evidence/PDF or silently restore Dart. There is no product/data migration in this prerequisite.

Prompt raw-byte vs Recorder LF-normalized hashes are distinguished in spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/prompt-hash-normalization.md; original approval/recovery and prompt bytes are preserved.
