# Independent stage-one Review: local PASS; hosted CI pending

Date: 2026-09-30 (Asia/Shanghai). Reviewer: fresh context /root/stage1_review, created by real Coordinator delegation after implementation and Fix. Reviewer neither implemented nor repaired the candidate. Sole write ownership transferred only after Fix clean handoff; writes are new review evidence/Recorder and current-task handoff only. No product, architecture正文, baseline, verifier or contract was modified by this reviewer.

Reviewed candidate: a09f4fbb1dc497c46c8dc0b8901b0417c534fb2d. Inherited base/diff: 8cd90a7..a09f4fbb1dc497c46c8dc0b8901b0417c534fb2d. Branch: task/LOOP1-ARCH-REMEDIATION. Managed independent checkout: H:/.codex/worktrees/architecture-stage1-review/IM-platform, detached at exact candidate; status --porcelain empty before and after checks. Candidate source worktree: H:/.codex/worktrees/architecture-remediation/IM-platform; no unknown original or Social worktree files read/copied/changed. Clean checkout created through app create_worktree; no manual cleanup/reset/clean.

Recorder: R-20260930T121610Z-80a2186d-1aef-444e-914f-4b9b3341e5b2. Prompt P-9aa0ee17-1d71-483f-b8bf-49431d4b87b2 captures the visible Coordinator delegation, not the entire Human prompt. Startup/read-only whole-document review and managed checkout creation occurred while Fix held write ownership; prospective_resume and incomplete pre-Recorder trace explicitly disclose that timing. Commands after run start route through recorder where possible; some read-only source reads and evidence-write setup remain outside command recorder. Do not represent this as a complete prospective trace.

## Scope and independent conclusions

Read the complete current Frozen Architecture (all chapters 0-21, subsections, both appendices, tables, examples, nine Mermaid graphs/captions, MUST/SHOULD/MAY rules and references), exact canonical diff, resolver/baseline and all three ADRs, Minimality Contract, all current domain/invariant/acceptance inputs, canonical HTTP/WSS/Sync/Plugin policy/readmes and relevant database schema, task/batch/recovery/25-item ledger. Public fixture verifiers independently rerun. All C01-C25 determinate findings are repaired consistently in current正文, not merely deferred to ADR. No substantive unresolved same-authority choice identified in this reviewed scope; review does not prove absence of every possible future defect.

- C01/C09 and SRC-01..07 consistently separate responsibility, physical roles and source ownership across Go/Java. Core owns Auth/session writes and Outbox; Gateway has its needed validation/connection capability. Shared permits primitives and transport support but explicitly forbids full Auth, write transactions, business repository/authorization/Outbox orchestration and service reverse dependencies. No mandatory three-module/three-binary or layered framework added. Root assembly/tests and historical per-backend placeholder scope/exit are explicit. allowed_paths grants no architecture exemption.
- C02/C03/C25 correctly establish one current Markdown authority, actual hash and historical provenance. v1.1 semantic tightening is explicit and separated from ADR-0002 historical representation_only/false; ADR-0001 is expired. No approved historical ADR, public contract or PDF bytes changed.
- C04-C08/C11-C15/C22-C23 align diagrams and examples with existing source-of-truth, transaction/ACK/Outbox, effective Session slots, native/Web differences, least privilege, historical renderers and token/WSS rules. They do not reverse-author product semantics from Go. DB stored event set is not assumed identical to public User Sync wire event set; existing public cursor kinds remain unchanged.
- C10/C16-C21/C24 resolve testing scope, independent review/fix loop, exact-current recovery, stage/Gate/head/job outcomes and current-vs-future scope. Isolated tests cannot replace real TLS entry acceptance; future compatibility/capacity targets cannot claim current delivery. Markdown-only governance triggers are required in正文 but implementation of these triggers remains stage 3.
- No unjustified product abstraction/dependency/infrastructure added. Changes to integrity verification replace historical representation/total-count assertions with chapter-bound structure/semantic relationship checks and negative controls while retaining actual SHA checks. This bounded checker is not a prose theorem prover or product ownership/import checker; independent full review and ordered stage 3 enforcement remain necessary.

I01 is still old Go implementation deviation, not legalized architecture. D01 is still ordered Agent/spec/CI synchronization in stages 2/3. Both remain PENDING downstream; Go structural acceptance, S1 and overall batch PASS are not claimed. All four-stage dependencies and single-current recovery are explicit; old Auth acceptance remains historical under old requirements.

## Exact command evidence

Python: C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe; PowerShell 7 resolved as bundled pwsh. PYTHONIOENCODING=utf-8. Full argv, exit, timing, stdout/stderr blobs in the new run. For commands using --repo independent checkout plus --research-root source worktree/research, command cwd is independent checkout; otherwise absolute verification script paths resolve their own independent root. Commands below are exact argv JSON, not shell paraphrase.

