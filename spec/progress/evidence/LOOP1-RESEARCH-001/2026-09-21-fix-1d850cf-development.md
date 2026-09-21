# LOOP1-RESEARCH-001 Fix Development Evidence

Date: 2026-09-21

Mode: fresh Fix Agent development evidence only; not independent acceptance.

## Isolation and candidate

- Fix Agent: `/root/recorder_fix1`; not the implementation Agent or failed reviewer.
- Isolated worktree: `H:\.codex\worktrees\research-recorder-fix\IM-platform`.
- Branch: `fix/LOOP1-RESEARCH-001-1`.
- Repair baseline: `a1563e8b1028510d18b4d0ad1feea11f888cc5af`, including permanent independent FAIL evidence.
- Repair content commit: `1d850cf8cbe6c9aeec94e43f7395b8901bcb5f78`.
- Frozen Architecture SHA-256 matched its manifest: `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`.
- The original `H:\IM-platform` worktree and paused-Agent-owned content were not read, modified, copied, moved, stashed, cleaned, or claimed.

## Repaired findings

- Finished-run manifests hash Git LF-canonical text bytes, and `research/.gitattributes` fixes research artifacts to LF. The committed bootstrap manifest now passes default repository validation on the clean committed candidate without exemption or history rewriting.
- Recursive secret handling now treats normalized structured keys including `password`, `api_key`, `token`, `access_token`, `refresh_token`, `authorization`, and `raw_auth_headers` as sensitive. Quoted JSON prompts are parsed and redacted before persistence.
- CI ingestion now enforces the exact eight-field allowlist, value types, commit SHA and result enums, rejecting secret-bearing extra fields before any event append. The JSON Schema sets `additionalProperties: false`.
- Prompt registration writes deterministic LF bytes and hashes those persisted bytes. Repository validation checks prompt content hashes and both prompt-to-run and run-to-prompt links. The committed Human prompt content was not rewritten; its clean-checkout blob SHA-256 and metadata now both equal `a7c3cb691d25fb8fd456c4f544653fc48e881c271ee3e32486f369a9cd08da8f`.
- The permanent review FAIL and bootstrap raw event stream remain unchanged. No Instrumentation Epoch was created.

## Verification

- `& '<bundled-python-3.12>' -m unittest discover -s tests/research -v`
  - PASS, exit `0`; 22 tests in `15.305s`.
  - New regressions cover the exact committed repository artifact, CRLF/LF manifest portability, prompt hash and cross-link tampering, sensitive structured keys and quoted JSON prompts, and rejection-without-persistence of secret-bearing CI extra fields.
- `& .\tools\research\recorder.ps1 validate-repository`
  - PASS, exit `0`, both before and after repair content commit.
- Clean committed blob comparison at `1d850cf8cbe6c9aeec94e43f7395b8901bcb5f78`:
  - Prompt Git blob SHA-256: `a7c3cb691d25fb8fd456c4f544653fc48e881c271ee3e32486f369a9cd08da8f`.
  - Prompt metadata SHA-256: `a7c3cb691d25fb8fd456c4f544653fc48e881c271ee3e32486f369a9cd08da8f`.
- `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Development`
  - PASS, exit `0`; task `LOOP1-RESEARCH-001` resolved once in `review`; five queues and ten Task Specs checked. This is explicitly non-acceptance.
- `git diff --check 1e1523c127c5a0f3baf85d8b5eca11b7b34d80dc..HEAD -- . ':(exclude)research/runs/**/diff.patch'`
  - PASS, exit `0`.
- Scope and generated-file checks:
  - No product, contract, Frozen Architecture, domain, invariant, acceptance, ACK, plugin-boundary, or `.github/workflows/**` path was changed by this repair.
  - No tracked or untracked `*.pyc` or `__pycache__` remains.
  - `LOOP1-CONTRACT-001` remains `review`, owner `unassigned-independent-review-agent`.

## Handoff

- Result: repair is development-verified only. It is not accepted and does not establish an Instrumentation Epoch.
- Next action: a new fresh independent Review Agent must review the final committed candidate from a clean isolated checkout under ADR-0001, repeat the 22 tests, default repository validation, CTRL-002 Acceptance mode, diff/scope checks, and the negative controls.
