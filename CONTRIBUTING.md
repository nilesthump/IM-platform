# Contributing

This page describes the collaboration conventions currently in use on this repository. Coding agents must still read [AGENTS.md](./AGENTS.md) first; this page covers the human and fork mechanics around it and never overrides governance.

## Repository relationship

- Upstream: `nilesthump/IM-platform`, protected `main` branch.
- Contributors work in personal forks. Task branches are pushed to the fork and proposed to upstream; fork-internal pull requests are not used for integration.
- First pull requests from a new fork require maintainer approval before GitHub Actions workflows run (checks stay at zero until then).

## Branches and commits

- One branch per work item: `task/<ID>-<SLUG>` for queued task work, `task/NONMAINLINE-<SLUG>-001` for non-queue maintenance (bug fixes, docs, tests).
- Commits are small, imperative, and self-contained.
- Line endings are LF. Byte-exact evidence files and recorder blobs are protected by `.gitattributes` `-text` rules; do not rewrite them.

## Pull requests

- PRs target upstream `main` from fork branches.
- Titles are concise Chinese summaries; queued task work prefixes `[LOOP1-XXX-001]`.
- The body records: the problem and root cause, exact verification commands with observed results, relevant SHAs (candidate plus baseline), and any preserved-state caveats. Honest disclosure of pre-existing failures discovered along the way is expected.
- Stacked PRs declare their dependency explicitly and merge after their prerequisite.

## Local verification

- Baseline integrity: `python -Xutf8 -B tools/verify_frozen_architecture.py` and `python -Xutf8 -B ci/check_s2_planning.py`.
- Suites: `python -m unittest discover -s tests/ci` and `python -m unittest discover -s tests/architecture`.
- The Windows verification launchers accept an explicit `-Python <path>` interpreter override when PATH discovery only finds the Microsoft Store alias stubs.
- Agents additionally record their work with the Research Recorder (`research/README.md`); recorder runs are committed together with the change and are research evidence, never acceptance evidence.
- CI is the independent judge. Local PASS is evidence, not Stage Gate PASS.

## Scope discipline

- Non-feature maintenance must not touch Frozen Architecture, `contracts/`, accepted evidence, or bounded checkers without an explicit reviewed proposal.
- Queued business work (for example the S2 group tasks) is activated only by the governance process in AGENTS.md; maintenance PRs stay clear of it.
- Architecture conflicts are escalated as `BLOCKED_BY_ARCHITECTURE` with the smallest decision question, never resolved silently in a PR.
