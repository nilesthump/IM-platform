---
task_id: LOOP1-ARCHDOC-001
title: Migrate Frozen Architecture canonical source from PDF to Markdown
status: review
owner: /root
stage: S0
gate: S0
---

# Goal

Migrate the immutable Frozen Architecture PDF to one repository-native Markdown canonical source and transfer the active frozen hash target to that Markdown without product architecture semantic change.

# Inputs

- `spec/architecture/README.md`, `spec/architecture/baseline.md`, and `scalable-distributed-im-architecture.pdf` (v1.0, SHA-256 `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`).
- `spec/architecture/decisions/ADR-0001-temporary-s0-bootstrap-acceptance-before-ci-availability.md`.
- Human Architect authorization in the recorded migration prompt `P-f0a652e5-89aa-4cad-84f2-578b28973d40`.
- `research/README.md`, `AGENTS.md`, `spec/handoff/agent-context.md`, and `spec/progress/current.md`.

# Dependencies

- `LOOP1-RESEARCH-001`, `LOOP1-CTRL-001`, and `LOOP1-CTRL-002` done.
- `LOOP1-CI-001` is not done; ADR-0001 independent bootstrap acceptance applies.

# Allowed Paths

- `AGENTS.md`
- `.gitattributes` (canonical Markdown byte-preservation rule only)
- `README.md`
- `spec/architecture/**` except the historical PDF (which is at repository root)
- `spec/handoff/agent-context.md`
- `spec/tasks/active/LOOP1-ARCHDOC-001.md`
- `spec/tasks/review/LOOP1-ARCHDOC-001.md`
- `spec/tasks/done/LOOP1-ARCHDOC-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-ARCHDOC-001/**`
- `spec/progress/checkpoints/*loop1-archdoc-001*.md`
- `tools/verify-loop1-ctrl-001.ps1`
- `tools/verify-loop1-ctrl-002.ps1`
- `tools/verify-frozen-architecture.ps1`
- `tools/research/recorder.py` (authority snapshot path only)
- `research/prompts/**` and `research/runs/**` (only this task's prospective Recorder artifacts)

# Acceptance

- PDF remains byte-identical and its original SHA-256 is retained as permanent provenance.
- One Markdown canonical file faithfully represents all PDF architecture semantics, numbers, and normative strength.
- Approved representation-only ADR, resolver, baseline manifest, and deterministic verifier transfer active authority and hash target to Markdown only after accepted merge to main.
- Independent section-by-section semantic review and clean-checkout acceptance pass; contracts and product implementation are unchanged.
- Recorder run validates; acceptance closure, post-merge verification, effective commit/time, and stable checkpoint are durable.

# Forbidden

- Modify, regenerate, rename, or delete the PDF; edit historical evidence; change Product Architecture semantics, contracts, or implementation; self-accept; force merge or push.

# Minimality

- Use one Markdown file, the existing baseline manifest, one representation-only ADR, a small verifier, and review evidence. No document service, new build system, or product changes.

# Verification

- `tools/verify-loop1-ctrl-002.ps1 -Mode Development` during implementation; Acceptance only from a clean committed independent checkout.
- `tools/verify-frozen-architecture.ps1` checks both real hashes, unique authority, governance references, and product-scope diff.
- PDF/Markdown semantic checklist and independent review; Recorder `validate-run`.

# Evidence

- Source PDF before candidate: SHA-256 `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`; still equal after implementation. PDF path and Git bytes are unchanged.
- Canonical Markdown candidate: SHA-256 `a41871e6596b79d37973d6747af233b91f098ba072bb648940b56ec5777ac9d8`, separately calculated from Markdown bytes.
- Recorder-wrapped exact text-layer check: 28/28 PDF pages match 28/28 Markdown blocks after line-ending normalization. Vector diagram edges are recorded separately in Markdown; implementation-side checklist is `spec/progress/evidence/LOOP1-ARCHDOC-001/semantic-equivalence-checklist.md`.
- Recorder-wrapped `tools/verify-frozen-architecture.ps1 -BaseCommit abcdb5beaf3bc46fed53f1208ab843a8c5e79f8a`: Development PASS, exit 0; both hashes, uniqueness, governance routing, representation-only metadata, and product diff pass.
- Recorder-wrapped `tools/verify-loop1-ctrl-001.ps1`: Development PASS, exit 0. `tools/verify-loop1-ctrl-002.ps1 -Mode Development`: PASS, exit 0 after staging the new canonical file. `git diff --check`: exit 0.
- Earlier exact-comparison attempts failed due command-shell delimiter escaping; they remain in the prospective Recorder event history. The corrected 28/28 comparison passed. No PDF or product file was edited.
- Initial Recorder run finished development `PASS` and `validate-run` PASS (40 events). During Git staging, 14/36 raw output blobs differed from working bytes due inherited EOL normalization. A run-local `blobs/.gitattributes` containing `*.txt -text -eol` and `git add --renormalize` preserved all 36/36 staged blob bytes without editing the finished event stream or blob contents. The first re-stage attempt was stopped by automatic approval review because of a usage limit; after the 2026-09-27 continuation the same approval path succeeded. The temporary transport mismatch remains disclosed, not erased.
- Continuation prompt `P-a61d816d-9e7f-4e01-8a8c-1a1e80fdd87b` and linked run `R-20260927T122147Z-09acf128-7271-40df-bfa5-a1741633c9cc` are `prospective_resume` with earlier same-turn staging explicitly incomplete as a prospective trace.
- The continuation run finished development `PASS` and `validate-run` PASS (22 events); its recorded staged-byte audit found exact canonical Markdown bytes and 36/36 first-run output blob matches. Durable development handoff: `spec/progress/evidence/LOOP1-ARCHDOC-001/2026-09-27-development-handoff.md`.
- Independent clean-checkout semantic review and acceptance remain pending.
- The independent reviewer rejected candidate `bc42205de19777ca033d14707b48d450a298a021` because the 28 fenced PDF pages were not native Markdown. Permanent FAIL evidence: `spec/progress/evidence/LOOP1-ARCHDOC-001/2026-09-27-independent-review-bc42205-fail.md`; closure commit `5f117a41bf2f906fcb0f490e0f87352ad19aadb7`.
- Fresh Fix Agent `/root/archdoc_fix1` repaired the canonical document into 86 native chapter/section/appendix anchors with clickable TOC, 25 tables, lists and nine Mermaid figures. PDF arrows, labels and standalone figure boxes were visually audited; both NATS → PostgreSQL arrows and their ambiguity are retained. New Markdown SHA-256 `e31fe163be90667b5562c1873ba427795e449e4ae22458390d2b7920de00894b`; the PDF provenance hash is unchanged.
- Deterministic verifier now rejects a synthetic 28-page fenced layout, a lost clickable index entry and missing diagrams. Recorder-wrapped 28/28 exact PDF text extraction audit, architecture verifier, CTRL-001 and CTRL-002 Development all PASS. Evidence: `spec/progress/evidence/LOOP1-ARCHDOC-001/2026-09-27-native-fix-semantic-checklist.md` and `2026-09-27-native-fix-development.md`. Prompt `P-9548431c-8181-4f5a-9598-1142c6215300`; run `R-20260927T144417Z-6e078f22-5d64-49fc-ab84-ad381cc6b575`. The Fix run finished and validated PASS with 14 events; a run-local byte-preservation attribute resolved four Git-normalized stdout blob mismatches, and all 19 staged Recorder files now match working bytes. These are development results only.
- The second fresh reviewer found that Figure 15-1 placed only six `Gate PASS` labels on stage arrows while the PDF has seven labels below S0–S6. Its authored FAIL evidence was copied verbatim as `spec/progress/evidence/LOOP1-ARCHDOC-001/2026-09-28-independent-review-4770214-fail.md` (SHA-256 `50bff40e2c3d98d6c09c7864017bef60b2eed8b286d47444d15004c049f82e2c`); that interrupted review's Recorder remains unfinished and is not claimed as valid acceptance evidence.
- Fresh Fix Agent `/root/archdoc_fix2` placed one `Gate PASS` label in each of the seven stage nodes in Figure 15-1 and restored the six unlabelled progression arrows shown by the PDF. It changed no other architecture figure or product scope. New canonical Markdown SHA-256 `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91`; PDF remains `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`. The verifier now rejects a missing S6 label. Development evidence: `spec/progress/evidence/LOOP1-ARCHDOC-001/2026-09-28-gate-label-fix-development.md`; prompt `P-9103b54f-c9bd-45a4-b968-b99ca558b5ef`, run `R-20260927T175510Z-eb27b12a-a4ec-45ef-8707-e3f6e537163b`.


# Handoff

- Base: clean local `main` commit `abcdb5beaf3bc46fed53f1208ab843a8c5e79f8a`; Fix branch is isolated at independent-FAIL closure `5f117a41bf2f906fcb0f490e0f87352ad19aadb7`. Original `H:\IM-platform` untracked `contracts/http/schema-lint/` remains untouched and owned by another agent.
- Recorder runs: implementation `R-20260924T065732Z-5b072546-5f38-480d-9ae7-2786a0b77c43` and continuation `R-20260927T122147Z-09acf128-7271-40df-bfa5-a1741633c9cc`.
- No product architecture conflict; canonical representation change requires the minimal Human-approved ADR under PDF section 2.1.

# Next Action

- Different fresh independent Review Agent: review the committed Figure 15-1 repair from a clean isolated checkout, compare the PDF's seven stage Gate labels and all architecture semantics, run deterministic and Acceptance-mode verification, and issue new PASS/FAIL evidence without Fix Agent self-acceptance.
