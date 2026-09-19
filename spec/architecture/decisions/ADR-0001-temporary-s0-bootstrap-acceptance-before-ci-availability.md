# ADR-0001: Temporary S0 Bootstrap Acceptance Before CI Availability

Status: Approved

Date: 2026-09-19

Approved by: Architect through the 2026-09-19 batch-orchestration instruction

## Context

`LOOP1-CI-001` is itself an S0 task. Requiring the final real CI implementation before every earlier bootstrap task can enter `done` creates a circular dependency.

## Decision

Before `LOOP1-CI-001` is operational and `done`, a bootstrap or control-plane task may temporarily satisfy the independent acceptance role through all of the following:

- a fresh independent Review Agent, with no self-review;
- a clean committed checkout or isolated Git worktree;
- deterministic verification;
- durable repository evidence under `spec/progress/evidence/<TASK_ID>/`.

The evidence must record the reviewed commit SHA, clean-state method and result, repository branch, reviewed diff range, exact commands, exit codes, elapsed times, PASS/FAIL result, evidence path, git status, and reviewer independence.

This mechanism does not bypass Task acceptance or Stage Gate requirements, authorize hidden skips, or weaken security, compatibility, contracts, or architecture invariants. It does not modify the Frozen business architecture.

## Expiration

This exception expires automatically when `LOOP1-CI-001` becomes `done` and operational. After expiration, the real CI mechanism is mandatory for every applicable task-to-`done` transition and this mechanism is not an alternative bypass.
