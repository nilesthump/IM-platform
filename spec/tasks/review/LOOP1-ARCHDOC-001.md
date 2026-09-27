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

# Handoff

- Base: clean local `main` commit `abcdb5beaf3bc46fed53f1208ab843a8c5e79f8a`; isolated worktree and task branch. Original `H:\IM-platform` untracked `contracts/http/schema-lint/` remains untouched and owned by another agent.
- Recorder runs: implementation `R-20260924T065732Z-5b072546-5f38-480d-9ae7-2786a0b77c43` and continuation `R-20260927T122147Z-09acf128-7271-40df-bfa5-a1741633c9cc`.
- No product architecture conflict; canonical representation change requires the minimal Human-approved ADR under PDF section 2.1.

# Next Action

- Fresh independent Review Agent: compare full PDF semantics, diagrams, normative strength, hashes, scope, and clean-checkout verifier; issue PASS/FAIL evidence without self-acceptance.
