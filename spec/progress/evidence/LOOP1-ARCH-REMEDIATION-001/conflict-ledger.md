# Whole-document audit coverage and conflict ledger

Scope: actual canonical frozen-architecture.md v1.0 at inherited 8cd90a7, all chapters 0-21, every subsection, both appendices, tables, code/tree examples, all nine Mermaid diagrams/captions, MUST/MUST NOT/SHOULD/MAY language and references. The full file was read in successive non-overlapping slices, not only searched for directory examples. Original document SHA ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91. Current version/hash are in the baseline manifest.

Compared against both approved historical ADRs, baseline/resolver, Minimality Contract, all current domain/invariant/acceptance documents, canonical HTTP/WSS/database/Sync/plugin schema and policy/readmes, actual Agent/handoff/current/task template/Auth done task and S1 batch, plus existing architecture verifier. Canonical machine rules and fixture verifiers are rerun; no contract or fixture bytes changed.

## Coverage (including areas with no determinate defect)

| Area | Inspection and outcome |
| --- | --- |
| status/front matter/TOC | Current vs original date/version and PDF provenance, normative keywords, authority link; C03/C25. Retain chapter and appendix anchors. |
| §0 summary, diagram, scope table | C03/C04; 100k future vs current 5k consistent, no capacity rewrite. |
| §1.1-1.3 goals/non-goals | Correctness vs capacity, 12-week budget, Loop2/N+1/Redis/Kafka scope consistent; no speculative change. |
| §2 F-01..F-10 and 2.1/2.2 | C03 and bounded approval/current-body process. No contract/security authority reversal. |
| §3 figure and 3.1-3.3 | C04/C08/C09/C10; independent roles do not force module/binary duplication. |
| §4 figure and 4.1-4.4 | C06/C07. Friend/direct atomicity and normalized pair, group idempotency, three distinct message identities consistent with canonical schema. Client conversation/request and server sender/conversation/request keys serve different roles; NOT treated as a conflict or changed. |
| §5 figure and 5.1-5.3 | C05; commit/Outbox sequence, duplicate publication, Sync recovery, one logical group message consistent. No ACK/reliability redesign. |
| §6 figure and 6.1-6.4 | C11. FAILED/SENT terminality, same-transaction cursor, account SQLite, user-vs-conversation cursor and realtime crossing consistent; no cursor change. |
| §7.1-7.4 | C12/C13; cookie/native token storage, logout/local-history distinction, TLS unchanged. |
| §8.1-8.3 package example/API table | C08 context; exact host bridge/default-deny/capability permissions and immutable renderer hashes consistent with policy. Package-tree indent cosmetic only, not false normative conflict. |
| §9 figure and 9.1-9.4 | C14/C15; install/upgrade snapshot/old service/backend-renderer atomicity/Echo/Poll unchanged. |
| §10 tree and 10.1 | C01/C02; source and support exceptions require actual explicit rules. Control-plane directory responsibilities retained. |
| §11.1-11.4 | C01; contract uniqueness/equivalence/golden vectors/migration component and expand-contract consistent. Go reference does not authorize Java inheriting illegal Go layout. |
| §12 figure and 12.1-12.3 | C01/C16/C17; allowed_paths not exemption, current task branch/serial migration bounded. |
| §13.1-13.3 | C18; handoff/checkpoint facts retained, current history moved out of recovery presentation but historical Git and evidence unchanged. |
| §14 figure and 14.1-14.4 | C19/C20/C21; compatibility scope retained, independent CI and fresh Review both required. |
| §15 diagram/table/execution policy | Seven stage progression gates and milestone-not-calendar consistent; stage delivery is distinct from overall batch/product Gate. No scope acceleration. |
| §16.1-16.4 | 8C/16GB/3TB, five authenticated stages, real TLS, per-profile reports and zero correctness redlines consistent. Soak/SLO concrete values delegated to future acceptance, not invented here and not current Auth acceptance criteria. |
| §17.1-17.5 | Immutable promotion, version windows, migration/rollback/forward-fix and incident criteria consistent. No release or destructive action authorized by audit. |
| §18.1-18.4 | C22/C23. Readiness/degraded/liveness and alert levels are future full-platform rules, not claim of present implementation. |
| §19 table | C24; task plan not actual status. Old done historical tasks not rewritten. |
| §20/20.1 | Dependencies and Java parity scope consistent; C24 interpretation. Java Sync after S2 does not require premature Go/Java business now. |
| §21.1-21.3 | Fresh independent Review clarified; existing stop conditions and empty-repo bootstrap remain conditional examples. |
| appendix A | Existing stage goals retained; applicable architecture/dependency/final head CI evidence added to general checklist. |
| appendix B | C03/C20 summarized consistently; other invariant summaries unchanged. |

