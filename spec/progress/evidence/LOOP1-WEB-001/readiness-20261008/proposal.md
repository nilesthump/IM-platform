# Web minimal prerequisite proposal

Status: PROPOSED_NOT_APPROVED / BLOCKED_BY_ARCHITECTURE. Task: LOOP1-WEB-001. Human visible request on 2026-10-08: 执行下一个task. This authorizes selecting the next dependency-satisfied Task; it does not select a new storage technology or expand task paths.

## Verified selection and current authority

GUI is uniquely done and independently accepted/integrated/synchronized at actual main 6a6e97e6b7d5e19d8607c6800877187e70b4bd36. Original final-sync report, binding and receipt are preserved byte-exact here. Approved ADR-0007 order places Web next. Accepted UI/planning/native decisions and GUI-only completion do not authorize a Web appearance storage mechanism. Main's 31 unrelated status entries / 781 protected files remain untouched. Assigned managed worktree H:/.codex/worktrees/w/IM-platform is exact-root verified and starts at accepted main.

## Present blockers

1. Canonical section 19 explicitly requires a decision before implementing an unfrozen appearance storage mechanism. Section 6.5 / ADR-0006 permits host state with React useState/useReducer/Context, while frozen client-ui/design-direction.md requires typography/density retention after restart and explicitly leaves Web storage for a later bounded decision. React state can retain values during page navigation but cannot supply page-restart persistence. ADR-0009 authorizes only Desktop app_data JSON and Android SharedPreferences. No accepted Web localStorage/IndexedDB/storage library decision exists. ci/check_architecture.py currently rejects all Web localStorage/indexedDB/SQLite identifiers in non-Markdown source (line 477). This rule remains effective; do not weaken it before accepted authority.
2. .github/workflows/ci.yml lines 188 and 356 still invoke ci/check_s0_boundary.py web. The current Web job only checks an empty skeleton and the compatibility job repeats it. The guard rejects every product file. tests/ci/test_s0_boundary.py line 97 requires exactly two old Web calls. None of those workflow/guard/test paths is in this Web Task's allowed_paths. A product cannot pass applicable real CI without a specifically approved scope change.

## Smallest concrete decision requested

Approve browser-native localStorage only for one host-owned versioned appearance record containing exactly theme (Cold AI or Warm Creative), font size and density. Proposed sole product adapter path: clients/web/src/ui/appearance.ts. Validate allowed values and bounded size; invalid/unavailable storage falls back to in-memory defaults without clearing unrelated origin keys. Theme changes preserve font size/density. Store no messages, history, users, sessions, access/refresh credentials, API endpoint, conversation state or sync cursors. Retain Web message/domain state in memory only, no SQLite/IndexedDB/offline history. No new third-party dependency, router/state/data framework or browser/native bridge is proposed.

Before product implementation, freeze this precise selection in a new proposed ADR-0011-web-appearance-storage.md and a narrow canonical section 6.5 clause, update only the corresponding baseline hash/discovery fields, and independently accept the freeze. The proposal is not approved authority and is not an implementation of the storage adapter.

Approve only these seven additional prerequisite/acceptance paths beyond the current Web Task scope:

- spec/architecture/frozen-architecture.md: the bounded Web appearance clause and machine policy only.
- spec/architecture/baseline.md: exact canonical digest and Web decision discovery only.
- spec/architecture/decisions/ADR-0011-web-appearance-storage.md: this named decision, authorization, limits, migration/rollback and acceptance.
- ci/check_architecture.py: authority-bound exact appearance-adapter exception; retain bans elsewhere and on chat/token/history persistence.
- tests/architecture/test_client_technology.py: positive approved appearance control plus negative authority/path/data/history controls.
- .github/workflows/ci.yml: replace the Web job and compatibility Web skeleton calls with actual Web build/behavior/source verification; preserve job selection/gate/protection and all other jobs.
- tests/ci/test_s0_boundary.py: verify the Web product commands and retained source/gate controls instead of requiring obsolete skeleton calls; preserve other backend/client controls.

No source permissions outside current Web paths are proposed. Existing React 18.3.1 / TypeScript build approach can copy locally locked approved UMD distributions and static assets as Desktop already does; no new bundler is necessary. Browser transport must use canonical WEB cookie refresh/auth metadata and default HTTPS/WSS, with access credentials only in memory/auth.bind, same-origin serving and no new backend/CORS/public contract. Any actual runtime trust/setup action requiring separate permission must be prepared and bounded when needed; this proposal grants no OS certificate-store/helper change.

## Required order and exit

Human/Architect decision and explicit seven-path scope -> frozen ADR/canonical/policy and negative guards -> fresh independent Review, applicable exact-head hosted CI, protected integration/actual-main verification and safe main sync -> reassess all Web inputs -> backlog to ready to active -> fresh implementation context -> real browser screenshots and Architect review/fix/approval -> fresh independent implementation Review and applicable exact-head CI -> protected integration/actual-main/safe sync. Do not treat local baseline or research validation as Task/Gate PASS. Web stays backlog while the mandatory input and CI scope are missing. No new product Task ID is proposed.

## Verification and recovery

Minimum assigned-root architecture all exits 0 in 3141ms; frozen integrity exits 0 in 187ms. Exact argv/output hashes are in baseline-result.json, full recorded streams stay private. No Web product files, workflows, guards, canonical/contracts, helper/trust or unknown main work were changed. The only current write scope is Web task/current/this evidence. Initial/direct startup and delegated read-only audit are explicitly incomplete trace, not a fabricated full prospective history. Current admin metadata requires its own independent Review/applicable CI/sync; product acceptance remains blocked.
