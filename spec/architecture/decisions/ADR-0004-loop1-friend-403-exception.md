# ADR-0004: Loop1 exception for restricted-principal friend403

Status: Human-approved decision; bounded propagation independently accepted at f8d1a287a295ff9f882843f2191cf8c220efeff2 / hostedCI36807927903 (12success, deploypathinactive).
Date:2026-10-01
Approval: exact visible Human instructions "明确loop1不实现403，记录为后续迭代待实现内容" and "保留openapi占位，记为loop1特例".
Evidence:spec/progress/evidence/LOOP1-GO-SOCIAL-001/2026-10-01-loop1-403-exception.md.
PromptP-SOCIAL-403-EXCEPTION-20261001 SHA2566276f3c9d5f2c48a864821755b5f9e2015f3eeb00ed1c845ea3676e91c6ef077.

## Decision

Retain byte-for-byte the OpenAPI PUT /v1/friends/{friendUserId}403AUTHORIZATION_DENIED placeholder and canonical negative fixture friend-add-authorization-denied. Loop1 does not implement this restricted-principal friend authorization403 scenario. It is the single approved exception to Loop1 runtime fixture requirements and must be reported DEFERRED_BY_HUMAN, not PASS, not silently omitted and not a runtime environment skip.

contracts/fixtures/auth-user-friend/loop1-exceptions.json is the machine-readable authority for this stage applicability exception. All other applicable fixture cases remain required under their backend/task stage. Later-iteration TODO FRIEND-AUTHORIZATION-403 remains not implemented/tested/done; activation of a named later iteration must explicitly retire this Loop1-only exception and provide approved credential issuance, permission/ownership semantics and executable denied setup.

## Boundaries and rationale

The independent clean-context report2026-10-01-independent-context-review.md found no approved executable insufficient-scope token or friend-owner authorization model. Human chooses a stage exception rather than inventing a permission system for Loop1. This ADR changes only acceptance applicability, not wire/schema behavior or security mechanism.

Preserve authentication401, self-friend422, other-domain membership/plugin authorization, six-claim JWT and PostgreSQL Session validation. Preserve immediate bidirectional friendship, unique normalized pair/DIRECT and atomic memberships/Sync/Outbox. No fake authorization hook, new scope/DBrole or response reinterpretation is permitted. Do not treat this as a general exemption from every403 or security check.

## Acceptance and compatibility

The future403 response/error/no-effects expectation remains intact for Go/Java. OpenAPI is retained as a placeholder, not evidence of currently supported restricted-principal authorization. Report required-case results and the single deferred case separately. Required-case acceptance may pass without executing this approved deferred case, but a universal all-fixtures-executed statement is false. No SocialTaskPASS or S1GatePASS follows from this decision.

Frozen v1.1 Markdown/manifest/PDF, historical ADRs, goldenfixture1.1/database0001, OpenAPI/error schemas and historical evidence remain immutable. Independent Review and applicable realCI verify exact bounded propagation before Social readiness.

## Bounded acceptance discovery

Fresh independent /root/loop1_exception_review accepted exactf8d1a28 with cleancheckout and exactCI36807927903. Shared report and separate source/archivehashes:spec/progress/evidence/LOOP1-GO-SOCIAL-001/2026-10-01-exception-independent-review.md and exception-transport.json. This discovery binds the prior reviewed decision bytes, not Socialbusiness or S1PASS.
