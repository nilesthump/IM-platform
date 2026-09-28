# LOOP1-CONTRACT-002 independent rereview: FAIL

- Fresh reviewer: `/root/contract002_review2`, distinct from implementation `/root/contract002_impl`, fix `/root/contract002_fix1`, and prior reviewer `/root/contract002_review1`. No product file was edited in this review.
- Exact reviewed candidate: `102b0ef8cd045ab628618cb541ed36a72d2b0db6` on `task/LOOP1-CONTRACT-002`; full activation diff `6e5c122..102b0ef`, focused fix diff `7ebb096..102b0ef`.
- Candidate branch checkout was clean before review. Separate detached `H:\.codex\worktrees\contract002-rereview-clean\IM-platform` at exact candidate SHA had empty `git status --porcelain=v1` before and after CTRL-002 Acceptance. Reviewer Recorder artifacts then dirtied only the branch checkout's authorized evidence paths.
- Canonical Frozen Architecture Markdown SHA-256 `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91` and retained PDF SHA-256 `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510` match `spec/architecture/baseline.md`. Approved ADRs, messaging domain/invariants/acceptance, shared HTTP/errors, and Minimality Contract were inspected.
- Recorder prompt `P-5b71ecfc-3d84-41a1-a874-0060f7087eaa`; run `R-20260928T022529Z-0d3417e3-6f8e-43df-aae6-2c75a1fe6c3c` used `prospective_resume`. Mandatory recovery, authority and candidate inspection before run start are not claimed as a complete prospective trace.

## Verification

| Exact command or method | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| Bundled Python 3 `tools/research/recorder.py run-command --run-id <review-run> -- <bundled-python3> contracts/websocket/verify.py` | 0 | 93 ms | Baseline fixture/generator comparison PASS: 8 positive, 10 negative shared Go/Java scenarios, 11 schema and 9 behavior mutations rejected. |
| Same Recorder, `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | 891 ms | Canonical and PDF hashes PASS. |
| Same Recorder, bundled Python 3 `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | 1 | 78 ms | Nine invalid mutations rejected, three invalid auth-state mutations unexpectedly accepted. Exit 1 is expected from the independent negative-control probe and means Task review FAIL. |
| Same Recorder, `pwsh -NoProfile -File H:\.codex\worktrees\contract002-rereview-clean\IM-platform\tools\verify-loop1-ctrl-002.ps1 -Mode Acceptance` | 0 | 1328 ms | Clean detached checkout Acceptance recovery PASS; `review` queue and clean Git state confirmed. |
| Same Recorder, `git diff --check 6e5c122..102b0ef -- contracts/websocket contracts/fixtures/websocket spec/tasks spec/progress/current.md spec/progress/evidence/LOOP1-CONTRACT-002` | 0 | 47 ms | Candidate product/recovery whitespace PASS. |
| Same Recorder, `git diff --exit-code 7ebb096..102b0ef -- contracts/websocket/envelope.schema.json contracts/fixtures/websocket/golden.json contracts/errors contracts/http spec/architecture` | 0 | 47 ms | Fix preserves canonical envelope, golden bytes, shared error/HTTP contracts, and Frozen Architecture. |

## Findings

1. **Blocking: positive and rejected auth.bind state behavior is not asserted.** `contracts/websocket/verify.py` validates schema shape and request identity but does not require a successful `auth.ack` for `bind-valid-session`, does not assert that a valid bind becomes `AUTHENTICATED`, and does not assert that a stale-epoch rejection leaves the socket `UNAUTHENTICATED`. The committed generator names these expectations, but `check_scenario` accepts all three independent in-memory invalid mutations. In particular, it accepts `bind-valid-session` with its sole successful output removed, which would make a non-binding connection pass contract tests. This fails the Task goal to machine-verify auth.bind/ack and the Frozen chapter 7.2 state/epoch rules. The probe is committed alongside this report and changes only in-memory scenario copies. A fresh Fix Agent should add direct state and output assertions with retained negative controls; a different fresh reviewer must repeat the probe.
2. The prior four review failures are repaired: wrong-Conversation delivery, omitted `session.revoked`, omitted invalid-signature rejection, and `MESSAGE_CREATED` before COMMIT are rejected. ACK-before-COMMIT, rollback success, unstable same-key retry, nonmember success, and pre-auth success are also rejected. These passes do not cure finding 1.
3. Full product diff stays in task-allowed WSS schema/verifier and shared fixture paths. `TEXT` only in WSS v1 remains a documented deferral: frozen Message includes `TEXT / PLUGIN`, while dependent `LOOP1-CONTRACT-003` owns Plugin API v1 and may extend `contracts/websocket/**`. No extra service, framework, dependency, or speculative abstraction was found under the Minimality Contract. Shared Go/Java parity is represented by one canonical fixture with both profiles listed; implementation profile conformance remains future work.

## Disposition

**FAIL** for `102b0ef`. Keep `LOOP1-CONTRACT-002` in `review`; no merge, push, Gate PASS, or `done` transition. The original `H:\IM-platform` untracked `contracts/http/schema-lint/` remains untouched. Recorder failure here is the intentional negative-control result; run structural validation is reported separately after finish.

- Recorder `validate-run --run-id R-20260928T022529Z-0d3417e3-6f8e-43df-aae6-2c75a1fe6c3c` exit 0 after finish with result FAIL, 16 events; elapsed not instrumented. Recorder integrity does not change the Task FAIL result.
