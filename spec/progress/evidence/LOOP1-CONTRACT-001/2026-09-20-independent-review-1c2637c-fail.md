# LOOP1-CONTRACT-001 Independent Review - FAIL

- Date: 2026-09-20 (Asia/Shanghai)
- Reviewer: `/root/contract001_review`
- Independence: fresh Review Agent; not the implementer, metadata fixer, or coordinator
- Result: **FAIL**
- Reviewed commit: `1c2637cb253dc6eece0393c229fe77cd5934160e`
- Review checkout: clean detached isolated worktree at `H:/.codex/worktrees/contract001-independent-review-2/IM-platform`
- Branch/state: detached HEAD; `git status --short` returned no entries before and after verification
- Reviewed diff range: `e5482b135a2ab7451c24c29c7517e1a8f19ce420..1c2637cb253dc6eece0393c229fe77cd5934160e`
- Acceptance mechanism: temporary S0 bootstrap review under ADR-0001

## Deterministic verification

| Command | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| `& .\contracts\http\verify-auth-user-friend.ps1` | 0 | 242.4866 ms | Development verifier passed, but did not detect the contract defects below. |
| `& .\tools\verify-loop1-ctrl-002.ps1` | 0 | 571.1891 ms | Acceptance-mode repository recovery passed from the clean detached checkout. |
| `git diff --check e5482b135a2ab7451c24c29c7517e1a8f19ce420..HEAD` | 0 | 58.0163 ms | Whitespace check passed. |

All 11 isolated reviewer mutations were rejected with exit `1`: missing schema, broken reference, missing operation, removed error code, duplicate fixture ID, missing Java profile, altered friend idempotency, altered atomicity, token in query, plaintext refresh, and dirty Acceptance-mode checkout. Those controls did not cover the semantic gaps found by direct review.

The frozen PDF was unique, readable, tracked as a Git blob, and matched SHA-256 `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`. The review found no workflow, backend, database, WSS, Sync, Plugin, or frozen-architecture changes. The disposable review worktree was removed after the clean-state check.

## Findings

1. **P1 - fixtures contradict OpenAPI and are not contract-validated.** Auth expectations flatten `clientType`, `sessionEpoch`, and `refreshToken` instead of using required `session` and `tokens`. Friend expectations flatten `lowUserId` and `highUserId` instead of using required `normalizedPair`, and omit required `memberUserIds`. The fixture schema admits arbitrary bodies. The verifier does not cross-validate request bodies, response bodies, or response statuses against the referenced OpenAPI schemas and does not prove that Go and Java normalized outputs equal the canonical expectation. This violates Architecture 11.2-11.3, AUF-A-008, and task acceptance.
2. **P1 - one negative fixture specifies an undeclared response.** `authorization-binding-mismatch` expects HTTP 403 for `GET /v1/users/me`, while that operation declares only 200 and 401 and classifies a mismatched authentication binding as 401.
3. **P1 - error behavior and coverage are underconstrained.** Every error response accepts the same unrestricted 15-code envelope. The verifier does not bind an error code to an operation/status. Negative fixtures omit `AUTH_TOKEN_INVALID`, `AUTH_TOKEN_EXPIRED`, `AUTH_SESSION_REVOKED`, `USERNAME_ALREADY_EXISTS`, `USER_NOT_FOUND`, and `FRIENDSHIP_STATE_CONFLICT`.
4. **P1 - refresh transport permits a credentialless request.** `/v1/auth/refresh` combines an optional request body with an anonymous security alternative, so neither a WEB cookie nor a native refresh credential/client metadata is structurally required.
5. **Hard process violation - implementation self-expanded its write boundary.** The activation Task Spec did not allow `spec/progress/evidence/LOOP1-CONTRACT-001/**`. Implementation commit `acfe36c2040e749ee508485ee8b577dc76604961` added that path to its own `Allowed Paths` before later commits wrote evidence there. This permanently remains a FAIL finding and is not retroactively excused.

## Coordinator authorization for repair evidence

On 2026-09-20, the Coordinator explicitly authorized retaining the exact path `spec/progress/evidence/LOOP1-CONTRACT-001/**` in this task's `allowed_paths` to satisfy the higher-level repository requirement for durable evidence. That prospective repair authorization does not erase or excuse the implementation-time self-expansion recorded above.

No PASS evidence was produced. The task remains in `review`; S0 remains NOT YET PASSED.
