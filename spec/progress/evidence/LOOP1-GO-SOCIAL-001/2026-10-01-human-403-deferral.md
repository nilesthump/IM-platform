# Human decision: defer friend403 beyond Loop1

Date:2026-10-01. Exact visible Human instruction:
明确loop1不实现403，记录为后续迭代待实现内容

## Decision and future work

In the preceding friend-add-authorization-denied discussion, Loop1 does not implement restricted-principal403AUTHORIZATION_DENIED for PUT /v1/friends/{friendUserId}. Record it as later-iteration TODO, not implemented, not tested and notPASS.

Deferred item: FRIEND-AUTHORIZATION-403.
Status: DEFERRED_BY_HUMAN; target iteration later than Loop1, exact iteration unassigned.
Future prerequisites: approved restricted credential issuance and server-side friend permission/ownership policy; exact denied setup; explicit public-contract applicability synchronization; fresh implementation/independentReview/realCI.
Future acceptance: preserved canonical403AUTHORIZATION_DENIED response, no friendship/DIRECT/membership/Sync/Outbox effects, applicable Go/Java equivalence, preserve401 and422 distinctions.
Existing user/session fields remain unchanged; no scope/role/permissionhook invented. Other-domain membership/plugin authorization is not waived by this scoped record.

## Current propagation limit

This file records Human scope intent and a future obligation only. The original negative fixture, OpenAPI403, canonical schemas, frozen architecture, ADRs and acceptance files are untouched. Universal machine-verifiable fixture applicability is therefore not yet reconciled; do not claim full canonicalfixturePASS or ready/active solely from this record.

Automatic approval review rejected the broader proposed OpenAPI/ADR/machine applicability amendment, stating that the latest instruction authorized recording deferral but did not explicitly authorize public-contract/architecture changes, and a smaller recording-only alternative exists. The rejected script made no filesystem edits. This safe alternative changes only current Social Task/current/evidence/checkpoint within its existing allowed_paths.

Concrete minimal pending synchronization proposal, for explicit approval:
- Add a canonical Loop1 applicability declaration for only friend-add-authorization-denied, reporting DEFERRED notPASS; keep its future403 expected payload/no-effects fixture intact.
- Add friendPUT403 stage metadata and approved decision/acceptance applicability reference.
- Bind later-iteration todo; retain all other Loop1 cases,401/422, DB/JWT/security and transaction requirements.
No product change, fixture deletion or response reinterpretation proposed. No contract changes were carried out.

## Verification and research

Base clean handoffbc737a07213ffa2409164ca03dcb4dace98e0c3e verified AcceptancePASS before recording.
Research exact Human promptP-SOCIAL-403-DEFERRAL-20261001 SHA5b2b612cd35175df5882f9a10bc54790abf31beb3c38eef1b31f4f9c23df581b. Startup/directreads and failed stdinbase64/start wrapper attempts preceded successful prospective_resume and remain exposed; no incomplete trace called complete. Candidate checks/run history are external Recorder evidence, not product acceptance.
