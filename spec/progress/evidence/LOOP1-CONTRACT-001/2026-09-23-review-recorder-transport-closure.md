# LOOP1-CONTRACT-001 Recorder transport closure — authorized evidence

- Task remains `review` during this transport-only closure; no product Contract semantics changed.
- Finished independent content Review run: `R-20260923T070109Z-876f5bdd-f4dd-4eb8-97e5-27cea22c1a21`, 149 events, linked to reviewed clean candidate `d46ce5a9e6ee7a7a080e0a574189b090135abdb5`.
- Prior blocker evidence: `spec/progress/evidence/LOOP1-CONTRACT-001/2026-09-23-independent-review-d46ce5a-pass.md`. The first Git staging pass normalized CRLF text and produced 35 hash mismatches among 142 unredacted output blobs. Its earlier run-local attribute request was rejected by automatic approval review: “Adding attributes inside an already validated Recorder run changes evidence transport semantics after the fact and is not explicitly authorized; the user expressly prohibited editing Recorder evidence to make work pass. Do not bypass this rejection through a workaround or indirect execution.” No change was made then, and the task stayed in `review`.
- Later Human response, registered verbatim as `P-5d79f6c7-6a1d-4ccd-8ab3-ecd523eb23f1`: `ok，最终merge时将task/LOOP1-MIN-001新增内容也merge进main`. The Coordinator confirmed this `ok` answered the exact path-specific transport request. The additional `task/LOOP1-MIN-001` merge request is a Coordinator handoff; this Review Agent did not merge either branch.
- New closure run: `R-20260923T141457Z-f14fe85b-7ec9-4ee4-a771-c2ef3eaa3b23`, role `review`, capture mode `prospective_resume`, `pre_recorder_work=true`, `pre_recorder_trace_complete=false`, parent linked to the finished Review run, experiment group `full_governance`. Human decision `HD-cf7e87da-6c46-43e4-99f6-f37cef9b9baf` records the exact path-specific authorization. Its own `blobs/.gitattributes` was installed before its first output-producing command.
- The sole change inside the finished Review run is the newly Human-authorized `research/runs/R-20260923T070109Z-876f5bdd-f4dd-4eb8-97e5-27cea22c1a21/blobs/.gitattributes`, containing `*.txt -text -eol`. It controls Git transport of Recorder output blobs. Existing `events.jsonl`, metadata, output-blob working-tree bytes, hashes, command results, timestamps, and the finished Review result were not edited. This is an explicit later authorization, not a retroactive rewriting of the earlier rejection.

## Verified transport result

The audits and `validate-run` below ran through the new closure run's `tools/research/recorder.ps1 run-command` wrapper; exact argv, timestamps, elapsed time, exit code, and output hashes are in that run's event stream. The explicit `git add` staging step was an agent Git action between the local and indexed audits.

| Check | Exit | Result |
| --- | ---: | --- |
| Bundled Python SHA-256 audit of every local unredacted finished-Review output blob against its `command_finished` hash | `0` | 71 commands, 142 blobs, 0 mismatches. |
| `git add -- research/prompts/P-2bac526e-8167-4763-a91c-3ed2bf3bac91 research/runs/R-20260923T070109Z-876f5bdd-f4dd-4eb8-97e5-27cea22c1a21` followed by bundled Python SHA-256 audit using `git show :<blob-path>` for every staged unredacted output blob | `0` | 71 commands, 142 indexed blobs, 0 mismatches. |
| `pwsh -NoProfile -File tools/research/recorder.ps1 validate-run --run-id R-20260923T070109Z-876f5bdd-f4dd-4eb8-97e5-27cea22c1a21` | `0` | Finished run validates with 149 events. |

The exact audit program and argv are stored in the closure run's `command_started` events. No original paused-Agent-owned `contracts/http/schema-lint/` content was read, copied, modified, staged, or used. That untracked tree remains solely owned by the paused Agent.

Next exact action: finish and validate the closure run; verify both runs' blob hashes after committing this transport evidence; then revalidate independent Review evidence from a clean committed detached checkout. Only after those checks may `LOOP1-CONTRACT-001` enter `done` under ADR-0001 and receive the exact authorized `2026-09-23` accepted checkpoint. S0 Gate remains NOT YET PASSED.
