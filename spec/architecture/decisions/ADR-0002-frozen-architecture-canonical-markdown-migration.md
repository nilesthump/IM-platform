# ADR-0002: Frozen Architecture canonical Markdown representation

Status: Architect-approved for representation-only migration; effective only after independently accepted merge and post-merge verification on `main`.

Date: 2026-09-24

Approved by: Human Architect's explicit `Frozen Architecture Canonical-Source Migration` instruction, registered as Recorder prompt `P-f0a652e5-89aa-4cad-84f2-578b28973d40`.

## Context and motivation

The v1.0 Frozen Architecture is currently the immutable repository PDF `scalable-distributed-im-architecture.pdf`, verified by SHA-256 `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`. Its section 2.1 requires Architect approval before changing frozen authority. Repository-native Markdown improves diffability, reviewability, Agent access, and deterministic text validation.

## Decision

Once this migration task passes fresh independent review, acceptance closure, merge to `main`, and post-merge verification, `spec/architecture/frozen-architecture.md` becomes the single active canonical Frozen Architecture source. Its own actual SHA-256, recorded in `spec/architecture/baseline.md`, becomes the frozen hash target. The former PDF remains at its original path, byte-for-byte unchanged, as an immutable pre-migration historical snapshot. Its original SHA-256 remains in the baseline manifest as provenance, never as the Markdown hash.

This decision changes canonical representation, authority routing, and hash target only. It does not approve any Product Architecture semantic, contract, invariant, ACK, compatibility, security, or implementation change. The future Markdown file remains frozen: subsequent edits still require the existing Architecture Change Proposal/ADR and Architect approval process.

## Impact, compatibility, migration, and rollback

- All future Agent recovery resolves the Markdown from the architecture index and verifies its hash; the PDF is read only for historical provenance or visual comparison.
- Existing historical checkpoints, evidence, and Recorder traces retain their at-the-time PDF facts unchanged.
- Product contracts and implementations remain unchanged. No data, wire, or client migration is required.
- Before the effective point, the PDF remains active authority. If candidate verification or independent review fails, leave `main` unchanged and repair the candidate. If a post-merge defect is found, restore the last accepted authority through an Architect-approved corrective ADR and independently reviewed commit; do not alter the PDF bytes or rewrite history.

## Effective point

The effective commit and UTC time are recorded only after accepted merge and post-merge PASS in the migration manifest/checkpoint. This ADR does not retroactively change prior authority.
