# PR109 shared contract regression

The coordinator's initial publication approval block was resolved. On branch `task/LOOP1-PARITY-001`, both independent reviews passed `d990c0459f93576ba0d9951abaab9a5f2fa18f26`. See `regular-review-d990c045.md` and `specialist-review-d990c045.md` in this directory.

| GitHub run on that SHA | Failing shared job | Required gate |
| --- | --- | --- |
| [push 44892604608](https://github.com/nilesthump/IM-platform/actions/runs/44892604608) | [136811681523](https://github.com/nilesthump/IM-platform/actions/runs/44892604608/job/136811681523) | Failed because shared failed |
| [PR109 44892634532](https://github.com/nilesthump/IM-platform/actions/runs/44892634532) | [136811704120](https://github.com/nilesthump/IM-platform/actions/runs/44892634532/job/136811704120) | Failed because shared failed |

Each run had twelve successful jobs. Each shared contract step reported one error in 29 group tests. Line 204 of `test_verification_failures.py` raised `StopIteration` before checking the migration ledger. The refactor moved the real native transport, SQL helpers and assertion into `run_profile`, while the regression still searched the CLI wrapper. The parity entry point invokes that same profile runner. Other GUI and Sync consumers use the WebSocket helper and frame builder.

The repair points existing extraction at the runner. All ten transcripts and native failure expectations are preserved. Changing either the test or its runner now selects the shared job. Both CI configuration and test changes already fall within task scope. The additional test-file authorization covers this ledger regression only.

| Local command in the assigned worktree | Result |
| --- | --- |
| `python -Xutf8 -B ci/check_architecture.py --scope all --json` | PASS, no violations |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | PASS, task in review. Clean independent acceptance pending |
| `python -Xutf8 -B tests/contract/group/test_verification_failures.py VerificationFailureTests.test_e2e_ledger_assertion_preserves_records_and_native_failures` | Before repair, exit 1 with the hosted StopIteration. After repair, exit 0 |
| `python -Xutf8 -B -m unittest discover -s tests/contract/group -p "test_*.py" -v` | All 29 passed |
| `python -Xutf8 -B -m unittest discover -s tests/ci -q` | 41 tests, four skipped, exit 0 |
| `python -Xutf8 -B contracts/websocket/verify.py` | PASS, eight positive and ten negative scenarios |
| `python -Xutf8 -B contracts/plugin-api/verify.py` | PASS, 79 fixture outcomes and 16 mutation controls |
| `python -Xutf8 -B ci/classify.py --paths ci/classify.py tests/ci/test_classify.py tests/contract/group/test_verification_failures.py` | All fourteen classification flags selected |

Fix agent `/root/hostedfix`, Research Recorder run `R-20261121T101433Z-74e9fdd8-eacb-410c-9fa5-05117cecf2fa`. The new candidate requires both fresh independent reviews, clean control verification and hosted acceptance. PR109 remains open. Accepted main is `3a5a54abff6410762d2039c4acf880abbe3269a5`.