No unresolved equal-authority substantive architecture choice was found in this audit scope. This is an implementation audit conclusion pending independent Review, not self-acceptance. Future implementation or review can identify additional issues. No claim that every possible defect is mechanically proved absent.

## Findings

All C findings below are repaired in the current body/manifest/checker candidate; independent Review is PENDING for each. I01 remains an explicit implementation deviation for stage 4, and D01 remains ordered downstream work for stages 2/3; neither is hidden or accepted as a permanent exception. Exact locations use stable actual sections/rule identifiers rather than line numbers that move during revision.

### C01

- Locations / conflicting rules: §3.1, §10 tree, §11.2 versus §12.1 root internal/message,outbox.
- Category: Internal conflict / example ambiguity.
- Impact: Go/Java ownership; future task generation.
- Authority: F-05 and §3.1 service responsibilities; explicit Human source-boundary instruction.
- Resolution: §10 SRC-01..07, §11 constrained internal variation, Core task paths; root assembly/tests/build and shared support enumerate limits.
- Normative semantic change: yes: executable ownership tightened.
- Downstream: Agent/spec tasks (stage 2), source/import checker (3), Go migration (4).
- Verification: §10/§12 structural mutation; independent source-boundary review.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C02

- Locations / conflicting rules: §10 overview.md/service-boundaries.md versus ADR-0002 resolver/canonical source.
- Category: Approved ADR not reflected.
- Impact: all Agents discover competing authority.
- Authority: ADR-0002 and current architecture README/baseline.
- Resolution: tree names actual resolver, baseline and sole frozen Markdown.
- Normative semantic change: no product change.
- Downstream: stage 2 references.
- Verification: unique canonical artifact check.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C03

- Locations / conflicting rules: §2.2 omits current frozen body; §0/appendix B unqualified sole contracts authority.
- Category: Cross-document authority ambiguity.
- Impact: all Agent and contract interpretation.
- Authority: AGENTS authority order, ADR-0002, §11.1.
- Resolution: rank body plus approved ADR first; contracts sole machine-verifiable public source, no reverse-authoring.
- Normative semantic change: governance clarification.
- Downstream: Agent/handoff/review (2).
- Verification: resolver and independent prose review.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C04

- Locations / conflicting rules: §0/§3 diagrams NATS->PG versus F-03, §5.1/.2.
- Category: Internal diagram conflict; historical representation artifact.
- Impact: runtime/deployment interpretation; verifier.
- Authority: Core transactional persistence and Outbox/NATS/Gateway existing rules.
- Resolution: replace arrow with NATS->Gateway, retain PDF unchanged and explain historical arrow.
- Normative semantic change: no product semantics change.
- Downstream: integrity verifier (1).
- Verification: both chapter-bound directed edge negatives.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C05

- Locations / conflicting rules: §5 figure Gateway membership, Core->Sender ACK, Bus->Receiver versus F-05/§5.1/.2.
- Category: Internal diagram conflict.
- Impact: Gateway/Core security responsibility and ACK delivery.
- Authority: contracts/websocket README; MSG-D-004/007, MSG-I-002/006.
- Resolution: Core authorizes; commit precedes Core->Gateway->Sender; dispatcher and Gateway fanout explicit.
- Normative semantic change: no product semantics change.
- Downstream: source migration/review (4).
- Verification: membership, early ACK, direct ACK and fanout negative controls.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C06

