# Research Recorder v1

Schema version: `1.0.0`.

This directory is a non-product research control plane. It records observable facts about Agent runs; it is not Frozen Product Architecture, does not define contract semantics, and never decides Task or Stage acceptance. Recorder PASS means only that Recorder artifacts are structurally valid.

## Workflow

The implementation uses only the Python 3 standard library. On Windows use `tools/research/recorder.ps1`; on other platforms invoke `python3 tools/research/recorder.py` with the same subcommands:

```text
tools/research/recorder.ps1 register-prompt --task-id TASK --file prompt.txt
tools/research/recorder.ps1 start-run --task-id TASK --role implementation --capture-mode prospective --prompt-id P-ID --experiment-group full_governance
tools/research/recorder.ps1 run-command --run-id R-ID -- command arg
tools/research/recorder.ps1 record-event --run-id R-ID --event-type architecture_conflict --data-json '{"decision":"...","reason":"..."}'
tools/research/recorder.ps1 record-human-decision --run-id R-ID --question "..." --alternatives-json '["A","B"]' --selected B --reason "..."
tools/research/recorder.ps1 finish-run --run-id R-ID --result PASS
tools/research/recorder.ps1 validate-run --run-id R-ID
```

`register-prompt` stores the visible Human prompt and SHA-256 before dispatch. It never claims access to platform-internal system prompts. `start-run` captures Git/task/authority state without reading untracked file contents. `run-command` executes the real argv, records timestamps, duration, raw-output hashes and redacted output blobs, and propagates the real exit code. Semantic events are reserved for facts scripts cannot infer.

Review, fix, and implementation are separate runs connected with `parent_run_id` or `related_run_id`. A review is independent only when the observed actor/context establishes that fact; the Recorder never promotes self-review. CI evidence is ingested with `ingest-ci` from an externally produced evidence object matching `schema/ci-ingestion.schema.json`; Recorder does not manufacture CI outcomes and no GitHub workflow is installed by this task.

## Capture modes and history

- `prospective`: complete observation begins at run start.
- `prospective_resume`: resumed pre-Recorder work; requires `pre_recorder_work=true` and records `pre_recorder_trace_complete=false`.
- `retrospective_backfill`: derived only from durable repository evidence. Unknown prompt/model/tool/timing/token/cost fields are `unavailable`.
- `bootstrap_partial`: Recorder construction itself; excluded from the primary prospective quantitative dataset.

`backfill` creates explicitly marked metadata. It does not replay history. A running run is partial; default validation fails it. Finished raw event streams are immutable through normal commands. JSONL sequence and the event hash chain detect malformed, partial, duplicate, reordered, or edited events.

## Secrets and unavailable facts

The Recorder never dumps the process environment. Prompt, argv, stdout, stderr, and semantic payloads are checked for common credential forms and redacted before durable storage. Do not pass `.env`, credentials, raw auth headers, signing keys, or secret-bearing files. Redaction is defense in depth, not authorization to submit secrets.

Hidden chain-of-thought, private reasoning traces, platform-internal prompts, and unavailable token/cost/context metadata are never inferred. A short public decision summary is allowed.

## Instrumentation Epoch

`INSTRUMENTATION_EPOCH.json` is intentionally absent until a fresh independent review accepts the Recorder candidate under repository governance. After acceptance it records timestamp, schema version, accepted commit, task, durable acceptance evidence, and the exact prospective trace start. Earlier artifacts remain pilot/backfill/bootstrap data and must not be mixed into the primary prospective dataset without their capture-mode labels.

## Export and analysis

Each run uses `runs/<run_id>/metadata.json`, `events.jsonl`, `initial_state.json`, `final_state.json`, `diff.patch`, `summary.json`, and optional redacted `blobs/`. JSON and JSONL are the stable export formats. Join runs by `run_id`, `task_id`, `parent_run_id`, and `related_run_id`; group experiments by `experiment_group`, with optional future `baseline_id`, `replicate_id`, `mutation_id`, `model_condition`, and `budget_condition` fields.

Research evidence and product acceptance evidence remain distinct. Recorder validation is not Task PASS; Task PASS is not Stage Gate PASS. Agents must expose Recorder failures, must not silently skip instrumentation, and must not edit evidence to make their own run pass.
