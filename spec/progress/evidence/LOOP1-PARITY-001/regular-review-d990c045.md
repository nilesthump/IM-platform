# Independent regular review of LOOP1-PARITY-001

PASS for d990c0459f93576ba0d9951abaab9a5f2fa18f26 on task/LOOP1-PARITY-001 against 3a5a54abff6410762d2039c4acf880abbe3269a5. Fresh delegated reviewer /root/review3 had no implementation, fix or earlier review role. Managed detached H:/.codex/worktrees/pr1/IM-platform matched the assigned root. Initial and final porcelain status were empty. Both task prerequisites were accepted. Clean Control Acceptance located the unique review task. S3 remains OPEN.

The canonical Markdown and historical PDF matched a52e871d4f48708c1fa7e06ea2e4ffae3922a93a9be6128cb79b3292b6b36bef and 546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510. All 16 changed paths fall within task scope. Production services, Web application, shared SDK, schema, migrations, public contracts and dependency definitions retain their accepted bytes. The existing lockfile build is shared between verification and parity. The harness drives product WebClient and its SDK through real HTTPS/WSS, with Node supplying the runtime. No browser rendering or visual change is claimed. The CI Java job executes both canonical Auth, Group/IM, Sync and TLS messaging profiles and checked child steps. Shared deployment inputs select the parity job. The full candidate selects all fourteen job flags.

The repaired runner disposes each constructed client even if another disposal fails and preserves concurrent body and cleanup errors. CA copy and Gateway startup now use bounded classified retries with the final cause, while certificate and unknown errors propagate. Registered socket and Compose cleanup callbacks are independently unwound. The four fault-injection cases directly cover the previous findings. The added regression scope and existing standard-library cleanup mechanism are proportionate to those failures.

Live independent execution on each profile passed strict TLS peer tests, durable ACK/one Outbox, duplicate/conflict, rollback, revocation, Web login, DIRECT and group delivery, Sync and logout. Both Compose projects verified zero remaining owned containers or volumes. Both used Web artifact SHA-256 58bc0ef831639eecea2a71fec77db588a5b32a93e13efe05b96aebcb6b017577. ADR-0004 preserves the single named friend authorization deferral. Live plugin permissions remain under S4. The CI suite ran 41 tests with four skips, and the architecture suite ran 99 tests with one skip. Independently reviewed pre-existing Auth/Group/Sync fixture job wiring awaits hosted execution on this candidate.

External Recorder R-20261121T080137Z-939bc9e6-aa80-4e59-977e-d04bd6d8edf5, parent R-20261121T070901Z-3e845e2e-3f89-4a05-8fb2-99ef8644a952, finished and validated 25 events. Initial architecture command hit a Windows GBK output-encoding failure in the Recorder; repeating with PYTHONUTF8=1 completed and recorded full output. Python below denotes bundled Python 3 first on PATH. Separate fresh error review, exact hosted acceptance, protected integration, actual-main verification and safe synchronization remain pending.

| Command | Exit | Elapsed ms |
|---|---:|---:|
| python -Xutf8 -B ci/check_architecture.py --scope all --json | 0 | 1922 |
| pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance | 0 | 27391 |
| python -Xutf8 -B tests/e2e/test_parity_failures.py | 0 | 968 |
| python -Xutf8 -B -m unittest discover -s tests/ci -q | 0 | 7500 |
| python -Xutf8 -B ci/classify.py --base 3a5a54ab --head HEAD | 0 | 969 |
| git -c core.whitespace=cr-at-eol diff --check 3a5a54ab HEAD | 0 | 156 |
| git -c core.excludesFile=.git/info/exclude status --porcelain=v1 --untracked-files=all | 0 | 203 |
| python -Xutf8 -B -m unittest discover -s tests/architecture -q | 0 | 34704 |
| python -Xutf8 -B tests/e2e/parity.py | 0 | 126375 |
| git -c core.excludesFile=.git/info/exclude status --porcelain=v1 --untracked-files=all | 0 | 78 |