- Locations / conflicting rules: §4 figure 1:1+ Message/Outbox versus §5.3, MSG-I-003, DB logical-event uniqueness.
- Category: Internal diagram conflict.
- Impact: message reliability / future implementations.
- Authority: one logical message.created Outbox per Message; retries are deliveries.
- Resolution: diagram states one logical message.created, not one publication attempt.
- Normative semantic change: no product semantics change.
- Downstream: none beyond reviewer.
- Verification: cardinality mutation.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C07

- Locations / conflicting rules: §4 User 0..3 diagram/UNIQUE shorthand versus §4.1 valid slots and contracts/database slot rows.
- Category: Example ambiguity.
- Impact: Session validation and DB interpretation.
- Authority: contracts/database README/0001 schema; AUF-D-001..004.
- Resolution: label active slots, describe current one row per slot and rotation; do not create history design.
- Normative semantic change: no DB change.
- Downstream: none.
- Verification: slot negative control and contract verification.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C08

- Locations / conflicting rules: §3.1 plugin-host blanket DB/file/network ban versus §8 controlled Host bridge and plugin_kv.
- Category: Subject ambiguity.
- Impact: plugin host versus untrusted WASM security.
- Authority: F-08, §8.1/.3, plugin policy/default-deny resources.
- Resolution: ban untrusted WASM direct access and Core authorization bypass, describe controlled bridge without granting new capability.
- Normative semantic change: no security boundary change.
- Downstream: future plugin task inputs (2).
- Verification: independent review against policy-v1.json.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C09

- Locations / conflicting rules: §3.2/§3.3 internal variation and optional processes versus three physical deployment units.
- Category: Normative gap.
- Impact: Go/Java deployment and build choices.
- Authority: §3.1, existing separate roles, Human prohibition of mandatory three modules/binaries.
- Resolution: independently startable roles may reuse one artifact; service boundary retained.
- Normative semantic change: clarification, no required new infrastructure.
- Downstream: stage 2 tasks, stage 4 role smoke.
- Verification: independent review; role smoke stage4.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C10

- Locations / conflicting rules: §3.3 all test traffic through TLS versus unit/isolated integration §14.
- Category: Scope ambiguity.
- Impact: testing and false acceptance.
- Authority: §16 and S1 E2E actual entry; §14 test layers.
- Resolution: scope real entry to deployment/E2E/load/release, isolated tests cannot substitute.
- Normative semantic change: no acceptance weakening.
- Downstream: acceptance/checklists (2/3).
- Verification: review stage-specific verification.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C11

- Locations / conflicting rules: §6.2 unconditional SQLite sequence versus §6.1 Web memory only.
- Category: Example applicability ambiguity.
- Impact: client parity.
- Authority: F-07; SP-D-001..006.
- Resolution: limit persistent sequence to Desktop/Mobile; Web memory convergence.
- Normative semantic change: no client semantics change.
- Downstream: future client tasks (2).
- Verification: independent whole-section review.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C12

- Locations / conflicting rules: §7.1 /auth/login and snake_case example versus canonical /v1/auth/login/camelCase wire.
- Category: Cross-document example ambiguity.
- Impact: HTTP client/SDK implementation.
- Authority: contracts/http/auth-user-friend.openapi.json and §11.1.
- Resolution: point to canonical path/fields; classify snake_case as domain names.
- Normative semantic change: no wire change.
- Downstream: none.
- Verification: HTTP verifier; independent canonical comparison.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C13

- Locations / conflicting rules: §7.3 eventually cannot reconnect versus AUF-I-002 and WSS authoritative bind.
- Category: Temporal ambiguity.
- Impact: stale-token auth and Gateway/Core coupling.
- Authority: §4.1/.7.2 and canonical WSS authority check.
- Resolution: require each new bind/reconnect authoritative ID+epoch; Gateway validates, Core owns all Auth writes/outbox.
- Normative semantic change: no auth behavior change; ownership clarified.
- Downstream: stage 2 rules, phase4 interface migration.
- Verification: WSS contract verifier; live integration later.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C14

