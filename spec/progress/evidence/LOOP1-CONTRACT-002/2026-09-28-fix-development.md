# LOOP1-CONTRACT-002 Fix Agent development evidence

- Actor: fresh Fix Agent `/root/contract002_fix1`; branch `task/LOOP1-CONTRACT-002`; starting clean commit `7ebb096b5066c78cc8d5988f41311e45174447ab`.
- This repairs independent FAIL `2026-09-28-independent-review-55670c2-fail.md`. It is development evidence, not independent acceptance.
- Recorder prompt `P-11a24716-4c67-4776-84f6-d543dd09b025`; run `R-20260928T021000Z-97be66ca-3d6f-4b95-855d-3dd6f033714f`, `prospective_resume`. Mandatory recovery, authority inspection, and baseline checks preceded the run and are not claimed as complete prospective trace.

## Fix

`contracts/websocket/verify.py` now directly rejects `message.created` before durable COMMIT, requires the expected negative `auth.ack`, prevents wrong-Conversation delivery, and requires the revocation event followed by a closed socket. Nine committed in-memory mutation controls cover those four findings and the five passing review controls. The canonical envelope and generated golden fixture bytes are unchanged. No Gateway, Core, Sync, or Plugin implementation was added.

## Development verification

| Command | Exit | Result |
| --- | ---: | --- |
| Bundled Python 3 `contracts/websocket/verify.py --write` through Recorder | 0 | PASS; deterministic fixture generator, 8 positive, 10 negative scenarios, 11 schema and 9 behavior mutations rejected. |
| Bundled Python 3 `contracts/websocket/verify.py` through Recorder | 0 | PASS; generated fixture bytes match committed golden vector. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` through Recorder | 0 | PASS; task recovered in `review`; non-acceptance mode. |
| `git diff --check` | 0 | PASS. |
| Bundled Python 3 `tools/research/recorder.py validate-run --run-id R-20260928T021000Z-97be66ca-3d6f-4b95-855d-3dd6f033714f` | 0 | PASS; finished Fix run structurally valid with 14 events. |

All 10 Recorder output blobs were compared byte-for-byte with their staged Git blobs (10/10 match). The run-local `blobs/.gitattributes` disables line-ending conversion for these immutable outputs. Raw Recorder stdout and `diff.patch` contain captured CRLF/patch whitespace; the product and governance diff check excludes those immutable artifacts.

No Frozen Architecture, approved ADR, shared HTTP/error, public WSS schema, or golden fixture changes. Independent review must repeat the negative controls from a clean committed checkout and decide acceptance.
