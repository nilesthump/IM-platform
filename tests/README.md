# Test suites

This page maps every suite to where it runs and how to run it locally. It describes the current state; CI selection is decided by `ci/classify.py` from the changed paths, and the workflow remains authoritative.

## Where each suite runs

| Suite | CI job | Entry point |
| --- | --- | --- |
| `tests/ci` | classify (every PR/push) | `python3 -m unittest discover -s tests/ci -v` |
| `tests/architecture` | architecture | `python3 -m unittest discover -s tests/architecture -v` |
| `tests/contract` | shared | `python3 -B -m unittest discover -s tests/contract -p test_sync_transport.py` |
| `tests/database` | migration (with disposable PostgreSQL) | `python3 -m unittest discover -s tests/database -v` |
| `tests/clients/web` | web, migration | `python3 -B -m unittest discover -s tests/clients/web -v` and `python3 -B tests/clients/web/verify.py` |
| `tests/clients/i18n` | run with its builder check | `python -Xutf8 -B -m unittest discover -s tests/clients/i18n -p test_language_packs.py` and `tools/build_language_packs.py --verify` |
| `tests/clients/gui` | desktop (`auth.mjs`), mobile (`android.py` on an API34 emulator) | job-specific commands |
| `tests/clients/sync`, `send`, `sqlite` | desktop/deploy exercise `go_smoke.py` against the SQLx `storage_probe`; full scopes run through their verifiers | `tools/verify_client_sync.py`, `tools/verify_client_send.py`, `tools/verify_client_sqlite.py` |
| `tests/go`, `tests/e2e` | deploy (real Compose stack, TLS E2E) | `tests/e2e/go_tls_messaging.py`, `tests/go/live_role_smoke.py` |
| `tests/infrastructure` | deploy | `./tests/infrastructure/smoke.ps1 -Profile go` / `-Profile java` |
| `tests/research` | **no CI job selects it** — agent-local suite for the Research Recorder | `python -m unittest discover -s tests/research` |
| `tests/compatibility`, `tests/integration`, `tests/load` | not currently selected by any job | local only until wired |

## Local quickstart

```text
python -Xutf8 -B -m unittest discover -s tests/ci
python -Xutf8 -B -m unittest discover -s tests/architecture
python -Xutf8 -B tools/verify_frozen_architecture.py
python -Xutf8 -B ci/check_s2_planning.py
```

## Environment notes (Windows)

- Machines where `python`/`python3` resolve only to the Microsoft Store alias stubs cannot use naive interpreter probes; explicit-interpreter overrides for the PowerShell launchers are proposed in review (check the open PRs for `-Python` / `RESEARCH_RECORDER_PYTHON` before relying on them locally).
- `tests/architecture` needs `javac` on PATH for the future-Java-layout compilation control; without a JDK that one test errors while the rest pass.
- Known skips: `tests/ci` reports 4 OS-dependent skips on Windows; `tests/architecture` skips the POSIX-symlink case in favor of a real Windows junction case.
