# Durable Verification Evidence

Store each independent review or CI run at `spec/progress/evidence/<TASK_ID>/<review-or-ci-run>.md`.

Every acceptance record must include Task ID and state, reviewed commit SHA, reviewer/context independence marker, clean checkout or isolated-worktree method, branch, reviewed diff range, exact commands, start time or elapsed time, exit codes, PASS/FAIL, summarized output, final git status, its own evidence path, and materially relevant tool/runtime versions. A Task Spec points to these records; `spec/progress/current.md` does not duplicate their history.

Development-mode verifier output is diagnostic only and must never be labeled or used as acceptance evidence.
