# LOOP1-ARCHDOC-001 Figure 15-1 fix development evidence

- Fresh Fix Agent: `/root/archdoc_fix2`; isolated managed worktree and branch `fix/LOOP1-ARCHDOC-001-gate-label`, based on exact candidate `4770214e36844334048c357508d626326944b452`. This is development evidence, not independent acceptance.
- The immutable PDF page 20 shows S0–S6 boxes, six unlabelled left-to-right progression arrows, and a distinct `Gate PASS` label below every stage. The repaired Mermaid retains the seven stages and six arrows, places `Gate PASS` on each corresponding stage node's final line, and adds no terminal arrow or new stage. The clickable TOC and the other eight Mermaid figures are unchanged.
- PDF SHA-256 before and after: `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`. Repaired Markdown SHA-256, separately computed: `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91`. The baseline manifest records both values in distinct active and historical fields.
- The prior independent reviewer's authored FAIL report was copied byte-for-byte from its interrupted worktree; source and copied SHA-256 are both `50bff40e2c3d98d6c09c7864017bef60b2eed8b286d47444d15004c049f82e2c`. That review Recorder is unfinished and is not presented as validated acceptance evidence. The earlier independent FAIL history is unchanged.
- Prospective Fix Recorder prompt: `P-9103b54f-c9bd-45a4-b968-b99ca558b5ef`; run: `R-20260927T175510Z-eb27b12a-a4ec-45ef-8707-e3f6e537163b`; experiment group `full_governance`. The prompt captures the latest exact Human steering and links to the original migration prompt already registered by the coordinator. One quoted shell edit failed before touching files; the final narrow patch and subsequent verifier results are visible in the run and Git diff.

## Development verification

| Exact command or check | Result |
| --- | --- |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1 -BaseCommit abcdb5beaf3bc46fed53f1208ab843a8c5e79f8a`, through Recorder | PASS, exit 0 after repair; real PDF and Markdown hashes, one active canonical path, governance, product diff, and focused S6-label negative control. |
| Bundled Python `spec/progress/evidence/LOOP1-ARCHDOC-001/semantic-audit.py`, through Recorder | PASS, exit 0; PDF extraction 28/28; 86 clickable targets, nine figures, key normative and numeric tokens; actual hashes printed. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-001.ps1`, through Recorder | PASS, exit 0; architecture routing and repository baseline. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`, through Recorder | PASS, exit 0; expressly non-acceptance mode. |

The Fix Recorder finished as development `PASS` with 26 events and `validate-run` PASS. Recorder integrity is distinct from task acceptance. Remaining: commit the narrow candidate cleanly and obtain a different fresh independent clean-checkout semantic review with Acceptance-mode verification. No self-acceptance is claimed.
