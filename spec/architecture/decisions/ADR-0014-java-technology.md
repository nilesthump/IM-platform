# ADR-0014: Java profile minimal technology

Status: Human-approved candidate; APPROVED_PENDING_FREEZE. semantic_change=true; v1.1.
Date: 2026-11-13
Task: LOOP1-JAVA-ARCH-001
Approval: spec/progress/evidence/LOOP1-JAVA-ARCH-001/human-approval.txt

## Decision and present need

Canonical §3.2 contains the authoritative approved stack and bounded machine identifiers. Java/Spring was already approved, but §2.3 requires explicit authority for Boot, networking, JDBC driver, serialization and core libraries before S3 product work. Human approved the minimal stack and then BCrypt-only Spring Security Crypto. This does not authorize a security authentication framework, ORM or custom cryptography. JNATS is reserved to the later IM task. No database/contract/password format change is authorized.

Existing Go compatibility evidence: backend/go/core/auth.go passwordMaterial hashes UTF-8 `im-password-v1:` plus password with SHA-256, lower-case hex, then BCrypt; register stores the hash and login verifies it. This inspection motivates the narrow library supplement, not new public contract authority. Future Java acceptance must demonstrate Go-created accounts work on Java and Java-created accounts work on Go against the existing shared schema.

## Scope, compatibility and rollback

One additive authority clause, resolver/manifest linkage, bounded static controls and task recovery records. No product source, contracts, migrations, clients or infrastructure change. Preserve S1/S2 PASS and all historical evidence. Unsupported/dynamic build declarations fail bounded checks rather than claim verified. Semantic Review checks actual dependencies and BCrypt-only use; static checks cannot prove runtime behavior.

New authority requires fresh regular Review and different fresh error review on the final SHA, exact-head hosted acceptance, protected integration, actual-main verification and safe synchronization. Pending candidates do not authorize product activation. Rollback of this authority-only change leaves the accepted Java S0 placeholder and Go product untouched; no data rollback is required.

Previous canonical SHA256: 33b7b2a0a29b555b8c2842383890ae67fc382286b582b4681d2cd78b9f5829ca