| Command argv | Exit | Elapsed seconds |
| --- | --- | --- |
| ["git", "-C", "H:/.codex/worktrees/architecture-stage1-review/IM-platform", "status", "--porcelain=v1"] | 0 | 0.157 |
| ["pwsh", "-NoProfile", "-File", "H:/.codex/worktrees/architecture-stage1-review/IM-platform/tools/verify-frozen-architecture.ps1", "-BaseCommit", "8cd90a7"] | 0 | 1.344 |
| ["pwsh", "-NoProfile", "-File", "H:/.codex/worktrees/architecture-stage1-review/IM-platform/tools/verify-loop1-ctrl-002.ps1", "-Mode", "Acceptance"] | 0 | 1.718 |
| ["pwsh", "-NoProfile", "-File", "H:/.codex/worktrees/architecture-stage1-review/IM-platform/contracts/http/verify-auth-user-friend.ps1"] | 0 | 6.344 |
| ["C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe", "-B", "H:/.codex/worktrees/architecture-stage1-review/IM-platform/contracts/websocket/verify.py"] | 0 | 0.141 |
| ["C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe", "-B", "H:/.codex/worktrees/architecture-stage1-review/IM-platform/contracts/plugin-api/verify.py"] | 0 | 0.125 |
| ["C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe", "-B", "-m", "unittest", "discover", "-s", "tests/ci", "-v"] | 0 | 2.266 |
| ["C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe", "-B", "spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/verify-transport.py", "--candidate"] | 0 | 8.422 |
| ["C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe", "-B", "H:/.codex/worktrees/architecture-remediation/IM-platform/spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/independent-review-controls.py", "--root", "H:/.codex/worktrees/architecture-stage1-review/IM-platform"] | 0 | 4.672 |
| ["git", "status", "--porcelain=v1"] | 0 | 0.047 |
| ["pwsh", "-NoProfile", "-File", "tools/verify-loop1-ctrl-002.ps1", "-Mode", "Development"] | 0 | 1.75 |

## Results and limitations

- Frozen integrity entrypoint PASS: canonical SHA 83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e, immutable PDF provenance hash, ADR/resolver/history/current semantics, protected no-product diff; 4 test methods including 20 semantic mutations, hash/PDF/provenance negatives and layout control. No skip.
- Additional reviewer-authored controls PASS: five independent chapter-specific negative mutations (second deployment figure, commit/ACK, independent Review path, governance Gate connection, shared reverse-dependency prohibition); exact candidate/clean state/protected product and historical ADR/PDF diff empty.
- CTRL-002 Acceptance PASS: exact Current Task review, five queues, 20 specs, detached checkout clean.
- HTTP PASS: 9 operations, 6 positive/21 negative vectors, 15 mutation regressions. WSS PASS: 8 positive/10 negative scenarios, 18 schema/26 behavior mutations. Sync/Plugin PASS: 79 contract outcome artifacts, 16 mutations. These are contract oracle results, not live Go/Java product parity.
- Existing CI regressions: 21 tests completed with four real OS symlink subcases skipped (WinError 1314). Simulated link checks ran. Hosted Linux CI must supply those real filesystem cases; skipped cases are not presented as executed. Existing CI does not yet enforce new architecture source/import/governance rules (stage 3).
- Transport script and independent 50-blob comparison PASS for persisted working/index/commit/clean checkout fidelity. Two finished original/Fix runs validate; partial usage-interrupted run remains partial. Exactly 49/50 raw event hashes match persisted text. Original C-3e0d003f-8661-4322-811e-7a14054a219e.stderr.txt has 60 UTF-8 replacement characters, persisted SHA 62b9875b8941f1e4ef1c891d9982191906e7658f8e2817178feb24286bc5bdfe versus raw event SHA 5acd8d8026f3fdb50f35b54c77376e4f3794c69d716a13755be080692d26cb74. Raw subprocess bytes unavailable. validate-run checks event structure/chain, not blob hashes. Historical records were not edited to conceal it. Original traces cannot independently prove raw stdout/stderr identity; current acceptance commands were freshly rerun in this independent run.
- No live Go build/race/PostgreSQL/NATS/Compose/TLS/product integration performed or claimed in architecture-only stage 1. They remain mandatory stage 4. No hosted remediation CI performed by Reviewer; Coordinator must push reviewed closure normally to authorized task branch and verify applicable exact-head job outcomes. No done/Stage Gate transition permitted on this local report alone.
- Outside-recorder setup had one PowerShell/python quoting SyntaxError before any write and one unsupported event type attempt (no event appended); both corrected. Read-only attempted wildcard/missing explanatory file reads failed and had no writes. These facts are disclosed, not manufactured into complete earlier command trace.

## Handoff

Local independent Review PASS of bounded stage-one candidate. Keep LOOP1-ARCH-REMEDIATION-001 in review, stages 2-4 backlog; batch and S1 Gate NOT PASSED. Current last-known-good product remains historical Auth 59d92f39234596a5b66841e8aa2ef7db0bf65e8a; remediation candidate is not yet accepted.

Next exact action: Coordinator inspect clean review closure, use ordinary non-force push to task/LOOP1-ARCH-REMEDIATION, collect applicable fresh hosted CI with precise head/jobs and durable evidence; close stage 1 only when accepted. Then activate dependency-satisfied stage 2 with fresh Implementation Agent. Before stage 3 exists, hosted green cannot be represented as Go source/import compliance.

Reviewer owns only this new run/evidence/001 handoff/current updates until commit; after clean committed handoff Coordinator receives sole write ownership. No architecture implementation was fixed by Reviewer; a future substantive failure must use a fresh Fix then new fresh Review context.

Handoff-only Recovery Development rerun passed after evidence/current updates; it is explicitly non-acceptance and does not replace clean candidate Acceptance. Recorder finalization/validation result is recorded in summary and final closure handoff.

Review Recorder finished PASS and validate-run exit 0: 27 events. This is Recorder structural validity, not hosted Task acceptance.