- Locations / conflicting rules: §9 single Artifact->Instance lifecycle chain versus caption/§9.1/.2 and SP-I-009.
- Category: Internal diagram conflict.
- Impact: plugin lifecycle state modelling.
- Authority: artifact immutable identity and separate Conversation instance.
- Resolution: separate subgraphs with prerequisite edge, preserve lifecycle requirements.
- Normative semantic change: no lifecycle contract change.
- Downstream: future plugin task source (2).
- Verification: separate state-machine negative control.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C15

- Locations / conflicting rules: §9 purge deletion versus §8.2 historical renderer retention.
- Category: Scope ambiguity.
- Impact: historical plugin rendering.
- Authority: SP-D-010, SP-I-010, canonical purge requirements.
- Resolution: purge cannot remove renderer still required by history.
- Normative semantic change: no new retention policy.
- Downstream: future plugin acceptance (2).
- Verification: independent policy and history review.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C16

- Locations / conflicting rules: §12 diagram review/failure->complete->handoff versus independent governance.
- Category: Internal workflow conflict.
- Impact: review independence/recovery.
- Authority: AGENTS batch protocol; Human fresh contexts.
- Resolution: fresh Implementation/Fix/Review, FAIL returns Test+new Review, PASS proceeds applicable CI.
- Normative semantic change: yes: executable independence clarified.
- Downstream: Agent/review checklists (2), CI (3).
- Verification: review/CI failure shortcut mutations.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C17

- Locations / conflicting rules: §12 done unconditional CI wording omits ADR-0001 bounded bootstrap and expiration.
- Category: Approved ADR not reflected.
- Impact: historical acceptance interpretation.
- Authority: ADR-0001; CI task done.
- Resolution: state exact temporary condition and current expiration; no reuse.
- Normative semantic change: no current waiver.
- Downstream: stage2 governance.
- Verification: expiration check and independent ADR review.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C18

- Locations / conflicting rules: §13 active empty -> ready first and active-task recovery versus exact current task governance.
- Category: Cross-document conflict.
- Impact: task skipping and lost review.
- Authority: AGENTS mandatory startup; Human exact current.
- Resolution: unique exact ID across queues, resume real state, dependency-driven next selection.
- Normative semantic change: yes: enforce existing recovery.
- Downstream: current fixed now; entry/template sync2.
- Verification: recovery shortcut mutation and CTRL-002.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C19

- Locations / conflicting rules: §14 serial classifier diagram and only public contract expansion versus table shared SDK/DB.
- Category: Internal graph/caption conflict.
- Impact: CI missing or overtriggered jobs.
- Authority: §14.1 existing path matrix.
- Resolution: independent Go/Java/shared classification, shared trigger semantics retained.
- Normative semantic change: no compatibility requirement change.
- Downstream: classifier/workflow stage3.
- Verification: independent branch graph check.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C20

- Locations / conflicting rules: §14 lacks architecture/Agent/template/checker triggers and required-job outcomes.
- Category: Normative gap.
- Impact: Markdown skips and false CI Gate.
- Authority: F-10; Human CI requirements.
- Resolution: governance branch to structural Gate; explicit missing/skip/fail/cancel and head SHA checks.
- Normative semantic change: yes: executable enforcement tightened.
- Downstream: phase3 checks and negatives.
- Verification: disconnected trigger/Gate negative controls; real workflow tests phase3.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C21

- Locations / conflicting rules: §14.3 v1/v2/HEAD immediate matrix versus current v1 skeleton/stage5.
- Category: Stage scope ambiguity.
- Impact: premature fake versions/false parity.
- Authority: §15 stage gates; existing canonical v1 only.
- Resolution: future complete matrix remains required; early exact fixture/placeholders cannot claim complete acceptance.
- Normative semantic change: no compatibility change.
- Downstream: phase2 task/acceptance, phase3 stage-aware checks.
- Verification: independent stage review.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C22

