# LOOP1-CI-001 Fix 2 development evidence

- Fix Agent: fresh `/root/ci001_fix2`, distinct from the implementer and independent reviewers. This is development evidence, not independent acceptance.
- Branch: `task/LOOP1-CI-001`; base handoff `a2caf7e2fd30f5a409e3b0f3fc81d58666bbcba4`; reviewed product diff range `10406be70bf66482836164400cd5b8be07709c58..HEAD` after commit.
- Change: `git diff --no-renames --name-only -z` exposes the deleted source and added destination of a rename. A move out of `contracts/`, `database/`, or `sdk/` therefore selects the full compatibility matrix. A copy leaves its source unchanged and has no source-side deletion to classify; its added destination is still reported.
- Scope: `ci/classify.py`, `tests/ci/test_classify.py`, task/current recovery, this evidence, and linked Recorder prompt/run only. No product behavior, public contract, migration, or Frozen Architecture change.
- Research Recorder: prompt `P-88e2f805-f0ca-4087-a588-964ed523aec2`; `prospective_resume` run `R-20260928T211249Z-a84b0c58-8b90-4854-af03-3b1eb3aba958`, related to Review 2. Mandatory startup reads and the initial baseline test preceded registration and are marked incomplete pre-Recorder work. The initial sandboxed baseline test exited 1 because Python could not create a temporary directory in the read-only sandbox; it did not show a code failure. A first recorded regression run exited 1 because the new test assumed source-first output order; corrected to order-independent comparison.

| Exact command in task checkout | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest discover -s tests/ci -v` | 0 | 1735 ms | 12 classifier/gate tests PASS after correction |
| `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B spec/progress/evidence/LOOP1-CI-001/review2-negative-probe.py` | 0 | 469 ms | Prior Review 2 rename bypass now schedules all compatibility jobs; gate controls PASS |
| `pwsh -NoProfile -File ./tools/verify-loop1-ctrl-002.ps1 -Mode Development` | 0 | 1094 ms | Five queues and recovery PASS; expressly non-acceptance |
| `pwsh -NoProfile -File ./tools/verify-frozen-architecture.ps1` | 0 | 703 ms | Canonical Markdown and historical PDF hashes PASS |

Review 1's backlog marker `spec/tasks/backlog/.gitkeep` remains tracked. The next independent reviewer must verify from a clean committed checkout, including CTRL-002 Acceptance, and judge the candidate. Actual GitHub workflow execution has not occurred. S0 Gate is NOT YET PASSED. Last known good independently accepted main: `10406be70bf66482836164400cd5b8be07709c58`. Fix Agent owns only the task-linked changes until commit; original `H:\IM-platform\contracts\http\schema-lint` remains untouched under another Agent's ownership.
