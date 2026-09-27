# LOOP1-ARCHDOC-001 development handoff (not acceptance)

Base: clean committed local `main` `abcdb5beaf3bc46fed53f1208ab843a8c5e79f8a`; isolated branch/worktree `task/LOOP1-ARCHDOC-001` at `H:\.codex\worktrees\loop1-archdoc-001\IM-platform`. Task is in `review`, not `done`. Independent acceptance is pending.

## Source and candidate

- PDF retained at `scalable-distributed-im-architecture.pdf`; before and after implementation SHA-256: `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`.
- Candidate Markdown `spec/architecture/frozen-architecture.md`; its own SHA-256: `a41871e6596b79d37973d6747af233b91f098ba072bb648940b56ec5777ac9d8`.
- `spec/architecture/baseline.md` is the minimal machine-readable migration record. It declares `representation_only`, `semantic_change: false`, the active Markdown hash, and the distinct historical PDF hash. ADR-0002 records the Human Architect authorization and delayed effective point.
- The candidate preserves 28/28 PDF text-layer pages exactly after CRLF-to-LF normalization. Vector diagram arrows absent from text extraction are transcribed in the Markdown diagram section. The implementation checklist is `semantic-equivalence-checklist.md`; fresh independent visual review remains required.

## Recorded development verification

- Initial prospective Recorder prompt `P-f0a652e5-89aa-4cad-84f2-578b28973d40`, run `R-20260924T065732Z-5b072546-5f38-480d-9ae7-2786a0b77c43`, full governance, finished development PASS, `validate-run` PASS with 40 events. This is Recorder integrity, not Task acceptance.
- Exact page-block comparison: PASS, 28/28. Two earlier command attempts failed from shell delimiter escaping; their actual failures remain in the run.
- `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1 -BaseCommit abcdb5beaf3bc46fed53f1208ab843a8c5e79f8a`: PASS, exit 0, real PDF/Markdown hashes, unique Markdown, provenance, governance routing, no staged product changes.
- `pwsh -NoProfile -File tools/verify-loop1-ctrl-001.ps1`: PASS, exit 0 after staging the canonical Markdown.
- `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`: PASS, exit 0 with task in review queue; explicitly not acceptance.
- `git diff --exit-code abcdb5beaf3bc46fed53f1208ab843a8c5e79f8a -- scalable-distributed-im-architecture.pdf contracts backend clients plugins`: PASS, exit 0. No Product Contract or implementation edit.
- `git diff --cached --check` returns exit 1 only because immutable Recorder output blobs and its raw `diff.patch` contain original trailing whitespace/CRLF. `git diff --cached --check -- . ':(exclude)research/runs/**'`: PASS, exit 0 for authored files. Recorder bytes were retained, not modified to silence this check.

## Recorder Git transport and continuation

Initial staging normalized 14 of 36 run stdout/stderr blobs. The initial `git add` retry was rejected because automatic approval review hit the account usage limit; the command did not run. After the 2026-09-27 Human continuation and usage reset, the same approved tool path succeeded. A run-local `blobs/.gitattributes` sets `*.txt -text -eol`; `git add --renormalize` made all 36/36 staged blob bytes equal the original working bytes. The finished events and output contents were not edited.

Continuation prompt `P-a61d816d-9e7f-4e01-8a8c-1a1e80fdd87b` and linked run `R-20260927T122147Z-09acf128-7271-40df-bfa5-a1741633c9cc` use `prospective_resume` with pre-run work explicitly not claimed as prospectively traced. The continuation finished development `PASS`; `validate-run` passed with 22 events. Its recorded staged Markdown bytes and 36/36 first-run blob audit passed.

## Next action

Stage and byte-audit the continuation run's outputs; commit the candidate; then assign a fresh independent Review Agent to a clean committed checkout. Do not accept or merge based on this development evidence.
