---
task_id: LOOP1-S3-GATE-001
title: S3 Java equivalence Gate evaluation
status: review
owner: /root/gate_writer
stage: S3
gate: S3
---

# Goal

Evaluate S3 on the accepted product tree and publish a recoverable stage decision.

# Inputs

Frozen Architecture from spec/architecture/README.md and baseline.md, §§2.3, 3, 6.1, 10–12, 15, 20 and Appendix B. Apply ADR-0004, 0007, 0008, 0013 and 0014 and the domain, invariant, acceptance and contract families identified by LOOP1-PARITY-001. Use AGENTS.md, research/README.md and the minimality, execution-boundaries, technology-selection, independent-review and error-handling governance documents.

# Technology Authorization

Gate evidence and recovery metadata only, using existing repository checks.

# Dependencies

- LOOP1-S2-GATE-001
- LOOP1-JAVA-ARCH-001
- LOOP1-JAVA-AUTH-001
- LOOP1-JAVA-IM-001
- LOOP1-PARITY-001

# Allowed Paths

- spec/tasks/active/LOOP1-S3-GATE-001.md
- spec/tasks/review/LOOP1-S3-GATE-001.md
- spec/tasks/done/LOOP1-S3-GATE-001.md
- spec/progress/current.md
- spec/progress/evidence/LOOP1-S3-GATE-001/**
- spec/progress/checkpoints/2026-11-22-s3-gate.md

# Acceptance

Trace Java core semantics, shared golden expectations and the unchanged compiled client across both live profiles to accepted runs. Verify the evidence against the recovery baseline, retain the named deferral and distinguish S4 plugin runtime scope. Record Gate PASS only after independent regular and different error-handling reviews, applicable exact-head hosted checks, protected integration, actual-main verification, safe synchronization and the independent Gate judgement.

# Forbidden

No edits to product, public contracts, CI or architecture. No S4 activation.

# Minimality

Reference the existing immutable task receipts. No additional runner or fixture.

# Verification

Run `python -Xutf8 -B ci/check_architecture.py --scope all --json` and `tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` from the clean committed candidate with Python 3 first on PATH. Inspect receipt digests, ancestry and the product diff through PR110.

# Evidence

spec/progress/evidence/LOOP1-S3-GATE-001/evaluation.md

# Handoff

The evidence matrix and proposed checkpoint cover the S3 conditions at main 9dffa06848bf07fa120420cf1be11ef6dbbeff38. The local architecture baseline passed. See the matrix for scope, commands and historical exceptions. Writer /root/gate_writer owns the Gate candidate in H:/.codex/worktrees/s3/IM-platform on task/LOOP1-S3-GATE-001. S3 OPEN. Both candidate reviews and hosted/main synchronization pending.

# Next Action

Perform fresh regular review on the committed candidate SHA, then a different fresh error-handling review on the same SHA before publication.
