# Paused Agent Resume Protocol

After Recorder independent acceptance, resume `LOOP1-CONTRACT-001` in its existing review cycle. Do not select a replacement task, transfer ownership, mark it done, rewrite its earlier history, or touch unknown paused-Agent work.

Before the first resumed operation, register the actual Human/Coordinator resume prompt and start a new run with role `review` (or the actual resumed role), capture mode `prospective_resume`, and `--pre-recorder-work`. The resulting metadata must keep `pre_recorder_work=true` and `pre_recorder_trace_complete=false`. Initial capture records the then-current Git/task/diff/checkpoint facts. Pre-Recorder facts may be added only as marked backfill from durable evidence; unavailable prompt, model-call, token, tool-trace, timing, reasoning, context, and cost facts remain `unavailable`.

At control-plane insertion observation, the paused task was `LOOP1-CONTRACT-001`, queue/state `review`, owner `unassigned-independent-review-agent`. The original worktree was `H:\IM-platform`, branch `task/LOOP1-CONTRACT-001`, HEAD `1e1523c127c5a0f3baf85d8b5eca11b7b34d80dc`, with untracked `contracts/http/schema-lint/` treated as unknown/paused-Agent-owned. This is an activation snapshot, not a prospective run start. Re-observe real state at resume; do not assume it remained unchanged.
