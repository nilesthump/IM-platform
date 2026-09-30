# ADR-0003: Whole-document architecture conflict resolution and executable service boundaries

Status: Human-approved bounded conflict resolution; canonical revision and downstream product remediation independently accepted; administrative finalization pending.
Date: 2026-09-30
Approval source: spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/approval-and-recovery.md; visible Human four-stage instruction and registered prompt P-ddf5a00c-27a1-412c-ad9b-2305e1aad734 (delegation plus exact approval excerpt, not complete Human prompt).

## Motivation and authority

Frozen v1.0 §3 assigns Gateway/Core/plugin-host responsibilities while §12 exemplifies root internal business packages and §11 allows unspecified internal variation. The historical Markdown migration retained diagram arrows and workflow expressions that conflict with operative invariants and current approved governance. Audit coverage and individual determinate resolutions are in the task conflict ledger. This approval is NOT approval for arbitrary product redesign or any changed public contract, database, ACK/Sync, compatibility or security boundary.

## Decision

Revise the current canonical body to v1.1, not merely append this ADR. §§3/10/11/12 now enforce shared service ownership and dependency direction across Go/Java with language-specific internal structures. Root assembly/build/testing exceptions and minimal shared support are explicit; complete Auth/session-write business cannot be shared into Gateway. No three-module/three-binary/multi-layer requirement is created. S0 exceptions are per backend and expire at first business implementation.

Correct diagrams and examples to existing current semantics: Core persistence and membership decisions, Outbox-to-NATS-to-Gateway, post-commit Gateway ACK forwarding, single logical message-created Outbox, effective Session slots, separate plugin artifact/instance states. Clarify native SQLite versus Web, token prohibition, current-versus-future stage scope, precise current-task recovery, fresh independent Review/fix loops, real CI head/job acceptance and stage-appropriate checks. Concrete wire/schema authority remains contracts/.

## Normative effect and baseline

semantic_change=true: source-boundary and governance ambiguity is tightened into executable rules. Existing product invariants are restated without changing their meaning. The v1.0 PDF-to-Markdown migration remains historical representation_only/semantic_change=false under ADR-0002. Its PDF and historical Markdown hashes remain recorded separately from the actual current Markdown SHA. Historical ADRs, reviews, checkpoints and Recorder evidence are never rewritten.

## Migration and validation

Four sequential tasks repair authority, execution constraints, effective checkers/CI, then Go implementation. Stage-one verifier preserves hash checks and replaces historical arrow/figure/format counts with section-bound graph/structure checks and negative controls. Stage three supplies product ownership/import/trigger tests; until stage four repairs old Go violations those are expected failures, never a permanent exception or product PASS. Java remains stage-appropriate and its future business boundaries are tested with fixtures.

Each bounded stage needs new independent Review and applicable CI. Final batch acceptance requires final candidate exact-head hosted CI, all applicable live regressions, no unresolved blocker and recovery checkpoint. Historical Auth acceptance remains valid for its old requirements. Rollback of this candidate is a new corrective commit/approved decision; do not rewrite historical source/evidence or discard Auth implementation. No data migration or public-wire migration is needed.

## Actual bounded acceptance point

Fresh stage-one Review accepted a09f4fbb1dc497c46c8dc0b8901b0417c534fb2d. Hosted run 36714913796 accepted exact head 3e6e89fa2b378f1fcb4c944466fef2e3bc905379, all ten jobs successful; evidence spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/hosted-acceptance.md and task001 done. This discovery update preserves decision/approval/history. Stages002-004 and product/batch/S1 acceptance remain outstanding.

## Current completion discovery (2026-10-01)

The preceding bounded acceptance paragraph records the stage-one historical point, not current pending work. Tasks001-003 are done; Task004 remainsreview with accepted product candidate d0ae52f5615320790ae7039cb48831873de6f486 / hosted36744072690 with fresh independent revocation Review. See evidence004/final-hosted-acceptance.md and conflict-closure-supplement.md. This administrative candidate requires new independent Review and exact-head hosted verification before final batch closure. Canonical v1.1 semantics/hash/approval, historical migrations and PDF remain unchanged; S1 product Gate OPEN.
