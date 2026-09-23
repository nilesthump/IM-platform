# LOOP1-CONTRACT-001 OpenAPI structural lint Fix — development evidence

- Task: `LOOP1-CONTRACT-001`; queue/status: `review`/`review`.
- Fix Agent: `/root/contract001_complete_oas_lint_fix`; independent review pending. This is development evidence, not acceptance.
- Branch: `task/LOOP1-CONTRACT-001`.
- Baseline at delegation: `23bcfc88048072ecd39b6247929f6353015ddddf`.
- Committed Fix candidate: `272bb28` (`fix: validate Auth User Friend OpenAPI structure with OAI schema`).
- Repair diff: `23bcfc88048072ecd39b6247929f6353015ddddf..272bb28`.
- Recorder prompt: `P-cafcccd1-0a7d-493b-b084-8be72c1c3019` (`source=agent`, exact visible delegation text).
- Recorder run: `R-20260923T034702Z-a877284a-a16d-4848-9d8f-164c2833b74a`; `role=fix`, `capture_mode=prospective`, real trace start `2026-09-23T03:47:02.457952Z`, parent failed Review run `R-20260921T085657Z-61a82ea3-f63b-4315-87b2-d090f3f48905`, `experiment_group=full_governance`.

## Repair

The earlier bespoke `auth-user-friend.openapi.structure.schema.json` was removed. The verifier now uses an offline validator generated from the OpenAPI Initiative's [2026-08-03 OpenAPI 3.1 structural schema](https://spec.openapis.org/oas/3.1/schema/2026-08-03). The source file is byte-preserved at `contracts/http/openapi-3.1-2026-08-03.schema.json` (SHA-256 `59f106413cb48c31299f96f024c938d3628aed6cd02cd14bcfb2fcaae7a130b6`). The generated standalone validator SHA-256 is `682b5f51c053c9876c16a6bdd92fb8968a50c6df1d4bab44d6e8e184ce9c7ee6`; a second generation produced the identical hash.

Ajv `8.20.0` compiled the pinned source after exactly four `$dynamicRef: "#meta"` references were pinned to OAI's own `#/$defs/schema` placeholder. This is the structural-only behavior of the published schema, without a dialect override. The adapted schema JSON SHA-256 is `f301b37b6ec27b0ada35082b8a5868967bc1e68dcc330ff745470a4c468df56e`. Build procedure and limits are documented in `contracts/http/openapi-3.1-lint.md`.

The normal verifier uses the generated self-contained validator, which requires Node.js but no runtime package install or network access. It rejects nine structural mutations: missing `info.title`; unknown root, Info, and Operation members; scalar Response Object and Media Type Object; invalid response key; invalid security-scheme type; and invalid parameter location. The three cases from independent Review are among these. Six earlier semantic mutations remain intact, for 15 total.

The OAI schema intentionally does not validate the contents of Schema Objects; this build also disables `format` assertions. Published structural schemas do not establish every OpenAPI prose rule. Existing task-specific semantic, error-binding, and fixture checks continue independently. This Fix does not claim full specification conformance solely from schema validation.

## Commands and results

Unless stated otherwise, commands below were executed by `tools/research/recorder.ps1 run-command --run-id R-20260923T034702Z-a877284a-a16d-4848-9d8f-164c2833b74a -- ...`, with command timestamp, duration, exit code, and stdout/stderr hashes in the run stream.

| Exact wrapped command | Result | Elapsed |
| --- | --- | ---: |
| `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1` (before repair) | PASS, exit `0`; preexisting 7 mutations | `5513.1098 ms` |
| `pwsh -NoProfile -Command '$document = Get-Content -Raw contracts/http/auth-user-friend.openapi.json; $document \| Test-Json -SchemaFile contracts/http/openapi-3.1-2022-10-07.schema.json'` (exploratory, discarded approach) | FAIL, exit `1`; PowerShell schema engine did not evaluate the official dynamic-reference schema correctly | `746.2501 ms` |
| `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1` (first integration) | FAIL, exit `1`; detected that OAI schema does not require Operation `responses`, so that speculative mutation was replaced by an unknown Operation member | `7405.6444 ms` |
| `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1` (final repair) | PASS, exit `0`; 9 operations, 15 error codes, 6 positive / 21 negative fixtures, Go/Java, 15 mutations | `6174.1193 ms` |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | PASS, exit `0`; state recovered as `review`, explicitly non-acceptance | `995.6156 ms` |
| `node contracts/http/build-openapi-3.1-validator.js C:/Users/21441/AppData/Local/Temp/loop1-contract001-oas-build-a877284a/node_modules/ajv` | PASS, exit `0`; source/adapted hashes and four reference pins reported | `1191.8544 ms` |
| `git diff --exit-code HEAD -- contracts/http/auth-user-friend.openapi.json contracts/errors/http-errors.schema.json contracts/fixtures/auth-user-friend` | PASS, exit `0`; canonical OpenAPI/errors/fixtures untouched | `30.5342 ms` |
| `git diff --check 23bcfc88048072ecd39b6247929f6353015ddddf..272bb28` | PASS, exit `0`; committed Fix diff clean | `36.08 ms` |

The index contained only seven intended Fix paths when candidate `272bb28` was committed: replacement source/generator/runtime checker, verifier, documentation, and deletion of the obsolete bespoke schema. The separately owned untracked `contracts/http/schema-lint/` tree was not read, copied, modified, staged, claimed, or used by this Fix. No canonical OpenAPI, shared error, fixture, product implementation, Frozen Architecture, ACK, or compatibility semantics changed.

## Instrumentation and handoff

An initial exact prompt registration used Recorder's default `source=human` for an Agent delegation, producing unused `P-6b9ea32e-4b68-47cd-86db-82c3d39095e1`. It remains preserved and is not associated with the Fix run. The same exact text was registered correctly as `source=agent`, and the Fix run links that second prompt. A CTRL-002 command attempt was blocked before execution when automatic approval review hit a usage limit; after the limit reset, the command ran prospectively and passed. These limitations were recorded as an `instrumentation_warning`; no missing command result was reconstructed.

Recorder `finish-run --result PASS` completed this Fix development run with 25 events, final event hash `86dba5930c0f628ae6cfee57c689d6a0bff7348a03fe28625b947746cc17d465`, and manifest hash `7a8653ab2ae038ef7872d20016b143c175032f3a8fb17c94d08673ef89ffede2`. `validate-run` returned exit `0`, `status=finished`, `event_count=25`. Recorder PASS means only that this Fix run's evidence is structurally valid and locally completed; it is not Task or Stage acceptance.

After run finalization, Git's inherited `research/.gitattributes` LF conversion was found to change six raw CRLF command-output blobs in the index. A run-local `blobs/.gitattributes` sets `*.txt -text -eol` so Git preserves the Recorder's original output bytes. No Recorder file content or recorded hash was edited. After restaging under that attribute, all 20 indexed stdout/stderr blobs matched their corresponding SHA-256 values in the immutable event stream. This Git transport check happened after `finish-run` and is documented here rather than backfilled as a run event.

Next exact action: a **fresh independent Review Agent** must inspect candidate `272bb28` and this handoff closure from a clean committed checkout, independently exercise structural negative controls and the complete verifier, then use the approved independent acceptance mechanism. This Fix Agent cannot accept its own work. Task remains in `review`; S0 Gate remains NOT YET PASSED.