- Locations / conflicting rules: §18.1 token default not collected versus §7.4 absolute prohibition.
- Category: Internal normative conflict.
- Impact: secret exposure.
- Authority: AUF-I-007, §7.4, canonical HTTP/WSS.
- Resolution: token prohibited in logs/trace, message body default unchanged.
- Normative semantic change: no security change.
- Downstream: review checklist (2).
- Verification: token-prohibition mutation.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C23

- Locations / conflicting rules: §18.3 pre-auth auth.bind/ping versus §7.2 ping/pong.
- Category: Internal omission.
- Impact: WSS implementer interpretation.
- Authority: AUF-I-003, canonical WSS.
- Resolution: include pong.
- Normative semantic change: no wire change.
- Downstream: none.
- Verification: WSS verifier.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C24

- Locations / conflicting rules: §19 list ordering / §20 task text versus actual dependency/queue state.
- Category: Example ambiguity.
- Impact: resumption and stage progression.
- Authority: AGENTS dependency satisfaction; §12 ready conditions.
- Resolution: list is planning not current queues; do not choose by filename/table order.
- Normative semantic change: no business scope change.
- Downstream: phase2 batch/task references.
- Verification: CTRL-002 and independent dependency review.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### C25

- Locations / conflicting rules: baseline migration_type=representation_only and verifier historical arrow/figure counts versus authorized current semantic tightening.
- Category: Historical representation binding conflict.
- Impact: all revisions and integrity CI.
- Authority: ADR-0002 unchanged historical scope; Human new revision approval.
- Resolution: separate historical metadata/hashes and current semantic_change=true; actual hash plus graph/flow structure and negative controls.
- Normative semantic change: yes current revision, old migration unchanged.
- Downstream: phase3 invoke and trigger integrity checker.
- Verification: actual hash/PDF/semantic mutation tests; full structure negative suite.
- Status / independent review: REPAIRED IN CANDIDATE; independent Review PENDING.

### I01

- Locations / conflicting rules: backend/go root auth.go/gateway.go/outbox.go versus clear §3 responsibilities.
- Category: Implementation deviation ONLY.
- Impact: Go package and Gateway full auth coupling.
- Authority: §3 F-05; SRC rules clarify already required responsibility.
- Resolution: do not legalize existing code; defer actual migration to ordered stage4 after effective checks.
- Normative semantic change: no architecture accommodation.
- Downstream: phase3 expose original violations; phase4 migration.
- Verification: future Go source/import negative fixture and final live regression.
- Status / independent review: REGISTERED; ordered downstream stage pending; independent Review PENDING.

### D01

- Locations / conflicting rules: AGENTS/handoff/template/backlog tasks/LOOP1-S1 and CI do not yet cite current SRC rules.
- Category: Downstream synchronization work.
- Impact: new Agents/Java source tasks/review.
- Authority: stage1 current body and explicit four-stage sequence.
- Resolution: register for stage2 then stage3; no product compliance claim.
- Normative semantic change: downstream only.
- Downstream: phase2 named paths; phase3 tests.
- Verification: new Agent recovery review and effective checker tests.
- Status / independent review: REGISTERED; ordered downstream stage pending; independent Review PENDING.


## Fresh independent Review 2026-09-30

Reviewer /root/stage1_review independently read full body/diff and authority inputs, accepted C01-C25 locally at a09f4fbb1dc497c46c8dc0b8901b0417c534fb2d. This append records current review without rewriting the candidate findings or their original pending facts. Each C finding: independent local Review PASS; hosted CI acceptance PENDING. I01/D01: downstream stages pending, not waived. Exact commands/negative controls/limitations: independent-review-pass.md; new Recorder R-20260930T121610Z-80a2186d-1aef-444e-914f-4b9b3341e5b2.
