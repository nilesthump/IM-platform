# Frozen Architecture Baseline Manifest

- baseline_title: 面向十万级在线连接的可扩展分布式即时通信平台
- version: `v1.1`
- status: Human-approved client clarification candidate; independent Review and hosted CI pending
- canonical_format: `markdown`
- repository_path: `spec/architecture/frozen-architecture.md`
- sha256: `aa2398020beeda5f7f9456aac346da57bd8b75212192123c943c35dfdc80f84c`
- previous_canonical_format: `pdf`
- previous_repository_path: `scalable-distributed-im-architecture.pdf`
- previous_sha256: `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`
- historical_migration_type: `representation_only`
- historical_semantic_change: `false`
- historical_migration_task_id: `LOOP1-ARCHDOC-001`
- historical_markdown_sha256: `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91`
- revision_type: `human_approved_client_clarification`
- semantic_change: `true`
- revision_task_id: `LOOP1-CLIENT-ARCH-CLARIFICATION-001`
- revision_adr: `spec/architecture/decisions/ADR-0005-client-technology-clarification.md`
- approval_source: `spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/approval-and-recovery.md`
- baseline_date: 2026-10-01

## Historical ADR-0003 acceptance discovery

At that prior revision, the Markdown was the single canonical source under the explicitly approved revision. Stage-one bounded acceptance: fresh Review of a09f4fbb1dc497c46c8dc0b8901b0417c534fb2d and hosted run 36714913796 on exact head 3e6e89fa2b378f1fcb4c944466fef2e3bc905379, all ten jobs successful; evidence spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/hosted-acceptance.md. This does not accept pending stages two through four, source compliance or remediation/S1 Gate. This revision tightens executable source ownership and governance semantics; it is NOT the historical representation-only migration. ADR-0002 and its original v1.0 migration facts are immutable history. The PDF remains the byte-for-byte immutable historical snapshot and is not a second current authority. No public wire, database, ACK/Sync, compatibility or security boundary is changed.

## Current completion discovery (2026-10-01)

The preceding stage-one paragraph is its bounded historical acceptance point. Subsequent task/product acceptance is now recorded in evidence004/final-hosted-acceptance.md (d0ae52f / hosted36744072690). Administrative finalization requires a new independent Review and exact-head hosted run. Version, hashes, approval and historical source metadata remain unchanged; S1 product Gate OPEN.

## Current Human-approved clarification (2026-10-01)

- previous_revision_sha256: `83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e`
- previous_revision_type: `conflict_resolution`
- previous_revision_task_id: `LOOP1-ARCH-REMEDIATION-001`
- previous_revision_adr: `spec/architecture/decisions/ADR-0003-architecture-conflict-resolution.md`
- previous_revision_approval_source: `spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/approval-and-recovery.md`

All preceding acceptance paragraphs are historical bounded discovery, not acceptance of these changed bytes. Version remains v1.1; canonical bytes/hash changed under ADR-0005. Original PDF, representation-only migration and ADR-0003 facts remain historical unchanged. S1 now PASS through accepted E2E/pre-PR7 tree restored by PR8; S2 OPEN. This clarification candidate requires NEW independent Review and exact-head hosted CI before effectiveness/product implementation. No public contract or product source change.

Supplemental Human Desktop decision freezes Tauri + SQLx(SQLite) atomic native transaction adapter; separate tauri-plugin-sql execute calls cannot emulate transaction. Mobile is Android Kotlin + Jetpack Compose, validated on Android Studio emulator; Mobile TS/TBD is superseded before candidate acceptance. Approval supplement: spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/human-desktop-sqlx-mobile-emulator-decision.txt.

- superseded_preacceptance_candidate_sha256: `ac0421074c41589d1d409cc91729953984839aea3c05e805608fcf7677da4f68`
- mobile_approval_source: `spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/human-mobile-kotlin-compose-decision.txt`

Candidate188d24a5a53abaa136aa939fded5968dd5fe728f was never accepted. New Human Mobile decision supersedes its TS/TBD clause before Review/CI. Previous accepted revision remains83d124b, not the superseded candidate hash. Android Kotlin/Compose same-contract behavior leaves Web/Desktop/shared TypeScript and Desktop SQLx boundaries unchanged.
